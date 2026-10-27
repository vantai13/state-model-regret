"""Doan Van Tai — reproduce L1.8B synthetic refinement using the new engine.

The L1.8B D is a teaching initialization, not any named v1.2 grid cell.
"""
from fractions import Fraction as F

import numpy as np

from experiments.lessons.l1_8_refinement import params_at, episode_distribution
from experiments.A00_engine.physical import side_from_law
from experiments.A00_engine.evaluate import evaluate_sides


def solve_toy_level(ref):
    p = params_at(ref, dtype=np.longdouble)
    D = episode_distribution(p)
    A_mass = np.zeros_like(D)
    A_mass[2 * ref] = [.5, .5]
    keep = F(str(p['p_onon']))
    # Finite-law rounded input; this does not certify a transcendental R2 limit.
    law_error = float(32 * (len(D) + 2) * ref * np.finfo(np.longdouble).eps)
    A, _ = side_from_law(F(1, ref), A_mass, rates=(F(1), F(1)), u_stay=F(2), u_switch=F(0),
                          capacity=F(3), H=2 * ref, dt=F(1, ref), keep=keep, D_error=law_error)
    B, _ = side_from_law(F(1, ref), D, rates=(F(0), F(5)), u_stay=F(0), u_switch=F(2),
                          capacity=F(3), H=2 * ref, dt=F(1, ref), keep=keep, D_error=law_error)
    return evaluate_sides(A, B, refinement=ref, dt=F(1, ref))
