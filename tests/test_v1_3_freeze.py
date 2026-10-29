"""Doan Van Tai — real Git snapshot tamper checks, readiness independent of a tag."""
import json
from pathlib import Path
import subprocess
import pytest
from experiments.R3R_05_contract.freeze import check_snapshot,readiness


def test_real_git_snapshot_rejects_mutated_science_file(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    (tmp_path/'contract.md').write_text('P1; epsilon_R=1/100\n')
    subprocess.run(['git','-C',str(tmp_path),'add','contract.md'],check=True)
    subprocess.run(['git','-C',str(tmp_path),'-c','user.name=Doan Van Tai','-c','user.email=fixture@example.invalid',
                    'commit','-qm','Synthetic contract fixture'],check=True)
    result=check_snapshot(tmp_path,'HEAD',['contract.md'])
    assert len(result['contract.md'])==64
    (tmp_path/'contract.md').write_text('P1; epsilon_R=1/200\n')
    with pytest.raises(ValueError,match='Frozen input changed'):check_snapshot(tmp_path,'HEAD',['contract.md'])


def test_contract_tag_does_not_clear_sampling_or_execution_gates():
    spec=json.loads(Path('experiments/R3R_05_contract/contract_spec.json').read_text())
    before=readiness(spec,tag_verified=False);after=readiness(spec,tag_verified=True)
    assert not before['hypothesis_freeze']['allowed'] and after['hypothesis_freeze']['allowed']
    assert not after['CF_sampling']['allowed'] and not after['Phase4']['allowed']
    assert any('D22' in s for s in after['Phase4']['reasons'])
    assert any('P0-V10' in s for s in after['Phase4']['reasons'])


def test_all_sanity_ids_and_regime_schema_fields_are_present():
    from experiments.R3R_05_contract.schema import IDENTITY
    spec=json.loads(Path('experiments/R3R_05_contract/contract_spec.json').read_text())
    schema=json.loads(Path('notes/design/regime_schema_v1_3.json').read_text())
    assert spec['sanity_ids']==[f'S{i:02}' for i in range(1,19)]
    assert set(IDENTITY)<=set(schema['required'])
    assert not {'K','ref'}&set(IDENTITY)
    assert spec['numerics']['K_star'] is spec['numerics']['dt_star'] is None
    assert spec['D22']['committed'] and spec['D22']['engine_implementation']=='DEFERRED'
