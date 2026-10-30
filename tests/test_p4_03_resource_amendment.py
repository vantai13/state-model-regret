"""Resource amendment preserves numerical source and physical worker arguments."""
import json
from pathlib import Path
import subprocess
import sys

from experiments.P4_03_map_audit import resource_resume as R


def test_pilot_retry_source_changes_only_cpu_limit():
    old=(R.ROOT/R.HERE/'replay_worker.py').read_text()
    new=(R.ROOT/R.HERE/'extended_replay_worker.py').read_text()
    assert old.count('resource.setrlimit(resource.RLIMIT_CPU,(900,905))')==1
    assert old.replace('resource.setrlimit(resource.RLIMIT_CPU,(900,905))',
                       'resource.setrlimit(resource.RLIMIT_CPU,(1800,1805))')==new


def test_versioned_native_routing_preserves_case_and_arguments(tmp_path,monkeypatch):
    folder=tmp_path/R.NEWOUT/'partA';folder.mkdir(parents=True)
    (folder/'summary.json').write_text(json.dumps(dict(status='PASS',row_receipts_sha256={})))
    monkeypatch.setattr(R,'ROOT',tmp_path)
    monkeypatch.setattr(R,'verify_extension',lambda:{})
    monkeypatch.setattr(R.original,'OUT',Path('old_output_for_test'))
    monkeypatch.setattr(sys,'argv',['resource_resume','benchmark'])
    observed=[]
    def capture(cmd,*args,**kwargs):observed.append((cmd,args,kwargs));return 'captured'
    monkeypatch.setattr(subprocess,'run',capture)
    def native(stage):
        assert stage=='benchmark' and R.original.OUT==R.NEWOUT
        return subprocess.run([sys.executable,'-m','experiments.P4_03_map_audit.run','worker','--case','FAKE'],check=False)
    monkeypatch.setattr(R.original,'run_native',native)
    assert R.main()=='captured'
    assert observed==[([sys.executable,'-m','experiments.P4_03_map_audit.resource_resume','worker','--case','FAKE'],(),{'check':False})]
