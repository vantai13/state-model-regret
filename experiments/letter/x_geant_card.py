"""Doan Van Tai — verdicts for CARD_X_GEANT (G1-G3), written and locked before truth.

Claude, 20/11/2026, under the author's full delegation. Reads only score.json (descriptive rows written by
x_geant.score) and predictions.csv. No new criteria: every threshold is copied from CARD_X_GEANT.md.
G_S = L_stale - L_fresh (letter sign); negative means fresher telemetry hurts.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/x_geant'
RULES = ('TH_0.65', 'TH_0.8', 'TH_0.9')
TH_ALL = ('TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9')
HS = (14400, 21600)
RESOLUTION_PCT = 0.25
G1_MIN, G1_ACC = 6, 0.80
G2_MIN, G2_REGRET = 20, 0.5
G3_MIN, G3_SHARE = 20, 0.90


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def predicted_signs(path):
    out = {}
    for r in csv.DictReader(open(path)):
        out[(r['regime'], r['rule'], int(r['tau_s']), int(r['h_s']))] = int(r['predicted_G_S_sign'])
    return out


def pooled(values):
    n = len(values)
    mean = sum(values) / n
    se = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) / math.sqrt(n) if n > 1 else math.inf
    return mean, se


def verdict(n, ok, minimum, passed):
    if n < minimum:
        return 'NOT_EVALUABLE'
    return 'STANDS' if passed else 'DOES_NOT_STAND'


def evaluate(rows, signs):
    x2 = [r for r in rows if r['set'] == 'X2' and r['h_s'] in HS and r['evaluable']]
    # G1: pooled cells over evaluable test-S days.
    cells = {}
    for r in x2:
        if r['rule'] in RULES:
            cells.setdefault((r['regime'], r['rule'], r['tau_s'], r['h_s']), []).append(r)
    g1_rows = []
    for key, rs in sorted(cells.items()):
        pred = signs.get(key, 0)
        if pred == 0:
            continue
        mean, se = pooled([r['G_S_Mbit_s'] for r in rs])
        cref = sum(r['C_ref_Mbit_s'] for r in rs) / len(rs)
        resolved = len(rs) > 1 and abs(mean) >= 2 * se and cref > 0 and abs(mean) >= RESOLUTION_PCT / 100 * cref
        obs = 0 if mean == 0 else (1 if mean > 0 else -1)
        g1_rows.append(dict(regime=key[0], rule=key[1], tau_s=key[2], h_s=key[3], days=len(rs), mean_G_S_Mbit_s=mean,
                            se=se, mean_C_ref=cref, G_S_pct=None if cref <= 0 else 100 * mean / cref,
                            resolved=resolved, predicted=pred, observed=obs, correct=resolved and obs == pred))
    res = [r for r in g1_rows if r['resolved']]
    acc = sum(r['correct'] for r in res) / len(res) if res else None
    # Record-level (descriptive D2).
    rec = []
    for r in x2:
        if r['rule'] in RULES and signs.get((r['regime'], r['rule'], r['tau_s'], r['h_s']), 0) != 0:
            cref = r['C_ref_Mbit_s']
            if cref > 0 and abs(r['G_S_Mbit_s']) >= 2 * r['G_S_SE_Mbit_s'] and abs(r['G_S_Mbit_s']) >= RESOLUTION_PCT / 100 * cref:
                pred = signs[(r['regime'], r['rule'], r['tau_s'], r['h_s'])]
                rec.append((1 if r['G_S_Mbit_s'] > 0 else -1) == pred)
    # G2: Stationary G_S = 0 everywhere and median both-side regret <= 0.5%.
    st = [r for r in x2 if r['rule'] == 'Stationary' and r['both_side_regret_pct'] is not None]
    gs_zero = all(r['G_S_Mbit_s'] == 0 for r in x2 if r['rule'] == 'Stationary')
    med = sorted(r['both_side_regret_pct'] for r in st)
    median = (med[len(med) // 2] if len(med) % 2 else (med[len(med) // 2 - 1] + med[len(med) // 2]) / 2) if med else None
    # G3: Stationary both-side regret <= min over TH of both-side regret.
    by = {}
    for r in x2:
        if r['both_side_regret_pct'] is not None:
            by.setdefault((r['regime'], r['date'], r['tau_s'], r['h_s']), {})[r['rule']] = r['both_side_regret_pct']
    g3 = [v['Stationary'] <= min(v[t] for t in TH_ALL) for v in by.values() if 'Stationary' in v and all(t in v for t in TH_ALL)]
    return dict(
        sign='G_S=L_stale-L_fresh; negative=fresh hurts',
        G1=dict(verdict=verdict(len(res), None, G1_MIN, acc is not None and acc >= G1_ACC), resolved=len(res),
                correct=sum(r['correct'] for r in res), accuracy=acc, threshold=G1_ACC, cells=g1_rows),
        D2_record_level=dict(resolved=len(rec), correct=sum(rec), accuracy=(sum(rec) / len(rec)) if rec else None),
        G2=dict(verdict=verdict(len(st), None, G2_MIN, gs_zero and median is not None and median <= G2_REGRET),
                records=len(st), G_S_all_zero=gs_zero, median_both_side_regret_pct=median, threshold=G2_REGRET),
        G3=dict(verdict=verdict(len(g3), None, G3_MIN, bool(g3) and sum(g3) / len(g3) >= G3_SHARE),
                cases=len(g3), stationary_not_worse=sum(g3), share=(sum(g3) / len(g3)) if g3 else None, threshold=G3_SHARE),
        X4='NOT_ENOUGH_SIGNAL (step 0, card)',
        null_comparison='NOT_EVALUABLE (null sign equals law sign in every X2 cell; declared in card)')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('lock', 'verify', 'score'))
    p.add_argument('--out', type=Path, default=OUT)
    a = p.parse_args(argv)
    files = {'card': a.out / 'CARD_X_GEANT.md', 'scorer': Path(__file__), 'lock': a.out / 'lock.json'}
    lock = a.out / 'lock_card.json'
    if a.command == 'lock':
        if lock.exists():
            raise SystemExit('lock_card.json exists; never overwrite')
        lock.write_text(json.dumps(dict(owner='Doan Van Tai', sha256={k: sha(v) for k, v in files.items()}), indent=2) + '\n')
        return
    locked = json.loads(lock.read_text())['sha256']
    now = {k: sha(v) for k, v in files.items()}
    if locked != now:
        raise SystemExit('lock_card mismatch: ' + json.dumps({k: (locked[k], now[k]) for k in now if locked[k] != now[k]}))
    if a.command == 'verify':
        print(json.dumps(dict(verified=True)))
        return
    rows = json.loads((a.out / 'score.json').read_text())['rows']
    result = evaluate(rows, predicted_signs(a.out / 'predictions.csv'))
    (a.out / 'card_verdicts.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: (v['verdict'] if isinstance(v, dict) and 'verdict' in v else v) for k, v in result.items() if k != 'sign'}))


if __name__ == '__main__':
    main()
