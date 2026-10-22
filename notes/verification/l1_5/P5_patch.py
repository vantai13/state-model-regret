# Doan Van Tai — isolated mutant; normal source is unchanged.
import sys
from fractions import Fraction as F
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
sys.path.insert(0, '/home/vantai/state-model-regret/tests')
from experiments.lessons import l1_5_identity as identity

def bad_per_state(belief, delta, m0):
    d01 = identity.belief_average(belief, m0)
    d00 = identity.belief_average(belief, m0)
    return {x: identity.i_delta(d00, m0[x], d01, delta[x]) for x in belief}
identity.i_delta_per_state = bad_per_state

raise SystemExit(pytest.main(sys.argv[1:]))
