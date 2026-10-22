# Doan Van Tai — isolated mutation, no repository copy.
import sys
import inspect
from fractions import Fraction as F
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_6_belief as lesson

original = lesson.m0_cost
lesson.m0_cost = lambda x, action, th: original(x,action,dict(th,rate_off=0))

raise SystemExit(pytest.main(sys.argv[1:]))
