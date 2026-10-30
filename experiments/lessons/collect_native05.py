"""Export the finished native05 calibration and verify every exported byte."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


def main():
    folder = Path('results/lessons/l3r_7/full_numerics/native05')
    remote = r'''
from pathlib import Path
import hashlib,json
base=Path.home()/'state-model-regret-l3r7-full-20261029'
raw=base/'native05-repo/results/R3R_population_numerics/20261030_05'
run=base/'attempt05'
if not (raw/'summary.json').exists() or not (run/'pipeline_result.json').exists():
 raise RuntimeError('no final recovery receipts; do not export as complete')
groups={'results/R3R_population_numerics/20261030_05':raw,'results/lessons/l3r_7/full_numerics/attempt05':run}
hashes={str(Path(local)/p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for local,root in groups.items() for p in root.rglob('*') if p.is_file()}
print(json.dumps({'source_sha256':hashes}))
'''
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=12',
        'dt4n-gcp', 'python3 -'], input=remote, text=True, capture_output=True,
        timeout=60, check=True)
    manifest = json.loads(result.stdout)
    for path in ('results/R3R_population_numerics/20261030_05',
                 'results/lessons/l3r_7/full_numerics/attempt05'):
        if Path(path).exists():
            raise FileExistsError('preserve existing export: ' + path)
    archive = folder / 'export05.tar.gz'
    with archive.open('xb') as stream:
        subprocess.run(['ssh', '-o', 'BatchMode=yes', 'dt4n-gcp',
            'tar -czf - -C /home/ubuntu/state-model-regret-l3r7-full-20261029 '
            'native05-repo/results/R3R_population_numerics/20261030_05 attempt05'],
            stdout=stream, timeout=120, check=True)
    staging = folder / 'export05_staging'
    staging.mkdir(exist_ok=False)
    with tarfile.open(archive) as tar:
        tar.extractall(staging, filter='data')
    (staging / 'native05-repo/results/R3R_population_numerics/20261030_05').rename(
        'results/R3R_population_numerics/20261030_05')
    (staging / 'attempt05').rename('results/lessons/l3r_7/full_numerics/attempt05')
    bad = [p for p, h in manifest['source_sha256'].items()
           if hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]
    manifest.update(owner='Doan Van Tai', status='PASS' if not bad else 'FAIL',
                    files=len(manifest['source_sha256']), mismatches=bad)
    with (folder / 'export_verification.json').open('x') as stream:
        stream.write(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'source_sha256'}))
    if bad:
        raise RuntimeError('export bytes mismatch')


if __name__ == '__main__':
    main()
