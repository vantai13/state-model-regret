# Doan Van Tai — isolated mutant; normal source is unchanged.
import sys
from fractions import Fraction as F
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
sys.path.insert(0, '/home/vantai/state-model-regret/tests')
from experiments.lessons import l1_5_identity as identity

def bad_f5(delta, predicted):
    wrong = abs(delta) if delta*predicted <= 0 else 0
    return wrong + (max(0, -delta) if predicted == 0 else 0)
identity.regret_identity = bad_f5

raise SystemExit(pytest.main(sys.argv[1:]))
