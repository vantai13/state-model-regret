"""Doan Van Tai — write score_l75.json with the LOCKED check_l75 functions, and the report-only D22 block with a
corrected copy (post-open, 04/11/2026) [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.score_l75_post    # -> results/explore_ctmc/score_l75.json

Why this file exists: the locked `check_l75.main()` crashed in the report-only `d22_report()` before writing anything:
`done.flags` returns pandas' DataFrame.flags attribute, not the 'flags' column (AttributeError: 'Flags' object has no
attribute 'map'). The locked file is NOT edited (its sha256 is in locks_l75.json). Here:
  - verdicts: `check_l75.load()` and `check_l75.score()` exactly as locked, and the same `counts` block as `main()`;
  - D22: `d22_report_fixed()` is `check_l75.d22_report()` with `done['flags']` instead of `done.flags`; report only.
"""
import hashlib
import json
from pathlib import Path

import pandas as pd

from experiments.explore_ctmc import check_l75 as C, tau as T5

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'


def d22_report_fixed(out=OUT):
    rows = []
    for st in ('sobol', 'old'):
        cases = {c['id']: c for c in json.loads((out / 'cases_l75' / f'{st}.json').read_text())}
        for f in sorted((out / 'runs_l75_d22' / st).glob('*.json')):
            d = json.loads(f.read_text())
            if d['status'] != 'COMPLETED':
                rows.append(dict(status=d['status']))
                continue
            tm = T5.tau_grid_map(cases[d['id']], st).get(d['tau'])
            for r in d['h']:
                if 'd22' in r:
                    rows.append(dict(status='COMPLETED', tau_mult=tm, G_S=r['G_S'], F=r['d22']['F'], flags=r.get('flags', [])))
    df = pd.DataFrame(rows)
    if df.empty:
        return dict(label='chỉ báo', units=0)
    done = df[df.status == 'COMPLETED']
    harm = done[(done.G_S < -0.5) & done.tau_mult.notna()]
    by = {f'{t:g}': dict(n=len(g), median_F_over_G_S=float((g.F / g.G_S).median()), share_F_neg=float((g.F < 0).mean()))
          for t, g in harm.groupby('tau_mult')}
    return dict(label='chỉ báo', rows=len(done), unresolved_rows=int((df.status != 'COMPLETED').sum()),
                flagged_rows=int(done['flags'].map(len).gt(0).sum()), harm_by_tau=by,
                note='post-open fix of a report-only bug in the locked check_l75.d22_report (done.flags -> done["flags"])')


def main():
    locks = json.loads((OUT / 'locks_l75.json').read_text())
    changed = [f for f, h in locks['files'].items() if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h]
    if changed:
        raise SystemExit(f'locked files changed: {changed}')
    m = C.load()
    res = C.score(m)
    if (OUT / 'runs_l75_d22').exists():
        res['D22'] = dict(d22_report_fixed(), verdict='REPORT')
    units = m.drop_duplicates(['stage', 'id', 'tau']).unit_status.value_counts().to_dict()
    verdicts = {k: v['verdict'] for k, v in res.items() if v['verdict'] != 'REPORT'}
    res['counts'] = dict(unit_status=units, verdicts=verdicts, PASS=sum(v == 'PASS' for v in verdicts.values()),
                         FAIL=sum(v == 'FAIL' for v in verdicts.values()),
                         INCONCLUSIVE=sum(v == 'INCONCLUSIVE' for v in verdicts.values()))
    res['provenance'] = ('verdicts from the locked check_l75.load/score (sha256 verified); the locked main() crashed in the '
                         'report-only D22 block (pandas DataFrame.flags shadowing the "flags" column), so this wrapper '
                         'wrote the file; D22 block from a corrected copy, report only.')
    (OUT / 'score_l75.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(res['counts'])


if __name__ == '__main__':
    main()
