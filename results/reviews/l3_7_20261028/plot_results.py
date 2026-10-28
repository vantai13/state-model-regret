"""Doan Van Tai — display saved audit metrics; no new experiment."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent
audit = json.loads((OUT / 'audit.json').read_text())
names = ['interpolation', 'extrapolation']
labels = ['Nội suy · 8 ô', 'Ngoại suy h=12 s · 2 ô']
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout='constrained')
x = np.arange(2)
for i, model in enumerate(['MAE0_pp', 'MAE1_pp']):
    bands = np.array([audit['PC4'][name][model] for name in names])
    mid = bands.mean(axis=1)
    bars = axes[0].bar(x + (i - .5) * .34, mid, .34, label=['H0', 'H1'][i],
                       color=['#6B7280', '#2563EB'][i])
    axes[0].errorbar(x + (i - .5) * .34, mid, yerr=(bands[:, 1] - bands[:, 0]) / 2,
                     fmt='none', color='black', capsize=3)
    axes[0].bar_label(bars, fmt='%.3f', padding=4)
axes[0].set(xticks=x, xticklabels=labels, ylim=(0, 2.65),
            title='Sai số dự báo: thấp hơn là tốt hơn', ylabel='MAE (điểm % C_ref)')
axes[0].legend(frameon=False)
axes[0].spines[['top', 'right']].set_visible(False)
axes[1].axvline(0, color='#6B7280', linewidth=1)
axes[1].axvline(audit['margin_pp'], color='#15803D', linestyle='--', label='Ngưỡng SUPPORT: 0,25')
for i, name in enumerate(names):
    value = sum(audit['PC4'][name]['d_pp']) / 2
    axes[1].scatter(value, i, color=['#B45309', '#B91C1C'][i], s=70, zorder=3)
    axes[1].annotate(f"{value:+.8f}\n{audit['PC4'][name]['verdict']}", (value, i),
                     xytext=(0, 13), textcoords='offset points', ha='center', fontsize=10)
axes[1].set(yticks=x, yticklabels=labels, ylim=(-.5, 1.65), xlim=(-.27, .4),
            xlabel='d = MAE0 − MAE1 (điểm % C_ref)', title='H1 phải hơn đủ mức đã khóa')
axes[1].invert_yaxis()
axes[1].legend(loc='lower right', frameon=False, fontsize=9)
axes[1].spines[['top', 'right']].set_visible(False)
fig.suptitle('L3.7 / A05-T · Kiểm tra lại dữ liệu đã lưu', fontsize=15)
fig.supxlabel('dt chấm 1/240 s; kiểm cặp 1/120 s. Khoảng số là enclosure, không phải CI.', fontsize=9)
for ext in ['png', 'pdf']:
    fig.savefig(OUT / f'results_comparison.{ext}', dpi=180)
print('Created results_comparison.png and results_comparison.pdf from audit.json')
