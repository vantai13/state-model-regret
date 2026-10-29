"""Read-only status for the isolated L3R.7 GCP profiles; never starts a job."""
import json
from pathlib import Path
import subprocess

REMOTE=r'''
from datetime import datetime,timezone
import json,os
from pathlib import Path
base=Path.home()/'state-model-regret-r3r7-20261029'
data=dict(utc=datetime.now(timezone.utc).isoformat(),jobs=[],workers=[])
for name in ['setup_environment','preflight','jobs_started','pipeline_result']:
 p=base/(name+'.json')
 if p.exists():data[name]=json.loads(p.read_text())
for n in (6,7):
 p=base/'repo/results/R3R_numerics'/f'20261029_candidate_{n:02}'
 row=dict(candidate=n,exists=p.exists())
 for f in p.glob('*/progress.jsonl'):
  lines=f.read_text().splitlines()
  if lines:row['progress']=json.loads(lines[-1])
 if (p/'summary.json').exists():row['summary']=json.loads((p/'summary.json').read_text())
 data['jobs'].append(row)
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0')
  if b'experiments.R3R_07_fast_stationary.balanced_worker' not in args:continue
  stat=(p/'stat').read_text().rsplit(')',1)[1].split();hz=os.sysconf('SC_CLK_TCK')
  status=dict(line.split(':',1) for line in (p/'status').read_text().splitlines() if ':' in line)
  data['workers'].append(dict(pid=int(p.name),job=args[args.index(b'--job')+1].decode(),
   cpu_seconds=(int(stat[11])+int(stat[12]))/hz,
   wall_seconds=float(Path('/proc/uptime').read_text().split()[0])-int(stat[19])/hz,
   rss_kB=int(status.get('VmRSS','0 kB').split()[0])))
 except (FileNotFoundError,ProcessLookupError):pass
if not data.get('preflight') and (base/'full_suite.log').exists():data['test_progress']=(base/'full_suite.log').read_text()[-350:]
if (base/'pipeline.log').exists():data['pipeline_log_tail']=(base/'pipeline.log').read_text()[-700:]
print(json.dumps(data))
'''


def main():
    call=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectionAttempts=1',
                         '-o','ConnectTimeout=15','dt4n-gcp','python3 -'],
                        input=REMOTE,capture_output=True,text=True,timeout=45)
    if call.returncode:
        print(json.dumps(dict(status='SSH_ERROR',stderr=call.stderr)))
        raise SystemExit(call.returncode)
    data=json.loads(call.stdout)
    folder=Path('results/lessons/l3r_7/extended_capacity/gcp');folder.mkdir(exist_ok=True)
    with (folder/'telemetry.jsonl').open('a') as f:f.write(json.dumps(data)+'\n')
    print('UTC',data['utc'],'preflight',data.get('preflight',{}).get('status'),
          'pipeline',data.get('pipeline_result',{}).get('status'))
    for worker in data['workers']:print(json.dumps(worker))
    for row in data['jobs']:
        result=row.get('summary',{});r=result.get('result') or {}
        print(json.dumps(dict(candidate=row['candidate'],progress=row.get('progress'),
              status=result.get('status'),error=r.get('error'),resources=result.get('resources'),
              law_error_upper=r.get('law_error_upper'))))
    if data.get('test_progress'):print(data['test_progress'])
    if data.get('pipeline_result',{}).get('error'):print(data['pipeline_result']['error'])


if __name__=='__main__':main()
