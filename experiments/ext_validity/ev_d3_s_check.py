"""Doan Van Tai — EV-D3a diagnostic (post-hoc, stationary quantities only, no D): is the hybrid's correction s_train
(CRN, 1e5 s) close to a 10x longer CRN estimate (1e6 s, independent seed)? [AI (Claude) theo ủy quyền 14/11/2026]"""
import json, sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
import numpy as np
from experiments.ext_validity import packet as P

O = Path('results/ext_validity/ev_d3')


def one(case):
    rng = np.random.default_rng(case['seed'] + 5_000_000)
    T, warm, dt = 1_000_000., 1000., 1.0
    _, both = P.long_run_crn(case, warm + T, rng)
    ts = np.arange(warm, warm + T, dt)
    means = [float(sum(P.backlog(r, ts) for r in both[a]).mean()) for a in (0, 1)]
    blocks = [np.array([P.backlog(r, ts) for r in both[a]]).sum(0).reshape(20, -1).mean(1) for a in (0, 1)]
    d = blocks[1] - blocks[0]
    tr = json.loads((O / 'train' / f"{case['id']}_s{case['seed']}.json").read_text())
    return dict(id=case['id'], s_train=tr['s_train'], s_long=means[1] - means[0], s_long_se=float(d.std(ddof=1) / np.sqrt(20)),
                mean_stay_long=means[0])


def main():
    cases = [c for c in json.loads((O / 'cases.json').read_text()) if c['tau'] == 300.0]
    with ProcessPoolExecutor(max_workers=int(sys.argv[1]), mp_context=get_context('spawn')) as pool:
        out = list(pool.map(one, cases))
    (O / 'diag_s_long.json').write_text(json.dumps(out, indent=1) + '\n')
    print('DIAG_DONE', flush=True)


if __name__ == '__main__':
    main()
