"""Doan Van Tai — targeted L1.7 limits beyond the thirteen supplied cases."""
from fractions import Fraction as F
import numpy as np
import pytest
from experiments.lessons.l1_3_expected_cost import CANON
from experiments.lessons.l1_7_streams import (
    DEMO_ROOT, background_B, identity2_residual, mk_action, mode_path, path_costs,
    predictor_rng, stream,
)
from experiments.lessons.l1_7_reference import exact_pairs, leak_reference, shifted_pairs


def test_zero_idle_residual_does_not_prove_same_future():
    th = dict(CANON,H=4)
    a,b = [0,5,0,0],[0,0,5,5]
    assert a != b
    assert identity2_residual(path_costs((2,2,"off"),th,a,b)) == 0


def test_exact_reference_checks_leak_and_shifted_marginals():
    x = (2,2,"off")
    truth,_ = leak_reference(x,dict(CANON,H=3))
    assert (truth["oracle"],truth["leak"],truth["honest"],truth["honest_win_probability"]) == (F(31,4),F(13,2),F(65,8),F(1,4))
    paired,_ = exact_pairs(x,dict(CANON,H=6))
    shifted,_ = shifted_pairs(x,dict(CANON,H=6))
    assert paired["delta"] == shifted["delta"] == F(145,16)
    for key in ("mean_stay","mean_switch","var_stay","var_switch"):
        assert paired[key] == shifted[key]
    assert shifted["paired_variance"] > paired["independent_variance"] > paired["paired_variance"]


def test_schema_guards_and_horizon_one():
    for bad in (True,-1,"Switch",0.5):
        with pytest.raises(TypeError):
            stream(DEMO_ROOT,"future",bad)
    for args in (("other",[],F(1,2),F(1,2)),("off",[1],F(1,2),F(1,2)),("on",[],2,F(1,2))):
        with pytest.raises(ValueError):
            mode_path(*args)
    with pytest.raises(ValueError):
        background_B((2,2,"off"),CANON,[])
    with pytest.raises(ValueError):
        identity2_residual({"Stay":(0,[0]),"Switch":(0,[])})
    th = dict(CANON,H=1)
    assert background_B((2,2,"off"),th,[]) == [0]
    for bad in (0,True,1.5):
        with pytest.raises(ValueError):
            mk_action((2,2,"off"),th,predictor_rng(DEMO_ROOT,0),bad)


def test_predictor_samples_are_nested_and_role_alias_is_not_same_key():
    # A recorder proves the first K=1 sample is exactly the prefix of K=4.
    class Recorder:
        def __init__(self):
            self.rng = predictor_rng(DEMO_ROOT,37)
            self.draws = []
        def random(self,n):
            x = self.rng.random(n)
            self.draws.append(x)
            return x
    one,four = Recorder(),Recorder()
    for rng,K in ((one,1),(four,4)):
        mk_action((2,2,"off"),dict(CANON,H=3),rng,K)
    assert len(one.draws)==1 and len(four.draws)==4
    assert np.array_equal(one.draws[0],four.draws[0])
    # Merely aliasing a role code does not make (1,i) equal (1,i,B).
    short = np.random.default_rng(np.random.SeedSequence(DEMO_ROOT,spawn_key=(1,37))).random(8)
    long = np.random.default_rng(np.random.SeedSequence(DEMO_ROOT,spawn_key=(1,37,1))).random(8)
    assert not np.array_equal(short,long)
