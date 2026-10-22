# Doan Van Tai — isolated mutant, never imported by normal tests.
from fractions import Fraction as F
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_3_expected_cost as lesson

def bad_mode_paths(m0, n, p_onon, p_offoff):
    paths = [((m0,), F(1))]
    for _ in range(n):
        nxt = []
        for seq, pr in paths:
            last = seq[-1]
            keep = p_onon if last == 'on' else p_offoff
            other = 'off' if last == 'on' else 'on'
            for mode, pm in ((last, keep), (other, 1-keep)):
                if pm > 0:
                    nxt.append((seq+(mode,), pm))
        paths = nxt
    return paths
lesson.mode_paths = bad_mode_paths

raise SystemExit(pytest.main(sys.argv[1:]))
