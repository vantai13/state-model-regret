"""Doan Van Tai — read the exploration rows as "what is worth investing in" [EXPLORATION ONLY].
AI (Claude) theo ủy quyền. Percent of Cref = L11 throughout.

Per regime:
  S_own   = G_S|M1            value of current state once the model is right (EVPI-like, >= 0)
  M_own   = G_M|S1            value of the right model once the state is current (>= 0)
  M_resid = G_M - (L00 - min_rho L00(rho))   model value left after the best L4.4 margin (stale state)
  S_marg  = L00(rho*) - L10(rho*)            state value for a margin-M0 controller (negative = harm)
  inv_*   = gain over the practical controller J1 = min_rho L00(rho) (stale state, M0, best margin):
            inv_state = J1 - min_rho L10(rho); inv_model = J1 - L01; inv_both = J1 - L11 (oracle)
  Gamma, G_S, G_M, stakes = Sbar
  python -m experiments.explore_p4.analyze STAGE [LEVEL_DIR]
"""
from fractions import Fraction as F
import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from experiments.explore_p4.scan import OUT


def metrics(d):
    C = F(d['Cref'])
    pct = lambda x: float(100 * F(x) / C)
    L = {k: F(v) for k, v in d['losses'].items()}
    J1 = min(F(b['L00']) for b in d['baseline'])     # practical controller: stale state + M0 + best margin
    J2 = min(F(b['L10']) for b in d['baseline'])     # fresh state + M0 + its own best margin
    base = {b['rho']: (F(b['L00']), F(b['L10'])) for b in d['baseline']}
    rho_star = min(base, key=lambda r: (base[r][0], F(r)))
    l00s, l10s = base[rho_star]
    lamA, lamB, kappa, eta, h, _ = d['parameters']
    return dict(id=d['id'], lamA=float(F(lamA)), lamB=float(F(lamB)), u=float(2 * F(eta)), kappa=float(F(kappa)),
                h=float(F(h)), S_own=pct(d['G_S_M1']), M_own=pct(d['G_M_S1']), Gamma=pct(d['Gamma']),
                G_S=pct(d['G_S']), G_M=pct(d['G_M']), M_resid=float(100 * (l00s - L['01']) / C),
                S_marg=float(100 * (l00s - l10s) / C), rho_star=rho_star, stakes=pct(d['Sbar']),
                inv_state=float(100 * (J1 - J2) / C), inv_model=float(100 * (J1 - L['01']) / C),
                inv_both=float(100 * (J1 - L['11']) / C),
                arith=bool(d.get('arithmetic_pass')), flags=';'.join(d.get('validity_errors') or []))


def load(stage, level='level_160_2'):
    rows, bad = [], []
    for f in sorted((OUT / stage / level).glob('*.json')):
        d = json.loads(f.read_text())
        (rows.append(metrics(d)) if d['status'] == 'COMPLETED' and d.get('baseline') else bad.append(d['id']))
    return rows, bad


def heat(ax, rows, key, title, kappas, hs, reduce=max, vmax=None, fmt='{:.1f}'):
    grid = np.full((len(hs), len(kappas)), np.nan)
    for i, h in enumerate(hs):
        for j, k in enumerate(kappas):
            vals = [r[key] for r in rows if r['h'] == h and r['kappa'] == k]
            if vals:
                grid[i, j] = reduce(vals)
    im = ax.imshow(grid, origin='lower', cmap='Blues', vmin=0, vmax=vmax or np.nanmax(grid), aspect='auto')
    for i in range(len(hs)):
        for j in range(len(kappas)):
            if not np.isnan(grid[i, j]):
                ax.text(j, i, fmt.format(grid[i, j]), ha='center', va='center', fontsize=7,
                        color='white' if grid[i, j] > 0.6 * (vmax or np.nanmax(grid)) else '#0b0b0b')
    ax.set_xticks(range(len(kappas)), [f'{k:g}' for k in kappas], fontsize=7)
    ax.set_yticks(range(len(hs)), [f'{h:g}' for h in hs], fontsize=7)
    ax.set_xlabel('κ/τ (mode kéo dài, so với tuổi telemetry)', fontsize=8)
    ax.set_ylabel('h/τ (horizon)', fontsize=8)
    ax.set_title(title, fontsize=8, loc='left')
    return im


def main():
    stage = sys.argv[1]
    rows, bad = load(stage)
    out = OUT / stage
    keys = list(rows[0])
    with open(out / 'metrics.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    kappas = sorted({r['kappa'] for r in rows})
    hs = sorted({r['h'] for r in rows})
    fig, axs = plt.subplots(1, 4, figsize=(15, 3.8), dpi=150)
    heat(axs[0], rows, 'inv_both', 'Lợi tối đa so với baseline (cả hai → oracle), max, % C̄', kappas, hs)
    heat(axs[1], rows, 'inv_state', 'Chỉ đầu tư state tươi, max, % C̄', kappas, hs)
    heat(axs[2], rows, 'M_own', 'Giá trị riêng của model Ḡ_M|S1 (cần state tươi), max, % C̄', kappas, hs)
    heat(axs[3], [dict(r, harm=max(0, -r['inv_state'])) for r in rows], 'harm',
         'State tươi + M0 (margin riêng) gây hại, max, % C̄', kappas, hs)
    fig.suptitle(f'Exploration {stage}: {len(rows)} regime, ±6, c_sw 0, τ = 1 s. Baseline = state cũ + M0 + margin tốt nhất. Mỗi ô = max trên λA, λB, u', fontsize=9, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out / 'heat_max.png')
    plt.close(fig)
    print(f'{len(rows)} rows, {len(bad)} unresolved: {bad[:5]}')


if __name__ == '__main__':
    main()
