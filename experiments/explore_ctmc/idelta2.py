"""Doan Van Tai — I_Delta round 2: does the share of Gamma explained by a constant-bias (threshold-only) model grow with
h? Fresh ctmc-v1 regimes (Part C2) and toy cells of the slotted fluid engine A00 (Part F2) [EXPLORATION ONLY;
AI (Claude) theo ủy quyền 14/11/2026: "tự soạn thực hiện rồi tự chạy"].

Card (predictions, written after the run01 / fluid-pilot calibration and before any panel outcome):
results/explore_ctmc/idelta/CARD_IDELTA2.md, locked by sha256 in lock_idelta2.json (run refuses otherwise).

    python -m experiments.explore_ctmc.idelta2 design            # write-once cases_fresh.json + fluid_points.json
    python -m experiments.explore_ctmc.idelta2 pilot --out DIR   # fluid pilot points only (calibration)
    python -m experiments.explore_ctmc.idelta2 calibrate         # run01 + pilot read-outs used to set the card
    python -m experiments.explore_ctmc.idelta2 run --out DIR     # GCP, after env.sh and the lock
    python -m experiments.explore_ctmc.idelta2 score --out DIR
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import multiprocessing
import os
import resource
import signal
import socket
import statistics as st
import time
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.stats import qmc

from experiments.explore_ctmc import ctmc as C
from experiments.explore_ctmc import idelta as D1
from experiments.explore_ctmc import design_l75 as L75
from experiments.explore_ctmc import tau as T5
from experiments.explore_ctmc.design import rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/idelta'
CASES = OUT / 'cases_fresh.json'
POINTS = OUT / 'fluid_points.json'
CARD = OUT / 'CARD_IDELTA2.md'
LOCK = OUT / 'lock_idelta2.json'
RUN01 = OUT / 'run01'
SEED = 20261114
N_PER = 15
GMIN = 0.05                                  # pp; a ratio Gamma_add / Gamma is read only where |Gamma| >= GMIN
FLUID_H = (F(1, 2), F(2), F(8), F(32))       # s; avoids the sealed h = 4 axis (R09/R10)
FLUID_GRID = dict(kappa=(F(3, 10), F(1), F(3)), lamA=(F(6), F(13, 2), F(7), F(15, 2), F(8)),
                  eta=(F(1, 2), F(3, 4)), y=(F(0), F(1), F(3), F(8)))     # kappa = 3/5 (R09/R10) never drawn
N_PILOT, N_PANEL = 4, 24
FLUID_REF = 2                                # dt = 1/240 s (A01 DL-053 choice for A04)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------------ design

def seen_all():
    """Every a = 6 regime tuple already in a ctmc case list (L7.1 cases/*, L7.5 cases_l75/*)."""
    seen = L75.seen_tuples()
    for f in glob.glob(str(ROOT / 'results/explore_ctmc/cases_l75/*.json')):
        d = json.loads(Path(f).read_text())
        if isinstance(d, list):
            seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in d if isinstance(c, dict) and 'parameters' in c}
    return seen


def fresh_cases(seen):
    """Same domain, strata, Sobol scheme and cost filter as design_l75.sobol, new seed, N_PER per stratum."""
    out, report = [], {}
    for k, (name, (lo, hi)) in enumerate(L75.STRATA.items()):
        pts = qmc.Sobol(4, scramble=True, seed=SEED + k).random(1024)
        acc, drop = [], dict(domain=0, seen=0, cost=0)
        for j, (pu, pa, px, pk) in enumerate(pts):
            if len(acc) >= N_PER:
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
            c = L75.regime_case(f'I{name[0].upper()}{j:04d}', lamA, lamB, u, kappa, dict(stratum=name, sobol=j))
            if max(un['est_truth'] for un in c['units']) > L75.CAP / 2:
                drop['cost'] += 1
                continue
            seen.add(key)
            acc.append(c)
        out += acc
        report[name] = dict(accepted=len(acc), dropped=drop)
    return out, report


def fluid_points():
    """Distinct toy points (kappa, lamA, eta, yA, yB) drawn without replacement; the first N_PILOT are the pilot."""
    g = FLUID_GRID
    combos = [(k, l, e, a, b) for k in g['kappa'] for l in g['lamA'] for e in g['eta'] for a in g['y'] for b in g['y']
              if l + 2 * e < 10]
    rng = np.random.default_rng(SEED)
    pick = rng.choice(len(combos), size=N_PILOT + N_PANEL, replace=False)
    pts = [dict(id=f'FT{i:02d}', kappa=str(combos[j][0]), lamA=str(combos[j][1]), eta=str(combos[j][2]),
                yA=str(combos[j][3]), yB=str(combos[j][4]), set='pilot' if i < N_PILOT else 'panel')
           for i, j in enumerate(pick)]
    grid = json.loads((ROOT / 'notes/design/grid_v1_2.json').read_text())
    named = {(F(r['kappa']), F(r.get('lambdaA', '-1')), F(r['eta']), F(r['yA']), F(r['yB']))
             for k in ('main', 'heldout', 'controls', 'probes') for r in grid[k]}
    assert not any((F(p['kappa']), F(p['lamA']), F(p['eta']), F(p['yA']), F(p['yB'])) in named for p in pts)
    return pts


def design():
    for path in (CASES, POINTS):
        if path.exists():
            raise FileExistsError(f'{path} is write-once')
    seen = seen_all()
    n_seen = len(seen)
    cases, report = fresh_cases(seen)
    CASES.write_text(json.dumps(cases, indent=1) + '\n')
    POINTS.write_text(json.dumps(dict(h=[str(h) for h in FLUID_H], ref=FLUID_REF, points=fluid_points()), indent=1) + '\n')
    (OUT / 'design_fresh_report.json').write_text(json.dumps(dict(seed=SEED, n_per=N_PER, seen_tuples=n_seen,
                                                                   strata=report), indent=1) + '\n')
    print(json.dumps(report))


# ------------------------------------------------------------------------------------------------------ fluid

def fluid_cell(p, h, ref=FLUID_REF):
    """One toy cell of contract v1.2 (age 1 s, B rates (2, 14)): the four L, Gamma and the constant-bias
    counterfactuals. S0 is one action per cell (T01), so with b = the cell bias L00 is unchanged."""
    from experiments.A00_engine.physical import side_table
    from experiments.A00_engine.evaluate import evaluate_sides
    from experiments.A00_engine.factorial_core import _cut_sum
    k, lam, eta = F(p['kappa']), F(p['lamA']), F(p['eta'])
    cell = dict(id=f"TOY_IDELTA2_{p['id']}", role='toy', origin='idelta2-toy', kappa=k, eta=eta, u=2 * eta, age=F(1),
                yA=F(p['yA']), yB=F(p['yB']), h=F(h), H_coarse=int(120 * F(h)), ratesA=(lam - 6, lam + 6),
                ratesB=(F(2), F(14)), lambdaA=lam)
    t0 = time.process_time()
    A, _ = side_table(cell, 'A', ref)
    B, _ = side_table(cell, 'B', ref)
    r = evaluate_sides(A, B, refinement=ref, dt=F(1, 120 * ref))
    pa, pb = (np.array(s.p, dtype=float) for s in (A, B))
    dA, dhA, dB, dhB = (np.array(v, dtype=float) for v in (A.d, A.dh, B.d, B.dh))
    eA, eB = dhA - dA, dhB - dB
    bA, bB = float(pa @ eA), float(pb @ eB)
    varA, varB = float(pa @ (eA - bA) ** 2), float(pb @ (eB - bB) ** 2)
    L = {key: float(v) for key, v in r['L'].items()}
    K = float(pa @ np.array(A.jst, dtype=float) + pb @ np.array(B.jst, dtype=float))
    cref = L['11']
    l10 = lambda kA, kB: K + float(_cut_sum(tuple(kA), tuple(dA), tuple(pa), tuple(kB), tuple(dB), tuple(pb))[1])
    gam = lambda L10: 100 * (L10 + L['01'] - L['00'] - L['11']) / cref
    b = bA + bB
    return dict(id=p['id'], h=str(h), status=r['status'], Cref=cref, Gamma=gam(L['10']),
                Gamma_engine=100 * float(r['G']['Gamma']) / cref, G_S=100 * float(r['G']['G_S']) / cref,
                G_M=100 * float(r['G']['G_M']) / cref, Gamma_add=gam(l10(dA + bA, dB + bB)),
                Gamma_minusA=gam(l10(dA + bA, dhB)), Gamma_minusB=gam(l10(dhA, dB + bB)),
                EabsI_pct=100 * float(r['E_abs_I_delta']) / cref, bias_pct=100 * b / cref,
                kappa_add=abs(b) / math.sqrt(b * b + varA + varB) if b * b + varA + varB > 0 else None,
                a00=r['a00'], a01=r['a01'], cpu=time.process_time() - t0)


def fluid_rows(points, which):
    rows = []
    for p in points['points']:
        if p['set'] != which:
            continue
        for h in points['h']:
            rows.append(fluid_cell(p, F(h), points['ref']))
    return rows


# ------------------------------------------------------------------------------------------------------ read-outs

def additivity_from_dose(dose_csv, h):
    """kappa_add = |E e| / sqrt(E e^2) of the network M0 gap error under pi_Stay x pi_Stay, from the saved per-path
    dose rows (states up to n_hi; the missing mass is <= 1e-9 per path and is renormalised)."""
    mom = {}
    for row in csv.reader(open(dose_csv)):
        if row[1] != h:
            continue
        e, pi = float(row[5]), float(row[11])
        m = mom.setdefault(row[2], [0.0, 0.0, 0.0])
        m[0] += pi
        m[1] += pi * e
        m[2] += pi * e * e
    b = var = 0.0
    for w, s1, s2 in mom.values():
        mean = s1 / w
        b += mean
        var += s2 / w - mean * mean
    return abs(b) / math.sqrt(b * b + var) if b * b + var > 0 else None


def ctmc_table(run):
    """Per regime: rows at h index 0..3 with Gamma, Gamma_add, E|I|, kappa_add."""
    ids = json.loads((run / 'regimes.json').read_text())
    out = {}
    for i in ids:
        d = json.loads((run / 'regimes' / f'{i}.json').read_text())
        if d['status'] != 'COMPLETED':
            out[i] = None
            continue
        rows = sorted(d['rows'], key=lambda r: r['h_Tint'])
        out[i] = [dict(h=r['h'], h_Tint=r['h_Tint'], Gamma=r['Gamma'], Gamma_add=r['Gamma_cf']['add'],
                       EabsI=r['I']['EabsI_pct'], kappa_add=additivity_from_dose(run / 'regimes' / f'{i}_dose.csv', r['h']),
                       stratum=r['stratum']) for r in rows]
    return out


def ratio(r):
    return r['Gamma_add'] / r['Gamma'] if abs(r['Gamma']) >= GMIN else None


def ctmc_readout(table, lo=1, hi=3):
    ok = {i: v for i, v in table.items() if v}
    rlo = [ratio(v[lo]) for v in ok.values() if ratio(v[lo]) is not None]
    rhi = [ratio(v[hi]) for v in ok.values() if ratio(v[hi]) is not None]
    both = [(ratio(v[lo]), ratio(v[hi])) for v in ok.values() if ratio(v[lo]) is not None and ratio(v[hi]) is not None]
    return dict(n_regimes=len(ok), n_elig_lo=len(rlo), n_elig_hi=len(rhi), n_elig_both=len(both),
                median_ratio_lo=st.median(rlo) if rlo else None, median_ratio_hi=st.median(rhi) if rhi else None,
                frac_ratio_up=sum(b > a for a, b in both) / len(both) if both else None,
                frac_EabsI_down=sum(v[hi]['EabsI'] < v[lo]['EabsI'] for v in ok.values()) / len(ok),
                frac_kadd_up=sum(v[hi]['kappa_add'] > v[lo]['kappa_add'] for v in ok.values()) / len(ok))


def fluid_readout(rows, exclude_hold=False):
    by = {}
    for r in rows:
        by.setdefault(r['id'], {})[r['h']] = r
    if exclude_hold:
        by = {i: v for i, v in by.items() if all(r['status'] == 'BOUNDED' for r in v.values())}
    if not by:
        return dict(n_points=0, n_hold=sum(r['status'] != 'BOUNDED' for r in rows), n_elig_lo=0, n_elig_hi=0,
                    n_elig_both=0, median_ratio_lo=None, median_ratio_hi=None, frac_ratio_up=None,
                    frac_EabsI_down=None, frac_EabsI_down_8_32=None, frac_kadd_up=None)
    hs = [str(h) for h in FLUID_H]
    lo, hi = hs[0], hs[-1]
    rat = lambda r: r['Gamma_add'] / r['Gamma'] if abs(r['Gamma']) >= GMIN else None
    rlo = [rat(v[lo]) for v in by.values() if rat(v[lo]) is not None]
    rhi = [rat(v[hi]) for v in by.values() if rat(v[hi]) is not None]
    both = [(rat(v[lo]), rat(v[hi])) for v in by.values() if rat(v[lo]) is not None and rat(v[hi]) is not None]
    return dict(n_points=len(by), n_hold=sum(r['status'] != 'BOUNDED' for r in rows), n_elig_lo=len(rlo), n_elig_hi=len(rhi),
                n_elig_both=len(both), median_ratio_lo=st.median(rlo) if rlo else None,
                median_ratio_hi=st.median(rhi) if rhi else None,
                frac_ratio_up=sum(b > a for a, b in both) / len(both) if both else None,
                frac_EabsI_down=sum(v[hi]['EabsI_pct'] < v[lo]['EabsI_pct'] for v in by.values()) / len(by),
                frac_EabsI_down_8_32=sum(v[hi]['EabsI_pct'] < v[hs[2]]['EabsI_pct'] for v in by.values()) / len(by),
                frac_kadd_up=sum((v[hi]['kappa_add'] or 0) > (v[lo]['kappa_add'] or 0) for v in by.values()) / len(by))


# ------------------------------------------------------------------------------------------------------ runner

def check_lock():
    if not LOCK.exists():
        raise PermissionError('card not locked: lock_idelta2.json missing')
    lock = json.loads(LOCK.read_text())
    for name, digest in lock['files'].items():
        if sha(ROOT / name) != digest:
            raise PermissionError(f'locked file changed: {name}')
    return lock


def run(out, workers, cap):
    lock = check_lock()
    out.mkdir(parents=True, exist_ok=False)
    env = D1.environment()
    env.update(lock=lock, idelta2_sha256=sha(__file__))
    (out / 'environment.json').write_text(json.dumps(env, indent=1) + '\n')
    cases = json.loads(CASES.read_text())
    (out / 'regimes.json').write_text(json.dumps([c['id'] for c in cases]) + '\n')
    rdir = out / 'regimes'
    rdir.mkdir()
    jobs = sorted(cases, key=lambda r: -max(r['N'].values()))
    ctx = multiprocessing.get_context('fork')
    pending, active = list(jobs), {}
    fluid_proc = ctx.Process(target=_fluid_child, args=(out / 'fluid.json',))
    fluid_proc.start()
    while pending or active:
        while pending and len(active) < workers - 1:
            case = pending.pop(0)
            p = ctx.Process(target=D1._child, args=(case, rdir / f"{case['id']}.json", rdir / f"{case['id']}_dose.csv", cap))
            p.start()
            active[p] = case
        time.sleep(0.2)
        for p in [p for p in active if not p.is_alive()]:
            case = active.pop(p)
            p.join()
            path = rdir / f"{case['id']}.json"
            if not path.exists():
                sig = -p.exitcode if p.exitcode is not None and p.exitcode < 0 else None
                status = 'UNRESOLVED' if sig in (signal.SIGKILL, signal.SIGXCPU) else 'ERROR'
                path.write_text(json.dumps(dict(id=case['id'], status=status, exitcode=p.exitcode)) + '\n')
            print(case['id'], json.loads(path.read_text())['status'], flush=True)
    fluid_proc.join()
    print('fluid', 'COMPLETED' if (out / 'fluid.json').exists() else f'FAILED exit {fluid_proc.exitcode}', flush=True)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    (out / 'done.json').write_text(json.dumps(dict(children_cpu=kids.ru_utime + kids.ru_stime,
                                                    finished=time.strftime('%Y-%m-%dT%H:%M:%S%z'))) + '\n')


def _fluid_child(path):
    resource.setrlimit(resource.RLIMIT_CPU, (3600, 3660))
    rows = fluid_rows(json.loads(POINTS.read_text()), 'panel')
    path.with_suffix('.tmp').write_text(json.dumps(rows, indent=1) + '\n')
    path.with_suffix('.tmp').rename(path)


def score(out):
    lock = json.loads((out / 'environment.json').read_text())['lock']
    pred = lock['predictions']
    res = dict(card_sha256=lock['files'][str(CARD.relative_to(ROOT))], card_sha256_now=sha(CARD))
    table = ctmc_table(out)
    rc = ctmc_readout(table)
    res['ctmc'] = rc
    res['ctmc_status'] = {i: (v is not None) for i, v in table.items()}
    fl = json.loads((out / 'fluid.json').read_text())
    rf = fluid_readout(fl)
    rfx = fluid_readout(fl, exclude_hold=True)
    res['fluid'], res['fluid_bounded_only'] = rf, rfx
    ctl = [r for i in table for r in json.loads((out / 'regimes' / f'{i}.json').read_text()).get('rows', [])]
    res['controls'] = dict(identity=max(r['controls']['identity_resid'] for r in ctl),
                           tower=max(max(r['controls']['tower_A'], r['controls']['tower_B']) for r in ctl),
                           Gamma_match_pp=max(r['controls']['Gamma_match_pp'] for r in ctl),
                           BN_rel=max(r['Eabs_noN_rel'] for r in ctl))
    c = res['controls']
    res['C1'] = c['identity'] <= 1e-7 and c['tower'] <= 1e-9 and c['Gamma_match_pp'] <= 1e-7 and c['BN_rel'] <= 1e-6
    res['C2_n_hold'] = rf['n_hold']
    v = lambda x, op, t: None if x is None else (x <= t if op == '<=' else x >= t)
    res['ctmc_all_completed'] = all(res['ctmc_status'].values())
    res['H1'] = dict(lo=v(rc['median_ratio_lo'], '<=', pred['H1_lo_max']), hi=v(rc['median_ratio_hi'], '>=', pred['H1_hi_min']))
    res['H1']['PASS'] = res['H1']['lo'] is True and res['H1']['hi'] is True
    res['H2'] = v(rc['frac_ratio_up'], '>=', pred['H2_min'])
    res['H3'] = v(rc['frac_EabsI_down'], '>=', pred['H3_min'])
    res['H4'] = v(rc['frac_kadd_up'], '>=', pred['H4_min'])
    if sum(not ok for ok in res['ctmc_status'].values()) > 0.1 * len(res['ctmc_status']):
        for k in ('H1', 'H2', 'H3', 'H4'):      # declared rule: > 10% regimes not COMPLETED -> no CTMC verdict
            res[k] = 'INCONCLUSIVE'

    def fluid_verdicts(r):
        f4 = (v(r['median_ratio_lo'], '<=', pred['F4_lo_max']) is True and v(r['median_ratio_hi'], '>=', pred['F4_hi_min']) is True)
        return dict(F1=v(r['frac_EabsI_down_8_32'], '>=', pred['F1_min']), F2=v(r['frac_kadd_up'], '>=', pred['F2_min']),
                    F3=v(r['frac_ratio_up'], '>=', pred['F3_min']) if r['n_elig_both'] >= pred['F_n_min'] else 'NOT_EVALUABLE',
                    F4=f4 if min(r['n_elig_lo'], r['n_elig_hi']) >= pred['F_n_min'] else 'NOT_EVALUABLE')
    fa, fb = fluid_verdicts(rf), fluid_verdicts(rfx)
    res['fluid_verdicts_all'], res['fluid_verdicts_bounded_only'] = fa, fb
    for k in fa:      # declared rule: a verdict that flips when HOLD_PRECISION points are dropped is INCONCLUSIVE
        res[k] = fa[k] if fa[k] == fb[k] else 'INCONCLUSIVE'
    (out / 'score.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    return res


def calibrate():
    t1 = ctmc_table(RUN01)
    pilot = json.loads((OUT / 'fluid_pilot.json').read_text()) if (OUT / 'fluid_pilot.json').exists() else None
    out = dict(run01=ctmc_readout(t1), run01_rows={i: [(r['h_Tint'], r['Gamma'], r['Gamma_add'], r['EabsI'], r['kappa_add'])
                                                       for r in v] for i, v in t1.items()})
    if pilot:
        out['fluid_pilot'] = fluid_readout(pilot)
        out['fluid_pilot_rows'] = [(r['id'], r['h'], r['status'], r['Gamma'], r['Gamma_add'], r['EabsI_pct'], r['kappa_add'])
                                   for r in pilot]
    (OUT / 'calibration_idelta2.json').write_text(json.dumps(out, indent=1, default=str) + '\n')
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=('design', 'pilot', 'calibrate', 'run', 'score'))
    p.add_argument('--out', type=Path)
    p.add_argument('--workers', type=int, default=os.cpu_count())
    p.add_argument('--cap', type=int, default=1800)
    a = p.parse_args()
    if a.cmd == 'design':
        design()
    elif a.cmd == 'pilot':
        rows = fluid_rows(json.loads(POINTS.read_text()), 'pilot')
        (OUT / 'fluid_pilot.json').write_text(json.dumps(rows, indent=1) + '\n')
        print(json.dumps(fluid_readout(rows), indent=1))
    elif a.cmd == 'calibrate':
        print(json.dumps({k: v for k, v in calibrate().items() if not k.endswith('rows')}, indent=1, default=str))
    elif a.cmd == 'run':
        run(a.out, a.workers, a.cap)
    else:
        print(json.dumps(score(a.out), indent=1, default=str))


if __name__ == '__main__':
    main()
