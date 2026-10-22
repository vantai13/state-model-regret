"""L1.3 — exact future trees, non-clairvoyant oracle, evaluator's D12 generator.

Author: Doan Van Tai.
Reuse the L1.2 plant; costs/regret are packet·slot with dt=1, c_sw=0.
H is a measurement design choice kept in the lesson configuration for convenience,
not a parameter of the world's law. Enumeration is only for short horizons.
"""
from fractions import Fraction as F

from experiments.lessons.l1_2_queue import rollout, two_queue_cost

CANON = dict(cA=3, cB=3, u=2, bA=1, rate_on=5, rate_off=0,
             p_onon=F(1, 2), p_offoff=F(1, 2), H=2)


def mode_paths(m0, n, p_onon, p_offoff):
    """All positive-probability mode sequences: initial known mode + n transitions."""
    if m0 not in ("on", "off") or not isinstance(n, int) or n < 0:
        raise ValueError("m0 must be on/off and n a nonnegative integer")
    if not (0 <= p_onon <= 1 and 0 <= p_offoff <= 1):
        raise ValueError("transition probabilities must be in [0,1]")
    paths = [((m0,), F(1))]
    for _ in range(n):
        next_paths = []
        for sequence, probability in paths:
            last = sequence[-1]
            keep = p_onon if last == "on" else p_offoff
            other = "off" if last == "on" else "on"
            for mode, conditional in ((last, keep), (other, 1 - keep)):
                if conditional > 0:
                    next_paths.append((sequence + (mode,), probability * conditional))
        paths = next_paths
    return paths


def _rate(mode, th):
    return th["rate_on"] if mode == "on" else th["rate_off"]


def futures(x, th):
    """B arrivals and probabilities; x fixes slot 0, w begins at slot 1."""
    if not isinstance(th["H"], int) or th["H"] < 1:
        raise ValueError("H must be a positive integer")
    for sequence, probability in mode_paths(x[2], th["H"] - 1, th["p_onon"], th["p_offoff"]):
        yield [_rate(mode, th) for mode in sequence], probability


def expected_cost(x, action, th):
    """J(a;x,theta) = sum P(w|x,theta) C(a,w), using exact supplied probabilities."""
    total = F(0)
    for bB, probability in futures(x, th):
        cost, _ = two_queue_cost(x[:2], [th["bA"]] * th["H"], bB,
                                 th["u"], th["cA"], th["cB"], action)
        total += probability * cost
    return total


def oracle(x, th):
    """Non-clairvoyant oracle knows x/law; D16 ties select Stay."""
    delta = expected_cost(x, "Switch", th) - expected_cost(x, "Stay", th)
    return ("Switch" if delta < 0 else "Stay"), delta


def p_idle(x, action, th):
    """Probability of any positive idle in either queue over the horizon."""
    probability_idle = F(0)
    for bB, probability in futures(x, th):
        _, idle = two_queue_cost(x[:2], [th["bA"]] * th["H"], bB,
                                 th["u"], th["cA"], th["cB"], action)
        if any(idle):
            probability_idle += probability
    return probability_idle


def generate_episodes(y, tau, th, prior_on):
    """Evaluator D12, NOT an S0 belief: evolve observation under Stay until t0.

    Initial mode at -tau has the declared prior independent of y. The first tau
    modes generate pre-t0 arrivals; the last mode is slot 0 and belongs to x.
    Multiple paths reaching the same state are aggregated.
    """
    if not isinstance(tau, int) or tau < 0 or not 0 <= prior_on <= 1:
        raise ValueError("tau must be a nonnegative integer and prior_on in [0,1]")
    episodes = {}
    for initial, initial_probability in (("on", prior_on), ("off", 1 - prior_on)):
        if initial_probability == 0:
            continue
        for sequence, probability in mode_paths(initial, tau, th["p_onon"], th["p_offoff"]):
            qA, _ = rollout(y[0], [th["bA"] + th["u"]] * tau, th["cA"])
            qB, _ = rollout(y[1], [_rate(mode, th) for mode in sequence[:-1]], th["cB"])
            state = (qA[-1] if qA else y[0], qB[-1] if qB else y[1], sequence[-1])
            episodes[state] = episodes.get(state, F(0)) + initial_probability * probability
    return episodes
