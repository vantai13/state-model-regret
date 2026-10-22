"""Doan Van Tai — C/D/E scientific checks, including independent references."""
import math
from fractions import Fraction as F
from itertools import product

import numpy as np
import pytest

from smr.design import (can_idle, conditional_on, design_cells, diagnostic,
                        episode_law, reserved_coordinates, stationary_mass,
                        stationary_parameters, stationary_total)
from smr.exact import value_backward
from smr.thresholds import packet_denominator, to_ms_per_packet, verdict
from experiments.lessons.l1_2_queue import two_queue_cost
from tests.golden_phase1 import EXPECTED_COSTS


def idle_grid_check():
    rows = []
    for qa,qb,ca,cb,u in product((0,2,10),(0,2,10),(2,3),(2,3),(0,2)):
        for a0,a1,b0,b1 in product((0,1,4), repeat=4):
            mismatches = 0
            for switch in (False,True):
                predicted = can_idle(qa,[a0+(0 if switch else u),a1+(0 if switch else u)],ca)
                predicted |= can_idle(qb,[b0+(u if switch else 0),b1+(u if switch else 0)],cb)
                _,idles = two_queue_cost((qa,qb),[a0,a1],[b0,b1],u,ca,cb,
                                         'Switch' if switch else 'Stay')
                mismatches += predicted != any(idles)
            rows.append(dict(qA=qa,qB=qb,cA=ca,cB=cb,u=u,a0=a0,a1=a1,b0=b0,b1=b1,
                             action_mismatches=mismatches))
    return rows


def test_idle_reference_5832():
    rows = idle_grid_check()
    assert len(rows) == 5832 and sum(r['action_mismatches'] for r in rows) == 0


def test_minimum_path_matches_all_futures():
    assert not can_idle(2,[1],3)  # Touching zero alone is insufficient.
    for q,H,mode,u in product(range(5),range(1,5),(0,1),(0,2)):
        paths = [(mode,)+tail for tail in product((0,1),repeat=H-1)]
        brute = any(can_idle(q,[5*m+u for m in path],3) for path in paths)
        assert brute == can_idle(q,[5*mode+u]+[u]*(H-1),3)


@pytest.mark.parametrize('keep',(.5,.625,.9,.99))
def test_stationary_infinite_law(keep):
    assert stationary_total(keep) == pytest.approx(1,abs=1e-13)
    r,A = stationary_parameters(keep)
    on_total = stationary_mass(0,1,keep)+A*r*(1+r)*r/(1-r)
    assert on_total == pytest.approx(.5,abs=1e-13)
    for q in range(30):
        for mode in (0,1):
            incoming = 0
            # Independent one-step balance, including all predecessors of q=0.
            for previous in range(q+3):
                for old in (0,1):
                    if max(0, previous+(1 if old else -2)) == q:
                        incoming += stationary_mass(previous,old,keep)*(keep if mode==old else 1-keep)
            assert incoming == pytest.approx(stationary_mass(q,mode,keep),abs=1e-14)
    assert conditional_on(0,keep) == 1-keep
    assert conditional_on(10**9,keep) == conditional_on(1,keep)


@pytest.mark.parametrize('x,expected',EXPECTED_COSTS.items())
def test_backward_golden(x,expected):
    qa,qb,mode = x
    for switch in (False,True):
        A = value_backward(0 if switch else 2,2,3,{'a':1},{'a':{'a':F(1)}},[qa],F(1))
        B = value_backward(2 if switch else 0,2,3,{'on':5,'off':0},
                           {m:{n:F(1,2) for n in ('on','off')} for m in ('on','off')},[qb],F(1))
        assert A[qa,'a']+B[qb,mode] == expected[int(switch)]


def test_backward_forward_B16():
    from experiments.lessons.l1_8_forward_reference import propagate_B
    m,H,keep=16,32,(1+.25**(1/16))/2
    P={i:{j:keep if i==j else 1-keep for j in (0,1)} for i in (0,1)}
    for managed in (0,2):
        backward=value_backward(managed,H,3,{0:0,1:5},P,range(33),F(1,m*m))
        for q,mode in product(range(33),(0,1)):
            mass=np.zeros((33,2)); mass[q,mode]=1
            _,forward=propagate_B(mass,H,keep,managed,m)
            assert float(backward[q,mode]) == pytest.approx(forward,abs=5e-13)


def test_additivity_with_correlated_background():
    # Perfect correlation; two possible common mode paths, not four independent paths.
    P={m:{n:F(1,2) for n in (0,1)} for m in (0,1)}
    for ma,mb in product((0,1), repeat=2):
        for switch in (False,True):
            A=value_backward(0 if switch else 2,2,3,{0:0,1:4},P,[2],F(1))
            B=value_backward(2 if switch else 0,2,3,{0:0,1:5},P,[1],F(1))
            joint=sum(F(1,2)*two_queue_cost((2,1),[4*ma,4*n],[5*mb,5*n],2,3,3,
                                           'Switch' if switch else 'Stay')[0] for n in (0,1))
            assert A[2,ma]+B[1,mb] == joint


def test_reachable_domain_not_artificially_capped():
    V=value_backward(0,3,1,{'a':3},{'a':{'a':1}},[0],1)
    assert V[0,'a'] == 2+4+6
    assert value_backward(0,0,1,{'a':3},{'a':{'a':1}},[0],1)[0,'a'] == 0
    with pytest.raises(ValueError):
        value_backward(0,1,1,{'a':3},{'a':{'a':.9}},[0],1)


def test_design_roles_and_coordinates():
    cells=design_cells()
    assert len(cells)==28 and len({c['id'] for c in cells})==28
    assert sum(c['role']=='main' for c in cells)==24
    assert len(reserved_coordinates())==16
    main={(c['z'],c['kappa'],c['eta']) for c in cells if c['role']=='main'}
    assert all((c['z'],c['kappa'],c['eta']) not in main for c in reserved_coordinates())


def test_conditional_D_and_shared_belief_interface():
    for cell in (design_cells()[0],design_cells()[12]):
        a=episode_law(cell); b=episode_law(dict(cell))
        assert np.array_equal(a[2],b[2]) and a[2].sum()==pytest.approx(1,abs=2e-14)
        # Queue/mode correlation is retained; posterior mode need not be 50/50.
        assert a[4] > .5 and conditional_on(int(cell['yB']/a[1]),a[4]) > .5


def test_negative_controls_and_scaling():
    for cell in (c for c in design_cells() if c['role']=='negative_control'):
        assert diagnostic(cell)['s_bt']==pytest.approx(1,abs=3e-14)
    cell=design_cells()[12]
    a=diagnostic(cell); b=diagnostic(cell,time_scale=F(3),rate_scale=F(7))
    assert a['s_bt']==b['s_bt'] and a['dt_over_Tmode']==b['dt_over_Tmode']


@pytest.mark.parametrize('g,label',((.04,'equivalent_point'),(-.04,'equivalent_point'),
                                    (.08,'practical_positive'),(-.08,'practical_negative'),
                                    (.05,'between_thresholds')))
def test_threshold_boundaries(g,label):
    assert verdict(g,8)==label


def test_threshold_guards_and_conversion():
    assert verdict(0,0)=='excluded_zero_reference'
    for args in ((math.nan,8),(1,-1),(1,8,.01,.005)):
        with pytest.raises(ValueError): verdict(*args)
    costs=[F(59,8),F(25,4),F(57,8),F(25,4)]
    gamma=costs[1]+costs[2]-costs[0]-costs[3]
    converted=[to_ms_per_packet(x,14) for x in costs]
    assert converted[1]+converted[2]-converted[0]-converted[3]==to_ms_per_packet(gamma,14)
    assert packet_denominator(4,5,2)==14
    with pytest.raises(ValueError): to_ms_per_packet(1,0)
