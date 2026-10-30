"""Compare every available prior K/ref result with the new registered replay.

Same quadrature/physical parameters only. Combined arithmetic enclosures test
numerical representation parity; this is not a total quadrature-error bound.
"""
import csv
from fractions import Fraction as F
import json
from pathlib import Path


def main():
    cfg = json.loads(Path('experiments/R3R_11_native_population/prereg.json').read_text())
    raw = Path(cfg['output'])
    levels = json.loads((raw / 'levels.json').read_text())
    cases = {j['id']: j for j in cfg['cases']}
    parents = [('03', Path('results/R3R_population_numerics/20261029_03'),
                'experiments/R3R_08_population_numerics/prereg_03.json'),
               ('04', Path('results/R3R_population_numerics/20261030_04'),
                'experiments/R3R_09_numerics_resume/prereg.json')]
    rows, missing = [], []
    for name, parent, prereg in parents:
        old_cfg = json.loads(Path(prereg).read_text())
        assert old_cfg['cases'] == cfg['cases']
        for path in sorted(parent.glob('*/*/level_*.json')):
            rid = path.parent.name
            before = json.loads(path.read_text())
            assert rid in cases
            key = f"{before['K']}:{before['ref']}"
            after = levels.get(rid, {}).get(key)
            if after is None:
                missing.append(dict(parent=name, id=rid, level=key))
                continue
            for metric in ('Cref', 'G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1'):
                a, b = F(before[metric]), F(after[metric])
                error = (F(before['cost_error']['11'])+F(after['cost_error']['11']) if metric == 'Cref'
                         else F(before['contrast_error'][metric])+F(after['contrast_error'][metric]))
                difference = abs(a-b)
                rows.append(dict(parent=name, id=rid, K=before['K'], ref=before['ref'],
                    metric=metric, before=str(a), after=str(b), absolute_difference=str(difference),
                    combined_arithmetic_enclosure=str(error), compatible=difference <= error))
    bad = [r for r in rows if not r['compatible']]
    out = Path('results/lessons/l3r_7/full_numerics/native05/report')
    with (out / 'prior_representation_comparison.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = dict(owner='Doan Van Tai', status='PASS' if not bad else 'FAIL',
        comparisons=len(rows), disagreements=bad, missing_new_levels=missing,
        scope='all available parent03/04 levels, including interrupted partial level files; no favorable-case selection; arithmetic representation parity only')
    with (out / 'prior_representation_comparison.json').open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('disagreements','missing_new_levels')}, indent=2))
    if bad:
        raise ArithmeticError('new evaluation differs outside combined arithmetic enclosures')


if __name__ == '__main__':
    main()
