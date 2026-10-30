"""Prepare a finite budget extension only if a clean parent stopped unfinished.

Never executes at import or samples CF. The caller must record the resource
decision and commit the generated prereg before starting the detached pipeline.
"""
import copy
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import subprocess
import sys

from experiments.R3R_07_confirmation.common import digest,write_once


def unfinished(summary, cfg):
    if summary.get('selected_levels') is not None:
        raise ValueError('parent already selected; no budget continuation needed')
    if any(r['status']!='COMPLETED' for r in summary['receipts']):
        raise ValueError('failed computation requires a separate diagnosis/version decision')
    expected={(stage,j['id']) for stage in cfg['stage_levels'] if stage!='marginal' for j in cfg['cases']}
    expected |= {('marginal',j['id']) for j in cfg['legacy_jobs']+cfg['marginals']}
    done={(r['stage'],r['id']) for r in summary['receipts']}
    missing=expected-done
    if not missing:
        raise ValueError('all registered levels finished; more budget cannot fix failed accuracy')
    return missing


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--decision',required=True,help='A new recorded resource decision, DL-NNN')
    args=parser.parse_args()
    if not re.fullmatch(r'DL-\d{3}',args.decision):parser.error('recorded DL-NNN decision required')
    parent_path=Path('experiments/R3R_11_native_population/prereg.json')
    parent=json.loads(parent_path.read_text())
    raw=Path(parent['output']);summary=json.loads((raw/'summary.json').read_text())
    missing=unfinished(summary,parent)
    manifest=Path('results/lessons/l3r_7/full_numerics/native05/export_verification.json')
    if json.loads(manifest.read_text())['status']!='PASS':raise ValueError('parent export not verified')
    cfg=copy.deepcopy(parent)
    cfg.update(id='R3R_NATIVE_CALIBRATION_BUDGET_CONTINUATION_06',decision=args.decision,
        declared_at=datetime.now(timezone.utc).isoformat(),output='results/R3R_population_numerics/20261030_06')
    cfg['limits']['total_cpu_seconds']=86400
    cfg['resume']=dict(parent_prereg=str(parent_path),parent_prereg_sha256=digest(parent_path),
        parent_output=str(raw),snapshot_manifest=str(manifest),
        prior_carried_cpu_reserve_seconds=parent['carried_cpu_reserve_seconds'],
        rationale='clean finite budget stop; same numerical targets, cases, levels and source; reuse only verified completed receipts')
    cfg['deviation']='Versioned total calibration CPU extension12h→24h before continuation; per-job resources/thresholds/models/designs unchanged; no additional candidate levels or CF data.'
    paths=[*Path('experiments/R3R_13_budget_resume').glob('*.py'),
        Path('tests/test_native_budget_continuation.py'),parent_path,manifest]
    for path in paths:cfg['source_sha256'][str(path)]=digest(path)
    collected=subprocess.check_output([sys.executable,'-m','pytest','--collect-only','-q'],text=True)
    cfg['full_tests_required']=int(re.search(r'(\d+) tests collected',collected).group(1))
    write_once('experiments/R3R_13_budget_resume/prereg.json',cfg)
    print(json.dumps(dict(missing_registered_jobs=len(missing),total_cpu_seconds=86400,
        prior_recorded_native_cpu_seconds=summary['cpu_seconds'],CF_generated=0),indent=2))


if __name__=='__main__':main()
