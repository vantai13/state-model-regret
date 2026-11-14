"""Doan Van Tai — EV-B sanity: with no alarm (q = 0) the alarm machinery must reproduce the unconditioned contract cells
and the zero-fit read-outs of ctmc.evaluate_m0 [AI (Claude) theo ủy quyền 14/11/2026]."""
from fractions import Fraction as F

from experiments.explore_ctmc import ctmc as C
from experiments.ext_validity import alarm as A


def test_no_alarm_reproduces_contract(monkeypatch):
    monkeypatch.setattr(A, 'Q_ALARM', 0.0)
    case = dict(id='T', stratum='test', parameters=['7', '15/2', '1', '1/2'], hs=['1', '3'])
    hs = [F(1), F(3)]
    ev = C.evaluate(F(7), F(15, 2), F(1), F(1, 2), hs, disagree=False)
    m = C.evaluate_m0(F(7), F(15, 2), F(1), F(1, 2), hs)
    for t, p, er, mr in zip(A.truth_one(case), A.predict_one(case), ev['h'], m['h']):
        assert abs(t['G_S'] - er['G_S']) <= 1e-9 and abs(t['Gamma'] - er['Gamma']) <= 1e-9
        assert abs(p['F_old'] - mr['F_old']) <= 1e-12 and abs(p['F_new'] - mr['F_new']) <= 1e-12
