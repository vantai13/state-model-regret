# Doan Van Tai — isolated mutation, no repository copy.
import sys
import inspect
from fractions import Fraction as F
import pytest
sys.path.insert(0,'/home/vantai/state-model-regret')
from experiments.lessons import l1_6_belief as lesson

def bad_m0(x, action, th):
    pi = (1-th['p_offoff'])/(2-th['p_onon']-th['p_offoff'])
    mean = pi*th['rate_on']+(1-pi)*th['rate_off']
    bB = [th['rate_on'] if x[2] == 'on' else th['rate_off']] + [mean]*(th['H']-1)
    return lesson.two_queue_cost(x[:2], [th['bA']]*th['H'], bB, th['u'],th['cA'],th['cB'],action)[0]
lesson.m0_cost = bad_m0

raise SystemExit(pytest.main(sys.argv[1:]))
