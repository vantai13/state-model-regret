"""Bước 0 — read-only diagnosis of the L4.3 and L4.4 HOLDs from COMMITTED artifacts only.

No engine import, no new plant call, no CF outcome (CF list: parameter columns only).
python -m experiments.P4_A1.diagnose        -> results/lessons/p4_a1/diagnosis/diagnosis.json (write-once)
"""
import glob
import json
import os
from fractions import Fraction as F
from pathlib import Path

from experiments.P4_03_map_audit.common import ROOT, sha, write_once

CAL = 'results/lessons/l3r_7/lean_close/calibration'
OUT = Path('results/lessons/p4_a1/diagnosis')
PAIRS = {'same_00_01': ('00', '01'), 'same_10_11': ('10', '11'),
         'cross_00_11': ('00', '11'), 'cross_01_11': ('01', '11')}
INPUTS = {}


def rd(path):
    INPUTS[str(path)] = sha(ROOT / path)
    return json.loads((ROOT / path).read_text())


def key_of(params):
    return tuple(str(F(p)) for p in params)


def pct(row, k):
    return 100 * F(row[k]) / F(row['Cref'])


def route_test(rows):
    viol = {k: 0 for k in PAIRS}; worst = {k: None for k in PAIRS}
    for r in rows:
        L = {k: F(v) for k, v in r['losses'].items()}; E = {k: F(v) for k, v in r['cost_error'].items()}
        for k, (hi, lo) in PAIRS.items():
            viol[k] += L[hi] + E[hi] < L[lo] - E[lo]
            d = 100 * (L[hi] - L[lo]) / F(r['Cref'])
            worst[k] = d if worst[k] is None else min(worst[k], d)
    return dict(rows=len(rows), violations_beyond_arithmetic_error=viol,
                most_negative_difference_pctCref={k: float(v) for k, v in worst.items()})


def main():
    files = sorted(glob.glob(str(ROOT / CAL / '*' / 'level_*.json')))
    all_rows = [rd(Path(f).relative_to(ROOT)) for f in files]
    all_rows = [r for r in all_rows if 'losses' in r]
    main_rows = {Path(f).parent.name: rd(Path(f).relative_to(ROOT))
                 for f in files if f.endswith('level_640_4.json')}
    # (1) X2000 == CAL_CORNER_001 ?
    a = main_rows['CAL_CORNER_001']; b = rd('results/lessons/l4_4/native/P44_000/level_640_4.json')
    x2000 = dict(same_parameters=a['parameters'] == b['parameters'], losses_serialized_identical=a['losses'] == b['losses'],
                 identity_scope='saved decimal cost strings; not a claim about original in-memory bits',
                 calibration_raw_validity=a['validity_errors'], L11_minus_L00_pctCref=float(pct(b, 'G_SM') * -1),
                 G_M_pctCref=float(pct(b, 'G_M')), G_M_S1_pctCref=float(pct(b, 'G_M_S1')))
    # (2) falsification test of the route diagnosis on all calibration levels
    routes = route_test(all_rows)
    # (3) raw validity at the frozen level (640,4)
    errs = [e.split(':')[1] for r in main_rows.values() for e in r['validity_errors']]
    raw = dict(cases=len(main_rows), raw_invalid=sum(bool(r['validity_errors']) for r in main_rows.values()),
               by_contrast={e: errs.count(e) for e in sorted(set(errs))},
               most_negative_cross_route_pctCref=float(min(min(pct(r, 'G_SM'), pct(r, 'G_S_M1')) for r in main_rows.values())))
    # (4) original L4.4 sanity (rho=0, cell00, arithmetic error only) on coinciding calibration rows
    by_key = {key_of(r['parameters']): r for r in main_rows.values()}
    coinc, fails = {}, {}
    for c in rd('experiments/P4_04_baseline/cases.json')['cases']:
        r = by_key.get(key_of(c['parameters']))
        if r is None:
            continue
        reg = c['regions'][0]; coinc[reg] = coinc.get(reg, 0) + 1
        if F(r['losses']['00']) + F(r['cost_error']['00']) < F(r['losses']['11']) - F(r['cost_error']['11']):
            fails[reg] = fails.get(reg, 0) + 1
    # (5) does the cross-route violation shrink with K? (honest: mostly not monotone)
    shrink, total = 0, 0
    for name, r6 in main_rows.items():
        if not r6['validity_errors']:
            continue
        r3 = rd(f'{CAL}/{name}/level_320_4.json'); total += 1
        shrink += abs(pct(r6, 'G_S_M1')) < abs(pct(r3, 'G_S_M1'))
    # (6) XM2X000 common-mode dt shift (L4.3)
    base = 'results/lessons/l4_3/resource_v2/native/P43_0000'
    L = {lv: rd(f'{base}/level_{lv}.json') for lv in ('640_4', '320_4', '640_2')}
    xm = dict(parameters=L['640_4']['parameters'],
              Cref={lv: r['Cref'] for lv, r in L.items()},
              cell_rel_change_dt_pct={k: float(100 * (F(L['640_2']['losses'][k]) / F(L['640_4']['losses'][k]) - 1)) for k in ('00', '01', '10', '11')},
              max_contrast_change_dt_pp=float(max(abs(pct(L['640_4'], m) - pct(L['640_2'], m)) for m in ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1'))),
              max_contrast_change_K_pp=float(max(abs(pct(L['640_4'], m) - pct(L['320_4'], m)) for m in ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1'))))
    # (7) Cref dt refinement inside the calibrated frame vs A-region benchmark points
    dt_cal = []
    for name, r6 in main_rows.items():
        r2 = rd(f'{CAL}/{name}/level_640_2.json'); dt_cal.append(abs(F(r6['Cref']) - F(r2['Cref'])) / F(r6['Cref']))
    a_points = {}
    for nid in ('P43_0379', 'P43_0114'):
        r6 = rd(f'results/lessons/l4_3/resource_v2/native/{nid}/level_640_4.json')
        r2 = rd(f'results/lessons/l4_3/resource_v2/native/{nid}/level_640_2.json')
        a_points[nid] = float(100 * abs(F(r6['Cref']) - F(r2['Cref'])) / F(r6['Cref']))
    # (8) CF-v2 kappa range: PARAMETER columns only
    cf = rd('results/lessons/l3r_7/lean_close/cf_generation/attempt01/regimes_cf.json')['rows']
    kappas = [F(r['regime']['kappa']) for r in cf]
    report = dict(responsible='Doan Van Tai', provenance='AI (Claude) soạn script; chạy read-only',
                  engine_calls=0, CF_outcomes=0, new_coordinates=0,
                  X2000_vs_CAL_CORNER_001=x2000, route_falsification_all_calibration_levels=routes,
                  raw_validity_at_640_4=raw,
                  original_L44_sanity_on_coinciding_points=dict(coinciding=coinc, would_fail=fails),
                  cross_route_K_convergence=dict(raw_invalid_cases=total, shrinks_320_to_640=shrink,
                                                 note='not monotone in K: source not established'),
                  XM2X000_common_mode=xm,
                  Cref_dt_delta_pct=dict(calibration_max=float(100 * max(dt_cal)), A_benchmark=a_points),
                  CF_v2_kappa_range=[float(min(kappas)), float(max(kappas))],
                  inputs_sha256=dict(sorted(INPUTS.items())))
    (ROOT / OUT).mkdir(parents=True, exist_ok=True)
    target = ROOT / OUT / 'diagnosis.json'
    if target.exists():
        if json.loads(target.read_text()) != json.loads(json.dumps(report)):
            raise RuntimeError('diagnosis differs from the committed one; never overwrite')
        print('diagnosis already recorded and reproduced exactly'); return
    write_once(target, report)
    print(json.dumps({k: report[k] for k in ('X2000_vs_CAL_CORNER_001', 'route_falsification_all_calibration_levels',
                                              'original_L44_sanity_on_coinciding_points')}, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
