"""DL-135 runner: order, labels, verdict, stops, pairs, rescore. Fake engine only."""
import json
from fractions import Fraction as F
from pathlib import Path

import pytest

from experiments.P6_band import run as R
from experiments.P6_band import probe as B
from experiments.P6_band import select_dii as S

ROOT = Path(__file__).resolve().parents[1]


def engine_row(gs_pct, width=F(1, 10**7)):
    """Algebraically consistent row: L11 = L01 = 10, G_S = L00 - L10 = gs_pct % of Cref."""
    L11 = L01 = F(10)
    L00 = F(21, 2)
    L10 = L00-F(gs_pct)/10
    L = {'00': L00, '01': L01, '10': L10, '11': L11}
    g = dict(G_S=L00-L10, G_M=L00-L01, G_SM=L00-L11, Gamma=L10+L01-L00-L11,
             G_S_M1=L01-L11, G_M_S1=L10-L11)
    return dict(Cref=str(L11), losses={k: str(v) for k, v in L.items()},
                cost_error={k: '0' for k in L}, normalized_error={k: str(width) for k in g},
                **{k: str(v) for k, v in g.items()})


def members(n_bases=13, twins=True):
    out = [dict(id='P6_B001C00', role='A-', base_id='B001', parameters=['7', '13/2', '1/10', '1/2', '8', '0'])]
    for i in range(n_bases):
        b = f'B{100+i}'
        out.append(dict(id=f'P6_{b}C05', role='D', base_id=b, parameters=[b, 'D']))
        if twins:
            out.append(dict(id=f'P6_{b}C00', role='twin', base_id=b, parameters=[b, 'T']))
    return R.ordered(out)


def fake_call(truth, calls, *, bug_at=None, out_dir=None):
    def call(m, lv, path, *, cpu_limit):
        calls.append((m['id'], lv, cpu_limit))
        value = truth[m['role']]
        row = engine_row(value(m) if callable(value) else value)
        if bug_at == (m['id'], lv):
            row['Cref'] = '11'                                       # Cref != L11 -> BUG
        row.update(id=m['id'], K=lv[0], ref=lv[1], parameters=m['parameters'], status='COMPLETED',
                   resources=dict(child_cpu_seconds=1.0))
        if out_dir is not None:
            p = Path(out_dir)/m['id']/f'level_{lv[0]}_{lv[1]}.json'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(row))
        return row
    return call


def clock(step=0.0):
    state = dict(t=0.0)

    def used():
        state['t'] += step
        return state['t']
    return used


H1_WORLD = {'A-': -5, 'twin': 2, 'D': -2}


def test_order_is_A_minus_then_twin_before_D_by_base():
    ms = members(3)
    assert [m['role'] for m in ms] == ['A-', 'twin', 'D', 'twin', 'D', 'twin', 'D']
    assert [m['base_id'] for m in ms[1:]] == ['B100', 'B100', 'B101', 'B101', 'B102', 'B102']


def test_frozen_predictions_are_parameter_only():
    cand = B.load_panel(ROOT)
    preds = R.build_predictions(cand, S.load_rows(ROOT), {r['id'] for r in cand})
    assert len(preds) == 27 and preds[0]['id'] == 'P6_B001C00'
    assert {k for p in preds for k in p} == {'id', 'scan_id', 'role', 'base_id', 'parameters', 'H1', 'H0',
                                           'z_H1_K640', 'z_H1_K320', 'c_over_Cref_pct'}
    d = next(p for p in preds if p['id'] == 'P6_B015C06')
    assert d['parameters'] == ['7', '15/2', '1/10', '3/4', '16', '3/8'] and (d['H1'], d['H0']) == ('-', '+')


@pytest.mark.parametrize('gs,width,expected', [
    (-2, F(1, 10**7), '-'),            # negative G_S is READY and labelled '-'
    (2, F(1, 10**7), '+'),
    (F(3, 10), F(1, 10**7), 'U'),      # inside the dead band
    (-2, F(1, 1000), 'U'),             # width too large -> not READY
])
def test_labels(gs, width, expected):
    rows = {lv: engine_row(gs, width) for lv in R.LEVELS}
    assert R.label(rows)['label'] == expected


@pytest.mark.parametrize('labels,expected', [
    ('-'*11+'U'+'+', 'H1_SUPPORTED'),
    ('-'*11+'UU', 'INCONCLUSIVE'),
    ('-'*10+'+++', 'MIXED'),
    ('+'*11+'-U', 'H0_SUPPORTED'),
    ('-'*8+'U+', 'H1_SUPPORTED'),      # N = 10 after a reduced panel
    ('-'*7+'+++', 'MIXED'),
])
def test_verdict_table(labels, expected):
    assert R.verdict(list(labels)) == expected


def test_full_fake_run_supports_H1_with_all_pairs():
    calls, ms = [], members()
    _, points, stop, rows = R.run_panel(ms, call=fake_call(H1_WORLD, calls), out='x', budget=7200, used_cpu=clock())
    s = R.score(points, ms, stop, rows)
    assert stop is None and len(calls) == 27*3
    assert s['verdict'] == 'H1_SUPPORTED' and len(s['intervention_pairs']) == 13 and s['intervention_wording_allowed']


def test_geometry_world_supports_H0():
    calls, ms = [], members()
    _, points, stop, rows = R.run_panel(ms, call=fake_call({'A-': -5, 'twin': 2, 'D': 2}, calls),
                                        out='x', budget=7200, used_cpu=clock())
    assert R.score(points, ms, stop, rows)['verdict'] == 'H0_SUPPORTED'


def test_bug_stops_at_once_without_retry():
    calls, ms = [], members()
    target = (ms[2]['id'], R.LEVELS[1])
    _, points, stop, _ = R.run_panel(ms, call=fake_call(H1_WORLD, calls, bug_at=target),
                                     out='x', budget=7200, used_cpu=clock())
    assert stop.startswith('BUG') and calls[-1][:2] == target and len(calls) == 3+3+2
    assert R.score(points, ms, stop)['verdict'] == 'INCOMPLETE'


def test_A_minus_must_be_negative():
    calls = []
    _, _, stop, _ = R.run_panel(members(), call=fake_call({'A-': 2, 'twin': 2, 'D': -2}, calls),
                                out='x', budget=7200, used_cpu=clock())
    assert stop == 'A_MINUS_FAILED' and len(calls) == 3


def test_budget_stop_and_per_call_cap():
    calls = []
    _, _, stop, _ = R.run_panel(members(), call=fake_call(H1_WORLD, calls), out='x', budget=7200,
                                used_cpu=clock(step=1000.0))
    assert stop == 'BUDGET'
    assert all(cap <= R.CALL_CPU_CAP for *_, cap in calls) and calls[-1][2] < R.CALL_CPU_CAP


def test_twin_not_plus_removes_the_pair_not_the_point():
    calls, ms = [], members()
    weak = {'B100', 'B101', 'B102'}
    world = dict(H1_WORLD, twin=lambda m: F(3, 10) if m['base_id'] in weak else 2)
    _, points, stop, rows = R.run_panel(ms, call=fake_call(world, calls), out='x', budget=7200, used_cpu=clock())
    s = R.score(points, ms, stop, rows)
    assert s['verdict'] == 'H1_SUPPORTED' and len(s['intervention_pairs']) == 10
    assert not s['intervention_wording_allowed']                   # 10 < ceil(0.8 * 13) = 11


def test_rescore_matches_and_detects_tampering(tmp_path, monkeypatch):
    ms = members(10, twins=False)
    (tmp_path/Path(R.PREDICTIONS).parent).mkdir(parents=True)
    (tmp_path/R.PREDICTIONS).write_text(''.join(json.dumps(m)+'\n' for m in ms))
    _, points, stop, rows = R.run_panel(ms, call=fake_call(H1_WORLD, [], out_dir=tmp_path/R.PANEL_OUT),
                                        out=tmp_path/R.PANEL_OUT, budget=7200, used_cpu=clock())
    summary = dict(stop_reason=stop, points=points, **R.score(points, ms, stop, rows))
    (tmp_path/R.SUMMARY).write_text(json.dumps(summary))
    assert R.cmd_rescore(tmp_path) == 0
    summary['verdict'] = 'H0_SUPPORTED'
    (tmp_path/R.SUMMARY).write_text(json.dumps(summary))
    assert R.cmd_rescore(tmp_path) == 1


def test_empty_or_missing_control_cannot_support():
    assert R.verdict([])=='INCONCLUSIVE'
    ms=members(10,twins=False)
    points={m['id']:dict(label='-') for m in ms if m['role']=='D'}
    assert R.score(points,ms,None)['verdict']=='INCOMPLETE'


def test_inconclusive_cannot_claim_intervention_despite_11_pairs():
    ms=members()
    points={m['id']:dict(label='-' if m['role']!='twin' else '+') for m in ms}
    ds=[m for m in ms if m['role']=='D']
    for m in ds[-2:]:points[m['id']]['label']='U'
    score=R.score(points,ms,None)
    assert score['verdict']=='INCONCLUSIVE' and len(score['intervention_pairs'])==11
    assert not score['intervention_wording_allowed']


def test_call_exception_preserves_incomplete_prefix():
    calls=[]
    base=fake_call(H1_WORLD,calls)
    def broken(m,lv,path,**kwargs):
        if len(calls)==3:raise RuntimeError('SYNTHETIC')
        return base(m,lv,path,**kwargs)
    _,points,stop,_=R.run_panel(members(),call=broken,out='x',budget=7200,used_cpu=clock())
    assert stop=='EXECUTION:CALL_EXCEPTION:RuntimeError' and len(calls)==3
    assert R.score(points,members(),stop)['verdict']=='INCOMPLETE'


def test_rescore_detects_forged_stop(tmp_path):
    ms=members(10,twins=False)
    path=tmp_path/R.PREDICTIONS;path.parent.mkdir(parents=True)
    path.write_text(''.join(json.dumps(m)+'\n' for m in ms))
    calls,points,stop,rows=R.run_panel(ms,call=fake_call(H1_WORLD,[],out_dir=tmp_path/R.PANEL_OUT),
                                   out=tmp_path/R.PANEL_OUT,budget=7200,used_cpu=clock())
    summary=dict(stop_reason='A_MINUS_FAILED',points=points,calls=calls,**R.score(points,ms,stop,rows))
    (tmp_path/R.SUMMARY).write_text(json.dumps(summary))
    assert R.cmd_rescore(tmp_path)==1


def test_gate_binds_exact_hashes_and_runner(tmp_path,monkeypatch):
    from experiments.P5_panel import run as V1
    paths=set(R.SOURCES+B.SOURCES+(R.PREDICTIONS,R.PLAN,B.OUT+'/summary.json',
         R.ANCHOR_OUT+'/report.json','notes/phases/PHASE_6.md','experiments/P6_band/window.py'))
    for name in paths:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture\n')
    (tmp_path/B.OUT/'summary.json').write_text(json.dumps(dict(total_phase_CPU_upper=1000)))
    raw=tmp_path/R.ANCHOR_OUT/f'{R.ANCHOR_PROBE}_level_640_4.json';raw.write_text('fixture raw\n')
    report=dict(status='PASS',runner_commit='fixture',predictions_sha256=R.sha(tmp_path/R.PREDICTIONS),
                plan_sha256=R.sha(tmp_path/R.PLAN),replay_sha256=R.sha(raw))
    (tmp_path/R.ANCHOR_OUT/'report.json').write_text(json.dumps(report))
    gate=dict(status='GO',policy='STRICT_NO_RETRY',panel_budget=7200,phase_cap=14400,
              call_cpu_cap=1800,call_wall_cap=3600,runner_commit='fixture',prior_phase_CPU_upper=2000,
              files={p:R.sha(tmp_path/p) for p in paths})
    log='### DL-135 test\n<!-- P6_GATE_D_ENTRY\n'+json.dumps(gate)+'\n-->\n'
    p=tmp_path/'notes/02_decision_log.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(log)
    def git(*args):
        if args[0]=='merge-base':return b''
        name=args[1].split(':',1)[1]
        return (tmp_path/name).read_bytes()
    monkeypatch.setattr(V1,'git',git)
    assert R.gate_record(tmp_path)['status']=='GO'
    (tmp_path/R.PLAN).write_text('changed plan\n')
    with pytest.raises(RuntimeError,match='FROZEN_SHA_MISMATCH'):
        R.gate_record(tmp_path)
