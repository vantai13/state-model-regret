"""Doan Van Tai — independent saved-row rescore and descriptive tables, S1-C rolling.

Does not import analyze_rolling and does not simulate decision costs. All writers
use exclusive creation. Cross-case statistics give every available case one vote.
"""
import csv
import hashlib
import itertools
import json
import math
import statistics as stat
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
FULL = HERE.parent / 'full'
TAGS = tuple(f'{e}_{w}' for w in ('60', '300', 'all') for e in ('sim', 'mm1'))
METHODS = ('M0', 'static', 'hybrid') + tuple(f'{kind}_{tag}' for tag in TAGS for kind in ('static', 'hybrid'))
MARGIN = .05  # percentage points, as specified in the brief


def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    with (HERE / name).open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(name, obj):
    with (HERE / name).open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')


def sign(x):
    return (x > 0) - (x < 0)


def close(a, b):
    if not math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-9):
        raise AssertionError((a, b))


def independent_groups(plan):
    groups = {}
    for case in plan['cases']:
        path = FULL / case['id'] / 'decisions.csv'
        if not path.exists():
            groups[case['id']] = dict(group='NOT_EVALUABLE')
            continue
        rows = read_csv(path)
        hm = max(float(r['h_mult']) for r in rows)
        use = [r for r in rows if float(r['h_mult']) == hm and float(r['tau_s']) == 0.]
        stest = stat.mean((float(r['cost_switch']) - float(r['cost_stay'])) / float(r['h_s']) for r in use)
        train = json.loads((path.parent / 'training.json').read_text())['s_hat']
        groups[case['id']] = dict(group='OK' if sign(train) == sign(stest) else 'FLIP',
                                  s_test_case=stest, s_train=train, group_h_mult=hm, group_n=len(use))
    return groups


def audit_rows(plan, groups, windows):
    cells = defaultdict(lambda: defaultdict(float))
    checked = 0
    with (HERE / 'rows_rolling.csv').open(newline='') as f:
        new = iter(csv.DictReader(f))
        for case in plan['cases']:
            path = FULL / case['id'] / 'decisions.csv'
            if not path.exists():
                continue
            with path.open(newline='') as original:
                for old in csv.DictReader(original):
                    r = next(new)
                    assert r['case_id'] == old['case_id']
                    for key in ('trace', 'point', 'alarm', 'block'):
                        assert r[key] == old[key], (key, r[key], old[key])
                    for key in ('t_test_s', 'h_s', 'h_mult', 'tau_s', 'fluid_gap', 'cost_stay',
                                'cost_switch', 'C_ref', 'regret_M0', 'regret_static', 'regret_hybrid'):
                        assert float(r[key]) == float(old[key]), key
                    expected_group = groups[case['id']]
                    assert r['group'] == expected_group['group']
                    close(r['s_test_case'], expected_group['s_test_case'])
                    e, h, gap = float(old['t_test_s']) - float(old['tau_s']), float(old['h_s']), float(old['fluid_gap'])
                    assert float(r['e_s']) == e
                    costs = [float(old['cost_stay']), float(old['cost_switch'])]
                    cref = float(old['C_ref'])
                    assert cref == min(costs)
                    measures = dict(C_ref=cref, n=1.)
                    local = (costs[1] - costs[0]) / h
                    assert float(r['s_test_local']) == local
                    measures['dis_original'] = old['disagreement'] == 'True'
                    measures['sign_ok_original'] = sign(expected_group['s_train']) == sign(expected_group['s_test_case'])
                    measures['sign_local_ok_original'] = sign(expected_group['s_train']) == sign(local)
                    for kind, action in (('M0', 'action_M0'), ('static', 'action_static'), ('hybrid', 'action_hybrid')):
                        value = costs[int(old[action])] - cref
                        assert float(r[f'regret_{kind}']) == value
                        measures['regret_' + kind] = value
                    for tag in TAGS:
                        s = float(r['shat_' + tag])
                        assert not math.isnan(s)
                        est, w = tag.split('_')
                        past = windows[(case['id'], w, e)]
                        assert s == past[est]
                        assert (r['flag_' + tag] == 'True') == (past['flag'] if est == 'mm1' else False)
                        ast, ah = int(s < 0), int(gap + h*s < 0)
                        for kind, action in (('static', ast), ('hybrid', ah)):
                            value = costs[action] - cref
                            assert float(r[f'regret_{kind}_{tag}']) == value
                            assert value >= 0.
                            measures[f'regret_{kind}_{tag}'] = value
                        assert (r['dis_' + tag] == 'True') == (ast != ah)
                        measures['dis_' + tag] = ast != ah
                        measures['sign_ok_' + tag] = sign(s) == sign(expected_group['s_test_case'])
                        measures['sign_local_ok_' + tag] = sign(s) == sign(local)
                        measures['flag_' + tag] = r['flag_' + tag] == 'True'
                    for pop in ('uniform', 'alarm') if old['alarm'] == 'True' else ('uniform',):
                        cell = cells[(case['id'], float(old['h_mult']), float(old['tau_s']), pop)]
                        for key, value in measures.items():
                            cell[key] += value
                    checked += 1
        assert next(new, None) is None
    return checked, cells


def audit_summary(cells, summary):
    checked = 0
    for r in summary:
        key = (r['case_id'], float(r['h_mult']), float(r['tau_s']), r['population'])
        if r['status'] != 'AVAILABLE':
            assert key not in cells and int(r['n']) == 0
            continue
        x = cells[key]
        n, cref = x['n'], x['C_ref']
        assert int(r['n']) == n
        close(r['mean_Cref'], cref/n)
        for method in METHODS:
            close(r['pct_' + method], 100*x['regret_' + method]/cref)
        for tag in ('original',) + TAGS:
            for prefix in ('dis_', 'sign_ok_', 'sign_local_ok_'):
                close(r[prefix + tag], x[prefix + tag]/n)
            if tag != 'original':
                close(r['flag_' + tag], x['flag_' + tag])
        checked += 1
    assert checked == len(cells)
    # Independently check the original summary, including missing support.
    original = {(r['case_id'], float(r['h_mult']), float(r['tau_s']), r['population']): r
                for r in read_csv(FULL / 'summary.csv')}
    for r in summary:
        key = (r['case_id'], float(r['h_mult']), float(r['tau_s']), r['population'])
        old = original[key]
        assert int(old['n']) == int(r['n'])
        if r['status'] == 'AVAILABLE':
            for kind in ('M0', 'static', 'hybrid'):
                close(r['pct_' + kind], 100*float(old['mean_regret_' + kind])/float(old['mean_Cref']))
    return checked


def window_audit(plan):
    counts = Counter()
    unique = set()
    cases = {r['id']: r for r in plan['cases']}
    windows = {}
    for r in read_csv(HERE / 'windows_rolling.csv'):
        key = (r['case_id'], r['window'], float(r['end_s']))
        assert key not in unique
        unique.add(key)
        e, start, span = float(r['end_s']), float(r['start_s']), float(r['span_s'])
        expected_start = 0. if r['window'] == 'all' else max(0., e - float(r['window']))
        assert start == expected_start and span == e-start and 0 <= start < e
        rates = [int(r['bg0_count']) / span, int(r['bg1_count']) / span]
        assert rates == [float(r['rate0']), float(r['rate1'])]
        c = cases[r['case_id']]
        def queue_mean(lam, mu):
            return lam / (mu-lam) if lam < mu else math.inf
        a, b = rates
        m0, m1 = c['mu']
        u = c['u']
        stay = queue_mean(a+u, m0) + queue_mean(b, m1)
        switch = queue_mean(a, m0) + queue_mean(b+u, m1)
        if math.isinf(stay) and math.isinf(switch):
            # Algebraically cancel shared overload before taking its sign.
            d = min(u, max(0., b+u-m1)) - min(u, max(0., a+u-m0))
            expected = math.copysign(math.inf, d) if d else 0.
            status = 'BOTH_UNSTABLE_SIGN_PROXY'
        else:
            expected = switch - stay
            status = 'ONE_UNSTABLE' if math.isinf(stay) or math.isinf(switch) else 'STABLE'
        close(r['mm1'], expected)
        assert r['mm1_status'] == status
        assert (r['flag_mm1'] == 'True') == (status != 'STABLE')
        assert math.isfinite(float(r['sim']))
        windows[key] = dict(sim=float(r['sim']), mm1=float(r['mm1']), flag=status != 'STABLE')
        counts[(r['window'], r['mm1_status'])] += 1
    table = [dict(window=w, status=s, windows=n) for (w, s), n in sorted(counts.items())]
    write_csv('window_flag_counts.csv', table)
    return len(unique), table, windows


def mean_median(values):
    return dict(mean=stat.mean(values), median=stat.median(values))


def aggregate(cells, groups):
    # Factor-complete tables, plus the headline with each case's largest h.
    buckets = defaultdict(list)
    for r in cells:
        if r['status'] != 'AVAILABLE':
            continue
        for group, trace in itertools.product(('ALL', r['group']), ('ALL', r['trace'])):
            buckets[(group, trace, r['h_mult'], r['tau_s'], r['population'])].append(r)
            if float(r['h_mult']) == groups[r['case_id']]['group_h_mult']:
                buckets[(group, trace, 'MAX_AVAILABLE', r['tau_s'], r['population'])].append(r)
    aggregates, comparisons, diagnostics = [], [], []
    for (group, trace, hm, tau, pop), rows in sorted(buckets.items()):
        base = dict(group=group, trace=trace, h_mult=hm, tau_s=tau, population=pop,
                    n_cases=len(rows), n_decisions=sum(int(r['n']) for r in rows))
        for method in METHODS:
            values = [float(r['pct_' + method]) for r in rows]
            aggregates.append(dict(**base, method=method, mean_pct=stat.mean(values), median_pct=stat.median(values)))
        for tag in ('original',) + TAGS:
            diagnostics.append(dict(**base, estimator=tag,
                mean_sign_ok=stat.mean(float(r['sign_ok_' + tag]) for r in rows),
                median_sign_ok=stat.median(float(r['sign_ok_' + tag]) for r in rows),
                mean_sign_local_ok=stat.mean(float(r['sign_local_ok_' + tag]) for r in rows),
                mean_disagreement=stat.mean(float(r['dis_' + tag]) for r in rows),
                row_weighted_disagreement=sum(float(r['dis_' + tag])*int(r['n']) for r in rows)/base['n_decisions']))
        for tag, kind in itertools.product(TAGS, ('static', 'hybrid')):
            for reference in (kind, 'M0'):
                changes = [float(r[f'pct_{kind}_{tag}']) - float(r['pct_' + reference]) for r in rows]
                comparisons.append(dict(**base, method=kind+'_'+tag, reference=reference, margin_pp=MARGIN,
                    better=sum(x < -MARGIN for x in changes), worse=sum(x > MARGIN for x in changes),
                    within_margin=sum(-MARGIN <= x <= MARGIN for x in changes),
                    mean_change_pp=stat.mean(changes), median_change_pp=stat.median(changes)))
    write_csv('aggregate_rolling.csv', aggregates)
    write_csv('comparisons_rolling.csv', comparisons)
    write_csv('diagnostics_rolling.csv', diagnostics)
    return aggregates, comparisons, diagnostics


def main():
    plan = json.loads((HERE.parent / 'design_ready' / 'plan.json').read_text())
    before = json.loads((HERE / 'audit_before.json').read_text())
    for path, expected in before['protected_sha256'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
    manifest = json.loads((HERE / 'variant_manifest_before_analysis.json').read_text())
    for name, expected in manifest.items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    groups = independent_groups(plan)
    for saved in read_csv(HERE / 'case_groups.csv'):
        expected = groups[saved['case_id']]
        assert saved['group'] == expected['group']
        if saved['group'] != 'NOT_EVALUABLE':
            for key in ('s_train', 's_test_case', 'group_h_mult', 'group_n'):
                close(saved[key], expected[key])
    window_n, flags, windows = window_audit(plan)
    checked, cells = audit_rows(plan, groups, windows)
    summary = read_csv(HERE / 'summary_rolling.csv')
    checked_cells = audit_summary(cells, summary)
    aggregates, comparisons, diagnostics = aggregate(summary, groups)
    result = dict(status='PASS', independent_imports='stdlib only, no scoring module',
        protected_hashes=len(before['protected_sha256']), output_source_hashes=len(manifest),
        checked_rows=checked, checked_available_cells=checked_cells, total_support_cells=len(summary),
        group_counts=dict(Counter(r['group'] for r in groups.values())), window_n=window_n,
        window_flags=flags, aggregate_rows=len(aggregates), comparison_rows=len(comparisons),
        diagnostic_rows=len(diagnostics), margin_pp=MARGIN,
        comparison_rule='better iff change < -0.05 pp, worse iff > +0.05 pp, otherwise within margin',
        scope='Saved costs/actions/flags, all summary fields, group definitions and immutable hashes. No new decision simulation.')
    write_json('independent_rescore.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
