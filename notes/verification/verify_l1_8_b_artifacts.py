"""Doan Van Tai — audit L1.8B saved data without running the solver or RNG.

Recomputes cell means, conditional diagnostic means, every contrast, split, F5,
pair thresholds and Richardson diagnostics from CSV; checks hashes and JUnit.
"""
import argparse
import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open() as f: return list(csv.DictReader(f))


def close(a,b):
    assert abs(float(a)-float(b))<1e-10,(a,b)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_b')
    out=parser.parse_args().output_dir.resolve()
    manifest=json.loads((out/'artifact_manifest.json').read_text())
    for entry in manifest['files']:
        path=out/entry['file']
        assert sha(path)==entry['sha256'] and path.stat().st_size==entry['size_bytes'],path
    result=json.loads((out/'results.json').read_text())
    for path,digest in result['config']['source_hashes'].items(): assert sha(ROOT/path)==digest,path
    levels=read(out/'level_metrics.csv')
    state_rows=read(out/'state_cells.csv')
    for level in levels:
        m=int(level['m'])
        states=[r for r in state_rows if int(r['m'])==m]
        assert len(states)==int(level['support_states'])
        close(math.fsum(float(r['probability']) for r in states),1)
        L={c:math.fsum(float(r['probability'])*float(r['ell'+c]) for r in states) for c in ('00','10','01','11')}
        for c in L: close(L[c],level['L'+c])
        star=math.fsum(float(r['probability'])*min(float(r['J_stay']),float(r['J_switch'])) for r in states)
        close(star,level['Lstar'])
        gains={'G_S':L['00']-L['10'],'G_M':L['00']-L['01'],'G_SM':L['00']-L['11'],
               'Gamma':L['10']+L['01']-L['00']-L['11'],'G_S|M1':L['01']-L['11'],'G_M|S1':L['10']-L['11']}
        for k,val in gains.items(): close(val,level[k])
        current={}
        for model in ('M0','M1'):
            current[model]=math.fsum(float(r['probability'])*float(r['J_switch'] if r['current_action_'+model]=='Switch' else r['J_stay']) for r in states)
            close(current[model],level['L_current_'+model])
        close(L['00']-current['M0'],level['freshness'])
        close(current['M0']-L['10'],level['mode_visibility'])
        close(L['01']-current['M1'],level['freshness_M1'])
        close(current['M1']-L['11'],level['mode_visibility_M1'])
        close(L['00']-current['M1'],level['hybrid_freshness'])
        close(current['M1']-L['10'],level['hybrid_mode'])
        close(math.fsum(float(r['probability'])*float(r['I_delta']) for r in states),level['mean_I_delta'])
        for r in states:
            true=float(r['J_switch'])-float(r['J_stay'])
            for c in ('00','10','01','11'):
                predicted=float(r['gap'+c])
                assert r['action'+c]==('Switch' if predicted<0 else 'Stay')
                direct=float(r['ell'+c])-min(float(r['J_stay']),float(r['J_switch']))
                identity=abs(true) if true*predicted<0 else (max(0,-true) if predicted==0 else 0)
                close(direct,identity)
    cref=float(levels[-1]['Lstar'])
    for name in ('pair_checks.csv','half_tolerance_checks.csv'):
        for row in read(out/name):
            a,b=float(row['coarse']),float(row['fine'])
            tol=float(row['tolerance_fraction'])*cref
            flip=a*b<0 and max(abs(a),abs(b))>tol
            assert (row['sign_violation']=='True')==flip
            assert (row['passed']=='True')==(abs(b-a)<=tol and not flip)
            close(abs(a-b)/cref,row['change_over_Cref'])
    indexed={int(s['m']):s for s in levels}
    triples=read(out/'triplet_diagnostics.csv')
    for t in triples:
        key=t['metric']
        a,b,c=(float(indexed[int(t[k])][key]) for k in ('coarse_m','middle_m','fine_m'))
        close(2*c-b,t['richardson_from_last'])
        if a-b!=0: close((b-c)/(a-b),t['rho_conv'])
        else: assert t['rho_conv']==''
    for r in read(out/'forward_reference.csv'):
        assert float(r['max_aggregate_cost_error'])<1e-10 and float(r['D_max_abs_error'])<1e-12
    for r in read(out/'precision_comparison.csv'): assert int(r['action_mismatch'])==0
    total=0
    for name,t in result['tests'].items():
        cases=list(ET.parse(out/t['junit']).iter('testcase'))
        assert len(cases)==t['total']
        assert all(c.find('failure') is None and c.find('error') is None and c.find('skipped') is None for c in cases)
        if name=='full_suite': total=len(cases)
    checked=dict(author='Doan Van Tai',status='PASS',verifier_sha256=sha(Path(__file__)),
        manifest_files_checked=len(manifest['files']),source_hashes_checked=len(result['config']['source_hashes']),
        levels=len(levels),state_rows=len(state_rows),F5_checks=4*len(state_rows),triplet_rows=len(triples),
        primary_and_diagnostic_means_recomputed=True,full_suite_passed=total,random_draws=0,
        known_source_rounding_discrepancies=len(result['source_discrepancies']))
    payload=json.dumps(checked,ensure_ascii=False,indent=2)+'\n'
    (out/'independent_artifact_audit.json').write_text(payload)
    (out/'independent_artifact_audit.txt').write_text(payload)
    entries=[dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
             if p.is_file() and p.name!='artifact_manifest.json']
    (out/'artifact_manifest.json').write_text(json.dumps(dict(author='Doan Van Tai',files=entries),indent=2)+'\n')
    print(payload,end='')


if __name__=='__main__': main()
