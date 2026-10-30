"""Doan Van Tai — L4.2 technical artifacts, AI theo ủy quyền.

No author addendum text is generated; no native map/CF/A05 engine is called.
Run with --out pointing to a new output directory. Original PNGs are copied from
the tag, never regenerated or silently corrected.
"""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import types

from experiments.P4_01_recount import recount_map as R
from experiments.P4_01_recount.verify_artifacts import verify
from . import toys
from .read_map import load_table,summarize,TABLE,MANIFEST


def golden_module():
    path=R.ROOT/'tests/test_p4_02_toys.py'
    spec=importlib.util.spec_from_file_location('l42_goldens_for_mutation',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def golden_checks(module):
    calls=[(name+'['+toy+']',getattr(module,name),(toy,))
           for name in ('test_toy_table','test_identities') for toy in toys.TOYS]
    calls.extend((name,getattr(module,name),()) for name in ('test_mutant_mechanism','test_mutant_tie_rule'))
    result=[]
    for name,fn,args in calls:
        try:
            fn(*args)
        except AssertionError:
            result.append(dict(test=name,status='FAIL_ASSERTION'))
        else:
            result.append(dict(test=name,status='PASS'))
    return result


def implementation_mutations():
    source=Path(toys.__file__).read_text()
    records=[]
    for name,before,after in [
        ('default_tie_switches','int(z < 0)','int(z <= 0)'),
        ('S0_leaks_current_state','a00 = (choose(gh),) * 2','a00 = tuple(choose(z) for z in dh)'),
    ]:
        if source.count(before)!=1:
            raise ValueError('mutation anchor not unique: '+name)
        mutant=types.ModuleType('l42_mutant_'+name)
        exec(compile(source.replace(before,after),str(toys.__file__),'exec'),mutant.__dict__)
        tests=golden_module()
        tests.cells=mutant.cells
        results=golden_checks(tests)
        caught=[r['test'] for r in results if r['status']=='FAIL_ASSERTION']
        records.append(dict(mutant=name,status='KILLED' if caught else 'SURVIVED',
                            caught_by=caught,tests=results))
    return records


def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(argv)
    if args.out.exists():
        raise FileExistsError('output exists; stop before reading data')
    integrity=verify()
    if integrity['status']!='PASS':
        raise ValueError('frozen/L4.1 integrity failed before reading map')
    summary,age_pairs,boundary,cross=summarize(load_table())
    goldens=golden_checks(golden_module())
    mutations=implementation_mutations()
    # Teaching recurrence only. The endpoint rule is not the continuous integral.
    q,c=toys.endpoint_cost((2,-4,3,0,-2),toys.F(1,4),toys.F(3,4))
    qt,ct=toys.endpoint_cost((2,-4,3,0,-2),toys.F(3,4),toys.F(9,4))
    qr,cr=toys.endpoint_cost((10,-20,15,0,-10),toys.F(1,4),toys.F(15,4))
    scaling=dict(unit='exact_recurrence_fixture_units',time_factor=3,cost_factor=str(ct/c),
                 rate_factor=5,rate_cost_factor=str(cr/c),base_cost=str(c),time_scaled_cost=str(ct),rate_scaled_cost=str(cr),
                 backlog_time_scaling_exact=qt==tuple(3*x for x in q),
                 backlog_rate_scaling_exact=qr==tuple(5*x for x in q),
                 continuous_ramp_costs=['4','16'],finite_endpoint_ramp_costs=['5','20'],
                 note='no production-engine audit, no finite test proves general scaling')
    summary.update(golden_passed=sum(r['status']=='PASS' for r in goldens),golden_total=len(goldens),
                   implementation_mutants_killed=sum(r['status']=='KILLED' for r in mutations),
                   implementation_mutants_total=len(mutations))
    summary['technical_status']='PASS' if (summary['verification_status']=='PASS' and summary['golden_passed']==8
                        and summary['implementation_mutants_killed']==2 and scaling['cost_factor']=='9'
                        and scaling['rate_cost_factor']=='5') else 'FAIL'
    args.out.mkdir(parents=True)
    for name,doc in [('map_summary.json',summary),('toys.json',toys.exact_toy_results()),
                     ('scaling_fixture.json',scaling),('golden_checks.json',goldens),
                     ('implementation_mutants.json',mutations),('integrity_before.json',integrity)]:
        (args.out/name).write_text(json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    for name,rows in [('age_pairs.csv',age_pairs),('near_boundary.csv',boundary),('lambdaA_lambdaB_classes.csv',cross),
                      ('delta_classes.csv',summary['delta_slice']['by_delta'])]:
        write_csv(args.out/name,rows)
    source_paths=[TABLE,MANIFEST,Path('notes/theory/T07_population_estimand.md'),Path('notes/01_definitions_v1_3.md'),
                  Path('experiments/P4_01_recount/recount_map.py'),Path('experiments/P4_01_recount/verify_artifacts.py'),
                  *sorted(Path('experiments/P4_02_reading').glob('*.py')),Path('tests/test_p4_02_toys.py'),
                  Path('tests/test_p4_02_read_map.py'),Path('tests/test_population_toys.py')]
    sources={str(path):R.digest((R.ROOT/path).read_bytes()) for path in source_paths}
    for name in ('regime_map_differ.png','regime_map_mechanism.png'):
        path='results/explore_v13/regime_map/'+name
        blob=R.git('show',f'{R.COMMIT}:{path}')
        (args.out/name).write_bytes(blob)
        sources[f'{R.COMMIT}:{path}']=R.digest(blob)
    plot_source='experiments/explore_v13/plot_map.py'
    sources[f'{R.COMMIT}:{plot_source}']=R.digest(R.git('show',f'{R.COMMIT}:{plot_source}'))
    manifest=dict(responsible='Doan Van Tai',provenance='AI theo ủy quyền; not author-written/self-check',
                  created_utc=datetime.now(timezone.utc).isoformat(),head=R.git('rev-parse','HEAD').decode().strip(),
                  source_sha256=sources,config=dict(arithmetic_toys='Fraction exact',seed=None,
                  map_tag=R.TAG,map_commit=R.COMMIT,map_levels='K40/ref1/dt1/120s; age/amp as stored',
                  numeric_roundoff_diagnostic_pp=R.TOL,boundary_radius_pp=.15,
                  delta_slice={'kappa_over_age':['1/20','3/20'],'h_over_age':['4','8'],'eta':['5/8','7/8'],'amp':'6'},
                  exploratory_A_by_delta='NOT_RUN',engine_calls=0,new_coordinates=0,CF_outcomes=0,
                  plot_action='byte copy of archived PNGs; no regeneration'),
                  author_addendum='OPEN; template only',G_level='G1',
                  outputs_sha256={f.name:R.digest(f.read_bytes()) for f in sorted(args.out.iterdir())})
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary['technical_status']!='PASS'


if __name__=='__main__':
    raise SystemExit(main())
