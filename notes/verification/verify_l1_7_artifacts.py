"""Doan Van Tai — audit persisted L1.7 artifacts in a fresh process.

Run after experiments.lessons.run_l1_7. Checks hashes, JUnit and replays saved
backgrounds via the L1.2 plant, without drawing RNG or opening new seeds.
"""
import argparse
import ast
import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.lessons.l1_2_queue import two_queue_cost  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def plant(x,b,action):
    return two_queue_cost(x[:2],[1]*len(b),b,2,3,3,action)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_7')
    out=parser.parse_args().output_dir.resolve()
    result=json.loads((out/'results.json').read_text())
    manifest=json.loads((out/'artifact_manifest.json').read_text())
    for entry in manifest['files']:
        path=out/entry['file']
        assert path.stat().st_size==entry['size_bytes'] and sha(path)==entry['sha256'],path
    for source,digest in result['config']['source_hashes'].items():
        assert sha(ROOT/source)==digest,source
    n=result['config']['N']
    crn=read_csv(out/'crn_episodes.csv')
    assert len(crn)==2*n
    for row in crn:
        st,sw=ast.literal_eval(row['background_stay']),ast.literal_eval(row['background_switch'])
        cs,ids=plant((2,2,'off'),st,'Stay')
        cw,idw=plant((2,2,'off'),sw,'Switch')
        assert (cs,cw,cw-cs)==tuple(int(row[k]) for k in ('cost_stay','cost_switch','delta'))
        assert ids==ast.literal_eval(row['idle_stay']) and idw==ast.literal_eval(row['idle_switch'])
        residual=cw-cs-sum((len(st)-j)*(w-s) for j,(s,w) in enumerate(zip(ids,idw)))
        assert residual==int(row['identity_residual'])
        assert (st!=sw)==(row['future_mismatch']=='True')
        if row['method']=='primitive': assert st==sw and residual==0
    summary=read_csv(out/'crn_summary.csv')
    for s in summary:
        data=[int(r['delta']) for r in crn if r['method']==s['method']]
        mean=sum(data)/F(n)
        var=sum((v-mean)**2 for v in data)/(n-1)
        assert abs(float(mean)-float(s['mean']))<1e-12
        assert abs(float(var)-float(s['sample_variance']))<1e-10
    leak_count=0
    for filename,expected in [('leak_episodes.csv',n),('canonical_blind_spot.csv',1200)]:
        rows=read_csv(out/filename)
        assert len(rows)==expected
        for r in rows:
            x,b=ast.literal_eval(r['state']),ast.literal_eval(r['background'])
            assert len(b)==int(r['H']) and b[0]==(5 if x[2]=='on' else 0)
            for name in ('oracle','leak','honest'):
                assert plant(x,b,r[name+'_action'])[0]==int(r[name])
            assert int(r['leak'])==min(plant(x,b,a)[0] for a in ('Stay','Switch'))
            if int(r['H'])==2: assert r['leak']==r['oracle']
        leak_count+=len(rows)
    sampler=read_csv(out/'sampler_episodes.csv')
    assert len(sampler)==4000
    for r in sampler:
        x,b=ast.literal_eval(r['state']),ast.literal_eval(r['background'])
        assert b[0]==(5 if x[2]=='on' else 0)
        assert plant(x,b,'Stay')[0]==int(r['stay']) and plant(x,b,'Switch')[0]==int(r['switch'])
    exact=read_csv(out/'exact_paths.csv')
    mass={}
    for r in exact:
        key=(r['H'],r['state'])
        mass[key]=mass.get(key,F(0))+F(r['probability'])
        x,b=ast.literal_eval(r['state']),ast.literal_eval(r['background'])
        assert plant(x,b,'Stay')[0]==int(r['stay']) and plant(x,b,'Switch')[0]==int(r['switch'])
    assert all(p==1 for p in mass.values())
    suites={}
    for name,s in {**result['tests'],**result['mutations']}.items():
        cases=list(ET.parse(out/s['junit']).iter('testcase'))
        failed=sum(c.find('failure') is not None for c in cases)
        errors=sum(c.find('error') is not None for c in cases)
        skipped=sum(c.find('skipped') is not None for c in cases)
        assert len(cases)==s['total'] and failed==s['failed'] and errors==skipped==0
        suites[name]=dict(total=len(cases),failed=failed)
    measured=dict(author='Doan Van Tai',status='PASS',verifier_sha256=sha(Path(__file__)),
                  command=[sys.executable,str(Path(__file__).resolve()),'--output-dir',str(out)],
                  existing_manifest_files_verified=len(manifest['files']),
                  source_hashes_verified=len(result['config']['source_hashes']),
                  crn_rows_plant_replayed=len(crn),leak_and_blind_rows_plant_replayed=leak_count,
                  sampler_rows_plant_replayed=len(sampler),exact_rows_plant_replayed=len(exact),
                  JUnit_suites=suites,new_rng_draws=0,new_seeds_opened=0)
    payload=json.dumps(measured,ensure_ascii=False,indent=2)+'\n'
    (out/'independent_artifact_audit.json').write_text(payload)
    (out/'independent_artifact_audit.txt').write_text(payload)
    # Refresh file manifest to include this audit; each entry excludes manifest itself.
    entries=[dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
             if p.is_file() and p.name!='artifact_manifest.json']
    (out/'artifact_manifest.json').write_text(json.dumps(dict(author='Doan Van Tai',files=entries),indent=2)+'\n')
    print(payload,end='')


if __name__=='__main__': main()
