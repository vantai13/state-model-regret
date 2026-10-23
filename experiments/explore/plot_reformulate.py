"""DISCOVERY figure: p_sw ladders per slice (sign probabilities only). Claude (AI) for Doan Van Tai."""
import json
from fractions import Fraction as F
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_reformulate'
INK, INK2, MUTED, GRID, AXIS, SURFACE, BAND = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#fcfcfb', '#f0efec'
SERIES = [('1/2', '1/2', '#2a78d6', 'o', 'B q50 · η 0,5'), ('9/10', '1/2', '#eb6834', 's', 'B q90 · η 0,5'),
          ('1/2', '3/4', '#1baf7a', '^', 'B q50 · η 0,75'), ('9/10', '3/4', '#eda100', 'D', 'B q90 · η 0,75')]
comma = FuncFormatter(lambda x, _: f'{x:g}'.replace('.', ','))


def main():
    rows = [json.loads(l) for l in (OUT / 'ladder_rows.jsonl').read_text().splitlines()]
    rows = [r for r in rows if r['status'] == 'OK' and r['alphaA'] == '9/10']
    kappas, horizons = ['3/10', '1', '3'], ['2', '8', 'rh1']
    names = {'2': 'h = 2 s', '8': 'h = 8 s', 'rh1': 'h = drain(B) (r_h = 1)'}
    fig, axes = plt.subplots(3, 3, figsize=(12, 10), sharex=True, sharey=True, facecolor=SURFACE)
    for i, hz in enumerate(horizons):
        for j, k in enumerate(kappas):
            ax = axes[i][j]
            ax.set_facecolor(SURFACE)
            ax.axhspan(0.1, 0.9, color=BAND, zorder=0)
            for t in (0.3, 0.7):
                ax.axhline(t, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
            for b, e, color, marker, label in SERIES:
                pts = sorted((float(F(r['lambdaA'])), (r['p_low_1'] + r['p_high_1']) / 2) for r in rows
                             if r['kappa'] == k and r['horizon'] == hz and r['alphaB'] == b and r['eta'] == e)
                if pts:
                    ax.plot(*zip(*pts), color=color, lw=2, marker=marker, ms=5, label=label, zorder=3,
                            markeredgecolor=SURFACE, markeredgewidth=1)
            ax.set_title(f"κ = {k.replace('3/10', '0,3')} · {names[hz]}", fontsize=10, color=INK, loc='left')
            ax.grid(color=GRID, lw=0.6)
            ax.set_ylim(-0.03, 1.03)
            for side in ('top', 'right'):
                ax.spines[side].set_visible(False)
            for side in ('left', 'bottom'):
                ax.spines[side].set_color(AXIS)
            ax.tick_params(colors=MUTED, labelsize=8)
            ax.xaxis.set_major_formatter(comma)
            ax.yaxis.set_major_formatter(comma)
            if i == 2:
                ax.set_xlabel('λA (packet/s, nền của A)', color=INK2, fontsize=9)
            if j == 0:
                ax.set_ylabel('p_sw (tỉ lệ oracle chọn Switch)', color=INK2, fontsize=9)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=4, frameon=False, fontsize=9, labelcolor=INK)
    fig.text(0.01, 0.005, 'Dải xám: vùng có quyết định thật [0,1; 0,9]. Đường chấm: mục tiêu neo 0,3 và 0,7. '
             'A ở q90. dt = 1/120 s. Chỉ là xác suất dấu của oracle, không có kết quả G hay regret.',
             fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(OUT / 'p_sw_ladders.png', dpi=130, facecolor=SURFACE)


if __name__ == '__main__':
    main()
