"""Doan Van Tai — export derived tables for letter 02_Code from X-CTMC, X1c and X-GEANT (Claude, 20/11/2026).

Writes small JSON tables (no raw arrays) under letter_smr_argon/02_Code/data/scope/:
  load_rules_ctmc.json  (cells of X-CTMC and X1c used by the paper's sign/slope/C5/Hybrid statements)
  load_rules_geant.json (X2 pooled cells, stationary checks, post hoc rolling shares, X4 step-0 counts)
"""
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEST = Path('/home/vantai/state-model-regret-papers/letter_smr_argon/02_Code/data/scope')
KEEP = ('regime', 'stratum', 'rule', 'h_T_int', 'tau_T_int', 's', 's_hat', 'C_ref', 'G_S', 'G_S_pct_C_ref', 'slope_measured',
        'regret_fresh_pct_C_ref', 'regret_stale_pct_C_ref', 'p_new', 'p_old', 'concentration_new', 'concentration_old',
        'tie_share_fresh', 'tie_share_stale')


def ctmc_set(folder):
    out = ROOT / 'results/letter' / folder
    pred = json.loads((out / 'predictions.json').read_text())
    fc = {(r['regime']['id'], v['rule'], round(v['h_T_int']), round(v['tau_T_int'])): v
          for r in pred['records'] if r['status'] == 'PLANNED' for v in r['rows']}
    cells = []
    for e in json.loads((out / 'truth_receipt.json').read_text())['raw']:
        raw = json.loads((ROOT / e['path']).read_text())
        for r in raw['rows']:
            if r.get('status') != 'COMPLETED':
                continue
            f = fc.get((r['regime'], r['rule'], round(r['h_T_int']), round(r['tau_T_int'])), {})
            cells.append(dict({k: r.get(k) for k in KEEP},
                              DeltaF_hat=f.get('DeltaF_hat'), sign_pred=f.get('sign_pred'), slope_pred=f.get('slope_pred'),
                              null_sign=f.get('null_sign'), c5_sign=f.get('c5_sign')))
    return dict(meta=dict(source='research repo results/letter/' + folder, namespace=pred['namespace'],
                          pilot_exposed_regimes=pred['pilot_exposed_regimes'],
                          estimator_invalid=sum(r['status'] == 'PLANNED' and r['estimator']['status'] != 'VALID'
                                                for r in pred['records']),
                          sign='G_S = L_stale - L_fresh', cells_not_independent=True), cells=cells)


def geant():
    g = ROOT / 'results/letter/x_geant'
    verdicts = json.loads((g / 'card_verdicts.json').read_text())
    rolling = json.loads((g / 'posthoc_rolling/summary.json').read_text())
    signal = json.loads((g / 'signal.json').read_text())
    stationary = []
    for m in json.loads((g / 'truth/receipt.json').read_text())['records']:
        z = np.load(g / f"truth/records/{m['regime']}_{m['date']}.npz")
        pipes = [str(x) for x in z['pipelines']]
        for ih, h in enumerate(z['h_seconds']):
            if int(h) not in (14400, 21600) or not bool(z['evaluable'][ih]):
                continue
            cref = float(z['C_ref'][:, ih].mean())
            for t, tau in enumerate(z['tau_seconds']):
                def bsr(q):
                    return 100 * max(float(z['costs'][:, q, 0, ih].mean()) - cref, float(z['costs'][:, q, t + 1, ih].mean()) - cref) / cref
                stationary.append(dict(regime=m['regime'], date=m['date'], tau_s=int(tau), h_s=int(h),
                                       stationary_G_S_zero=bool(np.all(z['G_S'][:, pipes.index('Stationary'), t, ih] == 0)),
                                       stationary_both_side_regret_pct=bsr(pipes.index('Stationary')),
                                       threshold_both_side_regret_pct={r: bsr(pipes.index(r)) for r in ('TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9')}))
    return dict(meta=dict(source='research repo results/letter/x_geant', sign='G_S = L_stale - L_fresh'),
                pooled_cells=verdicts['G1']['cells'], stationary_cases=stationary, posthoc_rolling=rolling,
                x4_step0=signal['gates']['X4'])


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    payload = dict(main_grid=ctmc_set('x_ctmc'))
    if (ROOT / 'results/letter/x_ctmc_c/truth_receipt.json').exists():
        payload['confirmation_grid_X1c'] = ctmc_set('x_ctmc_c')
    (DEST / 'load_rules_ctmc.json').write_text(json.dumps(payload, indent=1) + '\n')
    (DEST / 'load_rules_geant.json').write_text(json.dumps(geant(), indent=1) + '\n')
    print('written', [p.name for p in DEST.glob('load_rules_*.json')])


if __name__ == '__main__':
    main()
