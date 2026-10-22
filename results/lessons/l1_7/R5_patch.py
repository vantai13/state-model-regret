# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

original = lesson.stream
lesson.stream = lambda root,role,*index: original(root,role,*index[1:])

raise SystemExit(pytest.main(sys.argv[1:]))
