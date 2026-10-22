# Doan Van Tai — isolated mutation, no repository copy.
import sys
import inspect
from fractions import Fraction as F
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_6_belief as lesson

source = inspect.getsource(lesson.belief)
old = 'return {state: p/evidence for state, p in masses.items()}'
assert source.count(old) == 1
exec(source.replace(old, 'return masses'), lesson.__dict__)

raise SystemExit(pytest.main(sys.argv[1:]))
