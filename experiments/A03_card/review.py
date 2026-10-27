"""Doan Van Tai — six-check AI self-review using synthetic ledger witnesses.

No independent reviewer is impersonated. Witness tables demonstrate algebraic
consistency/falsifiability, not feasibility at frozen grid parameters or novelty.
"""
import hashlib
import json
from dataclasses import replace
from fractions import Fraction as F

from experiments.A00_engine.factorial_core import Side, aggregate
from experiments.A00_engine.toy_physics import toy_side
from experiments.A03_card.provenance import ROOT, CARD, metadata
from experiments.A03_card.membership import all_memberships
from experiments.A03_card.grading import point_claim, STANDS, FAILS


def canonical():
    half = F(1, 2)
    P = {m: {n: half for n in ('off', 'on')} for m in ('off', 'on')}
    A, _ = toy_side([(1, 2, 'x')], {'x': 1}, {'x': {'x': 1}}, 3, 2, 0, 2)
    B, _ = toy_side([(F(1, 4), q, m) for q in (0, 2) for m in ('off', 'on')],
                    {'off': 0, 'on': 5}, P, 3, 0, 2, 2)
    return A, B


def scaled(sides, factor, shift):
    return tuple(replace(s, d=tuple(factor * v for v in s.d), dh=tuple(factor * v for v in s.dh),
                         jst=tuple(factor * v + (shift if i == 0 else 0) for v in s.jst))
                 for i, s in enumerate(sides))


def row(result):
    values = {**{'L' + k: v for k, v in result['L'].items()}, **result['G'], 'C_ref': result['C_ref']}
    return {'intervals': {k: [v, v] for k, v in values.items()}}


def witnesses():
    half = (F(1, 2), F(1, 2))
    E5 = (Side(half, (F(0), F(3)), (F(3, 2), F(0)), (F(10), F(10)), (0, 1)),
          Side((F(1),), (F(-1),), (F(-1, 2),), (F(0),), (0,)))
    E7 = (Side(half, (F(1), F(3)), (F(1, 2), F(3, 2)), (F(0), F(0)), (1, 4)),
          Side(half, (F(-4), F(-1, 2)), (F(-2), F(-3, 4)), (F(0), F(0)), (0, 0)))
    joint = (Side(half, (F(0), F(38, 5)), (F(1, 2), F(2)), (F(102), F(102)), (0, 1)),
             Side(half, (F(-4), F(-4)), (F(-1), F(-1, 10)), (F(0), F(0)), (0, 1)))
    base = canonical()
    good = {'P2': aggregate(*scaled(base, 2, F(175, 2))),
            'P3_and_K5': aggregate(*joint), 'Q5': aggregate(*scaled(base, 4, 75)),
            'P6': aggregate(*scaled(base, 1, F(375, 4)))}
    bad = {'P2': aggregate(*scaled(E5, 1, F(181, 2))),
           'P3': aggregate(*scaled(base, 1, F(375, 4))),
           'P5_K': good['Q5'], 'P5_Q': good['P3_and_K5'],
           'P6': aggregate(*scaled(E7, 1, 101))}
    for predicate, name in (('P2', 'P2'), ('P3', 'P3_and_K5'), ('P5_K', 'P3_and_K5'),
                            ('P5_Q', 'Q5'), ('P6', 'P6')):
        assert point_claim(predicate, row(good[name])) == STANDS
    for predicate, result in bad.items():
        assert point_claim(predicate, row(result)) == FAILS
    return good, bad


def six_checks(card_path=ROOT / CARD):
    text = card_path.read_text()
    spec = metadata(text)
    assert spec['claims_sha256'] == hashlib.sha256((ROOT / 'notes/literature/claims.md').read_bytes()).hexdigest()
    claims = (ROOT / 'notes/literature/claims.md').read_text()
    for pc in ('PC2', 'PC3', 'PC5', 'PC6'):
        source = next(r for r in claims.splitlines() if r.startswith('| ' + pc + ' |'))
        assert source in text, pc
    p = spec['predictions']
    assert set(p) == {'P2', 'P3', 'P5', 'P6'}
    assert p['P2']['ids'] == ['M09', 'M10', 'M11', 'M12']
    assert p['P3']['ids'] == ['M19', 'M21'] and set(p['P3']['ids']) < set(p['P5']['K_ids'])
    assert p['P5']['K_ids'] == ['M19', 'M20', 'M21', 'M22']
    assert p['P5']['Q_ids'] == ['M01', 'M02', 'M03', 'M04']
    assert p['P6']['ids'] == ['M17', 'M18']
    assert (p['P2']['relation'], F(p['P2']['threshold'])) == ('>=', F(1, 100))
    assert (p['P3']['relation'], F(p['P3']['threshold'])) == ('>', F(1, 200))
    assert (p['P5']['K_relation'], F(p['P5']['K_threshold'])) == ('<=', F(1, 200))
    assert (p['P5']['Q_relation'], F(p['P5']['Q_threshold'])) == ('>=', F(1, 100))
    m = all_memberships()
    assert spec['K5_rule']['main'] == m['K5_kge2']['main']
    assert spec['K5_rule']['heldout'] == m['K5_kge2']['heldout']
    assert spec['optional_P2_P3_rules_adopted'] is False and spec['adopted_rule_count'] == 1
    assert spec['mechanism_provenance'] == 'FORECAST_WITHOUT_MECHANISM'
    assert spec['already_implied_readback'] == spec['engine_readback'] == 'AUTHOR_ATTESTED'
    good, bad = witnesses()
    result = dict(reviewer='AI self-check in same session; not independent', checks=[
        dict(id=1, status='PASS', evidence='five primitive countermodels, four grouped forecasts can fail'),
        dict(id=2, status='PASS', evidence='coordinate whitelist and forbidden-feature poison tests'),
        dict(id=3, status='PASS', evidence='explicit operators, exact thresholds and branch refutations'),
        dict(id=4, status='PASS_SCOPE_ONLY', evidence='uses DL-043 adopted boundary; no novelty/primary-paper re-audit'),
        dict(id=5, status='PASS', evidence='non-identity: each primitive has a standing witness and countermodel'),
        dict(id=6, status='PASS_ALGEBRAIC', evidence='distinct K2/K3 witnesses; K3 and K5 share a compatible table')],
        mechanism_claims=0, forecast_count=4, adopted_coordinate_rules=1,
        limitations='does not certify fixed-parameter queue feasibility, causal mechanism, novelty or independent review')
    return result, good, bad
