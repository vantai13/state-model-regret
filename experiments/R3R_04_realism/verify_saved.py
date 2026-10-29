"""Doan Van Tai — audit saved artifacts; never run the research engine."""
import csv
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from datetime import datetime,timezone

from experiments.R3R_04_realism.run_screen import verify_freeze,git_bytes,sha

ROOT=Path('results/lessons/l3r_4')
BASE='75601f304d1eb83a3e482aa29ae1abcbfcd9e7df'


def main():
    summary=json.loads((ROOT/'summary.json').read_text())
    receipt=json.loads((ROOT/'screen/receipt.json').read_text())
    freeze,_,hashes=verify_freeze(summary['freeze_commit'])
    for path in ['experiments/R3R_04_realism/check_stationary.py','experiments/R3R_04_realism/implied.py']:
        assert git_bytes(summary['original_envelope_commit'],path)==git_bytes(freeze,path),path
    subprocess.run(['git','merge-base','--is-ancestor',summary['original_envelope_commit'],freeze],check=True)
    subprocess.run(['git','merge-base','--is-ancestor',freeze,summary['labels_commit']],check=True)
    for path,expected in receipt['outputs'].items():
        assert sha(Path(path).read_bytes())==expected,path
        assert Path(path).read_bytes()==git_bytes(summary['labels_commit'],path),path
    labels=list(csv.DictReader((ROOT/'screen/labels.csv').open()))
    features=list(csv.DictReader((ROOT/'screen/implied_features.csv').open()))
    assert len(features)==432 and len(labels)==1296
    assert set(Counter(r['id'] for r in features).values())=={2}
    assert set(Counter(r['id'] for r in labels).values())=={6}
    assert len({r['id'] for r in labels})==216 and len({r['coordinate'] for r in labels})==210
    assert {r['label'] for r in labels}=={'UNSOURCED'}
    assert {len(r['missing'].split(';')) for r in labels}=={10}
    pairs={}
    for row in features:pairs.setdefault(row['id'],{})[row['context']]=row
    checks=0
    for rid,pair in pairs.items():
        a,b=pair['a'],pair['b']
        for name in ['T_mode_s','h_physical_s',*[q+'_virtual_delay_time_mean_s' for q in ['A_pre','A_post','B_pre','B_post']]]:
            assert math.isclose(float(b[name]),10*float(a[name]),rel_tol=2e-12,abs_tol=1e-14),(rid,name)
            checks+=1
        for name in ['phi','rho_A_pre','rho_B_post','mode_correlation_over_age',*[q+'_tail_delay_5T_sensitivity_only' for q in ['A_pre','A_post','B_pre','B_post']]]:
            assert math.isclose(float(a[name]),float(b[name]),rel_tol=2e-12,abs_tol=1e-14),(rid,name)
            checks+=1
        assert a['buffer_flag']==b['buffer_flag']=='UNSOURCED'
        assert a['actuation_flag']==b['actuation_flag']=='UNSOURCED'
        assert a['mode_oracle_flag']==b['mode_oracle_flag']=='True'
    protected=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--','src','experiments/A00_engine','experiments/A05_freeze','notes/01_definitions_v1_2.md','notes/01_definitions_v1_3_draft.md','notes/phases/PHASE_3_prediction_card.md','notes/phases/PHASE_3_prediction_card.lock.json'],text=True).splitlines()
    for path in protected:assert Path(path).read_bytes()==git_bytes(BASE,path),path
    old_plan=git_bytes(BASE,'notes/phases/PHASE_3R.md')
    assert Path('notes/phases/PHASE_3R.md').read_bytes().endswith(old_plan),'historical plan body changed'
    assert subprocess.check_output(['git','rev-parse','explore-v13-pilot^{commit}'],text=True).strip()=='a7435e9a3cb0d1625479c942041ec6748444014a'
    # Check existing L3R.3 evidence was not modified by the realism task.
    old_manifest=json.loads(Path('results/lessons/l3r_3/artifact_index.json').read_text())
    for path,expected in old_manifest.items():assert sha(Path(path).read_bytes())==expected,path
    files=list(ROOT.rglob('*'))+list(Path('notes/realism').glob('*'))+list(Path('experiments/R3R_04_realism').glob('*.py'))+list(Path('experiments/R3R_04_realism').glob('*.json'))
    excluded={'verification.json','artifact_index.json','verify_run.log','publication.json'}
    manifest={str(p):sha(p.read_bytes()) for p in sorted(set(files)) if p.is_file() and p.name not in excluded}
    (ROOT/'artifact_index.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Only new/updated task-facing documentation; no unrelated historic links.
    docs=[p for p in Path('notes/realism').glob('*.md')]+[ROOT/'report.md',ROOT/'blind_review.md']
    links=0
    for doc in docs:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',doc.read_text()):
            if target.startswith(('https:','http:','#')):continue
            path=(doc.parent/target.split('#')[0]).resolve()
            # This audit's own output is written after all assertions pass.
            if path==(ROOT/'verification.json').resolve():continue
            assert path.exists(),(str(doc),target)
            links+=1
    result=dict(owner=summary['owner'],checked_utc=datetime.now(timezone.utc).isoformat(),status='PASS',
                scope='saved evidence and workflow integrity, not empirical realism',realism='HOLD_UNSOURCED',
                artifact_hashes=len(manifest),frozen_inputs=len(hashes),labels=len(labels),feature_rows=len(features),
                cross_anchor_checks=checks,protected_legacy_files=len(protected),old_audit_artifacts_preserved=len(old_manifest),
                historical_plan_body_preserved=True,local_links=links,full_tests=summary['full_tests'],
                no_engine_reexecution=True)
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
