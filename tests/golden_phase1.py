"""Doan Van Tai — L1.2 supplied worked answers, recorded on 2026-10-09.

Source: the user's attached L1.2 Parts 1 and 2, §§7/12 and §7.
These are NOT answers independently calculated on paper by Doan Van Tai.
V11 remains open; replace/add author-owned answers when available.
"""
from fractions import Fraction as F

RECORDED_DATE = "2026-10-09"
PROVENANCE = "Doan Van Tai — supplied L1.2 worked answers, recorded on 2026-10-09; not independently calculated hand answers"
ONE_QUEUE = {
    "q0": 4, "c": 3, "arrivals": [2, 5, 1, 0, 0, 6],
    "backlogs": [3, 5, 3, 0, 0, 3], "idles": [0, 0, 0, 0, 3, 0],
}
TWO_QUEUE_CASES = {
    "dl010_no_idle": {
        "cfg": dict(q0=(10, 10), bA=[2, 2], bB=[1, 1], u=2, cA=3, cB=3),
        "costs": (37, 37), "idles": ([0, 0], [0, 0]),
    },
    "dl010_with_idle": {
        "cfg": dict(q0=(10, 0), bA=[2, 2], bB=[0, 0], u=2, cA=3, cB=3),
        "costs": (23, 17), "idles": ([3, 3], [1, 1]),
    },
    "canonical_B_on": {
        "cfg": dict(q0=(2, 0), bA=[1, 1], bB=[0, 5], u=2, cA=3, cB=3),
        "costs": (6, 4), "idles": ([3, 0], [1, 2]),
    },
    "canonical_B_off": {
        "cfg": dict(q0=(2, 0), bA=[1, 1], bB=[0, 0], u=2, cA=3, cB=3),
        "costs": (4, 0), "idles": ([3, 3], [1, 3]),
    },
    "exercise_4_restore_B_backlog": {
        "cfg": dict(q0=(10, 10), bA=[2, 2], bB=[0, 0], u=2, cA=3, cB=3),
        "costs": (34, 34), "idles": ([0, 0], [0, 0]),
    },
}

# L1.3, recorded 2026-10-21 from supplied Parts 1 §§8–11 and 2 §7.
# This recording date is not a claim of independently completed paper exercises.
L1_3_RECORDED_DATE = "2026-10-21"
L1_3_PROVENANCE = "Doan Van Tai — supplied L1.3 worked answers; author hand exercises pending"
X_A, X_B, X_C, X_D = (2, 2, "on"), (2, 2, "off"), (2, 0, "on"), (2, 0, "off")
EXPECTED_COSTS = {
    X_A: (F(23, 2), F(27, 2)), X_B: (F(5), F(7, 2)),
    X_C: (F(8), F(19, 2)), X_D: (F(5), F(2)),
}
IDLE_PROBABILITIES = {X_A: (F(0), F(1)), X_B: (F(1), F(1)),
                      X_C: (F(1, 2), F(1)), X_D: (F(1), F(1))}
# Rows keyed by (state, mode slot 1), each: (Stay cost, Switch cost, Stay idle, Switch idle).
FUTURE_BRANCHES = {
    (X_A, "on"): (14, 16, [0, 0], [0, 2]),
    (X_A, "off"): (9, 11, [0, 0], [0, 2]),
    (X_B, "on"): (6, 6, [1, 0], [0, 2]),
    (X_B, "off"): (4, 1, [1, 3], [0, 2]),
    (X_C, "on"): (10, 12, [0, 0], [0, 2]),
    (X_C, "off"): (6, 7, [0, 1], [0, 2]),
    (X_D, "on"): (6, 4, [3, 0], [1, 2]),
    (X_D, "off"): (4, 0, [3, 3], [1, 3]),
}
ASYMMETRIC_EXPECTED_COSTS = (F(11, 2), F(19, 4))

# Supplementary exact derivation, 2026-10-21: X_D, H=3, p=s=1/2.
# Future tails on/on, on/off, off/on, off/off, each 1/4:
# Stay A contributes 2+2+2=6. On/off B backlogs 0,2,0 add 2, so cost=8.
# Stay totals 12,8,8,6; Switch totals 12,7,4,0; means 17/2 and 23/4.
H3_BRANCH_COSTS = {("on", "on"): (12, 12), ("on", "off"): (8, 7),
                   ("off", "on"): (8, 4), ("off", "off"): (6, 0)}
H3_EXPECTED_COSTS = (F(17, 2), F(23, 4))

# y=(2,0), tau=2, prior_on=3/4, p=3/4, s=1/4: next-mode on probability=3/4.
# Last pre-t0 mode off -> B backlog 0, regardless of starting mode:
# 0 -> on/off: (1/4)*(3/4 or 1/4) = 3/16,1/16.
# on->on -> backlog 4: 27/64,9/64; off->on -> backlog 2: 9/64,3/64.
TAU2_EPISODES = {(2, 4, "on"): F(27, 64), (2, 4, "off"): F(9, 64),
                 X_A: F(9, 64), X_B: F(3, 64), X_C: F(3, 16), X_D: F(1, 16)}

# L1.4, recorded 2026-10-21 from supplied Part 1 C1–C3 / Part 2 §7.
# Supplied worked answers; not certification of author-owned paper calculations.
L1_4_PROVENANCE = "Doan Van Tai — supplied L1.4 worked answers, recorded 2026-10-21; paper exercises pending"
DELTA_HAT_10 = {X_A: F(2), X_B: F(-1, 2), X_C: F(2), X_D: F(-5, 2)}
FACTORIAL_ROWS = {
    X_A: {"00": F(23, 2), "10": F(23, 2), "01": F(27, 2), "11": F(23, 2)},
    X_B: {"00": F(5), "10": F(7, 2), "01": F(7, 2), "11": F(7, 2)},
    X_C: {"00": F(8), "10": F(8), "01": F(19, 2), "11": F(8)},
    X_D: {"00": F(5), "10": F(2), "01": F(2), "11": F(2)},
}
FACTORIAL_MEANS = {"00": F(59, 8), "10": F(25, 4), "01": F(57, 8), "11": F(25, 4)}
FACTORIAL_CONTRASTS = {"G_S": F(9, 8), "G_M": F(1, 4), "G_SM": F(9, 8),
                       "Gamma": F(-1, 4), "G_S|M1": F(7, 8), "G_M|S1": F(0)}
FACTORIAL_ASYMMETRIC = {"G_S": 2, "G_M": 0, "Gamma": 0}

# L1.5, supplied Parts 1 A2/B2–B4, recorded 2026-10-21. Not author paper work.
L1_5_PROVENANCE = "Doan Van Tai — supplied L1.5 worked answers, recorded 2026-10-21; paper exercises pending"
CANONICAL_BELIEF = {x: F(1, 4) for x in (X_A, X_B, X_C, X_D)}
CANONICAL_I_DELTA = {X_A: F(1, 2), X_B: F(-1, 2), X_C: F(0), X_D: F(0)}
# Per-cell regret keys keep the usual order 00,10,01,11.
IDENTITY_REGRETS = {
    X_A: {"00": F(0), "10": F(0), "01": F(2), "11": F(0)},
    X_B: {"00": F(3, 2), "10": F(0), "01": F(0), "11": F(0)},
    X_C: {"00": F(0), "10": F(0), "01": F(3, 2), "11": F(0)},
    X_D: {"00": F(3), "10": F(0), "01": F(0), "11": F(0)},
}
TIE_REGRET_GOLDEN = ((F(-11, 4), F(0), F(11, 4)),
                     (F(11, 4), F(0), F(0)), (F(0), F(0), F(0)))

# L1.6 Parts A-D supplied answers, recorded 2026-10-22; paper exercises pending.
L1_6_PROVENANCE = "Doan Van Tai — supplied L1.6 A-D worked answers, recorded 2026-10-22; paper exercises pending"
M0_COSTS = {X_A: (F(23, 2), F(27, 2)), X_B: (F(4), F(7, 2)),
            X_C: (F(15, 2), F(19, 2)), X_D: (F(4), F(3, 2))}
BELIEF_TAU2 = {(2,0,"on"): F(1,4), (2,0,"off"): F(1,4),
               (2,2,"on"): F(1,8), (2,2,"off"): F(1,8),
               (2,4,"on"): F(1,8), (2,4,"off"): F(1,8)}
BELIEF_TWO_OBS_UP = {(2,4,"on"): F(9,16), (2,4,"off"): F(3,16),
                     (2,0,"off"): F(3,16), (2,0,"on"): F(1,16)}
BELIEF_TWO_OBS_EMPTY = {(2,0,"off"): F(9,16), (2,0,"on"): F(3,16),
                        (2,2,"on"): F(3,16), (2,2,"off"): F(1,16)}
