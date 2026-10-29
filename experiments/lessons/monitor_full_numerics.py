"""Read-only progress of the current dedicated L3R.7 numerical audit on GCP."""
import argparse
import json
from pathlib import Path
import subprocess

REMOTE=r'''
from pathlib import Path
from datetime import datetime,timezone
import json,os
base=Path.home()/'state-model-regret-l3r7-full-20261029';run=base/'attemptATTEMPT';root=base/'repo/results/R3R_population_numerics/20261029_ATTEMPT'
data=dict(utc=datetime.now(timezone.utc).isoformat(),workers=[])
for group,names in [(run,['preflight','pipeline_result']),(root,['progress','summary'])]:
 for name in names:
  p=group/(name+'.json')
  if p.exists():data[name]={k:v for k,v in json.loads(p.read_text()).items() if k not in ('history','receipts','timing')}
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(bytes([0]))
  if b'experiments.R3R_08_population_numerics.worker' not in args:continue
  st=(p/'stat').read_text().rsplit(')',1)[1].split();out=Path(args[args.index(b'--out')+1].decode())
  row=dict(pid=int(p.name),job=args[args.index(b'--job')+1].decode(),stage=args[args.index(b'--stage')+1].decode(),cpu_seconds=(int(st[11])+int(st[12]))/os.sysconf('SC_CLK_TCK'))
  status=dict(s.split(':',1) for s in (p/'status').read_text().splitlines() if ':' in s)
  row['rss_kB']=int(status.get('VmRSS','0 kB').split()[0]);f=out/'progress.jsonl'
  if f.exists() and f.read_text().splitlines():row['phase']=json.loads(f.read_text().splitlines()[-1])
  data['workers'].append(row)
 except (FileNotFoundError,ProcessLookupError):pass
log=run/'pipeline.log'
if log.exists():data['last_log']=log.read_text()[-1200:]
print(json.dumps(data))
'''


def main():
    p=argparse.ArgumentParser();p.add_argument('--attempt',choices=['02','03'],default='03');a=p.parse_args()
    r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectionAttempts=1','-o','ConnectTimeout=15','dt4n-gcp','python3 -'],input=REMOTE.replace('ATTEMPT',a.attempt),capture_output=True,text=True,timeout=45)
    if r.returncode:raise RuntimeError(r.stderr)
    data=json.loads(r.stdout);folder=Path('results/lessons/l3r_7/full_numerics')
    with (folder/f'telemetry{a.attempt}.jsonl').open('a') as f:f.write(json.dumps(data)+'\n')
    print(json.dumps(data,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
