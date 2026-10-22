# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

lesson.predictor_rng = lambda root,episode: lesson.future_rng(root,episode,"B")

raise SystemExit(pytest.main(sys.argv[1:]))
