"""Finish collection/reporting of the registered batch; never freeze or sample CF."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import time

PROJECT='project-6b9ba053-75ff-440b-a6b'
RULE='dt4n-research-lesson7-ssh-20261029'
FOLDER=Path('results/lessons/l3r_7/full_numerics')
REMOTE="from pathlib import Path; import json; p=Path.home()/'state-model-regret-l3r7-full-20261029/attempt03/pipeline_result.json'; print(json.dumps({'finished':p.exists()}))"


def main():
    # This local monitor may survive the interactive turn. It only reads GCP
    # progress until the finite registered controller has produced its receipt.
    state=dict(owner='Doan Van Tai',status='WAITING_FOR_REGISTERED_BATCH',CF_generated=0,Phase4='HOLD',cleanup='PENDING_COLLECTION')
    target=FOLDER/'background_result.json'
    def save():
        state['utc']=datetime.now(timezone.utc).isoformat()
        tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(target)
    save();deadline=time.monotonic()+24*3600
    while time.monotonic()<deadline:
        try:
            r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','dt4n-gcp','python3 -'],input=REMOTE,text=True,capture_output=True,timeout=40)
            if r.returncode==0 and json.loads(r.stdout)['finished']:break
        except (subprocess.TimeoutExpired,ValueError):pass
        time.sleep(45)
    else:
        state.update(status='MONITOR_TIMEOUT_REMOTE_BATCH_STATE_UNKNOWN',cleanup='PENDING_COLLECTION');save();return 1
    try:
        for module in ('collect_full_numerics','report_full_numerics'):
            with (FOLDER/(module+'_03.log')).open('x') as log:
                subprocess.run([sys.executable,'-m','experiments.lessons.'+module,'--attempt','03'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        report=json.loads((FOLDER/'report03/verification.json').read_text())
        state.update(status='BATCH_EXPORTED_AND_AUDITED',numerical_status=report['numerical_status'],
                     tests=report['full_tests'],completed=report['completed'],unresolved=report['unresolved'],
                     selected_levels=report['selected_levels'],cpu_seconds=report['cpu_seconds'],
                     report=str(FOLDER/'report03/report.md'),n=None,confirmation_root=None,
                     next_step='closure audit and fixed validation before tag/n/seed' if report['selected_levels'] else 'numerical readiness failed or stop rule; inspect saved report')
        with (FOLDER/'firewall_cleanup.log').open('x') as log:
            subprocess.run(['gcloud','compute','firewall-rules','delete',RULE,'--project',PROJECT,'--quiet'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        r=subprocess.run(['gcloud','compute','firewall-rules','list','--project',PROJECT,'--filter=name='+RULE,'--format=json'],text=True,capture_output=True,check=True,timeout=90)
        assert json.loads(r.stdout)==[],'temporary firewall rule remains'
        state['cleanup']='DELETED_VERIFIED_API'
        connection=FOLDER/'cloud_connection.json';d=json.loads(connection.read_text());d['cleanup']=state['cleanup'];connection.write_text(json.dumps(d,indent=2)+'\n')
        path=Path('notes/phases/L3R_7_completion.json');d=json.loads(path.read_text())
        d['status']='FULL_CALIBRATION_COMPLETE_REQUIRES_CLOSURE' if report['selected_levels'] else 'FULL_CALIBRATION_FINISHED_NUMERICS_HOLD'
        d['latest_execution'].update(current_attempt_status=report['numerical_status'],
            completed=report['completed'],unresolved=report['unresolved'],CPU_seconds=report['cpu_seconds'],
            selected_levels=report['selected_levels'],temporary_SSH_rule_cleanup=state['cleanup'],report=state['report'])
        path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    except Exception as exc:
        state.update(status='POSTPROCESSING_FAILED',error_type=type(exc).__name__,error=str(exc))
        save();raise
    save();print(json.dumps(state,indent=2),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
