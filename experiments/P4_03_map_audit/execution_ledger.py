"""Keep every registered row, including uncomputed and sealed-blocked points."""
from collections import Counter
import csv
import json
from pathlib import Path

from .common import ROOT,HERE,OUT,write_once
from .resource_resume import NEWOUT


def main():
    folder=ROOT/OUT/'execution_ledger'
    if folder.exists():raise FileExistsError('ledger already exists')
    plan=json.loads((ROOT/HERE/'cases.json').read_text())
    blocked={r['native_id'] for r in json.loads((ROOT/HERE/'sealed_scope.json').read_text())['blocked']}
    observed={}
    for p in (ROOT/NEWOUT/'native').glob('*/comparison.json'):
        row=json.loads(p.read_text());observed[row['native_id']]=row['status']
    case_rows=[];status={}
    for c in plan['cases']:
        state='SEALED_BLOCKED' if c['id'] in blocked else observed.get(c['id'],'NOT_RUN_AUDIT_HOLD')
        status[c['id']]=state
        case_rows.append(dict(native_id=c['id'],parameters='|'.join(c['parameters']),
                              aliases='|'.join(c['aliases']),status=state))
    alias_rows=[dict(id=a['id'],native_id=a['native_id'],zones='|'.join(a['zones']),
                     pilot_class=a['pilot_class'],status=status[a['native_id']]) for a in plan['aliases']]
    folder.mkdir(parents=True)
    for name,rows in [('cases.csv',case_rows),('aliases.csv',alias_rows)]:
        with (folder/name).open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    summary=dict(responsible='Doan Van Tai',planned_distinct=len(case_rows),planned_aliases=len(alias_rows),
                 distinct_status_counts=dict(Counter(r['status'] for r in case_rows)),
                 alias_status_counts=dict(Counter(r['status'] for r in alias_rows)),
                 no_missing_registered_rows=True)
    write_once(folder/'summary.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
