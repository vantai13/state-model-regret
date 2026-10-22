# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

original = lesson.background_B
lesson.background_B = lambda x,th,uniforms: original((x[0],x[1],"off"),th,uniforms)

raise SystemExit(pytest.main(sys.argv[1:]))
