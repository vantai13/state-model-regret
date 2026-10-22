"""Doan Van Tai — L1.8D reporting units and deterministic point labels."""
import math


def verdict(gain, C_ref, eps_E=.005, eps_R=.01):
    """Point classification only; does not perform a statistical equivalence test."""
    if not all(math.isfinite(v) for v in (gain,C_ref,eps_E,eps_R)):
        raise ValueError('finite values required')
    if C_ref < 0 or not 0 < eps_E < eps_R:
        raise ValueError('C_ref >= 0 and 0 < eps_E < eps_R required')
    if C_ref == 0:
        return 'excluded_zero_reference'
    ratio = gain/C_ref
    if abs(ratio) <= eps_E:
        return 'equivalent_point'
    if ratio >= eps_R:
        return 'practical_positive'
    if ratio <= -eps_R:
        return 'practical_negative'
    return 'between_thresholds'


def to_ms_per_packet(cost_or_contrast, expected_packets):
    """Ratio of expectations; counts initial packets plus ALL horizon arrivals."""
    if not math.isfinite(cost_or_contrast) or not math.isfinite(expected_packets) or expected_packets <= 0:
        raise ValueError('finite numerator and positive expected packet count required')
    return 1000*cost_or_contrast/expected_packets


def packet_denominator(initial_expected, arrival_rate, horizon):
    if not all(math.isfinite(v) and v >= 0 for v in (initial_expected,arrival_rate,horizon)):
        raise ValueError('nonnegative finite inputs required')
    return initial_expected + arrival_rate*horizon
