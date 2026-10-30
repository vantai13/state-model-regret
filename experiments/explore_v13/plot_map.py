"""Doan Van Tai — regime-map figures from saved regimes.csv files [EXPLORATION ONLY].

AI (Claude) theo ủy quyền. Encoding: 3 validated categorical hues (all-pairs, light mode) for
STATE_DOM / STATE_HARM / MODEL_DOM, dark ink for BOTH, light gray for NEITHER; every class also has
its own marker shape so identity is never color-only. A CSV table view is written next to the PNGs.
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from fractions import Fraction as F

from experiments.explore_v13.regime_map import EPS, ORDER, load
from experiments.explore_v13.scan import inside_frozen_cards

COORDS = ('lambdaA', 'lambdaB', 'kappa', 'eta', 'h', 'age', 'amp')

STYLE = {
    'STATE_DOM': dict(color='#2a78d6', marker='o', label='State thắng (Ḡ_S ≥ 1%, Ḡ_M < 1%)'),
    'MODEL_DOM': dict(color='#1baf7a', marker='s', label='Model thắng (Ḡ_M ≥ 1%, Ḡ_S < 1%)'),
    'BOTH': dict(color='#2b2b2b', marker='D', label='Cả hai ≥ 1%'),
    'JOINT': dict(color='#8c8b86', marker='P', label='Cộng hưởng (G_SM ≥ 1%, Γ̄ ≥ max(Ḡ_S, Ḡ_M))'),
    'STATE_HARM': dict(color='#eb6834', marker='v', label='State gây hại (Ḡ_S ≤ −1%)'),
    'NEITHER': dict(color='#c9c8c2', marker='.', label='Không đáng kể'),
}
INK, MUTED, SURFACE = '#0b0b0b', '#52514e', '#fcfcfb'


def axes_style(ax):
    ax.set_facecolor(SURFACE)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(color='#e6e5e0', linewidth=0.6)
    ax.set_axisbelow(True)


def unique(rows):
    """One row per regime coordinate (pilot stages re-ran some points); tag card-box regimes."""
    seen, out = set(), []
    for r in rows:
        k = tuple(str(F(r[c]).limit_denominator(1000)) for c in COORDS)
        if k not in seen:
            seen.add(k)
            r['in_card'] = inside_frozen_cards(*k[:5])   # card boxes ignore age/amp: conservative
            out.append(r)
    return out


def scatter(ax, rows, xkey, ykey):
    for cls in reversed(ORDER):  # NEITHER drawn first, underneath
        pts = [r for r in rows if r['class'] == cls]
        if not pts:
            continue
        st = STYLE[cls]
        for hollow in (False, True):
            sub = [r for r in pts if r['in_card'] == hollow]
            if not sub:
                continue
            ax.scatter([r[xkey] for r in sub], [r[ykey] for r in sub], s=10 if cls == 'NEITHER' else 30,
                       c='none' if hollow else st['color'], marker=st['marker'],
                       edgecolors=st['color'] if hollow else SURFACE, linewidths=0.9 if hollow else 0.6,
                       label=None if hollow else f"{st['label']} · {len(pts)}",
                       zorder=3 if cls != 'NEITHER' else 2)
    ax.scatter([], [], s=30, c='none', marker='o', edgecolors=MUTED, linewidths=0.9,
               label='Rỗng = regime pilot nằm trong hộp card Phase 3R (đã lộ)')


LEFT = {'XM2X077'}   # label to the left where the right edge is crowded


def annotate(ax, rows, ids, xkey, ykey):
    for r in rows:
        if r['id'] in ids:
            left = r['id'] in LEFT
            ax.annotate(r['id'], (r[xkey], r[ykey]), xytext=(-6 if left else 6, 4), textcoords='offset points',
                        ha='right' if left else 'left', fontsize=7, color=INK)


LABELLED = {'XM1222', 'XA087', 'XM2X077', 'XM2X041', 'XM2S069', 'XM2S310'}


def legend_below(fig, ax):
    handles, labels = ax.get_legend_handles_labels()
    rank = {STYLE[c]['label']: i for i, c in enumerate(ORDER)}
    pairs = sorted(zip(handles, labels), key=lambda hl: rank.get(hl[1].split(' · ')[0], len(ORDER)))
    fig.legend(*zip(*pairs), fontsize=7, frameon=False, loc='lower left', ncol=2, labelcolor=INK,
               bbox_to_anchor=(0.06, 0.0))


def new_figure():
    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    axes_style(ax)
    return fig, ax


def finish(fig, ax, path):
    legend_below(fig, ax)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main(out_dir, *paths):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = unique(load(paths))

    fig, ax = new_figure()
    scatter(ax, rows, 'G_S_pctC', 'G_M_pctC')
    ax.set_xscale('symlog', linthresh=1)
    ax.set_yscale('symlog', linthresh=1)
    for v in (-EPS, EPS):
        ax.axvline(v, color=MUTED, linewidth=0.8, linestyle='--', zorder=1)
    ax.axhline(EPS, color=MUTED, linewidth=0.8, linestyle='--', zorder=1)
    region = dict(fontsize=8, color=MUTED, fontweight='bold', transform=ax.transAxes)
    ax.text(0.995, 0.22, 'A · STATE-\nDOMINANT', ha='right', **region)
    ax.text(0.60, 0.97, 'B · MODEL-DOMINANT', ha='center', va='top', **region)
    ax.text(0.995, 0.62, 'AB · BOTH', ha='right', va='top', **region)
    ax.text(0.01, 0.97, 'C · STATE-HARM', ha='left', va='top', **region)
    ax.text(0.47, 0.36, 'D · NEITHER\n(+ = cộng hưởng J)', ha='center', **region)
    ax.set_xlabel('Ḡ_S: lợi ích sửa state khi model vẫn là M0 (% C̄_ref)', color=INK, fontsize=9)
    ax.set_ylabel('Ḡ_M: lợi ích sửa model khi state vẫn cũ (% C̄_ref)', color=INK, fontsize=9)
    ax.set_title('Bản đồ regime: repair nào đáng làm (đường đứt = ±ε_R = 1%, trục symlog)',
                 color=INK, fontsize=10, loc='left')
    annotate(ax, rows, LABELLED, 'G_S_pctC', 'G_M_pctC')
    finish(fig, ax, out / 'regime_map_differ.png')

    fig, ax = new_figure()
    scatter(ax, rows, 'G_S_M1_pctC', 'G_M_S1_pctC')
    ax.set_xscale('symlog', linthresh=0.1, linscale=0.5)
    ax.set_yscale('symlog', linthresh=0.1, linscale=0.5)
    ax.axline((1, 1), (10, 10), color=MUTED, linewidth=0.8, linestyle=':', zorder=1)
    ax.set_xlabel('Ḡ_S|M1: giá trị state hiện tại khi model đúng (% C̄_ref)', color=INK, fontsize=9)
    ax.set_ylabel('Ḡ_M|S1: giá trị model đúng khi đã biết state (% C̄_ref)', color=INK, fontsize=9)
    ax.set_title('Bản đồ cơ chế: mỗi repair đo khi repair kia đã hoàn hảo (đường chấm: hai giá trị bằng nhau)',
                 color=INK, fontsize=10, loc='left')
    annotate(ax, rows, LABELLED, 'G_S_M1_pctC', 'G_M_S1_pctC')
    finish(fig, ax, out / 'regime_map_mechanism.png')

    keys = ['id', 'source', 'class', 'lambdaA', 'lambdaB', 'kappa', 'eta', 'h', 'age', 'amp', 'G_S_pctC', 'G_M_pctC',
            'Gamma_pctC', 'G_SM_pctC', 'G_S_M1_pctC', 'G_M_S1_pctC', 'G_S_pctS', 'G_M_pctS', 'P_flip',
            'P_wrong_ranking', 'in_card']
    with open(out / 'regime_map_table.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (ORDER.index(r['class']), -abs(r['G_S_pctC']) - r['G_M_pctC'])))


def composition(out_dir, path):
    """Class shares along each design axis, factorial grid only (a focused grid would bias shares)."""
    rows = unique(load([path]))
    axes_keys = [('kappa', 'κ (tốc độ đổi mode)'), ('eta', 'η (biên độ nền)'), ('h', 'h (horizon, s)'),
                 ('lambdaA', 'λA'), ('lambdaB', 'λB')]
    fig, axs = plt.subplots(1, len(axes_keys), figsize=(11, 3.6), dpi=160, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    for ax, (key, title) in zip(axs, axes_keys):
        axes_style(ax)
        ax.grid(False)
        levels = sorted({r[key] for r in rows})
        for i, lv in enumerate(levels):
            sub = [r for r in rows if r[key] == lv]
            bottom = 0.0
            for cls in ORDER:
                share = sum(r['class'] == cls for r in sub) / len(sub)
                if share:
                    ax.bar(i, share, bottom=bottom, width=0.7, color=STYLE[cls]['color'],
                           edgecolor=SURFACE, linewidth=1.0, label=STYLE[cls]['label'] if i == 0 else None)
                bottom += share
            ax.text(i, 1.02, f'n={len(sub)}', ha='center', fontsize=6, color=MUTED)
        ax.set_xticks(range(len(levels)), [f'{F(lv).limit_denominator(100)}' for lv in levels])
        ax.set_title(title, color=INK, fontsize=9, loc='left')
        ax.set_ylim(0, 1.08)
    axs[0].set_ylabel('tỷ lệ regime trong lưới map1', color=INK, fontsize=8)
    handles = {}
    for ax in axs:
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(l, h)
    labels = [STYLE[c]['label'] for c in ORDER if STYLE[c]['label'] in handles]
    fig.legend([handles[l] for l in labels], labels, fontsize=7, frameon=False, loc='lower center',
               ncol=len(labels), labelcolor=INK)
    fig.suptitle('Nhóm regime theo từng trục thiết kế (map1: lưới đủ tổ hợp ngoài hộp card, c_sw = 0)',
                 color=INK, fontsize=10, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(Path(out_dir) / 'regime_composition_map1.png', facecolor=SURFACE)
    plt.close(fig)


CODE = {'STATE_DOM': 'A', 'MODEL_DOM': 'B', 'BOTH': 'AB', 'JOINT': 'J', 'STATE_HARM': 'C', 'NEITHER': 'D'}
TEXT_ON = {'STATE_DOM': SURFACE, 'MODEL_DOM': INK, 'BOTH': SURFACE, 'JOINT': INK, 'STATE_HARM': SURFACE, 'NEITHER': MUTED}
PAIRS = [(6.5, 7.0), (7.5, 8.0), (6.5, 8.0)]
KAPPAS = [0.1, 0.3, 1.0]
ROWS = [(h, e) for h in (2.0, 4.0, 8.0) for e in (0.5, 0.75)]


def design_map(out_dir, axis, levels, fixed, name, title, *paths):
    """Tile map in design coordinates: x = axis (age or amp), y = h x eta; panels = (lamA, lamB) x kappa.
    Missing combinations (not run, unstable or outside the family) stay blank."""
    rows = unique(load(paths))
    cell = {}
    for r in rows:
        if all(abs(r[k] - v) < 1e-9 for k, v in fixed.items()) and r['c_sw'] == 0:
            cell[(r['lambdaA'], r['lambdaB'], r['kappa'], r['h'], r['eta'], r[axis])] = r
    fig, axs = plt.subplots(len(PAIRS), len(KAPPAS), figsize=(10, 9.2), dpi=160, sharex=True, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    for i, (a, b) in enumerate(PAIRS):
        for j, k in enumerate(KAPPAS):
            ax = axs[i][j]
            ax.set_facecolor(SURFACE)
            for side in ax.spines.values():
                side.set_visible(False)
            for x, lv in enumerate(levels):
                for y, (h, e) in enumerate(ROWS):
                    r = cell.get((a, b, k, h, e, lv))
                    if r is None:
                        continue
                    cls = r['class']
                    ax.add_patch(plt.Rectangle((x - .46, y - .46), .92, .92, color=STYLE[cls]['color'], linewidth=0))
                    ax.text(x, y + .12, CODE[cls], ha='center', va='center', fontsize=7, fontweight='bold',
                            color=TEXT_ON[cls])
                    ax.text(x, y - .22, f"{r['G_S_pctC']:+.1f}/{r['G_M_pctC']:.1f}", ha='center', va='center',
                            fontsize=4.6, color=TEXT_ON[cls])
            ax.set_xlim(-.5, len(levels) - .5)
            ax.set_ylim(-.5, len(ROWS) - .5)
            ax.set_xticks(range(len(levels)), [f'{F(lv).limit_denominator(8)}' for lv in levels], fontsize=7, color=MUTED)
            ax.set_yticks(range(len(ROWS)), [f'h{int(h)} η{F(e).limit_denominator(4)}' for h, e in ROWS], fontsize=7,
                          color=MUTED)
            ax.tick_params(length=0)
            ax.set_title(f'λA {a:g}, λB {b:g}, κ {k:g}', fontsize=8, color=INK, loc='left')
            if i == len(PAIRS) - 1:
                ax.set_xlabel(axis + (' (s)' if axis == 'age' else ' (±packet/s)'), fontsize=8, color=INK)
    handles = [plt.Rectangle((0, 0), 1, 1, color=STYLE[c]['color']) for c in ORDER]
    fig.legend(handles, [f"{CODE[c]} · {STYLE[c]['label']}" for c in ORDER], fontsize=7, frameon=False,
               loc='lower center', ncol=3, labelcolor=INK)
    fig.suptitle(title + '  (số trong ô: Ḡ_S / Ḡ_M, % C̄_ref)', color=INK, fontsize=10, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    fig.savefig(Path(out_dir) / name, facecolor=SURFACE)
    plt.close(fig)


if __name__ == '__main__':
    if sys.argv[1] == '--composition':
        composition(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == '--age':
        design_map(sys.argv[2], 'age', [0.25, 0.5, 1.0, 2.0, 4.0], {'amp': 6.0}, 'regime_design_age.png',
                   'Bản đồ thiết kế: age (độ cũ của quan sát) × h, η', *sys.argv[3:])
    elif sys.argv[1] == '--amp':
        design_map(sys.argv[2], 'amp', [4.0, 5.0, 6.0, 7.0], {'age': 1.0}, 'regime_design_amp.png',
                   'Bản đồ thiết kế: biên độ nền ON/OFF × h, η (age 1 s)', *sys.argv[3:])
    else:
        main(sys.argv[1], *sys.argv[2:])
