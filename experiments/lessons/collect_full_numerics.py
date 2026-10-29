"""Copy a finished dedicated GCP audit and verify every exported byte."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

REMOTE=r'''
from pathlib import Path
import hashlib,json
base=Path.home()/'state-model-regret-l3r7-full-20261029'
raw=base/'repo/results/R3R_population_numerics/20261029_ATTEMPT'
run=base/'attemptATTEMPT'
if not (raw/'summary.json').exists() or not (run/'pipeline_result.json').exists():raise RuntimeError('audit still running or no final receipt')
groups={'results/R3R_population_numerics/20261029_ATTEMPT':raw,'results/lessons/l3r_7/full_numerics/attemptATTEMPT':run}
hashes={str(Path(local)/p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for local,root in groups.items() for p in root.rglob('*') if p.is_file()}
cache=[]
for p in (base/'cache').rglob('*.json'):
 d=json.loads(p.read_text());row={k:v for k,v in d.items() if k in ('parameters','source_fingerprint','source','cold_cpu_seconds','certificate','sha256')}
 row.update(path=str(p.relative_to(base)),sha256_json=hashlib.sha256(p.read_bytes()).hexdigest())
 data=p.with_suffix('.npz')
 if data.exists():row['actual_npz_sha256']=hashlib.sha256(data.read_bytes()).hexdigest()
 cache.append(row)
print(json.dumps(dict(hashes=hashes,cache=cache)))
'''


def main():
    p=argparse.ArgumentParser();p.add_argument('--attempt',choices=['03'],required=True);a=p.parse_args()
    r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','dt4n-gcp','python3 -'],
        input=REMOTE.replace('ATTEMPT',a.attempt),text=True,capture_output=True,timeout=90,check=True)
    data=json.loads(r.stdout);base='/home/ubuntu/state-model-regret-l3r7-full-20261029'
    pairs=[(f'{base}/repo/results/R3R_population_numerics/20261029_{a.attempt}',Path('results/R3R_population_numerics')),
           (f'{base}/attempt{a.attempt}',Path('results/lessons/l3r_7/full_numerics'))]
    for remote,parent in pairs:
        dest=parent/Path(remote).name
        if dest.exists():raise FileExistsError('refuse overwriting an existing export: '+str(dest))
        parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['scp','-r','-o','BatchMode=yes','-o','ConnectTimeout=15','dt4n-gcp:'+remote,str(parent)+'/'],check=True,timeout=180)
    mismatches=[name for name,expected in data['hashes'].items() if not Path(name).exists() or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected]
    result=dict(status='PASS' if not mismatches else 'FAIL',files=len(data['hashes']),mismatches=mismatches,source_sha256=data['hashes'])
    folder=Path('results/lessons/l3r_7/full_numerics')
    with (folder/f'export{a.attempt}_verification.json').open('x') as f:json.dump(result,f,indent=2)
    with (folder/f'cache{a.attempt}_manifest.json').open('x') as f:json.dump(data['cache'],f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}))
    if mismatches:raise RuntimeError('export hash mismatch')


if __name__=='__main__':main()
