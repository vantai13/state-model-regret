"""E4b extra tests X1-X3 (Claude, 16/11/2026), written before the E4b truth run.

Reads <out>/cells.csv (merge output of the locked E4 code) and <out>/training_checks.json. Writes <out>/score_extra.json. Definitions are in
results/letter/e4b/CARD_E4B.md.
"""
import argparse
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGRET_MAX, GS_MAX = 0.5, 0.25
TAUS = ('0.3', '1.0', '3.0')


def rule2(r):
    return max(float(r['regret_fresh_pct']), float(r['regret_stale_pct'])) <= REGRET_MAX


# Regimes where Hybrid-i missed rule 2 at h = 7 T_int for at least one age on E4 (seed 3000001).
# Outcome-defined from E4, recorded before E4b; X1 tests whether this pattern recurs on new instances.
S8 = ('G2_r80_b3_s1', 'G2_r80_b6_s0', 'G2_r90_b3_s0', 'G2_r90_b6_s0',
      'G3_r80_b3_s1', 'G3_r80_b6_s0', 'G3_r90_b3_s0', 'G3_r90_b6_s0')


def score(out):
    rows = list(csv.DictReader(open(out / 'cells.csv')))
    regimes = sorted({r['regime'] for r in rows})
    training = json.loads((out / 'training_checks.json').read_text())
    agree = {t['regime'] for t in training['regimes'] if t['ii']['best_action_agrees']}
    sel = lambda p, h: [r for r in rows if r['pipeline'] == p and r['h_mult'] == h]
    res = dict(regimes=len(regimes))
    complete = len(regimes) == 17 and all(len(sel(p, h)) == 51 for p in ('Hybrid-i', 'Hybrid-ii', 'M0') for h in ('7', '15', '30'))
    # X1: regime pattern at h = 7 for Hybrid-i (rule 2, all three ages)
    slow = {g: g in S8 for g in regimes}
    ok7 = {g: all(rule2(r) for r in sel('Hybrid-i', '7') if r['regime'] == g) for g in regimes}
    fast = [g for g in regimes if not slow[g]]
    slows = [g for g in regimes if slow[g]]
    fast_pass = sum(ok7[g] for g in fast)
    slow_fail = sum(not ok7[g] for g in slows)
    res['X1'] = dict(slow_regimes=slows, fast_regimes=fast, fast_all_ages_pass=fast_pass, fast_n=len(fast),
                     slow_some_age_fail=slow_fail, slow_n=len(slows),
                     holds=bool(fast_pass >= len(fast) - 1 and slow_fail >= len(slows) - 2))
    # X2: Hybrid-ii rule 2 at h in {15, 30} in the regimes where r-hat (ii) orders correctly on training
    x2 = [r for h in ('15', '30') for r in sel('Hybrid-ii', h) if r['regime'] in agree]
    met = sum(rule2(r) for r in x2)
    res['X2'] = dict(regimes=len(agree), units=len(x2), met=met, fraction=met / len(x2) if x2 else None,
                     threshold=0.90, holds=bool(x2 and met / len(x2) >= 0.90))
    # X3: M0 harm reproduces
    m0 = [r for h in ('15', '30') for r in sel('M0', h)]
    m0_met = sum(rule2(r) for r in m0)
    med = statistics.median(float(r['G_S_pct']) for r in sel('M0', '30'))
    res['X3'] = dict(units=len(m0), m0_rule2_met=m0_met, m0_rule2_share=m0_met / len(m0) if m0 else None,
                     median_GS_pct_h30=med, holds=bool(m0 and m0_met / len(m0) <= 0.10 and med <= -25.0))
    for k in ('X1', 'X2', 'X3'):
        res[k]['verdict'] = ('HOLDS' if res[k]['holds'] else 'DOES_NOT_HOLD') if complete else 'NOT_EVALUABLE'
    res['complete'] = complete
    return res


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, default=ROOT / 'results/letter/e4b')
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    res = score(a.out)
    print(json.dumps(res, indent=1))
    if a.write:
        dest = a.out / 'score_extra.json'
        if dest.exists():
            raise SystemExit('score_extra.json exists; write-once')
        dest.write_text(json.dumps(res, indent=1) + '\n')
