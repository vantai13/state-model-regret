import pytest
from experiments.R3R_08_population_numerics.worker import select_job


def config():
    return dict(legacy_jobs=[dict(id='X2065',kind='legacy_anchor')],marginals=[],
                cases=[dict(id='X2065',kind='global_calibration')],stage_levels={'marginal':[],'base':[[80,2]],'empty':[]})


def test_legacy_and_calibration_with_same_design_id_use_separate_namespaces():
    cfg=config()
    assert select_job(cfg,'X2065','marginal')['kind']=='legacy_anchor'
    assert select_job(cfg,'X2065','base')['kind']=='global_calibration'


def test_empty_population_computation_cannot_return_completed():
    with pytest.raises(ValueError,match='empty population level'):select_job(config(),'X2065','empty')
