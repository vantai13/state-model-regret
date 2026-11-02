"""Doan Van Tai — print the environment facts that can change engine bits [AI (Claude) theo ủy quyền].

  python -m experiments.explore_mech.env_check            # print JSON
  python -m experiments.explore_mech.env_check A.json B.json [DIR_A DIR_B]
      compare two env prints and, optionally, two folders of reference rows (ignoring cpu and host)
"""
import json
import platform
import subprocess
import sys
from pathlib import Path


def facts():
    import numpy as np
    import scipy
    import mpmath
    gxx = subprocess.run(['g++', '--version'], capture_output=True, text=True).stdout.splitlines()[0].split()[-1]
    ld = np.finfo(np.longdouble)
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__, mpmath=mpmath.__version__,
                gxx=gxx, machine=platform.machine(), longdouble=dict(bits=ld.bits, eps=str(ld.eps), nmant=ld.nmant))


def main():
    if len(sys.argv) == 1:
        f = facts()
        f['cpu'] = platform.processor() or open('/proc/cpuinfo').read().split('model name')[1].split('\n')[0].strip(': ')
        print(json.dumps(f, indent=1))
        return
    a, b = (json.loads(Path(p).read_text()) for p in sys.argv[1:3])
    diff = {k: (a.get(k), b.get(k)) for k in set(a) | set(b) if k != 'cpu' and a.get(k) != b.get(k)}
    print('environment:', 'IDENTICAL' if not diff else f'DIFFERENT {diff}')
    if len(sys.argv) == 5:
        da, db = Path(sys.argv[3]), Path(sys.argv[4])
        bad = []
        for fa in sorted(da.glob('*.json')):
            ra, rb = json.loads(fa.read_text()), json.loads((db / fa.name).read_text())
            for r in (ra, rb):
                r.pop('cpu', None), r.pop('host', None)
            if ra != rb:
                bad.append(fa.name)
        n = len(list(da.glob('*.json')))
        print(f'reference rows: {n - len(bad)}/{n} bit-identical', bad or '')


if __name__ == '__main__':
    main()
