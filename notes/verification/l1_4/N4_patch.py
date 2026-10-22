# Doan Van Tai — isolated mutation only.
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_4_factorial as factorial

def bad_additive(delta, e_S, e_M):
    return {'00': delta+e_S+e_M, '10': delta+e_S, '01': delta+e_M, '11': delta}
factorial.additive_cells = bad_additive

raise SystemExit(pytest.main(sys.argv[1:]))
