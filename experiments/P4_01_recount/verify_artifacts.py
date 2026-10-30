"""Doan Van Tai — read-only L4.1 integrity verification (AI theo ủy quyền).

No physics/engine imports; checks pinned hashes and the three prerequisite commits.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from .recount_map import ROOT, COMMIT


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def verify():
    locks={}
    for name in ('contract_v1_3.lock.json','PHASE_3R_hypothesis_cards.lock.json',
                 'PHASE_3R_hypothesis_cards_v2.lock.json','numerics_v1_3_1_lean.lock.json'):
        doc=json.loads((ROOT/'notes/phases'/name).read_text())
        hashes=doc.get('source_sha256',doc.get('sha256'))
        bad=[p for p,h in hashes.items() if sha(p)!=h]
        locks[name]=dict(files=len(hashes),mismatched=bad,status='PASS' if not bad else 'FAIL')
    old=json.loads((ROOT/'results/lessons/l3r_8/freeze_check.json').read_text())
    cfbad=[v['path'] for v in old['cf_prereg_artifacts'].values() if sha(v['path'])!=v['sha256']]
    cards=[]
    for name in ('PHASE_3R_hypothesis_cards.md','PHASE_3R_hypothesis_cards_v2.md'):
        text=(ROOT/'notes/phases'/name).read_text()
        cards.append(json.loads(re.search(r'<!-- L3R6_CARDS\s*(.*?)\s*-->',text,re.S).group(1)))
    # Compare these explicit fields; the existing frozen receipt checks whole files.
    equality={k:cards[0][k]==cards[1][k] for k in ('regions','family','allocation')}
    out=Path('results/P4_01_recount/20261030_01')
    manifest=json.loads((ROOT/out/'manifest.json').read_text())
    badout=[name for name,h in manifest['outputs_sha256'].items() if sha(out/name)!=h]
    script_match=sha('experiments/P4_01_recount/recount_map.py')==manifest['script_sha256']
    badsources=[]
    for name,h in manifest['source_sha256'].items():
        if ':' in name:
            blob=subprocess.check_output(['git','-C',str(ROOT),'show',name])
            actual=hashlib.sha256(blob).hexdigest()
        else:
            actual=sha(name)
        if actual!=h: badsources.append(name)
    inputs=json.loads((ROOT/'results/lessons/l4_1/input_manifest.json').read_text())
    badin=[r['snapshot'] for r in inputs['inputs'] if sha(r['snapshot'])!=r['sha256']]
    commits=['7385015','87d6f83','c3aa70b']
    ancestry=all(subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',a,b],capture_output=True).returncode==0
                 for a,b in zip(commits,commits[1:]+['HEAD']))
    tag_match=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','explore-v13-regime-map^{}'],text=True).strip()==COMMIT
    result=dict(responsible='Doan Van Tai',scope='read-only hashes and git ancestry; no engine, no CF outcomes',
                locks=locks,cf_prereg_artifacts=dict(files=len(old['cf_prereg_artifacts']),mismatched=cfbad),
                card_v1_v2_selected_scientific_fields_equal=equality,recount_outputs_mismatched=badout,
                recount_source_hash_mismatched=badsources,recount_script_sha_matches=script_match,
                input_snapshots_mismatched=badin,record_DL_exposure_commits=commits,
                record_before_DL_before_exposure=ancestry,map_tag_unchanged=tag_match)
    result['status']='PASS' if (all(x['status']=='PASS' for x in locks.values()) and not(cfbad or badout or badin or badsources)
                                and script_match and all(equality.values()) and ancestry and tag_match) else 'FAIL'
    return result


if __name__=='__main__':
    result=verify()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(result['status']!='PASS')
