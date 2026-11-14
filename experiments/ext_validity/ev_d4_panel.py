"""Doan Van Tai — EV-D4: telemetry-age dose response on a 4 h continuous MAWI trace (DITL 2023-04-12 10:00-14:00 JST
window of files 202304121000..1345), predictions from the TRAIN seed only, and scoring [AI (Claude) theo ủy quyền 14/11/2026].

Changes against EV-D3a/b, decided after the independent audit (notes/ops/codex/AUDIT_report.md) and BEFORE any EV-D4
train/test output existed:
- audit B3: paths A and B replay two disjoint flow samples (s0, s1) of the same link with ONE shared phase (real-time
  alignment; packet.background with path_keys). EV-D3 used one key with two independent phases, so the A-B relative
  phase was fixed within a run and random across runs.
- audit B1: T12 says the plug-in effect has no h-linear term, not that it is above -0.25 % at a finite h. D1 is kept for
  continuity (practical reading); D6 tests the T12 statement itself (no growth from h = 10 to h = 30 T_int).
- six telemetry ages and a dose-response check D5.

    python -m experiments.ext_validity.ev_d4_panel series DIR   # 16 x (.bin, .json) from trace_rates.c -> series npz
    python -m experiments.ext_validity.ev_d4_panel design
    python -m experiments.ext_validity.packet train --cases results/ext_validity/ev_d4/cases.json --out results/ext_validity/ev_d4/train --workers N
    python -m experiments.ext_validity.ev_d4_panel predict      # train JSON only (no D, no test)
    python -m experiments.ext_validity.ev_d4_run N [i/n]        # test seed
    python -m experiments.ext_validity.ev_d4_panel score
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_d4'
CASES, PRED = OUT / 'cases.json', OUT / 'predictions.csv'
SERIES = 'results/ext_validity/ev_d4/series_ditl4h_mod10.npz'   # attempt 2 (attempt 1 = mod 250, see ATTEMPT1.md)
SEED = 20261221
STRATA = dict(neg=(-1.5, -0.1, 8), band=(0.02, 0.35, 4), pos=(0.4, 1.5, 8))
TAUS = (1, 10, 30, 60, 120, 300)
NOWCAST = (('fluid_nowcast', 'F_old_fluid_nowcast', 'F_new'), ('ratefluid_nowcast', 'F_old_ratefluid_nowcast', 'F_new_rate'))
PLUGIN = ('fluid', 'ratefluid')
BIN_NS = 10_000_000
MOD = 10   # Claude, attempt 2: paths = two disjoint 10 % flow subsets. Attempt 1 (MOD 250, volume-matched to EV-D3b) gave
           # train T_int median 1445 s, so all 120 cases failed the pre-train rule 30*T_int <= 7200 s (see attempt1_mod250/ATTEMPT1.md)


def series(src):
    """Concatenate consecutive 15-min files on one 10 ms grid anchored at the first file's first packet. Each file's
    last (incomplete) bin is dropped; a later file overwrites an overlap; gap bins get the mean of the 1000 bins before."""
    src = Path(src)
    metas = sorted(src.glob('*.json'))
    first = json.loads(metas[0].read_text())['start_ns']
    parts, info = [], []
    for m in metas:
        meta = json.loads(m.read_text())
        raw = m.with_suffix('.bin').read_bytes()
        counts = np.frombuffer(raw, dtype='<i4').reshape(-1, 3)[:-1]
        assert len(counts) == meta['bins'] - 1 and meta['bin'] == 0.01 and meta['mod'] == MOD
        off = int(round((meta['start_ns'] - first) / BIN_NS))
        parts.append((off, counts))
        info.append(dict(file=m.stem, offset_bins=off, bins=len(counts), packets=meta['packets'],
                         bin_sha256=hashlib.sha256(raw).hexdigest()))
    n = max(o + len(c) for o, c in parts)
    arr, filled = np.zeros((n, 3), dtype=np.int64), np.zeros(n, dtype=int)
    for off, c in parts:
        arr[off:off + len(c)] = c
        filled[off:off + len(c)] += 1
    gaps = np.flatnonzero(filled == 0)
    for g in gaps:
        arr[g] = np.rint(arr[max(0, g - 1000):g].mean(axis=0))
    meta = dict(source='MAWI samplepoint-F DITL 2023-04-12, 16 consecutive 15-min files', files=info, bin=0.01,
                bins=int(n), overlap_bins=int((filled > 1).sum()), gap_bins_filled=int(len(gaps)),
                mod=MOD, format=f'int counts [bins]: all, s0, s1 (FNV-1a 5-tuple hash mod {MOD} == 0 / == 1)')
    out = ROOT / SERIES
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('xb') as f:
        np.savez_compressed(f, all=arr[:, 0], s0=arr[:, 1], s1=arr[:, 2], metadata=json.dumps(meta, sort_keys=True))
    out.with_suffix('.json').write_text(json.dumps(meta, indent=1) + '\n')
    print(json.dumps({k: v for k, v in meta.items() if k != 'files'}))


def describe():
    """Train-free facts about the series, for the card."""
    from experiments.ext_validity.trace_cox import autocorrelation_time
    d = np.load(ROOT / SERIES)
    res = {}
    for k in ('s0', 's1'):
        x = d[k].astype(float)
        mins = x[: len(x) // 6000 * 6000].reshape(-1, 6000).mean(axis=1) / x.mean()
        res[k] = dict(mean_per_bin=float(x.mean()), cov_10ms=float(x.std() / x.mean()), acf_integral_s=autocorrelation_time(x, .01),
                      minute_mean_ratio=[float(mins.min()), float(mins.max())])
    a, b = (d[k][: len(d[k]) // 6000 * 6000].reshape(-1, 6000).sum(axis=1) for k in ('s0', 's1'))
    res['corr_s0_s1_1min'] = float(np.corrcoef(a, b)[0, 1])
    res['hours'] = len(d['s0']) * .01 / 3600
    print(json.dumps(res, indent=1))


def design():
    from scipy.stats import qmc
    if CASES.exists():
        raise FileExistsError(CASES)
    cases, i = [], 0
    for k, (name, (lo, hi, n)) in enumerate(STRATA.items()):
        acc = 0
        for pu, pa, px in qmc.Sobol(3, scramble=True, seed=SEED + k).random(1024):
            if acc >= n:
                break
            u = 0.25 * (1 + int(pu * 12))
            lamA = 6 + 0.25 * int(pa * max(1, int((10 - u - 6) * 4)))
            x = round(lo + (hi - lo) * px, 2)
            lamB = round(lamA + x * u, 4)
            if not (lamB >= 6 and max(lamA, lamB) + u < 9.75):
                continue
            base = dict(lamA=lamA, lamB=lamB, u=u, seed=13000 + i, n_inst=10000, spacing_mult=3, train_T=100000.,
                        sample_dt=0.2, h_mult=[10, 30], batches=40)
            p = dict(series=SERIES, key='s0', path_keys=['s0', 's1'], bin=0.01)
            for tau in TAUS:
                cases.append(dict(base, id=f'L{name[0].upper()}{acc:02d}_tau{tau}', cls='trace_cox', params=p,
                                  stratum=name, trace='ditl4h', tau=float(tau)))
            acc += 1
            i += 1
    OUT.mkdir(parents=True, exist_ok=True)
    CASES.write_text(json.dumps(cases, indent=1) + '\n')
    print(len(cases), 'cases')


def predict():
    if PRED.exists():
        raise FileExistsError(PRED)
    rows = []
    for c in json.loads(CASES.read_text()):
        t = json.loads((OUT / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        for m in c['h_mult']:
            sh, h = t['shares'][str(m)], m * t['T_int']
            for name, fo, fn in NOWCAST:
                rows.append(dict(id=c['id'], cls=c['cls'], stratum=c['stratum'], tau=c['tau'], h_mult=m, twin=name,
                                 pred_abs=h * t['s_train'] * (sh[fo] - sh[fn]), s_train=t['s_train'], T_int=t['T_int']))
    with PRED.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)
    print(len(rows), 'prediction rows')


def score():
    from scipy.stats import spearmanr
    P = {(r['id'], int(r['h_mult']), r['twin']): float(r['pred_abs']) for r in csv.DictReader(PRED.open())}
    cases = json.loads(CASES.read_text())
    rec, raw = [], {}
    for c in cases:
        for m in c['h_mult']:
            f = OUT / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json"
            if not f.exists():
                continue
            g = json.loads(f.read_text())
            Es = g['E_stay']['mean']
            raw[(c['id'], m)] = g
            for twin, tw in g['twins'].items():
                pr = P.get((c['id'], m, twin))
                rec.append(dict(id=c['id'], tau=c['tau'], h_mult=m, twin=twin, G=tw['pct_E_stay'], se=tw['se_pct'],
                                pred=None if pr is None else 100 * pr / Es))
    n_exp = sum(len(c['h_mult']) for c in cases)
    n_got = len(raw)
    r30 = [r for r in rec if r['h_mult'] == 30]
    plug = [r for r in r30 if r['twin'] in PLUGIN]
    D1 = sum(r['G'] >= -max(0.25, 2 * r['se']) for r in plug) / len(plug)
    nc = [r for r in r30 if r['pred'] is not None]
    sig = [r for r in nc if abs(r['pred']) >= 0.25]
    D2 = sum((r['G'] > 0) == (r['pred'] > 0) for r in sig) / len(sig) if sig else None
    D3 = sum(abs(r['G'] - r['pred']) <= max(0.15, 0.3 * abs(r['pred'])) + 2 * r['se'] for r in nc) / len(nc)
    hyb = [r for r in rec if r['twin'] == 'ratefluid_nowcast_hybrid_train']
    D4 = sum(r['G'] >= -max(0.1, 2 * r['se']) for r in hyb) / len(hyb)
    # D5 dose response: per tau, median over cases of the two nowcast twins at h = 30, predicted vs observed
    pm, om = [], []
    for t in TAUS:
        g = [r for r in nc if r['tau'] == t]
        pm.append(float(np.median([r['pred'] for r in g])) if g else None)
        om.append(float(np.median([r['G'] for r in g])) if g else None)
    rho5 = float(spearmanr(pm, om).statistic) if None not in pm + om else None
    # D6 T12 (no h-linear term for plug-in twins): growth of the absolute effect from h10 to h30, in % of E_stay(h30);
    # se bound = se30 + se10 * E10/E30 (no CRN-covariance credit). A linear term would give about 2/3 of the h30 effect.
    d6 = []
    for c in cases:
        if (c['id'], 10) not in raw or (c['id'], 30) not in raw:
            continue
        g10, g30 = raw[(c['id'], 10)], raw[(c['id'], 30)]
        e = g10['E_stay']['mean'] / g30['E_stay']['mean']
        for tw in PLUGIN:
            a, b = g10['twins'][tw], g30['twins'][tw]
            d6.append(dict(id=c['id'], twin=tw, growth=b['pct_E_stay'] - e * a['pct_E_stay'], se=b['se_pct'] + e * a['se_pct']))
    D6 = sum(abs(r['growth']) <= max(0.25, 2 * r['se']) for r in d6) / len(d6) if d6 else None
    v = lambda x, t: 'NOT_EVALUABLE' if x is None else ('PASS' if x >= t else 'FAIL')
    inc = n_got < 0.9 * n_exp
    res = dict(completed=n_got, of=n_exp,
               D1=dict(n=len(plug), share=D1, threshold=0.9, verdict='INCONCLUSIVE' if inc else v(D1, 0.9)),
               D2=dict(n=len(sig), share=D2, threshold=0.85, verdict='INCONCLUSIVE' if inc else (v(D2, 0.85) if len(sig) >= 5 else 'NOT_EVALUABLE')),
               D3=dict(n=len(nc), share=D3, threshold=0.8, verdict='INCONCLUSIVE' if inc else v(D3, 0.8)),
               D4=dict(n=len(hyb), share=D4, threshold=0.9, verdict='INCONCLUSIVE' if inc else v(D4, 0.9)),
               D5=dict(taus=list(TAUS), median_pred=pm, median_obs=om, spearman=rho5, threshold=0.8,
                       verdict='INCONCLUSIVE' if inc else v(rho5, 0.8)),
               D6=dict(n=len(d6), share=D6, threshold=0.9, verdict='INCONCLUSIVE' if inc else v(D6, 0.9)))
    by = {}
    for t in TAUS:
        for twin in PLUGIN + ('fluid_nowcast', 'ratefluid_nowcast', 'ratefluid_nowcast_hybrid_train'):
            for m in (10, 30):
                g = [r['G'] for r in rec if r['tau'] == t and r['twin'] == twin and r['h_mult'] == m]
                by[f'tau{t}|{twin}|h{m}'] = dict(n=len(g), median=float(np.median(g)) if g else None, harm=sum(x <= -0.25 for x in g))
    res['descriptive'] = by
    (OUT / 'score.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k != 'descriptive'}, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'series':
        series(sys.argv[2])
    else:
        dict(design=design, predict=predict, score=score, describe=describe)[cmd]()
