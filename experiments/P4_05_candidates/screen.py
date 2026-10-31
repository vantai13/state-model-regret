"""Pure screening kernel plus a fail-closed entrypoint. No research-engine calls.

Synthetic tests exercise the kernel. Real screening requires adopted rules and
complete native/baseline receipts for the candidate being screened.
"""
from collections import Counter
from fractions import Fraction as F
import json
from pathlib import Path

from experiments.P4_03_map_audit.common import ROOT,sha,git,require,write_once,cf_keys
from experiments.R3R_07_confirmation import power


HERE=Path('experiments/P4_05_candidates')
OUT=Path('results/lessons/l4_5')
COORDS=('lambdaA','lambdaB','u','kappa','h','c_sw')


def inside(row,box):
    coords={k:F(v) for k,v in zip(COORDS,row['key'])}
    coords['delta']=coords['lambdaB']-coords['lambdaA']
    for name,(lo,hi) in box.items():
        if name not in coords:raise ValueError('unknown box coordinate')
        if F(lo)>F(hi):raise ValueError('inverted box interval')
        if not F(lo)<=coords[name]<=F(hi):return False
    return True


def native_label(row,candidate):
    if candidate not in ('SV','SUB'):raise ValueError('unknown candidate')
    if F(row['Cref'])<=0:return 'UNDEFINED'
    if not row['r1_ready'] or not row['arithmetic_ready']:return 'UNRESOLVED'
    metric,boundary=('G_S',F(1,100)) if candidate=='SV' else ('Gamma',F(-1,100))
    value=F(row[metric])/F(row['Cref']);difference=F(row['d_normalized'][metric])
    if difference<0:raise ValueError('nonnegative refinement difference required')
    if not row.get('certified_exact',False) and abs(value-boundary)<=difference:return 'UNRESOLVED'
    meets=value>=boundary if candidate=='SV' else value<=boundary
    return 'MEETS' if meets else 'FAILS'


def region_summary(rows,box,candidate,forbidden):
    keys=[tuple(str(F(v)) for v in row['key']) for row in rows]
    if len(keys)!=len(set(keys)):raise ValueError('duplicate normalized physical key')
    for row,key in zip(rows,keys):
        if len(key)!=6:raise ValueError('six-coordinate identity required')
        if key in forbidden:raise RuntimeError('CF_COLLISION: refuse outcome rows')
        if row.get('CF_computed') is not False:raise RuntimeError('CF flag must be literal False')
        if row.get('source_kind') not in ('DISCOVERY_NATIVE','SYNTHETIC_TEST'):raise RuntimeError('native labels required; pilot forbidden')
    if any(inside(dict(key=list(key)),box) for key in forbidden):raise RuntimeError('CF_COLLISION: box touches a reserved key')
    sealed=json.loads((ROOT/'experiments/P4_03_map_audit/sealed_scope.json').read_text())
    sealed_keys={tuple(r['coordinates']) for r in sealed['sealed']}
    if any(key in sealed_keys for key in keys):raise RuntimeError('SEALED_R09_R10')
    pts=[row for row in rows if inside(row,box)]
    labels=Counter(native_label(row,candidate) for row in pts)
    n=len(pts);resolved=labels['MEETS']+labels['FAILS']
    return dict(n=n,counts={key:labels[key] for key in ('MEETS','FAILS','UNRESOLVED','UNDEFINED')},
                p_cond=F(labels['MEETS'],resolved) if resolved else None,
                r_hat=F(labels['UNRESOLVED'],n) if n else None)


def screen_box(plus_rows,plus_box,rules,forbidden,candidate,*,minus_rows=None,minus_box=None):
    """Caller must verify prereg/dependencies before passing real native rows.

    This pure kernel never reads discovery tables itself. No candidate card is
    selected by PASS_SCREEN; baseline and author decision remain separate.
    """
    if candidate not in ('SV','SUB'):raise ValueError('unknown candidate')
    require(int(rules['n'])==60,'unregistered n')
    require(F(rules['alpha'])==F(1,40) and F(rules['pi0'])==F(1,2),'power helper parameters do not match rules')
    plus=region_summary(plus_rows,plus_box,candidate,forbidden)
    summaries={'plus':plus}
    if candidate=='SV':
        if minus_rows is None or minus_box is None:raise ValueError('SV needs separate minus rows/box')
        if {tuple(str(F(v)) for v in r['key']) for r in plus_rows if inside(r,plus_box)} & {tuple(str(F(v)) for v in r['key']) for r in minus_rows if inside(r,minus_box)}:
            raise ValueError('plus/minus physical keys overlap')
        summaries['minus']=region_summary(minus_rows,minus_box,candidate,forbidden)
    result=dict(candidate=candidate,regions=summaries,power=None,decision='NOT_SCREENED',
                discovery_only=True,not_evidence=True)
    if any(s['n']==0 for s in summaries.values()):result['decision']='EMPTY';return result
    if any(s['counts']['UNDEFINED'] for s in summaries.values()):result['decision']='UNDEFINED_BLOCKED';return result
    if any(s['p_cond'] is None for s in summaries.values()):result['decision']='NO_RESOLVED';return result
    p_plan=max(F(0),plus['p_cond']-F(rules['haircut']));result['p_plus_plan']=p_plan
    r_plus=plus['r_hat']
    if candidate=='SUB':pw=power.robust_region_power(60,p_plan,r_plus,plus=True)
    else:
        minus=summaries['minus']
        result['p_minus_plan']=F(rules['SV']['p_minus_plan'])
        result['p_minus_observed_conditional']=minus['p_cond']
        pw=power.robust_pass_power(60,p_plan,result['p_minus_plan'],r_plus,minus['r_hat'])
    result['power']=pw
    ok=pw>=F(rules['min_power']) and all(s['r_hat']<=F(rules['max_unresolved']) for s in summaries.values())
    result['decision']='PASS_SCREEN' if ok else 'FAIL_SCREEN'
    return result


def reserve_trial(folder,candidate,box_id,box_spec):
    """Reserve before membership/counts, including empty/failed/error trials."""
    if candidate not in ('SV','SUB'):raise ValueError('unknown candidate')
    folder=Path(folder)/candidate;folder.mkdir(parents=True,exist_ok=True)
    old=sorted(folder.glob('trial_[0-9][0-9].json'))
    if len(old)>=3:raise RuntimeError('MAX_THREE_BOXES')
    if any(json.loads(p.read_text())['box_id']==box_id for p in old):raise RuntimeError('BOX_ALREADY_REGISTERED')
    path=folder/f'trial_{len(old)+1:02d}.json'
    write_once(path,dict(candidate=candidate,box_id=box_id,bounds=box_spec,
                         status='REGISTERED_BEFORE_COUNTS',result_path=path.with_suffix('.result.json').name))
    return path


def rules_adopted():
    path=ROOT/HERE/'screening_rules.json'
    rules=json.loads(path.read_text())
    if rules['status']!='ADOPTED_BY_AUTHOR_CHOICE':return False
    if git('show','HEAD:'+str(HERE/'screening_rules.json'))!=path.read_bytes():return False
    receipt=ROOT/HERE/'rules.lock.json'
    if not receipt.exists():return False
    for name,digest in json.loads(receipt.read_text())['source_sha256'].items():
        if sha(ROOT/name)!=digest:return False
        if git('show','HEAD:'+name)!=(ROOT/name).read_bytes():return False
    return git('show','HEAD:'+str(HERE/'rules.lock.json'))==receipt.read_bytes()


def committed_json(path):
    path=Path(path)
    if not path.is_absolute():path=ROOT/path
    relative=path.resolve().relative_to(ROOT.resolve())
    require(git('show','HEAD:'+str(relative))==path.read_bytes(),'uncommitted input: '+str(relative))
    return json.loads(path.read_text())


def candidate_receipt_ready(candidate=None):
    """Check the selected candidate, or every retained candidate when None."""
    path=ROOT/HERE/'candidate_readiness.json'
    if not path.exists():return False
    receipt=committed_json(path)
    require(receipt['status']=='READY_FOR_SCREENING','candidate receipt not ready')
    require(receipt['scope_supersedes_historical_HOLD'] is True,'historical HOLD not resolved for this support')
    require(receipt['new_prereg_path'] in receipt['source_sha256'] and
            receipt['author_scope_decision_path'] in receipt['source_sha256'],'new prereg/author scope decision required')
    for name,digest in receipt['source_sha256'].items():
        require(sha(ROOT/name)==digest,'candidate input hash changed: '+name)
        require(git('show','HEAD:'+name)==(ROOT/name).read_bytes(),'uncommitted candidate receipt source')
    approved=json.loads((ROOT/HERE/'author_choices.json').read_text())['approved_candidates']
    targets=approved if candidate is None else [candidate]
    for name in targets:
        require(name in approved,'candidate not retained by author: '+name)
        detail=receipt['candidates'].get(name)
        if detail is None:return False
        require(detail['native_readiness']=='PASS' and detail['baseline_readiness']=='PASS' and
                detail['support_complete'] is True and detail['rho_policy_frozen'] is True,
                'incomplete candidate-specific data: '+name)
        require(detail['native_manifest'] in receipt['source_sha256'] and
                detail['rho_policy_path'] in receipt['source_sha256'],'missing input bindings: '+name)
    return True


def preflight(candidate=None):
    l43=json.loads((ROOT/'notes/phases/L4_3_completion.json').read_text())
    l44=json.loads((ROOT/'notes/phases/L4_4_completion.json').read_text())
    adopted=rules_adopted()
    ready=candidate_receipt_ready(candidate)
    reasons=[]
    if not adopted:reasons.append('SCREEN_RULES_NOT_ADOPTED_AND_LOCKED')
    if not ready:
        if l43['technical_recommendation']!='PASS':reasons.append('L4_3_NATIVE_AUDIT_HOLD_OR_INCOMPLETE')
        if l44['experimental_gate']!='PASS':reasons.append('L4_4_BASELINE_SANITY_HOLD_OR_INCOMPLETE')
        reasons += ['CANDIDATE_SPECIFIC_NATIVE_AND_BASELINE_RECEIPTS_NOT_REGISTERED',
                    'NO_COMMITTED_BOX_BOUNDS_OR_SV_MINUS_POLICY']
    trials=list((ROOT/OUT/'box_trials').glob('*/trial_[0-9][0-9].json'))
    results=list((ROOT/OUT/'box_trials').glob('*/trial_[0-9][0-9].result.json'))
    counted=any(json.loads(p.read_text()).get('power') is not None for p in results)
    return dict(responsible='Doan Van Tai',status='BLOCKED_PART_B' if reasons else 'READY',reasons=reasons,
                author_rules_locked=adopted,real_boxes_evaluated=len(trials),p_hat_computed=counted,
                engine_calls=0,new_CF_outcomes=0,final_card_count=None,
                note='Upstream fixes need new receipts/prereg; historical HOLD artifacts remain unchanged')


def screen_registered(candidate,box_path,native_manifest):
    """Refuse before opening candidate data while scientific dependencies HOLD.

    Committed receipts/bindings are required for this candidate. There is no
    fallback to pilot labels or to another candidate's receipt.
    """
    status=preflight(candidate)
    require(status['status']=='READY','PART_B_BLOCKED: '+';'.join(status['reasons']))
    require(rules_adopted(),'rules not author-adopted/locked')
    rules=json.loads((ROOT/HERE/'screening_rules.json').read_text())
    require(candidate in rules['approved_candidates_partA'],'candidate not retained by author')
    box=committed_json(box_path);manifest=committed_json(native_manifest)
    require(box['candidate']==candidate and box['status']=='REGISTERED_BEFORE_BOX_COUNTS','unregistered bounds')
    readiness=committed_json(HERE/'candidate_readiness.json')
    expected=readiness['candidates'][candidate]['native_manifest']
    require(Path(native_manifest).resolve()==(ROOT/expected).resolve() or
            (ROOT/native_manifest).resolve()==(ROOT/expected).resolve(),'wrong native manifest for candidate')
    require(manifest['source_kind']=='DISCOVERY_NATIVE_BUNDLE_V1','native-only input required')
    for name,digest in manifest['source_sha256'].items():require(sha(ROOT/name)==digest,'native source changed')
    trial=reserve_trial(ROOT/OUT/'box_trials',candidate,box['id'],box)
    try:
        regions={}
        for region in ('plus','minus') if candidate=='SV' else ('plus',):
            path=manifest['rows'][region]
            require(path in manifest['source_sha256'],'unhashed native row table')
            rows=json.loads((ROOT/path).read_text())
            require(all(r['source_kind']=='DISCOVERY_NATIVE' for r in rows),'non-native rows')
            regions[region]=rows
        result=screen_box(regions['plus'],box['plus'],rules,cf_keys(),candidate,
                          minus_rows=regions.get('minus'),minus_box=box.get('minus'))
        from .design_power import plain
        result=plain(result)
        result.update(box_id=box['id'],native_manifest_sha256=sha(ROOT/native_manifest),
                      rules_sha256=sha(ROOT/HERE/'screening_rules.json'))
        write_once(trial.with_suffix('.result.json'),result)
        return result
    except Exception as exc:
        target=trial.with_suffix('.result.json')
        if not target.exists():write_once(target,dict(decision='ERROR',error=f'{type(exc).__name__}: {exc}'))
        raise


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('step',choices=['preflight','screen'])
    parser.add_argument('--candidate',choices=['SV','SUB']);parser.add_argument('--box');parser.add_argument('--native-manifest')
    args=parser.parse_args()
    if args.step=='preflight':
        result=preflight(args.candidate);print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='READY' else 2
    require(args.candidate and args.box and args.native_manifest,'screen arguments required')
    print(json.dumps(screen_registered(args.candidate,args.box,args.native_manifest),ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
