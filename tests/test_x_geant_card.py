"""Doan Van Tai — synthetic sanity checks for experiments/letter/x_geant_card.py (Claude, 20/11/2026)."""
from experiments.letter import x_geant_card as K


def row(regime, rule, tau, h, date, gs, se=1.0, cref=1000.0, regret=0.1):
    return dict(set='X2', regime=regime, rule=rule, tau_s=tau, h_s=h, date=date, evaluable=True, G_S_Mbit_s=gs,
                G_S_SE_Mbit_s=se, C_ref_Mbit_s=cref, both_side_regret_pct=regret)


def test_g1_counts_correct_signs_and_resolution():
    signs = {('NEW1', 'TH_0.8', 300, 14400): -1, ('NEW1', 'TH_0.9', 300, 14400): 1}
    rows = [row('NEW1', 'TH_0.8', 300, 14400, d, -50 - d) for d in range(5)]
    rows += [row('NEW1', 'TH_0.9', 300, 14400, d, -40 - d) for d in range(5)]   # wrong sign, resolved
    r = K.evaluate(rows, signs)
    assert r['G1']['resolved'] == 2 and r['G1']['correct'] == 1 and r['G1']['verdict'] == 'NOT_EVALUABLE'


def test_unresolved_cell_is_not_counted():
    signs = {('NEW1', 'TH_0.8', 300, 14400): -1}
    rows = [row('NEW1', 'TH_0.8', 300, 14400, d, (-1) ** d) for d in range(6)]  # mean ~0
    assert K.evaluate(rows, signs)['G1']['resolved'] == 0


def test_g2_g3_stationary():
    rows = []
    for d in range(25):
        rows.append(row('NEW2', 'Stationary', 300, 21600, d, 0.0, regret=0.0))
        for t in K.TH_ALL:
            rows.append(row('NEW2', t, 300, 21600, d, -5.0, regret=2.0))
    r = K.evaluate(rows, {})
    assert r['G2']['verdict'] == 'STANDS' and r['G3']['verdict'] == 'STANDS'
    rows[0]['G_S_Mbit_s'] = 1.0
    assert K.evaluate(rows, {})['G2']['verdict'] == 'DOES_NOT_STAND'
