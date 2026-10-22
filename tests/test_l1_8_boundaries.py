"""Doan Van Tai — targeted dimensional, rounding, fluid and persistence checks."""
import math
from dataclasses import replace
from fractions import Fraction as F
from itertools import product

import pytest
from experiments.lessons.l1_8_slots import (
    ANCHOR_A, ANCHOR_B, CANDIDATE_DT, T_mode_from_lambda, anchor_card,
    p_stay, persistence_R1, persistence_R2, to_slots,
)
from experiments.lessons.l1_8_reference import boundary_comparison, fluid_interval


def test_physical_anchor_units_and_rounding_are_exact():
    a,b=(anchor_card(x,CANDIDATE_DT[x.name]) for x in (ANCHOR_A,ANCHOR_B))
    assert (a['t_pkt_s'],a['capacity_packet_slot'],a['background_pre_packet_slot'])==(F(3,250000),10,8)
    assert (a['age_slots'],a['age_represented_s'],a['age_error_relative'],a['H'])==(42,F(63,12500),F(1,125),50)
    assert a['T_drain_pre_B_s']==F(3,500) and a['z_pre_represented']==F(25,21)
    assert a['T_mode_s'] is None and a['T_drain_post_B_switch_s'] is None
    assert (b['age_slots'],b['age_represented_s'],b['age_error_relative'],b['H'])==(17,F(51,250),F(1,50),50)
    assert (b['T_drain_pre_B_s'],b['T_drain_post_B_switch_s'],b['h_over_post_drain'])==(F(3,5),F(6,5),F(1,2))
    assert b['zone_requested'].startswith('①') and b['zone_represented'].startswith('②')


def test_round_trip_and_ties_to_even_and_explicit_zero_age():
    for dt,n,offset in product((F(3,250),F(3,500),F(3,1000)),range(1,101),(F(-49,100),F(0),F(49,100))):
        seconds=(n+offset)*dt
        count,error=to_slots(seconds,dt)
        assert count==n and error==count*dt-seconds and abs(error)<=dt/2
    assert to_slots(F(5,2),F(1))==(2,F(-1,2))
    assert to_slots(F(7,2),F(1))==(4,F(1,2))
    assert to_slots(0,F(1),allow_zero=True)==(0,0)
    for seconds in (0,F(1,2),F(49,100)):
        with pytest.raises(ValueError): to_slots(seconds,F(1))


def test_invalid_physical_inputs_are_rejected():
    for bad in (0,-1,math.nan,math.inf,True):
        with pytest.raises(ValueError): to_slots(1,bad)
        with pytest.raises(ValueError): persistence_R2(bad,.1)
        with pytest.raises(ValueError): persistence_R2(.01,bad)
    for bad in (-1,math.inf,math.nan,True):
        with pytest.raises(ValueError): to_slots(bad,1)
    for bad in (-2,2,math.nan,math.inf,True):
        with pytest.raises(ValueError): p_stay(bad)
    for bad in (-1,0,1,math.nan,math.inf):
        with pytest.raises(ValueError): T_mode_from_lambda(bad,1)
    with pytest.raises(ValueError): persistence_R1(.2,.1)
    assert p_stay(-1)==0 and p_stay(1)==1


def test_R2_stationarity_inverse_and_semigroup_grid():
    for dt,T in product((.00012,.003,.006,.012),(.05,.1,.5)):
        lam=persistence_R2(dt,T)
        p=p_stay(lam)
        ph=p_stay(persistence_R2(dt/2,T))
        assert T_mode_from_lambda(lam,dt)==pytest.approx(T,rel=1e-12)
        assert p==pytest.approx(ph**2+(1-ph)**2,rel=1e-12)
        assert .5*p+.5*(1-p)==pytest.approx(.5)


def test_R1_is_an_active_negative_control_for_semigroup():
    p=p_stay(persistence_R1(.012,.1))
    half=p_stay(persistence_R1(.006,.1))
    assert p==pytest.approx(.88)
    assert half**2+(1-half)**2==pytest.approx(.8872)
    assert not math.isclose(p,half**2+(1-half)**2,rel_tol=1e-12)
    assert .76**17 < .88**34 < .94**68 < math.exp(-4.08)


def test_R2_sampled_run_length_exceeds_true_holding_time():
    T,dt=.1,.012
    assert dt/(1-p_stay(persistence_R1(dt,T)))==pytest.approx(T)
    assert dt/(1-p_stay(persistence_R2(dt,T)))==pytest.approx(.11247954,rel=0,abs=5e-9)
    assert T_mode_from_lambda(.25,1)==pytest.approx(-2/math.log(.25))
    assert persistence_R2(.5,T_mode_from_lambda(.25,1))==pytest.approx(.5)


def test_endpoint_cost_converges_from_both_directions():
    for dt,fall,rise in ((F(1),F(0),F(2)),(F(1,2),F(1,2),F(3,2)),(F(1,4),F(3,4),F(5,4)),(F(1,8),F(7,8),F(9,8))):
        a=boundary_comparison(F(2),[F(1)]*int(1/dt),F(3),dt)
        b=boundary_comparison(F(0),[F(5)]*int(1/dt),F(3),dt)
        assert sum(r['fluid_area'] for r in a)==sum(r['fluid_area'] for r in b)==1
        assert sum(r['d13'] for r in a)==fall and sum(r['d13'] for r in b)==rise


def test_fluid_boundary_and_crossing_correction_on_grid():
    for q0,rate,service,dt in product((0,1,2,5),(0,1,3,5),(1,3),(F(1),F(1,2),F(1,4))):
        row=boundary_comparison(F(q0),[F(rate)],F(service),dt)[0]
        assert row['crossing_correction']>=0
        crosses=0<q0<(service-rate)*dt
        if not crosses: assert row['crossing_correction']==0
    row=boundary_comparison(F(1),[F(0)],F(2),F(1))[0]
    assert (row['fluid_area'],row['error'],row['boundary_term'],row['crossing_correction'])==(F(1,4),F(-1,4),F(-1,2),F(1,4))


def test_cumulative_cost_is_not_a_time_average_and_non_draining_loads():
    assert fluid_interval(F(10),F(1),F(3),F(10))==(0,25)
    assert fluid_interval(F(10),F(1),F(3),F(20))==(0,25)
    assert F(25,10)==F(5,2) and F(25,20)==F(5,4)
    for rho in (F(1),F(6,5)):
        card=anchor_card(replace(ANCHOR_B,rho_post_B_switch=rho),CANDIDATE_DT['b'])
        assert card['post_load_status']=='non_draining' and math.isinf(card['T_drain_post_B_switch_s'])
        assert card['h_over_post_drain'] is None


def test_time_rate_rescaling_preserves_slot_coordinates_and_ratios():
    base=anchor_card(ANCHOR_B,CANDIDATE_DT['b'])
    for k in (F(1,10),F(1),F(10),F(100)):
        scaled=replace(ANCHOR_B,link_bps=ANCHOR_B.link_bps*k,
                       age_plus_act_s=ANCHOR_B.age_plus_act_s/k,
                       horizon_s=ANCHOR_B.horizon_s/k,T_mode_s=ANCHOR_B.T_mode_s/k)
        card=anchor_card(scaled,CANDIDATE_DT['b']/k)
        for key in ('capacity_packet_slot','background_pre_packet_slot','age_slots','H',
                    'z_pre_represented','h_over_post_drain','mode_over_age'):
            assert card[key]==base[key]
        assert card['lambda_R2']==pytest.approx(base['lambda_R2'],rel=1e-12)
        assert card['T_drain_pre_B_s']==base['T_drain_pre_B_s']/k
