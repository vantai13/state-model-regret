"""Write-once L3R.7 preparation: hypothetical math, test seeds and old discovery.

This command creates no prereg.json, confirmation root or regimes_cf.json and does
not import a physical engine. Existing output is preserved on any rerun attempt.
"""
import argparse
import csv
from fractions import Fraction as F
import json
from pathlib import Path

from experiments.R3R_06_cards import discovery as D
from experiments.R3R_06_cards.regions import Box
from . import common as C, inventory as I, sampler as S, power as P, score as SC, feasibility as FE


def emit_csv(path,rows):
    with Path(path).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(argv); card=C.verified_card()
    args.out.mkdir(parents=True,exist_ok=False)
    log=D.ForkingLog(args.out/'forking_paths.jsonl')
    log.append(dict(kind='lesson_intake_and_planned_replay',owner='Doan Van Tai',
                    parent_log='results/lessons/l3r_6/forking_paths.jsonl',
                    parent_sha256=C.digest('results/lessons/l3r_6/forking_paths.jsonl'),parent_last_seq=21,
                    already_provided='L3R.7 Part3 MV16 values and location of SH15 non-meets',
                    plan='replay only the two already frozen regions against saved Stage1+2; no new regions/engine',
                    numerics='K40/ref1 pilot, no required coarse pairs; not confirmation'))
    inv=I.build();C.write_once(args.out/'collision_inventory.json',inv)
    table=P.tables();C.write_once(args.out/'power.json',table)
    for key,filename in (('power','power.csv'),('R5','r5_risk.csv'),('R4_R5','r4_r5_power.csv')):
        emit_csv(args.out/filename,table[key])
    C.write_once(args.out/'lattice_feasibility.json',FE.report(inv))
    rows,_=S.sample_region(C.TEST_ROOT,'MV+A',card['regions']['MV+A'],10000,set(),purpose='TEST_ONLY_NO_ENGINE')
    frequency=sum(F(row['regime']['kappa'])<F(1,5) for row in rows)/len(rows)
    import math
    C.write_once(args.out/'sampler_verification.json',dict(status='TEST_ONLY_NO_ENGINE',root=C.TEST_ROOT,
                 draws=10000,kappa_below_point2_frequency=frequency,
                 target_before_rounding=math.log(2)/math.log(3),
                 target_after_rounding=math.log(.1995/.1)/math.log(3),
                 test_parameters_persisted=False,environment=C.environment(),engine_runs=0))
    disc=D.load()
    summaries={}; old_rows=[]; old_results={}
    for name,col in (('MV+A','G_M_pctC'),('SH+A','G_S_pctC')):
        spec=card['regions'][name]
        box=Box(name,tuple((k,*v) for k,v in spec['bounds'].items()))
        listing=D.values(disc,box,[col,'Cbar'],log,who='Doan Van Tai (implementation under authorization)',
                         purpose='verify supplied lesson values only; no region change')
        emit_csv(args.out/('MV_discovery_values.csv' if name.startswith('MV') else 'SH_discovery_values.csv'),listing)
        values=sorted(F(str(row[col])) for row in listing)
        failures=[row for row in listing if F(str(row[col])) > -1] if name.startswith('SH') else []
        locations={}
        for row in failures:
            key=f"lambdaB={row['lambdaB']},lambdaA={row['lambdaA']}"
            locations[key]=locations.get(key,0)+1
        summaries[name]=dict(n=len(listing),sorted_percent_values=[float(x) for x in values],
                             non_meets_locations=locations)
        for row in listing:
            rid=row['id'];reg={'id':rid}
            old_rows.append(dict(regime=reg,origin_region=name))
            # Normalized saved values suffice to demonstrate missing-pair refusal.
            normalized=F(str(row[col]))/100
            main=dict(Cref='1',G_M=str(normalized) if name.startswith('MV') else '0',
                      G_S=str(normalized) if name.startswith('SH') else '0',
                      G_SM='0',Gamma='0',G_S_M1='0',G_M_S1='0')
            old_results[rid]=dict(main=main)  # deliberately NO coarse pair/arithmetic certificate
    C.write_once(args.out/'discovery_check.json',dict(scope='saved adaptive discovery, not evidence',
                                                   source_sha256=disc.blobs,regions=summaries))
    replay=SC.score_batch(old_rows,old_results)
    if set(replay['labels'].values())!={'UNRESOLVED'}:
        raise ValueError('old unpaired pilot data must not be labeled MEETS/FAILS')
    C.write_once(args.out/'unpaired_discovery_adapter.json',dict(status='PASS_EXPECTED_REFUSAL',
                 scope='format/label adapter only; NOT dry-run B at v1.3.1; dummy raw costs never reported as measurements',
                 counts=replay['counts'],cards=replay['cards']))
    C.write_once(args.out/'preparation_summary.json',dict(owner='Doan Van Tai',status='PREPARATION_ONLY',
                 inventory_records=len(inv['records']),distinct_reserved_v13_keys=inv['distinct_v13_keys'],
                 power_scenarios=len(table['power']),test_draws=10000,sampler_frequency=frequency,
                 saved_discovery_rows=len(old_rows),unpaired_pilot_unresolved=len(replay['labels']),
                 original_frozen_card_files=10,CF_generated=0,confirmation_roots_allocated=0,
                 research_engine_runs=0,full_dry_run_B='DEFERRED',Phase4='HOLD',G_level='G1'))
    print((args.out/'preparation_summary.json').read_text())


if __name__=='__main__':
    main()
