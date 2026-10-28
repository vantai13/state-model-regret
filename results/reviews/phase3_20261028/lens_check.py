"""Post-hoc DISCOVERY check on already-exposed A04 main-cell summaries (no engine run).

Question: does a 'constant-bias Gaussian lens' (threshold geometry with the cell's mean,
spread and average M0 bias) reproduce G_M|S1 (value of model repair when the state is known)?
If the lens strongly over-predicts, the M0 error must be concentrated away from the decision
boundary (state-dependent bias), i.e. there is structure beyond pure threshold geometry.

Inputs: results/A04/20261027_01/main_final.csv (exposed discovery data). Read-only.
"""
import csv, sys
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

path = sys.argv[1]
rows = list(csv.DictReader(open(path)))


def folded_mean(mu, s):
    return mu * (2 * norm.cdf(mu / s) - 1) + 2 * s * norm.pdf(mu / s)


def fit_sigma(mu, e_abs):
    f = lambda s: folded_mean(mu, s) - e_abs
    lo, hi = 1e-9, 1e6
    if f(lo) > 0:
        return float('nan')
    return brentq(f, lo, hi)


def band_regret(mu, s, b):
    lo, hi = sorted([0.0, -b])
    al, be = (lo - mu) / s, (hi - mu) / s
    part = mu * (norm.cdf(be) - norm.cdf(al)) + s * (norm.pdf(al) - norm.pdf(be))
    return abs(part)


print('cell  EΔ  sd_fit  bias  ratio(EΔhat/EΔ)  G_M|S1 actual  lens(const bias)  actual/lens')
out = []
for r in rows:
    mu = float(r['E_delta']); e_abs = float(r['E_pos']) + float(r['E_neg'])
    b = float(r['bias']); act = float(r['G_M_S1'])
    s = fit_sigma(mu, e_abs)
    lens = band_regret(mu, s, b) if s == s else float('nan')
    ratio = (mu + b) / mu if mu else float('nan')
    out.append((r['cell'], mu, s, b, ratio, act, lens))
    print(f"{r['cell']} {mu:7.3f} {s:6.3f} {b:7.3f} {ratio:6.2f}  {act:9.4f}  {lens:9.4f}  {act/lens if lens>0 else float('nan'):6.3f}")

same = [o for o in out if o[4] > 0]
acts = np.array([o[5] for o in same]); lens = np.array([o[6] for o in same])
print('\nsame-sign cells:', len(same))
print('median actual/lens = %.3f; mean actual = %.4f; mean lens = %.4f' % (np.median(acts / lens), acts.mean(), lens.mean()))
print('cells where lens over-predicts by >2x:', sum(acts < lens / 2), 'of', len(same))
