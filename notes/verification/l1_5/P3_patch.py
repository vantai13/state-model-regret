# Doan Van Tai — isolated mutant; normal source is unchanged.
import sys
from fractions import Fraction as F
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
sys.path.insert(0, '/home/vantai/state-model-regret/tests')
from experiments.lessons import l1_5_identity as identity

identity.i_delta = lambda d00, d10, d01, d11: d11+d10-d01+d00

raise SystemExit(pytest.main(sys.argv[1:]))
