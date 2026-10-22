# Doan Van Tai — isolated mutation only.
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_4_factorial as factorial

original = factorial.contrasts
def bad_contrasts(L00, L10, L01, L11):
    result = original(L00, L10, L01, L11)
    result['G_S|M1'] = L00-L01
    return result
factorial.contrasts = bad_contrasts

raise SystemExit(pytest.main(sys.argv[1:]))
