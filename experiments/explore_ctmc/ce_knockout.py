"""Doan Van Tai — Bayes vs plug-in aggregation of the stale twin ("CE knockout", redesigned) on ctmc-v1
[EXPLORATION ONLY; AI (Claude) theo ủy quyền 14/11/2026: "tự thiết kế và sửa lại làm sao cho hợp lí"].

Design (written before any outcome of this module): results/explore_ctmc/ce_knockout/DESIGN_CE.md.
Nothing here changes ctmc.py, the contract, the locked checkers or any old case list.

Stale arms (fresh cells S1M0 / S1M1 untouched). Per path, with y the old backlog, nbar(y) = E[n | y] and
p1(y) = P(m = high | y) under the true posterior D(.|y):
    B  (contract, Bayes)   g_B(y)  = E_D[v(X) | y]
    PB (backlog plug-in)   g_PB(y) = sum_m P(m | y) v(nbar(y), m), v linear between integer backlogs
    QM (full plug-in, M0)  fluid rollout at real backlog nbar(y) and mode sign 2 p1(y) - 1 (the proposal's version)
v is the M0 gap (twin) or the true gap (M1 control); the constant-bias surrogate uses v = Delta + b, b = E_pi e.
Penalties of the plug-in: P_M0 = L00^PB - L00, P_M1 = L01^PB - L01 (>= 0, L01 is Bayes-optimal), P_sur likewise.
Jensen terms: J_hat = g_B(Delta_hat) - g_PB(Delta_hat), J = g_B(Delta) - g_PB(Delta), K = J_hat - J
(= E[e | y] - e_PB(y), the Jensen gap of the M0 error itself).

    python -m experiments.explore_ctmc.ce_knockout calibrate --workers N   # exposed regimes of I_Delta rounds 2-3
    python -m experiments.explore_ctmc.ce_knockout design                  # fresh panel (write-once)
    python -m experiments.explore_ctmc.ce_knockout run --out DIR           # after the card lock
    python -m experiments.explore_ctmc.ce_knockout score --out DIR
"""
import argparse
import hashlib
import json
import math
import multiprocessing
import platform
import resource
import signal
import socket
import statistics as st
import sys
import time
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import scipy

from experiments.explore_ctmc import ctmc as C

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/ce_knockout'
DESIGN = OUT / 'DESIGN_CE.md'
CARD = OUT / 'CARD_CE.md'
LOCK = OUT / 'lock_ce.json'
CASES = OUT / 'cases_ce.json'
CALIB_SETS = (ROOT / 'results/explore_ctmc/idelta/cases_fresh.json', ROOT / 'results/explore_ctmc/idelta/cases_r3.json')
GMIN = 0.05            # pp: a ratio is read only when its denominator is at least this large
CAP = 1800             # CPU-s per regime


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------------- plug-in tools

def posterior_moments(stay):
    """E[n | y] and P(m = high | y) for the old backlog y (same push e^{Q tau} as C.posterior_mean)."""
    n = np.repeat(np.arange(stay.N + 1), 2).astype(float)
    m = np.tile([0.0, 1.0], stay.N + 1)
    post = C.posterior_mean(stay, np.column_stack([n, m]))
    return post[:, 0], np.clip(post[:, 1], 0.0, 1.0)


def plug_backlog(v, nbar, p1):
    """sum_m P(m | y) v(nbar(y), m) with v (index 2n + m) linear between integer backlogs."""
    V = np.asarray(v, dtype=float).reshape(-1, 2)
    grid = np.arange(V.shape[0], dtype=float)
    return (1 - p1) * np.interp(nbar, grid, V[:, 0]) + p1 * np.interp(nbar, grid, V[:, 1])


def fluid_vhat(load, kappa, n, sig, hs, a=C.A, mu=C.MU):
    """C.m0_vhat at real backlog n >= 0 and mode sign sig in [-1, 1]; same formulas, so at integer n and sig = +-1
    it reproduces C.m0_vhat. Returns (rows over hs, drain time T)."""
    a = float(a)
    L, k = float(load) - mu, float(kappa)
    if L >= 0:
        raise ValueError('mean rollout needs load < mu')
    n = np.asarray(n, dtype=float)
    sig = np.broadcast_to(np.asarray(sig, dtype=float), n.shape).copy()

    def phi(t):
        return n + L * t + sig * a * (k / 2) * (-C.det_expm1(-2 * t / k))
    rising = (sig > 0) & (L + sig * a > 0)
    tp = np.zeros_like(n)
    for i in np.flatnonzero(rising):
        tp[i] = (k / 2) * math.log(sig[i] * a / -L)
    lo = tp.copy()
    hi = (n + np.maximum(sig, 0.0) * a * k / 2) / -L
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        pos = phi(mid) > 0
        lo, hi = np.where(pos, mid, lo), np.where(pos, hi, mid)
    T = hi
    T[(n == 0) & ~rising] = 0.0

    def integral(t):
        return n * t + L * t * t / 2 + sig * a * (k / 2) * (t + (k / 2) * C.det_expm1(-2 * t / k))
    out = np.empty((len(hs), n.size))
    for j, h in enumerate(hs):
        t = np.minimum(float(h), T)
        v = integral(t)
        v[t == 0] = 0.0
        out[j] = np.maximum(v, 0.0)
    return out, T


def fluid_gap(lam, u, kappa, n, sig, hs, side):
    """C.m0_gap (finite h only) at real backlog n and mode sign sig: shift +-u h^2/2 and the certified-tie rule."""
    light, T = fluid_vhat(lam, kappa, n, sig, hs)
    heavy, _ = fluid_vhat(lam + u, kappa, n, sig, hs)
    out = np.empty_like(light)
    for j, h in enumerate(hs):
        h = float(h)
        diff = (light[j] - heavy[j]) if side == 'A' else (heavy[j] - light[j])
        c0 = float(u) * h * h / 2
        out[j] = diff + c0 if side == 'A' else diff - c0
        out[j][T >= h] = 0.0
    return out


def e_abs_pair(wa, a, wb, b):
    """E|a_i + b_j| under wa x wb (exact, sort + cumulative sums)."""
    return float(wa @ a + wb @ b) - 2 * C.pair_sum(wa, a, a, wb, b, b, 0.0)[1]


def sign_mass(wa, a, wb, b):
    """P(a_i + b_j > 0) and P(a_i + b_j < 0) under wa x wb."""
    neg = C.pair_sum(wa, a, a, wb, b, b, 0.0)[0]
    pos = C.pair_sum(wa, -a, -a, wb, -b, -b, 0.0)[0]
    return pos, neg


# ------------------------------------------------------------------------------------------------------- one regime

def regime(case):
    t0 = time.process_time()
    lamA, lamB, u, kappa, c = (F(x) for x in case['parameters'])
    hs = [F(h) for h in case['hs'][:4]]
    ev = C.evaluate(lamA, lamB, u, kappa, hs, c=c, disagree=False, arrays=True)
    ar = ev.pop('_arrays')
    Ast, Bst = C.chain(lamA + u, kappa, ar['NA']), C.chain(lamB, kappa, ar['NB'])
    wA, wB = Ast.pi, Bst.pi
    pA, pB = wA.reshape(-1, 2).sum(axis=1), wB.reshape(-1, 2).sum(axis=1)
    nbA, p1A = posterior_moments(Ast)
    nbB, p1B = posterior_moments(Bst)
    s, cf = ev['s'], float(c)
    rows = []
    for k, h in enumerate(hs):
        er = ev['h'][k]
        Cref, scale = er['Cref'], er['E_stay']
        pct = lambda x: 100 * x / Cref
        dA, dhA, dAo, dhAo = ar['dA'][k], ar['dhA'][k], ar['dAo'][k], ar['dhAo'][k]
        dB, dhB, dBo, dhBo = ar['dB'][k], ar['dhB'][k], ar['dBo'][k], ar['dhBo'][k]
        bA, bB = float(wA @ (dhA - dA)), float(wB @ (dhB - dB))
        # plug-in stale gaps: M0 (interpolated, exact fluid, full plug-in) and the true model
        hA_pb, hB_pb = plug_backlog(dhA, nbA, p1A), plug_backlog(dhB, nbB, p1B)
        tA_pb, tB_pb = plug_backlog(dA, nbA, p1A), plug_backlog(dB, nbB, p1B)
        fx = lambda lam, nb, p1, side: ((1 - p1) * fluid_gap(lam, u, kappa, nb, -1.0, [h], side)[0]
                                        + p1 * fluid_gap(lam, u, kappa, nb, 1.0, [h], side)[0])
        hA_px, hB_px = fx(lamA, nbA, p1A, 'A'), fx(lamB, nbB, p1B, 'B')
        hA_qm = fluid_gap(lamA, u, kappa, nbA, 2 * p1A - 1, [h], 'A')[0]
        hB_qm = fluid_gap(lamB, u, kappa, nbB, 2 * p1B - 1, [h], 'B')[0]
        tol = 1e-12 * (scale + 1)
        fresh = lambda kA, kB: C.pair_sum(wA, kA, dA, wB, kB, dB, cf, tol)
        stale = lambda kA, kB: C.pair_sum(pA, kA, dAo, pB, kB, dBo, cf, tol)
        c11, c10, c01, c00 = fresh(dA, dB), fresh(dhA, dhB), stale(dAo, dBo), stale(dhAo, dhBo)
        G11, G10, G01, G00 = c11[1], c10[1], c01[1], c00[1]
        c00_pb, c00_px, c00_qm = stale(hA_pb, hB_pb), stale(hA_px, hB_px), stale(hA_qm, hB_qm)
        c01_pb = stale(tA_pb, tB_pb)
        # constant-bias surrogate M0' = Delta + b: no state-dependent model error by construction
        c10_s, c00_s, c00_spb = fresh(dA + bA, dB + bB), stale(dAo + bA, dBo + bB), stale(tA_pb + bA, tB_pb + bB)
        # Jensen terms under p(y) x p(y)
        JhA, JhB = dhAo - hA_pb, dhBo - hB_pb
        JA, JB = dAo - tA_pb, dBo - tB_pb
        KA, KB = JhA - JA, JhB - JB
        Jh_pos, Jh_neg = sign_mass(pA, JhA, pB, JhB)
        K_pos, K_neg = sign_mass(pA, KA, pB, KB)
        # NK (added after calibration pass 1): remove only K = Jensen of the M0 error, keep the true Jensen J:
        # g_NK = E[Delta_hat | y] - K(y) = Delta_hat_PB(y) + J(y)
        c00_nk = stale(dhAo - KA, dhBo - KB)
        # stale-twin error vs stale truth with and without K: E|E[e|y]| and E|e_PB(y)|
        err_B = e_abs_pair(pA, dhAo - dAo, pB, dhBo - dBo)
        err_PB = e_abs_pair(pA, hA_pb - tA_pb, pB, hB_pb - tB_pb)
        ctrl = dict(
            L_match_pp=max(abs(pct(G00) - pct(er['L00'] - scale)), abs(pct(G10) - pct(er['L10'] - scale)),
                           abs(pct(G01) - pct(er['L01'] - scale)), abs(pct(G11) - pct(er['L11'] - scale))),
            tower_rel=max(abs(float(pA @ dhAo) - float(wA @ dhA)), abs(float(pB @ dhBo) - float(wB @ dhB)))
            / max(1.0, abs(float(wA @ dhA)) + abs(float(wB @ dhB))),
            bayes_M1_pp=pct(c01_pb[1] - G01),                       # must be >= -tolerance
            interp_vs_fluid_pp=abs(pct(c00_pb[1] - c00_px[1])),     # interpolation vs exact fluid at real nbar
            interp_gap_max_rel=max(float(np.abs(hA_pb - hA_px).max()), float(np.abs(hB_pb - hB_px).max())) / max(1.0, scale))
        rows.append(dict(
            h=str(h), h_Tint=er['h_Tint'], Cref=Cref, s_sign=int(np.sign(s)),
            G_S=er['G_S'], G_M=er['G_M'], Gamma=er['Gamma'],
            G_S_PB=pct(c00_pb[1] - G10), G_S_PX=pct(c00_px[1] - G10), G_S_QM=pct(c00_qm[1] - G10),
            G_S_sur=pct(c00_s[1] - c10_s[1]), G_S_sur_PB=pct(c00_spb[1] - c10_s[1]),
            G_S_NK=pct(c00_nk[1] - G10), P_NK=pct(c00_nk[1] - G00),
            err_B_pct=pct(err_B), err_PB_pct=pct(err_PB),
            P_M0=pct(c00_pb[1] - G00), P_M0_PX=pct(c00_px[1] - G00), P_QM=pct(c00_qm[1] - G00),
            P_M1=pct(c01_pb[1] - G01), P_sur=pct(c00_spb[1] - c00_s[1]),
            share_switch=dict(B=c00[0], PB=c00_pb[0], QM=c00_qm[0], NK=c00_nk[0], M1_B=c01[0], M1_PB=c01_pb[0],
                              fresh_M0=c10[0]),
            bias_pct=pct(bA + bB),
            E_Jhat_pct=pct(float(pA @ JhA + pB @ JhB)), E_J_pct=pct(float(pA @ JA + pB @ JB)),
            E_K_pct=pct(float(pA @ KA + pB @ KB)),
            Eabs_Jhat_pct=pct(e_abs_pair(pA, JhA, pB, JhB)), Eabs_J_pct=pct(e_abs_pair(pA, JA, pB, JB)),
            Eabs_K_pct=pct(e_abs_pair(pA, KA, pB, KB)),
            Jhat_sign_mass=dict(pos=Jh_pos, neg=Jh_neg), K_sign_mass=dict(pos=K_pos, neg=K_neg),
            controls=ctrl))
    return dict(id=case['id'], status='COMPLETED', stratum=case['tags']['stratum'], x=case['x'],
                parameters=case['parameters'], s=s, N=dict(A=ar['NA'], B=ar['NB']), rows=rows,
                cpu=time.process_time() - t0, host=socket.gethostname())


# ------------------------------------------------------------------------------------------------------------ jobs

def _job(item, path, cap):
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    signal.signal(signal.SIGXCPU, signal.SIG_DFL)
    out = regime(item)
    path.with_suffix('.tmp').write_text(json.dumps(out) + '\n')
    path.with_suffix('.tmp').rename(path)


def run_jobs(items, outdir, workers, cap=CAP):
    """One forked process per regime; the parent records UNRESOLVED/ERROR for a dead child."""
    outdir.mkdir(parents=True, exist_ok=True)
    ctx = multiprocessing.get_context('fork')
    pending, active = [(it, outdir / f"{it['id']}.json") for it in items], {}
    while pending or active:
        while pending and len(active) < workers:
            it, path = pending.pop(0)
            if path.exists():
                continue
            p = ctx.Process(target=_job, args=(it, path, cap))
            p.start()
            active[p] = (it, path)
        time.sleep(0.2)
        for p in [p for p in active if not p.is_alive()]:
            it, path = active.pop(p)
            p.join()
            if not path.exists():
                sig = -p.exitcode if p.exitcode is not None and p.exitcode < 0 else None
                status = 'UNRESOLVED' if sig in (signal.SIGKILL, signal.SIGXCPU) else 'ERROR'
                path.write_text(json.dumps(dict(id=it['id'], status=status, exitcode=p.exitcode)) + '\n')
            print(it['id'], json.loads(path.read_text())['status'], flush=True)


def load(outdir):
    return [json.loads(p.read_text()) for p in sorted(Path(outdir).glob('*.json'))]


def environment():
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                host=socket.gethostname(), platform=platform.platform(), design_sha256=sha(DESIGN),
                module_sha256=sha(__file__))


def calibrate(workers):
    """Exposed regimes only: the I_Delta round-2 and round-3 panels (their G_S/Gamma are already seen)."""
    if not DESIGN.exists():
        raise FileNotFoundError('the design must exist before any calibration output')
    items = []
    for path in CALIB_SETS:
        items += json.loads(path.read_text())
    outdir = OUT / 'calib'
    run_jobs(items, outdir / 'regimes', workers)
    (outdir / 'environment.json').write_text(json.dumps(environment(), indent=1) + '\n')


# ------------------------------------------------------------------------------------------------ panel and score

PRED = OUT / 'predictions_ce.json'
SEED = 20261116
COUNTS = dict(neg=15, band=10, pos=15)
H_SHORT, H_LONG = 1, 3          # indices of h = 1 and 7 x T_int_max in every case's hs


def design():
    """Fresh panel: same domain, Sobol scheme, strata and cost filter as I_Delta round 3, new seed, 0 overlap with
    every earlier case list (L7.1, L7.5, I_Delta rounds 2-3)."""
    from scipy.stats import qmc
    from experiments.explore_ctmc import design_l75 as L75
    from experiments.explore_ctmc import idelta2 as D2
    from experiments.explore_ctmc import tau as T5
    from experiments.explore_ctmc.design import rational
    if CASES.exists():
        raise FileExistsError(f'{CASES} is write-once')
    seen = D2.seen_all()
    for path in CALIB_SETS:
        seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads(path.read_text())}
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
            c = L75.regime_case(f'K{name[0].upper()}{j:04d}', lamA, lamB, u, kappa, dict(stratum=name, sobol=j))
            if max(un['est_truth'] for un in c['units']) > L75.CAP / 2:
                drop['cost'] += 1
                continue
            seen.add(key)
            acc.append(c)
        cases += acc
        report[name] = dict(accepted=len(acc), dropped=drop)
    CASES.write_text(json.dumps(cases, indent=1) + '\n')
    (OUT / 'design_ce_report.json').write_text(json.dumps(dict(seed=SEED, counts=COUNTS, seen_tuples=n_seen,
                                                                strata=report), indent=1) + '\n')
    print(json.dumps(report))


def _md(v):
    return st.median(v) if v else None


def _q(v, p):
    v = sorted(v)
    return v[int(p * (len(v) - 1))] if v else None


def stats(regs, k, scope, harm_pp=0.05, twin='PB'):
    """Read-outs at horizon index k for scope 'outside' (neg + pos) or 'band'. twin: PB (primary) or PX (control)."""
    X = [r['rows'][k] for r in regs if r.get('status') == 'COMPLETED'
         and ((r['stratum'] != 'band') if scope == 'outside' else (r['stratum'] == 'band'))]
    harm = [x for x in X if x['G_S'] < -harm_pp]
    ret = lambda key: [x[key] / x['G_S'] for x in harm]
    pb = 'G_S_PB' if twin == 'PB' else 'G_S_PX'
    Kr = [x['Eabs_K_pct'] / x['Eabs_Jhat_pct'] for x in X if x['Eabs_Jhat_pct'] > 0]
    out = dict(n_rows=len(X), n_harm=len(harm),
               retained=dict(NK=_md(ret('G_S_NK')), PB=_md(ret(pb)), QM=_md(ret('G_S_QM'))),
               retained_q10_q90=dict(NK=[_q(ret('G_S_NK'), .1), _q(ret('G_S_NK'), .9)],
                                     PB=[_q(ret(pb), .1), _q(ret(pb), .9)], QM=[_q(ret('G_S_QM'), .1), _q(ret('G_S_QM'), .9)]),
               frac_still_harm=dict(NK=sum(x['G_S_NK'] < 0 for x in harm) / len(harm) if harm else None,
                                    PB=sum(x[pb] < 0 for x in harm) / len(harm) if harm else None,
                                    QM=sum(x['G_S_QM'] < 0 for x in harm) / len(harm) if harm else None),
               K_over_Jhat=_md(Kr), K_over_Jhat_q90=_q(Kr, .9),
               err_ratio=_md([x['err_B_pct'] / x['err_PB_pct'] for x in X if x['err_PB_pct'] > 0]),
               P_M1_median=_md([x['P_M1'] for x in X]),
               G_S_median=dict(B=_md([x['G_S'] for x in X]), NK=_md([x['G_S_NK'] for x in X]),
                               PB=_md([x[pb] for x in X]), QM=_md([x['G_S_QM'] for x in X])))
    return out


def verdicts(regs, P, twin='PB'):
    """Apply the thresholds of predictions_ce.json. A prediction with fewer than min_rows harm rows is NOT_EVALUABLE."""
    out = {}
    for name in ('N1', 'N2', 'P1'):
        p = P[name]
        s = stats(regs, p['h_index'], p['scope'], P['harm_threshold_pp'], twin)
        if s['n_harm'] < P['min_rows']:
            out[name] = dict(verdict='NOT_EVALUABLE', stats=s)
            continue
        if name in ('N1', 'N2'):
            ok = (s['retained']['NK'] >= p['median_retained_NK_min'] and s['frac_still_harm']['NK'] >= p['frac_still_harm_NK_min'])
        else:
            ok = (s['frac_still_harm']['PB'] >= p['frac_still_harm_min'] and s['frac_still_harm']['QM'] >= p['frac_still_harm_min']
                  and s['retained']['PB'] >= p['median_retained_PB_min'] and s['retained']['QM'] >= p['median_retained_QM_min'])
        out[name] = dict(verdict='PASS' if ok else 'FAIL', stats=s)
    p = P['N3']
    s = stats(regs, p['h_index'], p['scope'], P['harm_threshold_pp'], twin)
    out['N3'] = dict(verdict='PASS' if s['K_over_Jhat'] is not None and s['K_over_Jhat'] <= p['median_K_over_Jhat_max'] else 'FAIL',
                     stats=s)
    return out


def summarize_calibration():
    regs = load(OUT / 'calib' / 'regimes')
    out = dict(source='calibration pass 2 (exposed I_Delta round-2/3 panels)', n=len(regs),
               controls=dict(L_match_pp_max=max(x['controls']['L_match_pp'] for r in regs for x in r['rows']),
                             tower_rel_max=max(x['controls']['tower_rel'] for r in regs for x in r['rows']),
                             bayes_M1_pp_min=min(x['controls']['bayes_M1_pp'] for r in regs for x in r['rows']),
                             interp_vs_fluid_pp_max=max(x['controls']['interp_vs_fluid_pp'] for r in regs for x in r['rows'])),
               stats={f'{scope}_h{k}': stats(regs, k, scope) for scope in ('outside', 'band') for k in (H_SHORT, H_LONG)})
    if PRED.exists():
        out['verdicts_on_calibration'] = {n: v['verdict'] for n, v in verdicts(regs, json.loads(PRED.read_text())).items()}
    (OUT / 'calibration_ce.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(out['stats'], indent=1)[:4000])


LOCKED = (DESIGN, CARD, PRED, CASES, Path(__file__), ROOT / 'experiments/explore_ctmc/ctmc.py')


def check_lock():
    if not LOCK.exists():
        raise RuntimeError('the card is not locked (lock_ce.json missing)')
    lock = json.loads(LOCK.read_text())
    bad = [p for p, h in lock['sha256'].items() if sha(ROOT / p) != h]
    if bad:
        raise RuntimeError(f'locked files changed: {bad}')
    if json.loads(PRED.read_text()).get('status') not in ('LOCKED_AI_DELEGATED', 'LOCKED_AUTHOR'):
        raise RuntimeError('predictions_ce.json is still a draft')
    return lock


def lock_card():
    if LOCK.exists():
        raise FileExistsError('lock_ce.json is write-once')
    LOCK.write_text(json.dumps(dict(created=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                    sha256={str(p.relative_to(ROOT)): sha(p) for p in LOCKED}), indent=1) + '\n')


def run(outdir, workers):
    lock = check_lock()
    outdir = Path(outdir)
    if (outdir / 'done.json').exists():
        raise FileExistsError('this run already finished; the card forbids a rerun')
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'environment.json').write_text(json.dumps(dict(environment(), lock=lock), indent=1) + '\n')
    items = json.loads(CASES.read_text())
    t0 = time.time()
    run_jobs(items, outdir / 'regimes', workers)
    (outdir / 'done.json').write_text(json.dumps(dict(wall_s=time.time() - t0, n=len(items)), indent=1) + '\n')


def score(outdir):
    check_lock()
    outdir = Path(outdir)
    P = json.loads(PRED.read_text())
    regs = load(outdir / 'regimes')
    n_done = sum(r.get('status') == 'COMPLETED' for r in regs)
    n_all = len(json.loads(CASES.read_text()))
    rows = [x for r in regs if r.get('status') == 'COMPLETED' for x in r['rows']]
    ctrl = dict(C1=max(x['controls']['L_match_pp'] for x in rows) <= 1e-7,
                C2=min(x['controls']['bayes_M1_pp'] for x in rows) >= -1e-9,
                C3=max(x['controls']['tower_rel'] for x in rows) <= 1e-10)
    v_pb, v_px = verdicts(regs, P, 'PB'), verdicts(regs, P, 'PX')
    final = {}
    for name, v in v_pb.items():
        verdict = v['verdict']
        if n_done < 0.9 * n_all or not all(ctrl.values()):
            verdict = 'INCONCLUSIVE'
        elif v_px[name]['verdict'] != verdict:
            verdict = 'INCONCLUSIVE'          # C4: interpolation and exact fluid must agree
        final[name] = verdict
    out = dict(completed=n_done, of=n_all, controls=ctrl, C4_PX_verdicts={n: v['verdict'] for n, v in v_px.items()},
               verdicts=final, details=v_pb,
               band_exploratory={f'h{k}': stats(regs, k, 'band') for k in (H_SHORT, H_LONG)},
               card_sha256=sha(CARD), predictions_sha256=sha(PRED))
    (outdir / 'score.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(dict(verdicts=final, controls=ctrl, completed=n_done), indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['calibrate', 'summarize', 'design', 'lock', 'run', 'score'])
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'calibrate':
        calibrate(a.workers)
    elif a.cmd == 'summarize':
        summarize_calibration()
    elif a.cmd == 'design':
        design()
    elif a.cmd == 'lock':
        lock_card()
    elif a.cmd == 'run':
        run(a.out, a.workers)
    else:
        score(a.out)


if __name__ == '__main__':
    main()
