"""Doan Van Tai — I_Delta round 3 [EXPLORATION ONLY; AI (Claude) theo ủy quyền 14/11/2026: "tiếp tục đi"].

(a) Help band: is the share of Gamma reproduced by a constant-bias (threshold-only) model governed by the threshold
    proximity T_prox = E|e~| / E|Delta + b| (state-dependent error relative to the additive model's distance to the
    decision threshold) rather than by kappa_add = |b| / sqrt(E e^2)? Fresh ctmc-v1 regimes, band-heavy.
(b) Fluid transfer retest with the short level moved to h = 2 s (round 2: Gamma too small at h = 1/2 s).

Card: results/explore_ctmc/idelta/CARD_IDELTA3.md, locked in lock_idelta3.json (run refuses otherwise).
    python -m experiments.explore_ctmc.idelta3 design
    python -m experiments.explore_ctmc.idelta3 calibrate --workers N     # run01/run02 regimes + run02 fluid points
    python -m experiments.explore_ctmc.idelta3 run --out DIR             # GCP, after env.sh and the lock
    python -m experiments.explore_ctmc.idelta3 score --out DIR
"""
import argparse
import hashlib
import json
import math
import multiprocessing
import os
import resource
import signal
import statistics as st
import time
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.stats import qmc, spearmanr

from experiments.explore_ctmc import ctmc as C
from experiments.explore_ctmc import idelta as D1
from experiments.explore_ctmc import idelta2 as D2
from experiments.explore_ctmc import design_l75 as L75
from experiments.explore_ctmc import tau as T5
from experiments.explore_ctmc.design import rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/idelta'
CASES = OUT / 'cases_r3.json'
POINTS = OUT / 'fluid_points_r3.json'
CARD = OUT / 'CARD_IDELTA3.md'
LOCK = OUT / 'lock_idelta3.json'
CALIB = OUT / 'calibration_idelta3.json'
SEED = 20261115
COUNTS = dict(neg=10, band=20, pos=10)
FLUID_H = (F(2), F(8), F(32))
N_FLUID = 64
GMIN = D2.GMIN


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def e_abs_pair(wa, a, wb, b):
    """E|a_i + b_j| under wa x wb (exact, sort + cumulative sums)."""
    return float(wa @ a + wb @ b) - 2 * C.pair_sum(wa, a, a, wb, b, b, 0.0)[1]


# ------------------------------------------------------------------------------------------------------ CTMC

def light_regime(case):
    """Gamma, constant-bias counterfactuals, kappa_add and threshold proximity at the four horizons, from the engine
    arrays only (no joint J, no boundary terms)."""
    t0 = time.process_time()
    lamA, lamB, u, kappa, c = (F(x) for x in case['parameters'])
    hs = [F(h) for h in case['hs'][:4]]
    ev = C.evaluate(lamA, lamB, u, kappa, hs, c=c, disagree=False, arrays=True)
    ar = ev.pop('_arrays')
    Ast, Bst = C.chain(lamA + u, kappa, ar['NA']), C.chain(lamB, kappa, ar['NB'])
    wA, wB = Ast.pi, Bst.pi
    pA, pB = wA.reshape(-1, 2).sum(axis=1), wB.reshape(-1, 2).sum(axis=1)
    cf = float(c)
    rows = []
    for k, h in enumerate(hs):
        er = ev['h'][k]
        Cref, scale = er['Cref'], er['E_stay']
        pct = lambda x: 100 * x / Cref
        dA, dhA, dAo, dhAo = ar['dA'][k], ar['dhA'][k], ar['dAo'][k], ar['dhAo'][k]
        dB, dhB, dBo, dhBo = ar['dB'][k], ar['dhB'][k], ar['dBo'][k], ar['dhBo'][k]
        eA, eB = dhA - dA, dhB - dB
        bA, bB = float(wA @ eA), float(wB @ eB)
        b = bA + bB
        varA, varB = float(wA @ (eA - bA) ** 2), float(wB @ (eB - bB) ** 2)
        tol = 1e-12 * (scale + 1)
        fresh = lambda kA, kB: C.pair_sum(wA, kA, dA, wB, kB, dB, cf, tol)[1]
        stale = lambda kA, kB: C.pair_sum(pA, kA, dAo, pB, kB, dBo, cf, tol)[1]
        G11, G10, G01, G00 = fresh(dA, dB), fresh(dhA, dhB), stale(dAo, dBo), stale(dhAo, dhBo)
        gam = lambda g10, g00: pct(g10 + G01 - g00 - G11)
        # threshold proximity: residual state-dependent error vs the additive model's distance to the threshold
        thr_f = e_abs_pair(wA, dA + bA, wB, dB + bB + cf)
        res_f = e_abs_pair(wA, eA - bA, wB, eB - bB)
        eAo, eBo = dhAo - dAo, dhBo - dBo
        thr_s = e_abs_pair(pA, dAo + bA, pB, dBo + bB + cf)
        res_s = e_abs_pair(pA, eAo - bA, pB, eBo - bB)
        # additivity of the TRUE gap: |E Delta| / sqrt(E Delta^2) under pi x pi (pass 2 of the calibration)
        mA, mB = float(wA @ dA), float(wB @ dB)
        mD = mA + mB + cf
        vD = float(wA @ (dA - mA) ** 2) + float(wB @ (dB - mB) ** 2)
        rows.append(dict(kappa_delta=abs(mD) / math.sqrt(mD * mD + vD) if mD * mD + vD > 0 else None,h=str(h), h_Tint=er['h_Tint'], Cref=Cref, Gamma=er['Gamma'], Gamma_self=gam(G10, G00),
                         Gamma_add=gam(fresh(dA + bA, dB + bB), stale(dAo + bA, dBo + bB)),
                         G_S=er['G_S'], G_M=er['G_M'], bias_pct=pct(b),
                         kappa_add=abs(b) / math.sqrt(b * b + varA + varB) if b * b + varA + varB > 0 else None,
                         T_fresh=res_f / thr_f if thr_f > 0 else None, T_stale=res_s / thr_s if thr_s > 0 else None,
                         thr_fresh_pct=pct(thr_f), res_fresh_pct=pct(res_f)))
    return dict(id=case['id'], status='COMPLETED', stratum=case['tags']['stratum'], x=case['x'],
                parameters=case['parameters'], rows=rows, cpu=time.process_time() - t0)


# ------------------------------------------------------------------------------------------------------ fluid

def fluid_point(p, hs=FLUID_H, ref=D2.FLUID_REF):
    """Round-2 fluid cell read-outs plus the threshold proximity inside the cell (S0 is one action per cell, so only
    the fresh-state proximity is defined)."""
    from experiments.A00_engine.physical import side_table
    from experiments.A00_engine.evaluate import evaluate_sides
    from experiments.A00_engine.factorial_core import _cut_sum
    k, lam, eta = F(p['kappa']), F(p['lamA']), F(p['eta'])
    out = []
    for h in hs:
        t0 = time.process_time()
        cell = dict(id=f"TOY_IDELTA3_{p['id']}", role='toy', origin='idelta3-toy', kappa=k, eta=eta, u=2 * eta, age=F(1),
                    yA=F(p['yA']), yB=F(p['yB']), h=F(h), H_coarse=int(120 * F(h)), ratesA=(lam - 6, lam + 6),
                    ratesB=(F(2), F(14)), lambdaA=lam)
        A, _ = side_table(cell, 'A', ref)
        B, _ = side_table(cell, 'B', ref)
        r = evaluate_sides(A, B, refinement=ref, dt=F(1, 120 * ref))
        pa, pb = (np.array(s.p, dtype=float) for s in (A, B))
        dA, dhA, dB, dhB = (np.array(v, dtype=float) for v in (A.d, A.dh, B.d, B.dh))
        eA, eB = dhA - dA, dhB - dB
        bA, bB = float(pa @ eA), float(pb @ eB)
        b = bA + bB
        varA, varB = float(pa @ (eA - bA) ** 2), float(pb @ (eB - bB) ** 2)
        L = {key: float(v) for key, v in r['L'].items()}
        K = float(pa @ np.array(A.jst, dtype=float) + pb @ np.array(B.jst, dtype=float))
        cref = L['11']
        cut = lambda a, va, bb, vb: float(_cut_sum(tuple(a), tuple(va), tuple(pa), tuple(bb), tuple(vb), tuple(pb))[1])
        gam = lambda L10: 100 * (L10 + L['01'] - L['00'] - L['11']) / cref
        eabs = lambda a, bb: float(pa @ a + pb @ bb) - 2 * cut(a, a, bb, bb)
        thr, res = eabs(dA + bA, dB + bB), eabs(eA - bA, eB - bB)
        mA, mB = float(pa @ dA), float(pb @ dB)
        vD = float(pa @ (dA - mA) ** 2) + float(pb @ (dB - mB) ** 2)
        out.append(dict(kappa_delta=abs(mA + mB) / math.sqrt((mA + mB) ** 2 + vD) if (mA + mB) ** 2 + vD > 0 else None,id=p['id'], h=str(h), status=r['status'], Cref=cref, Gamma=gam(L['10']),
                        Gamma_engine=100 * float(r['G']['Gamma']) / cref, Gamma_add=gam(K + cut(dA + bA, dA, dB + bB, dB)),
                        EabsI_pct=100 * float(r['E_abs_I_delta']) / cref, bias_pct=100 * b / cref,
                        kappa_add=abs(b) / math.sqrt(b * b + varA + varB) if b * b + varA + varB > 0 else None,
                        T_fresh=res / thr if thr > 0 else None, cpu=time.process_time() - t0))
    return dict(id=p['id'], status='COMPLETED', rows=out)


# ------------------------------------------------------------------------------------------------------ design

def design():
    for path in (CASES, POINTS):
        if path.exists():
            raise FileExistsError(f'{path} is write-once')
    seen = D2.seen_all()
    seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads(D2.CASES.read_text())}
    n_seen = len(seen)
    cases, report = [], {}
    for k, (name, (lo, hi)) in enumerate(L75.STRATA.items()):
        pts = qmc.Sobol(4, scramble=True, seed=SEED + k).random(2048)
        acc, drop = [], dict(domain=0, seen=0, cost=0)
        for j, (pu, pa, px, pk) in enumerate(pts):
            if len(acc) >= COUNTS[name]:
                break
            u = F(1, 4) * (1 + int(pu * 12))
            steps = int((F(10) - u - 6) * 4)
            if steps < 1:
                drop['domain'] += 1
                continue
            lamA = 6 + F(int(pa * steps), 4)
            x = F(round(float(lo + (hi - lo) * F(px)) * 100), 100)
            lamB = lamA + x * u
            if not (lamB >= 6 and lamB + u < 10 and x != 0):
                drop['domain'] += 1
                continue
            kappa = rational(math.exp(math.log(1 / 20) + pk * (math.log(2) - math.log(1 / 20))))
            key = (lamA, lamB, u, kappa)
            if key in seen or T5.is_control(key):
                drop['seen'] += 1
                continue
            c = L75.regime_case(f'J{name[0].upper()}{j:04d}', lamA, lamB, u, kappa, dict(stratum=name, sobol=j))
            if max(un['est_truth'] for un in c['units']) > L75.CAP / 2:
                drop['cost'] += 1
                continue
            seen.add(key)
            acc.append(c)
        cases += acc
        report[name] = dict(accepted=len(acc), dropped=drop)
    CASES.write_text(json.dumps(cases, indent=1) + '\n')
    g = D2.FLUID_GRID
    used = {(p['kappa'], p['lamA'], p['eta'], p['yA'], p['yB']) for p in json.loads(D2.POINTS.read_text())['points']}
    combos = [tuple(str(v) for v in (kk, l, e, a, bb)) for kk in g['kappa'] for l in g['lamA'] for e in g['eta']
              for a in g['y'] for bb in g['y'] if l + 2 * e < 10]
    combos = [c for c in combos if c not in used]
    pick = np.random.default_rng(SEED).choice(len(combos), size=N_FLUID, replace=False)
    pts = [dict(id=f'FU{i:02d}', kappa=combos[j][0], lamA=combos[j][1], eta=combos[j][2], yA=combos[j][3], yB=combos[j][4])
           for i, j in enumerate(pick)]
    POINTS.write_text(json.dumps(dict(h=[str(h) for h in FLUID_H], ref=D2.FLUID_REF, points=pts), indent=1) + '\n')
    (OUT / 'design_r3_report.json').write_text(json.dumps(dict(seed=SEED, counts=COUNTS, seen_tuples=n_seen,
                                                                strata=report, fluid_points=len(pts)), indent=1) + '\n')
    print(json.dumps(report))


# ------------------------------------------------------------------------------------------------------ jobs

def _job(kind, item, path, cap):
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    signal.signal(signal.SIGXCPU, signal.SIG_DFL)
    out = light_regime(item) if kind == 'ctmc' else fluid_point(item)
    path.with_suffix('.tmp').write_text(json.dumps(out) + '\n')
    path.with_suffix('.tmp').rename(path)


def run_jobs(jobs, workers, cap):
    """jobs: (kind, item, path). One forked process per job; the parent records UNRESOLVED/ERROR for a dead child."""
    ctx = multiprocessing.get_context('fork')
    pending, active = list(jobs), {}
    while pending or active:
        while pending and len(active) < workers:
            job = pending.pop(0)
            if job[2].exists():
                continue
            p = ctx.Process(target=_job, args=(*job, cap))
            p.start()
            active[p] = job
        time.sleep(0.2)
        for p in [p for p in active if not p.is_alive()]:
            kind, item, path = active.pop(p)
            p.join()
            if not path.exists():
                sig = -p.exitcode if p.exitcode is not None and p.exitcode < 0 else None
                status = 'UNRESOLVED' if sig in (signal.SIGKILL, signal.SIGXCPU) else 'ERROR'
                path.write_text(json.dumps(dict(id=item['id'], status=status, exitcode=p.exitcode)) + '\n')
            print(kind, item['id'], json.loads(path.read_text())['status'], flush=True)


def load(dirpath, ids):
    return [json.loads((dirpath / f'{i}.json').read_text()) for i in ids]


# ------------------------------------------------------------------------------------------------------ read-outs

def rho(r):
    return r['Gamma_add'] / r['Gamma'] if abs(r['Gamma']) >= GMIN else None


def _sp(rows, key):
    pairs = [(x[key], rho(x)) for x in rows if x.get(key) is not None]
    return float(spearmanr([a for a, _ in pairs], [b for _, b in pairs]).statistic) if len(pairs) >= 3 else None


def ctmc_readout(regs, k=3, cut=None, var='kappa_delta'):
    """Rows at level k (3 = 7 T_int): by stratum, rank associations over eligible rows, and a split at `cut` of `var`."""
    rows = [(d['stratum'], d['rows'][k]) for d in regs if d['status'] == 'COMPLETED']
    out = {}
    for s in ('neg', 'band', 'pos'):
        r = [rho(x) for t, x in rows if t == s and rho(x) is not None]
        kd = [x['kappa_delta'] for t, x in rows if t == s and x.get('kappa_delta') is not None]
        out[s] = dict(n=len(r), median_rho=st.median(r) if r else None, median_kappa_delta=st.median(kd) if kd else None)
    el = [x for _, x in rows if rho(x) is not None]
    out['n_elig'] = len(el)
    for key in ('T_fresh', 'kappa_add', 'kappa_delta'):
        out[f'spearman_{key}_rho'] = _sp(el, key)
    if cut is not None:
        lo = [rho(x) for x in el if x[var] <= cut]
        hi = [rho(x) for x in el if x[var] > cut]
        out['split'] = dict(var=var, cut=cut, n_le=len(lo), n_gt=len(hi),
                            median_rho_le=st.median(lo) if lo else None, median_rho_gt=st.median(hi) if hi else None)
    return out


def fluid_readout(points, exclude_hold=False):
    by = {d['id']: {r['h']: r for r in d['rows']} for d in points if d['status'] == 'COMPLETED'}
    if exclude_hold:
        by = {i: v for i, v in by.items() if all(r['status'] == 'BOUNDED' for r in v.values())}
    lo, hi = str(FLUID_H[0]), str(FLUID_H[-1])
    rlo = [rho(v[lo]) for v in by.values() if rho(v[lo]) is not None]
    rhi = [rho(v[hi]) for v in by.values() if rho(v[hi]) is not None]
    both = [(rho(v[lo]), rho(v[hi])) for v in by.values() if rho(v[lo]) is not None and rho(v[hi]) is not None]
    el = [r for v in by.values() for r in v.values() if rho(r) is not None and r['T_fresh'] is not None]
    return dict(n_points=len(by), n_hold=sum(r['status'] != 'BOUNDED' for v in by.values() for r in v.values()),
                n_elig_lo=len(rlo), n_elig_hi=len(rhi), n_elig_both=len(both),
                median_rho_lo=st.median(rlo) if rlo else None, median_rho_hi=st.median(rhi) if rhi else None,
                frac_rho_up=sum(b > a for a, b in both) / len(both) if both else None,
                frac_kadd_up=sum((v[hi]['kappa_add'] or 0) > (v[lo]['kappa_add'] or 0) for v in by.values()) / len(by) if by else None,
                spearman_T_rho=_sp(el, 'T_fresh'), spearman_kappa_delta_rho=_sp(el, 'kappa_delta'),
                spearman_kappa_add_rho=_sp(el, 'kappa_add'), n_rows_elig=len(el))


def calibrate(workers, cap, tag='r3b'):
    """Exposed sets only: run01 (L7.5 sobol regimes), run02 (cases_fresh), run02 fluid pilot+panel points.
    Pass 1 (calib_r3, T_prox only) is kept as recorded; pass 2 (calib_r3b) adds kappa_delta."""
    cdir = OUT / f'calib_{tag}'
    cdir.mkdir(exist_ok=True)
    regs01 = [c for c in json.loads(D1.CASES.read_text()) if c['id'] in json.loads((OUT / 'run01/regimes.json').read_text())]
    regs02 = json.loads(D2.CASES.read_text())
    pts02 = json.loads(D2.POINTS.read_text())['points']
    jobs = [('ctmc', c, cdir / f"{c['id']}.json") for c in sorted(regs01 + regs02, key=lambda r: -max(r['N'].values()))]
    jobs += [('fluid', p, cdir / f"{p['id']}.json") for p in pts02]
    run_jobs(jobs, workers, cap)
    regs = load(cdir, [c['id'] for c in regs01 + regs02])
    pts = load(cdir, [p['id'] for p in pts02])
    # consistency with the saved round-1/2 Gamma_add (same engine arrays, same counterfactual)
    saved = {}
    for d in D2.ctmc_table(OUT / 'run01').items():
        saved[d[0]] = d[1]
    for d in D2.ctmc_table(OUT / 'run02').items():
        saved[d[0]] = d[1]
    gap = max(abs(r['Gamma_add'] - s['Gamma_add']) + abs(r['Gamma'] - s['Gamma'])
              for d in regs for r, s in zip(d['rows'], saved[d['id']]))
    out = dict(max_abs_diff_vs_saved_pp=gap, ctmc_7T=ctmc_readout(regs, 3), ctmc_1T=ctmc_readout(regs, 1),
               fluid=fluid_readout(pts), fluid_bounded_only=fluid_readout(pts, exclude_hold=True))
    for k in (1, 3):
        out[f'ctmc_level{k}_sorted_kdelta_rho_stratum_T'] = sorted(
            (x['kappa_delta'], rho(x), d['stratum'], x['T_fresh']) for d in regs for x in d['rows'][k:k + 1] if rho(x) is not None)
    out['fluid_sorted_h_kdelta_rho'] = sorted((r['h'], r['kappa_delta'], rho(r), r['status']) for d in pts for r in d['rows']
                                              if rho(r) is not None)
    CALIB.write_text(json.dumps(out, indent=1, default=str) + '\n')
    return out


# ------------------------------------------------------------------------------------------------------ run/score

def check_lock():
    if not LOCK.exists():
        raise PermissionError('card not locked: lock_idelta3.json missing')
    lock = json.loads(LOCK.read_text())
    for name, digest in lock['files'].items():
        if sha(ROOT / name) != digest:
            raise PermissionError(f'locked file changed: {name}')
    return lock


def run(out, workers, cap):
    lock = check_lock()
    out.mkdir(parents=True, exist_ok=False)
    env = D1.environment()
    env.update(lock=lock, idelta3_sha256=sha(__file__))
    (out / 'environment.json').write_text(json.dumps(env, indent=1) + '\n')
    cases = json.loads(CASES.read_text())
    pts = json.loads(POINTS.read_text())['points']
    (out / 'ids.json').write_text(json.dumps(dict(ctmc=[c['id'] for c in cases], fluid=[p['id'] for p in pts])) + '\n')
    (out / 'jobs').mkdir()
    jobs = [('ctmc', c, out / 'jobs' / f"{c['id']}.json") for c in sorted(cases, key=lambda r: -max(r['N'].values()))]
    jobs += [('fluid', p, out / 'jobs' / f"{p['id']}.json") for p in pts]
    run_jobs(jobs, workers, cap)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    (out / 'done.json').write_text(json.dumps(dict(children_cpu=kids.ru_utime + kids.ru_stime,
                                                    finished=time.strftime('%Y-%m-%dT%H:%M:%S%z'))) + '\n')


def score(out):
    env = json.loads((out / 'environment.json').read_text())
    pred = env['lock']['predictions']
    ids = json.loads((out / 'ids.json').read_text())
    regs, pts = load(out / 'jobs', ids['ctmc']), load(out / 'jobs', ids['fluid'])
    res = dict(card_sha256=env['lock']['files'][str(CARD.relative_to(ROOT))], card_sha256_now=sha(CARD))
    ok = [d for d in regs if d['status'] == 'COMPLETED']
    res['ctmc_completed'] = f'{len(ok)}/{len(regs)}'
    res['C1_Gamma_self_max_diff_pp'] = max(abs(r['Gamma_self'] - r['Gamma']) for d in ok for r in d['rows'])
    res['C1'] = res['C1_Gamma_self_max_diff_pp'] <= 1e-7
    r7, r1 = ctmc_readout(regs, 3), ctmc_readout(regs, 1)
    res['ctmc_7T'], res['ctmc_1T'] = r7, r1          # includes descriptive Spearman of T_fresh, kappa_add, kappa_delta
    v = lambda x, op, t: None if x is None else (x <= t if op == '<=' else x >= t)
    med = lambda xs: st.median(xs) if xs else None
    rows7 = [(d['stratum'], d['rows'][3]) for d in ok]
    rows1 = [(d['stratum'], d['rows'][1]) for d in ok]
    out7 = [rho(x) for s, x in rows7 if s != 'band' and rho(x) is not None]
    out1 = [rho(x) for s, x in rows1 if s != 'band' and rho(x) is not None]
    res['B1'] = dict(band_median=r7['band']['median_rho'], outside_median=med(out7), n_band=r7['band']['n'], n_out=len(out7))
    res['B1']['PASS'] = (v(res['B1']['band_median'], '<=', pred['B1_band_max']) is True and
                         v(res['B1']['outside_median'], '>=', pred['B1_out_min']) is True)
    help_ = [rho(x) for _, x in rows7 if rho(x) is not None and x['G_S'] > 0]
    harm = [rho(x) for _, x in rows7 if rho(x) is not None and x['G_S'] < 0]
    res['B2'] = dict(n_help=len(help_), frac_help_le=sum(r <= pred['B2_help_rho_max'] for r in help_) / len(help_) if help_ else None,
                     n_harm=len(harm), frac_harm_ge=sum(r >= pred['B2_harm_rho_min'] for r in harm) / len(harm) if harm else None,
                     median_help=med(help_), median_harm=med(harm))
    if min(len(help_), len(harm)) < pred['B_n_min']:
        res['B2']['PASS'] = 'NOT_EVALUABLE'
    else:
        res['B2']['PASS'] = (res['B2']['frac_help_le'] >= pred['B2_help_frac'] and res['B2']['frac_harm_ge'] >= pred['B2_harm_frac'])
    band = [x for s, x in rows7 if s == 'band']
    res['B3'] = dict(n_band=len(band), frac_GS_pos=sum(x['G_S'] > 0 for x in band) / len(band) if band else None)
    res['B3']['PASS'] = v(res['B3']['frac_GS_pos'], '>=', pred['B3_frac'])
    res['B4'] = dict(median_1T=med(out1), median_7T=med(out7), n_1T=len(out1), n_7T=len(out7))
    res['B4']['PASS'] = (v(res['B4']['median_1T'], '<=', pred['B4_lo_max']) is True and v(res['B4']['median_7T'], '>=', pred['B4_hi_min']) is True)
    if len(ok) < 0.9 * len(regs):
        for k in ('B1', 'B2', 'B3', 'B4'):
            res[k] = 'INCONCLUSIVE'
    fa, fb = fluid_readout(pts), fluid_readout(pts, exclude_hold=True)
    res['fluid'], res['fluid_bounded_only'] = fa, fb

    def fv(r):
        n_ok = min(r['n_elig_lo'], r['n_elig_hi']) >= pred['F_n_min']
        return dict(G1=((r['frac_rho_up'] < pred['G1_below']) if r['n_elig_both'] >= pred['F_n_min'] else 'NOT_EVALUABLE'),
                    G2=((v(r['median_rho_lo'], '<=', pred['G2_lo_max']) is True and v(r['median_rho_hi'], '>=', pred['G2_hi_min']) is True)
                        if n_ok else 'NOT_EVALUABLE'),
                    G3=v(r['frac_kadd_up'], '>=', pred['G3_min']),
                    G4=v(r['spearman_kappa_add_rho'], '>=', pred['G4_min']) if r['n_rows_elig'] >= pred['F_n_min'] else 'NOT_EVALUABLE')
    va, vb = fv(fa), fv(fb)
    res['fluid_verdicts_all'], res['fluid_verdicts_bounded_only'] = va, vb
    for k in va:
        res[k] = va[k] if va[k] == vb[k] else 'INCONCLUSIVE'
    (out / 'score.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=('design', 'calibrate', 'run', 'score'))
    p.add_argument('--out', type=Path)
    p.add_argument('--workers', type=int, default=os.cpu_count())
    p.add_argument('--cap', type=int, default=1800)
    a = p.parse_args()
    if a.cmd == 'design':
        design()
    elif a.cmd == 'calibrate':
        r = calibrate(a.workers, a.cap)
        print(json.dumps({k: v for k, v in r.items() if "sorted" not in k}, indent=1, default=str))
    elif a.cmd == 'run':
        run(a.out, a.workers, a.cap)
    else:
        print(json.dumps(score(a.out), indent=1, default=str))


if __name__ == '__main__':
    main()
