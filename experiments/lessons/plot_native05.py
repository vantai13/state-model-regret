"""Standalone audit figures for fixed calibration records, not CF prevalence."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import numpy as np


def main():
    folder = Path('results/lessons/l3r_7/full_numerics/native05/report')
    coverage = json.loads((folder / 'r_coverage.json').read_text())
    cfg = json.loads(Path('experiments/R3R_11_native_population/prereg.json').read_text())
    ids = [j['id'] for j in cfg['cases']]
    matrix = np.zeros((len(coverage), len(ids)), dtype=int)
    for i, row in enumerate(coverage):
        for j, rid in enumerate(ids):
            check = row['checks'].get(rid, {})
            if check.get('reason') == 'missing_levels' or not check:
                continue
            matrix[i, j] = (3 if check['ready'] else
                            2 if check.get('refinement_ready') else 1)
    fig, (ax, bars) = plt.subplots(2, 1, figsize=(14, 5.5),
        gridspec_kw={'height_ratios':[2,1.2]}, constrained_layout=True)
    colors = ['#d9dfe5', '#bd3d3a', '#dfac35', '#27815b']
    ax.imshow(matrix, aspect='auto', interpolation='nearest',
              cmap=ListedColormap(colors), vmin=0, vmax=3)
    ax.set_yticks(range(len(coverage)), [f"K={r['K']}, ref={r['ref']}" for r in coverage])
    ax.set_xticks([0,31,63,95,103,111,113], [ids[i] for i in [0,31,63,95,103,111,113]], rotation=15, ha='right')
    ax.set_title('L3R.7: kiểm độ chính xác trên 114 calibration records cố định')
    ax.legend(handles=[Patch(color=c, label=t) for c,t in zip(colors,
        ['Chưa đủ levels', 'R1 chưa đạt', 'R1 đạt; arithmetic/validity chưa đạt', 'Đạt mọi điều kiện'])],
        loc='upper center', bbox_to_anchor=(.5, -.29), ncol=4, frameon=False, fontsize=8)
    ready = [r['ready'] for r in coverage]
    bars.bar(range(len(ready)), ready, color='#27815b')
    bars.axhline(len(ids), color='#485361', linestyle='--', linewidth=1)
    bars.set_xticks(range(len(ready)), [f"{r['K']}/{r['ref']}" for r in coverage])
    bars.set_ylabel('Records đạt / 114')
    bars.set_xlabel('K / ref · calibration coverage, không phải ước lượng tỷ lệ CF')
    bars.set_ylim(0, 124)
    for i, n in enumerate(ready):
        bars.text(i, n+2, str(n), ha='center', fontsize=9)
    fig.savefig(folder/'numerical_readiness.png', dpi=180)
    fig.savefig(folder/'numerical_readiness.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()
