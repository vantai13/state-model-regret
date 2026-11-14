"""Doan Van Tai — tests for csw_harm [AI (Claude) theo ủy quyền 14/11/2026]. No truth of the scored panel."""
import csv
import json
from fractions import Fraction as F

from experiments.explore_ctmc import ctmc as C
from experiments.explore_ctmc import csw_harm as H


def test_panel_is_new_and_in_harm_strata():
    seen = H.seen_all()
    cases = json.loads(H.CASES.read_text())
    keys = [tuple(F(x) for x in c['parameters'][:4]) for c in cases]
    assert len(cases) == sum(H.COUNTS.values()) and len(set(keys)) == len(keys) and not set(keys) & seen
    assert all((c['x'] <= -0.1) if c['stratum'] == 'neg' else (c['x'] >= 0.4) for c in cases)


def test_predictions_reproduce_bitwise():
    case = json.loads(H.CASES.read_text())[0]
    with H.PRED.open() as f:
        saved = [r for r in csv.DictReader(f) if r['id'] == case['id']]
    again = H._predict_one(case)
    assert len(saved) == len(again) == len(H.C_GRID) * len(H.H_MULT)
    for a, b in zip(saved, again):
        assert float(a['z_pred1']) == b['z_pred1'] and a['h_mult'] == b['h_mult']


def test_mc_units_rule():
    u = H.mc_units()
    assert len(u) == H.MC_UNITS and all(c > 0 for _, c, _ in u)
    assert u == H.mc_units()


def test_share_control_is_not_vacuous():
    """The per-h M0 Switch shares of evaluate_m0 (prediction side) equal those of evaluate (truth side) with c > 0."""
    lamA, lamB, u, kappa, c = F(7), F(15, 2), F(1), F(1, 2), F(1, 2)
    hs = [F(1), F(3)]
    m = C.evaluate_m0(lamA, lamB, u, kappa, hs, c=c, allow_csw=True)
    ev = C.evaluate(lamA, lamB, u, kappa, hs, c=c, disagree=False, allow_csw=True)
    for pm, pe in zip(m['h'][:-1], ev['h']):
        assert abs(pm['F_new'] - pe['shares']['M0_new']) <= 1e-12 and abs(pm['F_old'] - pe['shares']['M0_old']) <= 1e-12
    assert abs(m['z_inf'] - ev['asymptotic']['z_inf']) <= 1e-9
