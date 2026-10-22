# Doan Van Tai — isolated intentional mutant.
import sys, inspect
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_7_streams as lesson

original = lesson.primitive_two_actions
def bad(root, episode, x, th, extra_draws):
    st, _ = original(root,episode,x,th,extra_draws)
    sw = lesson.background_B(x,th,lesson.stream(root,"future",episode,lesson.PATH["B"],1).random(th["H"]-1))
    return st,sw
lesson.primitive_two_actions = bad

raise SystemExit(pytest.main(sys.argv[1:]))
