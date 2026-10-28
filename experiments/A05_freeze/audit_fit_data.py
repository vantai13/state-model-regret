"""Doan Van Tai — A04-only audit before A05-F; never loads held-out metadata."""
import csv
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np

from experiments.A03_card.grading import get, ratio, judge
from experiments.A05_freeze.ledger import contrasts, CONTRASTS

ROOT = Path(__file__).resolve().parents[2]


def audit():
    base = ROOT / 'results/A04/20261027_01'
    fine = json.loads((base/'grading_input.json').read_text())['fine']
    with (base/'main_final.csv').open() as handle:
        rows = list(csv.DictReader(handle))
    max_exact, max_float, violated, records = F(0), 0., [], []
    for row in rows:
        cid = row['cell']; r = fine[cid]
        C, ed, edh, en = map(F, (r['C_ref'], r['E_delta'], r['E_delta_hat'], r['E_neg']))
        t10 = F(r['G']['G_M_S1']) - en
        a00, a01 = int(edh < 0), int(ed < 0)
        l00, l01, l10, l11 = a00*ed, a01*ed, t10, -en
        expected = (l00-l10, l00-l01, l00-l11, l10+l01-l00-l11, l01-l11, l10-l11)
        exact_error = max(abs(x-F(r['G'][k]))/C for k,x in zip(CONTRASTS,expected))
        max_exact = max(max_exact, exact_error)
        s = [float(v/C) for v in (ed,edh,en,t10)]
        predicted = contrasts(s)
        max_float = max(max_float, max(abs(float(F(r['G'][k])/C)-v) for k,v in zip(CONTRASTS,predicted)))
        if en < max(0,-ed) or t10 < -en or t10 > ed+en:
            violated.append(cid)
        gm = ratio(get(r,'G_M'),get(r,'C_ref'))
        rr = ratio(get(r,'R00'),get(r,'C_ref'))
        records.append(dict(cell=cid, target_matches_a01=(int(F(row['targets'])==F('0.7'))==a01),
              nominal_GM_zero=F(r['G']['G_M'])==0,
              equivalent_certified=judge(gm,'<=',F(1,200))=='STANDS',
              practical_certified=judge(gm,'>=',F(1,100))=='STANDS',
              headroom_below_epsE=rr.hi < F(1,200),
              headroom_lower_pct=float(100*rr.lo),headroom_upper_pct=float(100*rr.hi),
              E_delta_hat=r['E_delta_hat'], a00=r['a00'],
              normalized_summaries=s, exact_decimal_identity_error=float(exact_error)))
    n = len(rows)
    return dict(responsible='Doan Van Tai', fit_cells=n, slices=len({r['slice'] for r in rows}),
          a01_target_matches=sum(r['target_matches_a01'] for r in records),
          nominal_GM_zero=sum(r['nominal_GM_zero'] for r in records),
          GM_equivalence_certified=sum(r['equivalent_certified'] for r in records),
          GM_practical_certified=sum(r['practical_certified'] for r in records),
          max_exact_decimal_identity_error=float(max_exact), max_float64_identity_error=max_float,
          nominal_feasibility_violations=violated,
          K5_headroom=[r for r in records if r['cell'] in ('M19','M20','M21','M22')],
          heuristic_K5_two_equivalence=float(F(36,38)**2),
          heuristic_four_nominal_zero=float(F(34,38)**4),
          heuristic_four_equivalence=float(F(36,38)**4),
          heuristic_scope='illustration under false exchangeability/independence; not a test probability',
          heldout_inputs_read=False, source_review_test_runtime='reviewer-reported 348/74s, not rerun here')


if __name__ == '__main__':
    result = audit()
    target = ROOT/'results/lessons/l3_6/preflight/a04_audit.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
