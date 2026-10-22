# Doan Van Tai — isolated mutation, no repository copy.
import sys
import inspect
from fractions import Fraction as F
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_6_belief as lesson

original = lesson.predict
def bad_predict(b, action, model, th):
    if model == 'M1':
        b = {x: F(1,len(b)) for x in b}
    return original(b, action, model, th)
lesson.predict = bad_predict

raise SystemExit(pytest.main(sys.argv[1:]))
