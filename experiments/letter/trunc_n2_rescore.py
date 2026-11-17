"""Doan Van Tai: independent arithmetic replay, without importing trunc_n2.

Run only after the raw commit and the primary/platform comparisons exist.
The schema below follows the card and the saved W1b field definitions.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


THRESHOLDS = {'percentage_pp': 1e-6, 'relative': 1e-9, 'discrete': 0}
PERCENT = {'G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M', 'G_S_hybrid',
           'G_S_hybrid_mm1', 'G_S_ko', 'z_inf', 'z_inf_ko',
           'M0_regret_new_pred', 'M0_regret_old_pred',
           'z_pred_first_order_inf_decisions', 'z_pred_first_order_ko'}


def leaves(value, path=()):
    if isinstance(value, dict) and value:
        for key in sorted(value):
            yield from leaves(value[key], path + (key,))
    elif isinstance(value, list) and value:
        for i, child in enumerate(value):
            yield from leaves(child, path + (i,))
    else:
        yield path, value


def ignored(path):
    for part in path:
        if isinstance(part, str):
            key = part.lower()
            if part == 'N' or key in {'cpu', 'wall', 'time', 'sha', 'sha256'}:
                return True
            if key.startswith(('cpu_', 'wall_', 'time_')) or key.endswith(('_sha256', '_sha', '_timestamp')):
                return True
    return False


def category(path, value):
    keys = [p for p in path if isinstance(p, str)]
    last = keys[-1]
    if isinstance(value, bool):
        return 'discrete'
    if (last in {'count', 'n_samples', 'decision', 'action', 'tie', 'tie_flag'}
            or last.endswith(('_count', '_counts', '_decision', '_action', '_flag'))
            or 'margin_best' in keys):
        return 'discrete'
    if (last in PERCENT or 'regret' in keys
            or 'hybrid_levels' in keys and last in {'regret_new', 'regret_old'}
            or 'margin' in keys and last in {'new', 'old'}):
        return 'percentage_pp'
    if 'shares' in keys and last in {'static', 'const'}:
        return 'discrete'
    if any(k in keys for k in ('shares', 'tie_mass', 'dep_static')):
        return 'relative'
    if 'parameters' in keys:
        return 'discrete'  # serialized case definitions, checked for exact identity
    if isinstance(value, (int, float)):
        return 'relative'
    try:
        Fraction(value) if isinstance(value, str) else (_ for _ in ()).throw(ValueError())
        return 'relative'
    except (ValueError, ZeroDivisionError):
        return 'discrete'


def number(value):
    return float(Fraction(value)) if isinstance(value, str) else float(value)


def metric(value):
    return 'infinity' if math.isinf(value) else value


def replay(root, comparison_path):
    report = json.loads(comparison_path.read_text())
    if report['thresholds'] != THRESHOLDS or report['compared_regimes'] != 27:
        raise AssertionError('thresholds/population differ')
    info = report['comparison']
    left_root = Path(info['baseline'])
    right_root = Path(info['candidate'])
    left_root = left_root if left_root.is_absolute() else root / left_root
    right_root = right_root if right_root.is_absolute() else root / right_root
    left_raw = left_root / 'raw' if info['same_platform'] else left_root
    right_raw = right_root / 'raw'
    summaries = {g: dict(count=0, maximum=0., maximum_absolute=0., violations=0,
                         fields=set()) for g in THRESHOLDS}
    detail = []
    for rid, hashes in info['input_sha256'].items():
        old_path, new_path = left_raw / (rid + '.json'), right_raw / (rid + '.json')
        for path, key in ((old_path, 'baseline_sha256'), (new_path, 'candidate_sha256')):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == hashes[key]
        a, b = (json.loads(p.read_text()) for p in (old_path, new_path))
        assert a['case'] == b['case'] and a['levels'] == b['levels']
        old, new = (dict(leaves(v['evaluations'])) for v in (a, b))
        assert old.keys() == new.keys()
        for ev1, ev2 in zip(a['evaluations'], b['evaluations']):
            assert ev2['N'] == {s: n * info['candidate_n_scale'] for s, n in ev1['N'].items()}
            assert all(ev2['chains'][k]['N'] == n['N'] * info['candidate_n_scale']
                       for k, n in ev1['chains'].items())
        for path in sorted(old, key=str):
            if ignored(path):
                continue
            v, w = old[path], new[path]
            group = category(path, v)
            field = ''.join('[]' if isinstance(p, int) else ('.' if j else '') + p
                            for j, p in enumerate(path))
            if group == 'discrete':
                absolute = delta = int(type(v) is not type(w) or v != w)
            else:
                x, y = number(v), number(w)
                absolute = abs(y-x)
                delta = (absolute if group == 'percentage_pp' else
                         absolute / abs(x) if x else 0. if y == 0 else math.inf)
            out = summaries[group]
            out['count'] += 1
            out['fields'].add(field)
            out['maximum'] = max(out['maximum'], delta)
            out['maximum_absolute'] = max(out['maximum_absolute'], absolute)
            if delta > THRESHOLDS[group]:
                out['violations'] += 1
                ev = a['evaluations'][path[0]]
                detail.append(dict(regime=rid, age=ev['age_label'], field=field,
                    group=group, baseline=v, candidate=w, difference=metric(delta),
                    absolute_difference=absolute))
    for group, values in summaries.items():
        actual = report['groups'][group]
        assert actual['count'] == values['count'], (group, 'count')
        assert actual['max_difference'] == metric(values['maximum']), (group, 'maximum')
        assert actual['max_absolute_difference'] == values['maximum_absolute'], (group, 'absolute')
        assert actual['fields'] == sorted(values['fields']), (group, 'schema')
        assert actual['passed'] == (values['violations'] == 0), (group, 'verdict')
        assert sum(v['group'] == group for v in report['violations']) == values['violations']
        values['fields'] = sorted(values['fields'])
        values['maximum'] = metric(values['maximum'])
    assert not any(report[k] for k in ('missing_regimes', 'extra_regimes', 'missing_fields', 'extra_fields'))
    expected = 'FAIL' if detail else 'PASS'
    assert report['status'] == expected
    return dict(comparison=str(comparison_path.relative_to(root)), matched=True,
                comparison_sha256=hashlib.sha256(comparison_path.read_bytes()).hexdigest(),
                regimes=27, status=expected, groups=summaries,
                violations_replayed=len(detail))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    out = args.root / 'results/letter/trunc_n2'
    results = [replay(args.root, p) for p in (out/'compare.json', out/'platform_noise/compare.json')]
    result = dict(owner='Doan Van Tai', imports_primary_scorer=False, matched=True, comparisons=results)
    with (out/'independent_rescore.json').open('x') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps(dict(matched=True, comparisons=len(results))))


if __name__ == '__main__':
    main()
