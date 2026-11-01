"""Doan Van Tai — phase-diagram figures for the mechanism-regime exploration [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

Reads results/explore_mech/<stage>/metrics.csv (analyze.py). Facets: u/mu band (columns) x rho band (rows); axes
log10 h/tau (x) and log10 kappa/tau (y). Point density reflects the Sobol design, not real-world frequency.

  python -m experiments.explore_mech.phase STAGE
"""
import csv
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from experiments.explore_mech.scan import OUT

U_BANDS = [(0, .1, 'u/μ < 0,10'), (.1, .2, 'u/μ 0,10–0,20'), (.2, .31, 'u/μ ≥ 0,20')]
RHO_BANDS = [(0, .7, 'ρ < 0,70'), (.7, .8, 'ρ 0,70–0,80'), (.8, 1, 'ρ ≥ 0,80')]
NEITHER = '#c9c9c9'


def rows(stage):
    with open(OUT / stage / 'metrics.csv') as f:
        return [{k: (float(v) if k not in ('id', 'flags', 'host', 'rho_star', 'arith', 'baseline_ok') else v)
                 for k, v in r.items()} for r in csv.DictReader(f)]


def facet(stage, rs, value, title, fname, cmap, vmin, vmax, mask=None, label=''):
    fig, axs = plt.subplots(3, 3, figsize=(13, 10.5), dpi=130, sharex=True, sharey=True)
    for i, (r0, r1, rl) in enumerate(RHO_BANDS[::-1]):
        for j, (u0, u1, ul) in enumerate(U_BANDS):
            ax = axs[i, j]
            sub = [r for r in rs if r0 <= r['rho'] < r1 and u0 <= r['u_mu'] < u1]
            off = [r for r in sub if mask and not mask(r)]
            on = [r for r in sub if not mask or mask(r)]
            if off:
                ax.scatter([math.log10(r['h']) for r in off], [math.log10(r['kappa']) for r in off], s=4, c=NEITHER,
                           linewidths=0)
            sc = ax.scatter([math.log10(r['h']) for r in on], [math.log10(r['kappa']) for r in on], s=7,
                            c=[value(r) for r in on], cmap=cmap, vmin=vmin, vmax=vmax, linewidths=0)
            xs = np.linspace(-1, 1.5, 2)
            ax.plot(xs, xs - math.log10(160), color='#6b6b6b', lw=.8, ls='--')
            ax.set_title(f'{rl} · {ul} · n={len(sub)}', fontsize=8, loc='left')
            if i == 2:
                ax.set_xlabel('log10 h/τ', fontsize=8)
            if j == 0:
                ax.set_ylabel('log10 κ/τ', fontsize=8)
            ax.tick_params(labelsize=7)
            ax.set_ylim(-1.85, 1.45)
            ax.set_xlim(-1.1, 1.6)
    cb = fig.colorbar(sc, ax=axs, shrink=.6, pad=.02)
    cb.set_label(label, fontsize=8)
    fig.suptitle(f'{title}\n{stage}: {len(rs)} regime, a/μ = 0,6, c_sw = 0; xám = {"không đạt điều kiện tô màu" if mask else ""};'
                 ' nét đứt h/κ = 160 (cận quét)', fontsize=9, x=.01, ha='left')
    fig.savefig(OUT / stage / fname, bbox_inches='tight')
    plt.close(fig)


def main():
    stage = sys.argv[1]
    rs = rows(stage)
    big = lambda r: r['S'] + r['M'] >= .5
    facet(stage, rs, lambda r: r['R'], 'R = S/(S+M): tím = state chiếm ưu thế, cam = model chiếm ưu thế (chỉ khi S+M ≥ 0,5%)',
          'phase_R.png', 'PuOr', 0, 1, big, 'R')
    facet(stage, rs, lambda r: r['Gamma'] / (r['S'] + r['M']), 'Γ/(S+M): đỏ = Γ > 0 (bổ trợ), xanh = Γ < 0 (thay thế)',
          'phase_Gamma.png', 'RdBu_r', -.5, .5, big, 'Γ/(S+M)')
    facet(stage, [dict(r, lsm=math.log10(max(r['S'] + r['M'], 1e-3))) for r in rs], lambda r: r['lsm'],
          'log10(S + M), % C̄_ref', 'phase_SM.png', 'Blues', -2, 1.5, None, 'log10(S+M)')
    ok = [r for r in rs if not math.isnan(r['inv_both'])]
    facet(stage, ok, lambda r: r['inv_both'], 'Lợi tối đa so với baseline margin (state cũ + M0 + ρ* tốt nhất), % C̄_ref',
          'phase_practical.png', 'Blues', 0, 5, None, 'inv_both')


if __name__ == '__main__':
    main()
