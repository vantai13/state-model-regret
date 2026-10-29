"""Doan Van Tai — design metadata and exact finite toys only; no research engine."""
import ast
import csv
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.R3R_05_contract import schema as S, rules as R
from experiments.lessons.run_l3r_2 import load_reference

ROOT=Path('results/lessons/l3r_5')
SPEC=Path('experiments/R3R_05_contract/contract_spec.json')


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    spec=json.loads(SPEC.read_text());source=spec['source_allowlist'];pilot=source['pilot_commit']
    assert subprocess.check_output(['git','rev-parse','explore-v13-pilot^{commit}'],text=True).strip()==pilot
    stages={};hashes={};flat=[]
    for rel in source['design_files']:
        # Only preregistered design specs.json files, never regimes.csv/pairs.npz.
        if not rel.endswith('/specs.json'):raise ValueError('design-only source contract violated')
        raw=subprocess.check_output(['git','show',f'{pilot}:{rel}']);hashes[rel]=sha(raw)
        stage=Path(rel).parent.name;records=[S.from_pilot(r) for r in json.loads(raw)]
        stages[stage]=records
        for row in records:
            d=S.derived(row)
            flat.append(dict(id=row['id'],stage=stage,scientific_key=S.key_string(row),
                             **{k:row[k] for k in S.IDENTITY},
                             phi=str(d['phi']),eta_pilot=row['provenance']['eta_pilot'],
                             K=row['numerics']['K'],ref=row['numerics']['ref']))
    main_rows=sum((stages[s] for s in ['stage1','stage2','stage3']),[])
    all_rows=sum(stages.values(),[])
    keys={S.canonical(r) for r in main_rows}
    dropped_cost={S.canonical(r)[:-1] for r in main_rows}
    with_numerics={S.canonical(r)+(r['numerics']['K'],r['numerics']['ref']) for r in all_rows}
    assert len(main_rows)==216 and len(keys)==210 and len(dropped_cost)==162
    assert len({S.canonical(r) for r in all_rows})==210 and len(with_numerics)>210
    assert all(not S.validity_errors(r) for r in all_rows)
    eta_checks=sum(1 for r in main_rows if F(r['lambdaB'])==8)
    assert all(S.derived(r)['phi']==F(r['provenance']['eta_pilot']) for r in main_rows if F(r['lambdaB'])==8)
    primary=[r for r in main_rows if F(r['c_sw'])==0]
    assert all(S.validate(r,primary=True) for r in primary)
    ROOT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'scientific_regimes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator='\n');w.writeheader();w.writerows(flat)
    reference=load_reference();goldens=[]
    for label,q in [('mode_only',{'x1':5,'x2':5}),('backlog_only',{'x1':8,'x2':2})]:
        P=reference.harm_toy(-2)|{'q':q};L=reference.cells(P);G=reference.contrasts(L)
        goldens.append(dict(toy=label,GS=str(G['GS']),F=str(G['F']),V=str(G['V']),unit='toy_cost_unit'))
    xs=('aON','aOFF','bON','bOFF')
    P=reference.one_snapshot(J={x:10 for x in xs},Delta=dict(zip(xs,(-1,-1,-1,1))),
                            Dhat=dict(zip(xs,(-1,2,-3,1))),q={x:x[0] for x in xs})
    G=reference.contrasts(reference.cells(P))
    goldens.append(dict(toy='cancellation',GS=str(G['GS']),F=str(G['F']),V=str(G['V']),unit='toy_cost_unit'))
    assert [(r['GS'],r['F'],r['V']) for r in goldens]==[('-1/2','0','-1/2'),('-1/2','-1/2','0'),('0','-1/2','1/2')]
    roe=R.ratio_of_expectations([F(1,2)]*2,[F(1,10)]*2,[1,19])
    eor=sum(F(1,2)*F(1,10)/d for d in [1,19])
    w=[F(1,2),F(3,10),F(1,5)];g=[0,F(4,5),0];c=[2,10,20]
    stationary=R.ratio_of_expectations(w,g,c)
    filtered=R.ratio_of_expectations(R.conditional_weights(w,[False,True,True]),g,c)
    near=R.classify_threshold(F('.0098'),F('.002'))
    assert (roe,eor,stationary,filtered,near)==(F(1,100),F(1,19),F(3,100),F(6,175),'UNRESOLVED')
    (ROOT/'toy_metrics.json').write_text(json.dumps(dict(RoE=str(roe),EoR=str(eor),P1_ratio=str(stationary),
                    P2a_ratio=str(filtered),D22_goldens=goldens,near_threshold_status=near,
                    zero_denominator=R.relative(0,0),population_engine_D22_implemented=False),indent=2)+'\n')
    with (ROOT/'toy_metrics.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['metric','fraction','decimal'],lineterminator='\n');writer.writeheader()
        for name,value in [('RoE',roe),('EoR',eor),('P1',stationary),('P2a',filtered)]:writer.writerow(dict(metric=name,fraction=str(value),decimal=float(value)))
    # Source boundary: this task's production helpers import no physical engine.
    forbidden=('smr','experiments.A00_engine','experiments.R3R_02_audit')
    for name in ['schema.py','rules.py','freeze.py','run_checks.py']:
        tree=ast.parse(Path('experiments/R3R_05_contract',name).read_text())
        modules=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        assert not any(m and m.startswith(forbidden) for m in modules),name
    result=dict(owner='Doan Van Tai',created_utc=datetime.now(timezone.utc).isoformat(),status='PASS',
                metadata_source_hashes=hashes,stage_counts={s:len(r) for s,r in stages.items()},
                main_ids=len(main_rows),scientific_distinct=len(keys),distinct_if_cost_omitted=len(dropped_cost),
                all_metadata_ids=len(all_rows),distinct_if_numerics_included=len(with_numerics),
                invalid_metadata_records=0,lambdaB8_eta_phi_checks=eta_checks,
                primary_zero_cost_ids=len(primary),primary_zero_cost_distinct=len({S.canonical(r) for r in primary}),
                D22_golden_checks=3,physical_D22_status='IMPLEMENTATION_AUDIT_DEFERRED',
                CF_collision_check='NOT_RUN_NO_CF_GENERATED',new_CF_regimes=0,new_research_J_gap_contrast=0,
                new_simulation_or_MC_runs=0,source_engine_boundary='PASS',
                frozen_file_hashes={rel:sha(Path(rel).read_bytes()) for rel in spec['freeze_paths']})
    (ROOT/'candidate_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['metadata_source_hashes','frozen_file_hashes']},indent=2))


if __name__=='__main__':main()
