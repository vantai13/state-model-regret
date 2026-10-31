"""Create runs/<RUN_ID>/prereg.json ONCE, before any plant call of that run.

Refuses unless: Bước 0 diagnosis is committed; the author file is ADOPTED_BY_AUTHOR with the
author-written fields and every author decision filled; the output folder has no plant results.
The prereg pins exact case lists, benchmark/control, caps, and SHA-256 of every source/input and of
every historical HOLD artifact that must stay byte-unchanged.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path

from experiments.P4_03_map_audit.common import ROOT, sha, require, write_once, canonical, cf_keys, forbid_cf, METRICS
from .config import PKG, RUNS, SEALED, INVENTORY, load, committed, check_author, guard_case

DIAGNOSIS = Path('results/lessons/p4_a1/diagnosis/diagnosis.json')
CONTROL = dict(id='A1_CONTROL_U0', parameters=['7', '6', '1/10', '0', '8', '0'],
               key=list(canonical(['7', '6', '1/10', '0', '8', '0'])),
               purpose='exact zero-action plant sanity; not discovery or CF')


def require_filled(value, where):
    """Every author decision, including nested ones, must be filled (no null anywhere)."""
    if isinstance(value, dict):
        for k, v in value.items():
            require_filled(v, f'{where}.{k}')
    else:
        require(value is not None, 'AUTHOR_DECISION_MISSING: ' + where)


def validate_design(design, decisions):
    K, ref = design['levels'][0]
    require(type(K) is int and type(ref) is int and K >= 2 and ref >= 2 and K % 2 == ref % 2 == 0,
            'invalid main numerical level')
    require(design['levels'] == [[K, ref], [K // 2, ref], [K, ref // 2]], 'wrong numerical neighbours')
    require(design['rho'] == ['0', '1/200', '1/100', '1/50', '1/20'], 'rho grid changed')
    for cap in decisions['caps'].values():
        require(0 <= F(cap) <= 1, 'cap must be in [0,1]')
    require(type(decisions['cpu_cap_hours']) is int and decisions['cpu_cap_hours'] > 0, 'positive integer CPU hours')
    if design['kind'] == 'L43_SV':
        require(decisions['sv_target_controller'] in ('00', '10'), 'invalid target controller')


def sort_key(case):
    return tuple(map(F, case['key']))


def cases_l44(design):
    doc = load(design['cases_source'])
    return [dict(id=c['id'], parameters=c['parameters'], key=c['key'], supports=list(c['regions']))
            for c in doc['cases']], []


def in_bounds(a, b, k, e, h, amp, bounds):
    def inside(name, value):
        lo, hi = bounds[name]
        return (lo is None or F(lo) <= value) and (hi is None or value <= F(hi))
    return (amp == F(bounds['amp']) and inside('kappa_over_age', k) and inside('h_over_age', h)
            and inside('eta', e) and inside('lambdaA', a) and inside('lambdaB', b))


def cases_l43_sv(design, choice):
    sealed = {tuple(r['coordinates']) for r in load(SEALED)['sealed']}
    doc = load(design['plus_source'])
    plus_ids = {a['native_id'] for a in doc['aliases'] if 'A' in a['zones']}
    plus = [dict(id=c['id'], parameters=c['parameters'], key=c['key'], supports=['SV+'])
            for c in doc['cases'] if c['id'] in plus_ids and tuple(c['key']) not in sealed]
    keep = {c['id'] for c in plus}
    aliases = [dict(a, supports=['SV+']) for a in doc['aliases'] if a['native_id'] in keep and 'A' in a['zones']]
    from experiments.P4_02_reading.read_map import load_table
    from experiments.P4_01_recount import recount_map as R
    bounds = choice['sv_minus_bounds']; forbidden = cf_keys(); by = {}
    plus_keys = {tuple(c['key']) for c in plus}
    for row in load_table():
        a, b, k, e, h, amp = R.scaled_key(row)
        if not in_bounds(a, b, k, e, h, amp, bounds):
            continue
        parameters = list(map(str, (a, b, k, e, h, F(0))))
        forbid_cf(parameters, forbidden)
        key = canonical(parameters)
        require(key not in plus_keys, 'SV minus overlaps SV plus: change bounds')
        if key in sealed:
            continue
        by.setdefault(key, dict(parameters=parameters, key=list(key), rows=[]))['rows'].append(row)
    minus = []
    for i, key in enumerate(sorted(by, key=lambda k: tuple(map(F, k)))):
        cid = f'A1M_{i:04d}'
        minus.append(dict(id=cid, parameters=by[key]['parameters'], key=by[key]['key'], supports=['SV-']))
        for row in by[key]['rows']:
            aliases.append(dict(id=row['id'], native_id=cid, supports=['SV-'], key=by[key]['key'],
                                pilot_class=row['class'], original_age=str(row['_key'][5]),
                                pilot_pctC={m: str(row[m + '_pctC']) for m in METRICS}))
    require(minus, 'SV minus bounds contain no exposed discovery coordinate')
    return plus + minus, aliases


def cases_sub_probe(design, choice):
    doc = load(design['plus_source'])
    sealed = {tuple(r['coordinates']) for r in load(SEALED)['sealed']}
    ab = {a['native_id'] for a in doc['aliases'] if 'AB' in a['zones']}
    pool = sorted([c for c in doc['cases'] if c['id'] in ab and F(c['parameters'][2]) == F(1, 20)
                   and tuple(c['key']) not in sealed], key=sort_key)
    n = int(choice['probe_n'])
    require(2 <= n <= len(pool), 'probe_n out of range')
    picked = [pool[round(i * (len(pool) - 1) / (n - 1))] for i in range(n)]
    ids = {c['id'] for c in picked}
    require(len(ids) == n, 'probe selection collapsed')
    cases = [dict(id=c['id'], parameters=c['parameters'], key=c['key'], supports=['SUB_PROBE']) for c in picked]
    aliases = [dict(a, supports=['SUB_PROBE']) for a in doc['aliases'] if a['native_id'] in ids and 'AB' in a['zones']]
    return cases, aliases


def main():
    p = argparse.ArgumentParser(); p.add_argument('--run', required=True); a = p.parse_args()
    folder = RUNS / a.run
    design = load(folder / 'design.json'); require(design['run_id'] == a.run, 'design run id')
    choice_path = folder / 'author_choices.json'
    choice = check_author(choice_path)
    require_filled(choice['decisions'], 'decisions')
    validate_design(design, choice['decisions'])
    for path in [DIAGNOSIS, folder / 'design.json', choice_path, folder / 'amendment.md']:
        committed(path)
    out = ROOT / design['output']
    require(not (out / 'native').exists() and not (out / 'controls').exists(), 'plant output already exists')
    if design['kind'] == 'L44':
        cases, aliases = cases_l44(design)
    elif design['kind'] == 'L43_SV':
        cases, aliases = cases_l43_sv(design, choice['decisions'])
    elif design['kind'] == 'SUB_PROBE':
        cases, aliases = cases_sub_probe(design, choice['decisions'])
    else:
        raise ValueError('unknown run kind')
    require(len({tuple(c['key']) for c in cases}) == len(cases), 'duplicate physical key')
    cfg = dict(run_id=a.run, kind=design['kind'], output=design['output'], levels=design['levels'], rho=design['rho'],
               cases=cases, aliases=aliases, audit_pilot=design['audit_pilot'], control=CONTROL)
    for c in cases:
        guard_case(c, cfg)
    guard_case(CONTROL, cfg, control=True)
    supports = {}
    for name, spec in design['supports'].items():
        spec = dict(spec)
        if spec.get('target') == 'AUTHOR':
            spec['target'] = choice['decisions']['sv_target_controller']
        supports[name] = spec
    benchmark = []
    for name in supports:
        group = sorted([c for c in cases if name in c['supports']], key=sort_key)
        require(group, 'empty support: ' + name)
        benchmark += [group[0]['id'], group[-1]['id']] if len(group) > 1 else [group[0]['id']]
    resources = dict(design['resources'], cpu_cap_hours=choice['decisions']['cpu_cap_hours'])
    sources = sorted({*map(str, (PKG / x for x in ('__init__.py', 'checks.py', 'config.py', 'evaluate.py',
                                                    'run.py', 'summarize.py', 'freeze.py', 'diagnose.py'))),
                      'tests/test_p4_a1.py', str(folder / 'design.json'), str(choice_path), str(folder / 'amendment.md'),
                      str(DIAGNOSIS), str(SEALED), str(INVENTORY), *design['input_files']})
    if choice.get('delegation_path'):
        sources.append(choice['delegation_path'])
    cfg.update(status='FROZEN_BEFORE_PLANT', responsible='Doan Van Tai', author_choices=str(choice_path),
               supports=supports, benchmark_ids=benchmark, caps=choice['decisions']['caps'],
               reading=dict(SV=choice['decisions'].get('sv_reading_rule')), resources=resources,
               CF_computed=False, card_v2_verdict_unchanged=True,
               source_sha256={s: sha(ROOT / s) for s in sources},
               preserved_history_sha256={s: sha(ROOT / s) for s in design['preserved_history']})
    for s in sources:
        committed(s)
    write_once(ROOT / folder / 'prereg.json', cfg)
    print(json.dumps(dict(run=a.run, cases=len(cases), aliases=len(aliases),
                          per_support={n: sum(n in c['supports'] for c in cases) for n in supports},
                          benchmark=benchmark), indent=1), flush=True)


if __name__ == '__main__':
    main()
