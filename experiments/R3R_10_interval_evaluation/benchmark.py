"""Registered component comparison on an already saved law; no law/plant runs."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import resource
import statistics
import time

import mpmath as mp

from experiments.R3R_07_confirmation.common import check_committed, digest, git, write_once
from experiments.R3R_08_population_numerics.law_cache import fingerprint, restore
from .evaluator import library, posteriors


def cpu():
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time() + children.ru_utime + children.ru_stime


def main():
    prereg = Path('experiments/R3R_10_interval_evaluation/benchmark_prereg.json')
    check_committed(prereg)
    cfg = json.loads(prereg.read_text())
    for path, wanted in cfg['source_sha256'].items():
        check_committed(path)
        if digest(path) != wanted:
            raise ValueError('benchmark source changed: ' + path)
    snapshot = Path(cfg['law_snapshot'])
    if digest(snapshot) != cfg['law_sha256']:
        raise ValueError('cached law bytes changed')
    payload = json.loads(snapshot.read_text())
    source = fingerprint()
    law = restore(payload, cfg['parameters'], source)
    start, wall = cpu(), time.monotonic()
    library()
    setup = dict(cpu_seconds=cpu()-start, wall_seconds=time.monotonic()-wall,
                 scope='native library load/compile; excluded from warm evaluator ratio')
    rows = []
    reference = None
    for method in ('original_interval', 'native_dyadic'):
        for repeat in range(cfg['repeats']):
            start, wall = cpu(), time.monotonic()
            if method == 'original_interval':
                pairs = [law.posterior(q) for q in cfg['indices']]
            else:
                values, errors = posteriors(law, cfg['indices'])
                pairs = list(zip(values, errors))
            elapsed, elapsed_wall = cpu()-start, time.monotonic()-wall
            if reference is None:
                reference = pairs
            for (value, error), (ref, ref_error) in zip(pairs, reference):
                if abs(value-ref) > error+ref_error:
                    raise ArithmeticError('posterior values disagree outside their enclosures')
                if error > 1e-8:
                    raise ArithmeticError('posterior threshold unchanged at1e-8')
            rows.append(dict(method=method, repeat=repeat, cpu_seconds=elapsed,
                wall_seconds=elapsed_wall, values=[str(v) for v,e in pairs],
                error_bounds=[str(e) for v,e in pairs]))
    medians = {method: statistics.median(r['cpu_seconds'] for r in rows if r['method'] == method)
               for method in ('original_interval', 'native_dyadic')}
    result = dict(owner='Doan Van Tai', status='PASS_COMPONENT_PARITY_ONLY_NOT_ADOPTED',
        utc=datetime.now(timezone.utc).isoformat(), source_commit=git('rev-parse','HEAD').decode().strip(),
        prereg_sha256=digest(prereg), python=platform.python_version(), mpmath=mp.__version__,
        machine=platform.platform(), parameters=cfg['parameters'], indices=cfg['indices'],
        roots=len(law.terms), law_error=str(law.error), setup=setup, measurements=rows,
        median_cpu_seconds=medians, median_cpu_ratio=medians['original_interval']/medians['native_dyadic'],
        scope='same local machine, three fixed previously seen q values, all repeats reported; no cloud speedup/p95 claim',
        new_laws=0, new_joint_regimes=0, CF_generated=0, candidate_adopted=False)
    write_once(cfg['output'], result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
