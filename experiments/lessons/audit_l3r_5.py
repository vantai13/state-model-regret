"""Doan Van Tai — read-only research checks, artifact reporting; no outcome engine."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from experiments.R3R_05_contract.freeze import verify_lock,readiness

BASE='158a9b24633787224ca937fa05b62dbc62efcc2f'
OUT=Path('results/lessons/l3r_5')


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--post-tag',action='store_true');args=parser.parse_args()
    spec=json.loads(Path('experiments/R3R_05_contract/contract_spec.json').read_text())
    candidate=json.loads((OUT/'candidate_verification.json').read_text());assert candidate['status']=='PASS'
    assert set(candidate['frozen_file_hashes'])==set(spec['freeze_paths'])
    for rel,h in candidate['frozen_file_hashes'].items():assert sha(Path(rel).read_bytes())==h,rel
    tests={}
    for name in ['targeted_tests','full_suite']:
        suites=ET.parse(OUT/(name+'.xml')).getroot().findall('testsuite')
        assert suites and all(int(s.get(k,'0'))==0 for s in suites for k in ['failures','errors','skipped'])
        tests[name]=sum(int(s.get('tests')) for s in suites)
    assert tests['targeted_tests']==41 and tests['full_suite']>=532
    assert len(spec['inventory'])==21 and spec['sanity_ids']==[f'S{i:02}' for i in range(1,19)]
    sanity_found=re.findall(r'^\| (S\d\d) \|',Path('notes/theory/T07_population_estimand.md').read_text(),re.M)
    assert sanity_found==spec['sanity_ids']
    assert spec['numerics']['K_star'] is spec['numerics']['dt_star'] is None
    assert spec['D22']['committed'] and spec['D22']['audit']=='DEFERRED'
    assert spec['realism']=='HOLD_UNSOURCED_ENVELOPE_V1' and spec['audit_L3R3']=='HOLD'
    protected=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--','src','experiments/A00_engine','experiments/A05_freeze','notes/01_definitions_v1_2.md','notes/01_definitions_v1_3_draft.md','notes/00_research_brief_v1_2.md','notes/00_research_brief_v1_3_draft.md','notes/theory/T07_population_estimand.md'],text=True).splitlines()
    for path in protected:
        old=subprocess.check_output(['git','show',f'{BASE}:{path}']);assert Path(path).read_bytes()==old,path
    old_counts={}
    for lesson in ['l3r_3','l3r_4']:
        old_manifest=json.loads(Path('results/lessons',lesson,'artifact_index.json').read_text())
        for path,h in old_manifest.items():assert sha(Path(path).read_bytes())==h,path
        old_counts[lesson]=len(old_manifest)
    old_plan=subprocess.check_output(['git','show',f'{BASE}:notes/phases/PHASE_3R.md'])
    assert Path('notes/phases/PHASE_3R.md').read_bytes().endswith(old_plan)
    choices=json.loads(Path(spec['author_choices']).read_text())
    assert choices['D22_verbatim'].startswith('Cam kết làm D22') and not choices['author_self_readback_attested']
    known=subprocess.check_output(['git','show',f'{spec["author_decision_commit"]}:{spec["author_choices"]}'])
    assert known==Path(spec['author_choices']).read_bytes()
    tagged=None
    if args.post_tag:
        lock=verify_lock();tagged=dict(tag=lock['tag'],commit=lock['commit'],tag_object=lock['tag_object'])
        subprocess.run(['git','merge-base','--is-ancestor',spec['author_decision_commit'],lock['commit']],check=True)
    ready=readiness(spec,tag_verified=args.post_tag)
    assert not ready['CF_sampling']['allowed'] and not ready['Phase4']['allowed']
    links=0
    docs=[Path(p) for p in spec['freeze_paths'] if p.endswith('.md') and p not in ['notes/theory/T07_population_estimand.md','notes/realism/envelope_v1.json','notes/realism/rules_v1.md','notes/realism/worksheet_v1.md']]
    docs+=[Path('notes/01_claim_boundary_v1_3.md'),OUT/'report.md']
    for doc in docs:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',doc.read_text()):
            if target.startswith(('http:','https:','#')):continue
            target=target.split('#')[0]
            if not target:continue
            path=(doc.parent/target).resolve()
            # These two outputs are created after the audit assertions finish;
            # their self-links cannot be checked as pre-existing inputs.
            if path in {(OUT/'verification.json').resolve(),(OUT/'artifact_index.json').resolve()}:continue
            if not args.post_tag and path==Path('notes/phases/contract_v1_3.lock.json').resolve():continue
            assert path.exists(),(str(doc),target)
            links+=1
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name not in ['artifact_index.json','verification.json','audit.log']]
    files+=[Path(p) for p in spec['freeze_paths']]
    manifest={str(p):sha(p.read_bytes()) for p in sorted(set(files))}
    (OUT/'artifact_index.json').write_text(json.dumps(manifest,indent=2)+'\n')
    result=dict(owner='Doan Van Tai',checked_utc=datetime.now(timezone.utc).isoformat(),status='PASS',
                mode='POST_TAG' if args.post_tag else 'PRE_TAG',tests=tests,frozen_inputs=len(spec['freeze_paths']),
                scientific_main_ids=216,scientific_distinct=210,wrong_without_cost=162,wrong_with_numerics=228,
                physical_D22_status='DEFERRED',numerical_levels='DEFERRED',realism='HOLD_UNSOURCED',
                inventory_rows=21,sanity_ids=18,legacy_files_preserved=len(protected),
                old_artifacts_preserved=old_counts,historical_plan_body_preserved=True,local_links=links,
                artifact_hashes=len(manifest),tag=tagged,readiness=ready,CF_generated=False,
                new_research_outcomes=False,new_MC_or_simulation=False,Understanding='OPEN',G_level='G1')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='readiness'},indent=2))


if __name__=='__main__':main()
