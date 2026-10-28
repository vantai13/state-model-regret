"""Independent physical Monte Carlo for L3R.3 C1/C2/C3.

Responsible: Doan Van Tai. Written by a delegated fresh AI session from the four
sources recorded in independent_mc_provenance.json, without viewing any engine.
Only NumPy/SciPy and the adjacent standalone C++ source are used. This module
does NOT implement policies: callers supply already determined binary actions.

Queue/mode order in x is (qA, mA, qB, mB); y is (qA, qB). Costs are packet*s.
Seeds and production N are supplied by the caller, never selected here.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
from typing import Mapping

import numpy as np
from scipy import optimize, sparse
from scipy.sparse.linalg import spsolve

POLICY_ORDER = ("00", "10", "01", "11")


def _slots(seconds: float, ref: int) -> int:
    if not isinstance(ref, (int, np.integer)) or ref < 1:
        raise ValueError("ref must be a positive integer")
    value = float(seconds) * 120 * ref
    if not math.isfinite(value) or value < 0 or abs(value - round(value)) > 1e-9:
        raise ValueError("time must be nonnegative with an integer number of slots")
    return int(round(value))


def _physical(lambda_bg: float, managed: float, kappa: float, mu: float) -> None:
    if not all(math.isfinite(float(v)) for v in (lambda_bg, managed, kappa, mu)):
        raise ValueError("physical parameters must be finite")
    if lambda_bg < 6 or managed < 0 or kappa < 0 or mu <= 0:
        raise ValueError("need lambda_bg>=6, managed>=0, kappa>=0, mu>0")


def _lattice(lambda_bg: float, managed: float, mu: float, ref: int):
    # Decimal input is interpreted as the decimal rational supplied by caller.
    low = (Fraction(str(lambda_bg)) - 6 + Fraction(str(managed)) - Fraction(str(mu))) / (120 * ref)
    high = low + Fraction(12, 120 * ref)
    den = math.lcm(low.denominator, high.denominator)
    ilow, ihigh = int(low * den), int(high * den)
    divisor = math.gcd(abs(ilow), abs(ihigh))
    quantum = Fraction(divisor, den)
    return float(quantum), ilow // divisor, ihigh // divisor, str(quantum)


def _lyapunov(steps: np.ndarray, keep: float, target: float) -> dict:
    """Positive eigenvector exponential drift and a stationary coupling bound.

    K(theta)=diag(exp(theta*d))P, Kr=rho*r, min(r)=1. Reflection
    adds at most b=max_m (Pr)_m * (1-exp(theta*d_m))_+ at q=0.
    Thus E_pi[V]<=A=b/(1-rho), and P_pi(q>=Q)<=A exp(-theta Q).
    The capped and unbounded stationary queues admit a monotone coupling with
    mismatch probability <=2*A*rho**t+t*A*exp(-theta*Q). The first terms
    couple each stationary queue to a zero-start queue with the same mode;
    the last term is a union bound for overflow of the zero-start queue.
    Floating-point eigenvalues/optimization are NOT interval certificates.
    """
    transition = np.array([[keep, 1 - keep], [1 - keep, keep]])
    def rho_at(theta):
        matrix = np.exp(theta * steps)[:, None] * transition
        a, b, c, d = matrix.ravel()
        return float((a + d + math.sqrt((a - d) ** 2 + 4 * b * c)) / 2)
    upper = 2.0 ** -20 / max(abs(steps))
    while rho_at(upper) >= 1.0:
        upper *= 0.5
        if upper < 1e-15:
            raise ArithmeticError("cannot resolve a strictly contracting exponential drift")
    while rho_at(upper) < 1.0:
        upper *= 2
        if upper * max(abs(steps)) > 100:
            raise ArithmeticError("failed to bracket positive drift root")
    fit = optimize.minimize_scalar(rho_at, bounds=(0, upper), method="bounded",
                                   options={"xatol": max(upper * 1e-11, 1e-15)})
    theta = float(fit.x)
    matrix = np.exp(theta * steps)[:, None] * transition
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    index = int(np.argmax(eigenvalues.real))
    rho = float(eigenvalues[index].real)
    r = np.abs(eigenvectors[:, index].real)
    r /= r.min()
    if not 0 < rho < 1 or not np.all(r > 0):
        raise ArithmeticError("no positive contracting exponential eigenvector")
    b = float(np.max((transition @ r) * np.maximum(0, 1 - np.exp(theta * steps))))
    amplitude = b / (1 - rho)
    coupling_slots = max(1, math.ceil(math.log(target / (4 * amplitude)) / math.log(rho)))
    required_cap = max(0.0, math.log(2 * coupling_slots * amplitude / target) / theta)
    return {"theta": theta, "rho": rho, "eigenvector": r.tolist(),
            "drift_b": b, "moment_amplitude_A": amplitude,
            "coupling_slots": coupling_slots, "required_cap_packets": required_cap,
            "bound_status": "analytic derivation evaluated in float64; not interval-certified"}


@dataclass
class StationaryLaw:
    lambda_bg: float
    managed: float
    kappa: float
    ref: int
    mu: float
    quantum: float
    joint: np.ndarray  # row q-index, column current-slot mode
    diagnostics: dict

    @property
    def q(self):
        return np.arange(len(self.joint), dtype=float) * self.quantum

    def sample_stationary(self, n: int, seed=None, *, rng=None):
        if not isinstance(n, (int, np.integer)) or n < 1:
            raise ValueError("n must be a positive integer")
        if rng is not None and seed is not None:
            raise ValueError("supply rng or seed, not both")
        rng = np.random.default_rng(seed) if rng is None else rng
        flat = rng.choice(self.joint.size, size=n, p=self.joint.ravel())
        return (flat // 2).astype(float) * self.quantum, (flat % 2).astype(np.uint8)

    def conditional_mode(self, y: float):
        if not math.isfinite(y) or y < 0:
            raise ValueError("y must be a nonnegative finite backlog")
        index = int(round(y / self.quantum))
        if abs(y - index * self.quantum) > 2e-10 * max(1, abs(y)):
            raise ValueError("exact conditioning requires a supported lattice backlog")
        if index >= len(self.joint):
            raise ValueError("y exceeds the stationary truncation")
        mass = float(self.joint[index].sum())
        if mass <= 0:
            raise ValueError("conditioning event has zero finite-chain probability")
        delta = self.diagnostics.get("stationary_cap_coupling_tv_bound", 0.0)
        conditional_bound = min(1.0, 2 * delta / (mass - delta)) if mass > delta else 1.0
        return self.joint[index] / mass, {
            "y": float(y), "finite_chain_marginal_mass": mass,
            "conditional_mode_cap_error_bound": conditional_bound,
            "bound_excludes_sparse_solve_numerical_error": True}


def stationary_law(lambda_bg: float, managed: float, kappa: float, ref: int = 1,
                   *, mu: float = 10.0, truncation_tv_target: float = 1e-10,
                   cap_packets: float | None = None, max_states: int = 2_000_000,
                   residual_tolerance: float = 1e-10) -> StationaryLaw:
    """IID sampling law from an independently solved capped lattice invariant.

    Supply cap_packets to audit a chosen cap; its actual bound is always reported.
    Default cap is selected using the explicit exponential coupling bound before
    any outcomes. No artificial finite buffer is applied during age/future runs.
    A residual is diagnostic, not a claimed rigorous stationary solve bound.
    """
    _physical(lambda_bg, managed, kappa, mu)
    _slots(0, ref)
    if lambda_bg + managed >= mu:
        raise ValueError("stationarity requires mean background+managed < mu")
    if not 0 < truncation_tv_target < 1 or residual_tolerance <= 0:
        raise ValueError("invalid numerical target")
    quantum, ilow, ihigh, rational_quantum = _lattice(lambda_bg, managed, mu, ref)
    keep = 0.5 if kappa == 0 else 0.5 * (1 + math.exp(-2 / (120 * ref * kappa)))
    diagnostics = {"method": "sparse regenerative invariant; anchor (q=0,mode=0)",
                   "lattice_quantum_fraction": rational_quantum,
                   "increments_lattice": [ilow, ihigh], "keep_probability": keep,
                   "numerical_solve_certified": False,
                   "truncation_tv_target": truncation_tv_target,
                   "refinement_comparison": "not automatically run; caller may request larger cap"}
    if ihigh <= 0:
        diagnostics.update({"method": "exact empty-backlog stationary law",
                            "stationary_cap_coupling_tv_bound": 0.0,
                            "tail_probability_bound": 0.0, "tail_first_moment_bound": 0.0,
                            "cap_packets": 0.0, "states": 2, "residual_l1": 0.0,
                            "residual_linf": 0.0, "negative_mass_correction": 0.0})
        return StationaryLaw(lambda_bg, managed, kappa, ref, mu, quantum,
                             np.array([[0.5, 0.5]]), diagnostics)
    lyap = _lyapunov(np.array([ilow, ihigh]) * quantum, keep, truncation_tv_target)
    desired_cap = lyap["required_cap_packets"] if cap_packets is None else float(cap_packets)
    if not math.isfinite(desired_cap) or desired_cap <= 0:
        raise ValueError("cap_packets must be positive and finite")
    cap = max(1, math.ceil(desired_cap / quantum))
    size = 2 * (cap + 1)
    if size > max_states:
        raise MemoryError(f"{size} lattice states exceed max_states={max_states}; do not silently coarsen")
    indices = np.arange(size, dtype=np.int64)
    queue, mode = indices // 2, indices % 2
    destination_q = np.clip(queue + np.where(mode == 0, ilow, ihigh), 0, cap)
    rows = np.concatenate([2 * destination_q, 2 * destination_q + 1])
    cols = np.concatenate([indices, indices])
    values = np.concatenate([np.where(mode == 0, keep, 1 - keep),
                             np.where(mode == 1, keep, 1 - keep)])
    pt = sparse.coo_matrix((values, (rows, cols)), shape=(size, size)).tocsc()
    matrix = sparse.eye(size - 1, format="csc") - pt[1:, 1:]
    relative = spsolve(matrix, pt[1:, 0].toarray().ravel(), permc_spec="COLAMD")
    weights = np.concatenate([[1.0], relative])
    if not np.all(np.isfinite(weights)) or weights.sum() <= 0:
        raise ArithmeticError("nonfinite sparse stationary solution")
    weights /= weights.sum()
    correction = float(-weights[weights < 0].sum())
    if correction > residual_tolerance:
        raise ArithmeticError(f"negative stationary mass {correction} exceeds tolerance")
    weights = np.maximum(0, weights)
    weights /= weights.sum()
    residual = pt @ weights - weights
    if np.abs(residual).sum() > residual_tolerance:
        raise ArithmeticError("stationary residual exceeds caller tolerance")
    cap_value = cap * quantum
    amplitude, theta, rho = (lyap[k] for k in ("moment_amplitude_A", "theta", "rho"))
    tail = amplitude * math.exp(-theta * cap_value)
    t = lyap["coupling_slots"]
    coupling = min(1.0, 2 * amplitude * rho ** t + t * tail)
    overflow = queue + np.where(mode == 0, ilow, ihigh) > cap
    diagnostics.update({"lyapunov": lyap, "cap_packets": cap_value, "cap_lattice": cap,
                        "states": size, "stationary_cap_coupling_tv_bound": coupling,
                        "truncation_target_met": coupling <= truncation_tv_target * (1 + 1e-12),
                        "tail_probability_bound": min(1.0, tail),
                        "tail_first_moment_bound": tail * (cap_value + 1 / theta),
                        "capped_law_overflow_flux": float(weights[overflow].sum()),
                        "residual_l1": float(np.abs(residual).sum()),
                        "residual_linf": float(np.abs(residual).max()),
                        "negative_mass_correction": correction,
                        "mode_marginal": weights.reshape(-1, 2).sum(axis=0).tolist()})
    return StationaryLaw(lambda_bg, managed, kappa, ref, mu, quantum,
                         weights.reshape(-1, 2), diagnostics)


def compare_stationary_laws(small: StationaryLaw, large: StationaryLaw) -> dict:
    """Measured cap refinement; not a substitute for a truncation error bound."""
    if (small.lambda_bg, small.managed, small.kappa, small.ref, small.mu, small.quantum) != (
            large.lambda_bg, large.managed, large.kappa, large.ref, large.mu, large.quantum):
        raise ValueError("cap comparison requires identical physical parameters and lattice")
    length = max(len(small.joint), len(large.joint))
    one, two = np.zeros((length, 2)), np.zeros((length, 2))
    one[:len(small.joint)] = small.joint
    two[:len(large.joint)] = large.joint
    return {"total_variation": float(np.abs(one - two).sum() / 2),
            "mean_backlog_difference": float(np.sum((two - one) *
                (np.arange(length) * small.quantum)[:, None])),
            "small_cap": small.diagnostics["cap_packets"],
            "large_cap": large.diagnostics["cap_packets"]}


def population_cost_truncation_bound(law_a: StationaryLaw, law_b: StationaryLaw,
                                     *, u, h, tau=1.0, c_sw=0.0) -> dict:
    """Conservative finite-cap bias allowance for full stationary C3 losses.

    Under the monotone stationary coupling, capped q<=unbounded q and a mismatch
    has probability at most delta (sum of the side coupling bounds). Every
    future action cost is bounded by B0+h*(yA+yB). For arbitrary policies,
    |E C_true-E C_cap| <= 2*B0*delta +
    2*h*sum_i[L_i*delta + A_i*exp(-theta_i*L_i)/theta_i].
    The bound covers pre-Stay age and policies that differ on a mismatch. It
    excludes sparse-solve arithmetic, numerical policy error, and quadrature;
    it does not apply to the separately declared discrete-node snapshot law.
    """
    if (law_a.ref, law_a.kappa, law_a.mu) != (law_b.ref, law_b.kappa, law_b.mu):
        raise ValueError("sides must share ref/kappa/mu")
    if not math.isclose(law_a.managed, u, abs_tol=1e-14) or law_b.managed != 0:
        raise ValueError("pre-Stay stationary laws must carry u on A and zero on B")
    _slots(h, law_a.ref)
    _slots(tau, law_a.ref)
    if not math.isfinite(c_sw) or c_sw < 0:
        raise ValueError("c_sw must be finite and nonnegative")
    delta = min(1.0, sum(law.diagnostics["stationary_cap_coupling_tv_bound"]
                         for law in (law_a, law_b)))
    if delta == 0:
        loss_bound, cutoffs = 0.0, [0.0, 0.0]
    else:
        cutoffs, moment_bound = [], 0.0
        for law in (law_a, law_b):
            lyap = law.diagnostics.get("lyapunov")
            if lyap is None:
                cutoffs.append(0.0)
                continue
            amplitude, theta = lyap["moment_amplitude_A"], lyap["theta"]
            cutoff = max(0.0, math.log(amplitude / delta) / theta)
            cutoffs.append(cutoff)
            moment_bound += cutoff*delta + amplitude*math.exp(-theta*cutoff)/theta
        pre_positive = sum(max(0.0, law.lambda_bg+6+law.managed-law.mu)
                           for law in (law_a, law_b))
        future_positive = sum(max(0.0, law.lambda_bg+6+u-law.mu)
                              for law in (law_a, law_b))
        dt = 1/(120*law_a.ref)
        b0 = h*tau*pre_positive + h*(h+dt)*future_positive/2 + c_sw
        loss_bound = 2*b0*delta + 2*h*moment_bound
    return {"full_stationary_episode_coupling_bound": delta,
            "per_policy_loss_absolute_bias_bound": loss_bound,
            "contrast_absolute_bias_bounds": {
                name: loss_bound*(4 if name == "Gamma" else 2)
                for name in ("GS", "GM", "GSM", "Gamma", "GS_given_M1", "GM_given_S1")},
            "tail_split_cutoffs_packets": cutoffs,
            "scope": "finite-cap approximation only, analytic formula in float64; excludes invariant sparse-solve arithmetic/policy error/quadrature; not interval-certified"}


@lru_cache(maxsize=1)
def _native():
    source = Path(__file__).with_name("independent_mc_native.cpp")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:20]
    directory = Path(tempfile.gettempdir()) / "state_model_regret_independent_mc"
    directory.mkdir(exist_ok=True)
    target = directory / f"mc_{digest}.so"
    if not target.exists():
        with tempfile.NamedTemporaryFile(dir=directory, suffix=".so", delete=False) as handle:
            candidate = Path(handle.name)
        try:
            subprocess.run(["g++", "-std=c++17", "-O3", "-shared", "-fPIC",
                            str(source), "-o", str(candidate)], check=True, capture_output=True)
            candidate.replace(target)
        finally:
            candidate.unlink(missing_ok=True)
    library = ctypes.CDLL(str(target))
    doubles = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags="C_CONTIGUOUS")
    modes = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags="C_CONTIGUOUS")
    library.independent_mc_age.argtypes = [ctypes.c_size_t, doubles, modes] + [ctypes.c_double] * 5 + [
        ctypes.c_uint64, ctypes.c_uint64, doubles, modes]
    library.independent_mc_future.argtypes = [ctypes.c_size_t, doubles, modes] + [ctypes.c_double] * 6 + [
        ctypes.c_uint64, ctypes.c_uint64, doubles, doubles]
    library.independent_mc_age.restype = library.independent_mc_future.restype = ctypes.c_int
    return library


def _initial(q, mode):
    q = np.ascontiguousarray(np.atleast_1d(q), dtype=np.float64)
    raw_mode = np.atleast_1d(mode)
    if q.ndim != 1 or raw_mode.shape != q.shape or np.any(q < 0) or not np.all(np.isfinite(q)):
        raise ValueError("q and mode must be matching one-dimensional finite state arrays")
    if not np.all((raw_mode == 0) | (raw_mode == 1)):
        raise ValueError("mode must be 0 or 1")
    return q, np.ascontiguousarray(raw_mode, dtype=np.uint8)


def simulate_age(q, mode, lambda_bg, managed, kappa, *, tau=1.0, ref=1, mu=10.0, seed):
    """Uncapped pre-Stay dynamics; includes transition after the final age slot."""
    _physical(lambda_bg, managed, kappa, mu)
    slots = _slots(tau, ref)
    _streams(seed)
    q, mode = _initial(q, mode)
    output, final_mode = np.empty_like(q), np.empty_like(mode)
    _native().independent_mc_age(len(q), q, mode, lambda_bg, managed, mu, 1 / (120 * ref),
                               kappa, slots, int(seed), output, final_mode)
    return output, final_mode


def simulate_future(q, mode, lambda_bg, managed_stay, managed_switch, kappa, *,
                    h, ref=1, mu=10.0, seed):
    """Side costs using one shared physical R2 sequence for both actions."""
    _physical(lambda_bg, managed_stay, kappa, mu)
    _physical(lambda_bg, managed_switch, kappa, mu)
    slots = _slots(h, ref)
    _streams(seed)
    q, mode = _initial(q, mode)
    stay, switch = np.empty_like(q), np.empty_like(q)
    _native().independent_mc_future(len(q), q, mode, lambda_bg, managed_stay,
                                  managed_switch, mu, 1 / (120 * ref), kappa,
                                  slots, int(seed), stay, switch)
    return stay, switch


def _streams(seed, count=8):
    if not isinstance(seed, (int, np.integer)) or not 0 <= seed < 2 ** 64:
        raise ValueError("seed must be an explicit uint64 integer")
    return [int(v) for v in np.random.SeedSequence(seed).generate_state(count, dtype=np.uint64)]


@dataclass
class MCDataset:
    y: np.ndarray
    x: np.ndarray
    CStay: np.ndarray
    CSwitch: np.ndarray
    metadata: dict

    def save(self, path):
        np.savez_compressed(path, y=self.y, x=self.x, CStay=self.CStay, CSwitch=self.CSwitch,
                            metadata_json=np.array(json.dumps(self.metadata, sort_keys=True)))


def sample_fixed_state(q_a, m_a, q_b, m_b, *, lambda_a, lambda_b, u, kappa,
                       h, n, seed, ref=1, mu=10.0, c_sw=0.0) -> MCDataset:
    """C1 IID future replications from one fixed current state."""
    if not isinstance(n, (int, np.integer)) or n < 1 or not math.isfinite(c_sw) or c_sw < 0:
        raise ValueError("need n>=1 and finite c_sw>=0")
    streams = _streams(seed)
    qa, ma = _initial(np.full(n, q_a), np.full(n, m_a))
    qb, mb = _initial(np.full(n, q_b), np.full(n, m_b))
    ca0, ca1 = simulate_future(qa, ma, lambda_a, u, 0.0, kappa, h=h, ref=ref, mu=mu, seed=streams[0])
    cb0, cb1 = simulate_future(qb, mb, lambda_b, 0.0, u, kappa, h=h, ref=ref, mu=mu, seed=streams[1])
    return MCDataset(np.column_stack([qa, qb]), np.column_stack([qa, ma, qb, mb]),
                     ca0 + cb0, ca1 + cb1 + c_sw,
                     {"check": "C1", "seed": int(seed), "stream_seeds": streams,
                      "n": n, "h": h, "ref": ref, "dt": 1 / (120 * ref),
                      "lambda_a": lambda_a, "lambda_b": lambda_b,
                      "u": u, "kappa": kappa, "mu": mu,
                      "c_sw": c_sw, "iid": True, "x_order": ["qA", "mA", "qB", "mB"]})


def sample_side_conditional(law: StationaryLaw, y: float, *, managed_stay: float,
                            managed_switch: float, h, n, seed, tau=1.0) -> dict:
    """C2 conditional old mode from the independently computed joint law."""
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be positive")
    streams = _streams(seed)
    mode_probability, condition = law.conditional_mode(y)
    old_mode = np.random.default_rng(streams[0]).choice(2, n, p=mode_probability).astype(np.uint8)
    old_q = np.full(n, y, dtype=float)
    q, mode = simulate_age(old_q, old_mode, law.lambda_bg, law.managed, law.kappa,
                          tau=tau, ref=law.ref, mu=law.mu, seed=streams[1])
    c0, c1 = simulate_future(q, mode, law.lambda_bg, managed_stay, managed_switch, law.kappa,
                             h=h, ref=law.ref, mu=law.mu, seed=streams[2])
    return {"y": old_q, "old_mode": old_mode, "x_q": q, "x_mode": mode,
            "CStay": c0, "CSwitch": c1, "gap": c1 - c0,
            "metadata": {"check": "C2", "seed": int(seed), "stream_seeds": streams,
                         "n": n, "tau": tau, "h": h, "condition": condition,
                         "lambda_bg": law.lambda_bg, "pre_managed": law.managed,
                         "managed_stay": managed_stay, "managed_switch": managed_switch,
                         "kappa": law.kappa, "mu": law.mu, "ref": law.ref,
                         "conditional_mode_probability": mode_probability.tolist(),
                         "stationary": law.diagnostics, "iid": True}}


def sample_population(law_a: StationaryLaw, law_b: StationaryLaw, *, u, h, n, seed,
                      tau=1.0, c_sw=0.0, y_nodes=None, node_weights=None) -> MCDataset:
    """C3 independent stationary episodes or an explicitly supplied node law.

    y_nodes=None draws the full finite stationary lattice law. For a same-law
    discrete-node audit, supply exact supported (yA,yB) rows and node_weights;
    modes still use the true stationary conditional. It is a DIFFERENT snapshot
    law, explicitly labelled in metadata. Representative policies on stationary
    samples remain bin-policy integrals, not representative-point quadrature.
    """
    if (law_a.ref, law_a.kappa, law_a.mu) != (law_b.ref, law_b.kappa, law_b.mu):
        raise ValueError("sides must share ref/kappa/mu")
    if not math.isclose(law_a.managed, u, abs_tol=1e-14) or law_b.managed != 0:
        raise ValueError("pre-Stay law must have managed u on A and zero on B")
    if not isinstance(n, (int, np.integer)) or n < 1 or not math.isfinite(c_sw) or c_sw < 0:
        raise ValueError("need n>=1 and finite c_sw>=0")
    streams = _streams(seed)
    rng = np.random.default_rng(streams[0])
    if y_nodes is None:
        if node_weights is not None:
            raise ValueError("node_weights requires y_nodes")
        ya, ma = law_a.sample_stationary(n, rng=rng)
        yb, mb = law_b.sample_stationary(n, rng=rng)
        observation_law = "independent full finite stationary lattice marginals"
    else:
        nodes = np.asarray(y_nodes, dtype=float)
        weights = np.asarray(node_weights, dtype=float)
        if nodes.ndim != 2 or nodes.shape[1] != 2 or weights.shape != (len(nodes),):
            raise ValueError("need y_nodes[M,2] and node_weights[M]")
        if np.any(weights < 0) or not np.isfinite(weights).all() or not np.isclose(weights.sum(), 1, atol=1e-12, rtol=0):
            raise ValueError("node weights must be a probability vector")
        condition_a = [law_a.conditional_mode(y) for y in nodes[:, 0]]
        condition_b = [law_b.conditional_mode(y) for y in nodes[:, 1]]
        conditional_a = np.array([item[0][1] for item in condition_a])
        conditional_b = np.array([item[0][1] for item in condition_b])
        chosen = rng.choice(len(nodes), n, p=weights / weights.sum())
        ya, yb = nodes[chosen].T.copy()
        ma = (rng.random(n) < conditional_a[chosen]).astype(np.uint8)
        mb = (rng.random(n) < conditional_b[chosen]).astype(np.uint8)
        observation_law = "supplied discrete snapshot node law; not full stationary population"
    qa, ma_now = simulate_age(ya, ma, law_a.lambda_bg, u, law_a.kappa,
                              tau=tau, ref=law_a.ref, mu=law_a.mu, seed=streams[1])
    qb, mb_now = simulate_age(yb, mb, law_b.lambda_bg, 0, law_b.kappa,
                              tau=tau, ref=law_b.ref, mu=law_b.mu, seed=streams[2])
    ca0, ca1 = simulate_future(qa, ma_now, law_a.lambda_bg, u, 0, law_a.kappa,
                               h=h, ref=law_a.ref, mu=law_a.mu, seed=streams[3])
    cb0, cb1 = simulate_future(qb, mb_now, law_b.lambda_bg, 0, u, law_b.kappa,
                               h=h, ref=law_b.ref, mu=law_b.mu, seed=streams[4])
    metadata = {"check": "C3", "seed": int(seed), "stream_seeds": streams,
                "n": n, "tau": tau, "h": h, "ref": law_a.ref, "dt": 1 / (120 * law_a.ref),
                "lambda_a": law_a.lambda_bg, "lambda_b": law_b.lambda_bg,
                "u": u, "kappa": law_a.kappa, "mu": law_a.mu,
                "c_sw": c_sw, "iid": True, "observation_law": observation_law,
                "x_order": ["qA", "mA", "qB", "mB"],
                "stationary_a": law_a.diagnostics, "stationary_b": law_b.diagnostics,
                "quadrature_warning": "Integrating bin policies is not representative-node quadrature; numerical allowance or same-law design required."}
    if y_nodes is not None:
        metadata["y_nodes"] = nodes.tolist()
        metadata["node_weights"] = weights.tolist()
        metadata["node_conditioning_a"] = [item[1] for item in condition_a]
        metadata["node_conditioning_b"] = [item[1] for item in condition_b]
    else:
        metadata["finite_cap_cost_bias_allowance"] = population_cost_truncation_bound(
            law_a,law_b,u=u,h=h,tau=tau,c_sw=c_sw)
    return MCDataset(np.column_stack([ya, yb]), np.column_stack([qa, ma_now, qb, mb_now]),
                     ca0 + cb0, ca1 + cb1 + c_sw, metadata)


def score_policies(dataset: MCDataset, actions, *, save_path=None) -> dict:
    """Paired IID loss/contrast moments. Policies must not see future arrays.

    actions mapping keys 00,10,01,11 (optionally cb0), or n*4 binary array in
    that order. The 11 policy is supplied ex ante; min(realized C) is forbidden.
    This evaluator cannot itself prove that caller policies obey information
    restrictions, optimality, or strict-gap tie handling.
    """
    names = list(POLICY_ORDER)
    if isinstance(actions, Mapping):
        if "cb0" in actions:
            names.append("cb0")
        a = np.column_stack([np.asarray(actions[name]) for name in names])
    else:
        a = np.asarray(actions)
    n = len(dataset.CStay)
    if a.shape != (n, len(names)) or not np.all((a == 0) | (a == 1)):
        raise ValueError("actions must be binary with shape (n,4), or required mapping keys")
    costs = dataset.CStay[:, None] + (dataset.CSwitch - dataset.CStay)[:, None] * a
    l00, l10, l01, l11 = costs[:, :4].T
    columns = [l00, l10, l01, l11, l00-l10, l00-l01, l00-l11,
               l10+l01-l00-l11, l01-l11, l10-l11, l11]
    metrics = ["L00", "L10", "L01", "L11", "GS", "GM", "GSM", "Gamma",
               "GS_given_M1", "GM_given_S1", "Cbar"]
    if "cb0" in names:
        cb = costs[:, 4]
        columns.extend([cb, l00-cb, cb-l10])
        metrics.extend(["Lcb0", "F", "V"])
    values = np.column_stack(columns)
    mean = values.mean(axis=0)
    sd = values.std(axis=0, ddof=1) if n > 1 else np.full(len(metrics), np.nan)
    result = {"n": n, "metric_names": metrics, "per_episode": values,
              "mean": dict(zip(metrics, mean.tolist())), "sd": dict(zip(metrics, sd.tolist())),
              "se": dict(zip(metrics, (sd / math.sqrt(n)).tolist())),
              "sum": values.sum(axis=0), "cross_sum": values.T @ values,
              "covariance": np.cov(values, rowvar=False, ddof=1) if n > 1 else None,
              "uncertainty_scope": "IID Monte Carlo only; excludes stationary sparse-solve, truncation, policy and quadrature errors"}
    if save_path is not None:
        np.savez_compressed(save_path, per_episode=values, metric_names=np.array(metrics),
                            mean=mean, sd=sd, se=sd / math.sqrt(n),
                            sum=result["sum"], cross_sum=result["cross_sum"])
    return result
