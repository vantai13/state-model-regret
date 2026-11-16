"""Doan Van Tai — W1b age-only CTMC comparison, importing the unchanged plant.

Stale telemetry is the full old (backlog, mode) state.  It has weight pi_Stay,
and every stale decision/value vector is exp(Q_Stay * tau) times its fresh
counterpart.  No backlog marginalization and no change to pair_sum's tie rule.
"""
from fractions import Fraction as F
import math

import numpy as np
from scipy.sparse.linalg import expm_multiply

from experiments.explore_ctmc import ctmc


def posterior_full(stay, vec, tau):
    """E[f(X_now) | X_old=x], indexed by the full old state x."""
    tau = float(tau)
    if not math.isfinite(tau) or tau < 0:
        raise ValueError('tau must be finite and nonnegative')
    vec = np.asarray(vec, dtype=float)
    if vec.shape[0] != stay.n:
        raise ValueError('state dimension mismatch')
    return vec.copy() if tau == 0 else expm_multiply(stay.Q * tau, vec)


def prepare_regime(lamA, lamB, u, kappa, hs, c=0, a=ctmc.A,
                   control=False, N_scale=1, allow_csw=False, v_table=None):
    """Compute the age-independent chains and gaps once for all requested ages."""
    ctmc._truth_allowed(a)
    lamA, lamB, u, kappa, c = (F(x) for x in (lamA, lamB, u, kappa, c))
    hs = [F(h) for h in hs]
    if not hs or not (min(lamA, lamB) >= max(ctmc.A, F(a))
                      and max(lamA, lamB) + u < ctmc.MU and kappa > 0
                      and c >= 0 and min(hs) > 0):
        raise ValueError('outside the ctmc-v1 domain')
    if not control and not (F(1, 4) <= u <= 3 and (c == 0 or allow_csw)):
        raise ValueError('outside the ctmc-v1 scientific domain')
    if int(N_scale) != N_scale or N_scale < 1:
        raise ValueError('N_scale must be a positive integer')
    NA, NB = (int(N_scale) * ctmc.choose_N(lam + u, kappa, a=a)
              for lam in (lamA, lamB))
    Ast, Asw = ctmc.chain(lamA + u, kappa, NA, a), ctmc.chain(lamA, kappa, NA, a)
    Bst, Bsw = ctmc.chain(lamB, kappa, NB, a), ctmc.chain(lamB + u, kappa, NB, a)
    hf = [float(h) for h in hs]

    def values(ch):
        if v_table is None:
            return ch.V(hs)
        key = (str(ch.load), str(ch.kappa), ch.N, str(F(ch.a)))
        out = np.asarray(v_table[key])
        if out.shape != (len(hs), ch.n):
            raise ValueError('precomputed V shape mismatch')
        return out

    def gaps(st, sw, sign):
        vst = values(st)
        vsw = vst if st is sw else values(sw)
        dh = ctmc.m0_gap(min(st.load, sw.load), abs(sw.load - st.load), kappa,
                         st.N, hf + [math.inf], 'A' if sign > 0 else 'B', a=a)
        return sign * (vsw - vst), dh, sign * (sw.g - st.g)

    dA, dhA, bA = gaps(Ast, Asw, +1)
    dB, dhB, bB = gaps(Bsw, Bst, -1)
    r_stay, r_switch = Ast.r + Bst.r, Asw.r + Bsw.r
    return dict(parameters=(lamA, lamB, u, kappa, c), hs=hs, a=a, NA=NA, NB=NB,
                Ast=Ast, Asw=Asw, Bst=Bst, Bsw=Bsw, dA=dA, dhA=dhA, bA=bA,
                dB=dB, dhB=dhB, bB=bB, r_stay=r_stay, r_switch=r_switch,
                s=r_switch - r_stay, r_min=min(r_stay, r_switch),
                s_mm1=ctmc.mm1_mean(lamA) + ctmc.mm1_mean(lamB + u)
                - ctmc.mm1_mean(lamA + u) - ctmc.mm1_mean(lamB),
                T_int=max(ch.T_int for ch in (Ast, Asw, Bst, Bsw)))


def evaluate_agediff(lamA, lamB, u, kappa, hs, tau, c=0, a=ctmc.A,
                     control=False, N_scale=1, disagree=True, arrays=False,
                     allow_csw=False, shat_levels=None, prepared=None):
    """Mirror ctmc.evaluate, changing only the stale observation to the full state.

    Optional prepared gaps avoid recomputing V for each age. shat_levels maps
    estimator names to scalar s-hat values; each gets the identical h*s-hat
    correction on both telemetry sides, and is always scored on the true plant.
    """
    args = tuple(F(x) for x in (lamA, lamB, u, kappa, c))
    hs = [F(h) for h in hs]
    p = prepared if prepared is not None else prepare_regime(
        *args[:4], hs, c=c, a=a, control=control, N_scale=N_scale,
        allow_csw=allow_csw)
    if p['parameters'] != args or p['hs'] != hs or F(p['a']) != F(a):
        raise ValueError('prepared regime does not match inputs')
    lamA, lamB, u, kappa, c = args
    Ast, Asw, Bst, Bsw = (p[n] for n in ('Ast', 'Asw', 'Bst', 'Bsw'))
    dA, dhA, bA, dB, dhB, bB = (p[n] for n in ('dA', 'dhA', 'bA', 'dB', 'dhB', 'bB'))
    H, hf = len(hs), [float(h) for h in hs]

    def old(stay, d, dh, b):
        post = posterior_full(stay, np.column_stack([d.T, dh.T, b]), tau)
        return post[:, :H].T, post[:, H:2 * H + 1].T, post[:, -1]

    dAo, dhAo, bAo = old(Ast, dA, dhA, bA)
    dBo, dhBo, bBo = old(Bst, dB, dhB, bB)
    wA, wB = Ast.pi, Bst.pi
    cf, s, r_stay, r_switch, r_min = (float(c), p['s'], p['r_stay'], p['r_switch'], p['r_min'])
    new = lambda uA, vA, uB, vB, tol=0.: ctmc.pair_sum(wA, uA, vA, wB, uB, vB, cf, tol)
    olds = new  # Old full state has exactly the same stationary law as current state.
    Fnew, Fold = new(dhA[H], bA, dhB[H], bB), olds(dhAo[H], bAo, dhBo[H], bBo)
    a_inf, Eb = s < 0, float(wA @ bA + wB @ bB) + cf
    asym = dict(F_new=Fnew[0], F_old=Fold[0],
                z_inf=100 * s * (Fold[0] - Fnew[0]) / r_min,
                a_inf_switch=bool(a_inf), B=Fold[1] - Fnew[1],
                beta_C=Eb if a_inf else 0.,
                M0_regret_new_pred=100 * abs(s) * ((1-Fnew[0]) if a_inf else Fnew[0]) / r_min,
                M0_regret_old_pred=100 * abs(s) * ((1-Fold[0]) if a_inf else Fold[0]) / r_min,
                tie_mass_new=new(dhA[H], bA, dhB[H], bB, 1e-12)[2],
                tie_mass_old=olds(dhAo[H], bAo, dhBo[H], bBo, 1e-12)[2])
    kn, ko = new(bA, bA, bB, bB), olds(bAo, bAo, bBo, bBo)
    asym.update(F_new_ko=kn[0], F_old_ko=ko[0],
                z_inf_ko=100 * s * (ko[0] - kn[0]) / r_min, B_ko=ko[1] - kn[1])
    levels = dict(true_s=s, mm1=p['s_mm1'])
    if shat_levels:
        levels.update(shat_levels)
    if not all(math.isfinite(float(v)) for v in levels.values()):
        raise ValueError('nonfinite s-hat')
    rows = []
    for k, h in enumerate(hf):
        scale, tol = h * r_stay, 1e-12 * (h * r_stay + 1)
        c11 = new(dA[k], dA[k], dB[k], dB[k], tol)
        c10 = new(dhA[k], dA[k], dhB[k], dB[k], tol)
        c01 = olds(dAo[k], dAo[k], dBo[k], dBo[k], tol)
        c00 = olds(dhAo[k], dAo[k], dhBo[k], dBo[k], tol)
        G00, G01, G10, G11 = c00[1], c01[1], c10[1], c11[1]
        Cref = scale + G11
        pct = lambda x: 100 * x / Cref
        Ed = float(wA @ dA[k] + wB @ dB[k]) + cf
        twins = dict(M1_new=G11, M1_old=G01, M0_new=G10, M0_old=G00,
                     static=Ed if h*s+cf < 0 else 0., const=min(0., Ed))
        shares = dict(M1_new=c11[0], M1_old=c01[0], M0_new=c10[0], M0_old=c00[0],
                      static=float(h*s+cf < 0), const=float(Ed < 0))
        margin = {}
        for rho in ctmc.RHOS:
            sh = float(rho) * scale
            mn = new(dhA[k]+sh, dA[k], dhB[k], dB[k])
            mo = olds(dhAo[k]+sh, dAo[k], dhBo[k], dBo[k])
            margin[str(rho)] = dict(new=pct(mn[1]-G11), old=pct(mo[1]-G11),
                                    share_new=mn[0], share_old=mo[0])
        best_new = min(margin, key=lambda r: (margin[r]['new'], F(r)))
        best_old = min(margin, key=lambda r: (margin[r]['old'], F(r)))
        twins['margin_new'] = G11 + margin[best_new]['new'] * Cref / 100
        twins['margin_old'] = G11 + margin[best_old]['old'] * Cref / 100
        hybrid = {}
        for name, sv in levels.items():
            hn = new(dhA[k]+h*float(sv), dA[k], dhB[k], dB[k])
            ho = olds(dhAo[k]+h*float(sv), dAo[k], dhBo[k], dBo[k])
            hybrid[name] = dict(s_hat=float(sv), regret_new=pct(hn[1]-G11),
                                regret_old=pct(ho[1]-G11), G_S=pct(ho[1]-hn[1]),
                                share_new=hn[0], share_old=ho[0],
                                excess_cost_new=hn[1]-G11, excess_cost_old=ho[1]-G11)
            if name in ('true_s', 'mm1'):
                twin_name = 'hybrid' if name == 'true_s' else 'hybrid_mm1'
                twins[twin_name+'_new'], twins[twin_name+'_old'] = hn[1], ho[1]
                shares[twin_name+'_new'], shares[twin_name+'_old'] = hn[0], ho[0]
        kn = new(dA[k]-h*s, dA[k], dB[k], dB[k])
        ko = olds(dAo[k]-h*s, dAo[k], dBo[k], dBo[k])
        twins['ko_new'], twins['ko_old'] = kn[1], ko[1]
        shares['ko_new'], shares['ko_old'] = kn[0], ko[0]
        row = dict(h=str(hs[k]), h_kappa=float(hs[k]/kappa), h_Tint=h/p['T_int'],
                   L00=scale+G00, L01=scale+G01, L10=scale+G10, L11=Cref, Cref=Cref,
                   E_stay=scale, E_gap=Ed, G_S=pct(G00-G10), G_M=pct(G00-G01),
                   G_SM=pct(G00-G11), Gamma=pct(G10+G01-G00-G11),
                   S=pct(G01-G11), M=pct(G10-G11),
                   regret={t: pct(v-G11) for t,v in twins.items()}, shares=shares,
                   margin=margin, margin_best=dict(new=best_new, old=best_old),
                   hybrid_levels=hybrid, G_S_hybrid=hybrid['true_s']['G_S'],
                   G_S_hybrid_mm1=hybrid['mm1']['G_S'],
                   z_pred_first_order_inf_decisions=100*(h*s*(asym['F_old']-asym['F_new'])+asym['B'])/(h*r_min+asym['beta_C']),
                   tie_mass=dict(c11=c11[2], c10=c10[2], c01=c01[2], c00=c00[2]),
                   G_S_ko=pct(ko[1]-kn[1]),
                   z_pred_first_order_ko=100*(h*s*(asym['F_old_ko']-asym['F_new_ko'])+asym['B_ko'])/(h*r_min+asym['beta_C']))
        row['dep_static'] = {t: v if shares['static'] == 0 else 1-v for t,v in shares.items()
                             if t not in ('static', 'const')}
        if disagree and wA.size*wB.size <= ctmc.DENSE_PAIRS:
            row['disagree_new'] = {t: ctmc.dense_disagree(wA, ua, dA[k], wB, ub, dB[k], cf)
                                   for t,(ua,ub) in dict(M0=(dhA[k],dhB[k]), hybrid=(dhA[k]+h*s,dhB[k])).items()}
            row['disagree_old'] = {t: ctmc.dense_disagree(wA, ua, dAo[k], wB, ub, dBo[k], cf)
                                   for t,(ua,ub) in dict(M0=(dhAo[k],dhBo[k]), hybrid=(dhAo[k]+h*s,dhBo[k])).items()}
        row['flags'] = [name+'_negative' for name in ('S','M','G_M') if row[name] < -1e-9]
        rows.append(row)
    chains = {name: dict(load=str(ch.load), N=ch.N, r=ch.r, T_int=ch.T_int,
                         var=ch.var, residual=ch.residual)
              for name,ch in dict(A_stay=Ast,A_switch=Asw,B_stay=Bst,B_switch=Bsw).items()}
    out = dict(namespace='ctmc-v1-letter-age-only', parameters=[str(x) for x in args],
               a=float(a), mu=ctmc.MU, tau=float(tau), stale_observation='full_old_state',
               N=dict(A=p['NA'],B=p['NB']), r_stay=r_stay,r_switch=r_switch,s=s,r_min=r_min,
               s_mm1=p['s_mm1'], x=float((lamB-lamA)/u) if u else None,
               delta=float(lamB-lamA), chains=chains, asymptotic=asym, h=rows)
    if arrays:
        out['_arrays'] = dict(dA=dA,dhA=dhA,dAo=dAo,dhAo=dhAo,dB=dB,dhB=dhB,dBo=dBo,
                              dhBo=dhBo,wA=wA,wB=wB,NA=p['NA'],NB=p['NB'])
    return out
