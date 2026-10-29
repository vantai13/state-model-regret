"""Doan Van Tai — separately declared post-observation verification extensions."""
import argparse
import json
import pickle
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.R3R_02_audit import bridge as B
from experiments.R3R_02_audit import independent_mc as M
from experiments.R3R_02_audit.run_mc import comparison, policies, sample, target, write, MAP


def precision():
    config = json.loads((ROOT / 'experiments/R3R_02_audit/precision_extension.json').read_text())
    rid = config['id']
    base = ROOT / f'results/lessons/l3r_3/mc_run01/{rid}'
    out = base / 'precision_extension.json'
    if out.exists(): raise ValueError('preserve completed precision extension')
    with (base / 'engine_cache.pkl').open('rb') as f: model, la, lb = pickle.load(f)
    audit = json.loads((ROOT / f'results/lessons/l3r_3/engine_run01/{rid}/audit.json').read_text())
    expected = target(audit['levels'][0])
    previous = json.loads((base / 'final.json').read_text())['C3']['stationary'][-1]
    start = time.monotonic()
    data = sample(model, la, lb, config['new_N'], config['seed'], 'stationary')
    scores = M.score_policies(data, policies(model, data), save_path=base / 'precision_extension_moments.npz')
    checks = {k: comparison(v, {'mean': scores['mean'][k], 'sd': scores['sd'][k],
                               'se': scores['se'][k], 'n': scores['n']},
                            previous['checks'][k]['numerical_allowance']) for k, v in expected.items()}
    maxse = 100 * max(scores['se'][k] for k in MAP) / audit['levels'][0]['Cbar']
    result = dict(config=config, checks=checks, contrast_SE_max_ppC=maxse,
                  status='PASS' if maxse <= .1 and all(v['status'] == 'PASS' for v in checks.values()) else 'UNRESOLVED',
                  original_UNRESOLVED_preserved=True, wall_s=time.monotonic() - start)
    write(out, result); print(json.dumps({'id': rid, 'status': result['status'], 'maxSE_ppC': maxse}))


def quadrature(rid):
    out = ROOT / f'results/lessons/l3r_3/K320_extension/{rid}.json'
    if out.exists(): raise ValueError('preserve completed quadrature extension')
    row, _ = B.P.evaluate(B.spec(rid, 1, 320))
    write(out, row); print(json.dumps({'id': rid, 'K': 320, 'wall_s': row['wall_s']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('kind', choices=('precision', 'K320')); p.add_argument('--id', choices=('X1008', 'X1009'))
    a = p.parse_args()
    precision() if a.kind == 'precision' else quadrature(a.id)
