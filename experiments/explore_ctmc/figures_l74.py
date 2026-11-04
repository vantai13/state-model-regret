"""Doan Van Tai — L7.4 figures from saved results only (no evaluator call) [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.figures_l74      # -> results/explore_ctmc/figures_l74/F1..F6.png + figure_data.csv

Each figure carries exactly one claim of notes/synthesis/CLAIMS_EVIDENCE.md. Palette: first three categorical slots of
the dataviz reference palette (validated all-pairs, light mode); aqua is below 3:1 contrast, so every series also has its
own marker shape and a legend, and the plotted rows are written to figure_data.csv (table view).
"""
from fractions import Fraction as F
import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from experiments.explore_ctmc import check_l72, check_l73

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
DEST = OUT / 'figures_l74'
C = ['#2a78d6', '#eb6834', '#1baf7a']
MK = ['o', 's', '^']
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def style(ax, title, xlabel, ylabel):
    ax.set_title(title, color=INK, fontsize=10, loc='left')
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, color=GRID, lw=0.6)
    for s in ax.spines.values():
        s.set_color(GRID)


def a6_rows():
    """L7.1 asym truth (a = 6) merged with its frozen zero fit (z_pred1 with the decisions at h)."""
    recs = []
    for f in sorted(glob.glob(str(OUT / 'runs/asym/*.json'))):
        t = json.loads(Path(f).read_text())
        m = json.loads((OUT / 'm0/asym' / Path(f).name).read_text())
        mh = {r['h']: r for r in m['h']}
        for r in t['h']:
            z = mh.get(r['h'], {})
            recs.append(dict(source='a=6 (L7.1)', id=t['id'], h_Tint=r['h_Tint'], h_kappa=r['h_kappa'], G_S=r['G_S'],
                             z_pred1=z.get('z_pred_first_order'), z_inf=t['asymptotic']['z_inf'],
                             reg_static=r['regret']['static'], delta=t['delta']))
    return pd.DataFrame(recs)


def l72_rows():
    out = []
    for tag, lab in (('a3', 'a=3 (L7.2)'), ('a7p5', 'a=7.5 (L7.2)')):
        m = check_l72.load(tag)
        m = m[m.done & m.set.isin(['asym', 'sobol'])]
        out.append(pd.DataFrame(dict(source=lab, id=m.id, h_Tint=m.h_Tint, G_S=m.G_S, z_pred1=m.z_pred1,
                                     reg_static=m.reg_static, delta=m.delta)))
    return pd.concat(out)


def l73_rows():
    m = check_l73.load()
    m = m[m.done & m.stage.isin(['asym', 'sobol'])]
    return pd.DataFrame(dict(source='two-scale (L7.3)', id=m.id, h_Tint=m.h_Tint, G_S=m.G_S, z_pred1=m.z_pred1,
                             reg_static=m.reg_static, delta=m.delta, ratio=m.ratio))


def fig1(rows, data):
    """C1: |G_S - z_pred1| at the same h against h/T_int; 0.1 pp line; onset band 4-7 T_int."""
    fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=150)
    for k, (lab, g) in enumerate(rows.groupby('group', sort=False)):
        g = g[g.z_pred1.notna() & (g.h_Tint > 0)]
        err = (g.G_S - g.z_pred1).abs().clip(lower=1e-6)
        ax.scatter(g.h_Tint, err, s=10, c=C[k], marker=MK[k], alpha=0.55, lw=0, label=f'{lab} (n={len(g)})')
        data.append(pd.DataFrame(dict(figure='F1', group=lab, h_Tint=g.h_Tint, y=err)))
    ax.axhline(0.1, color=INK2, lw=1, ls='--')
    ax.axvspan(4, 7, color=GRID, alpha=0.5, lw=0)
    ax.text(4.2, 3e-6, 'onset 4–7·T_int', color=INK2, fontsize=8)
    ax.text(0.02, 0.13, '0,1 pp', color=INK2, fontsize=8)
    ax.set_xscale('log'), ax.set_yscale('log')
    style(ax, 'F1 · C1: sai số của công thức bậc một zero-fit ở cùng h', 'h / T_int', '|G_S − z_pred1| (pp)')
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig(DEST / 'F1_onset.png')
    plt.close(fig)


def fig2(rows, data):
    """C2: regret of the stationary planner (Static) against h/T_int, delta != 0."""
    fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=150)
    for k, (lab, g) in enumerate(rows.groupby('group', sort=False)):
        g = g[(g.delta != 0) & (g.h_Tint > 0)]
        y = g.reg_static.clip(lower=1e-5)
        ax.scatter(g.h_Tint, y, s=10, c=C[k], marker=MK[k], alpha=0.55, lw=0, label=f'{lab} (n={len(g)})')
        data.append(pd.DataFrame(dict(figure='F2', group=lab, h_Tint=g.h_Tint, y=y)))
    ax.axhline(0.1, color=INK2, lw=1, ls='--')
    ax.axvline(7, color=INK2, lw=1, ls=':')
    ax.text(7.5, 30, 'h = 7·T_int', color=INK2, fontsize=8)
    ax.set_xscale('log'), ax.set_yscale('log')
    style(ax, 'F2 · C2: planner dừng (Static) đủ dùng ở horizon dài', 'h / T_int', 'regret Static (% C_ref; 1e−5 = 0)')
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig(DEST / 'F2_static.png')
    plt.close(fig)


def fig3(data):
    """C3: zero-fit z_inf along the x slices (kappa = 1/5), three amplitudes; help band where z_inf > 0."""
    fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=150)
    files = [('a=3', OUT / 'l72/ZEROFIT_a3.csv', 'zf_a3_xs'), ('a=6', OUT / 'l72/ZEROFIT_a6_xs.csv', 'zf_a6_xs'),
             ('a=7.5', OUT / 'l72/ZEROFIT_a7p5.csv', 'zf_a7p5_xs')]
    for k, (lab, path, stage) in enumerate(files):
        z = pd.read_csv(path)
        z = z[(z.stage == stage) & (z.status == 'COMPLETED') & np.isclose(z.kappa, 0.2) & np.isclose(z.u, 1.0 if lab != 'a=7.5' else 1.0)]
        z = z.drop_duplicates('id').sort_values('x')
        ax.plot(z.x, z.z_inf, color=C[k], lw=2, marker=MK[k], ms=3, label=f'{lab}, u = 1, λA = {z.lamA.iloc[0]:g}')
        data.append(pd.DataFrame(dict(figure='F3', group=lab, x=z.x, y=z.z_inf)))
    ax.axhline(0, color=INK2, lw=1)
    ax.set_ylim(-8, 3)
    ax.text(1.25, -7.6, 'trục y cắt ở −8 (đuôi tới −150)', color=INK2, fontsize=7)
    style(ax, 'F3 · C3: dải giúp hẹp quanh 0 < x < x* (zero-fit, κ = 1/5, h = ∞)', 'x = (λB − λA)/u', 'z_∞ = G_S (% C_ref)')
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig(DEST / 'F3_band.png')
    plt.close(fig)


def fig4(data):
    """C4: backlog-only part of the harm, F / G_S on harm rows (truth, a = 6), against kappa."""
    recs = []
    for f in glob.glob(str(OUT / 'runs_d22/*/*.json')):
        d = json.loads(Path(f).read_text())
        if d.get('status') != 'COMPLETED':
            continue
        kappa = float(F(d['parameters'][3]))
        for r in d['h']:
            if 'd22' in r and r['G_S'] < -0.5:
                recs.append(dict(kappa=kappa, share=r['d22']['F'] / r['G_S'], h_Tint=r['h_Tint']))
    df = pd.DataFrame(recs)
    fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=150)
    ax.scatter(df.kappa, df.share, s=8, c=C[0], marker=MK[0], alpha=0.35, lw=0, label=f'dòng harm, G_S < −0,5% (n={len(df)})')
    bins = np.logspace(np.log10(df.kappa.min()), np.log10(df.kappa.max()), 9)
    mid, med = [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        g = df[(df.kappa >= lo) & (df.kappa < hi)]
        if len(g) >= 10:
            mid.append(np.sqrt(lo * hi)), med.append(g.share.median())
    ax.plot(mid, med, color=C[1], lw=2, marker=MK[1], ms=4, label='trung vị theo khoảng κ')
    data.append(pd.DataFrame(dict(figure='F4', group='harm rows', x=df.kappa, y=df.share)))
    ax.set_xscale('log')
    style(ax, 'F4 · C4: phần harm do backlog (không cần mode), a = 6', 'κ (s)', 'F / G_S (phần backlog)')
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig(DEST / 'F4_backlog.png')
    plt.close(fig)


def fig5(data):
    """C5: share of states where M0 picks the long-run action, old vs fresh state, harm vs help rows (h >= 4 T_int,
    delta != 0). All a = 6 ctmc-v1 truth rows (runs/, runs_ko/, runs_d22/), one row per (parameters, h), from the
    Switch shares as in SUMMARY section 11A."""
    seen = {}
    for f in glob.glob(str(OUT / 'runs/*/*.json')) + glob.glob(str(OUT / 'runs_ko/*/*.json')) + glob.glob(str(OUT / 'runs_d22/*/*.json')):
        d = json.loads(Path(f).read_text())
        if d.get('status') != 'COMPLETED' or d.get('namespace') != 'ctmc-v1' or d['delta'] == 0 or float(d.get('a', 6)) != 6:
            continue
        ok = (lambda v: v) if d['s'] < 0 else (lambda v: 1 - v)
        for r in d['h']:
            seen[(tuple(d['parameters']), r['h'])] = (r['h_Tint'], r['G_S'], ok(r['shares']['M0_old']), ok(r['shares']['M0_new']))
    recs = [dict(cls='harm' if g < -0.1 else 'help', old=o, new=n) for (t, g, o, n) in seen.values()
            if t >= 4 and abs(g) > 0.1]
    df = pd.DataFrame(recs)
    fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=150)
    for k, cls in enumerate(('harm', 'help')):
        g = df[df.cls == cls]
        ax.scatter(g.old, g.new, s=12, c=C[k], marker=MK[k], alpha=0.6, lw=0,
                   label=f'{cls}: trung vị cũ {g.old.median():.2f}, mới {g.new.median():.2f} (n={len(g)})')
        data.append(pd.DataFrame(dict(figure='F5', group=cls, x=g.old, y=g.new)))
    ax.plot([0, 1], [0, 1], color=INK2, lw=1, ls='--')
    style(ax, 'F5 · C5: M0 với state cũ "đúng nhờ lấy trung bình" (h > 4·T_int, δ ≠ 0)',
          'tỷ lệ state M0 chọn action dài hạn — state cũ', '— state mới')
    ax.legend(fontsize=7, frameon=False, loc='upper left')
    fig.tight_layout()
    fig.savefig(DEST / 'F5_planner.png')
    plt.close(fig)


def fig6(a6, data):
    """C6: two clocks, |z - z_inf|/|z_inf| (|z_inf| >= 0.5, as AS-R4) against h/T_int and h/kappa, Spearman rho."""
    from scipy.stats import spearmanr
    g = a6[(a6.h_Tint > 0) & (a6.z_inf.abs() >= 0.5)].copy()          # the AS-R4 quantity and rows (check_asymptote)
    g['dev'] = ((g.G_S - g.z_inf).abs() / g.z_inf.abs()).clip(lower=1e-6)
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.4), dpi=150, sharey=True)
    for k, (ax, col, lab) in enumerate(zip(axs, ('h_Tint', 'h_kappa'), ('h / T_int', 'h / κ'))):
        rho = spearmanr(g[col], g.dev).statistic
        ax.scatter(g[col], g.dev, s=10, c=C[k], marker=MK[k], alpha=0.6, lw=0, label=f'Spearman ρ = {rho:.2f} (n={len(g)})')
        ax.set_xscale('log'), ax.set_yscale('log')
        style(ax, f'F6 · C6: đồng hồ {lab}', lab, '|z − z_∞| / |z_∞|' if k == 0 else '')
        ax.legend(fontsize=7, frameon=False, loc='lower left')
        data.append(pd.DataFrame(dict(figure='F6', group=lab, x=g[col], y=g.dev)))
    fig.tight_layout()
    fig.savefig(DEST / 'F6_clocks.png')
    plt.close(fig)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    a6 = a6_rows()
    l72, l73 = l72_rows(), l73_rows()
    rows = pd.concat([a6.assign(group='a = 6 (L7.1)'),
                      l72.assign(group=np.where(l72.source.str.startswith('a=3'), 'a = 3 (L7.2)', 'a = 7,5 (L7.2)')),
                      l73.assign(group='hai thang (L7.3)')])
    rows13 = rows[rows.group.isin(['a = 6 (L7.1)', 'a = 3 (L7.2)', 'hai thang (L7.3)'])]
    data = []
    fig1(rows13, data)
    fig2(rows13, data)
    fig3(data)
    fig4(data)
    fig5(data)
    fig6(a6, data)
    pd.concat(data).to_csv(DEST / 'figure_data.csv', index=False)
    print('wrote', sorted(p.name for p in DEST.glob('*.png')))


if __name__ == '__main__':
    main()
