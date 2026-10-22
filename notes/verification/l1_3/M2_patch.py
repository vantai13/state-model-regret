# Doan Van Tai — isolated mutant, never imported by normal tests.
from fractions import Fraction as F
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_3_expected_cost as lesson

def bad_futures(x, th):
    for seq, pr in lesson.mode_paths(x[2], th['H'], th['p_onon'], th['p_offoff']):
        yield [lesson._rate(m, th) for m in seq[1:]], pr
lesson.futures = bad_futures

raise SystemExit(pytest.main(sys.argv[1:]))
