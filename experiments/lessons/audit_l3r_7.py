"""Doan Van Tai — audit saved L3R.7 preparation, without engine or sampling."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from experiments.R3R_05_contract.freeze import verify_lock
from experiments.R3R_06_cards.verify_cards import verify
from experiments.R3R_07_confirmation.common import git,digest


def main():
    root=Path('results/lessons/l3r_7')
    contract=verify_lock(); card=verify()
    assert card['status']=='PASS' and card['files']==10
    assert contract['commit']=='3d2359b32d7bd24f9e9072d5b5b8131bd33fffa0'
    def count(path):
        suites=ET.parse(path).getroot().iter('testsuite')
        rows=list(suites)
        assert all(int(s.get('failures','0'))==int(s.get('errors','0'))==int(s.get('skipped','0'))==0 for s in rows)
        return sum(int(s.get('tests','0')) for s in rows)
    targeted=count(root/'logs/targeted_tests.xml'); full=count(root/'logs/full_suite.xml')
    assert targeted==38 and full==587
    prep=json.loads((root/'preparation/preparation_summary.json').read_text())
    assert prep['CF_generated']==prep['confirmation_roots_allocated']==prep['research_engine_runs']==0
    assert prep['inventory_records']==308 and prep['distinct_reserved_v13_keys']==245
    assert prep['saved_discovery_rows']==prep['unpaired_pilot_unresolved']==88
    inv=json.loads((root/'preparation/collision_inventory.json').read_text())
    for name,expected in inv['sources'].items():
        if ':' in name and name.startswith(inv['pilot_commit']):
            actual=hashlib.sha256(git('show',name)).hexdigest()
        else:
            actual=digest(name)
        assert actual==expected,name
    attempts=[json.loads(p.read_text()) for p in (root/'refusal_attempts').glob('*.json')]
    assert len(attempts)==3 and all(x['status']=='REFUSED' and x['engine_runs']==0 for x in attempts)
    assert not list(root.rglob('regimes_cf.json')) and not list(root.rglob('prereg.json'))
    power=json.loads((root/'preparation/power.json').read_text())
    assert len(power['power'])==36 and len(power['R5'])==12 and len(power['R4_R5'])==12
    choices=json.loads((root/'author_choices.json').read_text())
    budget=json.loads(Path('notes/design/confirmation_compute_budget_v1.json').read_text())
    completion=json.loads(Path('notes/phases/L3R_7_completion.json').read_text())
    assert choices['n_rule']==budget['n_rule']['status']==completion['n_rule_status']=='AUTHOR_ADOPTED'
    assert choices['compute_budget_sha256']==digest(choices['compute_budget'])
    assert choices['budget_cpu_hours']==budget['budget_cpu_hours']==completion['budget_cpu_hours']==48
    assert budget['budget_cpu_seconds']==3600*budget['budget_cpu_hours']
    assert choices['workers_initial']==budget['workers']['initial']==2
    assert choices['workers_max']==budget['workers']['maximum']==4
    assert all(x is None for x in (choices['n'],choices['n_bnd'],choices['confirmation_root'],budget['workers']['final_count']))
    hardware=json.loads(Path(budget['hardware_snapshot']).read_text())
    assert len(hardware['cpu']['affinity'])>=budget['workers']['maximum']
    assert hardware['memory']['available_bytes']>(6+3)*1024**3
    result=dict(owner='Doan Van Tai',status='PASS_PREPARATION_ONLY',targeted_tests=targeted,full_tests=full,
                frozen_contract_inputs=len(contract['source_sha256']),frozen_card_files=card['files'],
                runner_refusals=3,original_frozen_files_unchanged=True,**{k:prep[k] for k in
                 ('inventory_records','distinct_reserved_v13_keys','test_draws','sampler_frequency','CF_generated',
                  'confirmation_roots_allocated','research_engine_runs','Phase4','G_level')},
                n_rule_status=choices['n_rule'],budget_cpu_hours=budget['budget_cpu_hours'],
                workers_initial=2,workers_max=4,worker_internal_threads=1,
                test_results='recorded in preparation commit c4b4bf5; no full-suite rerun for metadata-only approval update',
                remaining=['numerics v1.3.1 and actual coverage/timing/r',
                           'final n/seed/prereg/CF list','audited backend + dry-run B','D22 audit/human/Gate3R'])
    (root/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    # The live stdout log and this index cannot hash their own final contents.
    index={str(p):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact_index.json' and not p.name.endswith('audit.log')}
    index[choices['compute_budget']]=digest(choices['compute_budget'])
    (root/'artifact_index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
