"""Real process-limit tests on synthetic subprocesses; no calibration outcomes."""
import json
from pathlib import Path
import sys

import pytest

from experiments.R3R_07_numerics.budget import bounded_call


def test_success_receipt_and_no_overwrite(tmp_path):
    out=tmp_path/'success'
    r=bounded_call([sys.executable,'-c','print(123)'],out,wall_seconds=3,cpu_seconds=2,rss_bytes=64*1024**2)
    assert r['outcome']=='COMPLETED' and r['exit_code']==0
    assert (out/'stdout.log').read_text().strip()=='123'
    assert json.loads((out/'resource.json').read_text())['stop_reason'] is None
    with pytest.raises(FileExistsError):
        bounded_call([sys.executable,'-c','print(456)'],out,wall_seconds=3,cpu_seconds=2,rss_bytes=64*1024**2)


@pytest.mark.parametrize('code,limits,reason',[
    ('import time;time.sleep(5)',dict(wall_seconds=.15,cpu_seconds=2,rss_bytes=64*1024**2),'WALL_LIMIT'),
    ('while True: pass',dict(wall_seconds=5,cpu_seconds=.15,rss_bytes=64*1024**2),'CPU_LIMIT'),
    ('import time;x=bytearray(96*1024**2);time.sleep(5)',dict(wall_seconds=5,cpu_seconds=2,rss_bytes=32*1024**2),'RSS_LIMIT'),
])
def test_actual_resource_stop(tmp_path,code,limits,reason):
    r=bounded_call([sys.executable,'-c',code],tmp_path/reason,**limits)
    assert r['outcome']=='RESOURCE_UNRESOLVED' and r['stop_reason']==reason
    assert r['wall_seconds']<4


def test_failed_worker_is_not_success(tmp_path):
    r=bounded_call([sys.executable,'-c','raise ValueError("synthetic")'],tmp_path/'bad',wall_seconds=3,cpu_seconds=2,rss_bytes=64*1024**2)
    assert r['outcome']=='WORKER_FAILED' and r['exit_code']!=0


def test_uncommitted_prereg_refused_before_engine(tmp_path):
    from experiments.R3R_07_numerics.run import verify_prereg
    fake=tmp_path/'fake.json';fake.write_text('{}')
    with pytest.raises(Exception):verify_prereg(fake)


def test_phase_plan_keeps_CF_closed_and_full_coverage_conditional():
    p=Path('experiments/R3R_07_numerics/prereg.json')
    cfg=json.loads(p.read_text())
    assert cfg['CF_allowed'] is False and cfg['confirmation_root'] is None
    assert len(cfg['legacy_jobs'])==3 and len(cfg['stationary_jobs'])==6
    assert all(j['kind']=='stationary_only' for j in cfg['stationary_jobs'])
    assert all(j['spec'][0] not in ('R09','R10') for j in cfg['legacy_jobs']+cfg['conditional_global_jobs'])
    assert cfg['on_any_stage0_failure']=='HOLD; do not open global calibration, freeze numerics, allocate n/root or generate CF'


def test_direct_worker_cannot_bypass_global_calibration_gate():
    from experiments.R3R_07_numerics.worker import registered_stage0_job
    cfg=json.loads(Path('experiments/R3R_07_numerics/prereg.json').read_text())
    assert registered_stage0_job(cfg,'X2065')['kind']=='legacy_anchor'
    for job in cfg['conditional_global_jobs']:
        with pytest.raises(ValueError,match='not authorized'):
            registered_stage0_job(cfg,job['id'])
