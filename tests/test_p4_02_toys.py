"""Doan Van Tai — L4.2 exact goldens; AI-run checks, not author hand work."""
from fractions import Fraction as F
import importlib.util
from pathlib import Path

import pytest

from experiments.P4_02_reading.toys import TOYS, TOY_B, cells, cls, endpoint_cost

EXPECTED = {
    'T-A': ((F(10), F(10), F(19, 2), F(19, 2)), (F(1,2),F(0),F(0),F(1,2)), 'A'),
    'T-AB': ((F(11), F(10), F(21, 2), F(10)), (F(1,2),F(1),F(-1,2),F(0)), 'AB'),
    "T-C'": ((F(10), F(10), F(21, 2), F(10)), (F(-1,2),F(0),F(1,2),F(0)), 'C'),
}


@pytest.mark.parametrize('name', TOYS)
def test_toy_table(name):
    c=cells(*TOYS[name])
    losses, contrasts, label=EXPECTED[name]
    assert tuple(c[k] for k in ('L00','L01','L10','L11')) == losses
    assert tuple(c[k] for k in ('GS','GM','Gam','GS_M1')) == contrasts
    assert cls(c)==label


@pytest.mark.parametrize('name', TOYS)
def test_identities(name):
    c=cells(*TOYS[name])
    assert min(c[k] for k in ('GM','GSM','GS_M1','GM_S1'))>=0
    assert c['Gam']==c['GS_M1']-c['GS']==c['GM_S1']-c['GM']
    assert c['GS_M1']==min(c['P'],c['N'])  # one observation only
    assert c['Gam']>=-min(c['GS'],c['GM'])
    if c['GS']<0: assert c['Gam']>=-c['GS']


def test_mutant_mechanism():
    # Input perturbation demonstration, not a claim that implementation mutants were killed.
    assert cls(cells((1,1),(-3,1)))=='AB'
    assert cls(cells((1,1),(-3,4)))=='C'


def test_mutant_tie_rule():
    assert cls(cells((1,1),(-3,3),tie_stay=True))=='C'
    assert cls(cells((1,1),(-3,3),tie_stay=False))=='AB'


def t07_reference():
    path=Path(__file__).with_name('test_population_toys.py')
    spec=importlib.util.spec_from_file_location('l42_t07_reference',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('name', TOYS)
def test_matches_existing_t07_exact_reference(name):
    ref=t07_reference()
    d,dh=TOYS[name]
    plant=ref.one_snapshot(J={i:F(10) for i in range(2)},Delta=dict(enumerate(d)),Dhat=dict(enumerate(dh)))
    c=cells(d,dh)
    assert tuple(ref.cells(plant)[k] for k in ('00','01','10','11'))==tuple(c[k] for k in ('L00','L01','L10','L11'))


def test_fourth_B_example_and_fixed_action_errors():
    b=cells(*TOY_B)
    assert cls(b)=='B' and (b['GS'],b['GM'],b['Gam'])==(0,1,0)
    ab,harm=(cells(*TOYS[k]) for k in ('T-AB',"T-C'"))
    assert ab['a10']==harm['a10'] and ab['L10']==harm['L10']
    assert TOYS['T-AB'][1]!=TOYS["T-C'"][1]  # numerical prediction errors differ


def test_population_S10_requires_average_of_conditional_minima():
    ref=t07_reference()
    plant=dict(p={'y1':F(1,2),'y2':F(1,2)},D={'y1':{0:F(1)},'y2':{1:F(1)}},
               J={0:F(10),1:F(10)},Delta={0:F(1),1:F(-1)},Dhat={0:F(1),1:F(-1)})
    assert ref.contrasts(ref.cells(plant))['GS_M1']==0
    assert min(F(1,2),F(1,2))==F(1,2)  # min of unconditional P,N would be wrong


@pytest.mark.parametrize('name',TOYS)
def test_negative_interaction_requires_both_gains(name):
    c=cells(*TOYS[name]); eps=F(1,2)
    if c['Gam']<=-eps: assert min(c['GS'],c['GM'])>=eps
    if min(c['GS'],c['GM'])<eps: assert c['Gam']>-eps


def test_time_and_rate_homogeneity_with_reflection_and_scaled_initial_backlog():
    rates=(2,-4,3,0,-2)
    q,c=endpoint_cost(rates,F(1,4),F(3,4))
    qt,ct=endpoint_cost(rates,F(3,4),F(9,4))
    qr,cr=endpoint_cost([5*r for r in rates],F(1,4),F(15,4))
    assert qt==tuple(3*x for x in q) and ct==9*c
    assert qr==tuple(5*x for x in q) and cr==5*c


def test_fixed_dt_and_fixed_buffer_do_not_inherit_scaling():
    q,c=endpoint_cost([2]*4,F(1,2))
    qt,ct=endpoint_cost([2]*4,F(1))
    assert qt[-1]==2*q[-1] and ct==4*c
    assert endpoint_cost([2]*8,F(1,2))[1]!=4*c  # keep dt fixed, different endpoint error
    assert endpoint_cost([2]*4,F(1),buffer=4)[1]!=4*c


def test_continuous_ramp_example_differs_from_endpoint_sum():
    # Analytic integral q(t)=2t: C(h)=h^2. Finite endpoint sums exceed it.
    assert (F(2)**2,F(4)**2)==(4,16)
    assert endpoint_cost([2]*4,F(1,2))[1]==5
    assert endpoint_cost([2]*4,F(1))[1]==20


def test_zero_reference_does_not_get_a_percentage_class():
    with pytest.raises(ValueError,match='positive Cref'):
        cls(cells((0,0),(0,0),js=F(0)))
