"""Doan Van Tai — L1.8 Part A physical-seconds to slots, without contract freeze.

Rounding: nearest, Python round ties-to-even. Return signed error in seconds.
R2 describes a symmetric CTMC skeleton; it does not integrate within-slot traffic.
Candidates/anchors are teaching illustrations, not measured network parameters.
"""
import math
from dataclasses import dataclass
from fractions import Fraction as F

from experiments.lessons.l0_6_timescale import drain_time_s, tx_time_s, zone


def _positive(value, name):
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')


def to_slots(seconds: float, dt: float, *, allow_zero: bool = False) -> tuple[int, float]:
    """Quantize duration; explicit zero-age exception for D8, no clamping."""
    _positive(dt, 'dt')
    if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds < 0:
        raise ValueError('seconds must be nonnegative and finite')
    if seconds == 0 and allow_zero:
        return 0, seconds
    n = round(seconds / dt)
    if n < 1:
        raise ValueError('duration rounds to zero slots: dt is too coarse')
    return n, n * dt - seconds


def persistence_R2(dt: float, T_mode: float) -> float:
    """Symmetric CTMC lambda; finite positive mean holding time in seconds."""
    _positive(dt, 'dt')
    _positive(T_mode, 'T_mode')
    return math.exp(-2 * dt / T_mode)


def p_stay(lam: float) -> float:
    """Symmetric two-state DTMC, allowing lambda in [-1,1]."""
    if isinstance(lam, bool) or not math.isfinite(lam) or not -1 <= lam <= 1:
        raise ValueError('lambda must be finite and in [-1,1]')
    return (1 + lam) / 2


def T_mode_from_lambda(lam: float, dt: float) -> float:
    """Inverse for finite positive symmetric holding time; exclude identity/limits.

    lambda=1 has degenerate embedding Q=0 (infinite holding time), not accepted.
    lambda=0 is not attainable with finite CTMC rates at positive dt.
    """
    _positive(dt, 'dt')
    if isinstance(lam, bool) or not math.isfinite(lam) or not 0 < lam < 1:
        raise ValueError('finite positive T_mode requires 0 < lambda < 1')
    return -2 * dt / math.log(lam)


def persistence_R1(dt: float, T_mode: float) -> float:
    """Geometric-slot control: preserves mean sampled run length, not semigroup."""
    _positive(dt, 'dt')
    _positive(T_mode, 'T_mode')
    leave = dt / T_mode
    if leave > 1:
        raise ValueError('R1 requires dt/T_mode <= 1')
    return 1 - 2 * leave


@dataclass(frozen=True)
class PhysicalAnchor:
    name: str
    link_bps: F
    packet_bytes: F
    qB0: F
    rho_pre_B: F
    age_plus_act_s: F
    horizon_s: F
    rho_post_B_switch: F | None = None
    T_mode_s: F | None = None


ANCHOR_A = PhysicalAnchor('a', F(10**9), F(1500), F(100), F(4,5), F(1,200), F(3,500))
ANCHOR_B = PhysicalAnchor('b', F(10**7), F(1500), F(100), F(4,5), F(1,5), F(3,5), F(9,10), F(1,10))
CANDIDATE_DT = {'a': F(3,25000), 'b': F(3,250)}


def anchor_card(anchor: PhysicalAnchor, dt):
    """Single conversion entry: declare physical quantities, derive slot parameters.

    Mean-load illustrations do not specify a complete ON/OFF arrival-rate law.
    age_plus_act is a timescale diagnostic, not simulated delayed actuation.
    """
    for name in ('link_bps','packet_bytes','age_plus_act_s','horizon_s'):
        _positive(getattr(anchor,name),name)
    if anchor.qB0 < 0 or not math.isfinite(anchor.qB0):
        raise ValueError('qB0 must be finite and nonnegative')
    for rho in (anchor.rho_pre_B,anchor.rho_post_B_switch):
        if rho is not None and (not math.isfinite(rho) or rho < 0):
            raise ValueError('rho must be finite and nonnegative')
    age_n,age_error = to_slots(anchor.age_plus_act_s,dt)
    H,h_error = to_slots(anchor.horizon_s,dt)
    t_pkt = tx_time_s(anchor.packet_bytes,anchor.link_bps)
    mu = F(1)/t_pkt
    pre = drain_time_s(anchor.qB0,anchor.link_bps,anchor.rho_pre_B,anchor.packet_bytes)
    post = None if anchor.rho_post_B_switch is None else drain_time_s(
        anchor.qB0,anchor.link_bps,anchor.rho_post_B_switch,anchor.packet_bytes)
    rounded_age = age_n*dt
    lam = None if anchor.T_mode_s is None else persistence_R2(dt,anchor.T_mode_s)
    return dict(anchor=anchor.name,queue='B',dt_candidate_s=dt,t_pkt_s=t_pkt,mu_packet_s=mu,
                capacity_packet_slot=mu*dt,background_pre_packet_slot=anchor.rho_pre_B*mu*dt,
                managed_added_packet_s=None if anchor.rho_post_B_switch is None else (anchor.rho_post_B_switch-anchor.rho_pre_B)*mu,
                age_requested_s=anchor.age_plus_act_s,age_slots=age_n,age_represented_s=rounded_age,
                age_error_s=age_error,age_error_relative=age_error/anchor.age_plus_act_s,
                h_requested_s=anchor.horizon_s,H=H,h_represented_s=H*dt,h_error_s=h_error,
                T_drain_pre_B_s=pre,T_drain_post_B_switch_s=post,
                z_pre_requested=pre/anchor.age_plus_act_s,z_pre_represented=pre/rounded_age,
                zone_requested=zone(pre,anchor.age_plus_act_s),zone_represented=zone(pre,rounded_age),
                h_over_post_drain=None if post is None or not math.isfinite(post) or post==0 else H*dt/post,
                post_load_status='unspecified' if post is None else ('non_draining' if not math.isfinite(post) else 'draining'),
                T_mode_s=anchor.T_mode_s,lambda_R2=lam,p_stay_R2=None if lam is None else p_stay(lam),
                mode_over_age=None if anchor.T_mode_s is None else anchor.T_mode_s/rounded_age,
                mode_over_age_requested=None if anchor.T_mode_s is None else anchor.T_mode_s/anchor.age_plus_act_s,
                dt_over_mode=None if anchor.T_mode_s is None else dt/anchor.T_mode_s,
                dt_over_age=dt/anchor.age_plus_act_s,dt_over_age_represented=dt/rounded_age,
                dt_over_drain_pre=None if not math.isfinite(pre) or pre==0 else dt/pre,
                dt_over_h=dt/anchor.horizon_s,
                source='T00 + supplied L1.8 Part A; illustrative configuration, not measured use case')
