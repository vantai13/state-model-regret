"""L4.6: independent toy answers, corrupt exports and D22 information semantics."""
import copy
from fractions import Fraction as F
import json

import pytest

from experiments.P4_06_decomposition import decompose as D


@pytest.mark.parametrize('costs,expected', [
    (('10','10','9.5','9.5'), (.5,0,0)),
    (('11','10','10.5','10'), (0,.5,-.5)),
    (('10','10','10.5','10'), (0,.5,.5)),
])
def test_lesson_toy_goldens(costs, expected):
    values = D.from_losses(dict(zip(('00','01','10','11'), costs)))
    assert tuple(values[m] for m in ('G_S_M1','G_M_S1','Gamma')) == expected


def test_s10_boundary_straddling_vs_ambiguity():
    # Equal ambiguous weights; only the first toy straddles the true boundary.
    def information_value(gaps):
        positive = sum(max(0, g)/2 for g in gaps)
        negative = sum(max(0, -g)/2 for g in gaps)
        return min(positive, negative)
    assert information_value((F(-1), F(6,5))) == F(1,2)
    assert information_value((F(1), F(1))) == 0


def test_d22_retaining_Y_changes_policy_even_at_stationarity():
    toy = D.d22_counterexample()
    assert F(toy['L00']) == F(48,5)
    assert F(toy['L10']) == F(19,2)
    assert F(toy['correct_Lcb0']) == F(48,5)
    assert F(toy['wrong_Q_only_Lcb0']) == 10
    assert F(toy['correct_F']) == 0
    assert F(toy['correct_V']) == F(1,10)
    assert F(toy['wrong_F']) == F(-2,5)
    assert F(toy['wrong_V']) == F(1,2)
    assert toy['Q_only_one_hot_recovers_L10'] is True
    assert toy['native_F'] is toy['native_V'] is None


def test_large_negative_gamma_does_not_require_large_GM_S1():
    # Both models under S1 choose Stay; averaging M0 under S0 wrongly Switches.
    # True gaps(+1,+1), model(-3,+1), mass(.4,.6): S0 Switches for all,
    # incurring regret1; S1 Switches only on mass.4, incurring regret.4.
    z = D.from_losses({'00':'11','01':'10','10':'10.4','11':'10'})
    assert z['Gamma'] == F(-3,5)
    assert z['G_M_S1'] == F(2,5)
    assert abs(z['Gamma']) > z['G_M_S1']
    assert abs(z['Gamma']) <= max(z['G_M'], z['G_M_S1'])


@pytest.fixture
def native(tmp_path):
    case = dict(id='fixture', parameters=['6','7','3/10','1/2','2','0'])
    losses = {'00':'12','01':'11','10':'11.5','11':'10'}
    raw = dict(id='fixture', parameters=case['parameters'], losses=losses, Cref='10',
               K=640, ref=4, dt='1/480', status='COMPLETED', CF_computed=False,
               arithmetic_pass=True, validity_errors=[],
               normalized_error={m:'0.000001' for m in D.METRICS},
               **{m:str(v) for m,v in D.from_losses(losses).items()})
    path = tmp_path/'saved.json'
    path.write_text(json.dumps(raw))
    comparison = dict(status='PASS', native_readiness_reasons=[])
    return raw, case, path, comparison


def test_native_export_and_unit_checks(native):
    raw, case, path, comparison = native
    row = D.native_row(raw, case, (640,4), 'fixture', path, comparison, {})
    assert row['G_S_M1_pctC'] == 10
    assert row['Gamma_pctC'] == 5
    assert row['G_M_S1_error_pp'] == .0001
    assert row['label_origin'] == 'native_estimate'
    assert max(D.check_identities(row).values()) < D.TOL_PP


def test_cost_path_catches_coherent_but_wrong_export(native):
    raw, case, path, comparison = native
    # Multiplying ALL exported contrasts preserves S11, but disagrees with costs.
    broken = copy.deepcopy(raw)
    for m in D.METRICS:
        broken[m] = str(2*F(broken[m]))
    with pytest.raises(ValueError, match='export disagrees with losses'):
        D.native_row(broken, case, (640,4), 'fixture', path, comparison, {})


@pytest.mark.parametrize('field,value', [('status','PARTIAL'), ('CF_computed',True),
                                        ('K',320), ('Cref','-1')])
def test_invalid_native_input_rejected(native, field, value):
    raw, case, path, comparison = native
    raw[field] = value
    with pytest.raises(ValueError):
        D.native_row(raw, case, (640,4), 'fixture', path, comparison, {})


def test_raw_flag_retained_without_clamping_or_readiness_upgrade(native):
    raw, case, path, comparison = native
    raw['arithmetic_pass'] = False
    raw['validity_errors'] = ['negative_nonnegative_contrast:G_S_M1']
    raw['losses']['01'] = '9.99'
    raw.update({m:str(v) for m,v in D.from_losses(raw['losses']).items()})
    comparison.update(status='NOT_READY', native_readiness_reasons=['R1'])
    row = D.native_row(raw, case, (640,4), 'fixture', path, comparison, {})
    assert row['G_S_M1_pctC'] == -.1
    assert row['arithmetic_pass'] is False
    assert row['native_ready'] is False
    assert row['bundle_status'] == 'NOT_READY'
    assert row['validity_errors']


def test_inconsistent_independent_basis_is_rejected(native):
    raw, case, path, comparison = native
    row = D.native_row(raw, case, (640,4), 'fixture', path, comparison, {})
    row['G_S_M1_pctC'] += .001
    with pytest.raises(ValueError, match='identity/unit mismatch'):
        D.check_identities(row)


def test_scaled_age_keys_match_without_merging_distinct_experiments():
    assert D.physical_key(6,7,2,F(1,2),8,2) == D.physical_key(6,7,1,F(1,2),4,1)


def test_quantiles_are_linear_design_quantiles():
    assert D.quantiles([{'x':1},{'x':3},{'x':11}], 'x') == dict(q10=1.4,q50=3,q90=9.4)
