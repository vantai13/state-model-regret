"""Doan Van Tai — F7: zero-fit z_inf against telemetry age tau/T_int, by x stratum (L7.5 Stage 0) [EXPLORATION ONLY;
AI (Claude) theo ủy quyền]. Zero fit only: there is no truth at tau != 1 outside the two control regimes.

  python -m experiments.explore_ctmc.figure_tau     # -> results/explore_ctmc/l75/F7_tau_zinf.png + F7_data.csv

Palette: first four categorical slots of the dataviz reference palette (adjacent pairs validated, light mode); aqua and
yellow are below 3:1 contrast, so every line is directly labelled and has its own marker, and the medians are in
F7_data.csv (table view).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from experiments.explore_ctmc import check_l75 as C, tau as T5

ROOT = Path(__file__).resolve().parents[2]
L75 = ROOT / 'results/explore_ctmc/l75'
COL = {'neg': '#2a78d6', 'pos': '#eb6834', 'band': '#1baf7a', 'old': '#eda100'}
MK = {'neg': 'o', 'pos': 's', 'band': '^', 'old': 'D'}
LAB = {'neg': 'x < 0', 'pos': 'x ≥ 0,4', 'band': '0 < x ≤ 0,35 (dải giúp)', 'old': '10 regime L7.1'}
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def main():
    z = pd.read_csv(L75 / 'ZEROFIT_tau.csv', dtype={'h': str, 'tau': str})
    z = z[(z.status == 'COMPLETED') & (z.h == 'inf') & z.stage.isin(['sobol', 'old'])].copy()
    gmap = {}
    for st in ('sobol', 'old'):
        for c in json.loads((ROOT / 'results/explore_ctmc/cases_l75' / f'{st}.json').read_text()):
            gmap.update({(st, c['id'], t): m for t, m in T5.tau_grid_map(c, st).items()})
    z['tau_mult'] = [gmap.get((s, i, t), np.nan) for s, i, t in zip(z.stage, z.id, z.tau)]
    z = z[z.tau_mult.notna()]
    med = z.groupby(['stratum', 'tau_mult']).z_inf.agg(['median', lambda s: s.quantile(.25), lambda s: s.quantile(.75), 'size'])
    med.columns = ['median', 'q25', 'q75', 'n']
    med.reset_index().to_csv(L75 / 'F7_data.csv', index=False)
    fig, ax = plt.subplots(figsize=(6.6, 3.9), dpi=150)
    for s in ('neg', 'pos', 'band', 'old'):
        g = med.loc[s]
        ax.plot(g.index, g['median'], color=COL[s], lw=2, marker=MK[s], ms=5, label=f'{LAB[s]} (n = {int(g["n"].iloc[0])})')
        ax.fill_between(g.index, g.q25, g.q75, color=COL[s], alpha=0.12, lw=0)
        ax.text(g.index[-1] * 1.15, g['median'].iloc[-1], LAB[s], color=INK2, fontsize=7, va='center')
    ax.axhline(0, color=INK2, lw=1)
    ax.set_xscale('log')
    ax.set_xlim(0.002, 60)
    ax.set_title('F7 · τ (zero-fit, h = ∞): trung vị z_∞ và khoảng q25–q75 theo tầng x', color=INK, fontsize=10, loc='left')
    ax.set_xlabel('τ / T_int (tuổi của telemetry bị thay)', color=INK2, fontsize=9)
    ax.set_ylabel('z_∞ = G_S (% C_ref); < 0 là harm', color=INK2, fontsize=9)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, color=GRID, lw=0.6)
    for sp in ax.spines.values():
        sp.set_color(GRID)
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig(L75 / 'F7_tau_zinf.png')
    print(med.round(3).to_string())


if __name__ == '__main__':
    main()
