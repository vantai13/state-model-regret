"""Doan Van Tai — final artifact, numerical sanity and preservation verification."""
import csv
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent


def read(p): return json.loads(p.read_text())


def keys(path):
    a=read(path)
    if not isinstance(a,list): return set()
    result=set()
    for c in a:
        if not isinstance(c,dict) or 'parameters' not in c or len(c['parameters'])<4: continue
        try: result.add(tuple(F(x) for x in c['parameters'][:4]))
        except (ValueError,TypeError,ZeroDivisionError): pass
    return result


def main():
    m=read(OUT/'input_manifest.json')
    changed=[]
    for f,h in m['sha256'].items():
        p=ROOT/f
        after=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        if after!=h: changed.append(dict(file=f,before=h,after=after))
    bad=[];n=0
    for exp in ('ev_d','ev_d2','ev_d3','ev_d3b'):
        for f in (ROOT/'results/ext_validity'/exp/'test').glob('*.json'):
            j=read(f);n+=1
            valid=j['E_stay']['mean']>0 and j['tau']>0 and j['h']>0 and j['spacing']>0 and j['n_inst']==10000
            valid=valid and all(all(math.isfinite(v) for v in t.values()) and min(t['se'],t['se_pct'])>=0 for t in j['twins'].values())
            if not valid: bad.append(str(f.relative_to(ROOT)))
    panels={exp:keys(ROOT/'results/ext_validity'/exp/'cases.json') for exp in ('ev_a','ev_a2','ev_b','ev_b_rep')}
    panels['csw_harm']=keys(ROOT/'results/explore_ctmc/csw_harm/cases_csw_harm.json')
    overlap=[]
    for a,ka in panels.items():
        for b,kb in panels.items():
            if a<b and ka&kb: overlap.append(dict(panelA=a,panelB=b,count=len(ka&kb)))
    # Bounded check of older CTMC case lists; never reads ext_validity/ev_d4*.
    old=set();old_files=[]
    for p in sorted((ROOT/'results/explore_ctmc').rglob('cases*.json')):
        if p.parent.name=='csw_harm': continue
        k=keys(p)
        if k: old|=k;old_files.append(str(p.relative_to(ROOT)))
    overlap_old={p:len(k&old) for p,k in panels.items()}
    r=read(OUT/'recomputation.json')
    assert not r['failed_checks'] and not r['verdict_mismatches']
    assert len(r['verdicts'])==30 and len(r['missing_score'])==4
    assert not changed and not bad
    assert not overlap and not any(overlap_old.values())
    log=(OUT/'pytest_final.log').read_text()
    assert '50 passed' in log
    report=ROOT/'notes/ops/codex/AUDIT_report.md'
    assert all('## '+letter+'.' in report.read_text() for letter in 'ABCDEF')
    all_outputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in OUT.iterdir() if p.is_file() and p.name not in ('final_verification.json','verify_audit.log')}
    result=dict(input_files=len(m['sha256']),changed_input_files=changed,
                packet_outputs=n,invalid_summaries=bad,verdicts=30,matched_existing_scores=26,
                matched_report_only_scores=4,independent_arithmetic_checks=r['checks'],
                lock_entries=r['lock_entries'],current_lock_mismatches=len(r['lock_mismatches']),
                targeted_pytest=log.strip(),panel_sizes={p:len(k) for p,k in panels.items()},
                pairwise_exact_parameter_overlap=overlap,older_case_lists=old_files,
                older_unique_parameter_keys=len(old),overlap_with_older_CTMC_case_lists=overlap_old,
                report_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),outputs_sha256=all_outputs,
                scope='No full study rerun, GCP, ev_d4 result access, old-file edits, or commit.')
    (OUT/'final_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('outputs_sha256','older_case_lists')},indent=2))


if __name__=='__main__': main()
