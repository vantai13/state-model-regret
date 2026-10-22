"""Doan Van Tai — standalone saved-artifact audit, no production imports/RNG.

Reconstructs stationary conditional law, forward episode mass, and conservation
screen from manifest using scalar dictionaries/Fraction; checks CSV/JSON/JUnit/SHA.
This is not external human review.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(out,name):
    with (out/name).open() as handle: return list(csv.DictReader(handle))


def close(a,b,atol=3e-12):
    assert math.isclose(float(a),float(b),rel_tol=3e-12,abs_tol=atol),(a,b)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_cde')
    out=parser.parse_args().output_dir.resolve()
    index=json.loads((out/'artifact_manifest.json').read_text())
    for entry in index['files']:
        p=out/entry['file']; assert p.stat().st_size==entry['size_bytes'] and sha(p)==entry['sha256'],p
    config=json.loads((out/'config.json').read_text())
    for name,digest in config['source_hashes'].items(): assert sha(ROOT/name)==digest,name
    manifest=json.loads((ROOT/'notes/design/grid_v1.json').read_text())
    result=json.loads((out/'results.json').read_text())
    assert not result['new_grid_contrasts_computed'] and not result['reserve_generated'] and result['random_draws']==0
    episodes=read(out,'episode_states.csv'); grouped=defaultdict(dict)
    for row in episodes:
        state=(F(row['qA_packet']),F(row['qB_packet']),int(row['mode']))
        assert state not in grouped[row['cell']]
        grouped[row['cell']][state]=float(row['probability'])
    diagnostics={r['cell']:r for r in read(out,'design_diagnostics.csv')}
    max_mass_error=0.; cells=manifest['cells']; dt=F(manifest['profile']['dt_candidate_s'])
    for cell in cells:
        name=cell['id']; age=F(cell['age']); horizon=F(cell['horizon']); u=2*F(cell['eta'])
        qinitial=F(cell['yB'])/(4*dt); assert qinitial.denominator==1
        s=.5*(1+math.exp(-2*float(dt/F(cell['kappa']))))
        r=(-(1-s)+math.sqrt((1-s)**2+4*s*s))/(2*s)
        b=r+r*r; prior=(1-s) if qinitial==0 else b/(1+b)
        mass={(int(qinitial),0):1-prior,(int(qinitial),1):prior}
        for _ in range(int(age/dt)):
            after=defaultdict(float)
            for (q,m),p in mass.items():
                qnext=max(0,q+(1 if m else -2))
                for n,chance in ((m,s),(1-m,1-s)): after[qnext,n]+=p*chance
            mass=after
        qa=max(F(0),F(cell['yA'])+(F(5)+u-10)*age)
        rebuilt={(qa,F(q)*4*dt,m):p for (q,m),p in mass.items() if p>0}
        assert set(rebuilt)==set(grouped[name]),name
        for state,p in rebuilt.items():
            error=abs(p-grouped[name][state]); max_mass_error=max(max_mass_error,error)
            close(p,grouped[name][state],atol=3e-14)
        close(sum(rebuilt.values()),1,atol=3e-14)
        # Independent analytic strict-idle screen; no action values or margins.
        H=int(horizon/dt); no_idle=0
        for (aqueue,bqueue,mode),p in rebuilt.items():
            can=False
            for sw in (False,True):
                for q,first,rest in ((aqueue,5+(0 if sw else u),5+(0 if sw else u)),
                                     (bqueue,(14 if mode else 2)+(u if sw else 0),2+(u if sw else 0))):
                    q1=q+(first-10)*dt
                    can |= q1<0 or (H>1 and q1+(H-1)*(rest-10)*dt<0)
            if not can: no_idle+=p
        close(no_idle,diagnostics[name]['s_bt'])
        close(prior,diagnostics[name]['prior_on'])
        if cell['role']=='negative_control': close(no_idle,1,atol=3e-14)
        assert int(diagnostics[name]['states'])==len(rebuilt)
    idle=read(out,'idle_grid_5832.csv')
    assert len(idle)==5832 and all(int(r['action_mismatches'])==0 for r in idle)
    for row in read(out,'golden_costs.csv'): assert F(row['J'])==F(row['golden'])
    for row in read(out,'backward_forward_B16.csv'):
        close(abs(float(row['backward'])-float(row['forward'])),row['abs_error'])
        assert float(row['abs_error'])<5e-13
    for row in read(out,'queue_additivity.csv'): assert F(row['joint'])==F(row['separate'])
    for row in read(out,'scale_checks.csv'): close(row['s_bt_original'],row['s_bt_scaled'])
    I=read(out,'canonical_I_delta.csv')
    expected_abs=sum(F(r['p'])*abs(F(r['I_delta'])) for r in I)
    assert expected_abs==F(1,4)
    threshold=manifest['thresholds']
    assert threshold['refinement_fraction']<=threshold['epsilon_E']/2<threshold['epsilon_E']<threshold['epsilon_R']
    total=0
    for name,t in result['tests'].items():
        cases=list(ET.parse(out/t['junit']).iter('testcase'))
        assert len(cases)==t['total']==t['passed']
        assert all(c.find('failure') is None and c.find('error') is None and c.find('skipped') is None for c in cases)
        if name=='full_suite': total=len(cases)
    audit=dict(author='Doan Van Tai',status='PASS',verifier_sha256=sha(Path(__file__)),
               manifest_files_checked=len(index['files']),source_hashes_checked=len(config['source_hashes']),
               grid_cells_rebuilt=len(cells),episode_state_rows=len(episodes),
               max_rebuilt_state_probability_error=max_mass_error,idle_pairs_checked=len(idle),
               full_suite_passed=total,new_grid_contrasts_computed=False,reserve_generated=False,random_draws=0)
    payload=json.dumps(audit,ensure_ascii=False,indent=2)+'\n'
    (out/'independent_artifact_audit.json').write_text(payload)
    (out/'independent_artifact_audit.txt').write_text(payload)
    entries=[dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
             if p.is_file() and p.name!='artifact_manifest.json']
    (out/'artifact_manifest.json').write_text(json.dumps(dict(author='Doan Van Tai',files=entries),indent=2)+'\n')
    print(payload,end='')


if __name__=='__main__': main()
