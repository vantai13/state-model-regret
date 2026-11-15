"""Doan Van Tai — EV-TE descriptive summary after scoring (post-hoc; no verdicts).

Provenance: written by Claude (author delegation 16/11/2026) after the locked score (ae046daa).
Reads only score.json, score_cells.csv, predictions.csv and regimes.json; numpy/stdlib only;
computes nothing that enters H1-H4. Writes results/ext_validity/ev_te/descriptive.json.
Sign convention (locked code): G_S = L(M0_old) - L(M0_new); G_S < 0 means fresh telemetry raised cost.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

OUT = Path('results/ext_validity/ev_te')


def f(x):
    return float(x)


def q(a):
    a = np.asarray(a, float)
    if a.size == 0:
        return None
    return dict(n=int(a.size), min=float(a.min()), q25=float(np.quantile(a, .25)), median=float(np.median(a)),
                q75=float(np.quantile(a, .75)), max=float(a.max()))


def main():
    score = json.loads((OUT / 'score.json').read_text())
    rows = list(csv.DictReader((OUT / 'score_cells.csv').open()))
    preds = {(r['regime'], f(r['tau_mult']), r['twin']): r for r in csv.DictReader((OUT / 'predictions.csv').open())}
    specs = {s['id']: s for s in json.loads((OUT / 'regimes.json').read_text())}
    h30 = {(r['regime'], f(r['tau_mult'])): r for r in rows if f(r['h_mult']) == 30}
    cells = score['cells']
    topo = lambda rid: 'Abilene' if rid.startswith('A') else 'GEANT'
    res = dict(note='post-hoc descriptive; no verdicts; G_S<0 means fresh telemetry raised cost')

    # failures of each hypothesis with the values that decided them
    fails = {}
    for H in ('H1', 'H2', 'H3', 'H4'):
        out = []
        for c in cells:
            if c[f'{H}_eligible'] and not c[f'{H}_pass']:
                r = h30[c['regime'], c['tau_mult']]
                out.append(dict(regime=c['regime'], tau_mult=c['tau_mult'],
                                z_M0=f(r['z_GS_M0']), z_M0_se=f(r['z_GS_M0_se']), pred_M0=f(r['pred_M0_pp']),
                                D_meas=f(r['Delta_M0_meas_pp']), D_se=f(r['Delta_M0_se_pp']),
                                D_pred=f(r['Delta_M0_pred_pp']), DP_meas=f(r['Delta_P_meas_pp']),
                                DP_se=f(r['Delta_P_se_pp'])))
        fails[H] = out
    res['failures'] = fails

    # sign mix among H1-eligible cells
    mix = Counter()
    for c in cells:
        if c['H1_eligible']:
            r = h30[c['regime'], c['tau_mult']]
            mix[f"{topo(c['regime'])}|pred{'+' if f(r['pred_M0_pp']) > 0 else '-'}|z{'+' if f(r['z_GS_M0']) > 0 else '-'}"] += 1
    res['H1_sign_mix'] = dict(sorted(mix.items()))

    # which term binds the H3 tolerance; relative magnitude error
    bind, rel = Counter(), []
    for c in cells:
        if c['H3_eligible']:
            r = h30[c['regime'], c['tau_mult']]
            dm, dp, se = f(r['Delta_M0_meas_pp']), f(r['Delta_M0_pred_pp']), f(r['Delta_M0_se_pp'])
            terms = {'0.25': .25, '0.25|dp|': .25*abs(dp), '2se': 2*se}
            bind[max(terms, key=terms.get)] += 1
            rel.append(abs(dm-dp)/abs(dp))
    res['H3_binding_term'] = dict(bind)
    res['H3_rel_error'] = q(rel)

    # H4 plug-in increment and its se
    res['H4_abs_DeltaP_pp'] = q([abs(f(h30[c['regime'], c['tau_mult']]['Delta_P_meas_pp'])) for c in cells if c['H4_eligible']])
    res['H4_DeltaP_se_pp'] = q([f(h30[c['regime'], c['tau_mult']]['Delta_P_se_pp']) for c in cells if c['H4_eligible']])

    # z at h = 30 T_int by topology, twin and tau (valid cells), plus D1 cells
    zt = defaultdict(list)
    d1 = defaultdict(list)
    for c in cells:
        r = h30[c['regime'], c['tau_mult']]
        for tw in ('M0', 'P', 'CE'):
            key = f"{topo(c['regime'])}|{tw}|tau{c['tau_mult']}"
            (zt if c['stationary_rate_valid'] else d1)[key].append(f(r[f'z_GS_{tw}']))
    res['z_h30_valid'] = {k: q(v) for k, v in sorted(zt.items())}
    res['z_h30_D1'] = {k: q(v) for k, v in sorted(d1.items())}

    # ratio measured / predicted at h30 (M0, H1-eligible)
    res['z_over_pred_M0_h30'] = q([f(h30[c['regime'], c['tau_mult']]['z_GS_M0'])/f(h30[c['regime'], c['tau_mult']]['pred_M0_pp'])
                                   for c in cells if c['H1_eligible']])

    # descriptive harm share (z < -0.1 %) by twin and h, all 244 cells
    harm = {}
    for tw in ('M0', 'P', 'CE'):
        by_h = {}
        for h in sorted({f(r['h_mult']) for r in rows}):
            sel = [r for r in rows if f(r['h_mult']) == h]
            by_h[str(h)] = f"{sum(f(r[f'z_GS_{tw}']) < -.1 for r in sel)}/{len(sel)}"
        harm[tw] = by_h
    res['harm_share_by_h'] = harm

    # slow vs fast, G_M and Gamma at h30 (valid cells)
    sf = defaultdict(list)
    gm, gam = defaultdict(list), defaultdict(list)
    for c in cells:
        if not c['stationary_rate_valid']:
            continue
        r = h30[c['regime'], c['tau_mult']]
        sf[f"{topo(c['regime'])}|slow{c['regime'][-1]}"].append(f(r['z_GS_M0']))
        gm[topo(c['regime'])].append(f(r['z_GM']))
        gam[topo(c['regime'])].append(f(r['z_Gamma']))
    res['z_M0_h30_slow_vs_fast'] = {k: q(v) for k, v in sorted(sf.items())}
    res['z_GM_h30'] = {k: q(v) for k, v in gm.items()}
    res['z_Gamma_h30'] = {k: q(v) for k, v in gam.items()}

    # s sign from training (M0 prediction slope at h30) by topology, valid cells
    ss = Counter()
    for c in cells:
        if c['stationary_rate_valid'] and c['tau_mult'] == 1.0:
            p = preds[c['regime'], 1.0, 'M0']
            ss[f"{topo(c['regime'])}|slope{'+' if f(p['slope_h30']) > 0 else '-'}"] += 1
    res['M0_slope_sign_by_regime'] = dict(ss)
    res['n_regimes'] = dict(Counter(topo(s) for s in specs))

    # per topology pass counts; per regime (all four ages pass)
    per_topo, per_regime = {}, {}
    for H in ('H1', 'H2', 'H3', 'H4'):
        for t in ('Abilene', 'GEANT'):
            e = [c for c in cells if topo(c['regime']) == t and c[f'{H}_eligible']]
            per_topo[f'{H}|{t}'] = f"{sum(c[f'{H}_pass'] for c in e)}/{len(e)}"
        reg = defaultdict(list)
        for c in cells:
            if c[f'{H}_eligible']:
                reg[c['regime']].append(c[f'{H}_pass'])
        per_regime[H] = f"{sum(all(v) for v in reg.values())}/{len(reg)} regimes with every eligible age passing"
    res['pass_by_topology'] = per_topo
    res['pass_by_regime'] = per_regime

    # H4: how each cell passed (strict 0.25 pp clause, or only through the 2 se clause)
    mode = Counter()
    for c in cells:
        if c['H4_eligible']:
            r = h30[c['regime'], c['tau_mult']]
            d, se = abs(f(r['Delta_P_meas_pp'])), f(r['Delta_P_se_pp'])
            mode[f"{topo(c['regime'])}|{'strict<=0.25pp' if d <= .25 else ('only_via_2se' if d <= 2*se else 'fail')}"] += 1
    res['H4_pass_mode'] = dict(sorted(mode.items()))

    # H1 eligible cells: |z|/se (eligibility does not require significance)
    zs = [abs(f(h30[c['regime'], c['tau_mult']]['z_GS_M0']))/f(h30[c['regime'], c['tau_mult']]['z_GS_M0_se'])
          for c in cells if c['H1_eligible']]
    res['H1_abs_z_over_se'] = q(zs) | dict(n_below_2=int(sum(np.asarray(zs) < 2)))

    # effects in % of E_stay (Stay-only cost over the same horizon), valid cells, h = 30 T_int
    est = defaultdict(list)
    for c in cells:
        if not c['stationary_rate_valid']:
            continue
        r = h30[c['regime'], c['tau_mult']]
        E, Cr = f(r['E_stay']), f(r['C_ref'])
        t = topo(c['regime'])
        est[f'{t}|Cref_over_Estay'].append(Cr/E)
        for tw in ('M0', 'P', 'CE'):
            est[f'{t}|GS_{tw}_pct_Estay'].append(100*f(r[f'GS_{tw}'])/E)
        est[f'{t}|abs_DeltaP_pct_Estay'].append(abs(f(r['Delta_P_meas_pp']))*Cr/E)
        est[f'{t}|DeltaP_se_pct_Estay'].append(f(r['Delta_P_se_pp'])*Cr/E)
        est[f'{t}|DeltaM0_pct_Estay'].append(f(r['Delta_M0_meas_pp'])*Cr/E)
    res['h30_in_pct_of_Estay'] = {k: q(v) for k, v in sorted(est.items())}

    (OUT / 'descriptive.json').open('x').write(json.dumps(res, indent=1) + '\n')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
