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
    numeric_path=Path('results/R3R_numerics/20261029_01/verification.json')
    if numeric_path.exists():
        numeric=json.loads(numeric_path.read_text())
        from experiments.R3R_07_numerics.run import verify_prereg
        verify_prereg(Path('experiments/R3R_07_numerics/prereg.json'))
        assert numeric['legacy_exact_pass']==3 and numeric['stationary_attempts']==6
        assert numeric['CF_generated']==0 and numeric['K_star'] is numeric['n'] is numeric['confirmation_root'] is None
        assert numeric['status']=='HOLD_NUMERICS_FEASIBILITY'
        numeric_full=count(root/'numerics_logs/full_suite_final.xml')
        numeric_targeted=count(root/'numerics_logs/targeted.xml')
        assert numeric_full==595 and numeric_targeted==8
        assert completion['numerics_v1_3_1'] in ('HOLD_FEASIBILITY_STAGE0','HOLD_CANDIDATE_ADOPTION_AND_FULL_AUDIT')
        dependency=json.loads((root/'numerics_logs/post_run_dependency_check.json').read_text())
        assert dependency['in_preregistered_manifest'] is False and dependency['unchanged_against_run_commit'] is True
        assert digest(dependency['path'])==dependency['sha256_current']==dependency['sha256_at_run_commit']
        raw=Path('results/R3R_numerics/20261029_01')
        for p,h in json.loads((raw/'artifact_index.json').read_text()).items():assert digest(p)==h,p
        result.update(status='VERIFIED_PROCESS_NUMERICS_HOLD',full_tests=numeric_full,
                      numerics_targeted_tests=numeric_targeted,preparation_full_tests_historical=full,
                      test_results='595 full / 8 numerics targeted PASS before calibration; original 587/38 retained historical',
                      research_engine_runs=3,population_engine_scope='replay of three previously exposed anchors',
                      stationary_only_attempts=6,stationary_unresolved=3,new_regime_population_outcomes=0,
                      numerics_status=numeric['status'],numerics_verification=str(numeric_path),
                      dependency_manifest_limitation='cut_value omitted; post-run verified against source commit; full-audit closure required',
                      calibration_cpu_seconds=numeric['cpu_seconds'])
    capacity_path=root/'extended_capacity/candidate_verification.json'
    if capacity_path.exists():
        from experiments.lessons.report_stationary_candidates import candidate
        from experiments.R3R_07_numerics.run import verify_prereg
        candidates=json.loads(capacity_path.read_text())
        raw=Path('results/R3R_numerics/20261029_02')
        capacity=json.loads((raw/'capacity_verification.json').read_text())
        verify_prereg(Path('experiments/R3R_07_numerics/prereg_extended_v2.json'))
        assert capacity['CF_generated']==0 and capacity['n'] is capacity['confirmation_root'] is None
        assert candidates['CF_generated']==0 and candidates['n'] is candidates['confirmation_root'] is None
        assert candidates['numerical_adoption'] is candidates['global_accuracy_audit_completed'] is False
        transfer=json.loads((root/'extended_capacity/gcp/transfer_verification.json').read_text())
        assert transfer['status']=='PASS' and transfer['files_checked']==29
        for p,h in json.loads((root/'extended_capacity/gcp/raw_export_manifest.json').read_text()).items():assert digest(p)==h,p
        connection=json.loads((root/'extended_capacity/gcp_connection_receipt.json').read_text())
        assert connection['temporary_rule_cleanup']=='DELETED_VERIFIED_API'
        assert count(root/'extended_capacity/balanced_full_suite.xml')==633
        assert count(root/'extended_capacity/gcp/full_suite.xml')==633
        for row in candidates['candidate_rows']:
            actual,_=candidate(row['candidate'])
            assert actual==row
            candidate_raw=Path(row['raw'])
            for p,h in json.loads((candidate_raw/'artifact_index.json').read_text()).items():assert digest(p)==h,p
        for p,h in json.loads((raw/'artifact_index.json').read_text()).items():assert digest(p)==h,p
        total_cpu_lower=numeric['cpu_seconds']+capacity['cpu_seconds_lower']+sum(r['cpu_seconds'] for r in candidates['candidate_rows'])
        assert completion['stationary_only_attempts']==6+capacity['attempted']+candidates['attempted']
        assert completion['local_capacity_verification']==str(capacity_path)
        assert completion['new_CF_regimes']==0 and completion['n'] is completion['confirmation_root'] is None
        assert completion['numerical_candidates_adopted'] is False
        result.update(status='VERIFIED_CAPACITY_RESULTS_NUMERICS_HOLD',full_tests=633,cloud_full_tests=633,
                      test_results='633 full PASS local and independent cloud preflight; historical suites and interrupted baseline retained',
                      baseline_v1_stationary_only_attempts=6,
                      extended_baseline_attempts=capacity['attempted'],extended_baseline_completed=capacity['completed'],
                      numerical_candidate_attempts=candidates['attempted'],numerical_candidate_completed=candidates['completed'],
                      balanced_profile_attempts=candidates['balanced_profile_attempts'],
                      balanced_profile_completed=candidates['balanced_profile_completed'],
                      cloud_marginals_completed=sum(r['candidate']>=6 and r['status']=='COMPLETED' for r in candidates['candidate_rows']),
                      stationary_only_attempts=completion['stationary_only_attempts'],
                      original_baseline_distinct_completed=capacity['combined_stationary_completed'],
                      stationary_unresolved=completion['stationary_unresolved'],
                      baseline_distinct_unresolved=capacity['combined_stationary_total']-capacity['combined_stationary_completed'],
                      candidate_adoption=False,global_audit_complete=False,
                      numerics_status='HOLD_CANDIDATE_ADOPTION_AND_FULL_AUDIT',
                      numerics_verification=str(capacity_path),baseline_v1_numerics_verification=str(numeric_path),
                      dependency_manifest_limitation='historical v1 cut_value omission preserved; current candidate source manifests checked, full physical audit still pending',
                      local_capacity_status=capacity['status'],local_capacity_verification=str(capacity_path),
                      extended_baseline_verification=str(raw/'capacity_verification.json'),
                      current_manifest_files={'extended_baseline':48,'sparse_candidate':59,'balanced_local':63,'balanced_cloud':64},
                      GCP_used=True,GCP_started_by_agent=False,calibration_cpu_seconds=None,
                      calibration_cpu_seconds_lower=total_cpu_lower,
                      interrupted_attempt_final_metrics_known=False)
    (root/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    # The live stdout log and this index cannot hash their own final contents.
    index={str(p):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact_index.json' and not p.name.endswith('audit.log')}
    index[choices['compute_budget']]=digest(choices['compute_budget'])
    (root/'artifact_index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
