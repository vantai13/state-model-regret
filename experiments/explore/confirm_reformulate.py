"""DISCOVERY stage 2 (plan §8): re-screen anchored cells of one procedure at dt, dt/2, dt/4 and add
DK1 labels. Claude (AI) for Doan Van Tai. Sign probabilities and labels only."""
import argparse, csv, hashlib, json, multiprocessing, subprocess
from fractions import Fraction as F
from experiments.explore.reformulate_grid import OUT, ROOT, PLAN, slices, task, write, library


def run(procedure, workers):
    rows = list(csv.DictReader((OUT / 'anchors.csv').open()))
    family = (lambda r: r['horizon'] == 'rh1') if procedure == 'P3' else (lambda r: r['horizon'] != 'rh1')
    chosen = sorted({(r['slice'], r['ladder_lambdaA']) for r in rows
                     if family(r) and r['anchored'] == 'True' and float(r['target']) in (0.3, 0.7)})
    defs = {s['slice']: s for s in slices()}
    tasks = [(defs[s], F(lam), (1, 2, 4), True) for s, lam in chosen]
    path = OUT / f'confirm_{procedure}.jsonl'
    if path.exists():
        raise SystemExit('preserve stage-2 evidence; remove nothing')
    write(OUT / f'config_confirm_{procedure}.json', dict(
        author='Claude (AI) for Doan Van Tai', plan=PLAN, procedure=procedure, cells=len(tasks), levels=[1, 2, 4],
        plan_commit=subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], text=True, cwd=ROOT).strip(),
        source_sha256=hashlib.sha256((ROOT / 'experiments/explore/confirm_reformulate.py').read_bytes()).hexdigest()))
    library()
    with path.open('w') as handle, multiprocessing.get_context('fork').Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            handle.write(json.dumps(row) + '\n')
            handle.flush()
            print(f"{i}/{len(tasks)} {row['slice']} lam={row['lambdaA']} {row['status']} {row['wall_s']:.1f}s", flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--procedure', choices=('P3', 'P4'), required=True)
    p.add_argument('--workers', type=int, default=8)
    a = p.parse_args()
    run(a.procedure, a.workers)
