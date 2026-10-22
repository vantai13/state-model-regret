# Doan Van Tai — isolated mutation only.
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_4_factorial as factorial

factorial.choose = lambda gap: 'Switch' if gap <= 0 else 'Stay'

raise SystemExit(pytest.main(sys.argv[1:]))
