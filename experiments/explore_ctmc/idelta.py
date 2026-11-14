"""Doan Van Tai — I_Delta: prediction-level interaction and the empty-queue boundary on ctmc-v1 (Part C) and on
the slotted fluid path of contract v1.3 (Part F) [EXPLORATION ONLY; AI (Claude) theo ủy quyền 14/11/2026].

Design and predictions, written before this file: results/explore_ctmc/idelta/DESIGN_IDELTA.md (its sha256 is
stored in every output). Nothing here changes ctmc.py, the locked checkers or any case list.

Cells: d11 = Delta(x), d10 = Delta_hat(x), d01 = E[Delta | y], d00 = E[Delta_hat | y], with e = Delta_hat - Delta:
    I_Delta(x, y) = d11 - d10 - d01 + d00 = -e(x) + E[e | y]       (E[I_Delta | y] = 0 by the tower property)
Per path and action, with V_free the unclipped linear rollout (exact up to the truncation N):
    V = V_free + mu * I0 - BN,  V_hat = V_free + C0
    I0 = int_0^h (h - s) P(n_s = 0) ds,  BN = int_0^h (h - s) E[lam(m_s) 1{n_s = N}] ds,  C0 = V_hat - V_free.

Run (GCP dt4n-research-01, after `source experiments/explore_ctmc/env.sh`):
    python -m experiments.explore_ctmc.idelta run --out results/explore_ctmc/idelta/run01
    python -m experiments.explore_ctmc.idelta score --out results/explore_ctmc/idelta/run01
"""
import argparse
import csv
import hashlib
import json
import math
import multiprocessing
import os
import platform
import resource
import signal
import socket
import sys
import time
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import scipy
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply

from experiments.explore_ctmc import ctmc as C

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'results/explore_ctmc/idelta/DESIGN_IDELTA.md'
CASES = ROOT / 'results/explore_ctmc/cases_l75/sobol.json'
FIGURE = {'neg': 'TN0003', 'band': 'TB0007', 'pos': 'TP0079'}
TRIM = 1e-22                 # (y, x) pairs with joint weight below this are dropped; the dropped mass is reported
DELTAS = (0.1, 0.5, 1.0)     # % of Cref
QUANTS = (0.5, 0.9, 0.99)
HIT = 1e-6                   # reach set: max over actions of P(hit 0 within h) >= HIT
BULK = 1e-9                  # n_hi = smallest n with pi_Stay(n' <= n) >= 1 - BULK
CAP = 3600                   # CPU-s per regime (design: 2 CPU-h for the whole Part C)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select_regimes(cases=None):
    """Fixed rule of the design: per stratum the L7.5 figure regime, then the first two other ids in file order."""
    cases = json.loads(CASES.read_text()) if cases is None else cases
    out = []
    for stratum in ('neg', 'band', 'pos'):
        rs = [c for c in cases if c['tags']['stratum'] == stratum]
        out += [c for c in rs if c['id'] == FIGURE[stratum]] + [c for c in rs if c['id'] != FIGURE[stratum]][:2]
    return out


# ---------------------------------------------------------------------------------------------------------- per chain

def vfree(load, kappa, N, hs, a=C.A, mu=C.MU):
    """Unclipped mean rollout int_0^h (n + C(t)) dt, C(t) = (load - mu) t + sigma a (kappa/2)(1 - e^{-2t/kappa})."""
    L, k = float(load) - mu, float(kappa)
    n = np.repeat(np.arange(N + 1), 2).astype(float)
    sig = np.tile([-1.0, 1.0], N + 1)
    out = np.empty((len(hs), n.size))
    for j, h in enumerate(hs):
        h = float(h)
        out[j] = n * h + L * h * h / 2 + sig * float(a) * (k / 2) * (h + (k / 2) * C.det_expm1(np.array([-2 * h / k]))[0])
    return out


def _propagate(M, Z, hs):
    """Z(h) = e^{M h} Z for each h (any order), stepping through the sorted horizons."""
    out, t, W = [None] * len(hs), 0.0, Z.copy()
    for k in sorted(range(len(hs)), key=lambda j: float(hs[j])):
        h = float(hs[k])
        if h > t:
            W = expm_multiply(M * (h - t), W)
            t = h
        out[k] = W.copy()
    return out


def boundary_terms(ch, hs):
    """I0 and BN per state via the augmented generator [[Q, f0, fN, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1], 0, 0]:
    started at the unit vector of the last-but-one (last) coordinate, the chain block equals
    int_0^h (h - u) e^{Qu} f0 du (fN)."""
    n = ch.n
    nn = np.repeat(np.arange(ch.N + 1), 2)
    m = np.tile([0, 1], ch.N + 1)
    lam = float(ch.load) + np.where(m == 1, float(ch.a), -float(ch.a))
    f0 = (nn == 0).astype(float)
    fN = lam * (nn == ch.N)
    rows = [sp.hstack([ch.Q, sp.csr_matrix(f0[:, None]), sp.csr_matrix(fN[:, None]), sp.csr_matrix((n, 2))])]
    tail = sp.csr_matrix(([1.0, 1.0], ([0, 1], [2, 3])), shape=(4, 4))
    rows.append(sp.hstack([sp.csr_matrix((4, n)), tail]))
    M = sp.vstack(rows).tocsr()
    Z = np.zeros((n + 4, 2))
    Z[n + 2, 0] = 1.0
    Z[n + 3, 1] = 1.0
    res = _propagate(M, Z, hs)
    return np.array([r[:n, 0] for r in res]), np.array([r[:n, 1] for r in res])


def hit_prob(ch, hs):
    """P(n_s = 0 for some s <= h | x): the states n = 0 made absorbing."""
    nn = np.repeat(np.arange(ch.N + 1), 2)
    Q = ch.Q.tolil()
    for i in np.flatnonzero(nn == 0):
        Q.rows[i], Q.data[i] = [], []
    Q = Q.tocsr()
    v = (nn == 0).astype(float)
    return np.array(_propagate(Q, v, hs))


def path_terms(lam, u, kappa, N, hs, side):
    """True and M0 costs, boundary terms and hitting probabilities of one path under both actions.
    Side A: Stay = heavy (lam + u), Switch = light; side B: Stay = light, Switch = heavy."""
    light, heavy = C.chain(lam, kappa, N), C.chain(lam + u, kappa, N)
    acts = dict(St=heavy, Sw=light) if side == 'A' else dict(St=light, Sw=heavy)
    out = {}
    for name, ch in acts.items():
        V = ch.V(hs)
        Vhat = C.m0_vhat(ch.load, kappa, N, hs)
        Vf = vfree(ch.load, kappa, N, hs)
        I0, BN = boundary_terms(ch, hs)
        out[name] = dict(V=V, Vhat=Vhat, Vf=Vf, I0=I0, BN=BN, C0=Vhat - Vf, P=hit_prob(ch, hs),
                         resid=V - Vf - C.MU * I0 + BN, scale=max(1.0, float(np.abs(V).max())), pi=ch.pi)
    St, Sw = out['St'], out['Sw']
    out['e'] = (Sw['Vhat'] - St['Vhat']) - (Sw['V'] - St['V'])
    out['dC0'] = Sw['C0'] - St['C0']
    out['dI0mu'] = -C.MU * (Sw['I0'] - St['I0'])
    out['dBN'] = Sw['BN'] - St['BN']
    out['Pmax'] = np.maximum(St['P'], Sw['P'])
    return out


# ---------------------------------------------------------------------------------------------------- pair statistics

def trim(w, v):
    keep = w >= TRIM
    return w[keep], v[keep], float(w[~keep].sum())


def abs_stats(wA, IA, wB, IB, cref):
    """E|IA + IB|, P(|I| > delta) and quantiles of |I|, exact over all pairs (sort + cumulative sums)."""
    EI = float(wA @ IA + wB @ IB)
    neg = C.pair_sum(wA, IA, IA, wB, IB, IB, 0.0)[1]
    EabsI = EI - 2 * neg
    below = lambda t: C.pair_sum(wA, IA + t, IA, wB, IB, IB, 0.0)[0]           # P(I < -t)
    above = lambda t: C.pair_sum(wA, -IA + t, IA, wB, -IB, IB, 0.0)[0]         # P(I > t)
    tot = float(wA.sum() * wB.sum())
    out = dict(EI=EI, EabsI=EabsI, EabsI_pct=100 * EabsI / cref)
    for d in DELTAS:
        t = d * cref / 100
        out[f'P_gt_{d}pct'] = (below(t) + above(t)) / tot
    hi0 = float(np.abs(IA).max() + np.abs(IB).max())
    for q in QUANTS:
        lo, hi = 0.0, hi0
        for _ in range(48):
            mid = 0.5 * (lo + hi)
            if 1 - (below(mid) + above(mid)) / tot >= q:
                hi = mid
            else:
                lo = mid
        out[f'q{q}'] = hi
        out[f'q{q}_pct'] = 100 * hi / cref
    return out


def cond_mean(J2, e):
    """E[e(X) | Y = y] from the joint J2[y, x]."""
    p = J2.sum(axis=1)
    return (J2 @ e) / np.where(p > 0, p, 1)


def first_quiet(values, ok):
    """Smallest index i such that ok holds for every index >= i; None if ok fails at the last index."""
    if not ok[-1]:
        return None
    bad = np.flatnonzero(~ok)
    return int(bad[-1] + 1) if bad.size else 0


def n_hi(pi):
    cum = np.cumsum(pi.reshape(-1, 2).sum(axis=1))
    return int(np.searchsorted(cum, 1 - BULK))


# ------------------------------------------------------------------------------------------------------- one regime

def run_regime(case, dose_path=None):
    t0 = time.process_time()
    lamA, lamB, u, kappa, c = (F(x) for x in case['parameters'])
    hs = [F(h) for h in case['hs'][:4]]
    ev = C.evaluate(lamA, lamB, u, kappa, hs, c=c, disagree=False, arrays=True)
    ar = ev.pop('_arrays')
    NA, NB = ar['NA'], ar['NB']
    Ast, Bst = C.chain(lamA + u, kappa, NA), C.chain(lamB, kappa, NB)
    JA = C._joint_old_current(Ast).reshape(NA + 1, -1)
    JB = C._joint_old_current(Bst).reshape(NB + 1, -1)
    TA = path_terms(lamA, u, kappa, NA, hs, 'A')
    TB = path_terms(lamB, u, kappa, NB, hs, 'B')
    wA, wB = Ast.pi, Bst.pi
    pA, pB = wA.reshape(-1, 2).sum(axis=1), wB.reshape(-1, 2).sum(axis=1)
    hiA, hiB = n_hi(wA), n_hi(wB)
    cf = float(c)
    rows, dose = [], []
    for k, h in enumerate(hs):
        hf = float(h)
        er = ev['h'][k]
        Cref, scale = er['Cref'], er['E_stay']
        pct = lambda x: 100 * x / Cref
        dA, dhA, dAo, dhAo = ar['dA'][k], ar['dhA'][k], ar['dAo'][k], ar['dhAo'][k]
        dB, dhB, dBo, dhBo = ar['dB'][k], ar['dhB'][k], ar['dBo'][k], ar['dhBo'][k]
        eA, eB = dhA - dA, dhB - dB                  # engine M0 (shifted by +-u h^2/2; shifts cancel in I and in sums)
        EeA, EeB = cond_mean(JA, eA), cond_mean(JB, eB)
        ctrl = dict(
            tower_A=float(np.abs((JA * (-eA[None, :] + EeA[:, None])).sum(axis=1)).max()) / scale,
            tower_B=float(np.abs((JB * (-eB[None, :] + EeB[:, None])).sum(axis=1)).max()) / scale,
            posterior_A=float(np.abs(EeA - (dhAo - dAo)).max()) / scale,
            posterior_B=float(np.abs(EeB - (dhBo - dBo)).max()) / scale,
            marginal_A=float(np.abs(JA.sum(axis=1) - pA).max()), marginal_B=float(np.abs(JB.sum(axis=1) - pB).max()),
            identity_resid=max(float(np.abs(T[a]['resid'][k]).max()) / T[a]['scale'] for T in (TA, TB) for a in ('St', 'Sw')),
            shift_A=float(np.abs((eA - TA['e'][k]) - float(u) * hf * hf / 2).max()) / scale,
            shift_B=float(np.abs((eB - TB['e'][k]) + float(u) * hf * hf / 2).max()) / scale)
        # prediction-level interaction over all (y_A, x_A) x (y_B, x_B)
        IA2 = -eA[None, :] + EeA[:, None]
        IB2 = -eB[None, :] + EeB[:, None]
        wa, ia, dropA = trim(JA.ravel(), IA2.ravel())
        wb, ib, dropB = trim(JB.ravel(), IB2.ravel())
        stats = abs_stats(wa, ia, wb, ib, Cref)
        # alternative explanation: the upper truncation (arrivals blocked at N); drop the BN part of e
        eA_noN, eB_noN = TA['e'][k] - TA['dBN'][k], TB['e'][k] - TB['dBN'][k]
        IA3 = (-eA_noN[None, :] + cond_mean(JA, eA_noN)[:, None]).ravel()
        IB3 = (-eB_noN[None, :] + cond_mean(JB, eB_noN)[:, None]).ravel()
        keepA, keepB = JA.ravel() >= TRIM, JB.ravel() >= TRIM
        EI3 = float(wa @ IA3[keepA] + wb @ IB3[keepB])
        Eabs_noN = EI3 - 2 * C.pair_sum(wa, IA3[keepA], IA3[keepA], wb, IB3[keepB], IB3[keepB], 0.0)[1]
        # decision cells, recomputed, and counterfactuals that keep the gap but change the M0 error
        tol = 1e-12 * (scale + 1)
        fresh = lambda kA, kB: C.pair_sum(wA, kA, dA, wB, kB, dB, cf, tol)[1]
        stale = lambda kA, kB: C.pair_sum(pA, kA, dAo, pB, kB, dBo, cf, tol)[1]
        G11, G10, G01, G00 = fresh(dA, dB), fresh(dhA, dhB), stale(dAo, dBo), stale(dhAo, dhBo)
        bA, bB = float(wA @ eA), float(wB @ eB)
        gam = lambda g10, g00: pct(g10 + G01 - g00 - G11)
        cfs = dict(
            add=gam(fresh(dA + bA, dB + bB), stale(dAo + bA, dBo + bB)),
            minusA=gam(fresh(dA + bA, dhB), stale(dAo + bA, dhBo)),
            minusB=gam(fresh(dhA, dB + bB), stale(dhAo, dBo + bB)))
        ctrl['L_match_pp'] = max(abs(pct(G00) - pct(er['L00'] - scale)), abs(pct(G10) - pct(er['L10'] - scale)),
                                 abs(pct(G01) - pct(er['L01'] - scale)), abs(pct(G11) - pct(er['L11'] - scale)))
        ctrl['Gamma_match_pp'] = abs(gam(G10, G00) - er['Gamma'])
        # dose-response per path and mode (unshifted e and its boundary parts), reach set, n_reach, n_1e-3
        mech = {}
        for side, T, w, nh in (('A', TA, wA, hiA), ('B', TB, wB, hiB)):
            e = T['e'][k]
            Pm = T['Pmax'][k]
            R = Pm >= HIT
            tot = float(w @ np.abs(e))
            mech[side] = dict(n_hi=nh, P_R=float(w[R].sum()), share_R=float(w[R] @ np.abs(e[R])) / tot if tot > 0 else None,
                              E_abs_e_pct=pct(tot), bias_pct=pct(float(w @ e)),
                              max_abs_dBN_bulk=float(np.abs(T['dBN'][k].reshape(-1, 2)[:nh + 1]).max()))
            for m in (0, 1):
                em = e.reshape(-1, 2)[:nh + 1, m]
                Pmm = Pm.reshape(-1, 2)[:nh + 1, m]
                mx = float(np.abs(em).max())
                nr = first_quiet(em, Pmm <= HIT)
                n3 = first_quiet(em, np.abs(em) <= 1e-3 * mx) if mx > 0 else 0
                mech[side][f'm{m}'] = dict(e0=float(em[0]), e0_pct=pct(float(em[0])), max_abs_e=mx, argmax=int(np.abs(em).argmax()),
                                           n_reach=nr, n_1e3=n3, e_at_reach=None if nr is None else float(em[nr]),
                                           P6=None if nr is None else bool(abs(float(em[nr])) <= 1e-3 * mx),
                                           Phit0=float(Pmm[0]))
                if dose_path is not None:
                    pim = w.reshape(-1, 2)[:nh + 1, m]
                    parts = [T[x][k].reshape(-1, 2)[:nh + 1, m] for x in ('dC0', 'dI0mu', 'dBN')]
                    for n in range(nh + 1):
                        dose.append([case['id'], str(h), side, m, n, em[n], parts[0][n], parts[1][n], parts[2][n],
                                     T['St']['P'][k].reshape(-1, 2)[n, m], T['Sw']['P'][k].reshape(-1, 2)[n, m], pim[n]])
        # the concrete 2x2 at h = hs[1]: same y and x_A, B empty now vs B with backlog now (low mode)
        ex = None
        if k == 1:
            yA, yB = int(pA.argmax()), 0
            xA = 2 * yA
            nb = mech['B']['m0']['n_reach']
            nb_flag = nb is None or nb > hiB
            nb = hiB if nb_flag else nb
            ex = {}
            for label, nB in (('B_empty', 0), ('B_backlog', nb)):
                xB = 2 * nB
                d11, d10 = dA[xA] + dB[xB] + cf, dhA[xA] + dhB[xB] + cf
                d01, d00 = dAo[yA] + dBo[yB] + cf, dhAo[yA] + dhBo[yB] + cf
                ex[label] = dict(n_B=nB, d00=d00, d10=d10, d01=d01, d11=d11, I=d11 - d10 - d01 + d00,
                                 d00_pct=pct(d00), d10_pct=pct(d10), d01_pct=pct(d01), d11_pct=pct(d11),
                                 I_pct=pct(d11 - d10 - d01 + d00),
                                 actions=dict(zip(('00', '10', '01', '11'),
                                                  ['Switch' if v < 0 else 'Stay' for v in (d00, d10, d01, d11)])))
            ex.update(y_A=yA, y_B=yB, x_A=[yA, 0], backlog_capped_at_n_hi=nb_flag)
        rows.append(dict(id=case['id'], stratum=case['tags']['stratum'], x=case['x'], parameters=case['parameters'],
                         h=str(h), h_Tint=er['h_Tint'], Cref=Cref, G_S=er['G_S'], G_M=er['G_M'], Gamma=er['Gamma'],
                         Gamma_cf=cfs, bias_pct=pct(bA + bB), I=stats, Eabs_noN_rel=abs(Eabs_noN - stats['EabsI']) / stats['EabsI']
                         if stats['EabsI'] > 0 else None, dropped_mass=dict(A=dropA, B=dropB), pairs=dict(A=int(wa.size), B=int(wb.size)),
                         controls=ctrl, mech=mech, example=ex))
    return dict(id=case['id'], status='COMPLETED', rows=rows, N=dict(A=NA, B=NB),
                cpu=time.process_time() - t0, host=socket.gethostname()), dose


# ------------------------------------------------------------------------------------------------------ Part F fluid

def fluid_part():
    """Slotted fluid path of contract v1.3, exact rational (reference of L4.7): e_l(q, m) over a backlog sweep."""
    from experiments.P4_07_clipping.check_clipping import exact_reference, rational_mean, threshold
    dt, H, kappa, lam, u = F(1, 20), 10, F(3, 10), 7, 2
    keep = (1 + math.exp(-2 * float(dt / kappa))) / 2
    inc = lambda managed: (F(lam - 6 + managed - 10) * dt, F(lam + 6 + managed - 10) * dt)
    sides = dict(B=dict(St=inc(0), Sw=inc(u)), A=dict(St=inc(u), Sw=inc(0)))
    rows = []
    for side, acts in sides.items():
        for m in (0, 1):
            tstar = max(threshold(H, acts[a], m) for a in ('St', 'Sw'))
            for i in range(101):
                q = F(i, 20)
                M1 = {a: exact_reference(H, acts[a], keep, q, m) * dt for a in acts}
                M0 = {a: rational_mean(H, acts[a], keep, q, m) * dt for a in acts}
                e = (M0['Sw'] - M0['St']) - (M1['Sw'] - M1['St'])
                rows.append(dict(side=side, mode=m, q=str(q), t_star=str(tstar), outside=q >= tstar, e=str(e), e_float=float(e),
                                 M1_St=float(M1['St']), M1_Sw=float(M1['Sw']), M0_St=float(M0['St']), M0_Sw=float(M0['Sw'])))
    return dict(parameters=dict(dt='1/20', H=H, kappa='3/10', lam=lam, u=u, mu=10, a=6, keep=keep), rows=rows)


# ------------------------------------------------------------------------------------------------------ runner/score

def _child(case, path, dose_path, cap):
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    signal.signal(signal.SIGXCPU, signal.SIG_DFL)
    out, dose = run_regime(case, dose_path=dose_path)
    with open(dose_path.with_suffix('.tmp'), 'w', newline='') as f:
        csv.writer(f).writerows(dose)
    dose_path.with_suffix('.tmp').rename(dose_path)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out) + '\n')
    tmp.rename(path)


def environment():
    return dict(host=socket.gethostname(), python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                platform=platform.platform(), env={k: os.environ.get(k) for k in
                                                   ('NPY_DISABLE_CPU_FEATURES', 'OPENBLAS_CORETYPE', 'OMP_NUM_THREADS')},
                design_sha256=sha(DESIGN), idelta_sha256=sha(__file__), ctmc_sha256=sha(C.__file__),
                cases_sha256=sha(CASES), started=time.strftime('%Y-%m-%dT%H:%M:%S%z'))


def run(out, workers, cap):
    out.mkdir(parents=True, exist_ok=False)
    (out / 'environment.json').write_text(json.dumps(environment(), indent=1) + '\n')
    t0 = time.process_time()
    (out / 'fluid.json').write_text(json.dumps(fluid_part(), indent=1) + '\n')
    fluid_cpu = time.process_time() - t0
    regs = select_regimes()
    (out / 'regimes.json').write_text(json.dumps([r['id'] for r in regs]) + '\n')
    rdir = out / 'regimes'
    rdir.mkdir()
    # heaviest first (largest N), so the run time is not dominated by a late straggler
    jobs = sorted(regs, key=lambda r: -max(r['N'].values()))
    ctx = multiprocessing.get_context('fork')
    pending, active = list(jobs), {}
    while pending or active:
        while pending and len(active) < workers:
            case = pending.pop(0)
            p = ctx.Process(target=_child, args=(case, rdir / f"{case['id']}.json", rdir / f"{case['id']}_dose.csv", cap))
            p.start()
            active[p] = case
        time.sleep(0.2)
        for p in [p for p in active if not p.is_alive()]:
            case = active.pop(p)
            p.join()
            path = rdir / f"{case['id']}.json"
            if not path.exists():
                sig = -p.exitcode if p.exitcode is not None and p.exitcode < 0 else None
                status = 'UNRESOLVED' if sig in (signal.SIGKILL, signal.SIGXCPU) else 'ERROR'
                path.write_text(json.dumps(dict(id=case['id'], status=status, exitcode=p.exitcode)) + '\n')
            print(case['id'], json.loads(path.read_text())['status'], flush=True)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    (out / 'done.json').write_text(json.dumps(dict(fluid_cpu=fluid_cpu, children_cpu=kids.ru_utime + kids.ru_stime,
                                                    finished=time.strftime('%Y-%m-%dT%H:%M:%S%z'))) + '\n')


def score(out):
    """Scores the design predictions from the saved rows only (no recomputation)."""
    regs = json.loads((out / 'regimes.json').read_text())
    data = [json.loads((out / 'regimes' / f'{i}.json').read_text()) for i in regs]
    status = {d['id']: d['status'] for d in data}
    rows = [r for d in data if d['status'] == 'COMPLETED' for r in d['rows']]
    fl = json.loads((out / 'fluid.json').read_text())['rows']
    res = dict(status=status, n_rows=len(rows))
    ctl = lambda key: max(r['controls'][key] for r in rows)
    res['P2'] = dict(identity_resid=ctl('identity_resid'), tower=max(ctl('tower_A'), ctl('tower_B')),
                     posterior=max(ctl('posterior_A'), ctl('posterior_B')), Gamma_match_pp=ctl('Gamma_match_pp'),
                     L_match_pp=ctl('L_match_pp'), shift=max(ctl('shift_A'), ctl('shift_B')),
                     marginal=max(ctl('marginal_A'), ctl('marginal_B')))
    res['P2']['PASS'] = (res['P2']['identity_resid'] <= 1e-7 and res['P2']['tower'] <= 1e-9 and res['P2']['Gamma_match_pp'] <= 1e-7)
    res['P3'] = dict(max_rel=max(r['Eabs_noN_rel'] for r in rows))
    res['P3']['PASS'] = res['P3']['max_rel'] <= 1e-6
    p1 = [(r['id'], r['h'], r['I']['EabsI_pct'], abs(r['Gamma'])) for r in rows]
    res['P1'] = dict(n=len(p1), n_ge_05=sum(e >= 0.5 for _, _, e, _ in p1), n_gt_Gamma=sum(e > g for _, _, e, g in p1),
                     fails=[x for x in p1 if not (x[2] >= 0.5 and x[2] > x[3])])
    res['P1']['PASS'] = not res['P1']['fails']
    p4 = {}
    for side in ('A', 'B'):
        for m in (0, 1):
            sel = [x for x in fl if x['side'] == side and x['mode'] == m]
            p4[f'{side}{m}'] = dict(t_star=sel[0]['t_star'], outside_all_zero=all(F(x['e']) == 0 for x in sel if x['outside']),
                                    inside_some_nonzero=any(F(x['e']) != 0 for x in sel if not x['outside']),
                                    n_outside=sum(x['outside'] for x in sel), n_inside=sum(not x['outside'] for x in sel))
    res['P4'] = dict(cases=p4, PASS=all(v['outside_all_zero'] and v['inside_some_nonzero'] for v in p4.values()))
    p5 = [(r['id'], r['h'], r['mech']['B']['m0']['e0'], r['mech']['A']['m0']['e0']) for r in rows]
    res['P5'] = dict(n=len(p5), fails=[x for x in p5 if not (x[2] < 0 and x[3] > 0)])
    res['P5']['PASS'] = not res['P5']['fails']
    p6 = [(r['id'], r['h'], s, m, r['mech'][s][f'm{m}']['P6']) for r in rows for s in ('A', 'B') for m in (0, 1)]
    res['P6'] = dict(n=len(p6), n_pass=sum(x[4] is True for x in p6), n_fail=sum(x[4] is False for x in p6),
                     n_not_evaluable=sum(x[4] is None for x in p6), fails=[x for x in p6 if x[4] is False])
    res['P6']['PASS'] = res['P6']['n_fail'] == 0 and res['P6']['n_pass'] > 0
    p7 = []
    for i in {r['id'] for r in rows}:
        rr = sorted([r for r in rows if r['id'] == i], key=lambda r: F(r['h']))
        for s in ('A', 'B'):
            for m in (0, 1):
                seq = [r['mech'][s][f'm{m}']['n_reach'] for r in rr]
                if None in seq:
                    p7.append((i, s, m, seq, None))
                else:
                    p7.append((i, s, m, seq, all(a <= b for a, b in zip(seq, seq[1:]))))
    res['P7'] = dict(n=len(p7), n_pass=sum(x[4] is True for x in p7), n_fail=sum(x[4] is False for x in p7),
                     n_not_evaluable=sum(x[4] is None for x in p7), fails=[x for x in p7 if x[4] is False])
    res['P7']['PASS'] = res['P7']['n_fail'] == 0 and res['P7']['n_pass'] > 0
    d1 = [(r['id'], r['h'], r['Gamma'], r['Gamma_cf']['add']) for r in rows if abs(r['Gamma']) >= 0.01]
    res['D1'] = dict(n=len(d1), n_big=sum(abs(g - a) >= 0.25 * abs(g) for _, _, g, a in d1))
    res['D1']['PASS'] = res['D1']['n_big'] * 2 >= res['D1']['n'] if d1 else None
    res['design_sha256_now'] = sha(DESIGN)
    res['design_sha256_run'] = json.loads((out / 'environment.json').read_text())['design_sha256']
    (out / 'score.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=('run', 'score'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--workers', type=int, default=os.cpu_count())
    p.add_argument('--cap', type=int, default=CAP)
    a = p.parse_args()
    if a.cmd == 'run':
        run(a.out, a.workers, a.cap)
    print(json.dumps({k: v.get('PASS') if isinstance(v, dict) else v for k, v in score(a.out).items()
                      if k.startswith(('P', 'D'))}, indent=1))


if __name__ == '__main__':
    main()
