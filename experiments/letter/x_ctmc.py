"""Doan Van Tai — x-ctmc-v1, DESIGN_X_CTMC.md including Appendix A.

Independent heterogeneous MMPP/M/1 chains use letter.mmpp.generator. No
ctmc.Chain, guarded truth API, monkey patch, amplitude unlock or old output is
used. Only the unchanged unguarded pair_sum/det_expm1 primitives are imported.
The backlog-only posterior option exists solely for legacy equivalence tests;
the experiment observes the full old (backlog, mode) state on both paths.

Commands are separate: pilot, predict, lock, verify-lock, truth, score. The
pilot exposes only the four largest parameter-selected regimes. Predict never
computes finite-h plant values. Truth is one-shot and score requires committed
raw. Independent rescoring is deliberately left for the requested later turn.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

import numpy as np
import scipy
from scipy.sparse.linalg import expm_multiply, splu

from experiments.explore_ctmc.ctmc import det_expm1, pair_sum
from experiments.letter import mmpp, pl_posterior, shat2

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/x_ctmc"
BRIEF = Path("/home/vantai/state-model-regret-papers/letter_smr/briefs/strengthen/DESIGN_X_CTMC.md")
DESIGN_SHA256 = "7f9464af9e6f96a04f56d7fe9c887e0507a80e8aa8a95eb735ae8e1790e4c8de"
NAMESPACE = "x-ctmc-v1"
SEEDS = dict(grid=2611201, train=2611202, test=2611203, pilot=2611204)
H_GRID = (1, 3, 10, 30, 100)
AGES = (1, 3)
THETAS = (.5, .65, .8, .9)
RULES = ("M0", "Hybrid_true", "Hybrid_hat", "Stationary_hat",
         "TH_0.5", "TH_0.65", "TH_0.8", "TH_0.9", "MLU", "Pool")
TAIL = 1e-13
REGIME_CPU_CAP = 3600
PAIR_COUNT = 2000
# A pilot is a timing/exposure sample at h=T_int, both requested ages. Full
# truth cost is projected to h=100*T_int and five horizons before inclusion.
PILOT_H = (1,)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write_once(path, obj):
    path = Path(path)
    payload = obj if isinstance(obj, str) else json.dumps(
        obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(payload)


def event(name, **fields):
    print(json.dumps(dict(event=name, **fields), allow_nan=False), flush=True)


def environment():
    return dict(python=os.sys.version, numpy=np.__version__, scipy=scipy.__version__,
                numeric_env={k: os.environ.get(k) for k in (
                    "NPY_DISABLE_CPU_FEATURES", "OPENBLAS_CORETYPE", "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")})


def require_environment():
    pl_posterior.require_environment()


@dataclass(frozen=True)
class PathSpec:
    load: float  # exogenous mean, without the managed flow
    mu: float
    alpha: float
    kappa: float


@dataclass(frozen=True)
class Regime:
    id: str
    A: PathSpec
    B: PathSpec
    u: float
    stratum: str = "control"

    def record(self):
        return asdict(self)

    @classmethod
    def from_record(cls, row):
        return cls(row["id"], PathSpec(**row["A"]), PathSpec(**row["B"]),
                   row["u"], row.get("stratum", "control"))


def heldout_collision(regime):
    return (regime.A.mu == regime.B.mu == 10 and
            regime.A.alpha == regime.B.alpha and regime.A.alpha in (3., 7.5))


def parameter_comparison(regime):
    a, b, u = regime.A, regime.B, regime.u
    stay = ((a.load + u) / a.mu, b.load / b.mu)
    switch = (a.load / a.mu, (b.load + u) / b.mu)
    util_gap = max(switch) - max(stay)
    mm1_gap = sum(r / (1 - r) for r in switch) - sum(r / (1 - r) for r in stay)
    label = "tie" if util_gap == 0 or mm1_gap == 0 else (
        "agree" if util_gap * mm1_gap > 0 else "disagree")
    return dict(rho_stay=list(stay), rho_switch=list(switch), s_U=util_gap,
                s_mm1=mm1_gap, stratum=label)


def generate_grid():
    """Parameter-only rejection sampling, no stationary/decision outcomes.

    Base utilizations are uniform [.2,.9); u is uniform over the remaining
    common stable headroom. The alpha ratio refers to exogenous load ell_p.
    Keep the first 32 in each strict ranking stratum, in draw order.
    """
    rng = np.random.default_rng(SEEDS["grid"])
    counts = dict(agree=0, disagree=0)
    records, rejected = [], dict(heldout_collision=0, ranking_tie=0, full_stratum=0)
    draws = 0
    while min(counts.values()) < 32:
        draws += 1
        if draws > 1000000:
            raise RuntimeError("parameter rejection sampler exhausted")
        mu = rng.choice([5., 10., 20.], 2)
        loads = rng.uniform(.2, .9, 2) * mu
        ratios = rng.choice([.2, .5, .8], 2)
        kappas = rng.choice([1., 5., 20.], 2)
        u = float(rng.uniform(0, min(.9 * mu - loads)))
        r = Regime("", PathSpec(*map(float, (loads[0], mu[0], ratios[0]*loads[0], kappas[0]))),
                   PathSpec(*map(float, (loads[1], mu[1], ratios[1]*loads[1], kappas[1]))), u)
        if heldout_collision(r):
            rejected["heldout_collision"] += 1
            continue
        label = parameter_comparison(r)["stratum"]
        if label == "tie":
            rejected["ranking_tie"] += 1
            continue
        if counts[label] == 32:
            rejected["full_stratum"] += 1
            continue
        counts[label] += 1
        records.append(Regime(f"XCTMC_{len(records)+1:03d}", r.A, r.B, u, label))
    return records, dict(seed=SEEDS["grid"], draws=draws, accepted=counts, rejected=rejected,
        sampling="mu/kappa/alpha_ratio independent discrete uniform; base rho uniform [.2,.9); u uniform (0,min(.9*mu-ell)); first 32 per strict stratum")


class Chain:
    """Sparse gain/bias solution, independent of the guarded ctmc.Chain."""
    def __init__(self, load, kappa, N, alpha, mu):
        self.load, self.kappa, self.N, self.alpha, self.mu = (
            float(load), float(kappa), int(N), float(alpha), float(mu))
        self.Q = mmpp.generator(load, kappa, N, alpha, mu)
        self.n = self.Q.shape[0]
        self.f = np.repeat(np.arange(N + 1), 2).astype(float)
        qt = self.Q.T.tocsc()
        rest = splu(qt[1:, 1:].tocsc()).solve(-qt[1:, 0].toarray().ravel())
        pi = np.r_[1., rest]
        self.pi = pi / pi.sum()
        self.r = float(self.pi @ self.f)
        rhs = -(self.f - self.r)
        g = np.r_[0., splu(self.Q[1:, 1:].tocsc()).solve(rhs[1:])]
        self.g = g - self.pi @ g
        self.var = float(self.pi @ (self.f - self.r)**2)
        self.T_int = float(self.pi @ ((self.f-self.r)*self.g)) / self.var if self.var > 0 else 0.
        self.residual = float(np.max(abs(self.pi @ self.Q)))
        if (not np.isfinite(self.pi).all() or self.pi.min() < 0 or
                self.residual > 1e-9 or not math.isfinite(self.T_int) or self.T_int <= 0):
            raise ArithmeticError("invalid stationary chain or backlog correlation time")

    @property
    def gamma(self):
        return self.load + self.alpha + self.mu + 1 / self.kappa

    def V(self, horizons):
        """h*r + g - exp(Q*h)g; direct sparse exponential, no tail omission."""
        hs = list(map(float, horizons))
        if any(not math.isfinite(h) or h < 0 for h in hs):
            raise ValueError("V requires finite nonnegative horizons")
        out = np.empty((len(hs), self.n))
        w, t = self.g.copy(), 0.
        for i in sorted(range(len(hs)), key=lambda j: hs[j]):
            if hs[i] > t:
                w = expm_multiply(self.Q * (hs[i] - t), w)
                t = hs[i]
            out[i] = hs[i] * self.r + self.g - w
        return out


def fluid_values(load, kappa, N, horizons, alpha, mu, return_T=False):
    """Eq. fluid generalized per path, same arithmetic as legacy m0_vhat."""
    if not (0 <= alpha <= load < mu and kappa > 0):
        raise ValueError("invalid fluid parameters")
    L, k = float(load) - float(mu), float(kappa)
    n = np.repeat(np.arange(N + 1), 2).astype(float)
    sig = np.tile([-1., 1.], N + 1)
    rising = (sig > 0) & (L + alpha > 0)
    tp = np.where(rising, (k/2)*math.log(alpha/-L) if L+alpha > 0 else 0., 0.)
    lo = tp.copy()
    hi = (n + np.where(sig > 0, alpha*k/2, 0.)) / -L
    for _ in range(200):
        mid = .5 * (lo + hi)
        pos = n + L*mid + sig*alpha*(k/2)*(-det_expm1(-2*mid/k)) > 0
        lo, hi = np.where(pos, mid, lo), np.where(pos, hi, mid)
    T = hi
    T[(n == 0) & ~rising] = 0.
    out = np.empty((len(horizons), n.size))
    for i, h in enumerate(horizons):
        if math.isnan(float(h)) or h < 0:
            raise ValueError("invalid fluid horizon")
        t = np.minimum(float(h), T)
        v = n*t + L*t*t/2 + sig*alpha*(k/2)*(t+(k/2)*det_expm1(-2*t/k))
        v[t == 0] = 0.
        out[i] = np.maximum(v, 0.)
    return (out, T) if return_T else out


def fluid_gap(path, u, N, horizons, side):
    light, T = fluid_values(path.load, path.kappa, N, horizons, path.alpha, path.mu, True)
    heavy = fluid_values(path.load+u, path.kappa, N, horizons, path.alpha, path.mu)
    out = np.empty_like(light)
    for i, h in enumerate(horizons):
        diff = light[i]-heavy[i] if side == "A" else heavy[i]-light[i]
        if h == math.inf:
            out[i] = diff
        else:
            shift = float(u)*float(h)*float(h)/2
            out[i] = diff+shift if side == "A" else diff-shift
            out[i][T >= h] = 0.  # certified busy-path equality, not an epsilon
    return out


def posterior(chain, values, tau, observation="full"):
    if not math.isfinite(tau) or tau < 0:
        raise ValueError("age must be finite and nonnegative")
    vec = np.asarray(values, dtype=float)
    if vec.shape[0] != chain.n:
        raise ValueError("posterior state dimension mismatch")
    push = vec.copy() if tau == 0 else expm_multiply(chain.Q * float(tau), vec)
    if observation == "full":
        return push
    if observation != "backlog":
        raise ValueError("unknown observation")
    one = vec.ndim == 1
    push = push[:, None] if one else push
    p = chain.pi.reshape(-1, 2)
    out = (p[:, :, None] * push.reshape(-1, 2, push.shape[1])).sum(axis=1)
    out /= np.where(p.sum(axis=1) > 0, p.sum(axis=1), 1)[:, None]
    return out[:, 0] if one else out


def prepare(regime, Ns=None):
    """Stationary/truncation metadata only; never computes finite-h truth."""
    if heldout_collision(regime):
        raise ValueError("excluded legacy L7.2 held-out coordinate")
    chains, truncation = {}, {}
    for side, path in (("A", regime.A), ("B", regime.B)):
        loads = dict(stay=path.load+(regime.u if side == "A" else 0.),
                     switch=path.load+(regime.u if side == "B" else 0.))
        selections = {a: mmpp.choose_N(load, path.kappa, path.alpha, path.mu, TAIL)
                      for a, load in loads.items()}
        N = max(v[0] for v in selections.values()) if Ns is None else Ns[side]
        truncation[side] = dict(N=N, actions={a: dict(selector_N=v[0], selector_tail=v[1],
                                                method=v[2]) for a, v in selections.items()})
        for action, load in loads.items():
            name = side + ("st" if action == "stay" else "sw")
            chains[name] = Chain(load, path.kappa, N, path.alpha, path.mu)
    r0 = chains["Ast"].r + chains["Bst"].r
    r1 = chains["Asw"].r + chains["Bsw"].r
    tint = max(ch.T_int for ch in chains.values())
    if tint <= 0:
        raise ArithmeticError("nonpositive T_int")
    busy = {action: 1-float(chains["A"+action].pi[:2].sum() * chains["B"+action].pi[:2].sum())
            for action in ("st", "sw")}
    return dict(regime=regime, chains=chains, truncation=truncation, T_int=tint,
                r_stay=r0, r_switch=r1, s=r1-r0, nearly_empty=all(v < .01 for v in busy.values()),
                busy_probability=busy)


def preparation_metadata(p):
    ch = p["chains"]
    state_pair = ch["Ast"].n * ch["Bst"].n
    return dict(id=p["regime"].id, T_int=p["T_int"], truncation=p["truncation"],
                state_pair=state_pair, nearly_empty=p["nearly_empty"], busy_probability=p["busy_probability"],
                chains={k: dict(states=c.n, r=c.r, T_int=c.T_int, residual=c.residual)
                        for k, c in ch.items()},
                work=dict(values=sum(c.n*c.gamma for c in ch.values())*p["T_int"],
                          posterior=sum(ch[k].n*ch[k].gamma for k in ("Ast", "Bst"))*4*p["T_int"],
                          pairs=sum(c.n*math.log2(c.n) for c in (ch["Ast"], ch["Bst"])),
                          training=sum(ch[k].gamma for k in ("Ast", "Bst"))*100*p["T_int"]))


def decision_vectors(p, horizons, tau, s_hat, observation="full"):
    ch, regime = p["chains"], p["regime"]
    fluid, old, mode = {}, {}, {}
    for side in ("A", "B"):
        path, stay = getattr(regime, side), ch[side+"st"]
        fluid[side] = fluid_gap(path, regime.u, stay.N, list(horizons)+[math.inf], side)
        sigma = np.tile([-1., 1.], stay.N+1)
        pushed = posterior(stay, np.column_stack([fluid[side].T, sigma]), tau, observation)
        old[side], mode[side] = pushed[:, :-1].T, pushed[:, -1]
    return dict(fresh=fluid, stale=old, old_mode=mode, s_hat=s_hat, observation=observation)


def utilization(path, mode, u, side):
    base = path.load + path.alpha*np.asarray(mode)
    return ((base+(u if side == "A" else 0.))/path.mu,
            (base+(u if side == "B" else 0.))/path.mu)


def utilization_null(regime):
    """Mean of max utilization, not max of mean utilization (grid label)."""
    mode = np.array([-1., 1.])
    a0, a1 = utilization(regime.A, mode, regime.u, "A")
    b0, b1 = utilization(regime.B, mode, regime.u, "B")
    # Each independent symmetric background mode has stationary mass 1/2.
    return float((np.maximum(a1[:,None], b1[None,:])-
                  np.maximum(a0[:,None], b0[None,:])).mean())


def threshold_inputs(ua0, ub1, threshold):
    if not math.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and nonnegative")
    return dict(a=-np.asarray(ua0), b=np.asarray(ub1),
                gate=np.asarray(ua0) > threshold, boundary=np.asarray(ua0) == threshold)


def rule_inputs(p, decisions, rule, side, i, h):
    regime, ch = p["regime"], p["chains"]
    a, b = decisions[side]["A"][i], decisions[side]["B"][i]
    if rule in ("M0", "Hybrid_true", "Hybrid_hat"):
        level = 0. if rule == "M0" else p["s"] if rule == "Hybrid_true" else decisions["s_hat"]
        if level is None:
            return None
        return dict(a=a+h*level, b=b)
    if rule in ("Stationary_hat", "Pool"):
        gap = decisions["s_hat"] if rule == "Stationary_hat" else float(
            ch["Ast"].pi @ decisions["fresh"]["A"][i] + ch["Bst"].pi @ decisions["fresh"]["B"][i])
        if gap is None:
            return None
        return dict(a=np.full_like(a, gap), b=np.zeros_like(b))
    if rule != "MLU" and rule not in {f"TH_{t:g}" for t in THETAS}:
        raise ValueError("unknown rule: "+rule)
    modes = ({s: np.tile([-1., 1.], ch[s+"st"].N+1) for s in ("A", "B")}
             if side == "fresh" else decisions["old_mode"])
    ua0, _ = utilization(regime.A, modes["A"], regime.u, "A")
    _, ub1 = utilization(regime.B, modes["B"], regime.u, "B")
    # Since u>0, max(U_A1,U_B1)<max(U_A0,U_B0) iff U_B1<U_A0.
    if rule.startswith("TH_"):
        return threshold_inputs(ua0, ub1, float(rule[3:]))
    return dict(a=-ua0, b=ub1)


def policy_sum(weights_a, weights_b, inputs, value_a, value_b):
    wa = weights_a if "gate" not in inputs else weights_a*inputs["gate"]
    mass, value, ties = pair_sum(wa, inputs["a"], value_a, weights_b, inputs["b"], value_b, 0.)
    if "boundary" in inputs:
        # score=max(theta-U_A0,U_B1-U_A0); exact zero chooses Stay.
        m, _, t = pair_sum(weights_a*inputs["boundary"], inputs["a"], value_a,
                           weights_b, inputs["b"], value_b, 0.)
        ties += m+t
    return mass, value, ties


def constant_action(inputs):
    """Certify a state-independent action from strict comparisons, no epsilon."""
    a, b = inputs["a"], inputs["b"]
    gate = inputs.get("gate", np.ones(len(a), dtype=bool))
    if not np.any(gate) or np.min(b) >= -np.min(a[gate]):
        return 0
    if np.all(gate) and np.max(b) < -np.max(a):
        return 1
    return None


def asymptotic_m0(p, decisions, tau):
    ch = p["chains"]
    b = {s: ch[s+"sw"].g-ch[s+"st"].g for s in ("A", "B")}
    bo = {s: posterior(ch[s+"st"], b[s], tau, decisions["observation"]) for s in ("A", "B")}
    wa, wb = ch["Ast"].pi, ch["Bst"].pi
    if decisions["observation"] == "backlog":
        oa, ob = wa.reshape(-1,2).sum(axis=1), wb.reshape(-1,2).sum(axis=1)
    else:
        oa, ob = wa, wb
    fn = pair_sum(wa, decisions["fresh"]["A"][-1], b["A"], wb, decisions["fresh"]["B"][-1], b["B"], 0.)
    fo = pair_sum(oa, decisions["stale"]["A"][-1], bo["A"], ob, decisions["stale"]["B"][-1], bo["B"], 0.)
    return dict(p_new_inf=fn[0], p_old_inf=fo[0], slope=p["s"]*(fo[0]-fn[0]), B_inf=fo[1]-fn[1])


def evaluate(p, horizons, ages, s_hat, rules=RULES, observation="full"):
    """Exact finite-h truth; callers choose pilot versus separately locked truth."""
    start, wall = time.process_time(), time.perf_counter()
    ch = p["chains"]
    t = time.process_time()
    values = {k: c.V(horizons) for k, c in ch.items()}
    gap = {s: values[s+"sw"]-values[s+"st"] for s in ("A", "B")}
    timing = dict(values=time.process_time()-t, posterior=0., pairs=0.)
    wa, wb = ch["Ast"].pi, ch["Bst"].pi
    rows, asym = [], {}
    for tau in ages:
        t = time.process_time()
        decisions = decision_vectors(p, horizons, tau, s_hat, observation)
        old_gap = {s: posterior(ch[s+"st"], gap[s].T, tau, observation).T for s in ("A", "B")}
        asym[str(tau)] = asymptotic_m0(p, decisions, tau)
        timing["posterior"] += time.process_time()-t
        oa, ob = ((wa.reshape(-1,2).sum(axis=1), wb.reshape(-1,2).sum(axis=1))
                  if observation == "backlog" else (wa, wb))
        t = time.process_time()
        for i, h in enumerate(horizons):
            oracle = pair_sum(wa, gap["A"][i], gap["A"][i], wb, gap["B"][i], gap["B"][i], 0.)[1]
            scale, cref = h*p["r_stay"], h*p["r_stay"]+oracle
            if cref <= 0:
                raise ArithmeticError("nonpositive C_ref")
            for rule in rules:
                ni = rule_inputs(p, decisions, rule, "fresh", i, h)
                oi = rule_inputs(p, decisions, rule, "stale", i, h)
                common = dict(regime=p["regime"].id, stratum=p["regime"].stratum, rule=rule,
                              h=h, h_T_int=h/p["T_int"], tau=tau, tau_T_int=tau/p["T_int"],
                              s=p["s"], s_hat=s_hat, C_ref=cref)
                if ni is None or oi is None:
                    rows.append(dict(**common, status="INVALID_ESTIMATOR"))
                    continue
                fn, vn, tn = policy_sum(wa, wb, ni, gap["A"][i], gap["B"][i])
                fo, vo, to = policy_sum(oa, ob, oi, old_gap["A"][i], old_gap["B"][i])
                an, ao = constant_action(ni), constant_action(oi)
                if an is not None or ao is not None:
                    # pi_0 P_0(tau)=pi_0: a constant action's exact expected
                    # cost is the same on either telemetry side. Avoid a
                    # spurious sign from numerical semigroup roundoff at zero.
                    unconditional = float(wa@gap["A"][i] + wb@gap["B"][i])
                    if an is not None:
                        fn, vn = float(an), an*unconditional
                    if ao is not None:
                        fo, vo = float(ao), ao*unconditional
                gs = vo-vn
                row = dict(**common, status="COMPLETED", L_fresh=scale+vn, L_stale=scale+vo,
                           G_S=gs, G_S_pct_C_ref=100*gs/cref, slope_measured=gs/h,
                           regret_fresh=vn-oracle, regret_stale=vo-oracle,
                           regret_fresh_pct_C_ref=100*(vn-oracle)/cref,
                           regret_stale_pct_C_ref=100*(vo-oracle)/cref,
                           p_new=fn, p_old=fo, tie_share_fresh=tn, tie_share_stale=to,
                           concentration_new=abs(fn-.5), concentration_old=abs(fo-.5),
                           constant_action_fresh=an, constant_action_stale=ao,
                           B_inf=asym[str(tau)]["B_inf"] if rule == "M0" else None)
                row["sides"] = {side: dict(L=row["L_"+side], regret=row["regret_"+side],
                                           G_S=gs, C_ref=cref, share_switch=share, tie_share=tie)
                                for side, share, tie in (("fresh", fn, tn), ("stale", fo, to))}
                rows.append(row)
        timing["pairs"] += time.process_time()-t
    return dict(namespace=NAMESPACE, status="COMPLETED", regime=p["regime"].record(),
                T_int=p["T_int"], s=p["s"], s_hat=s_hat, rows=rows, asymptotic_m0=asym,
                timing=timing, cpu_seconds=time.process_time()-start,
                wall_seconds=time.perf_counter()-wall, observation=observation)


def uniformized_events(chain, uniforms, initial_state):
    """PL's exact blocked embedded chain generalized to the path's service."""
    gamma = chain.gamma
    uniforms = np.asarray(uniforms)
    flip = uniforms < (1/chain.kappa)/gamma
    cumulative = np.cumsum(flip, dtype=np.int64)
    before = (initial_state%2+cumulative-flip)%2
    after = (initial_state%2+cumulative)%2
    loads = chain.load+np.where(before, chain.alpha, -chain.alpha)
    boundary = (1/chain.kappa+loads)/gamma
    steps = np.zeros(len(uniforms), dtype=np.int64)
    steps[(~flip) & (uniforms < boundary)] = 1
    steps[(uniforms >= boundary) & (uniforms < boundary+chain.mu/gamma)] = -1
    backlog = pl_posterior.reflect_walk(steps, initial_state//2, chain.N)
    return 2*backlog+after


def sample_at_times(chain, times, rng, chunk_events=200000):
    """Stationary joint history at arbitrary times; exact uniformization."""
    times = np.asarray(times, dtype=float)
    if times.ndim != 1 or not len(times) or times[0] != 0 or np.any(np.diff(times) <= 0):
        raise ValueError("times must start at zero and strictly increase")
    counts = rng.poisson(chain.gamma*np.diff(times))
    ends = np.cumsum(counts, dtype=np.int64)
    total = int(ends[-1]) if len(ends) else 0
    z = np.empty(len(times), dtype=np.int64)
    state = int(rng.choice(chain.n, p=chain.pi))
    z[0] = state
    zeros = int(np.searchsorted(ends, 0, side="right"))
    z[1:zeros+1] = state
    begin, filled = 0, zeros
    while begin < total:
        size = min(chunk_events, total-begin)
        states = uniformized_events(chain, rng.random(size), state)
        end = begin+size
        last = int(np.searchsorted(ends, end, side="right"))
        if last > filled:
            z[filled+1:last+1] = states[ends[filled:last]-begin-1]
        begin, filled, state = end, last, int(states[-1])
    if filled != len(times)-1:
        raise ArithmeticError("history polling endpoints missing")
    return z, dict(method="exact_uniformization_no_Poisson_tail_cutoff", gamma=chain.gamma,
                   embedded_events=total, observations=len(times), W=float(times[-1]))


def history_pairs(chain, tint, age_multiple, rng, count=PAIR_COUNT):
    W, tau = 100*tint, age_multiple*tint
    old_times = np.linspace(0., W-tau, count)
    new_times = old_times+tau
    times = np.unique(np.r_[old_times, new_times])
    z, info = sample_at_times(chain, times, rng)
    return z[np.searchsorted(times, old_times)], z[np.searchsorted(times, new_times)], dict(
        **info, pairs=count, tau=tau, overlapping_pairs=True, independent_trials=False)


def estimate_path(path, stay_load, shift, tint, rng, *, W=None):
    """Literal W2 count estimator with mu-specific domain validation.

    Reuses shat2 simulation and covariance. No parameter clipping (apart from
    the prescribed alpha^2 floor), no M/M/1 or true-s fallback.
    """
    W = 100*tint if W is None else float(W)
    delta = shat2.BIN_WIDTH
    count = int(math.floor(W/delta))
    if count < 2:
        raise ValueError("finite count record needs at least two complete bins")
    # Same bounded-memory count buffer as W2, under the allowed result root.
    import tempfile
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="counts_", dir=OUT) as directory:
        counts = np.memmap(Path(directory)/"counts.i4", mode="w+", dtype="<i4", shape=(count,))
        record = shat2.simulate_counts(stay_load, path.alpha, path.kappa, W, rng, counts, delta)
        mean = float(np.sum(counts, dtype=float)/count)
        ss = 0.
        for start in range(0, count, shat2.CHUNK_BINS):
            centered = np.asarray(counts[start:start+shat2.CHUNK_BINS], dtype=float)-mean
            ss += float(centered @ centered)
        lam = mean/delta
        variance = ss/count/delta**2
        raw = variance-lam/delta
        alpha2 = max(0., raw)
        cov = shat2.autocovariances(counts, delta, max(1, math.ceil(50*path.kappa/delta)))
        nonpositive = np.flatnonzero(cov[1:] <= 0)
        stop = int(nonpositive[0]+1) if len(nonpositive) else None
        used = stop-1 if stop is not None else len(cov)-1
        khat = float(2*np.sum(cov[1:used+1])*delta/alpha2) if alpha2 > 0 else None
        del counts
    errors = []
    alpha = math.sqrt(alpha2)
    if khat is None or khat <= 0 or not math.isfinite(khat):
        errors.append("undefined or nonpositive kappa_hat")
    if not (alpha <= min(lam, lam+shift) and max(lam, lam+shift) < path.mu):
        errors.append("estimated action loads/amplitude outside stable nonnegative MMPP domain")
    record.update(lambda_hat=lam, alpha_hat=alpha, alpha_squared_raw=raw, kappa_hat=khat,
                  stay_load_hat=lam, switch_load_hat=lam+shift, mu=path.mu, variance_ddof=0,
                  rate_variance=variance, first_nonpositive_lag=stop, positive_lags_summed=used,
                  max_lag_bins=len(cov)-1, lag_cap_reached=stop is None,
                  autocovariances=cov[:used+2].tolist(), fallback=None,
                  kappa_guess=path.kappa, kappa_guess_source="design kappa, computational lag cap only",
                  status="INVALID" if errors else "VALID", errors=errors)
    return record


def estimate_s(p, purpose):
    if purpose not in ("train", "pilot"):
        raise ValueError("only train/pilot may sample finite telemetry")
    regime = p["regime"]
    index = int(regime.id.rsplit("_", 1)[-1]) if regime.id.startswith("XCTMC_") else 0
    streams = np.random.SeedSequence([SEEDS[purpose], index, 0]).spawn(2)
    telemetry, means, errors = {}, {}, []
    for j, side in enumerate(("A", "B")):
        path = getattr(regime, side)
        shift = -regime.u if side == "A" else regime.u
        est = estimate_path(path, p["chains"][side+"st"].load, shift, p["T_int"], np.random.default_rng(streams[j]))
        telemetry[side] = est
        for action in ("stay", "switch"):
            key = side+"_"+action
            try:
                if est["status"] != "VALID":
                    raise ValueError("; ".join(est["errors"]))
                result = mmpp.stationary_mean(est[action+"_load_hat"], est["kappa_hat"], est["alpha_hat"], path.mu)
                means[key] = result.record()
            except (ValueError, ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
                errors.append(dict(chain=key, message=str(exc)))
    s_hat = None if errors else means["A_switch"]["r"]+means["B_switch"]["r"]-means["A_stay"]["r"]-means["B_stay"]["r"]
    return dict(seed=SEEDS[purpose], seed_coordinate=[SEEDS[purpose], index, 0], purpose=purpose,
                status="INVALID" if errors else "VALID", s_hat=s_hat, telemetry=telemetry,
                stationary_estimates=means, errors=errors, fallback=None)


def sampled_decisions(inputs, a_states, b_states):
    a, b = inputs["a"][a_states], inputs["b"][b_states]
    choices = a+b < 0
    if "gate" in inputs:
        choices &= inputs["gate"][a_states]
    return choices


def prediction_for(p, estimator, purpose="train", horizons=None):
    if purpose not in ("train", "pilot"):
        raise ValueError("prediction sampling uses train/pilot only")
    horizons = list(H_GRID) if horizons is None else list(horizons)
    hs = [h*p["T_int"] for h in horizons]
    regime, ch = p["regime"], p["chains"]
    index = int(regime.id.rsplit("_",1)[-1])
    rows, histories = [], {}
    for age in AGES:
        decisions = decision_vectors(p, hs, age*p["T_int"], estimator["s_hat"])
        streams = np.random.SeedSequence([SEEDS[purpose], index, age]).spawn(2)
        sampled = {}
        histories[str(age)] = {}
        for j, side in enumerate(("A", "B")):
            y, x, info = history_pairs(ch[side+"st"], p["T_int"], age, np.random.default_rng(streams[j]))
            sampled[side] = (y, x)
            histories[str(age)][side] = info
        for i, (h_multiple, h) in enumerate(zip(horizons, hs)):
            pooled = float(ch["Ast"].pi@decisions["fresh"]["A"][i] + ch["Bst"].pi@decisions["fresh"]["B"][i])
            c5_sign = -1 if (pooled < 0) == (p["s"] < 0) else 1
            for rule in RULES:
                ni = rule_inputs(p, decisions, rule, "fresh", i, h)
                oi = rule_inputs(p, decisions, rule, "stale", i, h)
                row = dict(regime=regime.id, rule=rule, h_T_int=h_multiple, tau_T_int=age,
                           c5_sign=c5_sign if rule == "M0" else None,
                           pooled_switch=bool(pooled < 0), long_run_switch=bool(p["s"] < 0))
                if ni is None or oi is None:
                    rows.append(dict(**row, status="INVALID_ESTIMATOR", slope_pred=None, sign_pred=None))
                    continue
                fresh = sampled_decisions(ni, sampled["A"][1], sampled["B"][1])
                stale = sampled_decisions(oi, sampled["A"][0], sampled["B"][0])
                pn, po = float(fresh.mean()), float(stale.mean())
                df = po-pn
                s_hat = estimator["s_hat"]
                su = utilization_null(regime)
                slope = None if s_hat is None else s_hat*df
                rows.append(dict(**row, status="COMPLETED", p_new_hat=pn, p_old_hat=po,
                                 DeltaF_hat=df, slope_pred=slope, sign_pred=None if slope is None else int(np.sign(slope)),
                                 null_s_U=su, null_slope=su*df, null_sign=int(np.sign(su*df)),
                                 concentration_new_hat=abs(pn-.5), concentration_old_hat=abs(po-.5)))
    return dict(regime=regime.record(), T_int=p["T_int"], estimator=estimator,
                seed=SEEDS[purpose], purpose=purpose, rows=rows, histories=histories,
                rows_independent_trials=False, finite_h_truth_computed=False)


@contextmanager
def cpu_limit(seconds):
    previous = resource.getrlimit(resource.RLIMIT_CPU)
    handler = signal.getsignal(signal.SIGXCPU)
    def stop(signum, frame):
        raise TimeoutError("per-regime CPU cap reached; no retry")
    soft = max(1, math.ceil(time.process_time()+seconds))
    if previous[1] != resource.RLIM_INFINITY:
        soft = min(soft, previous[1])
    signal.signal(signal.SIGXCPU, stop)
    resource.setrlimit(resource.RLIMIT_CPU, (soft, previous[1]))
    try:
        yield
    finally:
        resource.setrlimit(resource.RLIMIT_CPU, previous)
        signal.signal(signal.SIGXCPU, handler)


def save_design(out):
    target = out/"design_snapshot.md"
    if target.exists():
        if sha(target) != DESIGN_SHA256:
            raise ValueError("design snapshot changed")
    else:
        if sha(BRIEF) != DESIGN_SHA256:
            raise ValueError("brief differs from ad3db0d Appendix A")
        write_once(target, BRIEF.read_text())


def pilot_selection(metadata):
    return sorted(metadata, key=lambda r: (-r["state_pair"], r["id"]))[:4]


def project_costs(metadata, results):
    """Conservative component work scaling, no outcome-based exclusions."""
    lookup = {r["id"]: r for r in metadata}
    factors = dict(values=100., posterior=(2*len(H_GRID)+3)/(2*len(PILOT_H)+3),
                   pairs=len(H_GRID)/len(PILOT_H), training=0.)
    coefficients = {}
    for part in factors:
        valid = [r for r in results if r["status"] == "COMPLETED"]
        coefficients[part] = max((r["timing"][part]/max(lookup[r["id"]]["work"][part], 1.)
                                  for r in valid), default=None)
    rows = []
    for row in metadata:
        cost = (None if any(v is None for v in coefficients.values()) else
                sum(coefficients[k]*row["work"][k]*v for k, v in factors.items()))
        # Noncompleted pilots only establish a cost lower bound; exclude them,
        # and any unseen regime at least as costly in generator*size work.
        timed_out = [r for r in results if r["status"] == "NOT_RUN_CPU_CAP"]
        censored = any(row["work"]["values"] >= lookup[r["id"]]["work"]["values"] for r in timed_out)
        reason = ("PILOT_COST_LOWER_BOUND" if censored else "PROJECTION_UNAVAILABLE" if cost is None else
                  "PROJECTED_CPU_CAP" if cost > REGIME_CPU_CAP else None)
        rows.append(dict(id=row["id"], projected_truth_cpu_seconds=cost,
                         status="PLANNED" if reason is None else "NOT_RUN", reason=reason,
                         state_pair=row["state_pair"]))
    return rows, dict(coefficients=coefficients, scale_factors=factors,
                     rule="worst completed pilot coefficient per component; cost only; cap 3600 CPU-s per regime",
                     caveat="Four timing samples at h=T_int. Full V scales to 100*T_int; batched posteriors scale by columns. Projection is not a guarantee/CI. No arbitrary state-product threshold is invented; its cost enters sparse workload and pilot ranking.")


def pilot(out=OUT):
    require_environment()
    if (out/"lock.json").exists() or (out/"truth_started.json").exists():
        raise RuntimeError("pilot refused after lock/truth")
    save_design(out)
    write_once(out/"pilot_source.py", Path(__file__).read_text())
    start, wall = time.process_time(), time.perf_counter()
    regimes, sampling = generate_grid()
    metadata = [preparation_metadata(prepare(r)) for r in regimes]
    grid = dict(namespace=NAMESPACE, owner="Doan Van Tai", seed=SEEDS["grid"],
                sampling=sampling, regimes=[dict(**r.record(), **{k:v for k,v in parameter_comparison(r).items()
                                                                 if k != "stratum"}) for r in regimes],
                metadata=metadata, truth_status="NOT_RUN")
    write_once(out/"regimes.json", grid)
    selected = pilot_selection(metadata)
    write_once(out/"pilot_plan.json", dict(created_utc=stamp(), source_sha256=sha(__file__),
        design_sha256=DESIGN_SHA256, seed=SEEDS["pilot"], ids=[r["id"] for r in selected],
        selection="largest |X_A|*|X_B|, then id", h_T_int=list(PILOT_H), tau_T_int=list(AGES),
        cpu_cap_per_regime=REGIME_CPU_CAP, no_other_finite_h_outcomes=True))
    by_id = {r.id:r for r in regimes}
    results = []
    for meta in selected:
        t, w = time.process_time(), time.perf_counter()
        event("pilot_start", regime=meta["id"], state_pair=meta["state_pair"], T_int=meta["T_int"])
        record = dict(id=meta["id"], purpose="pilot", seed=SEEDS["pilot"])
        try:
            with cpu_limit(REGIME_CPU_CAP):
                p = prepare(by_id[meta["id"]])
                t_train = time.process_time()
                estimator = estimate_s(p, "pilot")
                train_seconds = time.process_time()-t_train
                # Actual decision-history sampling is included in pilot cost;
                # the complete forecast grid remains for predict (train seed).
                sampled = prediction_for(p, estimator, "pilot", PILOT_H)
                sample_seconds = time.process_time()-t_train-train_seconds
                result = evaluate(p, [v*p["T_int"] for v in PILOT_H],
                                  [a*p["T_int"] for a in AGES], estimator["s_hat"])
                record.update(status="COMPLETED", evaluation=result, pilot_prediction=sampled,
                              timing=dict(**result["timing"], training=train_seconds+sample_seconds))
        except TimeoutError as exc:
            record.update(status="NOT_RUN_CPU_CAP", error=str(exc), scientific_verdict="NOT_EVALUABLE")
        record.update(cpu_seconds=time.process_time()-t, wall_seconds=time.perf_counter()-w)
        write_once(out/"pilot"/(meta["id"]+".json"), record)
        results.append(record)
        event("pilot_complete", regime=meta["id"], status=record["status"],
              cpu_seconds=record["cpu_seconds"], wall_seconds=record["wall_seconds"])
    if sha(__file__) != sha(out/"pilot_source.py"):
        raise RuntimeError("source changed during pilot; preserve outputs, no retry")
    costs, projection = project_costs(metadata, results)
    total = sum(r["projected_truth_cpu_seconds"] or 0 for r in costs)
    eligible = sum(r["projected_truth_cpu_seconds"] or 0 for r in costs if r["status"] == "PLANNED")
    report = dict(namespace=NAMESPACE, owner="Doan Van Tai", created_utc=stamp(), environment=environment(),
                  design_sha256=DESIGN_SHA256, source_sha256=sha(__file__), grid_sha256=sha(out/"regimes.json"),
                  sampling=sampling, pilot_ids=[r["id"] for r in selected],
                  pilot_h_T_int=list(PILOT_H), pilot_tau_T_int=list(AGES),
                  pilot_cpu_seconds=time.process_time()-start, pilot_wall_seconds=time.perf_counter()-wall,
                  measured=[{k:v for k,v in r.items() if k not in ("evaluation", "pilot_prediction")} for r in results],
                  projection=projection, planned=costs,
                  expected_not_run=sum(r["status"] == "NOT_RUN" for r in costs),
                  projected_all64_truth_cpu_hours=total/3600,
                  projected_eligible_truth_cpu_hours=eligible/3600,
                  projection_available=all(r["projected_truth_cpu_seconds"] is not None for r in costs),
                  pilot_outputs={r["id"]:sha(out/"pilot"/(r["id"]+".json")) for r in results},
                  truth_status="NOT_RUN", score_status="NOT_RUN")
    write_once(out/"pilot.json", report)
    event("pilot_projection", expected_not_run=report["expected_not_run"],
          all64_cpu_hours=report["projected_all64_truth_cpu_hours"],
          eligible_cpu_hours=report["projected_eligible_truth_cpu_hours"])
    return report


def load_preparation(out):
    grid = json.loads((out/"regimes.json").read_text())
    regenerated, _ = generate_grid()
    if [r.record() for r in regenerated] != [
            {k:r[k] for k in ("id", "A", "B", "u", "stratum")} for r in grid["regimes"]]:
        raise ValueError("grid differs from parameter-only seed generation")
    report = json.loads((out/"pilot.json").read_text())
    if sha(out/"pilot_source.py") != report["source_sha256"]:
        raise ValueError("actual pilot source snapshot changed")
    if sha(out/"regimes.json") != report["grid_sha256"]:
        raise ValueError("pilot grid hash changed")
    for key, digest in report["pilot_outputs"].items():
        if sha(out/"pilot"/(key+".json")) != digest:
            raise ValueError("pilot output changed: "+key)
    return regenerated, grid, report


def predict(out=OUT):
    require_environment()
    if (out/"lock.json").exists() or (out/"truth_started.json").exists():
        raise RuntimeError("predict refused after lock/truth")
    regimes, _, pilot_report = load_preparation(out)
    if not pilot_report["projection_available"]:
        raise RuntimeError("pilot did not establish a usable cost projection")
    costs = {r["id"]:r for r in pilot_report["planned"]}
    rows = []
    for regime in regimes:
        cost = costs[regime.id]
        if cost["status"] != "PLANNED":
            rows.append(dict(regime=regime.record(), status="NOT_RUN", cost=cost))
            continue
        p = prepare(regime)
        estimator = estimate_s(p, "train")
        row = prediction_for(p, estimator)
        row.update(status="PLANNED", cost=cost)
        rows.append(row)
        event("prediction_complete", regime=regime.id, estimator_status=estimator["status"])
    result = dict(namespace=NAMESPACE, owner="Doan Van Tai", created_utc=stamp(),
                  code_sha256=sha(__file__), design_sha256=DESIGN_SHA256, seeds=SEEDS,
                  pilot_exposed_regimes=pilot_report["pilot_ids"],
                  pilot_exposure=dict(h_T_int=list(PILOT_H), tau_T_int=list(AGES),
                                      purpose="timing pilot; not an unseen population", reused_as_truth=False),
                  h_T_int=list(H_GRID), tau_T_int=list(AGES), rules=list(RULES),
                  records=rows, truth_status="NOT_RUN", finite_h_truth_computed=False,
                  operational_prediction="s_hat * sampled(stale Switch share - fresh Switch share)",
                  mechanism_only="C5 uses true stationary s, separately labeled; never substituted into operational slope",
                  invalid_estimator="retain regime; Hybrid_hat/Stationary_hat unavailable, no true-s or MM1 fallback",
                  aggregate_verdict="NO_PREREGISTERED_NUMERIC_PASS_THRESHOLD_IN_DESIGN; descriptive sign/slope comparisons only")
    write_once(out/"predictions.json", result)
    return result


def source_paths(out):
    names = ("experiments/letter/x_ctmc.py", "tests/test_x_ctmc.py", "experiments/letter/mmpp.py",
             "experiments/letter/shat2.py", "experiments/letter/pl_posterior.py",
             "experiments/letter/e3_agediff.py", "experiments/letter/r2_o1_check.py",
             "experiments/explore_ctmc/ctmc.py", "experiments/explore_ctmc/env.sh")
    return sorted({*(ROOT/n for n in names), out/"design_snapshot.md", out/"regimes.json",
                   out/"pilot_plan.json", out/"pilot_source.py", out/"pilot.json", out/"predictions.json",
                   *sorted((out/"pilot").glob("*.json"))})


def lock(out=OUT):
    require_environment()
    if (out/"truth_started.json").exists():
        raise RuntimeError("truth already attempted")
    pred = json.loads((out/"predictions.json").read_text())
    if pred["code_sha256"] != sha(__file__) or pred["design_sha256"] != DESIGN_SHA256:
        raise ValueError("source/design changed since predictions")
    load_preparation(out)
    result = dict(namespace=NAMESPACE, owner="Doan Van Tai", created_utc=stamp(),
                  sha256={str(p.relative_to(ROOT)):sha(p) for p in source_paths(out)},
                  environment=environment(), truth_status="NOT_RUN", no_retry_no_resume=True,
                  commit_required_before_truth=True)
    write_once(out/"lock.json", result)
    return result


def require_committed(path):
    relative = str(path.relative_to(ROOT))
    result = subprocess.run(["git", "show", "HEAD:"+relative], cwd=ROOT, capture_output=True)
    if result.returncode or result.stdout != path.read_bytes():
        raise RuntimeError("commit identical input before proceeding: "+relative)


def verify_lock(out=OUT, committed=False):
    record = json.loads((out/"lock.json").read_text())
    expected = {str(p.relative_to(ROOT)) for p in source_paths(out)}
    if record["namespace"] != NAMESPACE or set(record["sha256"]) != expected:
        raise ValueError("lock namespace/input set changed")
    for key, digest in record["sha256"].items():
        path = ROOT/key
        if sha(path) != digest:
            raise ValueError("locked file changed: "+key)
        if committed:
            require_committed(path)
    if environment() != record["environment"]:
        raise ValueError("numeric environment changed")
    if committed:
        require_committed(out/"lock.json")
    return record


def truth_worker(task):
    regime_row, prediction, out_name = task
    out = Path(out_name)
    regime = Regime.from_record(regime_row)
    verify_lock(out, committed=True)  # before chain/input computations
    start, wall = time.process_time(), time.perf_counter()
    try:
        with cpu_limit(REGIME_CPU_CAP):
            p = prepare(regime)
            result = evaluate(p, [h*p["T_int"] for h in H_GRID], [a*p["T_int"] for a in AGES],
                              prediction["estimator"]["s_hat"])
            result.update(purpose="truth", test_seed=SEEDS["test"],
                          test_rng="unused: exact deterministic quadrature, no Monte Carlo",
                          estimator=prediction["estimator"])
    except BaseException as exc:
        result = dict(namespace=NAMESPACE, regime=regime.record(), status="INCOMPLETE",
                      error_type=type(exc).__name__, error=str(exc), no_retry_no_resume=True)
    result.update(worker_cpu_seconds=time.process_time()-start, worker_wall_seconds=time.perf_counter()-wall)
    path = out/"raw"/(regime.id+".json")
    write_once(path, result)
    return dict(id=regime.id, path=str(path.relative_to(ROOT)), sha256=sha(path),
                status=result["status"], cpu_seconds=result["worker_cpu_seconds"])


def truth(out=OUT, workers=1):
    """Claude's later explicit command only; never called by preparation."""
    require_environment()
    verify_lock(out, committed=True)
    if workers < 1:
        raise ValueError("workers must be positive")
    if any((out/n).exists() for n in ("truth_started.json", "truth_receipt.json", "raw")):
        raise FileExistsError("one-shot truth already attempted; no retry/resume")
    prediction = json.loads((out/"predictions.json").read_text())
    planned = [r for r in prediction["records"] if r["status"] == "PLANNED"]
    if not planned:
        raise RuntimeError("empty eligible population")
    write_once(out/"truth_started.json", dict(namespace=NAMESPACE, created_utc=stamp(),
        lock_sha256=sha(out/"lock.json"), workers=workers, cpu_cap_per_regime=REGIME_CPU_CAP,
        ids=[r["regime"]["id"] for r in planned], no_retry_no_resume=True))
    wall, outputs, error = time.perf_counter(), [], None
    try:
        context = multiprocessing.get_context("spawn")
        tasks = [(r["regime"], r, str(out)) for r in planned]
        with context.Pool(workers, maxtasksperchild=1) as pool:
            for item in pool.imap_unordered(truth_worker, tasks):
                outputs.append(item)
                event("truth_regime_complete", **item)
        verify_lock(out, committed=True)
    except BaseException as exc:
        error = dict(type=type(exc).__name__, message=str(exc))
        raise
    finally:
        complete = error is None and len(outputs) == len(planned) and all(r["status"] == "COMPLETED" for r in outputs)
        write_once(out/"truth_receipt.json", dict(namespace=NAMESPACE, created_utc=stamp(),
            status="COMPLETED_RAW_UNSCORED" if complete else "INCOMPLETE", error=error,
            expected_regimes=len(planned), completed_regimes=sum(r["status"] == "COMPLETED" for r in outputs),
            raw=sorted(outputs, key=lambda r:r["id"]), wall_seconds=time.perf_counter()-wall,
            worker_cpu_seconds=sum(r["cpu_seconds"] for r in outputs), no_retry_no_resume=True))


def score(out=OUT):
    """Report sign/slope comparisons; design specifies no aggregate cutoffs."""
    require_environment()
    verify_lock(out, committed=True)
    receipt = json.loads((out/"truth_receipt.json").read_text())
    if receipt["status"] != "COMPLETED_RAW_UNSCORED":
        raise ValueError("incomplete truth cannot be scored")
    require_committed(out/"truth_receipt.json")
    prediction = json.loads((out/"predictions.json").read_text())
    forecasts = {(r["regime"]["id"], v["rule"], v["h_T_int"], v["tau_T_int"]):v
                 for r in prediction["records"] if r["status"] == "PLANNED" for v in r["rows"]}
    comparisons, all_rows = [], []
    for entry in receipt["raw"]:
        path = ROOT/entry["path"]
        if sha(path) != entry["sha256"]:
            raise ValueError("raw checksum mismatch")
        require_committed(path)
        raw = json.loads(path.read_text())
        if raw["status"] != "COMPLETED":
            raise ValueError("noncompleted regime")
        all_rows.extend(raw["rows"])
        for row in raw["rows"]:
            h, age = int(round(row["h_T_int"])), int(round(row["tau_T_int"]))
            if h not in (30, 100):
                continue
            pred = forecasts[(raw["regime"]["id"], row["rule"], h, age)]
            valid = row["status"] == "COMPLETED" and pred.get("slope_pred") is not None
            actual = int(np.sign(row["G_S"])) if valid else None
            comparisons.append(dict(regime=raw["regime"]["id"], rule=row["rule"], h_T_int=h, tau_T_int=age,
                status="COMPLETED" if valid else "NOT_EVALUABLE", sign_measured=actual,
                sign_pred=pred.get("sign_pred"), sign_matches=None if not valid else actual == pred["sign_pred"],
                null_sign_matches=None if not valid else actual == pred["null_sign"],
                slope_measured=row.get("slope_measured"), slope_pred=pred.get("slope_pred"),
                slope_absolute_error=None if not valid else abs(row["slope_measured"]-pred["slope_pred"]),
                c5_sign=pred["c5_sign"], c5_matches=None if not valid or row["rule"] != "M0" else actual == pred["c5_sign"]))
    summary = {}
    for rule in RULES:
        group = [r for r in comparisons if r["rule"] == rule]
        valid = [r for r in group if r["status"] == "COMPLETED"]
        observed = [r for r in all_rows if r["rule"] == rule and r["status"] == "COMPLETED"]
        summary[rule] = dict(planned=len(group), evaluable=len(valid), not_evaluable=len(group)-len(valid),
                             sign_matches=sum(r["sign_matches"] for r in valid),
                             null_sign_matches=sum(r["null_sign_matches"] for r in valid),
                             harm_cells=sum(r["G_S"] < 0 for r in observed), total_cells=len(observed))
    result = dict(namespace=NAMESPACE, owner="Doan Van Tai", created_utc=stamp(),
                  aggregate_verdict="NOT_SPECIFIED_BY_DESIGN", summary=summary, comparisons=comparisons,
                  note="No aggregate scientific PASS/FAIL threshold invented. Regime/age/horizon cells are dependent.")
    write_once(out/"scores.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pilot", "predict", "lock", "verify-lock", "truth", "score"))
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.command == "truth":
        truth(workers=args.workers)
    elif args.command == "verify-lock":
        result = verify_lock()
        event("lock_verified", files=len(result["sha256"]))
    else:
        globals()[args.command]()


if __name__ == "__main__":
    main()
