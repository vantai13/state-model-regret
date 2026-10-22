"""Doan Van Tai — L1.4 exact two-by-two bookkeeping (contract D19).

The same contrasts apply to episode costs and their expectation. Decisions use
predicted gaps only; the evaluator scores them with true J afterwards. Additive
errors are a bookkeeping toy, not an implemented state estimator/response model.
Cost/gain units are inherited from J: packet·slot in the canonical example.
"""


def contrasts(L00, L10, L01, L11):
    """Return all six D19 contrasts, ordered by (state repair, model repair)."""
    return {
        "G_S": L00 - L10,
        "G_M": L00 - L01,
        "G_SM": L00 - L11,
        "Gamma": L10 + L01 - L00 - L11,
        "G_S|M1": L01 - L11,
        "G_M|S1": L10 - L11,
    }


def choose(delta_hat):
    """L1.4 decision rule D16: Switch iff predicted gap is strictly negative."""
    return "Switch" if delta_hat < 0 else "Stay"


def cell_costs(J_stay, J_switch, delta_hat_by_cell):
    """Score each cell using true J after choosing from its predicted gap."""
    true_cost = {"Stay": J_stay, "Switch": J_switch}
    return {cell: true_cost[choose(gap)] for cell, gap in delta_hat_by_cell.items()}


def gamma_coefficient(i00, i10, i01):
    """Gamma/margin for binary wrong-choice indicators, assuming i11=0."""
    return i10 + i01 - i00


def additive_cells(delta, e_S, e_M):
    """Predicted gaps: cell 10 has removed e_S; cell 01 has removed e_M."""
    return {"00": delta + e_S + e_M, "10": delta + e_M,
            "01": delta + e_S, "11": delta}


def table_from_additive(J_stay, J_switch, e_S, e_M):
    """Episode costs for the additive-error toy, using the fixed D16 tie rule."""
    return cell_costs(J_stay, J_switch, additive_cells(J_switch-J_stay, e_S, e_M))
