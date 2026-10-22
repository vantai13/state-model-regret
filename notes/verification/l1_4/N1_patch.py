# Doan Van Tai — isolated mutation only.
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_4_factorial as factorial

original = factorial.contrasts
def bad_contrasts(*args):
    result = original(*args)
    result['Gamma'] = -result['Gamma']
    return result
factorial.contrasts = bad_contrasts

raise SystemExit(pytest.main(sys.argv[1:]))
