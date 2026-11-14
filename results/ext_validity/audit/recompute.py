"""Doan Van Tai — independent audit. Standard library only; no project imports.
Run from repository root with .venv/bin/python. Outputs only in this directory.
"""
import csv
import hashlib
import json
import math
import statistics as S
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'results/ext_validity'
verdicts, checks, rows, locks = [], [], [], []


def read(p):
    return json.loads(Path(p).read_text())


def csvread(p):
    with Path(p).open() as f:
        return list(csv.DictReader(f))


def csvwrite(name, data):
    if not data:
        return
    keys = list(dict.fromkeys(k for r in data for k in r))
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(data)


def check(name, actual, expected, tol=1e-10):
    ok = actual == expected if not isinstance(actual, (int, float)) else (
        math.isfinite(actual) and abs(actual-expected) <= tol*max(1., abs(expected)))
    checks.append(dict(check=name, actual=actual, expected=expected, match=ok))


def record(exp, label, hits, threshold, reported, minimum=1, incomplete=False):
    n, k = len(hits), sum(hits)
    v = 'INCONCLUSIVE' if incomplete else ('NOT_EVALUABLE' if n < minimum else (
        'PASS' if k/n >= threshold else 'FAIL'))
    rv = reported.get('verdict') if reported else None
    verdicts.append(dict(experiment=exp, ID=label, reported=rv or 'MISSING_SCORE',
                         recomputed=v, match=rv == v if rv else None, k=k, n=n,
                         share=k/n if n else None, threshold=threshold))
    if reported:
        if 'n' in reported:
            check(exp+'/'+label+'/n', n, reported['n'])
        for key in ('share', 'sign_agree'):
            if key in reported and reported[key] is not None:
                check(exp+'/'+label+'/'+key, k/n, reported[key])


def audit_locks():
    paths = [BASE / n / 'lock.json' for n in (
        'ev_a','ev_a2','ev_b','ev_b_rep','ev_d','ev_d2','ev_d3','ev_d3b')]
    paths += [BASE/'ev_b_rep'/q/'lock.json' for q in ('q75','q95')]
    paths += [ROOT/'results/explore_ctmc/csw_harm/lock_csw_harm.json']
    for p in paths:
        for path, expected in read(p)['sha256'].items():
            f = ROOT/path
            actual = hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None
            locks.append(dict(lock=str(p.relative_to(ROOT)), file=path,
                              expected=expected, actual=actual, match=actual == expected))


def audit_a():
    p = BASE/'ev_a'
    P = {(r['id'], F(r['Delta']), F(r['h_p'])): r for r in csvread(p/'predictions.csv')}
    score = read(p/'score.json')
    a = []
    seen = set()
    for file in sorted((p/'run01').glob('*.json')):
        j = read(file)
        key = j['id'], F(j['Delta']), F(j['h_p'])
        check('ev_a/unique/'+file.name, key not in seen, True)
        seen.add(key)
        if j['status'] != 'COMPLETED':
            continue
        check('ev_a/cell_status/'+file.name, all(c['status']=='COMPLETED' for c in j['cells'].values()), True)
        J = {k: c['J'] for k,c in j['cells'].items()}
        pr = P[key]
        g, pred = 100*(J['00']-J['10'])/J['11'], 100*float(pr['G_S_CL_pred1'])/J['11']
        a.append(dict(experiment='ev_a', id=j['id'], dm=pr['dm'], hm=pr['hm'], G=g, pred=pred,
                      one_shot=j['one_shot']['G_S'], stratum=pr['stratum'], J11=J['11']))
    check('ev_a/completed', len(a), score['completed'])
    record('ev_a','A1',[abs(r['G']-r['pred']) <= max(.1,.05*abs(r['pred'])) for r in a if F(r['dm']) >= 3],
           .9, score['A1'], incomplete=len(a)<.9*len(P))
    record('ev_a','A2',[(r['G']>0)==(r['pred']>0) for r in a if F(r['dm'])==10 and abs(r['pred'])>=.25],
           .9, score['A2'], minimum=5, incomplete=len(a)<.9*len(P))
    rows.extend(a)
    p = BASE/'ev_a2'
    P = {(r['id'],r['which']):r for r in csvread(p/'predictions.csv')}
    T = {(r['id'],r['which']):r for r in csvread(p/'truth.csv')}
    ids = [c['id'] for c in read(p/'cases.json')]
    hits=[]
    for i in ids:
        pair=[T.get((i,w)) for w in ('lo','hi')]
        if all(t and t['status']=='COMPLETED' for t in pair):
            hits.append(float(pair[0]['G_S_CL_abs'])>0 and float(pair[1]['G_S_CL_abs'])<0)
        for t in pair:
            if t:
                check('ev_a2/normalization/'+i+'/'+t['which'],float(t['G_S_CL_pct']),100*float(t['G_S_CL_abs'])/float(t['J11']))
                rows.append(dict(experiment='ev_a2',id=i,which=t['which'],G=float(t['G_S_CL_pct']),
                                 pred=100*float(P[i,t['which']]['pred_abs'])/float(t['J11'])))
    record('ev_a2','Z1',hits,.75,read(p/'score.json')['Z1'],minimum=10)


def audit_b():
    for exp in ('ev_b','ev_b_rep/q75','ev_b_rep/q95'):
        p=BASE/exp
        P={(r['id'],F(r['h_mult'])):r for r in csvread(p/'predictions.csv')}
        T=csvread(p/'truth.csv')
        score=read(BASE/'ev_b_rep/score.json')[exp.split('/')[-1]] if '/' in exp else read(p/'score.json')
        b=[]
        for t in T:
            if F(t['h_mult'])!=10:
                continue
            pred=100*float(P[t['id'],F(10)]['G_S_pred_abs'])/float(t['Cref'])
            g=100*float(t['G_S_abs'])/float(t['Cref'])
            check(exp+'/normalization/'+t['id'],g,float(t['G_S']))
            b.append(dict(experiment=exp,id=t['id'],G=g,pred=pred,G_uncond=float(t['G_S_uncond']),stratum=t['stratum']))
        if exp=='ev_b':
            record(exp,'B1',[abs(r['G']-r['pred'])<=max(.1,.05*abs(r['pred'])) for r in b],.9,score['B1'])
            record(exp,'B2',[(r['G']>0)==(r['pred']>0) for r in b if abs(r['pred'])>=.25],.9,score['B2'],minimum=5)
        else:
            record(exp,'R1',[abs(r['G']-r['pred'])<=max(.1,.05*abs(r['pred'])) for r in b],.9,score['R1'])
            record(exp,'R2',[(r['G']>0)==(r['pred']>0) for r in b if abs(r['pred'])>=.25],.9,score['R2'])
            harm=[r for r in b if r['G_uncond']<=-.25]
            # At most 20% retained = at least 80% reversed.
            record(exp,'R3',[r['G']>-.25 for r in harm],.8,score['R3'],minimum=5)
            check(exp+'/R3/retained',sum(r['G']<=-.25 for r in harm),score['R3']['kept'])
        rows.extend(b)


def audit_d():
    details={}
    for exp in ('ev_d','ev_d2','ev_d3','ev_d3b'):
        p=BASE/exp
        cases=read(p/('cases_c1.json' if exp=='ev_d2' else 'cases.json'))
        P={(r['id'],int(r['h_mult']),r['twin']):r for r in csvread(p/'predictions.csv')}
        reported=read(p/'score.json') if (p/'score.json').exists() else {}
        dr=[]
        n_outputs=0
        for c in cases:
            tr=read(p/'train'/f"{c['id']}_s{c['seed']}.json")
            sig=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
            check(exp+'/train_sha/'+c['id'],tr['case_sha256'],sig)
            check(exp+'/train_case/'+c['id'],tr['case'],c)
            check(exp+'/train_seed/'+c['id'],tr['seed'],c['seed'])
            for m in c['h_mult']:
                for twin,fo,fn in [('fluid_nowcast','F_old_fluid_nowcast','F_new'),
                                   ('ratefluid_nowcast','F_old_ratefluid_nowcast','F_new_rate')]:
                    pr=P[c['id'],m,twin]
                    predicted=m*tr['T_int']*tr['s_train']*(tr['shares'][str(m)][fo]-tr['shares'][str(m)][fn])
                    check(exp+'/train_prediction/'+c['id']+'/'+str(m)+'/'+twin,float(pr['pred_abs']),predicted)
                file=p/'test'/f"{c['id']}_s{c['seed']}_h{m}.json"
                if not file.exists():
                    continue
                g=read(file)
                n_outputs+=1
                check(exp+'/test_sha/'+file.name,g['case_sha256'],sig)
                check(exp+'/test_case/'+file.name,g['case'],c)
                check(exp+'/test_seed/'+file.name,g['seed'],c['seed']+1000000)
                check(exp+'/test_tau/'+file.name,g.get('tau',1.),c.get('tau',1.))
                check(exp+'/test_h/'+file.name,g['h'],m*tr['T_int'])
                check(exp+'/test_s/'+file.name,g['s_train'],tr['s_train'])
                check(exp+'/test_twins/'+file.name,len(g['twins']),8)
                for twin,tw in g['twins'].items():
                    G=100*tw['G_S']/g['E_stay']['mean']
                    check(exp+'/normalization/'+file.name+'/'+twin,tw['pct_E_stay'],G)
                    pr=P.get((c['id'],m,twin))
                    pred=None if pr is None else 100*float(pr['pred_abs'])/g['E_stay']['mean']
                    r=dict(experiment=exp,id=c['id'],cls=c['cls'],stratum=c['stratum'],h_mult=m,twin=twin,
                           G=G,se=tw['se_pct'],pred=pred,tau=c.get('tau',1.),T_int=tr['T_int'],
                           tau_T=c.get('tau',1.)/tr['T_int'],h=g['h'],s_train=tr['s_train'],
                           mean_stay=tr['mean_stay'],E_stay=g['E_stay']['mean'],
                           lamA=c['lamA'],lamB=c['lamB'],u=c['u'])
                    if pr:
                        fo='F_old_'+twin
                        fn='F_new_rate' if twin.startswith('rate') else 'F_new'
                        r.update(Fdiff_train=tr['shares'][str(m)][fo]-tr['shares'][str(m)][fn],
                                 Fdiff_test=g[fo]-g[fn],beta_A=tr['nowcast']['A']['beta'][1],
                                 beta_B=tr['nowcast']['B']['beta'][1])
                    dr.append(r)
        exp_outputs=sum(len(c['h_mult']) for c in cases)
        if reported:
            check(exp+'/completed',n_outputs,reported['completed'])
            check(exp+'/expected',exp_outputs,reported['of'])
        plug=[r for r in dr if r['h_mult']==30 and r['twin'] in ('fluid','ratefluid')]
        now=[r for r in dr if r['h_mult']==30 and r['pred'] is not None]
        sig=[r for r in now if abs(r['pred'])>=.25]
        hyb=[r for r in dr if r['h_mult'] in (10,30) and r['twin']=='ratefluid_nowcast_hybrid_train']
        inc=n_outputs<.9*exp_outputs
        record(exp,'D1',[r['G']>=-max(.25,2*r['se']) for r in plug],.9,reported.get('D1'),incomplete=inc)
        record(exp,'D2',[(r['G']>0)==(r['pred']>0) for r in sig],.85,reported.get('D2'),minimum=5,incomplete=inc)
        record(exp,'D3',[abs(r['G']-r['pred'])<=max(.15,.3*abs(r['pred']))+2*r['se'] for r in now],.8,reported.get('D3'),incomplete=inc)
        record(exp,'D4',[r['G']>=-max(.1,2*r['se']) for r in hyb],.9,reported.get('D4'),incomplete=inc)
        for r in dr:
            if r['pred'] is not None:
                r['size_pass']=abs(r['G']-r['pred'])<=max(.15,.3*abs(r['pred']))+2*r['se']
        details[exp]=dict(completed=n_outputs,expected=exp_outputs)
        rows.extend(dr)
    return details


def audit_csw():
    p=ROOT/'results/explore_ctmc/csw_harm'
    P={(r['id'],F(r['c']),F(r['h'])):r for r in csvread(p/'predictions_csw_harm.csv')}
    jobs=[read(f) for f in sorted((p/'run01/jobs').glob('*.json'))]
    good={(j['id'],F(j['c'])):j for j in jobs if j['status']=='COMPLETED'}
    score=read(p/'run01/score.json')
    cs=[]
    control_inf=control_share=0.
    for key,j in good.items():
        for t in j['rows']:
            pr=P[j['id'],F(j['c']),F(t['h'])]
            G=100*(t['L00']-t['L10'])/t['Cref']
            check('csw/normalization/'+str(key)+'/'+t['h'],G,t['G_S'])
            zero=next(r for r in good[j['id'],F(0)]['rows'] if r['h']==t['h'])
            control_inf=max(control_inf,abs(float(pr['z_inf'])-j['asymptotic']['z_inf']),
                            abs(float(pr['F_old_inf'])-j['asymptotic']['F_old']),
                            abs(float(pr['F_new_inf'])-j['asymptotic']['F_new']))
            control_share=max(control_share,abs(float(pr['F_old_h'])-t['share_M0_old']),abs(float(pr['F_new_h'])-t['share_M0_new']))
            cs.append(dict(experiment='csw_harm',id=j['id'],c=str(F(j['c'])),h_mult=float(F(pr['h_mult'])),
                           G=G,pred=float(pr['z_pred1']),pred0=float(P[j['id'],F(0),F(t['h'])]['z_pred1']),
                           null=100*(zero['L00']-zero['L10'])/zero['Cref']))
    mc=read(p/'run01/mc.json')
    mcz=[]
    for u in mc['units']:
        t=next(r for r in good[u['id'],F(u['c'])]['rows'] if r['h']==u['h'])
        for metric,v in u['checks'].items():
            check('csw/MC_exact/'+u['id']+'/'+metric,v['exact'],
                  (t['L00']-t['L10']) if metric=='G_S' else t['L10']-t['L11'])
            z=(v['mc']-v['exact'])/v['se']
            check('csw/MC_z/'+u['id']+'/'+metric,z,v['z'])
            mcz.append(abs(z)<=3.5)
    controls=dict(complete=len(good)>=.9*180,prediction_vs_engine_inputs=control_inf<=1e-9,
                  per_h_shares_match=control_share<=1e-9,mc=all(mcz) and len(mc['units'])==6)
    for k,v in controls.items(): check('csw/control/'+k,v,score['controls'][k])
    long=[r for r in cs if r['h_mult']>=3 and F(r['c'])>0]
    inc=not all(controls.values())
    record('csw_harm','S1',[abs(r['G']-r['pred'])<=.1 for r in long],.9,score['details']['S1'],incomplete=inc)
    sens=[r for r in long if abs(r['pred']-r['pred0'])>=.25]
    el=[abs(r['G']-r['pred']) for r in sens]
    en=[abs(r['G']-r['null']) for r in sens]
    share=sum(a<b for a,b in zip(el,en))/len(el)
    v='PASS' if S.median(el)<=.5*S.median(en) and share>=.8 else 'FAIL'
    verdicts.append(dict(experiment='csw_harm',ID='S2',reported=score['verdicts']['S2'],
                         recomputed='INCONCLUSIVE' if inc else v,match=(not inc and score['verdicts']['S2']==v),
                         k=sum(a<b for a,b in zip(el,en)),n=len(el),share=share,threshold=.8))
    check('csw/S2/median_law',S.median(el),score['details']['S2']['median_err_law'])
    check('csw/S2/median_null',S.median(en),score['details']['S2']['median_err_null'])
    signs=[r for r in long if abs(r['pred'])>=.25 and abs(r['pred0'])>=.25 and (r['pred']>0)!=(r['pred0']>0)]
    record('csw_harm','S3',[(r['G']>0)==(r['pred']>0) for r in signs],.9,score['details']['S3'],minimum=5,incomplete=inc)
    rows.extend(cs)
    return dict(controls=controls,consistency_max=control_inf,per_h_share_max=control_share,
                max_mc_z=max(abs(v['z']) for u in mc['units'] for v in u['checks'].values()))


def main():
    audit_locks()
    audit_a()
    audit_b()
    d=audit_d()
    csw=audit_csw()
    csvwrite('verdicts.csv',verdicts)
    csvwrite('lock_checks.csv',locks)
    csvwrite('arithmetic_checks.csv',checks)
    csvwrite('recomputed_rows.csv',rows)
    result=dict(verdicts=verdicts,packet_completion=d,csw_controls=csw,
                checks=len(checks),failed_checks=[r for r in checks if not r['match']],
                lock_entries=len(locks),lock_mismatches=[r for r in locks if not r['match']],
                verdict_mismatches=[r for r in verdicts if r['match'] is False],
                missing_score=[r for r in verdicts if r['match'] is None])
    (OUT/'recomputation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('lock_mismatches','verdicts')},indent=2))
    print('LOCK MISMATCHES:',[(r['lock'],r['file']) for r in locks if not r['match']])
    print('VERDICTS:',[(r['experiment'],r['ID'],r['recomputed'],f"{r['k']}/{r['n']}") for r in verdicts])


if __name__=='__main__':
    main()
