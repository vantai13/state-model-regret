# Doan Van Tai — isolated mutation, no repository copy.
import sys
import inspect
from fractions import Fraction as F
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_6_belief as lesson

source = inspect.getsource(lesson.belief)
old = 'if next_time in observations and observations[next_time] != (qA, qB):'
assert source.count(old) == 1
exec(source.replace(old, 'if False:'), lesson.__dict__)

raise SystemExit(pytest.main(sys.argv[1:]))
