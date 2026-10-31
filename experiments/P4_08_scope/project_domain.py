"""Doan Van Tai — AI-assisted L4.8 metadata projection, not empirical validation.

Run: python -m experiments.P4_08_scope.project_domain --out NEW_DIRECTORY
"""
import argparse
from collections import Counter
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from experiments.R3R_05_contract import schema as S

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = Path('notes/realism/declared_domain_l4_8.json')


def scales(capacity_bps, tau_s):
    c, tau = S.exact(capacity_bps), S.exact(tau_s)
    if c <= 0 or tau <= 0:
        raise ValueError('positive capacity/tau required')
    rate, time = c/S.MU, tau/S.AGE
    return dict(rate=rate,time=time,backlog=rate*time,cost=rate*time*time)


def project(parameters, *, capacity_bps, tau_s, ref):
    """Map exact design parameters only. Overload after Switch remains valid."""
    a,b,k,e,h,c = map(S.exact, parameters)
    reg = dict(id='projection',contract_id=S.CONTRACT_ID,role='discovery',
               lambdaA=str(a),lambdaB=str(b),u=str(2*e),kappa=str(k),h=str(h),c_sw=str(c))
    S.validate(reg,primary=True)
    mult = scales(capacity_bps,tau_s)
    r,t,q = mult['rate'],mult['time'],mult['backlog']
    try:
        H = S.slot_count(reg,ref)
    except ValueError:
        H = None
    return dict(lambdaA_over_mu=float(a/S.MU),lambdaB_over_mu=float(b/S.MU),
                u_over_mu=float(2*e/S.MU),kappa=float(k),h_over_tau=float(h/S.AGE),
                rho_A_pre=float((a+2*e)/S.MU),rho_A_post=float(a/S.MU),
                rho_B_pre=float(b/S.MU),rho_B_post=float((b+2*e)/S.MU),
                background_ON_A_over_mu=float((a+S.AMPLITUDE)/S.MU),
                background_ON_B_over_mu=float((b+S.AMPLITUDE)/S.MU),
                physical_valid=True,current_native_supported=(b+2*e < S.MU),
                ref=ref,H=H,horizon_admissible=(H is not None),
                capacity_bps=float(S.exact(capacity_bps)),tau_s=float(S.exact(tau_s)),
                lambdaA_bps=float(a*r),lambdaB_bps=float(b*r),managed_bps=float(2*e*r),
                amplitude_bps=float(S.AMPLITUDE*r),T_mode_s=float(k*S.exact(tau_s)),
                h_s=float(h*t),dt_s=float(t/F(120*ref)),
                bits_per_model_backlog_unit=float(q),bytes_per_model_backlog_unit=float(q/8),
                bit_seconds_per_model_cost_unit=float(mult['cost']),
                physical_tau_measured=False,empirical_mapping_status='UNRESOLVED',
                projection_status='ILLUSTRATIVE_ONLY_NOT_CALIBRATED')


def designs():
    """Use prereg coordinates, not raw costs or L4.6 outcomes/class columns."""
    parking_path = Path('results/lessons/l4_5_v2/parking.json')
    parking = json.loads((ROOT/parking_path).read_text())
    sources = {str(parking_path): hashlib.sha256((ROOT/parking_path).read_bytes()).hexdigest()}
    rows = []
    for run in ('L43_A1_SV','L44_A3','SUB_BOX'):
        path = Path('experiments/P4_A1/runs')/run/'prereg.json'
        cfg = json.loads((ROOT/path).read_text())
        sources[str(path)] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        cases = cfg['cases']
        if run == 'SUB_BOX':
            cases = [c for c in cases if c['id'] in parking['preserved_complete_ids']]
            if len(cases) != parking['completed_keys']:
                raise ValueError('parked SUB coordinate list mismatch')
        for c in cases:
            cohort = ('SV+' if 'SV+' in c['supports'] else 'SV-') if run=='L43_A1_SV' else (
                'MV' if 'MV+A' in c['supports'] else 'SH') if run=='L44_A3' else 'SUB'
            rows.append(dict(id=c['id'],cohort=cohort,parameters=c['parameters'],
                             key='|'.join(c['key']),K=cfg['levels'][0][0],ref=cfg['levels'][0][1]))
    if len({r['key'] for r in rows}) != len(rows):
        raise ValueError('overlapping design keys; do not double count')
    return rows,sources


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        raise FileExistsError('use a new output directory')
    from experiments.P4_A1.config import verify_run
    for run in ('L43_A1_SV','L44_A3','SUB_BOX'):
        verify_run(run)
    domain = json.loads((ROOT/DOMAIN).read_text())
    anchor = domain['illustrative_projection_only']
    coords,sources = designs()
    sources[str(DOMAIN)] = hashlib.sha256((ROOT/DOMAIN).read_bytes()).hexdigest()
    rows = []
    for c in coords:
        params = c['parameters']
        row = {k:c[k] for k in ('id','cohort','key','K')}
        row.update(project(params,capacity_bps=anchor['capacity_bps'],tau_s=anchor['tau_s'],ref=c['ref']))
        rows.append(row)
    fields = ('lambdaA_over_mu','lambdaB_over_mu','u_over_mu','kappa','h_over_tau',
              'rho_A_pre','rho_B_post','background_ON_A_over_mu','background_ON_B_over_mu',
              'managed_bps','T_mode_s','h_s','bits_per_model_backlog_unit','bytes_per_model_backlog_unit')
    summary = dict(status=domain['status'],responsible=domain['responsible'],date=domain['date'],
                   coordinate_rows=len(rows),cohorts=dict(Counter(r['cohort'] for r in rows)),
                   physical_valid=sum(r['physical_valid'] for r in rows),
                   current_native_supported=sum(r['current_native_supported'] for r in rows),
                   horizon_admissible=sum(r['horizon_admissible'] for r in rows),
                   ranges={f:[min(r[f] for r in rows),max(r[f] for r in rows)] for f in fields},
                   measured_tau_s=None,empirically_validated_regimes=0,
                   empirical_status='UNRESOLVED; not zero feasible regimes and not an IN/OUT classification',
                   new_simulations=0,new_CF_or_sealed_outcomes=0,SUB_resumed=False,
                   source_sha256=sources)
    args.out.mkdir(parents=True)
    with (args.out/'illustrative_projection.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    (args.out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
