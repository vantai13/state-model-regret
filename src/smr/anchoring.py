"""Doan Van Tai — v1.2 boundary-anchoring rule for the design grid.

Scientific purpose: place every design slice where the oracle decision is contested,
so that state-information value is not zero by construction (DL-038, v1.2 protocol).
Used by: experiments/lessons/run_v1_2.py. Metric: plant-only sign probabilities p_sw.
Inputs are ladder rows with p_low_<level>/p_high_<level>; no costs, margins or contrasts.
"""
from fractions import Fraction as F

BAND = (0.1, 0.9)
TARGETS = (0.3, 0.7)
WINDOW = 0.15


def midpoint(row, level):
    return (row[f'p_low_{level}'] + row[f'p_high_{level}']) / 2


def in_band(row, levels=(1, 2)):
    return all(row[f'p_low_{l}'] >= BAND[0] and row[f'p_high_{l}'] <= BAND[1] for l in levels)


def anchor(rows, target, window=WINDOW, levels=(1, 2)):
    """Apply the v1.2 rule to one slice ladder for one target.

    Choice: the ladder point whose coarse midpoint is closest to the target; ties go to the
    smaller lambdaA. Accepted iff the point's p interval lies inside [target-window,
    target+window] at every screen level. The rule never searches outside the ladder.

    Bracketing (reported, never used to accept): 'bracketed' if some ladder point lies at or
    below the target and some at or above it. Otherwise 'floor' (every point is above the
    target, so the crossing would need lambdaA below the physical floor) or 'ceiling'.
    """
    if not rows:
        raise ValueError('empty ladder')
    ladder = sorted(rows, key=lambda r: F(r['lambdaA']))
    best = min(ladder, key=lambda r: (abs(midpoint(r, 1) - target), F(r['lambdaA'])))
    accepted = all(best[f'p_low_{l}'] >= target - window and best[f'p_high_{l}'] <= target + window
                   for l in levels)
    below = any(midpoint(r, 1) <= target for r in ladder)
    above = any(midpoint(r, 1) >= target for r in ladder)
    bracketing = 'bracketed' if below and above else ('floor' if above else 'ceiling')
    return dict(lambdaA=F(best['lambdaA']), accepted=accepted, bracketing=bracketing,
                at_ladder_floor=F(best['lambdaA']) == F(ladder[0]['lambdaA']),
                at_ladder_ceiling=F(best['lambdaA']) == F(ladder[-1]['lambdaA']),
                p_coarse=midpoint(best, 1), deviation=abs(midpoint(best, 1) - target), row=best)
