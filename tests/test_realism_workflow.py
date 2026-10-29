"""Boundaries preventing outcome-dependent labels or unchecked source changes."""
import ast
import inspect
import json
from pathlib import Path

import pytest

from experiments.R3R_04_realism import run_screen as S


def test_design_only_import_boundary():
    code = ast.parse(inspect.getsource(S))
    modules = [n.module for n in ast.walk(code) if isinstance(n, ast.ImportFrom)]
    assert not any(m.startswith('smr') or 'population' in m or 'overlay' in m for m in modules)
    assert 'G_M_pctC' not in inspect.getsource(S) and 'G_S_pctC' not in inspect.getsource(S)


def test_distinct_identity_includes_cost_but_not_stage_or_id():
    row = dict(lambdaA='7',lambdaB='8',kappa='1/10',u='1',h='8',c_sw='0',ref='1',K='40',id='toy1',stage='s1')
    same = dict(row,id='toy2',stage='s2',kappa='0.1')
    assert S.key(row) == S.key(same)
    assert S.key(row) != S.key(dict(row,c_sw='1'))


def test_outcome_column_is_rejected_before_numeric_use(tmp_path):
    path = tmp_path/'bad.csv';path.write_text('id,stage,G_M_pctC\ntoy,s1,2\n')
    with pytest.raises(ValueError,match='design-only'):S.designs({'design_csv':str(path),'main_stages':['s1']})


def test_freeze_detects_worktree_source_tampering(tmp_path, monkeypatch):
    # No research data, only two tiny byte strings.
    monkeypatch.chdir(tmp_path)
    Path('spec.json').write_text(json.dumps({'freeze_paths':['source.py']}))
    Path('source.py').write_text('changed\n')
    monkeypatch.setattr(S,'CONFIG',Path('spec.json'))
    monkeypatch.setattr(S.subprocess,'check_output',lambda *a,**k:'a'*40+'\n')
    monkeypatch.setattr(S.subprocess,'run',lambda *a,**k:None)
    monkeypatch.setattr(S,'git_bytes',lambda *a:b'frozen\n')
    with pytest.raises(ValueError,match='Frozen source changed'):S.verify_freeze('toy')


def test_complete_generic_row_export_does_not_collide_shared_keys(tmp_path, monkeypatch, capsys):
    spec=json.loads(Path('notes/realism/envelope_v1.json').read_text())
    design=tmp_path/'design.csv'
    design.write_text('id,stage,lambdaA,lambdaB,kappa,eta,h,c_sw,ref,K,u\ntoy,stage1,7,8,3/10,1/2,8,0,1,40,1\n')
    spec.update(design_csv=str(design),expected_ids=1,expected_distinct=1,contexts=spec['contexts'][:1])
    monkeypatch.setattr(S,'verify_freeze',lambda *a:('toy-commit',spec,{}))
    monkeypatch.setattr(S,'OUT',tmp_path/'output')
    monkeypatch.setattr('sys.argv',['run_screen','--freeze','toy-commit'])
    S.main()
    receipt=json.loads((S.OUT/'receipt.json').read_text())
    assert receipt['feature_rows']==1 and receipt['label_rows']==3 and not receipt['outcomes_opened']
    assert set(receipt['counts'])=={'a:f=1.5','a:f=2','a:f=3'}
    assert all(c=={'UNSOURCED':1} for c in receipt['counts'].values())
