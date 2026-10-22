# Doan Van Tai — isolated mutant; normal source is unchanged.
import sys
from fractions import Fraction as F
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
sys.path.insert(0, '/home/vantai/state-model-regret/tests')
from experiments.lessons import l1_5_identity as identity

identity.belief_average = lambda belief, values: sum(values[x] for x in belief)/F(len(belief))

raise SystemExit(pytest.main(sys.argv[1:]))
