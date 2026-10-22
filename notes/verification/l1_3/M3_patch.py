# Doan Van Tai — isolated mutant, never imported by normal tests.
from fractions import Fraction as F
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_3_expected_cost as lesson

def bad_episodes(y, tau, th, prior_on):
    out = {}
    for initial, p0 in (('on', prior_on), ('off', 1-prior_on)):
        if p0 == 0:
            continue
        for seq, pr in lesson.mode_paths(initial, tau, th['p_onon'], th['p_offoff']):
            x = (*y, seq[-1])
            out[x] = out.get(x, 0) + p0*pr
    return out
lesson.generate_episodes = bad_episodes

raise SystemExit(pytest.main(sys.argv[1:]))
