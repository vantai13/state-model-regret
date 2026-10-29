"""Doan Van Tai — exact scientific identity, separated from numerical settings."""
from fractions import Fraction as F
import re

MU, AMPLITUDE, AGE = F(10), F(6), F(1)
CONTRACT_ID = 'contract-v1.3'
IDENTITY = ('lambdaA', 'lambdaB', 'u', 'kappa', 'h', 'c_sw')
ROLES = ('discovery', 'calibration', 'confirmation', 'control')
EXACT_PATTERN = r'-?(?:[0-9]+/[1-9][0-9]*|[0-9]+(?:\.[0-9]+)?|\.[0-9]+)'


def exact(value):
    """Never silently canonicalize an inexact binary float into a scientific key."""
    if isinstance(value, bool) or not isinstance(value, (str, int, F)):
        raise ValueError('exact integer/rational/decimal string required; no binary floats')
    if isinstance(value, str) and not re.fullmatch(EXACT_PATTERN, value):
        raise ValueError(f'invalid exact numeric token: {value!r}')
    return F(value)


def canonical(reg):
    """Within the fixed v1.3 plant/law/cost namespace; id/role/K/ref are not physics."""
    if reg.get('contract_id', CONTRACT_ID) != CONTRACT_ID:
        raise ValueError('different contract namespace requires explicit conversion')
    return tuple(exact(reg[k]) for k in IDENTITY)


def validity_errors(reg):
    try: lA, lB, u, kappa, h, c_sw = canonical(reg)
    except (KeyError, ValueError, ZeroDivisionError) as exc: return [str(exc)]
    err = []
    if not isinstance(reg.get('id'), str) or not reg['id'].strip(): err.append('nonempty string id required')
    if reg.get('contract_id') != CONTRACT_ID: err.append('explicit contract namespace required')
    allowed={'id','contract_id',*IDENTITY,'role','numerics','provenance'}
    if set(reg)-allowed: err.append('unknown fields; keep outcomes and frame metadata outside regime schema')
    if reg.get('role') not in ROLES: err.append('explicit valid role required')
    if lA < AMPLITUDE or lB < AMPLITUDE: err.append('negative OFF rate')
    if lA + u >= MU: err.append('A not stable before decision under Stay')
    if lB >= MU: err.append('B not stable before decision under Stay')
    if kappa <= 0 or h <= 0: err.append('kappa and h must be positive')
    if u < 0 or (u == 0 and reg.get('role') != 'control'): err.append('u=0 only for a zero-action control; negative u forbidden')
    if c_sw < 0: err.append('switching surcharge must be nonnegative')
    numerics=reg.get('numerics',{})
    if not isinstance(numerics,dict) or set(numerics)-{'K','ref'}:err.append('invalid separate numerics metadata')
    for field in ('K', 'ref'):
        if isinstance(numerics,dict) and field in numerics:
            v = numerics[field]
            if isinstance(v, bool) or not isinstance(v, int) or v < (2 if field == 'K' else 1):
                err.append(f'invalid numerical metadata {field}')
    provenance=reg.get('provenance',{})
    if not isinstance(provenance,dict) or set(provenance)-{'source','eta_pilot'}:err.append('invalid provenance metadata')
    elif 'eta_pilot' in provenance:
        try:
            if 2*exact(provenance['eta_pilot']) != u:err.append('pilot eta/u mismatch')
        except (ValueError,ZeroDivisionError):err.append('invalid pilot eta provenance')
    return err


def validate(reg, *, primary=False):
    errors = validity_errors(reg)
    if primary and not errors:
        if exact(reg['c_sw']) != 0: errors.append('primary requires c_sw=0')
        if reg['role'] == 'control': errors.append('controls do not belong to the primary regime denominator')
    if errors: raise ValueError('; '.join(errors))
    return reg


def derived(reg):
    validate(reg)
    lA, lB, u, kappa, h, _ = canonical(reg)
    return dict(rhoA=(lA + u)/MU, rhoB=lB/MU, rhoA_post=lA/MU,
                rhoB_post=(lB+u)/MU, phi=u/(MU-lB), h_over_tau=h/AGE)


def key_string(reg): return '|'.join(str(x) for x in canonical(reg))


def from_pilot(spec):
    """Preserve a ninth switching-cost field; default zero only when absent.

    Input is the frozen design specs, not an outcome CSV. Numerical metadata is
    retained separately and cannot create a new scientific regime.
    """
    if len(spec) not in (8, 9): raise ValueError('pilot spec must have 8 or 9 fields')
    rid, lA, lB, kappa, eta_pilot, h, ref, K, *cost = spec
    reg = dict(id=rid, contract_id=CONTRACT_ID, lambdaA=str(exact(lA)), lambdaB=str(exact(lB)),
               u=str(2*exact(eta_pilot)), kappa=str(exact(kappa)), h=str(exact(h)),
               c_sw=str(exact(cost[0]) if cost else F(0)), role='discovery',
               numerics=dict(ref=int(exact(ref)), K=int(exact(K))),
               provenance=dict(source='explore-v13-pilot design spec', eta_pilot=str(exact(eta_pilot))))
    if exact(ref).denominator != 1 or exact(K).denominator != 1:
        raise ValueError('integer pilot numerical settings required')
    return validate(reg)


def frame_errors(reg, bounds):
    """Caller-supplied design bounds; never treated as stationary-law validity."""
    values = {**dict(zip(IDENTITY,canonical(reg))), **derived(reg)}
    return [name for name,(lo,hi) in bounds.items() if not exact(lo) <= values[name] <= exact(hi)]


def normalized_design_vector(reg):
    lA,lB,u,kappa,h,c_sw=canonical(reg)
    return (lA/MU,lB/MU,u/MU,kappa,h/AGE,c_sw/(MU*AGE*AGE))


def freshness(candidate, seen):
    """Parameter-only collision/distance check; no outcome-based independence claim."""
    validate(candidate)
    target=canonical(candidate);v=normalized_design_vector(candidate)
    collisions=[r['id'] for r in seen if canonical(r)==target]
    distances=[max(abs(a-b) for a,b in zip(v,normalized_design_vector(r))) for r in seen]
    return dict(fresh=not collisions,collisions=collisions,min_design_Linf=min(distances) if distances else None)


def slot_count(reg, ref):
    """Numerical admissibility, separate from physical schema; never silently ceil h."""
    if isinstance(ref,bool) or not isinstance(ref,int) or ref<1:raise ValueError('positive integer refinement')
    H=exact(reg['h'])*120*ref
    if H.denominator!=1:raise ValueError('h not on registered slot lattice; no silent horizon change')
    return int(H)
