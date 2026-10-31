"""Read-only L4.5 receipt/design verification. No data screening or engine calls."""
import argparse
import csv
from fractions import Fraction as F
from math import comb
import json

from .screen import ROOT,HERE,OUT,preflight,rules_adopted
from .identity_checks import fixtures
from experiments.P4_03_map_audit.common import sha,require,write_once,verify_prereg
from experiments.R3R_06_cards import verdict,stats
from experiments.R3R_07_confirmation import power


def load(path):
    return json.loads((ROOT/path).read_text())


def verify():
    require(rules_adopted(),'author-approved rules/source lock not valid')
    verify_prereg()  # Includes frozen physical sources, F1 cards and CF parameters.
    snapshot=preflight()
    require(snapshot==load(OUT/'dependency_preflight_after_lock.log'),'preflight snapshot changed')
    require(snapshot['status']=='BLOCKED_PART_B' and snapshot['author_rules_locked'],'unexpected dependency state')
    require(snapshot['real_boxes_evaluated']==0 and not snapshot['p_hat_computed'],'real box was screened')
    require(not list((ROOT/OUT/'box_trials').glob('*/trial_*.json')),'real trial artifacts exist')
    require(not (ROOT/HERE/'candidate_readiness.json').exists(),'unexpected candidate readiness receipt')
    require(not (ROOT/OUT/'native').exists(),'unexpected native data directory')
    registry=load(OUT/'box_registry_status.json')
    require(registry['counts']=={'SV':0,'SUB':0} and registry['trials']==[],'registry differs')
    choice=load(HERE/'author_choices.json')
    require(choice['approved_candidates']==['SV','SUB'] and choice['final_card_count'] is None,'author choice/card count changed')
    completion=load('notes/phases/L4_5_completion.json')
    require(completion['new_card_count'] is None and completion['PartB']=='BLOCKED_DEPENDENCIES','premature final card choice')
    for name,digest in load(OUT/'source_manifest.json')['source_sha256'].items():
        require(sha(ROOT/name)==digest,'existing note/source changed: '+name)
    manifest=load(OUT/'design/manifest.json')
    require(sha(ROOT/HERE/'design_power.py')==manifest['script_sha256'],'design script changed')
    for name,digest in manifest['outputs_sha256'].items():
        require(sha(ROOT/OUT/'design'/name)==digest,'design artifact changed')
    rows_checked=0
    with (ROOT/OUT/'design/power_no_unresolved.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            p=F(row['p_plus'])
            require(float(power.pass_power(60,p,F(1,5)))==float(row['two_region_power']),'two-region table mismatch')
            require(float(verdict.plus_power(60,p))==float(row['one_region_power']),'one-region table mismatch')
            rows_checked+=1
    with (ROOT/OUT/'design/power_with_unresolved.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            p,r=F(row['p_cond']),F(row['r'])
            require(float(power.robust_region_power(60,p,r,plus=True))==float(row['one_region_power']),'robust table mismatch')
            rows_checked+=1
    require(rows_checked==14,'design row count changed')
    require((stats.k_support(60,F(1,2),F(1,40)),stats.k_reject(60,F(1,2),F(1,40)))==(39,21),'cutoffs changed')
    design=load(OUT/'design/summary.json')
    for name,bracket in design['min_p_for_half_power'].items():
        lo,hi=F(bracket['lower']),F(bracket['upper'])
        rp,rm=F(bracket['r_plus']),F(bracket['r_minus'])
        calc=(lambda p:power.robust_pass_power(60,p,F(1,5),rp,rm)) if name.startswith('SV') else (
              lambda p:power.robust_region_power(60,p,rp,plus=True))
        require(0<hi-lo<F(1,10_000_000) and calc(lo)<F(1,2)<=calc(hi),'minimum-power bracket invalid')
    with (ROOT/OUT/'design/R5_failure.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            r=F(row['r']);independent=sum(F(comb(60,k))*r**k*(1-r)**(60-k) for k in range(7,61))
            require(float(independent)==float(row['probability_R5_fails']),'R5 tail mismatch')
    saved=load(OUT/'design/identity_fixtures.json')
    for name in ('SV_and_MV_both_hold','AB_without_SUB'):
        example=fixtures()[name]
        require(all(F(saved[name][k])==example[k] for k in ('GS','GM','Gamma','Cref')),'identity example changed')
    require('16 passed in 0.18s' in (ROOT/OUT/'targeted_tests_16_pass.log').read_text(),'targeted test receipt missing')
    require('813 passed in 82.29s' in (ROOT/OUT/'full_tests.log').read_text(),'full test receipt missing')
    error=(ROOT/OUT/'blocked_screen_entrypoint.log').read_text()
    require('RuntimeError: PART_B_BLOCKED:' in error and 'FileNotFoundError' not in error,'entrypoint read data before dependency guard')
    artifact=load(OUT/'artifact_manifest.json')
    for name,receipt in artifact['files'].items():require(sha(ROOT/name)==receipt['sha256'],'artifact changed: '+name)
    return dict(responsible='Doan Van Tai',verification_status='PASS',
                scientific_status='PART_A_RULES_ADOPTED_PART_B_BLOCKED',
                author_choices_and_committed_rules='PASS',frozen_physical_F1_CF_hashes='PASS',
                local_note_hashes='PASS',power_table_rows_checked=14,minimum_power_brackets_checked=4,
                R5_tails_checked=2,exact_counterexamples_checked=2,
                plus_support_min=39,minus_reject_max=21,
                targeted_tests_passed=16,full_tests_passed=813,full_test_seconds=82.29,
                dependency_preflight='EXPECTED_BLOCKED',real_entrypoint='REFUSED_BEFORE_INPUT_READ',
                real_box_trials=0,new_box_p_hat=False,new_research_engine_calls=0,new_CF_outcomes=0,
                final_card_count=None,F1_unchanged=True,G_level='G1',artifact_files_checked=len(artifact['files']))


def main():
    p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
    result=verify()
    if args.output:write_once(ROOT/args.output,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
