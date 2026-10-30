"""Collect the finite registered recovery after completion; never freeze/sample CF."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


REMOTE = r'''
from pathlib import Path
from datetime import datetime,timezone
import json
base=Path.home()/'state-model-regret-l3r7-full-20261029'
raw=base/'native05-repo/results/R3R_population_numerics/20261030_05'
d={'utc':datetime.now(timezone.utc).isoformat()}
for key,p in [('progress',raw/'progress.json'),('summary',raw/'summary.json'),('pipeline',base/'attempt05/pipeline_result.json')]:
 if p.exists():d[key]={k:v for k,v in json.loads(p.read_text()).items() if k not in ('history','receipts','receipt_origins','timing')}
d['controllers']=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(bytes([0]))
  if b'experiments.R3R_11_native_population.run' in args:d['controllers'].append(int(p.name))
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
print(json.dumps(d))
'''


def main():
    folder = Path('results/lessons/l3r_7/full_numerics/native05')
    deadline = time.monotonic() + 6 * 3600
    state = dict(owner='Doan Van Tai', status='WATCHING_REGISTERED_CALIBRATION', CF_generated=0)
    while time.monotonic() < deadline:
        try:
            result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=12',
                'dt4n-gcp', 'python3 -'], input=REMOTE, capture_output=True, text=True,
                timeout=30, check=True)
            data = json.loads(result.stdout)
            with (folder / 'watcher_telemetry.jsonl').open('a') as stream:
                stream.write(json.dumps(data) + '\n')
            state.update(utc=datetime.now(timezone.utc).isoformat(), remote=data)
            (folder / 'watcher_state.json').write_text(json.dumps(state, indent=2) + '\n')
            print(json.dumps(data), flush=True)
            if 'pipeline' in data:
                if 'summary' not in data:
                    raise RuntimeError('pipeline ended without a calibration summary')
                break
            if 'progress' in data and not data['controllers']:
                raise RuntimeError('controller lost before final summary; preserve checkpoint')
        except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
            print(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), connection_error=str(exc))), flush=True)
        time.sleep(45)
    else:
        raise TimeoutError('watch deadline; remote batch state remains unresolved')
    for module in ('collect_native05', 'report_native05'):
        with (folder / (module + '.log')).open('x') as stream:
            subprocess.run([sys.executable, '-m', 'experiments.lessons.' + module],
                stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=240)
    state.update(status='EXPORTED_AND_INDEPENDENTLY_AUDITED_NO_FREEZE_NO_CF',
                 utc=datetime.now(timezone.utc).isoformat())
    (folder / 'watcher_state.json').write_text(json.dumps(state, indent=2) + '\n')
    print(json.dumps(state), flush=True)


if __name__ == '__main__':
    main()
