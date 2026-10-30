"""Post-stop, read-only accounting and oracle-bound diagnosis. No new calls."""
import csv
from fractions import Fraction as F

from .common import ROOT,OUT,LEVELS,load,plan,write_once


def main():
    failing=load(OUT/'native/P44_000/level_640_4.json')
    c=F(failing['Cref'])
    old=F(failing['losses']['00']);oracle=F(failing['losses']['11'])
    old_error=F(failing['cost_error']['00']);oracle_error=F(failing['cost_error']['11'])
    diagnosis=dict(responsible='Doan Van Tai',scope='read-only original raw row; no additional physical evaluation',
        id='P44_000',parameters=failing['parameters'],failed_stage='rho=0, cell00, oracle arithmetic sanity before theta0 bit checks',
        L00=str(old),L11=str(oracle),L00_error=str(old_error),L11_error=str(oracle_error),
        L11_minus_L00=str(oracle-old),sum_arithmetic_errors=str(old_error+oracle_error),
        excess_beyond_arithmetic_errors=str(oracle-old-old_error-oracle_error),
        apparent_oracle_violation_pctC=float(100*(oracle-old)/c),
        raw_arithmetic_pass=failing['arithmetic_pass'],raw_validity_errors=failing['validity_errors'],
        frozen_lean_width_pass=True,frozen_lean_consistency_violations=[],
        R1='NOT_EVALUATED: stopped before two coarse neighbours',
        interpretation='Original cell00 already violates oracle bound outside reported arithmetic errors; cannot attribute failure to positive margin. Finite-quadrature discrepancy is a candidate explanation, not established root cause.',
        forbidden_inferences=['not a physical oracle violation proof','not a model/SH/MV falsification','not evidence every baseline or every card numerics fails'],
        next='Preregister diagnosis of quadrature/oracle-bound coverage or establish a suitable error certificate; preserve threshold and failed attempt. No posthoc widening or rho selection.')
    from experiments.R3R_14_lean_close.checks import arithmetic_ok,consistency
    diagnosis['frozen_lean_width_pass']=bool(arithmetic_ok(failing))
    diagnosis['frozen_lean_consistency_violations']=consistency(failing)
    write_once(ROOT/OUT/'sanity_diagnosis.json',diagnosis)
    raw=[];grid=[]
    for case in plan()['cases']:
        for lv in LEVELS:
            path=ROOT/OUT/'native'/case['id']/f'level_{lv[0]}_{lv[1]}.json'
            if not path.exists():continue
            row=load(path.relative_to(ROOT));raw.append(row)
            if lv!=LEVELS[0] or row.get('baseline_sanity_pass') is not True:continue
            for b in row['baseline']:
                cc=F(row['Cref']);gm=F(row['G_M'])
                grid.append(dict(id=case['id'],aliases='|'.join(case['aliases']),rho_grid=b['rho'],
                    L00_original=row['losses']['00'],L10_original=row['losses']['10'],
                    L00_margin=b['L00'],L10_margin=b['L10'],
                    GS_original_pctC=float(100*F(row['G_S'])/cc),
                    GS_margin_pctC=float(100*F(b['GS_theta'])/cc),
                    R_M=None if gm<=0 else float((F(row['losses']['00'])-F(b['L00']))/gm),
                    deltaL10=b['deltaL10'],Stay=row['Stay'],Stay_headroom_pctC=float(100*(F(row['Stay'])-cc)/cc),
                    selected_rho_star=False))
    with (ROOT/OUT/'observed_baselines.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(grid[0]),lineterminator='\n');writer.writeheader();writer.writerows(grid)
    control=load(OUT/'controls/P44_CONTROL_U0/level_640_4.json')
    benchmark=load(OUT/'benchmark_summary.json')
    measured=sum(r['call_cpu_seconds'] for r in raw)
    measured_control=control['call_cpu_seconds']
    accounting=dict(responsible='Doan Van Tai',discovery_native_level_rows=len(raw),
                    discovery_baseline_sanity_pass_rows=sum(r.get('baseline_sanity_pass') is True for r in raw),
                    control_level_rows=1,discovery_eval_cpu_seconds=measured,control_eval_cpu_seconds=measured_control,
                    total_eval_cpu_seconds=measured+measured_control,
                    recorded_benchmark_summary_cpu_seconds=benchmark['cpu_seconds'],
                    summary_omitted_failed_case_cpu_seconds=failing['call_cpu_seconds'],
                    benchmark_wall_seconds=benchmark['wall_seconds'],
                    added_baseline_cpu_seconds=sum(r['baseline_added_cpu_seconds'] for r in raw),
                    scope_note='evaluation-call CPU only; does not include every import/launch/compiler child cost',
                    not_run_cases=90-3,selected_rho_star=False,forecast_status='NOT_EVALUABLE')
    write_once(ROOT/OUT/'measured_summary.json',accounting)
    print(diagnosis,flush=True);print(accounting,flush=True)


if __name__=='__main__':main()
