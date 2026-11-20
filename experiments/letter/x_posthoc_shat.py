"""Doan Van Tai — POST-HOC improvement check for X-CTMC T3 (Claude, 20/11/2026; Codex out of quota).

Locked verdict T3 = DOES_NOT_STAND is unchanged. This asks, on the saved truth, whether an operator-available rate
estimate gives a better slope than the locked W2 estimate from a 100 T_int record:
  (a) the M/M/1 mean-load estimate s_mm1 (parameters only; never invalid);
  (b) the same W2 estimator on a 1000 T_int record (new post-hoc seed 2611205, not the train seed).
Shares DeltaF_hat are the locked sampled ones. Any real gain must be confirmed by a new card on a fresh grid.
"""
import json
import math
import multiprocessing
import statistics
from pathlib import Path

import numpy as np

from experiments.letter import mmpp
from experiments.letter import x_ctmc as X

POSTHOC_SEED = 2611205
LOAD = ('TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9', 'MLU')
OUT = X.OUT / 'posthoc_shat'


def long_record_s(regime_record, multiple=1000):
    regime = X.Regime.from_record(regime_record)
    p = X.prepare(regime)
    index = int(regime.id.rsplit('_', 1)[-1])
    streams = np.random.SeedSequence([POSTHOC_SEED, index, multiple]).spawn(2)
    means, errors = {}, []
    for j, side in enumerate(('A', 'B')):
        path = getattr(regime, side)
        shift = -regime.u if side == 'A' else regime.u
        est = X.estimate_path(path, p['chains'][side + 'st'].load, shift, p['T_int'],
                              np.random.default_rng(streams[j]), W=multiple * p['T_int'])
        for action in ('stay', 'switch'):
            try:
                if est['status'] != 'VALID':
                    raise ValueError('; '.join(est['errors']))
                means[side + '_' + action] = mmpp.stationary_mean(est[action + '_load_hat'], est['kappa_hat'],
                                                                  est['alpha_hat'], path.mu).r
            except (ValueError, ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
                errors.append(str(exc))
    s = None if errors else means['A_switch'] + means['B_switch'] - means['A_stay'] - means['B_stay']
    return regime.id, s, errors


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pred = json.loads((X.OUT / 'predictions.json').read_text())
    regimes = {r['id']: r for r in json.loads((X.OUT / 'regimes.json').read_text())['regimes']}
    planned = [r['regime'] for r in pred['records'] if r['status'] == 'PLANNED']
    with multiprocessing.get_context('spawn').Pool(8) as pool:
        long_s = {rid: (s, err) for rid, s, err in pool.map(long_record_s, planned)}
    fc = {(r['regime']['id'], v['rule'], round(v['h_T_int']), round(v['tau_T_int'])): v
          for r in pred['records'] if r['status'] == 'PLANNED' for v in r['rows']}
    exposed = set(pred['pilot_exposed_regimes'])
    rows = []
    for e in json.loads((X.OUT / 'truth_receipt.json').read_text())['raw']:
        raw = json.loads((X.ROOT / e['path']).read_text())
        rows += [r for r in raw['rows'] if r.get('status') == 'COMPLETED' and r['regime'] not in exposed]
    variants = {'locked_W100': lambda r: r['s_hat'], 'mm1_mean_load': lambda r: regimes[r['regime']]['s_mm1'],
                'W2_1000Tint': lambda r: long_s[r['regime']][0], 'true_s_bound': lambda r: r['s']}
    result = {}
    for name, est in variants.items():
        signs, slopes, covered = [], [], 0
        for r in rows:
            h, t = round(r['h_T_int']), round(r['tau_T_int'])
            f = fc.get((r['regime'], r['rule'], h, t))
            if r['rule'] not in LOAD or h not in (30, 100) or not f or f.get('status') != 'COMPLETED':
                continue
            if abs(f['DeltaF_hat']) < 0.01 or abs(r['G_S_pct_C_ref']) < 0.25:
                continue
            s = est(r)
            if s is None:
                continue
            covered += 1
            pred_sign = int(np.sign(s * f['DeltaF_hat']))
            if pred_sign != 0:
                signs.append(int(np.sign(r['G_S'])) == pred_sign)
            if h == 100 and r['slope_measured'] != 0:
                slopes.append(abs(r['slope_measured'] - s * f['DeltaF_hat']) / abs(r['slope_measured']))
        result[name] = dict(cells=covered, sign_accuracy=sum(signs) / len(signs) if signs else None, sign_cells=len(signs),
                            slope_cells=len(slopes), slope_median_rel_error=statistics.median(slopes) if slopes else None)
    result['W2_1000Tint_invalid_regimes'] = sum(v[0] is None for v in long_s.values())
    result['label'] = 'POST-HOC on saved truth; locked T3 verdict unchanged; confirm any gain with a new card'
    (OUT / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
