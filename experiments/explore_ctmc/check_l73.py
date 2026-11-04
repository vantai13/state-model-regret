"""Doan Van Tai — score results/explore_ctmc/l73/CARD_L7_3.md exactly as locked [EXPLORATION ONLY; AI (Claude) theo
ủy quyền; the card itself is AI-drafted on the author's request].

  python -m experiments.explore_ctmc.check_l73    # -> results/explore_ctmc/score_l73.json

Inputs: truth rows results/explore_ctmc/runs_l73/<stage>/<id>.json (stages asym, sobol, mid); frozen zero-fit rows
l73/ZEROFIT_2s.csv (single host). Parameter conditions (h/T_int, delta, T_s/T_f) come from the frozen zero-fit rows, so
every (case, h) is known even when its truth is UNRESOLVED.

Readings fixed here before any truth (the card is silent on them; the strictest reading is used):
  R1  Combining parts (L73-1 six parts): FAIL if any part FAILs, PASS if all PASS, otherwise INCONCLUSIVE.
  R2  UNRESOLVED rule (card §5): unit = distinct case eligible by the parameter conditions of the prediction or part; a
      missing truth file, a non-COMPLETED status, or a row without the D22 block counts as UNRESOLVED.
  R3  The harm mask G_S < -0.5 (L73-4) is applied to truth rows after the UNRESOLVED gate; the gate is computed over the
      parameter-eligible cases (h/T_int <= 1), as in check_l72 L72-5.
  R4  L73-3 uses every MID row; MID has delta != 0 by construction (asserted).
  R5  Report-only breakdowns (per T_s/T_f, per (f, T_f), the (1; 4] bin of L73-1) use the same gate but never change a
      verdict.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
SETS = ('asym', 'sobol', 'mid')
N_MIN, UNRES_MAX = 10, 0.10


def load(out=OUT):
    z = pd.read_csv(out / 'l73' / 'ZEROFIT_2s.csv', dtype={'h': str})
    z = z[(z.status == 'COMPLETED') & z.stage.isin(SETS)].copy()
    recs, status = [], {}
    for st in SETS:
        for f in sorted((out / 'runs_l73' / st).glob('*.json')):
            d = json.loads(f.read_text())
            status[(st, d['id'])] = d['status']
            if d['status'] != 'COMPLETED':
                continue
            for r in d['h']:
                recs.append(dict(stage=st, id=d['id'], h=r['h'], G_S=r['G_S'], reg_static=r['regret']['static'],
                                 reg_M0_new=r['regret']['M0_new'], F=r['d22']['F'] if 'd22' in r else np.nan))
    t = pd.DataFrame(recs, columns=['stage', 'id', 'h', 'G_S', 'reg_static', 'reg_M0_new', 'F'])
    m = z.merge(t, on=['stage', 'id', 'h'], how='left')
    m['case_status'] = [status.get((s, i), 'MISSING') for s, i in zip(m.stage, m.id)]
    m['done'] = (m.case_status == 'COMPLETED') & m.G_S.notna() & m.F.notna()
    return m


def gate(elig, truth_mask, hit, thr):
    """Card §5: UNRESOLVED share over eligible distinct cases, then n >= 10 rows, then the threshold (>=)."""
    cases = elig.drop_duplicates(['stage', 'id'])
    unres = float((~elig.groupby(['stage', 'id']).done.all()).mean()) if len(cases) else 0.0
    rows = elig[elig.done]
    sel = rows[truth_mask(rows)]
    n = len(sel)
    out = dict(n=n, eligible_cases=len(cases), unresolved_share=unres)
    if unres > UNRES_MAX or n < N_MIN:
        return dict(out, value=float(hit(sel).mean()) if n else None, threshold=thr, verdict='INCONCLUSIVE')
    v = float(hit(sel).mean())
    if thr is None:                                     # report-only part (R5)
        return dict(out, value=v, threshold=None, verdict='REPORT')
    return dict(out, value=v, threshold=thr, verdict='PASS' if v >= thr else 'FAIL')


def combine(parts):
    vs = [p['verdict'] for p in parts]
    return 'FAIL' if 'FAIL' in vs else ('PASS' if all(v == 'PASS' for v in vs) else 'INCONCLUSIVE')


def score(m):
    always = lambda r: np.ones(len(r), dtype=bool)
    AS = m[m.stage.isin(['asym', 'sobol'])]
    MID = m[m.stage == 'mid']
    res = {}
    onset = lambda r: (r.G_S - r.z_pred1).abs() <= 0.1
    parts, report = {}, {}
    for ratio in (10, 100):
        g = AS[np.isclose(AS.ratio, ratio)]
        for (lo, hi), thr in (((4, 7), 0.90), ((7, 15), 0.95), ((15, 40), 0.95)):
            parts[f'ratio{ratio} ({lo};{hi}]'] = gate(g[(g.h_Tint > lo) & (g.h_Tint <= hi)], always, onset, thr)
        report[f'ratio{ratio} (1;4]'] = gate(g[(g.h_Tint > 1) & (g.h_Tint <= 4)], always, onset, None)
    res['L73-1'] = dict(label='onset', parts=parts, report_only=report, verdict=combine(list(parts.values())))

    e = AS[(AS.delta != 0) & (AS.h_Tint > 7)]
    static_ok = lambda r: r.reg_static <= 0.1
    res['L73-2'] = dict(label='onset', **gate(e, always, static_ok, 0.90),
                        report_only={f'ratio{q}': gate(e[np.isclose(e.ratio, q)], always, static_ok, None) for q in (10, 100)})

    assert (MID.delta != 0).all(), 'MID must have delta != 0 (R4)'
    beats = lambda r: r.reg_M0_new <= r.reg_static - 0.1
    res['L73-3'] = dict(label='rủi ro', **gate(MID, always, beats, 0.50),
                        report_only={c: gate(MID[MID.combo == c], always, beats, None) for c in sorted(MID.combo.unique())})

    D = m[m.h_Tint <= 1]
    harm = lambda r: r.G_S < -0.5
    neg = lambda r: r.F < 0
    res['L73-4'] = dict(label='rủi ro', **gate(D, harm, neg, 0.70),
                        report_only={f'ratio{q}': gate(D[np.isclose(D.ratio, q)], harm, neg, None) for q in (10, 100)})
    return res


def main():
    m = load()
    res = score(m)
    status = m.drop_duplicates(['stage', 'id']).case_status.value_counts().to_dict()
    verdicts = {k: v['verdict'] for k, v in res.items()}
    res['counts'] = dict(case_status=status, verdicts=verdicts, PASS=sum(v == 'PASS' for v in verdicts.values()),
                         FAIL=sum(v == 'FAIL' for v in verdicts.values()),
                         INCONCLUSIVE=sum(v == 'INCONCLUSIVE' for v in verdicts.values()))
    (OUT / 'score_l73.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(res['counts'])


if __name__ == '__main__':
    main()
