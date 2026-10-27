"""Doan Van Tai — deterministic D1 selection, no plant or grid imports.

Numeric enclosures are included in the pair test. A PASS certifies the observed
finite-level differences, conditional on those bounds, never continuum error.
"""
import math

NAMES = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')


def pair_check(lo, hi):
    if hi['m'] != 2 * lo['m']:
        raise ValueError('adjacent doubling levels required')
    C = min(lo['Cref'], hi['Cref'])
    C_low = min(lo.get('Cref_low', C), hi.get('Cref_low', C))
    differences = {g: abs(hi[g] - lo[g]) for g in NAMES}
    upper = {g: differences[g] + lo.get('e_' + g, 0) + hi.get('e_' + g, 0) for g in NAMES}
    flip = any(lo[g] * hi[g] < 0 and max(abs(lo[g]), abs(hi[g])) > .005 * C for g in NAMES)
    valid = (all(math.isfinite(v) for v in (*differences.values(), *upper.values(), C_low))
             and C_low > 0 and all(x.get('precision_ok', True) for x in (lo, hi)))
    ok = valid and max(upper.values()) <= .0025 * C_low and not flip
    return dict(m_lo=lo['m'], m_hi=hi['m'], pair_pass=ok,
                max_change=max(differences.values()), max_change_upper=max(upper.values()),
                Cref_min=C, Cref_lower=C_low, tolerance=.0025 * C_low,
                relative_change=max(differences.values()) / C if C > 0 else None,
                relative_change_upper=max(upper.values()) / C_low if C_low > 0 else None,
                significant_sign_flip=flip, precision_ok=valid)


def choose_all_finer(levels):
    if [x['m'] for x in levels] != [1, 2, 4, 8, 16]:
        raise ValueError('the complete preregistered budget 1,2,4,8,16 is required')
    checks = [pair_check(a, b) for a, b in zip(levels, levels[1:])]
    for i in range(len(checks)):
        if all(x['pair_pass'] for x in checks[i:]):
            return levels[i + 1]['m']
    return 'HOLD'


def choose_final(per_cell):
    if set(per_cell) != {'M01', 'M09', 'M22'}:
        raise ValueError('exactly the three frozen calibration cells are required')
    picks = {cid: choose_all_finer(levels) for cid, levels in per_cell.items()}
    return ('HOLD' if 'HOLD' in picks.values() else max(picks.values())), picks


def diagnostics(levels):
    result = []
    for i, hi in enumerate(levels):
        for g in NAMES:
            row = dict(m=hi['m'], contrast=g, rho=None, rho_status='needs_three_levels',
                       Richardson=None)
            if i:
                row['Richardson'] = 2 * hi[g] - levels[i - 1][g]
            if i >= 2:
                before = abs(levels[i - 1][g] - levels[i - 2][g])
                after = abs(hi[g] - levels[i - 1][g])
                row['rho'] = after / before if before else None
                row['rho_status'] = 'finite' if before else 'undefined_0_over_0' if not after else 'infinite'
            result.append(row)
    return result


def main():
    import argparse
    import csv
    import json
    parser = argparse.ArgumentParser(description='Reapply the frozen A01 rule to its CSV only')
    parser.add_argument('csv_path')
    args = parser.parse_args()
    per_cell = {}
    for r in csv.DictReader(open(args.csv_path)):
        row = {k: float(v) for k, v in r.items() if k in NAMES or k.startswith('e_') or k in ('Cref', 'Cref_low')}
        row.update(m=int(r['m']), precision_ok=r['precision_ok'] == 'True')
        per_cell.setdefault(r['cell'], []).append(row)
    final, picks = choose_final(per_cell)
    print(json.dumps(dict(final_ref=final, per_cell=picks)))


if __name__ == '__main__':
    main()
