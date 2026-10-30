"""Parameter-only sampler. Production entry point is separately gated in frame.py."""
from fractions import Fraction as F
import math
import numpy as np

from experiments.R3R_05_contract.schema import IDENTITY, canonical, validate, exact
from .common import ORDER

STEP = {key: F(1, 120) if key == 'h' else F(1, 1000) for key in IDENTITY if key != 'c_sw'}


def snap(value, step):
    return round(F(value) / step) * step


def draw(rng, lo, hi, law, step):
    lo, hi = exact(lo), exact(hi)
    if lo > hi or lo % step or hi % step:
        raise ValueError('ordered grid-aligned bounds required')
    if lo == hi:
        return lo
    a, b = float(lo), float(hi)
    if law == 'uniform':
        value = a + rng.random() * (b - a)
    elif law == 'log_uniform' and a > 0:
        value = np.exp(np.log(a) + rng.random() * (np.log(b) - np.log(a)))
    else:
        raise ValueError(f'unsupported measure: {law}')
    return min(hi, max(lo, snap(value, step)))


def inside(regime, region):
    return all(exact(lo) <= exact(regime[key]) <= exact(hi)
               for key, (lo, hi) in region['bounds'].items())


def sample_region(root, name, region, n, taken, *, purpose, max_redraw=1000, steps=None):
    if isinstance(root, bool) or not isinstance(root, int) or root < 0:
        raise ValueError('nonnegative integer root required')
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError('nonnegative integer n required')
    if purpose not in ('TEST_ONLY_NO_ENGINE', 'COMMITTED_CONFIRMATION'):
        raise ValueError('explicit sampling purpose required')
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(root, spawn_key=(ORDER.index(name),))))
    rows, redraws = [], 0
    while len(rows) < n:
        values = {key: draw(rng, *region['bounds'][key], region['measure'].get(key, 'pinned'), step)
                  for key, step in (steps or STEP).items()}
        reg = dict(id=f'{name}:{len(rows) + 1:04d}', contract_id='contract-v1.3', role='confirmation',
                   **{key: str(value) for key, value in values.items()}, c_sw='0')
        validate(reg, primary=True)
        if not inside(reg, region):
            raise ValueError('sampler produced a point outside origin region')
        key = canonical(reg)
        if key in taken:
            redraws += 1
            if redraws > max_redraw:
                raise ValueError('exact-collision redraw cap exceeded; preserve attempt and HOLD')
            continue
        taken.add(key)
        rows.append(dict(regime=reg, origin_region=name, purpose=purpose))
    return rows, redraws


def card_steps(card):
    """Rounding steps from the card's measure_rules (card v2, DL-095); card v1 gives exactly STEP."""
    rounding = card.get('measure_rules', {}).get('rounding')
    if rounding is None:
        return dict(STEP)
    steps = {key: F(rounding[key]) for key in STEP}
    if any(step <= 0 for step in steps.values()):
        raise ValueError('positive rounding steps required')
    return steps


def sample_all(root, card, n, bnd, taken, *, purpose):
    rows, redraws = [], {}
    steps = card_steps(card)
    for name in ORDER:
        batch, count = sample_region(root, name, card['regions'][name],
                                     bnd if name.endswith('BND') else n, taken, purpose=purpose, steps=steps)
        rows.extend(batch)
        redraws[name] = count
    return rows, redraws


def distances(reg, seen, region):
    """Both descriptive metrics; zero-width axes are omitted only in the added metric."""
    from experiments.R3R_05_contract.schema import normalized_design_vector
    if not seen:
        return dict(contract_Linf=None, range_log_Linf=None)
    v = normalized_design_vector(reg)
    contract = min(max(abs(a-b) for a, b in zip(v, normalized_design_vector(old))) for old in seen)
    bounds = region['bounds']
    def scaled(old):
        values = []
        for key in IDENTITY:
            lo, hi = map(exact, bounds[key])
            if lo == hi:
                continue
            a, b = float(exact(reg[key])), float(exact(old[key]))
            if key in ('kappa', 'h'):
                if min(a, b) <= 0:
                    return math.inf
                values.append(abs(math.log(a/b))/math.log(float(hi/lo)))
            else:
                values.append(abs(a-b)/float(hi-lo))
        return max(values, default=0.)
    pinned = [key for key,(lo,hi) in bounds.items() if exact(lo)==exact(hi)]
    same = [old for old in seen if all(exact(old[k])==exact(reg[k]) for k in pinned)]
    return dict(contract_Linf=str(contract), range_log_Linf=min(map(scaled, seen)),
                range_log_Linf_same_pinned=min(map(scaled,same)) if same else None,
                same_pinned_count=len(same),pinned_axes=pinned)
