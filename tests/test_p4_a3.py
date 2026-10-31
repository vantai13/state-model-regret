"""B1 scientific rules and incomplete-input rejection; no research engine calls."""
from copy import deepcopy
from fractions import Fraction as F
import json

import pytest

from experiments.P4_A3 import b1_summary as B
from experiments.P4_A1.config import load


def fake_row(cid, costs, *, gs='0.1', d10='-1'):
    return dict(id=cid, Cref='100', Stay='60', G_M='4', G_S='3',
                losses={'00':'58','01':'52','10':'57','11':'50'},
                baseline=[dict(rho=r, L00='56', L10=str(costs[r]), GS_theta=gs,
                               deltaL10=d10, R_M_denominator_certified=True) for r in B.RHOS])


def test_all_rows_influence_selection_and_exact_tie_uses_smaller_rho():
    a = fake_row('a',dict(zip(B.RHOS,[60,54,54,58,59])))
    b = fake_row('b',dict(zip(B.RHOS,[60,56,56,51,59])))
    assert B.level_reading([a,b],'10','SH+A')['rho_star'] == '1/50'
    assert B.level_reading([a],'10','SH+A')['rho_star'] == '1/200'


@pytest.mark.parametrize('gs,d10,narrow',[('0.49','-1',True),('0.5','-1',False),('0.1','0',False)])
def test_sh_reading_preserves_strict_dl104_boundaries(gs,d10,narrow):
    row = fake_row('x',{r:55 for r in B.RHOS},gs=gs,d10=d10)
    assert B.level_reading([row],'10','SH+A')['reading']['descriptive_narrow'] is narrow
    mv = B.level_reading([row],'00','MV+A')['reading']
    assert mv['median_recovery'] == .5 and mv['descriptive_narrow'] is True


def test_verdict_compares_all_three_rhos_and_readings():
    per = {f'{k}_{r}':dict(rho_star='1/50',reading={'descriptive_narrow':False}) for k,r in B.LEVELS}
    assert B.verdict(per) == 'STABLE'
    changed = deepcopy(per);changed['320_4']['rho_star']='1/100'
    assert B.verdict(changed) == 'UNRESOLVED_RHO_DEPENDS_ON_NUMERICS'
    changed = deepcopy(per);changed['640_2']['reading']['descriptive_narrow']=True
    assert B.verdict(changed) == 'UNRESOLVED_READING_DEPENDS_ON_NUMERICS'
    with pytest.raises(RuntimeError,match='three levels'):
        B.verdict({})
    with pytest.raises(RuntimeError,match='three levels'):
        B.verdict({'640_4':per['640_4']})


def cfg_for(tmp_path):
    cfg = load('experiments/P4_A1/runs/L44_A1/prereg.json')
    cfg.update(run_id=B.RUN_ID,output=str(tmp_path),caps={'max_not_ready_fraction':'1'})
    return cfg


def test_replay_requires_full_reference_subset_and_detects_changed_values(tmp_path,monkeypatch):
    cfg = cfg_for(tmp_path);monkeypatch.setattr(B,'fingerprint',lambda:'test-receipt')
    with pytest.raises(RuntimeError,match='missing reference row'):
        B.replay(cfg)
    for cid in cfg['benchmark_ids']:
        for k,r in B.LEVELS:
            name=f'level_{k}_{r}.json'
            row=load(B.A1_NATIVE/cid/name);row['a1_prereg_sha256']='test-receipt'
            path=tmp_path/'native'/cid/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(row))
    assert B.replay(cfg)['rows_equal'] == 12
    path=tmp_path/'native'/cfg['benchmark_ids'][0]/'level_640_4.json'
    row=json.loads(path.read_text());row['baseline'][0]['L00']='12345'
    path.write_text(json.dumps(row))
    with pytest.raises(RuntimeError,match='REPRODUCTION_MISMATCH'):
        B.replay(cfg)


@pytest.mark.parametrize('status,completed',[('HOLD',90),('PASS',89)])
def test_partial_run_cannot_select_rho(tmp_path,monkeypatch,status,completed):
    cfg=cfg_for(tmp_path);monkeypatch.setattr(B,'fingerprint',lambda:'test-receipt')
    (tmp_path/'full_summary.json').write_text(json.dumps(dict(status=status,completed=completed,
        results=[],a1_prereg_sha256='test-receipt')))
    with pytest.raises(RuntimeError,match='not complete: no selection'):
        B.load_results(cfg)


def test_design_retains_original_population_numerics_and_rules():
    a1=load('experiments/P4_A1/runs/L44_A1/design.json')
    a3=load('experiments/P4_A1/runs/L44_A3/design.json')
    for key in ('kind','levels','rho','supports','cases_source','audit_pilot','resources'):
        assert a3[key] == a1[key]
    cfg=cfg_for('/tmp/test-p4-a3-output-unused');B.validate_protocol(cfg)
    cfg['cases']=cfg['cases'][:-1]
    with pytest.raises(RuntimeError,match='same 90 cases'):
        B.validate_protocol(cfg)
