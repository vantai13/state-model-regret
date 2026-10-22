"""Doan Van Tai — L1.6 B2 filtering, conditional mean rollout and exact 2x2.

Observation schema: noiseless backlogs at the START of integer slots <=0.
The prior is conditional on the declared oldest observation/initialization of D.
Before t0 managed traffic stays on A. Enumeration is for short histories/horizons.
Both predictors receive one shared belief; only S1 cells receive the true state.
"""
from fractions import Fraction as F

from experiments.lessons.l1_2_queue import rollout, two_queue_cost
from experiments.lessons.l1_3_expected_cost import _rate, expected_cost, mode_paths
from experiments.lessons.l1_4_factorial import choose


def belief(history, th, prior_on):
    """Posterior at t0: eliminate incompatible paths, then normalize by evidence."""
    if not history or not 0 <= prior_on <= 1:
        raise ValueError("history must be nonempty and prior_on must be in [0,1]")
    times = [t for t, _ in history]
    if any(not isinstance(t, int) or t > 0 for t in times) or times != sorted(set(times)):
        raise ValueError("observation times must be unique increasing integers <=0")
    if any(len(q) != 2 or any(v < 0 for v in q) for _, q in history):
        raise ValueError("each observation must contain two nonnegative backlogs")
    first = times[0]
    tau = -first
    observations = {t: tuple(q) for t, q in history}
    masses, evidence = {}, F(0)
    for mode_start, p0 in (("on", prior_on), ("off", 1-prior_on)):
        if p0 == 0:
            continue
        for seq, pr in mode_paths(mode_start, tau, th["p_onon"], th["p_offoff"]):
            qA, qB = observations[first]
            compatible = True
            for k in range(tau):
                path_A, _ = rollout(qA, [th["bA"]+th["u"]], th["cA"])
                path_B, _ = rollout(qB, [_rate(seq[k], th)], th["cB"])
                qA, qB = path_A[0], path_B[0]
                next_time = first+k+1
                if next_time in observations and observations[next_time] != (qA, qB):
                    compatible = False
                    break
            if compatible:
                state = (qA, qB, seq[-1])
                masses[state] = masses.get(state, F(0))+p0*pr
                evidence += p0*pr
    if evidence == 0:
        raise ValueError("observation history is impossible under the declared law: P(history)=0")
    return {state: p/evidence for state, p in masses.items()}


def m0_cost(x, action, th):
    """Load-aware mean rollout; slot0 known, later arrivals conditional on its mode."""
    if x[2] not in ("on", "off") or not isinstance(th["H"], int) or th["H"] < 1:
        raise ValueError("mode must be on/off and H must be a positive integer")
    p_on = F(1) if x[2] == "on" else F(0)
    bB = []
    for _ in range(th["H"]):
        bB.append(p_on*th["rate_on"]+(1-p_on)*th["rate_off"])
        p_on = p_on*th["p_onon"]+(1-p_on)*(1-th["p_offoff"])
    return two_queue_cost(x[:2], [th["bA"]]*th["H"], bB, th["u"],
                          th["cA"], th["cB"], action)[0]


def predict(b, action, model, th):
    """Average state-wise predictions over the supplied SAME belief for M0/M1."""
    if model not in ("M0", "M1"):
        raise ValueError("model must be M0 or M1")
    f = m0_cost if model == "M0" else expected_cost
    return sum(p*f(x, action, th) for x, p in b.items())


def factorial_end_to_end(history, th, prior_S0, D):
    """Return (mean costs, episode costs, S0 belief); D is evaluator-only truth."""
    if not D or any(p < 0 for p in D.values()) or sum(D.values()) != 1:
        raise ValueError("D must be a nonempty normalized distribution")
    b = belief(history, th, prior_S0)
    a00 = choose(predict(b, "Switch", "M0", th)-predict(b, "Stay", "M0", th))
    a01 = choose(predict(b, "Switch", "M1", th)-predict(b, "Stay", "M1", th))
    L = {cell: F(0) for cell in ("00", "10", "01", "11")}
    rows = {}
    for x, p in D.items():
        J = {a: expected_cost(x, a, th) for a in ("Stay", "Switch")}
        a10 = choose(m0_cost(x, "Switch", th)-m0_cost(x, "Stay", th))
        a11 = choose(J["Switch"]-J["Stay"])
        ell = {"00": J[a00], "10": J[a10], "01": J[a01], "11": J[a11]}
        rows[x] = ell
        for cell in L:
            L[cell] += p*ell[cell]
    return L, rows, b


def cost_with_current_backlog(D, th, model):
    """Diagnostic S0^(tau=0): condition evaluator D on current backlog, hide mode."""
    groups = {}
    for x, p in D.items():
        if p > 0:
            groups.setdefault(x[:2], {})[x] = p
    total = F(0)
    for group in groups.values():
        mass = sum(group.values())
        b = {x: p/mass for x, p in group.items()}
        action = choose(predict(b, "Switch", model, th)-predict(b, "Stay", model, th))
        total += sum(p*expected_cost(x, action, th) for x, p in group.items())
    return total
