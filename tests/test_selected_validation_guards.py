import pytest
from experiments.R3R_12_validation.prepare import require_ready, cpu_limit
from experiments.R3R_12_validation.run import can_launch


def test_unselected_or_incomplete_global_audit_cannot_start_validation():
    with pytest.raises(ValueError,match='verified numerical selection'):
        require_ready(dict(status='PASS_RECORD_INTEGRITY_NUMERICS_HOLD',selected_levels=None))


def test_every_reference_and_global_case_must_be_complete():
    row=dict(status='PASS_RECORD_INTEGRITY_NUMERICS_READY_FOR_CLOSURE',selected_levels=[640,4],
             unresolved=0,base_global_bundles_complete=114,legacy_pass=3,marginals_pass=6)
    assert require_ready(row)==[640,4]
    row['marginals_pass']=5
    with pytest.raises(ValueError):require_ready(row)


def test_job_ceiling_requires_measured_positive_timing_and_keeps_declared_cap():
    assert cpu_limit(10)==60
    assert cpu_limit(100)==230
    assert cpu_limit(3500)==3600
    with pytest.raises(ValueError):cpu_limit(0)
    with pytest.raises(ValueError):cpu_limit(4000)


def test_active_call_ceilings_reserve_cpu_before_another_call_starts():
    assert can_launch(10,[20],20,100)
    assert not can_launch(10,[40],40,100)
    assert can_launch(10,[],40,60)
