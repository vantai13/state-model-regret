import subprocess,sys,json,platform,time
from pathlib import Path
from importlib.metadata import version
base=Path(__file__).parent
start=time.monotonic()
packages={'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'matplotlib': '3.11.2', 'mpmath': '1.3.0', 'pytest': '9.1.1'}
args=[sys.executable,'-m','pip','install','--disable-pip-version-check','--timeout','30','--retries','1']+[k+'=='+v for k,v in packages.items()]
try:
 subprocess.run(args,check=True)
 observed={k:version(k) for k in packages}
 if observed!=packages:raise RuntimeError('version mismatch')
 result=dict(status='PASS',python=platform.python_version(),packages=observed,setup_wall_seconds=time.monotonic()-start)
except Exception as e:result=dict(status='FAIL',error=str(e),setup_wall_seconds=time.monotonic()-start)
(base/'setup_environment.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
