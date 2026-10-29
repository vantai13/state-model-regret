"""Enforce wall/CPU/RSS ceilings outside the numerical worker."""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time


def process_usage(pid):
    try:
        fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
        cpu=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK')
        status={line.split(':',1)[0]:line.split(':',1)[1].strip()
                for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line}
        rss=max(int(status.get(k,'0 kB').split()[0])*1024 for k in ('VmRSS','VmHWM'))
        return cpu,rss
    except (FileNotFoundError,ProcessLookupError,PermissionError):
        return 0.,0


def bounded_call(command,out,*,wall_seconds,cpu_seconds,rss_bytes,env=None):
    """Serial parent: RUSAGE_CHILDREN delta includes each completed job's descendants.

    /proc high water is sampled; worker also reports ru_maxrss on normal exit.
    No partial scientific scalar is printed by this parent.
    """
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic()
    reason=None;peak_rss=peak_cpu=0.
    with (out/'stdout.log').open('x') as log:
        child=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while child.poll() is None:
            cpu,rss=process_usage(child.pid);peak_cpu=max(peak_cpu,cpu);peak_rss=max(peak_rss,rss)
            elapsed=time.monotonic()-start
            if elapsed>wall_seconds:reason='WALL_LIMIT'
            elif cpu>cpu_seconds:reason='CPU_LIMIT'
            elif rss>rss_bytes:reason='RSS_LIMIT'
            if reason:
                try:os.killpg(child.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    try:os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    child.wait()
                break
            time.sleep(.05)
        child.wait()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
    result=dict(exit_code=child.returncode,stop_reason=reason,wall_seconds=time.monotonic()-start,
                cpu_seconds=cpu,sampled_peak_rss_bytes=int(peak_rss),sampled_peak_cpu_seconds=peak_cpu,
                limits=dict(wall_seconds=wall_seconds,cpu_seconds=cpu_seconds,rss_bytes=rss_bytes),
                outcome='RESOURCE_UNRESOLVED' if reason else ('COMPLETED' if child.returncode==0 else 'WORKER_FAILED'))
    with (out/'resource.json').open('x') as stream:json.dump(result,stream,indent=2)
    return result
