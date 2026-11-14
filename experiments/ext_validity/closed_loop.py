"""Doan Van Tai — EV-A, finite-truncation closed-loop evaluator (c_sw=0).

CLI: predict/run --cases cases.json --grid grid.json --out PATH
     time --case '{"id":"timing","parameters":["7","29/4","1/2","1/2"]}'
time accepts a JSON object/file; missing T_int_max is computed, multipliers default to 3.
Exact here means matrix exponentials on the ctmc-v1 truncations, in floating point.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import resource
import signal
import tempfile
import time

from experiments.explore_ctmc import ctmc as C
from experiments.explore_ctmc.design import rational
import numpy as np
from scipy.linalg import expm

CELLS = ('00', '01', '10', '11')


def _chains(case, h):
    a, b, u, k = map(F, case['parameters'])
    if not (min(a, b) >= C.A and max(a, b) + u < C.MU and F(1, 4) <= u <= 3 and k > 0 and F(h) > 0):
        raise ValueError('outside the ctmc-v1 scientific domain')
    na, nb = (C.choose_N(l + u, k) for l in (a, b))
    return ((C.chain(a + u, k, na), C.chain(b, k, nb)),
            (C.chain(a, k, na), C.chain(b + u, k, nb)))


def _m0(case, h, chains):
    a, b, u, k = map(F, case['parameters'])
    dhA, dhB = (C.m0_gap(l, u, k, ch.N, [float(F(h)), math.inf], side)
                 for l, ch, side in zip((a, b), chains[0], ('A', 'B')))
    # Preserve evaluate's stationary-bias column: expm_multiply's stopping rule
    # depends on the whole batch, even though each output column is independent.
    old = [C.posterior_mean(st, np.column_stack([dh.T, sw.g - st.g]))[:, :2].T
           for st, sw, dh in zip(chains[0], chains[1], (dhA, dhB))]
    return dict(dhA=dhA, dhB=dhB, dhAo=old[0], dhBo=old[1])


def zero_fit(case, h_p):
    """M0 + stationary laws only; no evaluate, V, true gap, or closed-loop truth."""
    t = time.process_time()
    chains = _chains(case, h_p)
    ar = _m0(case, h_p, chains)
    out = dict(id=case['id'], h_p=str(F(h_p)), kind='M0_and_stationary_only')
    rates = [sum(ch.r for ch in pair) for pair in chains]
    for name, suffix in (('new', ''), ('old', 'o')):
        ga, gb = (ar['dh' + s + suffix][0] for s in ('A', 'B'))
        q = []
        for pair in chains:
            wa, wb = [ch.pi if not suffix else ch.pi.reshape(-1, 2).sum(1) for ch in pair]
            q.append(C.pair_sum(wa, ga, ga, wb, gb, gb, 0)[0])
        den = 1 - q[1] + q[0]
        p = q[0] / den if den > 0 else None  # two absorbing actions: no unique p*
        out[name] = dict(q=q, p=p, J_pred=None if p is None else rates[0] + p * (rates[1] - rates[0]))
    po, pn = out['old']['p'], out['new']['p']
    out.update(r_stay=rates[0], r_switch=rates[1], s=rates[1] - rates[0], cpu=time.process_time() - t,
               G_S_CL_pred=None if po is None or pn is None else (rates[1] - rates[0]) * (po - pn))
    return out


def _masks(ar):
    masks = {}
    for cell, prefix, suffix in (('11', 'd', ''), ('10', 'dh', ''), ('01', 'd', 'o'), ('00', 'dh', 'o')):
        ga, gb = (ar[prefix + s + suffix][0] for s in ('A', 'B'))
        mask = ga[:, None] + gb[None, :] < 0
        masks[cell] = mask.repeat(2, 0).repeat(2, 1) if suffix else mask
    return masks


class _Epoch:
    def __init__(self, chains, Delta):
        self.Delta = float(Delta)
        if not math.isfinite(self.Delta) or self.Delta <= C.TAU:
            raise ValueError('Delta must be finite and > tau')
        self.initial = np.outer(chains[0][0].pi, chains[0][1].pi)
        times = {self.Delta, float(C.TAU), self.Delta - C.TAU}
        unique = {ch for pair in chains for ch in pair}
        cache = {(ch, dt): expm(ch.Q.toarray() * dt) for ch in unique for dt in times}
        self.P = {dt: [[cache[ch, dt] for ch in pair] for pair in chains] for dt in times}
        vs = {id(ch): ch.V([Delta])[0] for ch in unique}
        self.cost = [vs[id(a)][:, None] + vs[id(b)][None, :] for a, b in chains]

    def push(self, law, action, dt):
        pa, pb = self.P[dt][action]
        return pa.T @ law @ pb

    def step(self, law, mask, stale):
        nxt = np.zeros_like(law)
        cost, p = 0.0, 0.0
        for a, select in enumerate((~mask, mask)):
            if stale:
                phi = sum(self.push(law[b] * select, b, float(C.TAU)) for b in (0, 1))
                nxt[a] = self.push(phi, a, self.Delta - C.TAU)
            else:
                phi = law * select
                nxt += self.push(phi, a, self.Delta)
            cost += float(np.sum(phi * self.cost[a]))
            if a:
                p = float(phi.sum())
        return nxt, cost / self.Delta, p

    def stationary(self, mask, stale, max_iter):
        t = time.process_time()
        law = np.stack([self.initial, np.zeros_like(self.initial)]) if stale else self.initial.copy()
        previous, max_drift = None, 0.0
        for it in range(1, max_iter + 1):
            nxt, J, p = self.step(law, mask, stale)
            drift = float(nxt.sum() - 1)
            max_drift = max(max_drift, abs(drift))
            if not np.isfinite(nxt).all() or nxt.min() < -1e-14 or not math.isfinite(J) or abs(drift) > 1e-8:
                raise ArithmeticError('invalid epoch law/cost')
            nxt /= nxt.sum()
            residual = float(np.abs(nxt - law).sum())
            relative = None if previous is None else abs(J - previous) / max(abs(J), 1e-300)
            law, previous = nxt, J
            if relative is not None and relative < 1e-12 and residual < 1e-11:
                break
        converged = relative is not None and relative < 1e-12 and residual < 1e-11
        return dict(J=J, p=p, iterations=it, law_l1=residual, J_relative=relative, mass_drift=drift,
                    max_mass_drift=max_drift, status='COMPLETED' if converged else 'UNRESOLVED',
                    cpu=time.process_time() - t), law


def closed_loop(case, Delta, h_p, max_iter=10000):
    """J is a backlog cost rate; p is the stationary fraction of Switch epochs."""
    t = time.process_time()
    if max_iter < 1:
        raise ValueError('max_iter must be positive')
    chains = _chains(case, h_p)
    kernel = _Epoch(chains, Delta)
    ev = C.evaluate(*map(F, case['parameters']), [F(h_p)], c=0, disagree=False, arrays=True)
    ar = ev['_arrays']
    cells = {s: kernel.stationary(mask, s[0] == '0', max_iter)[0] for s, mask in _masks(ar).items()}
    one = ev['h'][0]   # added by Claude (review): one-shot contrasts at h = h_p, for the open- vs closed-loop comparison
    return dict(id=case['id'], parameters=list(map(str, map(F, case['parameters']))),
                Delta=str(F(Delta)), h_p=str(F(h_p)), N=dict(A=ar['NA'], B=ar['NB']), cells=cells,
                one_shot={k: one[k] for k in ('G_S', 'G_M', 'Gamma', 'Cref', 'h_Tint')},
                J_static=min(sum(ch.r for ch in pair) for pair in chains),
                status='COMPLETED' if all(v['status'] == 'COMPLETED' for v in cells.values()) else 'UNRESOLVED',
                cpu=time.process_time() - t)


def single_epoch_costs(case, h):
    """Integrated costs (not rates) from the P1 initial law, for the golden control."""
    chains = _chains(case, h)
    epoch = _Epoch(chains, h)
    ar = C.evaluate(*map(F, case['parameters']), [F(h)], c=0, disagree=False, arrays=True)['_arrays']
    old = np.stack([epoch.initial, np.zeros_like(epoch.initial)])
    return {'L' + s: epoch.step(old if s[0] == '0' else epoch.initial, mask, s[0] == '0')[1] * float(h)
            for s, mask in _masks(ar).items()}


def _write_once(path, record):
    """Publish a complete JSON atomically, without replacing an existing result."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.ev-a-')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(record, f, allow_nan=False)
            f.write('\n')
        try:
            os.link(tmp, path)
        except FileExistsError:
            pass
    finally:
        os.unlink(tmp)


def _child(job, cap):
    case, Delta, hp, path = job
    limit = math.ceil(cap)
    resource.setrlimit(resource.RLIMIT_CPU, (limit, limit))
    t = time.process_time()
    try:
        out = closed_loop(case, Delta, hp)
    except Exception as exc:
        out = dict(status='ERROR', error=f'{type(exc).__name__}: {exc}')
    out.update(id=case['id'], parameters=case['parameters'], Delta=str(Delta), h_p=str(hp), cpu=time.process_time() - t)
    _write_once(path, out)


def _run(jobs, workers, cap):
    if workers < 1 or not math.isfinite(cap) or cap <= 0:
        raise ValueError('workers and cap must be positive')
    ctx, active, pending = mp.get_context('fork'), {}, iter(jobs)
    exhausted = False
    try:
        while active or not exhausted:
            while len(active) < workers and not exhausted:
                job = next(pending, None)
                if job is None:
                    exhausted = True
                elif not job[3].exists():
                    proc = ctx.Process(target=_child, args=(job, cap))
                    proc.start()
                    active[proc] = job
            for proc in list(active):
                if proc.is_alive():
                    continue
                case, Delta, hp, path = active.pop(proc)
                proc.join()
                if not path.exists():
                    status = 'UNRESOLVED' if proc.exitcode in (-signal.SIGKILL, -signal.SIGXCPU) else 'ERROR'
                    _write_once(path, dict(id=case['id'], parameters=case['parameters'], Delta=str(Delta), h_p=str(hp),
                                          status=status, cpu=None, cap=cap, error=f'child exitcode {proc.exitcode}'))
                proc.close()
            if active:
                time.sleep(.02)
    finally:
        for proc in active:
            proc.terminate()
            proc.join()
            proc.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('predict', 'run'):
        p = sub.add_parser(name)
        for arg in ('cases', 'grid', 'out'):
            p.add_argument('--' + arg, required=True)
        if name == 'run':
            p.add_argument('--workers', type=int, default=1)
            p.add_argument('--shard', default='0/1', help='zero-based i/n')
            p.add_argument('--cap', type=float, default=3600)
    p = sub.add_parser('time')
    p.add_argument('--case', required=True, help='JSON object or path to one')
    p.add_argument('--Delta-mult', type=F, default=F(3))
    p.add_argument('--h-p-mult', type=F, default=F(3))
    args = parser.parse_args(argv)
    if args.command == 'time':
        case = json.loads(args.case if args.case.lstrip().startswith('{') else Path(args.case).read_text())
        chains = _chains(case, 1)
        T = case.get('T_int_max', max(ch.T_int for pair in chains for ch in pair))
        t = time.perf_counter()
        out = closed_loop(case, rational(float(args.Delta_mult) * T), rational(float(args.h_p_mult) * T))
        print(json.dumps(dict(out, wall=time.perf_counter() - t, T_int_max=T)))
        return
    cases, grid = (json.loads(Path(f).read_text()) for f in (args.cases, args.grid))
    shard, count = map(int, args.shard.split('/')) if args.command == 'run' else (0, 1)
    if not 0 <= shard < count:
        parser.error('shard must satisfy 0 <= i < n')
    jobs, predictions = [], []
    for case in cases:
        for dm, hm in grid:
            Delta, hp = [rational(float(F(m)) * case['T_int_max']) for m in (dm, hm)]
            if Delta <= C.TAU:
                parser.error('grid Delta must be > tau after rational rounding')
            if args.command == 'predict':
                predictions.append(dict(zero_fit(case, hp), Delta=str(Delta)))
            else:
                key = [case, str(Delta), str(hp)]
                token = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()
                if int(token, 16) % count == shard:
                    jobs.append((case, Delta, hp, Path(args.out) / (token + '.json')))
    if args.command == 'predict':
        _write_once(args.out, predictions)
    else:
        _run(jobs, args.workers, args.cap)


if __name__ == '__main__':
    main()


def zero_fit_first_order(case, Delta, h_p):
    """Added by Claude (review, 14/11): first-order closed-loop law, the closed-loop analogue of T11, zero fit.
    Poisson identity per epoch: E[cost] = Delta * r_a + g_a(x_k) - E[g_a(x_{k+1})], and x_{k+1} ~ pi_a when
    Delta >> T_int, so  J ~ sum_b P(b) [ (1 - q_b) r_St + q_b r_Sw + (E_{pi_b} g_St + E_{pi_b}[1{Sw} (g_Sw - g_St)]) / Delta ],
    b = previous action, q_b = P(M0 chooses Switch | state ~ pi_b). Uses M0 maps, g, pi and e^{Q tau} only."""
    chains = _chains(case, h_p)
    ar = _m0(case, h_p, chains)
    (Ast, Bst), (Asw, Bsw) = chains
    gdA, gdB = Asw.g - Ast.g, Bsw.g - Bst.g
    r = [Ast.r + Bst.r, Asw.r + Bsw.r]
    out = {}
    for name, stale in (('new', False), ('old', True)):
        q, val = [], []
        for (cA, cB) in chains:
            base = float(cA.pi @ Ast.g + cB.pi @ Bst.g)                  # E_{pi_b} g_St
            if stale:
                pA, pB = cA.pi.reshape(-1, 2).sum(1), cB.pi.reshape(-1, 2).sum(1)
                vA, vB = C.posterior_mean(cA, gdA), C.posterior_mean(cB, gdB)   # E_b[g_Sw - g_St | y]
                m, v, _ = C.pair_sum(pA, ar['dhAo'][0], vA, pB, ar['dhBo'][0], vB, 0)
            else:
                m, v, _ = C.pair_sum(cA.pi, ar['dhA'][0], gdA, cB.pi, ar['dhB'][0], gdB, 0)
            q.append(m)
            val.append(base + v)
        den = 1 - q[1] + q[0]
        P1 = q[0] / den if den > 0 else 0.0
        Pb = [1 - P1, P1]
        J = sum(Pb[b] * ((1 - q[b]) * r[0] + q[b] * r[1] + val[b] / float(Delta)) for b in (0, 1))
        out[name] = dict(q=q, p=P1, J_pred=J)
    out['G_S_CL_pred1'] = out['old']['J_pred'] - out['new']['J_pred']
    return out
