"""Doan Van Tai — F8: truth G_S(tau) next to S(tau) for the three regimes fixed in the card before the lock (TN0003 prior
correct, TB0007 prior wrong, TP0079 harm appearing with tau), h = 7 T_int, with the frozen zero-fit z_pred1 as reference
[EXPLORATION ONLY; AI (Claude) theo ủy quyền]. Reads saved truth only.

  python -m experiments.explore_ctmc.figure_tau_truth   # -> results/explore_ctmc/l75/F8_truth_GS_S.png + F8_data.csv

Palette: slot 1 (blue) for G_S, slot 2 (orange) for S, neutral gray dashed for the zero-fit reference; markers differ and
each panel has a legend; numbers in F8_data.csv.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from experiments.explore_ctmc import check_l75 as C

ROOT = Path(__file__).resolve().parents[2]
L75 = ROOT / 'results/explore_ctmc/l75'
REGIMES = (('TN0003', 'prior đúng (x = −0,54)'), ('TB0007', 'prior sai (x = 0,28)'), ('TP0079', 'harm xuất hiện theo τ (x = 0,81)'))
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def main(h_mult=7.0):
    m = C.load()
    rows = []
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.5), dpi=150)
    for ax, (rid, lab) in zip(axs, REGIMES):
        g = m[(m.id == rid) & m.tau_mult.notna() & (m.h_mult == h_mult)].sort_values('tau_s')
        rows.append(g[['id', 'tau_mult', 'z_pred1', 'G_S', 'S', 'done']].assign(h_mult=h_mult))
        ax.plot(g.tau_mult, g.z_pred1, color=INK2, lw=1, ls='--', label='z_pred1 (zero-fit, khóa)')
        ax.plot(g.tau_mult, g.G_S, color='#2a78d6', lw=2, marker='o', ms=4, label='G_S (truth)')
        ax.plot(g.tau_mult, g.S, color='#eb6834', lw=2, marker='s', ms=4, label='S (truth)')
        ax.axhline(0, color=INK2, lw=0.8)
        ax.set_xscale('log')
        ax.set_title(f'{rid}: {lab}', color=INK, fontsize=9, loc='left')
        ax.set_xlabel('τ / T_int', color=INK2, fontsize=8)
        ax.tick_params(colors=INK2, labelsize=7)
        ax.grid(True, color=GRID, lw=0.6)
        for sp in ax.spines.values():
            sp.set_color(GRID)
    axs[0].set_ylabel(f'% C_ref (h = {h_mult:g}·T_int)', color=INK2, fontsize=8)
    axs[0].legend(fontsize=7, frameon=False, loc='lower left')
    fig.suptitle('F8 · L7.5 truth: G_S(τ) và S(τ) cho ba regime chọn trước khóa', color=INK, fontsize=10, x=0.01, ha='left')
    fig.tight_layout()
    tag = '' if h_mult == 7.0 else f'_h{h_mult:g}T'
    fig.savefig(L75 / f'F8_truth_GS_S{tag}.png')
    pd.concat(rows).to_csv(L75 / f'F8_data{tag}.csv', index=False)
    print(pd.concat(rows).round(4).to_string())


if __name__ == '__main__':
    main()
    main(1.0)      # post-open, descriptive: at h = T_int S is not flat (added 04/11 after seeing F8 at 7 T_int)
