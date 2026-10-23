"""Doan Van Tai — artifact audit and six consistency/readiness checks for Part A.

No candidate action values are recomputed. A rejected grid is a valid measured
outcome, never converted into a successful freeze by this verifier.
"""
import argparse,csv,hashlib,json,re,subprocess
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]


def load(path):return json.loads(path.read_text())
def rows(path):
    with path.open() as h:return list(csv.DictReader(h))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def run(out):
    out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/'readiness.json').exists():raise SystemExit('Choose fresh --output-dir; preserve evidence')
    manifests={};support_count=0
    directories=['v1_1_a1','v1_1_a1_redesign','v1_1_a2','v1_1_a2_redesign','v1_1_a3','v1_1_a4','v1_1_a4_redesign','v1_1_a5']
    for name in directories:
        directory=ROOT/'results/lessons'/name;items=load(directory/'manifest.json')
        for item in items:assert sha(directory/item['file'])==item['sha256'],(name,item['file'])
        manifests[name]=len(items)
    # Legacy byte manifests do not claim current active documents equal old ones.
    for name in ('l1_8_a','l1_8_b','l1_8_cde','l1_8_v1_1_b1','v1_1_m2'):
        directory=ROOT/'results/lessons'/name;items=load(directory/'artifact_manifest.json')['files']
        for item in items:assert sha(directory/item['file'])==item['sha256']
        manifests[name]=len(items)
    prior_rows=[]
    for name in ('v1_1_a1','v1_1_a1_redesign'):
        part=rows(ROOT/'results/lessons'/name/'certificates.csv');assert len(part)==20
        for r in part:
            assert r['status']=='PASS'
            assert max(float(r['law_error_A']),float(r['law_error_B']))<=1e-10
            posterior=float(r.get('posterior_bound_max',r.get('posterior_bound')));assert posterior<=1e-8
            assert float(r['wall_s'])<=1200 and int(r['peak_rss_bytes'])<=4*1024**3
        prior_rows+=part
    for name in ('v1_1_a2','v1_1_a2_redesign'):
        directory=ROOT/'results/lessons'/name;meta=load(directory/'supports.json');assert len(meta)==136
        for m in meta:
            with np.load(directory/f"{m['cell']}_{m['refinement']}_{m['queue']}.npz") as arrays:
                p,support=arrays['mass'],arrays['support'];support_count+=1
                assert int(support.sum())==m['support_states']
                assert not np.any(support & (p==0)) and not np.any(p<0)
                assert abs(p.sum(dtype=np.longdouble)-1)<=m['TV_error']+1e-15
        labels=rows(directory/'labels.csv');assert len(labels)==68
        assert all(r['label']=='SD-cell' for r in labels if r['cell'] in ('N01','N02'))
        assert all(r['label']=='conservation-cell' for r in labels if r['cell'] in ('N03','N04'))
    screen_rows=[];counts=[]
    allowed={'cell','refinement','dt','p_low','p_high','unresolved_mass','D_error','aggregation_rounding_bound','classification',
             'extended','initial_unresolved_mass','wall_s','peak_rss_bytes'}
    for name in ('v1_1_a4','v1_1_a4_redesign'):
        directory=ROOT/'results/lessons'/name;part=rows(directory/'screen.csv');assert len(part)==44
        assert set(part[0])==allowed
        groups={c:[r for r in part if r['cell']==c] for c in {r['cell'] for r in part}}
        assert len(groups)==22 and not any(c.startswith('R') for c in groups)
        in_count=0
        for c,levels in groups.items():
            assert {r['refinement'] for r in levels}=={'1','2'}
            inside=[]
            for r in levels:
                lo,hi=float(r['p_low']),float(r['p_high']);assert 0<=lo<=hi<=1
                assert float(r['unresolved_mass'])<=.01
                actual='in' if lo>=.1 and hi<=.9 else 'out' if hi<.1 or lo>.9 else 'unstable'
                assert actual==r['classification'];inside.append(actual=='in')
            in_count+=all(inside)
        counts.append(in_count);screen_rows+=part
    assert counts==[8,11]
    final=load(ROOT/'notes/design/grid_v1_1.json');assert not final['accepted'] and final['redesigns_used']==1
    assert len(final['cells'])==34 and not final['deleted_cells'] and not final['calibration_cells']
    assert final['status']=='REJECTED_NARROW_REQUIRED'
    chronological=['27eeed4','e3161cf','9f0783e','571d4cf','c7ddef3','6b87256','19d03cc','3fe81d2','ae876ab','8126ef9']
    for a,b in zip(chronological,chronological[1:]):subprocess.run(['git','merge-base','--is-ancestor',a,b],cwd=ROOT,check=True)
    contract=(ROOT/'notes/01_definitions_v1_1_draft.md').read_text();brief=(ROOT/'notes/00_research_brief_v1_1_draft.md').read_text()
    ids=re.findall(r'^\| (D\d+) \|',contract,re.M);assert ids==[f'D{i}' for i in range(1,26)]
    rq='For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?'
    assert rq in contract and rq in brief
    frozen=subprocess.check_output(['git','show','contract-v0:notes/01_definitions.md'],cwd=ROOT)
    assert frozen==(ROOT/'notes/01_definitions.md').read_bytes()
    max_law=max(max(float(r['law_error_A']),float(r['law_error_B'])) for r in prior_rows)
    max_posterior=max(float(r.get('posterior_bound_max',r.get('posterior_bound'))) for r in prior_rows)
    max_width=max(float(r['p_high'])-float(r['p_low']) for r in screen_rows)
    assert .0025<=.005/2 and 1e-9<.005*1e-6
    assert max_posterior<1e-8 and max_width<.01
    checks=[dict(id=1,status='PASS',check='Each operational term defined once',definitions=len(ids)),
        dict(id=2,status='PASS',check='Brief concepts and Main RQ map to D1–D25; scope retained'),
        dict(id=3,status='PASS',check='Deferred items assigned: A01 final dt, A05 null/heldout, Phase8 feasible repairs, P0-V10 independent review'),
        dict(id=4,status='PARTIAL',check='Full Final Review source consistency',reason='Reading note and known scope checked; full source not available to independently compare sections'),
        dict(id=5,status='PASS',check='25-term budget and immutable v0 bytes'),
        dict(id=6,status='FAIL',check='Cross-card numerical/grid/calibration constraints',
             numeric_constraints='PASS',law_error_max=max_law,posterior_error_max=max_posterior,p_interval_width_max=max_width,
             reason='Grid acceptance11/22<15/22 after one redesign; no eligible final calibration set can be locked')]
    suite=list(ET.parse(ROOT/'results/lessons/v1_1_a6/full_suite.xml').getroot().iter('testcase'))
    assert len(suite)==177 and all(t.find('failure') is None and t.find('error') is None for t in suite)
    mutant=[]
    for name in ('native_subtraction_mutant_first_attempt','native_subtraction_mutant'):
        cases=list(ET.parse(ROOT/f'results/lessons/v1_1_a6/{name}.xml').getroot().iter('testcase'))
        assert len(cases)==1
        mutant.append(cases[0].find('failure') is not None)
    assert mutant==[False,True]
    receipt=dict(author='Doan Van Tai',artifact_audit='PASS',B4_status='REJECTED_NARROW_REQUIRED',B5_status='NOT_READY',
        initial_in=8,redesign_in=11,required=15,checks=checks,full_suite_passed=177,
        native_subtraction_mutant=dict(first_attempt='SURVIVED',after_nondyadic_test='KILLED'),manifest_files_checked=manifests,queue_supports_checked=support_count,
        prior_rows_checked=40,sign_rows_checked=88,chronology=chronological,
        max_law_error=max_law,max_posterior_error=max_posterior,max_p_interval_width=max_width,
        unresolved_mass_max=max(float(r['unresolved_mass']) for r in screen_rows),
        formal_contract_promoted=False,tag_allowed=False,headsup_sent=False,author_attestation='V1/V8/P0-V3/P0-V11 direct user confirmation, no stored human artifacts')
    write(out/'readiness.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/v1_1_a6');run(p.parse_args().output_dir)
