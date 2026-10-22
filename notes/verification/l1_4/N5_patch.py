# Doan Van Tai — isolated mutation only.
import sys
import pytest
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.lessons import l1_4_factorial as factorial

def bad_cell_costs(J_stay, J_switch, gaps):
    costs = {'Stay': J_stay, 'Switch': J_switch}
    return {cell: min(J_stay, J_switch) if gap == 0 else costs[factorial.choose(gap)]
            for cell, gap in gaps.items()}
factorial.cell_costs = bad_cell_costs

raise SystemExit(pytest.main(sys.argv[1:]))
