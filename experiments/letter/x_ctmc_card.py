"""Doan Van Tai — verdicts for CARD_X_CTMC (T1-T6b), written and locked before truth.

Claude, 20/11/2026, under the author's full delegation. Reads only the locked predictions.json, the truth receipt and
the raw regime files it lists (checksums verified). Every threshold is copied from CARD_X_CTMC.md.
G_S = L_stale - L_fresh (letter sign); negative means fresher telemetry hurts.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/x_ctmc'
LOAD_RULES = ('TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9', 'MLU')
HS = (30, 100)
MIN_DF, MIN_PCT = 0.01, 0.25


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sgn(x):
    return 0 if x == 0 else (1 if x > 0 else -1)


def median(values):
    v = sorted(values)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def verdict(n, minimum, passed, extra_ok=True):
    if n < minimum or not extra_ok:
        return 'NOT_EVALUABLE'
    return 'STANDS' if passed else 'DOES_NOT_STAND'


def load(out):
    pred = json.loads((out / 'predictions.json').read_text())
    exposed = set(pred.get('pilot_exposed_regimes', []))
    forecasts = {}
    for rec in pred['records']:
        if rec['status'] != 'PLANNED':
            continue
        for v in rec['rows']:
            forecasts[(rec['regime']['id'], v['rule'], int(round(v['h_T_int'])), int(round(v['tau_T_int'])))] = v
    receipt = json.loads((out / 'truth_receipt.json').read_text())
    rows = []
    for entry in receipt['raw']:
        path = ROOT / entry['path']
        if sha(path) != entry['sha256']:
            raise SystemExit('raw checksum mismatch: ' + entry['path'])
        raw = json.loads(path.read_text())
        if raw['status'] != 'COMPLETED':
            continue
        rows.extend(raw['rows'])
    return pred, exposed, forecasts, receipt, rows


def evaluate(exposed, forecasts, rows):
    cells = []
    for r in rows:
        if r.get('status') != 'COMPLETED' or r['regime'] in exposed:
            continue
        h, age = int(round(r['h_T_int'])), int(round(r['tau_T_int']))
        f = forecasts.get((r['regime'], r['rule'], h, age))
        cells.append(dict(r, h_i=h, tau_i=age, f=f))
    def eligible(c):
        f = c['f']
        return (c['h_i'] in HS and f is not None and f.get('status') == 'COMPLETED' and f.get('sign_pred') not in (None, 0)
                and abs(f['DeltaF_hat']) >= MIN_DF and abs(c['G_S_pct_C_ref']) >= MIN_PCT)
    load_cells = [c for c in cells if c['rule'] in LOAD_RULES and eligible(c)]
    def acc(group, key='sign_pred'):
        if not group:
            return None
        return sum(sgn(c['G_S']) == c['f'][key] for c in group) / len(group)
    def by_regime(group, key='sign_pred'):
        reg = {}
        for c in group:
            reg.setdefault(c['regime'], []).append(sgn(c['G_S']) == c['f'][key])
        return dict(regimes=len(reg), majority_correct=sum(sum(v) * 2 > len(v) for v in reg.values()))
    t1_acc = acc(load_cells)
    t1 = dict(verdict=verdict(len(load_cells), 20, t1_acc is not None and t1_acc >= 0.90,
                              by_regime(load_cells)['regimes'] >= 8),
              cells=len(load_cells), accuracy=t1_acc, threshold=0.90, **by_regime(load_cells),
              by_stratum={s: dict(cells=len(g), accuracy=acc(g)) for s in ('agree', 'disagree')
                          for g in [[c for c in load_cells if c['stratum'] == s]]})
    dis = [c for c in load_cells if c['stratum'] == 'disagree']
    law, null = acc(dis), acc(dis, 'null_sign')
    t2 = dict(verdict=verdict(len(dis), 10, law is not None and null is not None and law - null >= 0.20),
              cells=len(dis), law_accuracy=law, null_accuracy=null, threshold_gap=0.20)
    slope_cells = [c for c in load_cells if c['h_i'] == 100 and c['slope_measured'] != 0]
    rel = [abs(c['slope_measured'] - c['f']['slope_pred']) / abs(c['slope_measured']) for c in slope_cells]
    t3 = dict(verdict=verdict(len(rel), 20, rel and median(rel) <= 0.25), cells=len(rel), median_relative_error=median(rel),
              threshold=0.25)
    m0 = [c for c in cells if c['rule'] == 'M0' and eligible(c)]
    t4_acc = acc(m0)
    t4 = dict(verdict=verdict(len(m0), 20, t4_acc is not None and t4_acc >= 0.90), cells=len(m0), accuracy=t4_acc,
              threshold=0.90, **by_regime(m0))
    hyb = [c for c in cells if c['rule'] == 'Hybrid_hat' and c['h_i'] in HS and c.get('s_hat') is not None
           and sgn(c['s_hat']) == sgn(c['s']) and sgn(c['s']) != 0]
    ok = [max(c['regret_fresh_pct_C_ref'], c['regret_stale_pct_C_ref']) <= 0.5 for c in hyb]
    wrong = [c for c in cells if c['rule'] == 'Hybrid_hat' and c['h_i'] in HS and c.get('s_hat') is not None
             and sgn(c['s_hat']) != sgn(c['s'])]
    t5 = dict(verdict=verdict(len(ok), 20, ok and sum(ok) / len(ok) >= 0.90), cells=len(ok),
              share=(sum(ok) / len(ok)) if ok else None, threshold=0.90, wrong_sign_cells=len(wrong),
              wrong_sign_median_both_side_regret_pct=median([max(c['regret_fresh_pct_C_ref'], c['regret_stale_pct_C_ref'])
                                                             for c in wrong]))
    c5 = [c for c in m0 if c['f'].get('c5_sign') in (-1, 1)]
    t6_acc = (sum(sgn(c['G_S']) == c['f']['c5_sign'] for c in c5) / len(c5)) if c5 else None
    t6 = dict(verdict=verdict(len(c5), 20, t6_acc is not None and t6_acc >= 0.85), cells=len(c5), accuracy=t6_acc,
              threshold=0.85)
    conc = [c['concentration_old'] >= c['concentration_new'] for c in m0]
    t6b = dict(verdict=verdict(len(conc), 20, conc and sum(conc) / len(conc) >= 0.80), cells=len(conc),
               share=(sum(conc) / len(conc)) if conc else None, threshold=0.80)
    d1 = {}
    for rule in sorted({c['rule'] for c in cells}):
        g = [c for c in cells if c['rule'] == rule and c['h_i'] == 30 and c['tau_i'] == 1]
        d1[rule] = dict(regimes=len(g), harm_regimes=sum(c['G_S_pct_C_ref'] < -0.5 for c in g),
                        median_G_S_pct=median([c['G_S_pct_C_ref'] for c in g]))
    d2 = {rule: median([max(c['tie_share_fresh'], c['tie_share_stale']) for c in cells if c['rule'] == rule])
          for rule in sorted({c['rule'] for c in cells})}
    return dict(sign='G_S=L_stale-L_fresh; negative=fresh hurts', excluded_pilot_regimes=sorted(exposed),
                T1=t1, T2=t2, T3=t3, T4=t4, T5=t5, T6=t6, T6b=t6b, D1_harm_at_30Tint_tau1=d1, D2_median_tie_share=d2,
                note='Cells share regimes and are not independent trials.')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('lock', 'verify', 'score'))
    p.add_argument('--out', type=Path, default=OUT)
    a = p.parse_args(argv)
    files = {'card': a.out / 'CARD_X_CTMC.md', 'scorer': Path(__file__), 'lock': a.out / 'lock.json'}
    lock = a.out / 'lock_card.json'
    if a.command == 'lock':
        if lock.exists():
            raise SystemExit('lock_card.json exists; never overwrite')
        lock.write_text(json.dumps(dict(owner='Doan Van Tai', sha256={k: sha(v) for k, v in files.items()}), indent=2) + '\n')
        return
    locked = json.loads(lock.read_text())['sha256']
    now = {k: sha(v) for k, v in files.items()}
    if locked != now:
        raise SystemExit('lock_card mismatch')
    if a.command == 'verify':
        print(json.dumps(dict(verified=True)))
        return
    _, exposed, forecasts, receipt, rows = load(a.out)
    result = evaluate(exposed, forecasts, rows)
    result['receipt_status'] = receipt['status']
    (a.out / 'card_verdicts.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v['verdict'] for k, v in result.items() if isinstance(v, dict) and 'verdict' in v}))


if __name__ == '__main__':
    main()
