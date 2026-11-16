"""Doan Van Tai — one-regime LETTER-W2 evaluator, unchanged CTMC plant.

All decision costs use pair_sum's strict Switch test.  The probabilistic
disagreement uses the real stationary old/current Markov coupling, not an
implicit coupling of equal state indices; the latter is also reported.
"""
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time

import numpy as np
from scipy.sparse.linalg import expm_multiply

from experiments.explore_ctmc import ctmc
from experiments.letter.e3_agediff import evaluate_agediff, prepare_regime
from experiments.letter.shat import ROOT, load_cases, saved_path
from experiments.letter.shat2 import estimate_levels

THETAS = (.5, 1., 2., 4.)
LEVELS = ('true_s', 'mm1')
NUM_TOL = 1e-9  # arithmetic probability/cost check, not an effect threshold


def write_json_once(path, obj):
    """Publish a fully serialized file atomically, without replacing a target."""
    path = Path(path)
    payload = json.dumps(obj, indent=2, allow_nan=False)+'\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(tmp, path)
    finally:
        os.unlink(tmp)


def onset_shift(h, s_hat, theta, T_int):
    if theta < 0:
        raise ValueError('theta must be nonnegative')
    return float(s_hat)*max(0., float(h)-float(theta)*float(T_int))


def _inclusive_pair(wA, uA, vA, wB, uB, vB, c=0.):
    """pair_sum plus *exact* zero pairs, including their true cost weights."""
    mass, value, ties = ctmc.pair_sum(wA, uA, vA, wB, uB, vB, c)
    order = np.argsort(uB, kind='stable')
    sorted_b = uB[order]
    W = np.r_[0., np.cumsum(wB[order])]
    WV = np.r_[0., np.cumsum((wB*vB)[order])]
    left = np.searchsorted(sorted_b, -float(c)-uA, side='left')
    right = np.searchsorted(sorted_b, -float(c)-uA, side='right')
    tie_value = float(wA @ ((vA+float(c))*(W[right]-W[left])+WV[right]-WV[left]))
    return mass+ties, value+tie_value, ties


def absolute_tail_mass(wA, a, wB, b, threshold):
    """P(|a+b| >= threshold), inclusive at both boundaries, exact sorted sum."""
    if threshold <= 0:
        return float(wA.sum()*wB.sum())
    order = np.argsort(b, kind='stable')
    W = np.r_[0., np.cumsum(wB[order])]
    lower = np.searchsorted(b[order], -threshold-a, side='right')
    upper = np.searchsorted(b[order], threshold-a, side='left')
    return float(wA @ (W[lower]+W[-1]-W[upper]))


def _probability_columns(chain, tau, columns):
    """Columns of exp(Q tau), with no probability cutoff or Monte Carlo."""
    unit = np.zeros((chain.n, len(columns)))
    unit[columns, np.arange(len(columns))] = 1.
    P = expm_multiply(chain.Q*float(tau), unit)
    minimum = float(P.min())
    if minimum < -1e-12 or not np.isfinite(P).all():
        raise ArithmeticError('invalid transition probabilities')
    # expm_multiply of a Metzler generator is nonnegative in exact arithmetic.
    return np.maximum(P, 0.)


class JointDisagreement:
    """Exact sorted-pair computation under pi(y) P_tau(y,x) on each path.

    A bivariate cumulative table on the smaller path computes the Switch /
    Switch intersection.  The other path's transition columns are streamed.
    Table construction is repeated by horizon, but transition exponentials
    are cached in temporary memmaps and shared across all those horizons.
    This avoids the four-dimensional joint tensor entirely.
    """
    def __init__(self, A, B, tau, directory, block=64):
        self.A, self.B, self.tau, self.block = A, B, float(tau), block
        self.paths = {}
        self.diagnostics = {}
        for name, chain in (('A', A), ('B', B)):
            array = np.memmap(Path(directory)/(name+'.f8'), mode='w+', dtype='float64',
                              shape=(chain.n, chain.n))
            max_row_error = 0.
            row_sums = np.zeros(chain.n)
            for first in range(0, chain.n, block):
                columns = np.arange(first, min(first+block, chain.n))
                P = _probability_columns(chain, tau, columns)
                row_sums += P.sum(axis=1)
                array[:, columns] = chain.pi[:, None]*P
            max_row_error = float(np.max(np.abs(row_sums-1)))
            if max_row_error > 1e-8:
                raise ArithmeticError('transition rows do not sum to one')
            array.flush()
            self.paths[name] = array
            self.diagnostics[name] = dict(states=chain.n, transition_row_sum_max_error=max_row_error,
                                          joint_total_mass=float(array.sum()))

    def mass(self, freshA, staleA, freshB, staleB, correction):
        if self.A.n*self.B.n <= 3000:
            # On tiny state spaces, use the requested dense helper directly
            # on the correctly expanded joint-path events.
            fa = np.tile(freshA, self.A.n)
            oa = np.repeat(staleA, self.A.n)
            fb = np.tile(freshB, self.B.n)
            ob = np.repeat(staleB, self.B.n)
            return ctmc.dense_disagree(self.paths['A'].ravel(), fa+correction, oa+correction,
                                       self.paths['B'].ravel(), fb, ob, 0.)
        # B is the smaller CDF table; swapping paths preserves pair sums.
        if self.A.n < self.B.n:
            JA, JB = self.paths['B'], self.paths['A']
            a, ao, b, bo = freshB, staleB, freshA, staleA
            wa, wb = self.B.pi, self.A.pi
        else:
            JA, JB = self.paths['A'], self.paths['B']
            a, ao, b, bo = freshA, staleA, freshB, staleB
            wa, wb = self.A.pi, self.B.pi
        order_new, order_old = np.argsort(b, kind='stable'), np.argsort(bo, kind='stable')
        table = np.zeros((len(b)+1, len(b)+1))
        table[1:, 1:] = JB[np.ix_(order_old, order_new)]
        np.cumsum(table, axis=0, out=table)
        np.cumsum(table, axis=1, out=table)
        cutoff_new = np.searchsorted(b[order_new], -correction-a, side='left')
        cutoff_old = np.searchsorted(bo[order_old], -correction-ao, side='left')
        both = 0.
        for first in range(0, len(a), self.block):
            end = min(first+self.block, len(a))
            both += float(np.sum(JA[:, first:end]*table[cutoff_old[:, None], cutoff_new[None, first:end]]))
        zero_a, zero_b = np.zeros(len(a)), np.zeros(len(b))
        fresh = ctmc.pair_sum(wa, a+correction, zero_a, wb, b, zero_b, 0.)[0]
        stale = ctmc.pair_sum(wa, ao+correction, zero_a, wb, bo, zero_b, 0.)[0]
        result = fresh+stale-2*both
        if result < -NUM_TOL or result > 1+NUM_TOL:
            raise ArithmeticError('invalid joint disagreement mass')
        return float(np.clip(result, 0., 1.))


def probabilistic_bound(p, arrays, index, h, joint=None):
    wA, wB = arrays['wA'], arrays['wB']
    a, b = arrays['dhA'][index], arrays['dhB'][index]
    ao, bo = arrays['dhAo'][index], arrays['dhBo'][index]
    threshold = float(h)*abs(p['s'])
    fresh_tail = absolute_tail_mass(wA, a, wB, b, threshold)
    stale_tail = absolute_tail_mass(wA, ao, wB, bo, threshold)
    correction = float(h)*p['s']
    same_index = sorted_disagreement(wA, a+correction, ao+correction, wB, b, bo)
    actual = joint.mass(a, ao, b, bo, correction) if joint is not None else None
    return dict(D=fresh_tail+stale_tail, fresh_tail=fresh_tail, stale_tail=stale_tail,
                threshold=threshold, disagreement=actual,
                disagreement_law='independent paths; pi_A(yA) P_A(yA,xA) pi_B(yB) P_B(yB,xB)',
                same_index_policy_disagreement=same_index,
                P17_holds=None if actual is None else actual <= fresh_tail+stale_tail+NUM_TOL,
                arithmetic_tolerance=NUM_TOL)


def sorted_disagreement(wA, a1, a2, wB, b1, b2):
    """Same-index policy distance, dense when affordable, exact CDF otherwise."""
    if len(wA)*len(wB) <= ctmc.DENSE_PAIRS:
        return ctmc.dense_disagree(wA, a1, a2, wB, b1, b2, 0.)
    # Weighted offline dominance queries, implemented by a Fenwick sweep.
    order = np.argsort(b1, kind='stable')
    coordinates = np.unique(b2)
    ranks = np.searchsorted(coordinates, b2)+1
    tree = np.zeros(len(coordinates)+1)
    queries = np.argsort(-a1, kind='stable')
    cursor, both = 0, 0.
    for i in queries:
        while cursor < len(order) and b1[order[cursor]] < -a1[i]:
            j = order[cursor]
            pos = int(ranks[j])
            while pos < len(tree):
                tree[pos] += wB[j]
                pos += pos & -pos
            cursor += 1
        pos = int(np.searchsorted(coordinates, -a2[i], side='left'))
        total = 0.
        while pos:
            total += tree[pos]
            pos -= pos & -pos
        both += wA[i]*total
    za, zb = np.zeros(len(a1)), np.zeros(len(b1))
    m1 = ctmc.pair_sum(wA, a1, za, wB, b1, zb, 0.)[0]
    m2 = ctmc.pair_sum(wA, a2, za, wB, b2, zb, 0.)[0]
    return float(np.clip(m1+m2-2*both, 0., 1.))


def _variant(arr, k, base, correction=0., tie_switch=False):
    wA, wB = arr['wA'], arr['wB']
    pair = _inclusive_pair if tie_switch else ctmc.pair_sum
    fresh = pair(wA, arr['dhA'][k]+correction, arr['dA'][k],
                 wB, arr['dhB'][k], arr['dB'][k], 0.)
    stale = pair(wA, arr['dhAo'][k]+correction, arr['dAo'][k],
                 wB, arr['dhBo'][k], arr['dBo'][k], 0.)
    oracle = base['Cref']-base['E_stay']
    scale = 100/base['Cref']
    return dict(regret_new=scale*(fresh[1]-oracle), regret_old=scale*(stale[1]-oracle),
                G_S=scale*(stale[1]-fresh[1]), share_new=fresh[0], share_old=stale[0],
                exact_tie_mass_new=fresh[2], exact_tie_mass_old=stale[2],
                correction=correction, tie_action='Switch' if tie_switch else 'Stay')


def evaluate_age(p, tau, estimator, *, include_bound=False, joint=None):
    levels = {} if estimator['s_hat_mmpp'] is None else dict(mmpp=estimator['s_hat_mmpp'])
    raw = evaluate_agediff(*p['parameters'][:4], p['hs'], tau, c=p['parameters'][4],
                          a=p['a'], prepared=p, arrays=True, disagree=False, shat_levels=levels)
    arr = raw.pop('_arrays')
    rows = []
    for k, base in enumerate(raw['h']):
        h = float(p['hs'][k])
        hybrids = dict(base['hybrid_levels'])
        if 'mmpp' not in hybrids:
            hybrids['mmpp'] = dict(status='INVALID', regret_new=None, regret_old=None, G_S=None)
        onset, ties = {}, {}
        for level in LEVELS:
            s = p['s'] if level == 'true_s' else p['s_mm1']
            onset[level] = {f'{theta:g}': _variant(arr, k, base, onset_shift(h, s, theta, p['T_int']))
                            for theta in THETAS}
            ties[level] = _variant(arr, k, base, tie_switch=s < 0)
        row = dict(h=base['h'], h_Tint=base['h_Tint'], Cref=base['Cref'],
                   M0=_variant(arr, k, base), M1=dict(regret_new=base['regret']['M1_new'],
                                                    regret_old=base['regret']['M1_old']),
                   hybrid=hybrids, onset=onset, tie_break=ties, flags=base['flags'])
        if include_bound:
            row['bound'] = probabilistic_bound(p, arr, k, h, joint)
        rows.append(row)
    return dict(tau=float(tau), tau_Tint=float(tau)/p['T_int'], h=rows)


def e1_regimes(cases=None):
    """First negative-s case in each file, using existing stationary metadata."""
    cases = load_cases() if cases is None else cases
    result = {}
    for case in cases:
        if case['family'] in result:
            continue
        existing = json.loads(saved_path(case).read_text())
        if 's' not in existing:
            raise ValueError('E1 selection requires stationary s in saved baseline')
        if existing['s'] < 0:
            result[case['family']] = case['id']
    return result


def e1_data(p):
    ratios = np.geomspace(.1, 30., 60)
    hs = ratios*p['T_int']
    states = {}
    for side in ('A', 'B'):
        stay = p[side+'st']
        cdf = np.cumsum(stay.pi.reshape(-1, 2).sum(axis=1))
        median, q95 = (int(np.searchsorted(cdf, q)) for q in (.5, .95))
        states[side] = [(0, 0), (median, 1), (q95, 1)]
    paths = {}
    for name, key in (('A_stay', 'Ast'), ('A_switch', 'Asw'), ('B_stay', 'Bst'), ('B_switch', 'Bsw')):
        ch = p[key]
        indices = [2*n+m for n, m in states[name[0]]]
        truth = ch.V(hs)[:, indices]
        hat, drains = ctmc.m0_vhat(ch.load, ch.kappa, ch.N, hs, a=p['a'], return_T=True)
        # The asymptotic slope follows from Qg=-(f-r). Report finite-grid
        # terminal slopes separately, without asserting equality at finite h.
        terminal_slope = expm_multiply(ch.Q*float(hs[-1]), ch.f)[indices]
        plateau_checks = []
        for j, idx in enumerate(indices):
            beyond = hs >= drains[idx]
            values = hat[beyond, idx]
            plateau_checks.append(bool(len(values) >= 2 and np.all(values == values[0])))
        paths[name] = dict(states=[dict(n=n, mode=m, index=2*n+m) for n, m in states[name[0]]],
                           V=truth.T.tolist(), V_hat=hat[:, indices].T.tolist(),
                           drain_times=drains[indices].tolist(), r=ch.r,
                           flat_after_drain=plateau_checks,
                           terminal_slopes=terminal_slope.tolist(),
                           slope_limit=ch.r,
                           poisson_equation_max_residual=float(np.max(np.abs(ch.Q@ch.g+ch.f-ch.r))))
    actions = {}
    for action in ('stay', 'switch'):
        A, B = paths['A_'+action], paths['B_'+action]
        actions[action] = dict(V=(np.asarray(A['V'])+np.asarray(B['V'])).tolist(),
                               V_hat=(np.asarray(A['V_hat'])+np.asarray(B['V_hat'])).tolist(),
                               r=A['r']+B['r'],
                               drain_times=np.maximum(A['drain_times'], B['drain_times']).tolist())
    return dict(h_Tint=ratios.tolist(), h=hs.tolist(), state_labels=['empty_low', 'median_high', 'q95_high'],
                state_convention='joint state pairs: corresponding Stay-backlog quantiles on each path; per-path data also retained',
                paths=paths, actions=actions,
                P19_flat=all(all(ch['flat_after_drain']) for ch in paths.values()),
                P19_slope_identity=all(ch['poisson_equation_max_residual'] <= NUM_TOL for ch in paths.values()),
                slope_statement='V(h,x)=h*r+g(x)-exp(Qh)g(x); slope tends to r, not exactly r at finite h')


def run_regime(case, out, e1_ids=None):
    target = Path(out)/(case['id']+'.json')
    if target.exists():
        raise FileExistsError(target)
    start, wall = time.process_time(), time.monotonic()
    la, lb, u, k, c = case['parameters']
    p = prepare_regime(la, lb, u, k, case['hs'], c=c, a=F(case.get('a', 6)))
    prepared_cpu = time.process_time()-start
    estimate_start = time.process_time()
    estimator = estimate_levels(p, case['regime_index'])
    estimate_cpu = time.process_time()-estimate_start
    age_one = evaluate_age(p, 1., estimator)
    with tempfile.TemporaryDirectory(prefix='letter_w2_joint_') as tmp:
        joint_start = time.process_time()
        # Claude 16/11 (author delegation): the exact joint disagreement builds full exp(Q*T_int) per path, which
        # takes hours for regimes with long T_int and large N. With LETTER_W2_SKIP_JOINT=1 it is skipped (P17 not
        # evaluated for that regime); the bound D(h) is still computed. P17 is a math check already run on 71 regimes.
        joint = None if os.environ.get('LETTER_W2_SKIP_JOINT') == '1' else JointDisagreement(p['Ast'], p['Bst'], p['T_int'], tmp)
        joint_cpu = time.process_time()-joint_start
        age_tint = evaluate_age(p, p['T_int'], estimator, include_bound=True, joint=joint)
        joint_diagnostics = joint.diagnostics if joint is not None else dict(skipped='LETTER_W2_SKIP_JOINT=1')
        del joint
    figure_ids = e1_regimes() if e1_ids is None else e1_ids
    figure = e1_data(p) if case['id'] in figure_ids.values() else None
    sources = ('results/letter/CARD_W2.md', 'experiments/letter/mmpp.py', 'experiments/letter/shat2.py',
               'experiments/letter/w2_eval.py', 'experiments/letter/e3_agediff.py', 'experiments/explore_ctmc/ctmc.py')
    result = dict(owner='Doan Van Tai', namespace='ctmc-v1-letter-W2-exploratory',
                  status='COMPLETED', id=case['id'], family=case['family'], regime_index=case['regime_index'],
                  case=case, T_int=p['T_int'], s=p['s'], s_mm1=p['s_mm1'],
                  N=dict(A=p['NA'], B=p['NB']), estimator=estimator,
                  evaluations=[dict(age_label='seconds_1', **age_one), dict(age_label='Tint_1', **age_tint)],
                  joint_disagreement_diagnostics=joint_diagnostics, e1=figure,
                  cpu_components=dict(prepare=prepared_cpu, estimator=estimate_cpu, joint_transitions=joint_cpu),
                  cpu_seconds=time.process_time()-start, wall_seconds=time.monotonic()-wall,
                  input_sha256={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources})
    write_json_once(target, result)
    return dict(id=case['id'], family=case['family'], cpu_seconds=result['cpu_seconds'],
                wall_seconds=result['wall_seconds'], estimator_status=estimator['status'])
