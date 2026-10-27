"""Doan Van Tai — descriptive tables only after the score checkpoint."""
import argparse
import csv
from fractions import Fraction as F
from pathlib import Path

from experiments.A01_null_refinement.run import write, csv_write
from experiments.A03_card.grading import get, ratio, STANDS, refinement, numerical_hold
from experiments.A04_discovery.provenance import ROOT, BASE, read, require_score_commit


def cheap_kill(ids, fine, coarse, threshold=F(1, 100)):
    rows = []
    for cid in ids:
        r = fine[cid]
        C = get(r, 'C_ref')
        eligible = not numerical_hold(r) and refinement(coarse[cid], r) == STANDS and C.lo > 0
        band = ratio(get(r, 'R00'), C) if C.lo > 0 else None
        rows.append(dict(cell=cid, eligible=eligible, lower=float(band.lo) if band else None,
                         upper=float(band.hi) if band else None,
                         certified_below=bool(eligible and band.hi < threshold),
                         certified_not_below=bool(eligible and band.lo >= threshold)))
    if rows and all(r['certified_below'] for r in rows):
        status = 'NARROW_BASELINE_GAIN'
    elif any(r['certified_not_below'] for r in rows):
        status = 'NOT_CHEAP_KILLED'
    else:
        status = 'UNRESOLVED'
    return dict(status=status, n=len(rows), certified_below=sum(r['certified_below'] for r in rows),
                ineligible=[r['cell'] for r in rows if not r['eligible']], cells=rows)


def describe(out):
    out = Path(out)
    commit = require_score_commit(out)
    cfg = read(ROOT / (BASE + 'config.json'))
    data = read(out / 'grading_input.json')
    with (out / 'cells.csv').open() as handle:
        allrows = list(csv.DictReader(handle))
    fine = [r for r in allrows if r['refinement'] == '2' and r['cell'] in cfg['main_ids']]
    controls = [r for r in allrows if r['refinement'] == '2' and r['cell'] in cfg['controls']]
    csv_write(out / 'main_final.csv', fine)
    csv_write(out / 'controls_final.csv', controls)
    domains = {g: cheap_kill([r['cell'] for r in fine if r['group'] == g], data['fine'], data['coarse'])
               for g in cfg['cheap_kill_domains']}
    write(out / 'cheap_kill.json', domains)
    csv_write(out / 'cheap_kill.csv', [dict(domain=g, status=d['status'], cells=d['n'],
              certified_below=d['certified_below'], max_upper_pct=100*max(r['upper'] for r in d['cells'] if r['upper'] is not None),
              ineligible='|'.join(d['ineligible'])) for g, d in domains.items()])
    keys = ['cell', 'group', 'kappa', 'alphaA', 'alphaB', 'eta', 'h_s', 'targets', 'lambdaA', 'p_sw', 'floor',
            'status', 'pair_flag', 'G_S_sign', 'G_S', 'G_M', 'Gamma', 'G_M_S1', 'G_S_M1', 'F', 'V',
            'bias', 'abs_bias', 'abs_E_delta', 'E_abs_e_M', 'E_abs_I_delta', 'abs_delta_q50', 'abs_delta_q90',
            'abs_delta_q99', 'R04_predicted_gain', 'R04_delta_old', 'R04_delta_new', 'R04_identity_residual']
    csv_write(out / 'margin_route_diagnostics.csv', [{k: r[k] for k in keys} for r in fine])
    def x(row, key):
        return float(F(row[key]))
    summary = dict(score_commit=commit, main_cells=len(fine), controls_probes=len(controls),
                   action_flip_cells=[r['cell'] for r in fine if r['a00_nominal'] != r['a01_nominal']],
                   G_M_positive_cells=[r['cell'] for r in fine if x(r, 'G_M') > 0],
                   G_S_negative_cells=[r['cell'] for r in fine if x(r, 'G_S') < 0],
                   G_S_practical_negative_cells=[r['cell'] for r in fine if r['G_S_verdict_010'] == 'practical_negative'],
                   floor_cells=[r['cell'] for r in fine if r['floor'] == 'True'],
                   max_R04_identity_residual=max(abs(x(r, 'R04_identity_residual')) for r in fine),
                   heldout_outcomes_evaluated=False, mechanism_preregistered=False)
    for metric in ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1'):
        summary[metric] = dict(min_pct=min(x(r, metric + '_pct_Cref') for r in fine),
                              max_pct=max(x(r, metric + '_pct_Cref') for r in fine),
                              primary_point_counts={s: sum(r[metric + '_verdict_010'] == s for r in fine)
                                    for s in ('equivalent_point', 'practical_positive', 'practical_negative', 'between_thresholds')},
                              practical_positive_cells=[r['cell'] for r in fine if r[metric + '_verdict_010'] == 'practical_positive'])
    write(out / 'discovery_summary.json', summary)
    print('[DISCOVERY] Descriptive tables created; every considered pattern must be logged separately.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    describe(args.run_dir)


if __name__ == '__main__':
    main()
