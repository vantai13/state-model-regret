"""Doan Van Tai — read the mechanism-regime rows [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

Per regime, in % of Cref = L11 unless marked _abs (packet*s):
  S = G_S|M1 (pure state value), M = G_M|S1 (pure model value), Gamma = S - G_S = M - G_M (so Gamma <= M always,
  Gamma > S iff G_S < 0), G_S, G_M, R = S/(S+M) only when S+M >= 0.5 (else NaN: "neither" region),
  inv_state/inv_model/inv_both = gain over J1 = min_rho L00(rho) (stale state + M0 + best L4.4 margin),
  coordinates rho = (lamA+lamB)/2mu, d = (lamB-lamA)/mu, u/mu, kappa/tau, h/tau, h/kappa, rhoA = (lamA+u)/mu,
  rhoB_post = (lamB+u)/mu; P_flip; stationary means of the two paths (from the captured side arrays).

  python -m experiments.explore_mech.analyze STAGE [STAGE ...]   -> results/explore_mech/<first stage>/metrics.csv
"""
from fractions import Fraction as F
import csv
import json
import math
import sys

from experiments.explore_mech.scan import OUT


def metrics(d):
    C = F(d['Cref'])
    pct = lambda x: float(100 * F(x) / C)
    lamA, lamB, kappa, eta, h, _ = (F(x) for x in d['parameters'])
    u = 2 * eta
    S, M = pct(d['G_S_M1']), pct(d['G_M_S1'])
    r = dict(id=d['id'], lamA=float(lamA), lamB=float(lamB), u=float(u), kappa=float(kappa), h=float(h),
             rho=float((lamA + lamB) / 20), d=float((lamB - lamA) / 10), u_mu=float(u / 10), h_kappa=float(h / kappa),
             rhoA=float((lamA + u) / 10), rhoB_post=float((lamB + u) / 10),
             S=S, M=M, Gamma=pct(d['Gamma']), G_S=pct(d['G_S']), G_M=pct(d['G_M']), G_SM=pct(d['G_SM']),
             R=S / (S + M) if S + M >= 0.5 else math.nan,
             S_abs=float(F(d['G_S_M1'])), M_abs=float(F(d['G_M_S1'])), Gamma_abs=float(F(d['Gamma'])), Cref=float(C),
             P_flip=float(F(d['P_flip'])) if d.get('P_flip') is not None else math.nan,
             meanA=float(F(d['sides'][0]['mean'])) if d.get('sides') else math.nan,
             meanB=float(F(d['sides'][1]['mean'])) if d.get('sides') else math.nan,
             arith=bool(d.get('arithmetic_pass')), flags=';'.join(d.get('validity_errors') or []),
             baseline_ok=bool(d.get('baseline')), host=d.get('host'), cpu=d.get('cpu'))
    if d.get('baseline'):
        L = {k: F(v) for k, v in d['losses'].items()}
        J1 = min(F(b['L00']) for b in d['baseline'])
        J2 = min(F(b['L10']) for b in d['baseline'])
        r.update(inv_state=float(100 * (J1 - J2) / C), inv_model=float(100 * (J1 - L['01']) / C),
                 inv_both=float(100 * (J1 - L['11']) / C),
                 rho_star=min(d['baseline'], key=lambda b: (F(b['L00']), F(b['rho'])))['rho'])
    else:
        r.update(inv_state=math.nan, inv_model=math.nan, inv_both=math.nan, rho_star='')
    return r


def load(stages, level='level_160_2'):
    rows, unresolved = [], []
    for stage in stages:
        for f in sorted((OUT / stage / level).glob('*.json')):
            d = json.loads(f.read_text())
            (rows.append(metrics(d)) if d['status'] == 'COMPLETED' else unresolved.append(d['id']))
    return rows, unresolved


def main():
    stages = sys.argv[1:]
    rows, unresolved = load(stages)
    out = OUT / stages[0] / 'metrics.csv'
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} rows -> {out}; {len(unresolved)} unresolved {unresolved[:5]}')


if __name__ == '__main__':
    main()
