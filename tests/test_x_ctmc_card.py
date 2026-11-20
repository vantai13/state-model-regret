"""Doan Van Tai — synthetic sanity checks for experiments/letter/x_ctmc_card.py (Claude, 20/11/2026)."""
from experiments.letter import x_ctmc_card as K


def cell(reg, rule, h, g, stratum='disagree', s=-1.0, s_hat=-1.0, rf=0.1, rs=0.1, cn=0.1, co=0.4):
    return dict(status='COMPLETED', regime=reg, rule=rule, h_T_int=h, tau_T_int=1, stratum=stratum, G_S=g,
                G_S_pct_C_ref=100 * g, slope_measured=g / h, s=s, s_hat=s_hat, regret_fresh_pct_C_ref=rf,
                regret_stale_pct_C_ref=rs, concentration_new=cn, concentration_old=co, tie_share_fresh=0, tie_share_stale=0)


def fc(sign, null, df=0.1, slope=None, c5=None):
    return dict(status='COMPLETED', sign_pred=sign, null_sign=null, DeltaF_hat=df, slope_pred=slope, c5_sign=c5)


def test_t1_t2_and_exclusion():
    rows, f = [], {}
    for i in range(12):
        reg = f'R{i}'
        rows.append(cell(reg, 'TH_0.8', 30, -0.01))
        f[(reg, 'TH_0.8', 30, 1)] = fc(-1, 1, slope=-0.01 / 30)
        rows.append(cell(reg, 'MLU', 100, -0.02))
        f[(reg, 'MLU', 100, 1)] = fc(-1, 1, slope=-0.02 / 100)
    r = K.evaluate({'R0'}, f, rows)
    assert r['T1']['cells'] == 22 and r['T1']['accuracy'] == 1.0 and r['T1']['verdict'] == 'STANDS'
    assert r['T2']['law_accuracy'] == 1.0 and r['T2']['null_accuracy'] == 0.0 and r['T2']['verdict'] == 'STANDS'
    assert r['T3']['median_relative_error'] == 0.0


def test_small_effects_are_not_eligible():
    rows = [cell(f'R{i}', 'TH_0.8', 30, -0.001) for i in range(30)]   # 0.1% < 0.25%
    f = {(f'R{i}', 'TH_0.8', 30, 1): fc(-1, -1) for i in range(30)}
    assert K.evaluate(set(), f, rows)['T1']['verdict'] == 'NOT_EVALUABLE'


def test_t5_counts_only_correct_sign():
    rows = [cell(f'R{i}', 'Hybrid_hat', 30, 0.0, rf=0.1, rs=0.2) for i in range(25)]
    rows += [cell('W', 'Hybrid_hat', 30, 0.0, s_hat=1.0, rf=5, rs=5)]
    r = K.evaluate(set(), {}, rows)
    assert r['T5']['cells'] == 25 and r['T5']['share'] == 1.0 and r['T5']['wrong_sign_cells'] == 1
