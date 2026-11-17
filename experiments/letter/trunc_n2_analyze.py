"""Saved-data diagnosis of the locked comparison. Owner: Doan Van Tai.

This does not evaluate a model, change a field class, or alter a verdict.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/trunc_n2'


def read(path):
    return json.loads(path.read_text())


def analyze(name):
    comparison = OUT / name
    report = read(comparison)
    fields = defaultdict(list)
    for row in report['violations']:
        fields[(row['group'], row['field'])].append(row)
    by_field = []
    for (group, field), rows in sorted(fields.items()):
        largest = max(rows, key=lambda r: r['absolute_difference'])
        by_field.append(dict(group=group, field=field, violations=len(rows),
            regimes=len({r['regime'] for r in rows}),
            max_absolute_difference=largest['absolute_difference'],
            max_relative_difference=max(float(r['difference']) for r in rows)
                if group == 'relative' else None,
            absolute_argmax=largest))
    relative = [r for r in report['violations'] if r['group'] == 'relative']
    discrete = [r for r in report['violations'] if r['group'] == 'discrete']
    margin_changes = []
    baseline = ROOT / report['comparison']['baseline']
    candidate = ROOT / report['comparison']['candidate']
    for row in discrete:
        if row['field'] != '[].h[].margin_best.old':
            raise ValueError('unexpected discrete change')
        record = dict(row)
        for label, folder in [('one', baseline), ('two', candidate)]:
            raw = read(folder / 'raw' / (row['regime'] + '.json'))
            age = next(e for e in raw['evaluations'] if e['age_label'] == row['age'])
            h = next(h for h in age['h'] if h['h'] == row['h'])
            old = h['margin'][row['baseline']]['old']
            new = h['margin'][row['candidate']]['old']
            record[label] = dict(old_choice_regret_pp=old, new_choice_regret_pp=new,
                choice_regret_difference_pp=abs(old-new), Cref=h['Cref'])
        margin_changes.append(record)
    groups = Counter()
    absolute = defaultdict(float)
    for row in relative:
        field = row['field']
        kind = ('residual' if field.endswith('.residual') else
                'bias' if field.endswith('.B_ko') else
                'excess_cost' if 'excess_cost' in field else 'probability')
        groups[kind] += 1
        absolute[kind] = max(absolute[kind], row['absolute_difference'])
    return dict(comparison=name, comparison_sha256=hashlib.sha256(comparison.read_bytes()).hexdigest(),
        status=report['status'], violations=len(report['violations']),
        relative_violation_count=len(relative),
        zero_reference_relative_violations=sum(float(r['baseline']) == 0 for r in relative),
        relative_max_absolute=max((r['absolute_difference'] for r in relative), default=0.),
        relative_failure_types={k:dict(count=v,max_absolute=absolute[k]) for k,v in groups.items()},
        by_field=by_field, margin_changes=margin_changes,
        max_margin_choice_gap_pp=max((r[s]['choice_regret_difference_pp']
            for r in margin_changes for s in ('one','two')), default=0.))


def main():
    result = dict(owner='Doan Van Tai', scope='POST-HOC, saved raw only; no reclassification',
        comparisons=[analyze(name) for name in ('compare.json','platform_noise/compare.json')])
    for value in result['comparisons']:
        for row in value['by_field']:
            if row['max_relative_difference'] == float('inf'):
                row['max_relative_difference'] = 'infinity'
    (OUT/'analysis_saved.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (OUT/'analysis_by_field.csv').open('w') as f:
        columns = ['comparison','group','field','violations','regimes',
                   'max_absolute_difference','max_relative_difference']
        writer = csv.DictWriter(f,columns,lineterminator='\n')
        writer.writeheader()
        for value in result['comparisons']:
            for row in value['by_field']:
                writer.writerow(dict(comparison=value['comparison'],
                    **{k:row[k] for k in columns[1:]}))
    print(json.dumps({r['comparison']:dict(relative=r['relative_failure_types'],
        max_margin_choice_gap_pp=r['max_margin_choice_gap_pp']) for r in result['comparisons']}))


if __name__ == '__main__':
    main()
