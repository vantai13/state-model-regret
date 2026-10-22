"""L1.2: deterministic F1 plant, idle capacity, and end-of-slot D13 cost.

Author: Doan Van Tai.
Scientific purpose: verify the two queue identities and the no-idle control.
Arrivals precede service (D1); managed traffic is conserved (D5); c_sw = 0.
Use int/Fraction inputs for exact comparisons. No random sampling is used.
This lesson implementation is not the Phase 3 smr.plant or network validation.
"""


def step(q, a, c):
    """Return (end-of-slot backlog, unused capacity) for one queue."""
    if q < 0 or a < 0 or c < 0:
        raise ValueError("q, a, c must be nonnegative")
    available = q + a
    served = min(available, c)
    return available - served, c - served


def rollout(q0, arrivals, c):
    """Return backlogs q_1..q_H and idles I_0..I_(H-1); omit q0."""
    if q0 < 0 or c < 0:
        raise ValueError("q0 and c must be nonnegative")
    backlogs, idles = [], []
    q = q0
    for arrival in arrivals:
        q, idle = step(q, arrival, c)
        backlogs.append(q)
        idles.append(idle)
    return backlogs, idles


def two_queue_cost(q0, bA, bB, u, cA, cB, action, dt=1):
    """D13 cost on one shared future; packet·slot at dt=1, packet·s in seconds."""
    if action not in ("Stay", "Switch"):
        raise ValueError("action must be 'Stay' or 'Switch'")
    if len(q0) != 2 or len(bA) != len(bB):
        raise ValueError("q0 must have two entries; backgrounds must share H")
    if u < 0 or dt <= 0 or any(b < 0 for b in (*bA, *bB)):
        raise ValueError("traffic must be nonnegative and dt must be positive")
    managed = (u, 0) if action == "Stay" else (0, u)
    qA, iA = rollout(q0[0], [b + managed[0] for b in bA], cA)
    qB, iB = rollout(q0[1], [b + managed[1] for b in bB], cB)
    return dt * (sum(qA) + sum(qB)), [a + b for a, b in zip(iA, iB)]
