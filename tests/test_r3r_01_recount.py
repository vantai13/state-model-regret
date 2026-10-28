"""Doan Van Tai — L3R.1: kiểm script đếm lại bằng dữ liệu giả có đáp án biết trước.

AI (Claude) viết theo PHASE_3R §8; tác giả chưa duyệt. Không đọc dữ liệu pilot thật.
"""
from fractions import Fraction
import pytest

from experiments.R3R_01_recount import recount as R

COLS = ['id', 'lambdaA', 'lambdaB', 'kappa', 'eta', 'h'] + [f'{c}_pct{x}' for c in R.CONTRASTS for x in 'CS']


def fake_csv():
    # 5 dòng, giá trị chọn để có biên bằng đúng ngưỡng (≥ 1, ≤ −1, ≤ −0,05).
    vals = {
        'X0': dict(G_S=-1.0, G_M=1.0, G_SM=0.0, Gamma=1.0),     # harm đúng biên, GM đúng biên
        'X1': dict(G_S=-0.99, G_M=0.0, G_SM=1.5, Gamma=-0.05),  # chưa tới harm; Γ̄ đúng biên âm
        'X2': dict(G_S=2.0, G_M=12.0, G_SM=0.2, Gamma=0.0),     # state value dương; GM lớn
        'X3': dict(G_S=-5.0, G_M=0.0, G_SM=0.0, Gamma=5.0),     # harm, Γ̄ lớn
        'X4': dict(G_S=0.0, G_M=0.5, G_SM=0.0, Gamma=-0.04),    # Γ̄ âm nhưng chưa tới −0,05
    }
    lines = [','.join(COLS)]
    for i, (rid, v) in enumerate(vals.items()):
        row = [rid, '7.5', '8.0', '0.1', '0.75', str(8 + i)]
        for c in R.CONTRASTS:
            pc = v.get(c, 0.0)
            row += [str(pc), str(pc * 10)]  # pctS = 10 × pctC trong dữ liệu giả
        lines.append(','.join(row))
    return '\n'.join(lines) + '\n'


def test_read_rows_defaults_c_sw():
    rows = R.read_rows(fake_csv())
    assert len(rows) == 5
    assert all(r['c_sw'] == 0.0 and r['c_sw_defaulted'] for r in rows)


def test_summary_row_known_answers():
    got = R.summary_row(R.read_rows(fake_csv()))
    assert got['n'] == 5
    assert got['GS_harm'] == 2      # X0 (= −1), X3; X1 = −0,99 không tính
    assert got['GS_pos'] == 1       # X2
    assert got['GM_C'] == 2         # X0 (= 1), X2
    assert got['GM_S'] == 2         # pctS = 10 × pctC: X0 (10), X2 (120)
    assert got['Gam_abs'] == 2      # X0, X3
    assert got['Gam_neg'] == 1      # X1 (= −0,05); X4 = −0,04 không tính
    assert got['GSM'] == 1          # X1
    assert got['maxGM'] == 12.0 and got['minGS'] == -5.0


def test_matches_uses_displayed_precision():
    assert R.matches(-8.258, '−8,3')
    assert R.matches(0.852, '0,85')
    assert not R.matches(80, '79')
    assert not R.matches(0.1933, '0,15')


def test_robustness_pairs_by_coordinates_not_id():
    base = R.read_rows(fake_csv())
    rob = [dict(r, id='XR' + r['id'], G_S_pctC=r['G_S_pctC'] + 0.2) for r in base[:2]]
    diffs, missing = R.robustness(base, rob, 'pctC')
    gs = [d for d in diffs if d['quantity'] == 'G_S_pctC']
    assert not missing and len(gs) == 2
    assert all(abs(d['diff'] - 0.2) < 1e-12 for d in gs)
    assert {d['base_id'] for d in gs} == {'X0', 'X1'}


def test_eta_meaning_splits_when_lambdaB_not_8():
    rows = [dict(lambdaB=6.0, eta=0.75), dict(lambdaB=8.0, eta=0.75)]
    got = {(e['lambdaB'], e['eta_label']): e for e in R.eta_meaning(rows)}
    assert got[('6', '3/4')]['u'] == '3/2' and got[('6', '3/4')]['u_over_headroom'] == '3/8'
    assert got[('8', '3/4')]['u_over_headroom'] == '3/4'   # trùng nhãn khi λB = 8


def test_overlap_v12_uses_u_equals_two_eta():
    grid = dict(main=[dict(id='M99', lambdaA='15/2', kappa='1/10', u='3/2', h='8')], heldout=[])
    hits, n = R.overlap_v12(R.read_rows(fake_csv()), grid)
    assert n == 1
    assert [h['pilot_id'] for h in hits] == ['X0']          # chỉ X0 có h = 8
    assert hits[0]['coords'] == ['15/2', '8', '1/10', '3/2', '8']


def test_sealed_neighbourhood_counts_parameters_only():
    grid = dict(main=[], heldout=[dict(id='R09', kappa='3/5', h='4'), dict(id='R01', kappa='1/10', h='8')])
    out = R.sealed_neighbourhood(R.read_rows(fake_csv()), grid)
    assert [z['cell'] for z in out] == ['R09']               # R01 không phải ô niêm phong
    assert out[0]['pilot_same_kappa'] == 0 and out[0]['pilot_same_h'] == 0


def test_duplicates_are_found_by_coordinates_not_id():
    rows = R.read_rows(fake_csv())
    for r in rows:
        r.update(ref=1.0, K=40.0)
    twin = dict(rows[3], id='X9')                         # cùng tọa độ với X3, ID khác
    groups, n_distinct = R.duplicates(rows + [twin])
    assert n_distinct == 5 and len(groups) == 1
    assert groups[0]['ids'] == ['X3', 'X9'] and groups[0]['max_spread_all_columns'] == 0.0
    assert [r['id'] for r in R.distinct(rows + [twin])] == ['X0', 'X1', 'X2', 'X3', 'X4']
    other_K = dict(rows[3], id='X8', K=80.0)              # khác mức số -> regime khác
    assert R.duplicates(rows + [other_K])[1] == 6


def test_frac_is_exact_for_grid_values():
    assert R.frac(7.5) == Fraction(15, 2) and R.frac(0.1) == Fraction(1, 10)


@pytest.mark.parametrize('value', ['nan', 'inf', '-inf'])
def test_nonfinite_csv_is_rejected(value):
    with pytest.raises(ValueError, match='non-finite'):
        R.read_rows('id,lambdaA\nX0,' + value + '\n')


def test_existing_output_stops_before_reading_pilot(tmp_path, monkeypatch):
    def forbidden(*args):
        raise AssertionError('build must not read pilot for an existing output')
    monkeypatch.setattr(R, 'build', forbidden)
    with pytest.raises(FileExistsError, match='before reading data'):
        R.main(['--out', str(tmp_path)])
