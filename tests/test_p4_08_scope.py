"""L4.8: unit scaling, finite-horizon validity and missing empirical evidence."""
from fractions import Fraction as F

import pytest

from experiments.P4_08_scope import project_domain as D


def test_independent_physical_units_known_answer():
    x=D.project(['7','8','3/10','1/2','4','0'],capacity_bps='10000000000',tau_s='1/100',ref=4)
    assert x['managed_bps']==1e9
    assert x['T_mode_s']==.003 and x['h_s']==.04
    assert x['bytes_per_model_backlog_unit']==1_250_000
    assert x['bit_seconds_per_model_cost_unit']==100_000
    assert x['H']==1920
    assert x['physical_tau_measured'] is False
    assert x['empirical_mapping_status']=='UNRESOLVED'


def test_finite_horizon_overload_valid_but_outside_current_native_subset():
    x=D.project(['6','17/2','3/10','1','4','0'],capacity_bps='10000000000',tau_s='1/100',ref=4)
    assert x['rho_B_post']==1.05
    assert x['physical_valid'] is True
    assert x['current_native_supported'] is False


def test_horizon_is_not_silently_ceiled():
    x=D.project(['7','8','3/10','1/2','123/1000','0'],capacity_bps='10000000000',tau_s='1/100',ref=4)
    assert x['H'] is None and x['horizon_admissible'] is False
    assert x['h_s']==.00123


@pytest.mark.parametrize('capacity,tau',[('0','1'),('10','0'),('-1','1'),('10','-1'),(10.,'1')])
def test_bad_or_inexact_anchor_rejected(capacity,tau):
    with pytest.raises(ValueError):D.scales(capacity,tau)


def test_backlog_and_cost_do_not_scale_like_rates_alone():
    a=D.scales('10000000000','1/100')
    b=D.scales('10000000000','1/50')
    assert a['rate']==b['rate']
    assert b['backlog']==2*a['backlog']
    assert b['cost']==4*a['cost']


def test_lindley_recurrence_and_cost_homogeneity_exact():
    # A finite predetermined teaching path, not a research simulation.
    mult=D.scales('10000000000','1/100')
    rates=list(map(F,(2,14,2,2)))
    q0,q1=F(1),mult['backlog']
    cost0=cost1=F(0)
    for rate in rates:
        q0=max(F(0),q0+(rate+1-10)*F(1,10))
        q1=max(F(0),q1+((rate+1)*mult['rate']-F(10)*mult['rate'])*F(1,10)*mult['time'])
        assert q1==q0*mult['backlog']
        cost0+=q0*F(1,10)
        cost1+=q1*F(1,10)*mult['time']
    assert cost1==cost0*mult['cost']


def test_normalized_cost_difference_invariant_without_empirical_claim():
    # Given toy costs, scaling both numerator and denominator is pure units.
    before=list(map(F,('11','10','10.5','10')))
    after=[x*D.scales('10000000000','1/100')['cost'] for x in before]
    assert (before[0]-before[2])/before[3]==(after[0]-after[2])/after[3]


def test_primary_contract_is_not_relaxed_for_projection():
    with pytest.raises(ValueError,match='A not stable'):
        D.project(['9','8','3/10','1/2','4','0'],capacity_bps='10000000000',tau_s='1/100',ref=4)
    with pytest.raises(ValueError,match='primary requires'):
        D.project(['7','8','3/10','1/2','4','1'],capacity_bps='10000000000',tau_s='1/100',ref=4)
