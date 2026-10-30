"""Parameter-only checks; never evaluate sealed outcomes."""
import pytest
from experiments.P4_03_map_audit.sealed_guard import guard_case,eligible_plan,worker_command


SEALED=('15/2','8','1','3/5','4','0')


def test_sealed_R10_coordinate_is_rejected():
    with pytest.raises(RuntimeError,match='SEALED_R09_R10'):
        guard_case({'key':list(SEALED)},{SEALED})


def test_scheduler_keeps_original_alias_ledger_but_never_schedules_sealed_case():
    original={'cases':[{'id':'blocked','key':list(SEALED)},{'id':'ok','key':['6','7','1','1/5','2','0']}],
              'aliases':[{'id':'XA097','native_id':'blocked'}]}
    effective=eligible_plan(original,{SEALED})
    assert [c['id'] for c in effective['cases']]==['ok']
    assert effective['aliases']==original['aliases'] and len(original['cases'])==2


def test_worker_routing_preserves_all_case_arguments():
    c=['python','-m','experiments.P4_03_map_audit.resource_resume','worker','--case','FAKE']
    out=worker_command(c)
    assert out[:2]==c[:2] and out[3:]==c[3:]
    assert out[2]=='experiments.P4_03_map_audit.sealed_guard'
    assert c[2]=='experiments.P4_03_map_audit.resource_resume'
