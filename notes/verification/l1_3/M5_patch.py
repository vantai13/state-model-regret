# Doan Van Tai — isolated mutant, never imported by normal tests.
from fractions import Fraction as F
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_3_expected_cost as lesson

def bad_expected_cost(x, action, th):
    costs = [lesson.two_queue_cost(x[:2], [th['bA']]*th['H'], bB,
             th['u'], th['cA'], th['cB'], action)[0] for bB, pr in lesson.futures(x, th)]
    return F(sum(costs), len(costs))
lesson.expected_cost = bad_expected_cost

raise SystemExit(pytest.main(sys.argv[1:]))
