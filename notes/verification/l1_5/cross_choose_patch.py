# Doan Van Tai — isolated mutant; normal source is unchanged.
import sys
from fractions import Fraction as F
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
sys.path.insert(0, '/home/vantai/state-model-regret/tests')
from experiments.lessons import l1_4_factorial
l1_4_factorial.choose = lambda gap: 'Switch' if gap <= 0 else 'Stay'
from experiments.lessons import l1_5_identity as identity

raise SystemExit(pytest.main(sys.argv[1:]))
