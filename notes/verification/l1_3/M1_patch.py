# Doan Van Tai — isolated mutant, never imported by normal tests.
from fractions import Fraction as F
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_3_expected_cost as lesson

def bad_oracle(x, th):
    delta = lesson.expected_cost(x, 'Switch', th) - lesson.expected_cost(x, 'Stay', th)
    return ('Switch' if delta <= 0 else 'Stay'), delta
lesson.oracle = bad_oracle

raise SystemExit(pytest.main(sys.argv[1:]))
