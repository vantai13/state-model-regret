# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

source = inspect.getsource(lesson.mk_action)
old = 'return choose(F(total, K))'
assert source.count(old)==1
exec(source.replace(old,'return choose(total)'),lesson.__dict__)

raise SystemExit(pytest.main(sys.argv[1:]))
