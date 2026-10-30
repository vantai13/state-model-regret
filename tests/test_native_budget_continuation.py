import copy
import pytest
from experiments.R3R_13_budget_resume.run import validate_config
from experiments.R3R_13_budget_resume.prepare import unfinished


def configs():
    parent=dict(source_sha256={'engine.py':'a'},limits={'job_cpu_seconds':10,'total_cpu_seconds':100},
                carried_cpu_reserve_seconds=20,candidates=[['base',80,2]])
    child=copy.deepcopy(parent);child['limits']['total_cpu_seconds']=200
    child['resume']={'prior_carried_cpu_reserve_seconds':20}
    return parent,child


def test_budget_extension_keeps_estimator_and_individual_job_caps():
    parent,child=configs();validate_config(child,parent)
    child['limits']['job_cpu_seconds']=20
    with pytest.raises(ValueError,match='per-job'):validate_config(child,parent)


def test_budget_extension_cannot_change_numerical_candidates_or_past_ledger():
    parent,child=configs();child['candidates']=[['base',640,8]]
    with pytest.raises(ValueError,match='setting changed'):validate_config(child,parent)
    parent,child=configs();child['resume']['prior_carried_cpu_reserve_seconds']=0
    with pytest.raises(ValueError,match='ledger'):validate_config(child,parent)


def test_completed_but_inaccurate_schedule_cannot_be_rescued_by_more_budget():
    cfg=dict(stage_levels={'marginal':[],'base':[[80,2]]},cases=[{'id':'A'}],legacy_jobs=[],marginals=[])
    summary=dict(selected_levels=None,receipts=[dict(id='A',stage='base',status='COMPLETED')])
    with pytest.raises(ValueError,match='all registered levels finished'):unfinished(summary,cfg)


def test_only_unfinished_clean_parent_is_eligible_for_budget_continuation():
    cfg=dict(stage_levels={'marginal':[],'base':[[80,2]]},cases=[{'id':'A'},{'id':'B'}],legacy_jobs=[],marginals=[])
    summary=dict(selected_levels=None,receipts=[dict(id='A',stage='base',status='COMPLETED')])
    assert unfinished(summary,cfg)=={('base','B')}
    summary['receipts'][0]['status']='UNRESOLVED'
    with pytest.raises(ValueError,match='failed computation'):unfinished(summary,cfg)
