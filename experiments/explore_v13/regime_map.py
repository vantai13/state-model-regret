"""Doan Van Tai — classify explored regimes into a state/model regime map [EXPLORATION ONLY].

AI (Claude) theo ủy quyền ("tự thiết kế và chạy… bản đồ regime"). Reads saved regimes.csv files;
no engine call. Threshold = contract eps_R = 1% of Cbar (a reading aid, not a test).

Classes (per regime, % of Cbar_ref):
  STATE_HARM : G_S <= -1                      (fresh state + mean-field model makes decisions worse)
  BOTH       : G_S >= 1 and G_M >= 1
  STATE_DOM  : G_S >= 1 and G_M < 1           (state repair worth it, model repair not)
  MODEL_DOM  : G_M >= 1 and G_S < 1 (and G_S > -1)
  JOINT      : G_S < 1, G_M < 1, G_SM >= 1 and Gamma >= max(G_S, G_M)  (complementarity: each repair
               alone is small and the interaction is the largest component; carved out of NEITHER, so a
               regime just under the threshold plus a small Gamma stays NEITHER)
  NEITHER    : |G_S| < 1, G_M < 1 and not JOINT
Intrinsic axes (each repair measured with the *other* one already perfect):
  x = G_S|M1 / Cbar  value of current state when the model is right (EVPPI-like)
  y = G_M|S1 / Cbar  value of the right model when the state is known
"""
import csv
from pathlib import Path

EPS = 1.0
ORDER = ('STATE_DOM', 'MODEL_DOM', 'BOTH', 'JOINT', 'STATE_HARM', 'NEITHER')


def classify(gs, gm, gsm=float('-inf')):
    if gs <= -EPS:
        return 'STATE_HARM'
    if gs >= EPS and gm >= EPS:
        return 'BOTH'
    if gs >= EPS:
        return 'STATE_DOM'
    if gm >= EPS:
        return 'MODEL_DOM'
    if gsm >= EPS and gsm - gs - gm >= max(gs, gm):
        return 'JOINT'
    return 'NEITHER'


def load(paths):
    rows = []
    for path in paths:
        for r in csv.DictReader(open(path)):
            f = {k: float(r[k]) for k in r if k not in ('id',)}
            f['id'] = r['id']
            f['source'] = Path(path).parent.name
            f.setdefault('age', 1.0)    # stages before the age/amp extension used the inherited plant
            f.setdefault('amp', 6.0)
            f.setdefault('c_sw', 0.0)
            f['class'] = classify(f['G_S_pctC'], f['G_M_pctC'], f['G_SM_pctC'])
            rows.append(f)
    return rows
