# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

source = inspect.getsource(lesson.mode_path)
old = 'last if u < keep else'
assert source.count(old)==1
exec(source.replace(old,'last if u >= keep else'),lesson.__dict__)

raise SystemExit(pytest.main(sys.argv[1:]))
