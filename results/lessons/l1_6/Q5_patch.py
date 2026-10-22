# Doan Van Tai — isolated mutation, no repository copy.
import sys
import inspect
from fractions import Fraction as F
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_6_belief as lesson

original = lesson.belief
lesson.belief = lambda history, th, prior_on: original(history,th,F(1,2))

raise SystemExit(pytest.main(sys.argv[1:]))
