"""Read-only receipt verification after L4.4; never evaluates a physical point."""
import argparse
from fractions import Fraction as F

from .common import (ROOT,HERE,OUT,LEVELS,load,plan,sha,require,write_once,
                     verify_prereg,guard_case,validate_row,compare_bundle)
from .analysis import select_rho


def verify():
    cfg=verify_prereg()
    fingerprint=sha(ROOT/HERE/'prereg.json')
    cases=plan()['cases']
    observed={};count=0;raw_false=[]
    control=load(OUT/'control_summary.json')
    require(control['status']=='PASS','control not passed')
    c=cfg['control'];guard_case(c,control=True)
    row=load(OUT/'controls'/c['id']/'level_640_4.json')
    validate_row(row,c,LEVELS[0],fingerprint)
    require(row['zero_action_certificate'] is True,'not exact u0 control')
    require(all(F(v)==F(row['Stay']) for v in row['losses'].values()),'u0 original cell differs')
    require(all(F(b[k])==F(row['Stay']) for b in row['baseline'] for k in ('L00','L10')),'u0 margin differs')
    rows_by_id={}
    for case in cases:
        guard_case(case)
        folder=OUT/'native'/case['id']
        target=ROOT/folder/'comparison.json'
        if not target.exists():continue
        saved=load(target.relative_to(ROOT));observed[case['id']]=saved
        levels={}
        for lv in LEVELS:
            path=ROOT/folder/f'level_{lv[0]}_{lv[1]}.json'
            if not path.exists():continue
            row=load(path.relative_to(ROOT));levels[lv]=row;count+=1
            require(row['id']==case['id'] and row['parameters']==case['parameters'] and
                    (row['K'],row['ref'])==lv and row['audit_prereg_sha256']==fingerprint and
                    row['CF_computed'] is False,'raw identity/fingerprint/CF mismatch')
            if row.get('arithmetic_pass') is not True or row.get('validity_errors'):
                raw_false.append(dict(id=case['id'],level=list(lv),arithmetic_pass=row.get('arithmetic_pass'),validity_errors=row.get('validity_errors')))
        rows_by_id[case['id']]=levels
        if saved['status']=='PASS':require(compare_bundle(case,levels)==saved,'passing comparison differs')
    summary=load(OUT/'summary/summary.json')
    require(summary['observed_cases']==len(observed) and summary['level_rows']==count,'summary counts differ')
    complete=summary['selection_allowed']
    if complete:
        require(len(observed)==90 and count==270 and all(r['status']=='PASS' for r in observed.values()),'incomplete data used for rho selection')
        frozen=load(HERE/'rho_freeze.json')
        require(frozen['prereg_sha256']==fingerprint,'rho freeze prereg changed')
        for region,target in [('MV+A','00'),('SH+A','10')]:
            rows=[rows_by_id[c['id']][LEVELS[0]] for c in cases if region in c['regions']]
            rho,_=select_rho(rows,target)
            require(rho==frozen['rho_by_region'][region],'rho selection differs')
    else:
        require(not (ROOT/HERE/'rho_freeze.json').exists(),'rho frozen from incomplete subset')
    report=load(OUT/'summary/manifest.json')
    require(report['script_sha256']==sha(ROOT/HERE/'summarize.py'),'summary source changed')
    for name,digest in report['outputs_sha256'].items():
        require(sha(ROOT/OUT/'summary'/name)==digest,'summary artifact changed')
    for name,record in load(OUT/'artifact_manifest.json')['files'].items():
        require(sha(ROOT/name)==record['sha256'],'artifact changed: '+name)
    cache=load(OUT/'cache_manifest.json')
    for name,receipt in cache['files'].items():
        p=ROOT/cache['cache_root']/name
        require(p.stat().st_size==receipt['bytes'] and sha(p)==receipt['sha256'],'local cache changed')
    return dict(responsible='Doan Van Tai',verification_status='PASS',
                scientific_status=summary['status'],source_and_author_receipts='PASS',
                discovery_cases_observed=len(observed),discovery_level_rows=count,
                control_cases=1,control_levels=1,control_status='PASS',
                passing_cases=sum(r['status']=='PASS' for r in observed.values()),
                failed_cases=[cid for cid,r in observed.items() if r['status']!='PASS'],
                raw_native_nonpassing_flags=raw_false,
                CF_or_sealed_cases=0,rho_selected=complete,card_v2_verdict_unchanged=True,
                local_cache_files=len(cache['files']),artifact_files=len(load(OUT/'artifact_manifest.json')['files']),
                G_level='G1',L43_HOLD='UNCHANGED',L48_integration='PENDING')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
    result=verify()
    if args.output:write_once(ROOT/args.output,result)
    import json
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
