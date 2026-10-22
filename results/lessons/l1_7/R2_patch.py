# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

def bad(root, episode, x, th, extra_draws):
    st = lesson.background_B(x,th,lesson.future_rng(root,episode,"B").random(th["H"]-1))
    rng = lesson.future_rng(root,episode,"B")
    rng.random(extra_draws)
    return st,lesson.background_B(x,th,rng.random(th["H"]-1))
lesson.primitive_two_actions = bad

raise SystemExit(pytest.main(sys.argv[1:]))
