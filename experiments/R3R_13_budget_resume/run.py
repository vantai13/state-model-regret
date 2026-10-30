"""Resume infrastructure interruption without changing the registered estimators.

Parent artifacts remain immutable. Only certified completed jobs are reused;
the interrupted job is repeated in a new directory. No confirmation is sampled.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from experiments.R3R_07_confirmation.common import digest, git, write_once
from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_08_population_numerics.checks import check, planning_seconds
from experiments.R3R_08_population_numerics.worker import select_job


METADATA = {'id', 'declared_at', 'decision', 'output', 'full_tests_required',
            'source_sha256', 'deviation', 'prior_attempt', 'resume', 'limits'}


def validate_config(cfg, parent):
    for key, value in parent.items():
        if key not in METADATA and cfg.get(key) != value:
            raise ValueError('registered scientific/execution setting changed: ' + key)
    for path, sha in parent['source_sha256'].items():
        if cfg['source_sha256'].get(path) != sha:
            raise ValueError('parent estimator source changed: ' + path)
    for key, value in parent['limits'].items():
        if key != 'total_cpu_seconds' and cfg['limits'].get(key) != value:
            raise ValueError('per-job resource setting changed: ' + key)
    if cfg['limits']['total_cpu_seconds'] <= parent['limits']['total_cpu_seconds']:
        raise ValueError('budget continuation must explicitly increase total CPU')
    if cfg['resume']['prior_carried_cpu_reserve_seconds'] != parent['carried_cpu_reserve_seconds']:
        raise ValueError('prior resource ledger changed')


def verify_snapshot(manifest, root):
    expected = manifest['source_sha256']
    root = Path(root)
    actual = {str(p) for p in root.rglob('*') if p.is_file()}
    covered = {p for p in expected if Path(p).is_relative_to(root)}
    if actual != covered or not actual:
        raise ValueError('parent snapshot manifest is incomplete')
    for path, wanted in expected.items():
        if not Path(path).is_file() or digest(path) != wanted:
            raise ValueError('parent snapshot bytes changed: ' + path)


def load_completed(cfg, root):
    """Requires verify_snapshot first; do not infer success from progress.json."""
    root = Path(root)
    rows, origins, bundles = [], {}, {}
    for stage in cfg['stage_levels']:
        for path in sorted((root / stage).glob('*/receipt.json')):
            row = json.loads(path.read_text())
            rid = path.parent.name
            job = select_job(cfg, rid, stage)
            if row['id'] != rid or row['stage'] != stage:
                raise ValueError('parent job identity mismatch')
            if row['status'] != 'COMPLETED':
                raise ValueError('failed computation requires a versioned full rerun')
            data = json.loads((path.parent / 'result.json').read_text())
            resources = json.loads((path.parent / 'resource.json').read_text())
            if (resources != row['resources'] or resources['exit_code'] != 0
                    or not row['payload_valid'] or data['status'] != 'COMPLETED'
                    or data['kind'] != job['kind'] or data['id'] != rid
                    or data['stage'] != stage or data.get('CF_generated') != 0):
                raise ValueError('parent receipt/payload is not a completed registered job')
            if stage != 'marginal':
                expected = {f'{k}:{r}' for k, r in cfg['stage_levels'][stage]}
                if not expected or set(data['levels']) != expected:
                    raise ValueError('parent population levels are incomplete')
                bundles.setdefault(rid, {}).update(data['levels'])
            elif job['kind'] == 'legacy_anchor' and data['comparison']['status'] != 'PASS':
                raise ValueError('parent anchor failed')
            key = stage + ':' + rid
            if key in origins:
                raise ValueError('duplicate parent receipt')
            rows.append(row)
            origins[key] = str(path.parent)
    return rows, origins, bundles


def budget_fits(cfg, receipts, active):
    spent = sum(row['resources']['cpu_seconds'] for row in receipts)
    spent += cfg['resume']['prior_carried_cpu_reserve_seconds']
    return spent + (active + 1) * (cfg['limits']['job_cpu_seconds'] + 10) <= cfg['limits']['total_cpu_seconds']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prereg', type=Path, required=True)
    a = p.parse_args()
    cfg = verify_prereg(a.prereg)
    parent_path = Path(cfg['resume']['parent_prereg'])
    parent = json.loads(parent_path.read_text())
    if digest(parent_path) != cfg['resume']['parent_prereg_sha256']:
        raise ValueError('parent prereg changed')
    validate_config(cfg, parent)
    manifest = json.loads(Path(cfg['resume']['snapshot_manifest']).read_text())
    verify_snapshot(manifest, cfg['resume']['parent_output'])
    prior_attempt = json.loads((Path(cfg['resume']['parent_output']) / 'attempt.json').read_text())
    if prior_attempt['prereg_sha256'] != digest(parent_path):
        raise ValueError('parent attempt/prereg mismatch')
    subprocess.run(['git', 'merge-base', '--is-ancestor', prior_attempt['source_commit'], 'HEAD'], check=True)
    receipts, origins, bundles = load_completed(cfg, cfg['resume']['parent_output'])
    reused = len(receipts)
    out = Path(cfg['output'])
    out.mkdir(parents=True, exist_ok=False)
    write_once(out / 'attempt.json', dict(owner='Doan Van Tai',
        source_commit=git('rev-parse', 'HEAD').decode().strip(),
        prereg_sha256=digest(a.prereg), utc=datetime.now(timezone.utc).isoformat(),
        parent_attempt=prior_attempt, reused_receipts=reused, CF_generated=0))
    print(json.dumps(dict(status='RECOVERY_STARTED', reused=reused, CF_generated=0)), flush=True)
    peak = max(r['resources']['sampled_peak_rss_bytes'] for r in receipts)
    memory = {s.split(':')[0]: int(s.split()[1]) * 1024
              for s in Path('/proc/meminfo').read_text().splitlines() if ':' in s}
    pool = min(6 * 1024**3, memory['MemAvailable'] - 3 * 1024**3) - 512 * 1024**2
    workers = min(cfg['max_workers'], max(0, int(pool / (1.25 * peak + 32 * 1024**2))))
    if workers < 1:
        raise ValueError('registered memory reserve cannot accommodate one worker')
    write_once(out / 'resource_selection.json', dict(workers=workers,
        measured_parent_peak_rss_bytes=peak, available_memory_bytes=memory['MemAvailable'],
        pool_after_reserves_bytes=pool, policy='unchanged DL-077 measured-memory rule'))
    all_pass = True

    def progress(active, queue):
        data = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(receipts),
            reused=reused, active=[item[3] for item in active], queued=len(queue),
            cpu_seconds=sum(r['resources']['cpu_seconds'] for r in receipts),
            prior_carried_cpu_reserve_seconds=cfg['resume']['prior_carried_cpu_reserve_seconds'], CF_generated=0)
        tmp = out / 'progress.tmp'
        tmp.write_text(json.dumps(data))
        tmp.replace(out / 'progress.json')

    def group(ids, stage, count):
        nonlocal all_pass
        queue = [rid for rid in ids if stage + ':' + rid not in origins]
        active = []
        while queue or active:
            while queue and len(active) < count:
                if not budget_fits(cfg, receipts, len(active)):
                    if active:
                        break  # drain existing reservations before reducing concurrency
                    all_pass = False
                    queue = []
                    break
                rid = queue.pop(0)
                dest = out / stage / rid
                dest.parent.mkdir(parents=True, exist_ok=True)
                log = (out / (stage + '_' + rid + '_controller.log')).open('x')
                proc = subprocess.Popen([sys.executable, '-m', 'experiments.R3R_11_native_population.run_job',
                    '--prereg', str(a.prereg), '--job', rid, '--stage', stage,
                    '--out', str(dest), '--cache', cfg['cache_path']],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                active.append((proc, log, dest, rid))
            progress(active, queue)
            for item in list(active):
                proc, log, dest, rid = item
                if proc.poll() is None:
                    continue
                log.close()
                active.remove(item)
                if not (dest / 'receipt.json').exists():
                    all_pass = False
                    queue = []
                    continue
                row = json.loads((dest / 'receipt.json').read_text())
                receipts.append(row)
                origins[stage + ':' + rid] = str(dest)
                if row['status'] != 'COMPLETED':
                    all_pass = False
                    queue = []
                elif stage != 'marginal':
                    data = json.loads((dest / 'result.json').read_text())
                    bundles.setdefault(rid, {}).update(data['levels'])
                print(json.dumps(dict(stage=stage, id=rid, status=row['status'],
                    cpu_seconds=row['resources']['cpu_seconds'])), flush=True)
            progress(active, queue)
            if active:
                time.sleep(.3)
        return all_pass

    group([j['id'] for j in cfg['legacy_jobs'] + cfg['marginals']], 'marginal', 1)
    if all_pass:
        group([j['id'] for j in cfg['cases']], 'base', workers)
    selected, history = None, []
    if all_pass:
        for stage, K, ref in cfg['candidates']:
            if stage != 'base':
                group([j['id'] for j in cfg['cases']], stage, workers)
            if not all_pass:
                break
            checks = {j['id']: check(bundles[j['id']], K, ref) for j in cfg['cases']}
            entry = dict(stage=stage, K=K, ref=ref, checks=checks,
                ready=sum(v['ready'] for v in checks.values()), total=len(checks))
            history.append(entry)
            write_once(out / ('checks_' + stage + '.json'), entry)
            print(json.dumps({k: entry[k] for k in ('stage', 'K', 'ref', 'ready', 'total')}), flush=True)
            if all(v['ready'] for v in checks.values()):
                selected = (K, ref)
                break
    timing = [] if selected is None else [dict(id=j['id'], **planning_seconds(bundles[j['id']], *selected)) for j in cfg['cases']]
    summary = dict(owner='Doan Van Tai',
        status='CALIBRATION_READY_REQUIRES_CLOSURE_AUDIT' if selected else 'HOLD_NUMERICAL_AUDIT',
        selected_levels=list(selected) if selected else None, history=history, receipts=receipts,
        receipt_origins=origins, reused_receipts=reused, new_receipts=len(receipts)-reused,
        timing=timing, cpu_seconds=sum(r['resources']['cpu_seconds'] for r in receipts),
        prior_carried_cpu_reserve_seconds=cfg['resume']['prior_carried_cpu_reserve_seconds'],
        cpu_seconds_scope='current and reused native receipts only; prior03/04 carry is reported separately',
        workers_final=workers, CF_generated=0, confirmation_root=None, n=None, tag_created=False, Phase4='HOLD')
    write_once(out / 'summary.json', summary)
    write_once(out / 'levels.json', bundles)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('history', 'receipts', 'timing', 'receipt_origins')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
