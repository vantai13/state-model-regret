"""Doan Van Tai — switching cost c_sw > 0 in the HARM region of ctmc-v1: a zero-fit test of the pooling + bias
mechanism [EXPLORATION ONLY; AI (Claude) theo ủy quyền 14/11/2026: "tự thiết kế và kiểm tra… bằng chứng thật mạnh"].

Design: results/explore_ctmc/csw_harm/DESIGN_CSW_HARM.md. Stage F (PREDICTIONS_csw.md) tested c > 0 only on six
help-band bases; THREATS K7 reads it as "harm vanishes when c > 0", which was never tested where harm lives.

Prediction (zero fit, M0 and stationary quantities only, written before any truth):
    z_pred1(c, h) = 100 (h s (F_old(c) - F_new(c)) + B(c)) / (h r_min + beta_C(c))       (ctmc.evaluate_m0)
Rivals: K7-literal (c removes harm) and the empirical null G_S(c, h) = G_S(0, h) (uses the c = 0 truth).

    python -m experiments.explore_ctmc.csw_harm design             # fresh panel (write-once, no truth)
    python -m experiments.explore_ctmc.csw_harm predict --workers N # zero-fit numbers (write-once, no truth)
    python -m experiments.explore_ctmc.csw_harm lock                # after the card; commit before truth
    python -m experiments.explore_ctmc.csw_harm truth --workers N --out DIR
    python -m experiments.explore_ctmc.csw_harm mc --out DIR        # independent Monte Carlo check of the truth
    python -m experiments.explore_ctmc.csw_harm score --out DIR
"""
import argparse
import csv
import hashlib
import json
import math
import multiprocessing
import platform
import resource
import signal
import socket
import statistics as st
import sys
import time
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import scipy

from experiments.explore_ctmc import ctmc as C

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/csw_harm'
DESIGN = OUT / 'DESIGN_CSW_HARM.md'
CARD = OUT / 'CARD_CSW_HARM.md'
CASES = OUT / 'cases_csw_harm.json'
PRED = OUT / 'predictions_csw_harm.csv'
LOCK = OUT / 'lock_csw_harm.json'
SEED = 20261141                                   # 20261117 shared Sobol streams with earlier panels (seed + k); discarded before any prediction
COUNTS = dict(neg=15, pos=15)                     # harm region only (I_Delta / L7.5 strata x < -0.1, x > 0.4)
C_GRID = [F(0), F(1, 4), F(1, 2), F(1), F(2), F(4)]
H_MULT = [F(1), F(3), F(10), F(30)]               # x T_int_max; the first-order law is scored from 3 T_int (AS-R1)
N_MAX = 2500                                      # cost filter on the truncation (both paths), fixed before truth
CAP = 3600                                        # CPU-s per (regime, c) truth job
TOL = 0.1                                         # pp, inherited from F-R1 / L72-2
HARM = 0.25                                       # pp, inherited from F-R2
MC_UNITS = 6
MC_EPISODES = 40000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(case):
    lamA, lamB, u, kappa = (F(x) for x in case['parameters'][:4])
    return lamA, lamB, u, kappa, [F(h) for h in case['hs']]


# ------------------------------------------------------------------------------------------------- panel (no truth)

def seen_all():
    from experiments.explore_ctmc import design_l75 as L75
    from experiments.explore_ctmc import idelta2 as D2
    seen = D2.seen_all() | L75.seen_tuples()
    for path in (ROOT / 'results/explore_ctmc/idelta/cases_fresh.json', ROOT / 'results/explore_ctmc/idelta/cases_r3.json',
                 ROOT / 'results/explore_ctmc/ce_knockout/cases_ce.json'):
        seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads(path.read_text())}
    return seen


def design():
    from scipy.stats import qmc
    from experiments.explore_ctmc import design_l75 as L75
    from experiments.explore_ctmc import tau as T5
    from experiments.explore_ctmc.design import rational
    if CASES.exists():
        raise FileExistsError(f'{CASES} is write-once')
    if not DESIGN.exists():
        raise FileNotFoundError('the design must exist before the panel')
    seen = seen_all()
    n_seen = len(seen)
    cases, report = [], {}
    for k, name in enumerate(COUNTS):
        lo, hi = L75.STRATA[name]
        pts = qmc.Sobol(4, scramble=True, seed=SEED + k).random(2048)
        acc, drop = [], dict(domain=0, seen=0, cost=0)
        for j, (pu, pa, px, pk) in enumerate(pts):
            if len(acc) >= COUNTS[name]:
                break
            u = F(1, 4) * (1 + int(pu * 12))
            steps = int((F(10) - u - 6) * 4)
            if steps < 1:
                drop['domain'] += 1
                continue
            lamA = 6 + F(int(pa * steps), 4)
            x = F(round(float(lo + (hi - lo) * F(px)) * 100), 100)
            lamB = lamA + x * u
            if not (lamB >= 6 and lamB + u < 10 and x != 0):
                drop['domain'] += 1
                continue
            kappa = rational(math.exp(math.log(1 / 20) + pk * (math.log(2) - math.log(1 / 20))))
            key = (lamA, lamB, u, kappa)
            if key in seen or T5.is_control(key):
                drop['seen'] += 1
                continue
            Tm, _, NA, NB = T5.tint_max(lamA, lamB, u, kappa)
            if max(NA, NB) > N_MAX:
                drop['cost'] += 1
                continue
            seen.add(key)
            acc.append(dict(id=f'H{name[0].upper()}{j:04d}', parameters=[str(v) for v in (lamA, lamB, u, kappa)],
                            hs=[str(rational(m * Tm)) for m in H_MULT], T_int_max=Tm, N=dict(A=NA, B=NB),
                            x=float(x), stratum=name, sobol=j))
        cases += acc
        report[name] = dict(accepted=len(acc), dropped=drop)
    CASES.write_text(json.dumps(cases, indent=1) + '\n')
    (OUT / 'design_report.json').write_text(json.dumps(dict(seed=SEED, counts=COUNTS, seen_tuples=n_seen, strata=report,
                                                            c_grid=[str(c) for c in C_GRID],
                                                            h_mult=[str(m) for m in H_MULT]), indent=1) + '\n')
    print(json.dumps(report))


def _predict_one(case):
    lamA, lamB, u, kappa, hs = parse(case)
    rows = []
    for c in C_GRID:
        m = C.evaluate_m0(lamA, lamB, u, kappa, hs, c=c, allow_csw=True)
        inf = m['h'][-1]
        for r, h, hm in zip(m['h'][:-1], hs, H_MULT):
            rows.append(dict(id=case['id'], stratum=case['stratum'], x=case['x'], c=str(c), h=str(h), h_mult=str(hm),
                             h_Tint=float(h) / case['T_int_max'], z_pred1=r['z_pred_first_order'], z_inf=m['z_inf'],
                             F_old_h=r['F_old'], F_new_h=r['F_new'],
                             F_old_inf=inf['F_old'], F_new_inf=inf['F_new'], s=m['s'], r_min=m['r_min'],
                             a_inf_switch=m['a_inf_switch']))
    return rows


def predict(workers):
    if PRED.exists():
        raise FileExistsError(f'{PRED} is write-once')
    cases = json.loads(CASES.read_text())
    with multiprocessing.get_context('fork').Pool(workers) as pool:
        rows = [r for rs in pool.map(_predict_one, cases) for r in rs]
    with PRED.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})
    print(len(rows), 'prediction rows')


# ------------------------------------------------------------------------------------------------------------ lock

LOCKED = (DESIGN, CARD, CASES, PRED, Path(__file__), ROOT / 'experiments/explore_ctmc/ctmc.py',
          ROOT / 'experiments/explore_ctmc/mc.py')


def lock_card():
    if LOCK.exists():
        raise FileExistsError('lock is write-once')
    LOCK.write_text(json.dumps(dict(created=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                    sha256={str(p.relative_to(ROOT)): sha(p) for p in LOCKED}), indent=1) + '\n')


def check_lock():
    if not LOCK.exists():
        raise RuntimeError('not locked')
    lock = json.loads(LOCK.read_text())
    bad = [p for p, h in lock['sha256'].items() if sha(ROOT / p) != h]
    if bad:
        raise RuntimeError(f'locked files changed: {bad}')
    return lock


def environment():
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                host=socket.gethostname(), platform=platform.platform())


# ----------------------------------------------------------------------------------------------------------- truth

def truth_job(case, c):
    t0 = time.process_time()
    lamA, lamB, u, kappa, hs = parse(case)
    ev = C.evaluate(lamA, lamB, u, kappa, hs, c=c, disagree=False, allow_csw=True)
    rows = [dict(h=str(h), h_Tint=r['h_Tint'], G_S=r['G_S'], G_M=r['G_M'], Gamma=r['Gamma'], Cref=r['Cref'],
                 L00=r['L00'], L01=r['L01'], L10=r['L10'], L11=r['L11'], z_pred_inf_decisions=r['z_pred_first_order_inf_decisions'],
                 share_M0_old=r['shares']['M0_old'], share_M0_new=r['shares']['M0_new'],
                 tie_mass=r['tie_mass'], G_S_hybrid=r['G_S_hybrid']) for r, h in zip(ev['h'], hs)]
    return dict(id=case['id'], c=str(c), status='COMPLETED', stratum=case['stratum'], x=case['x'],
                asymptotic=dict(z_inf=ev['asymptotic']['z_inf'], F_old=ev['asymptotic']['F_old'],
                                F_new=ev['asymptotic']['F_new']),
                s=ev['s'], N=ev['N'], rows=rows, cpu=time.process_time() - t0, host=socket.gethostname())


def _job(case, c, path, cap):
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    signal.signal(signal.SIGXCPU, signal.SIG_DFL)
    out = truth_job(case, c)
    path.with_suffix('.tmp').write_text(json.dumps(out) + '\n')
    path.with_suffix('.tmp').rename(path)


def truth(outdir, workers, cap=CAP):
    lock = check_lock()
    outdir = Path(outdir)
    if (outdir / 'done.json').exists():
        raise FileExistsError('this truth run already finished; the card forbids a rerun')
    (outdir / 'jobs').mkdir(parents=True, exist_ok=True)
    (outdir / 'environment.json').write_text(json.dumps(dict(environment(), lock=lock), indent=1) + '\n')
    cases = json.loads(CASES.read_text())
    # heaviest first (largest N, then longest h), so the tail of the run is short
    jobs = sorted(((cs, c) for cs in cases for c in C_GRID),
                  key=lambda j: (-(j[0]['N']['A'] + j[0]['N']['B']), -float(F(j[0]['hs'][-1])), j[0]['id'], j[1]))
    ctx = multiprocessing.get_context('fork')
    pending, active, t0 = list(jobs), {}, time.time()
    while pending or active:
        while pending and len(active) < workers:
            cs, c = pending.pop(0)
            path = outdir / 'jobs' / f"{cs['id']}_c{str(c).replace('/', '-')}.json"
            if path.exists():
                continue
            p = ctx.Process(target=_job, args=(cs, c, path, cap))
            p.start()
            active[p] = (cs, c, path)
        time.sleep(0.2)
        for p in [p for p in active if not p.is_alive()]:
            cs, c, path = active.pop(p)
            p.join()
            if not path.exists():
                sig = -p.exitcode if p.exitcode is not None and p.exitcode < 0 else None
                status = 'UNRESOLVED' if sig in (signal.SIGKILL, signal.SIGXCPU) else 'ERROR'
                path.write_text(json.dumps(dict(id=cs['id'], c=str(c), status=status, exitcode=p.exitcode)) + '\n')
            print(cs['id'], c, json.loads(path.read_text())['status'], flush=True)
    (outdir / 'done.json').write_text(json.dumps(dict(wall_s=time.time() - t0, jobs=len(jobs)), indent=1) + '\n')


# --------------------------------------------------------------------------- independent Monte Carlo check (V3 + c)

def mc_units():
    """Fixed rule written before truth: the MC_UNITS (regime, c) pairs with c > 0 at h = 3 T_int on the regimes with
    the smallest T_int_max (cheapest burn-in), c alternating over the grid; deterministic."""
    cases = sorted(json.loads(CASES.read_text()), key=lambda cs: (cs['T_int_max'], cs['id']))
    cpos = C_GRID[1:]
    return [(cs, cpos[(2 * i + 1) % len(cpos)], F(cs['hs'][1])) for i, cs in enumerate(cases[:MC_UNITS])]


def mc_end_to_end(case, c, h, episodes, seed):
    """mc.end_to_end of controls V3 with the switching cost c in the exact decisions and in the cost difference."""
    from experiments.explore_ctmc import mc
    lamA, lamB, u, kappa, _ = parse(case)
    exact = C.evaluate(lamA, lamB, u, kappa, [h], c=c, arrays=True, disagree=False, allow_csw=True)
    arr = exact.pop('_arrays')
    row = exact['h'][0]
    rng = np.random.default_rng(seed)
    T_burn = 30 * max(exact['chains']['A_stay']['T_int'], exact['chains']['B_stay']['T_int'], 1.0)
    side = {}
    for name, stay, switch, N in (('A', lamA + u, lamA, arr['NA']), ('B', lamB, lamB + u, arr['NB'])):
        n = np.zeros(episodes, dtype=np.int64)
        m = rng.integers(0, 2, episodes).astype(np.int64)
        mc.advance(n, m, stay, kappa, T_burn, rng)
        y = n.copy()
        mc.advance(n, m, stay, kappa, C.TAU, rng)
        if max(y.max(), n.max()) > N:
            raise ArithmeticError(f'path {name}: simulated backlog above truncation N={N}')
        cS, cW, _ = mc.costs(n, m, stay, switch, kappa, h, rng)
        side[name] = dict(y=y, x=2 * n + m, cS=cS, cW=cW)
    A_, B_ = side['A'], side['B']
    cf = float(c)
    a10 = arr['dhA'][0][A_['x']] + arr['dhB'][0][B_['x']] + cf < 0
    a00 = arr['dhAo'][0][A_['y']] + arr['dhBo'][0][B_['y']] + cf < 0
    a11 = arr['dA'][0][A_['x']] + arr['dB'][0][B_['x']] + cf < 0
    D = A_['cW'] + B_['cW'] + cf - (A_['cS'] + B_['cS'])
    samples = dict(G_S=(a00.astype(float) - a10) * D, M=(a10.astype(float) - a11) * D)
    exact_abs = dict(G_S=row['G_S'] * row['Cref'] / 100, M=row['M'] * row['Cref'] / 100)
    checks = {}
    for k, v in samples.items():
        mean, se = float(v.mean()), float(v.std(ddof=1) / np.sqrt(v.size))
        z = (mean - exact_abs[k]) / se if se > 0 else (0.0 if mean == exact_abs[k] else math.inf)
        checks[k] = dict(mc=mean, se=se, exact=exact_abs[k], z=z, pass_=bool(abs(z) <= 3.5))
    return dict(id=case['id'], c=str(c), h=str(h), episodes=episodes, seed=seed, checks=checks,
                PASS=all(v['pass_'] for v in checks.values()))


def mc(outdir):
    check_lock()
    outdir = Path(outdir)
    path = outdir / 'mc.json'
    if path.exists():
        raise FileExistsError('the MC check already ran')
    res = [mc_end_to_end(cs, c, h, MC_EPISODES, SEED + 100 + i) for i, (cs, c, h) in enumerate(mc_units())]
    path.write_text(json.dumps(dict(units=res, PASS=all(r['PASS'] for r in res)), indent=1) + '\n')
    print(json.dumps([(r['id'], r['c'], r['PASS'], {k: round(v['z'], 2) for k, v in r['checks'].items()}) for r in res]))


# ----------------------------------------------------------------------------------------------------------- score

def load_pred():
    with PRED.open() as f:
        return {(r['id'], r['c'], r['h']): r for r in csv.DictReader(f)}


def table(outdir):
    """One record per (regime, c, h) with truth, prediction and the empirical null (truth at c = 0, same h)."""
    pred = load_pred()
    jobs = [json.loads(p.read_text()) for p in sorted((Path(outdir) / 'jobs').glob('*.json'))]
    ok = {(j['id'], j['c']): j for j in jobs if j.get('status') == 'COMPLETED'}
    recs = []
    for (rid, c), j in ok.items():
        zero = ok.get((rid, '0'))
        for r in j['rows']:
            p = pred[(rid, c, r['h'])]
            null = None
            if zero is not None:
                null = next(z['G_S'] for z in zero['rows'] if z['h'] == r['h'])
            p0 = float(pred[(rid, '0', r['h'])]['z_pred1'])
            recs.append(dict(id=rid, c=c, cf=float(F(c)), h=r['h'], h_mult=float(F(p['h_mult'])), h_Tint=float(p['h_Tint']),
                             stratum=j['stratum'],
                             G_S=r['G_S'], z_pred1=float(p['z_pred1']), z_pred1_c0=p0, null=null,
                             z_pred_inf_decisions=r['z_pred_inf_decisions'],
                             share_old_pred=float(p['F_old_h']), share_old_truth=r['share_M0_old'],
                             share_new_pred=float(p['F_new_h']), share_new_truth=r['share_M0_new'],
                             z_inf_pred=float(p['z_inf']), z_inf_truth=j['asymptotic']['z_inf'],
                             F_old_pred=float(p['F_old_inf']), F_old_truth=j['asymptotic']['F_old'],
                             F_new_pred=float(p['F_new_inf']), F_new_truth=j['asymptotic']['F_new']))
    return recs, len(jobs), len(ok)


def _frac(mask):
    return sum(mask) / len(mask) if mask else None


def score(outdir):
    check_lock()
    outdir = Path(outdir)
    recs, n_jobs, n_ok = table(outdir)
    n_all = len(json.loads(CASES.read_text())) * len(C_GRID)
    consistency = max(max(abs(r['F_old_pred'] - r['F_old_truth']), abs(r['F_new_pred'] - r['F_new_truth']),
                          abs(r['z_inf_pred'] - r['z_inf_truth'])) for r in recs)
    engine = max(max(abs(r['share_old_pred'] - r['share_old_truth']), abs(r['share_new_pred'] - r['share_new_truth']))
                 for r in recs)
    mcj = json.loads((outdir / 'mc.json').read_text()) if (outdir / 'mc.json').exists() else None
    ctrl = dict(complete=n_ok >= 0.9 * n_all, prediction_vs_engine_inputs=consistency <= 1e-9,
                per_h_shares_match=engine <= 1e-9, mc=None if mcj is None else mcj['PASS'])
    long = [r for r in recs if r['h_mult'] >= 3 and r['cf'] > 0]          # by the grid multiple, not the rounded h
    out = {}
    # S1 accuracy of the zero-fit law (inherited tolerance and share)
    hit = [abs(r['G_S'] - r['z_pred1']) <= TOL for r in long]
    out['S1'] = dict(n=len(long), share=_frac(hit), threshold=0.9,
                     verdict='PASS' if hit and _frac(hit) >= 0.9 else ('FAIL' if hit else 'NOT_EVALUABLE'))
    # S2 the law beats the empirical null where it predicts that c matters
    D = [r for r in long if abs(r['z_pred1'] - r['z_pred1_c0']) >= HARM and r['null'] is not None]
    if len(D) >= 10:
        el = [abs(r['G_S'] - r['z_pred1']) for r in D]
        en = [abs(r['G_S'] - r['null']) for r in D]
        closer = _frac([a < b for a, b in zip(el, en)])
        ok = st.median(el) <= 0.5 * st.median(en) and closer >= 0.8
        direction = _frac([(r['G_S'] - r['null'] > 0) == (r['z_pred1'] - r['z_pred1_c0'] > 0) for r in D])
        out['S2'] = dict(n=len(D), median_err_law=st.median(el), median_err_null=st.median(en), law_closer=closer,
                         direction_agree_descriptive=direction,
                         n_more_harm_predicted=sum(r['z_pred1'] < r['z_pred1_c0'] for r in D),
                         verdict='PASS' if ok else 'FAIL')
    else:
        out['S2'] = dict(n=len(D), verdict='NOT_EVALUABLE')
    # S3 predicted sign changes relative to c = 0
    S = [r for r in long if abs(r['z_pred1']) >= HARM and abs(r['z_pred1_c0']) >= HARM
         and (r['z_pred1'] > 0) != (r['z_pred1_c0'] > 0)]
    if len(S) >= 5:
        agree = _frac([(r['G_S'] > 0) == (r['z_pred1'] > 0) for r in S])
        out['S3'] = dict(n=len(S), sign_agree=agree, threshold=0.9, verdict='PASS' if agree >= 0.9 else 'FAIL')
    else:
        out['S3'] = dict(n=len(S), verdict='NOT_EVALUABLE')
    # K7 read-out (descriptive): harm at c = 0 that is gone at c > 0, truth vs law
    harm0 = [r for r in long if r['null'] is not None and r['null'] <= -HARM]
    out['K7'] = dict(n_harm_rows_c0=len(harm0),
                     truth_harm_gone=_frac([r['G_S'] > -HARM for r in harm0]),
                     law_harm_gone=_frac([r['z_pred1'] > -HARM for r in harm0]),
                     status_agree=_frac([(r['G_S'] > -HARM) == (r['z_pred1'] > -HARM) for r in harm0]),
                     by_c={c: dict(n=len(g), truth_gone=_frac([r['G_S'] > -HARM for r in g]),
                                   law_gone=_frac([r['z_pred1'] > -HARM for r in g]))
                           for c in sorted({r['c'] for r in harm0}, key=lambda s: F(s))
                           for g in [[r for r in harm0 if r['c'] == c]]})
    short = [r for r in recs if r['h_mult'] < 3 and r['cf'] > 0]
    out['short_h_descriptive'] = dict(n=len(short), share_within_tol=_frac([abs(r['G_S'] - r['z_pred1']) <= TOL for r in short]))
    final = {k: (v['verdict'] if all(x is not False for x in ctrl.values()) else 'INCONCLUSIVE')
             for k, v in out.items() if 'verdict' in v}
    res = dict(completed=n_ok, of=n_all, controls=ctrl, consistency_max=consistency, per_h_share_max=engine,
               verdicts=final, details=out, card_sha256=sha(CARD), predictions_sha256=sha(PRED))
    (outdir / 'score.json').write_text(json.dumps(res, indent=1) + '\n')
    with (outdir / 'table.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0]))
        w.writeheader()
        w.writerows(recs)
    print(json.dumps(dict(verdicts=final, controls=ctrl), indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['design', 'predict', 'lock', 'truth', 'mc', 'score'])
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'design':
        design()
    elif a.cmd == 'predict':
        predict(a.workers)
    elif a.cmd == 'lock':
        lock_card()
    elif a.cmd == 'truth':
        truth(a.out, a.workers)
    elif a.cmd == 'mc':
        mc(a.out)
    else:
        score(a.out)


if __name__ == '__main__':
    main()
