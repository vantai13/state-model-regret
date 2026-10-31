"""A1 tests: synthetic (exactness, mutants) + read-only real committed rows. No engine/plant calls."""
from fractions import Fraction as F
import glob
import json

import numpy as np
import pytest

from experiments.P4_03_map_audit.common import ROOT
from experiments.P4_A1 import checks as K

CAL = 'results/lessons/l3r_7/lean_close/calibration'
L43 = 'results/lessons/l4_3/resource_v2/native'
LEVELS = [(640, 4), (320, 4), (640, 2)]


def rd(path):
    return json.loads((ROOT / path).read_text())


def levels_of(folder):
    return {lv: rd(f'{folder}/level_{lv[0]}_{lv[1]}.json') for lv in LEVELS}


# ---------- synthetic: the same-route bound is exact on one grid ----------

def side(rng, n):
    from experiments.R3R_08_population_numerics.piecewise import LD
    w = rng.random(n).astype(LD); w /= w.sum(dtype=LD)
    return dict(d=rng.normal(size=n).astype(LD), h=rng.normal(size=n).astype(LD),
                ed=np.full(n, LD('1e-15')), eh=np.full(n, LD('1e-15')), w=w, w_error=LD('1e-17'),
                zero_h=np.zeros(n, dtype=bool), sat_h=np.zeros(n, dtype=bool))


def test_same_route_point_inequality_is_exact_for_every_margin():
    from experiments.P4_04_baseline.margin import pair_loss_margin
    from experiments.R3R_08_population_numerics.population import pair_loss
    from experiments.R3R_08_population_numerics.piecewise import LD
    rng = np.random.default_rng(20261031)
    for trial in range(300):
        A, B = side(rng, 1 + trial % 9), side(rng, 1 + (trial * 5) % 7)
        truth = pair_loss(A, B, model='true')[0]
        for theta in (LD(0), LD(str((trial % 13) / 7)), LD(50)):
            assert pair_loss_margin(A, B, model='mean', theta=theta)[0] >= truth   # no tolerance at all


def test_cross_route_mismatch_is_not_a_bug():
    # two-state toy of the lesson: true G_S|M1 = 0, grids weigh the rare state 1.02% vs 0.98%
    gap01, gap11 = F('0.0102') * F('-0.5'), F('0.0098') * F('-0.5')
    losses = {'00': 10 + gap01, '01': 10 + gap01, '10': 10 + gap11 + F('0.3'), '11': 10 + gap11}
    errors = {k: F(1, 10**15) for k in losses}
    assert K.same_route_violations(losses, errors) == []                 # no BUG
    report = K.cross_route_report(dict(losses={k: str(v) for k, v in losses.items()}, Cref=str(losses['11'])))
    assert F(report['01-11']) < 0                                         # cross-route negative, reported only


# ---------- real committed rows (read-only) ----------

def test_X2000_original_rule_fails_but_A1_bug_checks_pass_and_lean_ready():
    rows = levels_of(f'{CAL}/CAL_CORNER_001')
    main = rows[(640, 4)]
    assert main['losses'] == rd('results/lessons/l4_4/native/P44_000/level_640_4.json')['losses']
    L, E = {k: F(v) for k, v in main['losses'].items()}, {k: F(v) for k, v in main['cost_error'].items()}
    assert L['00'] + E['00'] < L['11'] - E['11']                          # original L4.4 sanity: fails
    for row in rows.values():
        assert K.same_route_violations(row['losses'], row['cost_error']) == []
    assert K.row_readiness(rows, (640, 4)) == []                          # frozen lean acceptance: ready


def test_diagnosis_survives_falsification_on_all_calibration_rows():
    same = cross = 0
    for path in glob.glob(str(ROOT / CAL / '*' / 'level_*.json')):
        row = json.loads(open(path).read())
        if 'losses' not in row:
            continue
        same += len(K.same_route_violations(row['losses'], row['cost_error']))
        L, E = {k: F(v) for k, v in row['losses'].items()}, {k: F(v) for k, v in row['cost_error'].items()}
        cross += L['01'] + E['01'] < L['11'] - E['11']
    assert same == 0 and cross > 0


def test_XM2X000_is_NOT_READY_not_BUG():
    rows = levels_of(f'{L43}/P43_0000')
    reasons = K.row_readiness(rows, (640, 4))
    assert any(r.startswith('R1_dt') for r in reasons) and not any(r.startswith('R1_K') for r in reasons)
    bugs = [b for row in rows.values() for b in K.same_route_violations(row['losses'], row['cost_error'])]
    assert K.classify(bugs, reasons) == 'NOT_READY'


@pytest.mark.parametrize('nid', ['P43_0379', 'P43_0114'])
def test_audit_compare_reproduces_original_L43_labels(nid):
    from experiments.P4_03_map_audit import common as C
    doc = rd('experiments/P4_03_map_audit/cases.json')
    case = next(c for c in doc['cases'] if c['id'] == nid)
    rows = levels_of(f'{L43}/{nid}')
    for alias in [a for a in doc['aliases'] if a['native_id'] == nid]:
        old, new = C.compare(alias, case, rows), K.audit_compare(alias, rows, (640, 4))
        for k in ('native_class', 'native_class_R6', 'class_flipped', 'z_pctC', 'd_pp', 'shift_pp'):
            assert old[k] == new[k], k


def test_manifest_rows_feed_the_locked_L45_label_function():
    from experiments.P4_05_candidates.screen import native_label
    doc = rd('experiments/P4_03_map_audit/cases.json')
    labels = {}
    for nid in ('P43_0379', 'P43_0114'):
        case = next(c for c in doc['cases'] if c['id'] == nid)
        rows = levels_of(f'{L43}/{nid}')
        labels[nid] = native_label(K.manifest_row(case, rows, (640, 4), K.row_readiness(rows, (640, 4))), 'SV')
    assert labels == {'P43_0379': 'MEETS', 'P43_0114': 'UNRESOLVED'}   # XM2S189 3.9%; XM2S110 0.970% within d


def test_not_ready_point_enters_screen_as_unresolved():
    from experiments.P4_05_candidates.screen import native_label
    doc = rd('experiments/P4_03_map_audit/cases.json')
    case = next(c for c in doc['cases'] if c['id'] == 'P43_0000')
    rows = levels_of(f'{L43}/P43_0000')
    row = K.manifest_row(case, rows, (640, 4), K.row_readiness(rows, (640, 4)))
    assert row['r1_ready'] is False and native_label(row, 'SUB') == 'UNRESOLVED'


# ---------- stop policy ----------

def test_stop_policy_bug_now_not_ready_only_beyond_cap():
    caps = dict(max_not_ready_fraction='1/10', max_pilot_flag_fraction='1/10')
    plan = {'S': 20}
    one_nr = [dict(native_id='a', supports=['S'], status='NOT_READY')]
    assert K.stop_decision(one_nr, plan, caps) == []                     # 1 <= 2: continue
    three_nr = one_nr * 3
    assert K.stop_decision(three_nr, plan, caps)                         # 3 > 2: stop
    assert K.stop_decision([dict(native_id='b', supports=['S'], status='BUG')], plan, caps)


# ---------- mutants: the A1 wrapper must catch real bugs ----------

def engine_like_row(A, B, h=8):
    from experiments.R3R_08_population_numerics.population import pair_loss, contrasts
    from experiments.R3R_08_population_numerics.piecewise import EPS, number
    base = number(h) * (A['mean'] + B['mean'])
    ebase = abs(number(h)) * (A['mean_error'] + B['mean_error']) + 128 * EPS * (abs(base) + 1)
    losses, errors, amb = {}, {}, {}
    for key, kind, model in [('00', 'old', 'mean'), ('01', 'old', 'true'), ('10', 'current', 'mean'), ('11', 'current', 'true')]:
        gap, err, u = pair_loss(A[kind], B[kind], model=model)
        losses[key] = base + gap; errors[key] = ebase + err + 64 * EPS * (abs(base) + abs(gap) + 1); amb[key] = u
    G = contrasts(losses)
    return dict(**{k: str(v) for k, v in G.items()}, losses={k: str(v) for k, v in losses.items()}, cost_error={k: str(v) for k, v in errors.items()},
                uncertain_action_mass=amb, contrast_error={'G_M': str(errors['00'] + errors['01'])},
                Cref=str(losses['11']), zero_action_certificate=False)


def synthetic_sides(seed):
    from experiments.R3R_08_population_numerics.piecewise import LD
    rng = np.random.default_rng(seed)
    A = dict(old=side(rng, 5), current=side(rng, 6), mean=LD('1.5'), mean_error=LD('1e-16'))
    B = dict(old=side(rng, 4), current=side(rng, 7), mean=LD('0.7'), mean_error=LD('1e-16'))
    return A, B


RHOS = ('0', '1/200', '1/100', '1/50', '1/20')


def test_wrapper_clean_on_consistent_synthetic_engine():
    from experiments.P4_A1.evaluate import add_baselines_a1
    for seed in range(40):
        A, B = synthetic_sides(seed)
        row = add_baselines_a1(engine_like_row(A, B), (A, B), F(8), RHOS)
        assert row['a1_bug_reasons'] == [], row['a1_bug_reasons']


def test_mutant_corrupted_engine_cell_is_killed():
    from experiments.P4_A1.evaluate import add_baselines_a1
    A, B = synthetic_sides(1)
    row = engine_like_row(A, B)
    from experiments.R3R_08_population_numerics.piecewise import LD
    row['losses']['00'] = str(LD(row['losses']['00']) + LD('1e-6'))
    assert any(r.startswith('theta0_cell_bits:00') for r in add_baselines_a1(row, (A, B), F(8), RHOS)['a1_bug_reasons'])


def test_mutant_margin_that_beats_the_same_route_oracle_is_killed(monkeypatch):
    from experiments.P4_A1 import evaluate as E
    real = E.pair_loss_margin

    def cheat(A, B, cost=F(0), *, model='mean', theta=0, theta_error=0):
        loss, err, amb = real(A, B, cost, model=model, theta=theta, theta_error=theta_error)
        return (loss - 1 if theta > 0 else loss), err, amb                # better than any rule can be
    monkeypatch.setattr(E, 'pair_loss_margin', cheat)
    A, B = synthetic_sides(2)
    reasons = E.add_baselines_a1(engine_like_row(A, B), (A, B), F(8), RHOS)['a1_bug_reasons']
    assert any('same_route:L00<01' in r for r in reasons) and any('same_route:L10<11' in r for r in reasons)


# ---------- guards and author ownership ----------

def test_guard_rejects_cf_and_sealed():
    from experiments.P4_A1.config import guard_case, load, SEALED
    from experiments.P4_03_map_audit.common import cf_keys
    cfg = dict(cases=[])
    for key in (next(iter(cf_keys())), tuple(load(SEALED)['sealed'][1]['coordinates'])):
        a, b, u, k, h, c = map(F, key)
        case = dict(id='X', parameters=list(map(str, (a, b, k, u / 2, h, c))), key=list(key))
        with pytest.raises(RuntimeError, match='CF_COLLISION|SEALED_R09_R10'):
            guard_case(case, cfg)


@pytest.mark.parametrize('run', ['L44_A1', 'L43_A1_SV', 'SUB_PROBE'])
def test_draft_author_choice_cannot_freeze(run, tmp_path):
    from experiments.P4_A1.config import check_author, RUNS, load
    draft = load(RUNS / run / 'author_choices.json')
    draft['status'] = 'DRAFT_AWAITING_AUTHOR'
    for field in ('decision_verbatim', 'prediction_verbatim', 'why_not_posthoc_in_author_words'):
        draft[field] = '<author must supply this field>'
    path = tmp_path / 'c.json'; path.write_text(json.dumps(draft))
    with pytest.raises(RuntimeError, match='AUTHOR_NOT_ADOPTED'):
        check_author(path)
    draft['status'] = 'ADOPTED_BY_AUTHOR'                              # status alone is not enough
    path.write_text(json.dumps(draft))
    with pytest.raises(RuntimeError, match='AUTHOR_FIELD_EMPTY'):
        check_author(path)


def test_sv_minus_options_support_sizes():
    from experiments.P4_A1.freeze import in_bounds
    from experiments.P4_02_reading.read_map import load_table
    from experiments.P4_01_recount import recount_map as R
    rec = rd('experiments/P4_A1/runs/L43_A1_SV/author_choices.json')['recommended_by_AI_not_adopted']
    for option in ('sv_minus_bounds_option_kappa_flip', 'sv_minus_bounds_option_h_flip'):
        bounds = rec[option]
        keys = {tuple(R.scaled_key(r)) for r in load_table() if in_bounds(*R.scaled_key(r), bounds)}
        assert len(keys) == bounds['exposed_distinct_points']


def test_kappa_flip_control_cannot_touch_CF_but_h_flip_does():
    from experiments.P4_05_candidates.screen import inside
    from experiments.P4_03_map_audit.common import cf_keys
    kappa_flip = {'kappa': ['2', '3'], 'h': ['1', '4']}
    h_flip = {'kappa': ['1/5', '1'], 'h': ['8', '16']}
    keys = cf_keys()
    assert not any(inside(dict(key=list(k)), kappa_flip) for k in keys)
    assert any(inside(dict(key=list(k)), h_flip) for k in keys)


def test_sub_probe_selection_is_a_fixed_rule_on_kappa_one_twentieth():
    from experiments.P4_A1.freeze import cases_sub_probe
    cases, aliases = cases_sub_probe({'plus_source': 'experiments/P4_03_map_audit/cases.json'}, {'probe_n': 5})
    assert len(cases) == 5 and cases[0]['id'] == 'P43_0000'
    assert all(F(c['parameters'][2]) == F(1, 20) for c in cases) and aliases


def test_nested_author_decisions_must_be_filled():
    from experiments.P4_A1.freeze import require_filled
    with pytest.raises(RuntimeError, match='decisions.caps.max_not_ready_fraction'):
        require_filled({'caps': {'max_not_ready_fraction': None}, 'cpu_cap_hours': 8}, 'decisions')
    require_filled({'caps': {'max_not_ready_fraction': '1/10'}, 'cpu_cap_hours': 8}, 'decisions')


def test_baseline_only_not_ready_is_unresolved_in_exported_manifest():
    from experiments.P4_05_candidates.screen import native_label
    doc = rd('experiments/P4_03_map_audit/cases.json')
    case = next(c for c in doc['cases'] if c['id'] == 'P43_0379')
    rows = levels_of(f'{L43}/P43_0379')
    assert K.row_readiness(rows, (640, 4)) == []
    row = K.manifest_row(case, rows, (640, 4), ['baseline_R1:1/20:L00'])
    assert row['r1_ready'] is False and native_label(row, 'SV') == 'UNRESOLVED'


def test_algebra_guard_catches_corrupted_gamma_even_inside_lean_tolerance():
    from copy import deepcopy
    row = deepcopy(rd(f'{CAL}/CAL_CORNER_001/level_640_4.json'))
    assert K.algebra_violations(row) == []
    row['Gamma'] = str(F(row['Gamma']) + F(1, 10**6))
    assert K.algebra_violations(row) == ['S11_state_identity', 'S11_model_identity']


@pytest.mark.parametrize('field,bad', [('K',320), ('ref',2), ('CF_computed',0), ('id','foreign')])
def test_resume_rejects_foreign_level_identity_or_cf_flag(field, bad):
    from experiments.P4_A1.run import validate_saved_row
    case = dict(id='SYNTHETIC', parameters=['7','6','1/10','1/2','8','0'])
    row = dict(id=case['id'], parameters=case['parameters'], K=640, ref=4,
               CF_computed=False, a1_prereg_sha256='fixture')
    row[field] = bad
    with pytest.raises(RuntimeError, match='foreign resumed row'):
        validate_saved_row(row, case, (640,4), 'fixture')


def test_worker_stops_before_next_level_after_bug(tmp_path, monkeypatch):
    from experiments.P4_A1 import run as R, evaluate as E
    case = dict(id='SYNTHETIC', parameters=['7','6','1/10','1/2','8','0'], supports=['S'])
    cfg = dict(cases=[case], control={'id':'U'}, output='fixture', levels=[[640,4],[320,4],[640,2]],
               rho=list(RHOS), resources=dict(case_cpu_seconds=10,address_space_bytes=1024**3),
               benchmark_ids=[case['id']])
    out = tmp_path/'fixture'; out.mkdir(); (out/'control_summary.json').write_text('{"status":"PASS"}')
    monkeypatch.setattr(R, 'ROOT', tmp_path)
    monkeypatch.setattr(R, 'verify_run', lambda _: cfg)
    monkeypatch.setattr(R, 'guard_case', lambda *a, **k: None)
    monkeypatch.setattr(R, 'fingerprint', lambda _: 'fixture')
    monkeypatch.setattr(R, 'load', lambda p: json.loads((tmp_path/p).read_text()))
    monkeypatch.setattr(R.resource, 'setrlimit', lambda *a: None)
    calls=[]
    def fake(c, lv, cache, rhos):
        calls.append(lv)
        return dict(id=c['id'],K=lv[0],ref=lv[1],a1_bug_reasons=['synthetic_bug'],call_cpu_seconds=.1)
    monkeypatch.setattr(E, 'evaluate_level', fake)
    assert R.worker('FIXTURE',case['id']) == 1
    assert calls == [(640,4)]
    saved=json.loads((out/'native/SYNTHETIC/comparison.json').read_text())
    assert saved['status']=='BUG' and saved['cpu_seconds']==.1


def test_delegated_choices_require_matching_committed_evidence(tmp_path, monkeypatch):
    from experiments.P4_A1 import config as C
    text='User explicitly delegates drafting and execution in this session.'
    evidence=tmp_path/'delegation.json'; evidence.write_text(json.dumps({'user_instruction_verbatim':text}))
    path=tmp_path/'choice.json'
    choice=dict(status='ADOPTED_BY_AUTHOR_DELEGATION',author_self_written=False,drafted_by='AI',
                delegation_path=str(evidence),delegation_verbatim=text,
                **{k:'AI drafted under explicit delegation, not an author self-attestation.' for k in C.AUTHOR_FIELDS})
    path.write_text(json.dumps(choice)); monkeypatch.setattr(C,'committed',lambda _:None)
    assert C.check_author(path)['author_self_written'] is False
    choice['delegation_verbatim']='This does not match the supplied instruction.'; path.write_text(json.dumps(choice))
    with pytest.raises(RuntimeError,match='DELEGATION_EVIDENCE_MISMATCH'):C.check_author(path)
