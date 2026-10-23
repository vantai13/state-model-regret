"""DISCOVERY analysis for notes/explore/reformulate_grid_plan.md (Claude (AI) for Doan Van Tai).

Reads only sign-interval rows from reformulate_grid.py and the archived v1.1 screen/budget CSVs.
Applies the procedures P0-P4 and the anchoring rule exactly as written in the plan.
"""
import csv, json, math, itertools
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_reformulate'
BAND = (0.1, 0.9)
TARGETS = (0.3, 0.7)
WINDOW = 0.15
CAP = 2e11


def load():
    rows = [json.loads(line) for line in (OUT / 'ladder_rows.jsonl').read_text().splitlines()]
    for r in rows:
        for k in ('lambdaA', 'kappa', 'eta', 'alphaA', 'alphaB', 'u', 'psi', 'delta'):
            r[k] = F(r[k])
    return rows


def p_mid(r, ref):
    return (r[f'p_low_{ref}'] + r[f'p_high_{ref}']) / 2


def in_band(r):
    return all(r[f'p_low_{ref}'] >= BAND[0] and r[f'p_high_{ref}'] <= BAND[1] for ref in (1, 2))


def edge_distance(r):
    return min(min(r[f'p_low_{ref}'] - BAND[0], BAND[1] - r[f'p_high_{ref}']) for ref in (1, 2))


def drift(r):
    return abs(p_mid(r, 1) - p_mid(r, 2))


def by_slice(rows):
    out = {}
    for r in rows:
        if r['status'] == 'OK':
            out.setdefault(r['slice'], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: r['lambdaA'])
    return out


def anchor(curve, t):
    """Plan rule: ladder point with coarse p closest to t (tie -> smaller lambdaA);
    anchored iff p at both levels lies in [t-.15, t+.15]."""
    best = min(curve, key=lambda r: (abs(p_mid(r, 1) - t), r['lambdaA']))
    ok = all(r_ok >= t - WINDOW and r_hi <= t + WINDOW
             for r_ok, r_hi in ((best[f'p_low_{ref}'], best[f'p_high_{ref}']) for ref in (1, 2)))
    return best, ok


def crossing(curve, t):
    """Continuous lambdaA where the coarse p curve crosses t (linear between ladder points)."""
    for a, b in zip(curve, curve[1:]):
        pa, pb = p_mid(a, 1), p_mid(b, 1)
        if (pa - t) * (pb - t) <= 0 and pa != pb:
            return float(a['lambdaA']) + (t - pa) / (pb - pa) * float(b['lambdaA'] - a['lambdaA'])
    return None


def monotone_violations(curve, tol=1e-9):
    return sum(p_mid(b, 1) < p_mid(a, 1) - tol for a, b in zip(curve, curve[1:]))


def coverage(cells):
    key = lambda name: sorted({str(c[name]) for c in cells}, key=lambda s: float(F(s)) if s[0].isdigit() else 0)
    psis = [float(c['psi']) for c in cells]
    return dict(kappa=key('kappa'), alphaB=key('alphaB'), alphaA=key('alphaA'), eta=key('eta'),
                horizon=sorted({c['horizon'] for c in cells}),
                psi_range=[min(psis), max(psis)] if psis else None,
                psi_levels=len({c['psi'] for c in cells}))


def summarize(name, main, anchored_pairs=None, note=''):
    good = [c for c in main if in_band(c)]
    s = dict(procedure=name, main_cells=len(main), in_band=len(good),
             in_fraction=round(len(good) / len(main), 3) if main else None,
             min_edge_distance=round(min(map(edge_distance, good)), 3) if good else None,
             max_drift=round(max(map(drift, main)), 6) if main else None,
             over_cap_dt16=sum(c['updates_16'] > CAP for c in main),
             over_cap_dt8=sum(c['updates_8'] > CAP for c in main),
             max_updates_dt16=max(c['updates_16'] for c in main) if main else None,
             coverage_in=coverage(good), note=note)
    if anchored_pairs is not None:
        s['anchor_attempts'] = len(anchored_pairs)
        s['anchored'] = sum(ok for _, ok in anchored_pairs)
    return s


def p0():
    comp = {r['cell']: r for r in csv.DictReader(open(ROOT / 'results/lessons/v1_1_a6/screen_comparison.csv'))}
    budget = {}
    for r in csv.DictReader(open(ROOT / 'results/lessons/v1_1_a2_redesign/budget.csv')):
        budget.setdefault(r['cell'], {})[r['refinement']] = int(r['scalar_updates'])
    cells = json.loads((ROOT / 'results/lessons/v1_1_a5/selection.json').read_text())['cells']
    main = [c for c in cells if c['role'] == 'main']
    good = [c for c in main if comp[c['id']]['redesign_class'] == 'in']
    psis = sorted({(F(c['lambdaA']) - 8) / 10 for c in good})
    return dict(procedure='P0 v1.1 redesign (archived)', main_cells=len(main), in_band=len(good),
                in_fraction=round(len(good) / len(main), 3),
                over_cap_dt16=sum(budget[c['id']]['16'] > CAP for c in main),
                over_cap_dt8=sum(budget[c['id']]['8'] > CAP for c in main),
                max_updates_dt16=max(budget[c['id']]['16'] for c in main),
                coverage_in=dict(kappa=sorted({c['kappa'] for c in good}), alphaB=sorted({c['alphaB'] for c in good}),
                                 alphaA=sorted({c['alphaA'] for c in good}), eta=sorted({c['eta'] for c in good}),
                                 r_h=sorted({c['r_h'] for c in good}), psi_levels=len(psis),
                                 psi_range=[float(psis[0]), float(psis[-1])]),
                note='from results/lessons/v1_1_a6 and v1_1_a2_redesign; not recomputed')


def main():
    rows = load()
    failures = [r for r in rows if r['status'] != 'OK']
    slices = by_slice(rows)
    meta = {s: v[0] for s, v in slices.items()}
    symmetric = lambda c: c['lambdaA'] == 8 - c['u']
    physical = lambda s: meta[s]['horizon'] != 'rh1'
    results, anchors = [p0()], []

    for name, pick in (('P1 symmetric, r_h=1', lambda s: not physical(s)),
                       ('P2 symmetric, physical h', physical)):
        main_cells = [r for s, curve in slices.items() if pick(s) for r in curve if symmetric(r)]
        results.append(summarize(name, main_cells))

    anchored_cells = {}
    for s, curve in slices.items():
        for t in TARGETS + (0.5,):
            best, ok = anchor(curve, t)
            lam_c = crossing(curve, t)
            anchors.append(dict(slice=s, target=t, kappa=str(meta[s]['kappa']), alphaA=str(meta[s]['alphaA']),
                                alphaB=str(meta[s]['alphaB']), eta=str(meta[s]['eta']), horizon=meta[s]['horizon'],
                                ladder_lambdaA=str(best['lambdaA']), p1=round(p_mid(best, 1), 4), p2=round(p_mid(best, 2), 4),
                                anchored=ok, crossing_lambdaA=None if lam_c is None else round(lam_c, 3),
                                crossing_delta=None if lam_c is None else round((lam_c + float(meta[s]['u']) - 8) / 10, 4),
                                updates_16=best['updates_16'], monotone_violations=monotone_violations(curve),
                                ladder_min=str(curve[0]['lambdaA']), ladder_max=str(curve[-1]['lambdaA']),
                                p_at_min=round(p_mid(curve[0], 1), 4), p_at_max=round(p_mid(curve[-1], 1), 4)))
            if t in TARGETS:
                anchored_cells.setdefault(s, []).append((best, ok))
    for name, pick in (('P3 anchored, r_h=1', lambda s: not physical(s)),
                       ('P4 anchored, physical h', physical)):
        pairs = [(b, ok) for s, v in anchored_cells.items() if pick(s) for b, ok in v]
        main_cells = [b for b, ok in pairs if ok]
        results.append(summarize(name, main_cells, pairs, note='main = anchored cells only; unanchored targets listed in anchors.csv'))

    # Leave-one-out interpolation at kappa=1 from kappa=.3 and 3 (log scale), per procedure family.
    w = (math.log(1) - math.log(.3)) / (math.log(3) - math.log(.3))
    loo = []
    index = {(str(m['kappa']), str(m['alphaA']), str(m['alphaB']), str(m['eta']), m['horizon']): s for s, m in meta.items()}
    for (k, a, b, e, h), s in index.items():
        if k != '1':
            continue
        lo, hi = index.get(('3/10', a, b, e, h)), index.get(('3', a, b, e, h))
        if not lo or not hi:
            continue
        for t in TARGETS:
            x0, x1 = crossing(slices[lo], t), crossing(slices[hi], t)
            if x0 is None or x1 is None:
                loo.append(dict(slice=s, target=t, horizon=h, predicted=None, result='no crossing at an end'))
                continue
            pred = x0 + w * (x1 - x0)
            curve = slices[s]
            point = min(curve, key=lambda r: (abs(float(r['lambdaA']) - pred), r['lambdaA']))
            loo.append(dict(slice=s, target=t, horizon=h, predicted=round(pred, 3), ladder=str(point['lambdaA']),
                            p1=round(p_mid(point, 1), 4), in_band=in_band(point),
                            in_window=abs(p_mid(point, 1) - t) <= WINDOW))
    summary = dict(rows=len(rows), failures=len(failures), failure_status=sorted({r['status'] for r in failures}),
                   slices=len(slices), procedures=results,
                   loo=dict(cases=len(loo), in_band=sum(bool(x.get('in_band')) for x in loo),
                            in_window=sum(bool(x.get('in_window')) for x in loo)),
                   monotone_violation_slices=sum(monotone_violations(c) > 0 for c in slices.values()))
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    with (OUT / 'anchors.csv').open('w') as h:
        wr = csv.DictWriter(h, fieldnames=list(anchors[0]))
        wr.writeheader()
        wr.writerows(anchors)
    with (OUT / 'loo.csv').open('w') as h:
        keys = sorted({k for x in loo for k in x})
        wr = csv.DictWriter(h, fieldnames=keys)
        wr.writeheader()
        wr.writerows(loo)
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
