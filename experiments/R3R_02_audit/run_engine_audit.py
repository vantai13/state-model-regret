"""Doan Van Tai — declared T2/T3/T6, refinements and timing on seen regimes."""
import argparse
import json
import platform
import time
from fractions import Fraction as F
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from smr.cells import law_for, queue_D
from smr.stationary import r2_keep
from experiments.A00_engine.factorial_core import Side
from experiments.A00_engine.evaluate import evaluate_sides
from experiments.R3R_02_audit import bridge as B
from experiments.R3R_02_audit import pilot_population as P


def forward(mass, inc, keep, steps):
    size = len(mass) + steps * max(0, *inc)
    out = np.zeros((size, 2), dtype=np.longdouble)
    out[:len(mass)] = mass
    p = np.longdouble(keep.numerator) / keep.denominator
    for _ in range(steps):
        after = np.zeros_like(out)
        for m, delta in enumerate(inc):
            idx = np.maximum(0, np.arange(size) + delta)
            good = idx < size
            for mm in (0, 1):
                np.add.at(after[:, mm], idx[good], out[good, m] * (p if m == mm else 1 - p))
        out = after
    return out


def posterior_prior(cell, which, ref):
    rates = cell['rates' + which]
    u = cell['u'] if which == 'A' else F(0)
    unit, law = law_for(sum(rates) / 2, u, cell['kappa'], ref)
    cap = law.quantile(F(9999999999, 10000000000))
    prior = law.mass(cap)
    removed = max(0., float(1 - prior.sum()))
    evolved = forward(prior, law.increments, law.keep, 120 * ref)
    reference = np.zeros_like(evolved)
    reference[:len(prior)] = prior
    tv = float(abs(evolved - reference).sum() / 2)
    points = sorted({0, *[law.quantile(F(k, 10)) for k in (2, 4, 6, 8)]})
    mode_errors = []
    mass = law.mass(max(points))
    for q in points:
        _, posterior, _, _ = queue_D(dict(cell, **{'y' + which: q * unit}), which, ref)
        # Independently propagate a point initialized by stationary joint row.
        start = np.zeros((q + 1, 2), dtype=np.longdouble)
        start[q] = mass[q] / mass[q].sum()
        expected = forward(start, law.increments, law.keep, 120 * ref)
        n = max(len(expected), len(posterior))
        a, b = np.zeros((n, 2), dtype=np.longdouble), np.zeros((n, 2), dtype=np.longdouble)
        a[:len(expected)] = expected; b[:len(posterior)] = posterior
        mode_errors.append(float(abs(a - b).sum() / 2))
    return {'TV_retained_prior_after_age': tv, 'removed_probability': removed,
            'TV_tolerance': removed + 1e-12,
            'full_retained_support_via_linearity': True,
            'actual_queue_D_point_checks': len(points), 'max_queue_D_point_TV': max(mode_errors),
            'point_q_indices': points, 'cutoff': cap, 'unit': str(unit),
            'status': 'PASS' if tv <= removed + 1e-12 and max(mode_errors) <= 1e-12 else 'FAIL'}


def compare_snapshot(s, data):
    ia = min(2, len(data['A']['reps']) - 1)
    ib = min(3, len(data['B']['reps']) - 1)
    sides = []
    for w, index in [('A', ia), ('B', ib)]:
        obj, cell = data[w], data['cell']
        y = obj['reps'][index] * obj['unit']
        _, mass, _, err = queue_D(dict(cell, **{'y' + w: y}), w, int(s[6]))
        keep, ke = r2_keep(F(1, 120 * int(s[6])), cell['kappa'])
        from experiments.A00_engine.physical import side_from_law
        table, _ = side_from_law(obj['unit'], mass, rates=cell['rates' + w],
                                u_stay=cell['u'] if w == 'A' else F(0),
                                u_switch=cell['u'] if w == 'B' else F(0), capacity=F(10),
                                H=cell['H_coarse'] * int(s[6]), dt=F(1, 120 * int(s[6])),
                                keep=keep, keep_error=ke, D_error=err)
        if w == 'A' and F(s[8]):
            c = np.longdouble(float(F(s[8])))
            table = Side(table.p, tuple(v + c for v in table.d), tuple(v + c for v in table.dh),
                         table.jst, table.group)
        sides.append(table)
    old = evaluate_sides(*sides, refinement=int(s[6]), dt=F(1, 120 * int(s[6])))
    pop = P.pair_values(data['A']['side'], data['B']['side'], ia, ib, F(s[8]))
    differences = {k: float(abs(pop['L'][k] - old['L'][k])) for k in ('00', '01', '10', '11')}
    scale = max(1., float(abs(old['L']['11'])))
    actions_match = all(int(pop[k]) == old['nominal_actions'][cell]
                        for k, cell in [('a00', '00'), ('a01', '01')])
    return dict(differences=differences, max_relative=max(differences.values()) / scale,
                actions_match=actions_match, yA_index=data['A']['reps'][ia], yB_index=data['B']['reps'][ib],
                status='PASS' if actions_match and max(differences.values()) <= 1e-12 * scale else 'FAIL')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rid'); ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        ap.error('preserve existing output')
    args.out.mkdir(parents=True)
    start = time.monotonic()
    record = {'id': args.rid, 'levels': [], 'status': 'RUNNING'}
    def save():
        (args.out / 'audit.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    save()
    for ref, K in [(1, 40), (1, 80), (1, 160), (2, 40), (2, 20)]:
        s = B.spec(args.rid, ref, K)
        out, pairs = P.evaluate(s)
        # Preserve every reported scalar, not only favourable contrasts.
        record['levels'].append(out)
        save()
    s = B.spec(args.rid)
    cell = B.cell_for(s)
    record['posterior_prior'] = {w: posterior_prior(cell, w, 1) for w in ('A', 'B')}
    save()
    atom = []
    for w in ('A', 'B'):
        pre = cell['u'] if w == 'A' else F(0)
        lam = sum(cell['rates' + w]) / 2 + pre
        expected = float((10 - lam) / (16 - lam))
        vals = []
        for ref in (1, 2):
            _, law = law_for(lam - pre, pre, cell['kappa'], ref)
            actual = float(law.mass(0).sum())
            vals.append({'ref': ref, 'actual': actual, 'abs_error': abs(actual - expected)})
        status = 'PASS' if vals[0]['abs_error'] <= .01 and vals[1]['abs_error'] <= vals[0]['abs_error'] + 1e-12 else 'UNRESOLVED'
        atom.append(dict(side=w, fluid_atom=expected, slotted=vals, status=status))
    record['atoms'] = atom
    save()
    direct = {}
    da, ba = B.direct_stationary_tables(cell, 'A', 1)
    db, bb = B.direct_stationary_tables(cell, 'B', 1)
    # Need only S1 costs: avoid pilot's O(nA*nB) wrong-ranking diagnostic on full priors.
    pa, pb = da['w'][0], db['w'][0]
    c = np.longdouble(float(F(s[8])))
    j = (pa * da['j']).sum() + (pb * db['j']).sum()
    directL = {'10': j + P.cut_value(da['dh'] + c, da['d'] + c, pa, db['dh'], db['d'], pb),
               '11': j + P.cut_value(da['d'] + c, da['d'] + c, pa, db['d'], db['d'], pb)}
    direct.update(L10=float(directL['10']), L11=float(directL['11']), tail_A=ba, tail_B=bb)
    record['direct_stationary_S1'] = direct
    # Reconstruct four quadrature costs from the recorded Cbar and contrasts.
    quad = []
    for r in record['levels'][:3]:
        C = r['Cbar']
        q10 = C + r['G_M_S1']
        quad.append(dict(K=r['K'], error_L10_ppC=100 * abs(q10 - direct['L10']) / direct['L11'],
                         error_L11_ppC=100 * abs(C - direct['L11']) / direct['L11']))
    record['S1_quadrature_errors'] = quad
    record['T2b_status'] = 'PASS' if max(quad[-1]['error_L10_ppC'], quad[-1]['error_L11_ppC']) <= .25 and all(
        quad[i + 1][key] <= quad[i][key] + 1e-10 for i in range(2) for key in ('error_L10_ppC', 'error_L11_ppC')) else 'UNRESOLVED'
    save()
    data = B.instrument(s)
    L = B.population_from_tables(data['A']['side'], data['B']['side'], data['A']['weights'], data['B']['weights'], F(s[8]))
    record['population_layer_parity_abs'] = max(abs(float(L['11']) - record['levels'][0]['Cbar']),
                                               *[abs(float(B.P.contrasts(L)[k]) - record['levels'][0][k]) for k in B.GKEYS])
    # LD accumulation differs by normal float order only; same declared 1e-12 relative check.
    record['snapshot_v12'] = compare_snapshot(s, data)
    record['wall_s'] = time.monotonic() - start
    record['status'] = 'PASS' if record['snapshot_v12']['status'] == 'PASS' and all(
        v['status'] == 'PASS' for v in record['posterior_prior'].values()) else 'FAIL'
    record['scope'] = 'core code checks; numerical unresolved statuses remain separately visible'
    save()
    print(json.dumps({'id': args.rid, 'status': record['status'], 'T2b': record['T2b_status'], 'wall_s': record['wall_s']}))


if __name__ == '__main__':
    main()
