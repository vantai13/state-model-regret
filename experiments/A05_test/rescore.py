"""Doan Van Tai — independent re-application of the frozen A05-T rules to a saved grading input.

AI (Claude) viết theo ủy quyền (L3.7). Written without importing A03 grading,
A05 scoring or score_test; it re-implements prereg §7 with exact Fractions and
compares its verdicts with the run's verdict.json. No engine, no new cell.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path

SIX = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')
PC4 = ('G_S', 'G_M', 'Gamma')
S, N, U, X = 'STANDS', 'DOES_NOT_STAND', 'UNRESOLVED', 'EXCLUDED_ZERO_REFERENCE'
MARGIN, RADIUS, EQUIV, PAIR_TOL, FLIP, MASS = Q(1, 400), Q(1, 4000), Q(1, 200), Q(1, 400), Q(1, 200), Q(1, 100)


def num(x):
    if isinstance(x, bool):
        raise ValueError('boolean endpoint')
    return Q(str(x))


def iv(row, key):
    lo, hi = (num(v) for v in row['intervals'][key])
    if lo > hi:
        raise ValueError('reversed interval')
    return lo, hi


def div(a, b):
    if b[0] <= 0:
        raise ZeroDivisionError('nonpositive denominator')
    corners = [x / y for x in a for y in b]
    return min(corners), max(corners)


def kleene_all(states):
    states = list(states)
    if not states:
        return U
    return N if N in states else S if all(s == S for s in states) else U


def hold(row):
    mass = row.get('unresolved_mass', {})
    return (row.get('status') != 'BOUNDED' or row.get('numeric_budget_met') is not True or
            not {'oracle', 'M0', 'D22'} <= set(mass) or any(num(v) > MASS for v in mass.values()))


def check_reference(row):
    if iv(row, 'C_ref') != iv(row, 'L11'):
        raise ValueError('C_ref must equal L11 of the same row')
    ctx = row['reference_context']
    if ctx['refinement'] != row['refinement'] or num(ctx['dt_s']) != num(row['dt_s']):
        raise ValueError('mixed reference context')


def pair_state(coarse, fine):
    check_reference(coarse)
    check_reference(fine)
    if fine['refinement'] != 2 * coarse['refinement'] or num(coarse['dt_s']) != 2 * num(fine['dt_s']):
        raise ValueError('pair must be adjacent')
    if hold(coarse) or hold(fine):
        return U
    C, Cc = iv(fine, 'C_ref'), iv(coarse, 'C_ref')
    states = []
    for g in SIX:
        f, c = iv(fine, g), iv(coarse, g)
        d = (f[0] - c[1], f[1] - c[0])
        low = Q(0) if d[0] <= 0 <= d[1] else min(abs(d[0]), abs(d[1]))
        high = max(abs(d[0]), abs(d[1]))
        state = S if high <= PAIR_TOL * C[0] else N if low > PAIR_TOL * C[1] else U
        if C[0] > 0 and Cc[0] > 0:
            cr, fr = div(c, Cc), div(f, C)
            certain = (cr[0] > FLIP and fr[1] < -FLIP) or (fr[0] > FLIP and cr[1] < -FLIP)
            possible = (cr[1] > FLIP and fr[0] < -FLIP) or (fr[1] > FLIP and cr[0] < -FLIP)
            if certain:
                state = N
            elif possible and state == S:
                state = U
        states.append(state)
    return kleene_all(states)


def equivalence_cell(fine, coarse):
    if fine is None or coarse is None:
        return U, 'NOT_RESOLVED'
    if fine['dt_s'] != '1/240' or coarse['dt_s'] != '1/120':
        raise ValueError('frozen equivalence must use the registered final dt')
    other = 'NOT_STANDING_OR_UNRESOLVED'
    check_reference(fine)
    C = iv(fine, 'C_ref')
    if C == (0, 0):
        return X, other
    if hold(fine) or pair_state(coarse, fine) != S:
        return U, other
    if C[0] <= 0:
        return U, other
    gm = div(iv(fine, 'G_M'), C)
    state = S if gm[1] <= EQUIV else N if gm[0] > EQUIV else U
    headroom = div(iv(fine, 'R00'), C)
    label = ('STANDS_HEADROOM_LIMITED' if state == S and headroom[1] < EQUIV
             else 'STANDS_NOT_CERTIFIED_BY_HEADROOM' if state == S else 'NOT_STANDING_OR_UNRESOLVED')
    return state, label


def comparison(ids, data, predictions, group, declared_D):
    if num(declared_D) < MARGIN:
        return dict(verdict='DO_NOT_OPEN')
    eligible, missing = [], []
    for cid in ids:
        fine, coarse = data.get('fine', {}).get(cid), data.get('coarse', {}).get(cid)
        if fine is None or coarse is None:
            missing.append(cid); continue
        if fine['dt_s'] != '1/240' or coarse['dt_s'] != '1/120':
            missing.append(cid); continue
        if hold(fine) or pair_state(coarse, fine) != S or iv(fine, 'C_ref')[0] <= 0:
            missing.append(cid); continue
        bands = [div(iv(fine, g), iv(fine, 'C_ref')) for g in PC4]
        if max((b[1] - b[0]) / 2 for b in bands) > RADIUS:
            missing.append(cid); continue
        eligible.append((cid, bands))
    cap = 2 if group == 'interpolation' else 0
    if len(missing) > cap or not eligible:
        return dict(verdict='INCONCLUSIVE', eligible=[c for c, _ in eligible], unavailable=missing)
    triples = []
    for cid, bands in eligible:
        for g, band in zip(PC4, bands):
            triples.append((band, num(predictions[cid]['H0']['contrasts'][g]),
                            num(predictions[cid]['H1']['contrasts'][g])))
    D = sum(abs(a - b) for _, a, b in triples) / len(triples)
    if D < MARGIN:
        return dict(verdict='INCONCLUSIVE', eligible=[c for c, _ in eligible], unavailable=missing, active_D=D)
    lows, highs = [], []
    for (lo, hi), a, b in triples:
        ends = [abs(a - y) - abs(b - y) for y in (lo, hi)]
        lows.append(min(ends)); highs.append(max(ends))
    d = (sum(lows) / len(lows), sum(highs) / len(highs))
    verdict = ('SUPPORT' if d[0] >= MARGIN else 'FALSIFY' if d[1] <= 0
               else 'WEAKEN' if d[0] > 0 and d[1] < MARGIN else 'INCONCLUSIVE')
    return dict(verdict=verdict, d_interval=d, active_D=D, eligible=[c for c, _ in eligible], unavailable=missing)


def rescore(data, predictions, disc, k5_ids=('R03', 'R04'), c1_ids=('R05', 'R06', 'R07', 'R08')):
    allowed = set(disc['outcome_open_ids'])
    if any(set(data.get(k, {})) - allowed for k in ('fine', 'coarse')):
        raise PermissionError('saved outcomes include an unauthorized cell')
    pc4 = {name: comparison(info['ids'], data, predictions, name, info['D']) for name, info in disc['groups'].items()}
    def branch(ids):
        cells = {c: equivalence_cell(data.get('fine', {}).get(c), data.get('coarse', {}).get(c)) for c in ids}
        return dict(verdict=kleene_all(s for s, _ in cells.values()), cells=cells)
    K, C1 = branch(k5_ids), branch(c1_ids)
    return dict(PC4=pc4, K5=K, K5_full_rule=kleene_all([S, S, K['verdict']]), C1=C1)


def agree(mine, frozen):
    """Compare with score_test output (Fractions serialized as strings)."""
    problems = []
    for name, res in mine['PC4'].items():
        theirs = frozen['PC4'][name]
        if res['verdict'] != theirs['verdict']:
            problems.append(f'PC4 {name} verdict {res["verdict"]} != {theirs["verdict"]}')
        if 'd_interval' in res and tuple(num(x) for x in theirs.get('d_interval', ())) != res['d_interval']:
            problems.append(f'PC4 {name} d_interval differs')
    for key, mine_branch, theirs in (('K5', mine['K5'], frozen['K5']['heldout_K']),
                                     ('C1', mine['C1'], frozen['C1']['heldout'])):
        if mine_branch['verdict'] != theirs['verdict']:
            problems.append(f'{key} verdict differs')
        for cid, (state, label) in mine_branch['cells'].items():
            cell = theirs['cells'][cid]
            if state != cell['verdict'] or label != cell['headroom_label']:
                problems.append(f'{key} {cid} differs')
    if mine['K5_full_rule'] != frozen['K5']['full_rule_verdict']:
        problems.append('K5 full rule differs')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    data = json.loads((args.run_dir / 'grading_input.json').read_text())
    predictions = json.loads((root / 'experiments/A05_freeze/predictions_heldout.json').read_text())['predictions']
    disc = json.loads((root / 'experiments/A05_freeze/discrimination.json').read_text())
    frozen = json.loads((args.run_dir / 'verdict.json').read_text())['grades']
    mine = rescore(data, predictions, disc)
    problems = agree(mine, frozen)
    summary = dict(primary=mine['PC4']['interpolation']['verdict'],
                   extrapolation=mine['PC4']['extrapolation']['verdict'],
                   weak=mine['PC4']['weak_interpolation']['verdict'],
                   K5=mine['K5']['verdict'], C1=mine['C1']['verdict'],
                   d_interpolation=[str(x) for x in mine['PC4']['interpolation'].get('d_interval', ())],
                   d_extrapolation=[str(x) for x in mine['PC4']['extrapolation'].get('d_interval', ())],
                   agreement='PASS' if not problems else 'FAIL', problems=problems)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
