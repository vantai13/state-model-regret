"""Doan Van Tai — independent rescore of X-CTMC and X-GEANT by Claude (Codex out of quota), 20/11/2026.

Does not import x_ctmc, x_geant, x_ctmc_card, x_geant_card or any scorer. Reads committed JSON/NPZ/CSV only, re-derives
every card quantity from the card definitions, and compares field by field with card_verdicts.json.
G_S = L_stale - L_fresh. Usage: python3 -m experiments.letter.x_rescore_claude
"""
import csv
import glob
import hashlib
import json
import math
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
C, G = ROOT / 'results/letter/x_ctmc', ROOT / 'results/letter/x_geant'
OUT = ROOT / 'results/letter/x_rescore'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sgn(x):
    return (x > 0) - (x < 0)


def ctmc(C=C):
    pred = json.loads((C / 'predictions.json').read_text())
    exposed = set(pred['pilot_exposed_regimes'])
    fc = {(r['regime']['id'], v['rule'], round(v['h_T_int']), round(v['tau_T_int'])): v
          for r in pred['records'] if r['status'] == 'PLANNED' for v in r['rows']}
    rec = json.loads((C / 'truth_receipt.json').read_text())
    rows = []
    for e in rec['raw']:
        assert sha(ROOT / e['path']) == e['sha256'], e['path']
        raw = json.loads((ROOT / e['path']).read_text())
        rows += [r for r in raw['rows'] if r.get('status') == 'COMPLETED' and r['regime'] not in exposed]
    load = ('TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9', 'MLU')
    out = {k: [] for k in ('T1', 'T1dis', 'T1null', 'T3', 'T4', 'T6', 'T6b')}
    for r in rows:
        h, t = round(r['h_T_int']), round(r['tau_T_int'])
        f = fc.get((r['regime'], r['rule'], h, t))
        if not (h in (30, 100) and f and f.get('status') == 'COMPLETED' and f.get('sign_pred') not in (None, 0)
                and abs(f['DeltaF_hat']) >= 0.01 and abs(r['G_S_pct_C_ref']) >= 0.25):
            continue
        hit = sgn(r['G_S']) == f['sign_pred']
        if r['rule'] in load:
            out['T1'].append(hit)
            if r['stratum'] == 'disagree':
                out['T1dis'].append(hit)
                out['T1null'].append(sgn(r['G_S']) == f['null_sign'])
            if h == 100 and r['slope_measured'] != 0:
                out['T3'].append(abs(r['slope_measured'] - f['slope_pred']) / abs(r['slope_measured']))
        if r['rule'] == 'M0':
            out['T4'].append(hit)
            out['T6'].append(sgn(r['G_S']) == f['c5_sign'])
            out['T6b'].append(r['concentration_old'] >= r['concentration_new'])
    t5 = [max(r['regret_fresh_pct_C_ref'], r['regret_stale_pct_C_ref']) <= 0.5 for r in rows
          if r['rule'] == 'Hybrid_hat' and round(r['h_T_int']) in (30, 100) and r.get('s_hat') is not None
          and sgn(r['s_hat']) == sgn(r['s']) != 0]
    mine = dict(T1=(len(out['T1']), sum(out['T1'])), T2=(len(out['T1dis']), sum(out['T1dis']), sum(out['T1null'])),
                T3=(len(out['T3']), statistics.median(out['T3'])), T4=(len(out['T4']), sum(out['T4'])),
                T5=(len(t5), sum(t5)), T6=(len(out['T6']), sum(out['T6'])), T6b=(len(out['T6b']), sum(out['T6b'])))
    v = json.loads((C / 'card_verdicts.json').read_text())
    reported = dict(T1=(v['T1']['cells'], round(v['T1']['accuracy'] * v['T1']['cells'])),
                    T2=(v['T2']['cells'], round(v['T2']['law_accuracy'] * v['T2']['cells']),
                        round(v['T2']['null_accuracy'] * v['T2']['cells'])),
                    T3=(v['T3']['cells'], v['T3']['median_relative_error']), T4=(v['T4']['cells'], round(v['T4']['accuracy'] * v['T4']['cells'])),
                    T5=(v['T5']['cells'], round(v['T5']['share'] * v['T5']['cells'])),
                    T6=(v['T6']['cells'], round(v['T6']['accuracy'] * v['T6']['cells'])),
                    T6b=(v['T6b']['cells'], round(v['T6b']['share'] * v['T6b']['cells'])))
    return {k: dict(mine=mine[k], reported=reported[k],
                    match=all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12) for a, b in zip(mine[k], reported[k])))
            for k in mine}


def geant():
    pred = {(r['regime'], r['rule'], int(r['tau_s']), int(r['h_s'])): int(r['predicted_G_S_sign'])
            for r in csv.DictReader(open(G / 'predictions.csv'))}
    rec = json.loads((G / 'truth/receipt.json').read_text())
    cells, st_zero, cases, not_worse, st_reg = {}, True, 0, 0, []
    for m in rec['records']:
        p = G / f"truth/records/{m['regime']}_{m['date']}.npz"
        assert sha(p) == m['npz_sha256'], p
        z = np.load(p)
        pipes = [str(x) for x in z['pipelines']]
        for ih, h in enumerate(z['h_seconds']):
            if int(h) not in (14400, 21600) or not bool(z['evaluable'][ih]):
                continue
            cref = float(z['C_ref'][:, ih].mean())
            for t, tau in enumerate(z['tau_seconds']):
                for rule in ('TH_0.65', 'TH_0.8', 'TH_0.9'):
                    cells.setdefault((m['regime'], rule, int(tau), int(h)), []).append(
                        (float(z['G_S'][:, pipes.index(rule), t, ih].mean()), cref))
                def bsr(q):
                    lf, ls = float(z['costs'][:, q, 0, ih].mean()), float(z['costs'][:, q, t + 1, ih].mean())
                    return 100 * max(lf - cref, ls - cref) / cref
                s = pipes.index('Stationary')
                st_zero &= bool(np.all(z['G_S'][:, s, t, ih] == 0))
                cases += 1
                st_reg.append(bsr(s))
                not_worse += bsr(s) <= min(bsr(pipes.index(r)) for r in ('TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9'))
    resolved = matched = 0
    for key, vals in cells.items():
        g = [a for a, _ in vals]
        n = len(g)
        mean = sum(g) / n
        se = statistics.stdev(g) / math.sqrt(n) if n > 1 else math.inf
        cref = sum(b for _, b in vals) / n
        matched += sgn(mean) == pred[key]
        if abs(mean) >= 2 * se and abs(mean) >= 0.0025 * cref:
            resolved += 1
    v = json.loads((G / 'card_verdicts.json').read_text())
    mine = dict(G1=(len(cells), resolved, matched), G2=(cases, st_zero, statistics.median(st_reg)), G3=(cases, not_worse))
    rep_matched = sum(c['observed'] == c['predicted'] for c in v['G1']['cells'])
    reported = dict(G1=(len(v['G1']['cells']), v['G1']['resolved'], rep_matched),
                    G2=(v['G2']['records'], v['G2']['G_S_all_zero'], v['G2']['median_both_side_regret_pct']),
                    G3=(v['G3']['cases'], v['G3']['stationary_not_worse']))
    return {k: dict(mine=mine[k], reported=reported[k], match=mine[k] == reported[k]) for k in mine}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    result = dict(owner='Doan Van Tai', by='Claude (independent script, no scorer imports; Codex out of quota)',
                  x_ctmc=ctmc(), x_geant=geant())
    if (ROOT / 'results/letter/x_ctmc_c/truth_receipt.json').exists():
        result['x1c'] = ctmc(ROOT / 'results/letter/x_ctmc_c')
    result['all_match'] = all(d['match'] for part in ('x_ctmc', 'x_geant', 'x1c') if part in result for d in result[part].values())
    (OUT / 'rescore_claude.json').write_text(json.dumps(result, indent=2, default=str) + '\n')
    print(json.dumps({'all_match': result['all_match'],
                      **{f'{p}.{k}': d['match'] for p in ('x_ctmc', 'x_geant', 'x1c') if p in result for k, d in result[p].items()}}))


if __name__ == '__main__':
    main()
