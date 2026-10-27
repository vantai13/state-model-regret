"""Doan Van Tai — score immutable A03 before opening A04 discovery columns."""
import argparse
from datetime import datetime, timezone
from pathlib import Path

from experiments.A03_card.provenance import ROOT, CARD, metadata
from experiments.A03_card.grade_card import grade_main
from experiments.A03_card.grading import get, ratio, judge, STANDS, FAILS, UNKNOWN, EXCLUDED, point_claim
from experiments.A01_null_refinement.run import write, csv_write
from experiments.A04_discovery.provenance import verify, read, validate_run_inputs


def branches(grades):
    return {'P2': grades['P2'], 'P3': grades['P3'], 'P5_K': grades['P5']['K'],
            'P5_Q': grades['P5']['Q'], 'P6': grades['P6']}


def claim_intervals(kind, r):
    C = get(r, 'C_ref')
    if kind == 'P6':
        return [('V', get(r, 'V'), '>', '0'), ('V_minus_F', get(r, 'V') - get(r, 'F'), '>', '0')]
    if C.lo <= 0:
        return [('relative_excluded_or_unresolved', None, '', '')]
    metric, iv, relation, threshold = {
        'P2': ('L01_minus_L10_over_Cref', get(r, 'L01') - get(r, 'L10'), '>=', '1/100'),
        'P3': ('Gamma_over_Cref', get(r, 'Gamma'), '>', '1/200'),
        'P5_K': ('G_M_over_Cref', get(r, 'G_M'), '<=', '1/200'),
        'P5_Q': ('G_M_over_Cref', get(r, 'G_M'), '>=', '1/100'),
    }[kind]
    return [(metric, ratio(iv, C), relation, threshold)]


def score(spec, data):
    grades = grade_main(spec, data['fine'], data['coarse'])
    summary, detail = [], []
    for kind, part in branches(grades).items():
        counts = part['counts']
        summary.append(dict(prediction=kind, verdict=part['verdict'], denominator=len(part['cells']),
                            denominator_unit='cells', **counts, mechanism='NOT_PREREGISTERED'))
        for cid, result in part['cells'].items():
            r = data['fine'][cid]
            for metric, iv, relation, threshold in claim_intervals(kind, r):
                detail.append(dict(prediction=kind, cell=cid, metric=metric,
                      lower=str(iv.lo) if iv else '', upper=str(iv.hi) if iv else '',
                      lower_decimal=float(iv.lo) if iv else '', upper_decimal=float(iv.hi) if iv else '',
                      relation=relation, threshold=threshold, verdict=result['verdict'],
                      inequality_at_final_dt=judge(iv, relation, threshold) if iv else UNKNOWN,
                      coarse_point_verdict=point_claim(kind, data['coarse'][cid]),
                      reason=result['reason'], sensitive_to_dt=result['sensitive_to_dt']))
    states = [grades['P5'][k]['verdict'] for k in ('K', 'Q')]
    summary.append(dict(prediction='P5', verdict=grades['P5']['verdict'], denominator=2,
                        denominator_unit='branches', **{v: states.count(v) for v in (STANDS, FAILS, UNKNOWN, EXCLUDED)},
                        mechanism='NOT_PREREGISTERED'))
    return grades, summary, detail


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    receipt = verify()
    out = args.run_dir.resolve()
    for name in ('card_scores.json', 'card_scores.csv', 'card_details.csv'):
        if (out / name).exists():
            raise FileExistsError('scores already exist; replay in memory instead of overwriting evidence')
    inputs = validate_run_inputs(out)
    manifest = read(out / 'manifest.json')
    if manifest['receipt_commit'] != receipt['receipt_commit']:
        raise PermissionError('run and scoring receipt differ')
    spec = metadata((ROOT / CARD).read_text())
    data = read(out / 'grading_input.json')
    expected = {f'M{i:02}' for i in range(1, 39)}
    if any(set(data[level]) != expected for level in ('fine', 'coarse')):
        raise PermissionError('grading input must contain exactly 38 main cells per level')
    grades, summary, detail = score(spec, data)
    csv_write(out / 'card_scores.csv', summary)
    csv_write(out / 'card_details.csv', detail)
    write(out / 'card_scores.json', dict(responsible='Doan Van Tai',
          scored_utc=datetime.now(timezone.utc).isoformat(), **receipt,
          input_sha256=inputs, grades=grades, discovery_started=False))
    for r in summary:
        print(f'[PREREG-CARD] {r["prediction"]}: {r["verdict"]}; n={r["denominator"]} {r["denominator_unit"]}')
    print('[PREREG-CARD] Commit score artifacts now; do not begin discovery before that checkpoint.')


if __name__ == '__main__':
    main()
