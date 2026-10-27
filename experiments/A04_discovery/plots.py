"""Doan Van Tai — A04 figures, available only after committed card scoring."""
import argparse
import csv
from fractions import Fraction as F
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from experiments.A03_card.grading import CONTRASTS
from experiments.A04_discovery.provenance import require_score_commit

CAPTION = ('Selected near-boundary cells, not network frequencies; psi in [-0.20, +0.05]. '
           'lambdaA differs across slices; h=2 s only at kappa=0.3.\n'
           'D-specific finite-window costs, not long-run loss. Points are not connected. '
           'Error bars: numeric enclosure, not CI; DK1=candidate for main cells.')
COLORS = {.3: '#2166ac', 1.: '#238b45', 3.: '#b2182b'}
GROUPS = ('core', 'spoke_A50', 'spoke_h2')


def load_rows(out):
    with (Path(out) / 'cells.csv').open() as f:
        return [r for r in csv.DictReader(f) if r['refinement'] == '2' and r['cell'].startswith('M')]


def val(row, key):
    return float(F(row[key]))


def label(r):
    mark = '*' if r['floor'] == 'True' else ''
    flag = '!' if r['pair_flag'] == 'True' or r['status'] != 'BOUNDED' else ''
    return f'{r["cell"]}{mark}{flag}\nl={val(r,"lambdaA"):g}\np={val(r,"p_sw"):.3f}'


def save(fig, path):
    fig.savefig(path.with_suffix('.png'), dpi=180, bbox_inches='tight')
    fig.savefig(path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)


def generate(out):
    out = Path(out)
    commit = require_score_commit(out)
    rows = load_rows(out)
    target = out / 'figures'
    target.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1.6])
    for j, h in enumerate((8, 2)):
        ax = fig.add_subplot(gs[0, j])
        subset = [r for r in rows if val(r, 'h_s') == h]
        for r in subset:
            c, x, y = val(r, 'C_ref'), 100*val(r, 'E_delta')/val(r, 'C_ref'), 100*val(r, 'E_delta_hat')/val(r, 'C_ref')
            ax.errorbar(x, y, xerr=100*val(r, 'e_E_delta')/c, yerr=100*val(r, 'e_E_delta_hat')/c,
                        fmt='o' if r['alphaB'] == '1/2' else '^', color=COLORS[val(r, 'kappa')],
                        ms=6, alpha=.8, capsize=2)
            ax.annotate(r['cell'] + ('*' if r['floor'] == 'True' else ''), (x, y),
                        xytext=(3, 4 if int(r['cell'][1:]) % 2 else -11), textcoords='offset points', fontsize=6.5)
        lo, hi = min(ax.get_xlim()[0], ax.get_ylim()[0]), max(ax.get_xlim()[1], ax.get_ylim()[1])
        ax.plot([lo, hi], [lo, hi], ':', color='gray', lw=.8)
        ax.axhline(0, color='black', lw=.7); ax.axvline(0, color='black', lw=.7)
        ax.set(xlabel='True E[Delta] (% Cref)', ylabel='M0 E[Delta_hat] (% Cref)', title=f'H1: T01 decision plane, h={h} s')
        ax.grid(alpha=.15)
    ax = fig.add_subplot(gs[1, :]); ax.axis('off')
    lines = [f'{r["cell"]}{"*" if r["floor"] == "True" else ""}: lambdaA={val(r,"lambdaA"):g}; p_sw={val(r,"p_sw"):.4f}' for r in rows]
    for j in range(3):
        ax.text(.02 + j*.33, .97, '\n'.join(lines[j*13:(j+1)*13]), va='top', fontsize=8, family='monospace')
    fig.suptitle('H1: near-boundary design | blue kappa=.3, green=1, red=3 | circle B q50, triangle B q90 | *=floor', fontsize=11)
    fig.text(.02, .005, CAPTION, fontsize=8)
    fig.subplots_adjust(hspace=.3, bottom=.07)
    save(fig, target / 'H1_decision_plane')

    fig, axes = plt.subplots(6, 3, figsize=(25, 18), gridspec_kw={'width_ratios': [22, 8, 8]})
    for col, group in enumerate(GROUPS):
        subset = [r for r in rows if r['group'] == group]
        x = np.arange(len(subset))
        for line, metric in enumerate(CONTRASTS):
            ax = axes[line, col]
            y = [100*val(r, metric)/val(r, 'C_ref') for r in subset]
            err = [100*val(r, 'e_' + metric)/val(r, 'C_ref') for r in subset]
            ax.axhspan(-.5, .5, color='#e5e5e5', label='equivalence band')
            ax.axhline(1, color='#d95f02', ls='--', lw=.8); ax.axhline(-1, color='#d95f02', ls='--', lw=.6)
            ax.errorbar(x, y, yerr=err, fmt='o', ms=4, color='#225ea8', capsize=2)
            ax.set_ylabel(metric + ' (% Cref)')
            ax.set_xticks(x, [label(r) if line == 5 else r['cell'] for r in subset], fontsize=6.5,
                          rotation=90 if line != 5 else 0)
            ax.grid(axis='y', alpha=.15)
            if line == 0:
                ax.set_title(group + (' (h=2 s)' if group == 'spoke_h2' else ' (h=8 s)'))
    fig.suptitle('H2: six contrasts | gray band +/-0.5%; dashed +/-1% | l=lambdaA, p=p_sw; *=floor, !=HOLD/dt flag', fontsize=13)
    fig.text(.015, .005, CAPTION, fontsize=9)
    fig.subplots_adjust(hspace=.45, wspace=.28, top=.95, bottom=.08)
    save(fig, target / 'H2_six_contrasts')

    fig, axes = plt.subplots(1, 3, figsize=(25, 6), gridspec_kw={'width_ratios': [22, 8, 8]})
    for ax, group in zip(axes, GROUPS):
        subset = [r for r in rows if r['group'] == group]
        x = np.arange(len(subset))
        y = [100*val(r, 'R00')/val(r, 'C_ref') for r in subset]
        err = [100*val(r, 'e_R00')/val(r, 'C_ref') for r in subset]
        ax.errorbar(x, y, yerr=err, fmt='o', color='#238b45', capsize=3)
        ax.axhline(1, ls='--', color='#d95f02'); ax.set_title(group)
        ax.set_xticks(x, [label(r) for r in subset], fontsize=7)
        ax.set_ylabel('R00 = L00 - L11 (% Cref)'); ax.grid(axis='y', alpha=.2)
    fig.suptitle('H3: baseline headroom, fixed cheap-kill domains | dashed=1%; l=lambdaA, p=p_sw; *=floor', fontsize=12)
    fig.text(.015, .005, CAPTION, fontsize=9)
    fig.subplots_adjust(bottom=.22, wspace=.23)
    save(fig, target / 'H3_headroom')
    return commit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    print('[DISCOVERY] plots created after score commit ' + generate(args.run_dir))


if __name__ == '__main__':
    main()
