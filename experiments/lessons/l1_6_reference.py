"""Doan Van Tai — evaluator reference for short-history posterior verification.

Uses a Cartesian product and direct transition products, never the controller's
belief(), mode_paths(), or forward-filter code. Reuses the declared L1.2 plant.
This is a computational cross-check, not an independent human scientific review.
"""
from fractions import Fraction as F
from itertools import product

from experiments.lessons.l1_2_queue import rollout


def history_reference(history, th, prior_on):
    """Return (conditional D, evidence, path records) under explicit initialization."""
    first, initial = history[0]
    tau = -first
    masses, records = {}, []
    for sequence in product(("on", "off"), repeat=tau+1):
        probability = prior_on if sequence[0] == "on" else 1-prior_on
        for prev, current in zip(sequence, sequence[1:]):
            keep = th["p_onon"] if prev == "on" else th["p_offoff"]
            probability *= keep if current == prev else 1-keep
        if probability == 0:
            continue
        compatible = True
        for time, observed in history[1:]:
            n = time-first
            qA, _ = rollout(initial[0], [th["bA"]+th["u"]]*n, th["cA"])
            rates = [th["rate_on"] if m == "on" else th["rate_off"] for m in sequence[:n]]
            qB, _ = rollout(initial[1], rates, th["cB"])
            generated = (qA[-1] if qA else initial[0], qB[-1] if qB else initial[1])
            if generated != tuple(observed):
                compatible = False
        qA, _ = rollout(initial[0], [th["bA"]+th["u"]]*tau, th["cA"])
        qB, _ = rollout(initial[1], [th["rate_on"] if m == "on" else th["rate_off"]
                                   for m in sequence[:tau]], th["cB"])
        state = (qA[-1] if qA else initial[0], qB[-1] if qB else initial[1], sequence[-1])
        if compatible:
            masses[state] = masses.get(state, F(0))+probability
        records.append(dict(modes=" -> ".join(sequence), prior_path_probability=probability,
                            compatible=compatible, qA0=state[0], qB0=state[1], mode0=state[2]))
    evidence = sum(masses.values(), F(0))
    posterior = {x: p/evidence for x, p in masses.items()} if evidence else {}
    return posterior, evidence, records
