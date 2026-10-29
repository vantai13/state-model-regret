"""Doan Van Tai — L3R.6 card tooling: exact CP decisions, verdict maps, design-only regions.

Synthetic counts/values only, plus design-only pilot metadata; no new outcome.
"""
from fractions import Fraction as F
from itertools import product

import pytest

from experiments.R3R_06_cards import stats, verdict as V
from experiments.R3R_06_cards.regions import Box, DesignView, EMPTY, in_region, sealed_and_exposed
from experiments.R3R_06_cards import discovery as D

A, HALF = F(1, 40), F(1, 2)
SCORE = {'PASS': 3, 'WEAKEN': 2, 'INCONCLUSIVE': 1, 'FALSIFY': 0}


def reg(lA='7', lB='8', u='1', kappa='1/10', h='12', c_sw='0'):
    return DesignView(dict(lambdaA=lA, lambdaB=lB, u=u, kappa=kappa, h=h, c_sw=c_sw))


# ---------------------------------------------------------------- exact Clopper–Pearson
@pytest.mark.parametrize('p0,alpha', [(HALF, A), (F(4, 5), F(1, 20)), (HALF, F(1, 20))])
def test_exact_tail_decision_matches_beta_quantile(p0, alpha):
    for n in range(1, 61):
        for k in range(n + 1):
            lo, hi = stats.cp_bounds(n, k, alpha)
            if abs(lo - float(p0)) > 1e-9:
                assert stats.lower_bound_exceeds(n, k, p0, alpha) == (lo > float(p0))
            if abs(hi - float(p0)) > 1e-9:
                assert stats.upper_bound_below(n, k, p0, alpha) == (hi < float(p0))


def test_lesson_tables_reproduce():
    assert round(stats.cp_bounds(30, 21, A)[0], 3) == 0.506
    table = {20: (15, [0.021, 0.13, 0.42, 0.80, 0.99]), 30: (21, [0.021, 0.18, 0.59, 0.94, 1.00]),
             40: (27, [0.019, 0.21, 0.70, 0.98, 1.00])}
    for n, (k, row) in table.items():
        assert stats.k_support(n, HALF, A) == k
        got = [float(V.plus_power(n, F(p))) for p in ('0.5', '0.6', '0.7', '0.8', '0.9')]
        assert all(abs(g - r) <= 0.006 for g, r in zip(got, row))
    assert stats.k_reject(30, HALF, A) == 9
    assert round(float(V.primary_pass_power(30, F(7, 10), 30, F(1, 5))), 2) == 0.55
    g = dict(pi0=F(4, 5), alpha=F(1, 20))
    assert stats.k_support(10, F(4, 5), F(1, 20)) is None              # cannot PASS
    assert stats.k_support(15, F(4, 5), F(1, 20)) == 15
    assert stats.k_support(20, F(4, 5), F(1, 20)) == 20
    assert stats.k_support(30, F(4, 5), F(1, 20)) == 28
    assert round(float(V.gamma_pass_power(30, F(9, 10), **g)), 2) == 0.41
    assert round(float(V.gamma_pass_power(15, F(9, 10), **g)), 2) == 0.21


# ---------------------------------------------------------------- per-regime labels
def test_regime_labels_and_R6_boundaries():
    assert V.regime_label('effect', None, 0) == 'UNDEFINED'
    assert V.regime_label('effect', F(2, 100), 0) == 'MEETS'
    assert V.regime_label('effect', F(9, 1000), F(1, 10000)) == 'FAILS'
    assert V.regime_label('effect', F(98, 10000), F(2, 1000)) == 'UNRESOLVED'   # lesson L3R.5 toy
    assert V.regime_label('effect', F(1, 100), 0) == 'UNRESOLVED'               # equality is conservative
    assert V.regime_label('effect', F(1, 100), 0, certified_exact=True) == 'MEETS'
    assert V.regime_label('harm', F(-2, 100), 0) == 'MEETS'
    assert V.regime_label('harm', F(-5, 1000), 0) == 'FAILS'
    assert V.regime_label('noninferiority', F(-4, 1000), 0) == 'MEETS'
    assert V.regime_label('noninferiority', F(-6, 1000), 0) == 'FAILS'
    assert V.regime_label('noninferiority', F(-5, 1000), F(1, 10000)) == 'UNRESOLVED'
    assert V.regime_label('effect', F(5, 100), 0, r1_ready=False) == 'UNRESOLVED'
    with pytest.raises(ValueError): V.regime_label('effect', 0, -1)


def test_condition_labels():
    assert V.condition_label(F(1, 100), 0, 0, strict=False) == 'ELIGIBLE'
    assert V.condition_label(0, 0, 0, strict=False) == 'AMBIGUOUS'
    assert V.condition_label(0, 0, 0, strict=False, certified_exact=True) == 'ELIGIBLE'
    assert V.condition_label(F(-1, 100), 0, F(1, 1000), strict=False) == 'EXCLUDED'
    assert V.condition_label(F(5, 1000), F(5, 1000), 0, strict=True, certified_exact=True) == 'EXCLUDED'
    assert V.all_conditions(['ELIGIBLE', 'AMBIGUOUS']) == 'AMBIGUOUS'
    assert V.all_conditions(['AMBIGUOUS', 'EXCLUDED']) == 'EXCLUDED'


# ---------------------------------------------------------------- verdict tables
def test_primary_table_covers_every_outcome_and_is_monotone():
    states = {}
    for n in range(1, 41):
        for k in range(n + 1):
            states[(n, k)] = (V.plus_state(n, k), V.minus_state(n, k))
    for (n1, k1), (n2, k2) in product([(n, k) for n in (1, 10, 20, 30, 40) for k in range(n + 1)], repeat=2):
        v, code = V.primary_map(n1, k1, n2, k2)
        assert v in SCORE
        assert (v == 'WEAKEN') == (code in ('W1', 'W2', 'W3'))
        if k1 < n1: assert SCORE[V.primary_map(n1, k1 + 1, n2, k2)[0]] >= SCORE[v]
        if k2 < n2: assert SCORE[V.primary_map(n1, k1, n2, k2 + 1)[0]] <= SCORE[v]
    assert set(V.PRIMARY_TABLE) == set(product(('S', 'U_hi', 'U_lo', 'R'), ('N', 'U', 'Y')))


def test_lesson_exercise():
    a = V.primary_verdict(dict(MEETS=24, FAILS=6), dict(MEETS=5, FAILS=25))
    b = V.primary_verdict(dict(MEETS=24, FAILS=6), dict(MEETS=20, FAILS=10))
    c = V.primary_verdict(dict(MEETS=17, FAILS=9, UNRESOLVED=4), dict(MEETS=3, FAILS=27))
    c34 = V.primary_verdict(dict(MEETS=17, FAILS=13, UNRESOLVED=4), dict(MEETS=3, FAILS=27))
    assert a['verdict'] == 'PASS'
    # Lesson answer key says Y- -> W1; exact CP: 20/30 lower97.5%=.472<.5, so U- -> W2.
    assert not stats.lower_bound_exceeds(30, 20, HALF, A)
    assert (b['verdict'], b['codes']) == ('WEAKEN', ['W2'])
    b21 = V.primary_verdict(dict(MEETS=24, FAILS=6), dict(MEETS=21, FAILS=9))
    assert (b21['verdict'], b21['codes']) == ('WEAKEN', ['W1'])
    assert c['verdict'] == 'INCONCLUSIVE' and c['codes'] == ['VALIDITY:R5_UMAX_plus']
    assert c34['codes'] == ['VALIDITY:R5_UMAX_plus']                    # 4/34 > .10 as well


def test_r4_and_r5_rules():
    exact10 = V.primary_verdict(dict(MEETS=20, FAILS=7, UNRESOLVED=3), dict(MEETS=2, FAILS=28))
    assert exact10['codes'] != ['VALIDITY:R5_UMAX_plus']               # exactly .10 is not > .10
    assert exact10['r4'] is not None
    assert V.primary_verdict({}, dict(MEETS=1, FAILS=29))['codes'] == ['VALIDITY:R5_N0_plus']
    assert V.combine([('PASS', None), ('FALSIFY', None)])[0] == 'INCONCLUSIVE'
    assert V.combine([('WEAKEN', 'W3'), ('FALSIFY', None)])[:2] == ('INCONCLUSIVE', ['R4_FALSIFY_NOT_ROBUST'])
    assert V.combine([('PASS', None), ('WEAKEN', 'W2')])[:2] == ('WEAKEN', ['R4_DOWNGRADE', 'W2'])
    assert V.combine([('WEAKEN', 'W1'), ('WEAKEN', 'W3')])[:2] == ('WEAKEN', ['W1', 'W3'])
    v = V.primary_verdict(dict(MEETS=20, FAILS=9, UNRESOLVED=1), dict(MEETS=9, FAILS=20, UNRESOLVED=1))
    assert v['r4']['downgraded'] and v['verdict'] == 'WEAKEN'
    assert V.primary_verdict(dict(MEETS=30), dict(FAILS=30), validity_reasons=['CONTROL_NONZERO'])['verdict'] == 'INCONCLUSIVE'


def test_four_corners_never_more_favorable_than_two_uniform():
    for m1, u1, m2, u2 in product(range(0, 31, 3), range(0, 4), range(0, 31, 3), range(0, 4)):
        plus, minus = dict(MEETS=m1, FAILS=30 - m1, UNRESOLVED=u1), dict(MEETS=m2, FAILS=30 - m2, UNRESOLVED=u2)
        r = V.primary_verdict(plus, minus)
        if r['r4'] is None: continue
        assert SCORE[r['verdict']] <= SCORE[V.combine([tuple(x) for x in (r['r4']['corners']['MEETS/MEETS'],
                                                                          r['r4']['corners']['FAILS/FAILS'])])[0]] \
            or r['verdict'] == 'INCONCLUSIVE'


def test_gamma_map():
    g = dict(pi0=F(4, 5), alpha=F(1, 20), n_min=30)
    assert V.gamma_map(29, 29, **g) == ('INCONCLUSIVE', 'N_MIN')
    assert V.gamma_map(30, 28, **g) == ('PASS', None)
    assert V.gamma_map(30, 27, **g) == ('WEAKEN', 'POINT_ONLY')
    assert V.gamma_map(30, 24, **g)[0] in ('WEAKEN', 'INCONCLUSIVE')
    assert V.gamma_map(30, 18, **g) == ('FALSIFY', 'SUBSTITUTION')
    for k in range(31):
        assert V.gamma_map(30, k, **g)[0] in SCORE
    assert V.gamma_verdict(dict(MEETS=28, FAILS=2), **g)['verdict'] == 'PASS'
    assert V.gamma_verdict(dict(MEETS=27, FAILS=1, UNRESOLVED=2), **g)['verdict'] == 'WEAKEN'
    assert V.gamma_verdict(dict(MEETS=26, UNRESOLVED=4), **g)['codes'] == ['VALIDITY:R5_UMAX']


# ---------------------------------------------------------------- design-only regions
def test_region_rules_cannot_read_outcomes():
    with pytest.raises(KeyError):
        reg()['G_M_pctC']
    bad = Box('BAD', (('lambdaB', '8', '8'),))
    with pytest.raises(TypeError):
        in_region(bad, dict(lambdaB=8, G_M_pctC=5.0))
    with pytest.raises(KeyError):
        in_region(lambda d: d['G_M_pctC'] > 1, reg())
    with pytest.raises(ValueError): Box('X', (('P_flip', '0', '1'),))
    with pytest.raises(ValueError): Box('X', (('kappa', '1', '1/2'),))


def test_box_membership_exact_and_derived():
    b = Box('MV', (('lambdaB', '8', '8'), ('lambdaA', '7', '15/2'), ('kappa', '1/10', '3/10'), ('h', '12', '16')))
    assert in_region(b, reg()) and in_region(b, reg(lA='15/2', kappa='3/10', h='16'))
    assert not in_region(b, reg(lA='8')) and not in_region(b, reg(kappa='1'))
    assert reg(lA='15/2', u='3/2')['rhoA'] == F(9, 10) == reg(lA='8', u='1')['rhoA']
    assert reg(lB='6', u='3/2')['phi'] == F(3, 8)
    assert b.active() == ['lambdaB', 'lambdaA', 'kappa', 'h']
    assert sealed_and_exposed(Box('ALL', (('lambdaA', '6', '10'),)))['sealed_inside'] == ['R09', 'R10']
    assert sealed_and_exposed(b)['sealed_inside'] == []


def test_pilot_design_counts_without_outcomes():
    disc = D.load()
    assert len(disc) == 162 and len(disc.duplicates) == 6
    assert all(diff == 0 for _, _, diff in disc.duplicates)
    assert sum(in_region(EMPTY, d) for _, _, d in disc.designs()) == 0
    everything = Box('ALL', (('c_sw', '0', '0'),))
    assert sum(in_region(everything, d) for _, _, d in disc.designs()) == 162


def test_every_summary_is_logged(tmp_path):
    rows = [('T1', 's', reg(), dict.fromkeys(D.OUTCOMES, 0.0) | dict(G_M_pctC=2.0)),
            ('T2', 's', reg(lA='8'), dict.fromkeys(D.OUTCOMES, 0.0))]
    disc = D.Discovery(rows, {}, [])
    log = D.ForkingLog(tmp_path / 'log.jsonl')
    pred = dict(MV=('G_M_pctC', '>=', 1))
    assert D.summarize(disc, EMPTY, pred, log, who='test', purpose='empty')[0] == 0
    n, counts, _ = D.summarize(disc, Box('ALL', (('c_sw', '0', '0'),)), pred, log, who='test', purpose='all')
    assert (n, counts['MV']) == (2, 1)
    D.table(disc, [('c', EMPTY)], pred, log, who='test', purpose='table')
    assert [e['seq'] for e in log.entries()] == [0, 1, 2]
    both = dict(AND=[('G_M_pctC', '>=', 1), ('abs(G_S_pctC)', '<', 0.5)], MIN=('min(G_M_pctC,G_S_pctC)', '>', -1))
    _, counts, _ = D.summarize(disc, Box('ALL', (('c_sw', '0', '0'),)), both, log, who='test', purpose='and')
    assert counts == dict(AND=1, MIN=2) and len(log.entries()) == 4
    assert log.entries()[1]['ids'] == ['T1', 'T2']


# ---------------------------------------------------------------- frozen card ↔ code consistency
def test_card_machine_block_matches_code():
    from experiments.R3R_06_cards.check_cards import load_card
    from experiments.R3R_06_cards.run_discovery import CANDIDATES
    card = load_card()
    assert card['status'] == 'FROZEN' and card['allocation']['secondary'] is None
    table = card['verdict_maps']['primary_v1']['table']
    for (p, m), (v, code) in V.PRIMARY_TABLE.items():
        assert table[f'{p}|{m}'] == (v if code is None else f'{v}-{code}')
    logged = {b.rule_id: sorted(b.bounds) for b in CANDIDATES}
    for rid, spec in card['regions'].items():
        if rid == 'SH-BND': continue
        assert logged[rid] == sorted((c, lo, hi) for c, (lo, hi) in spec['bounds'].items())
    for name, c in card['cards'].items():
        assert F(c['aggregate']['alpha']) == V.PRIMARY_ALPHA and F(c['aggregate']['pi0']) == V.PRIMARY_PI0
        assert F(c['r6_boundary']) == V.CRITERIA[c['criterion']][0]


def test_card_receipt_verifies_and_fails_closed(tmp_path, monkeypatch):
    import json as _json
    from experiments.R3R_06_cards import verify_cards as VC
    assert VC.verify()['status'] == 'PASS'
    rec = _json.loads(VC.RECEIPT.read_text())
    rec['sha256']['notes/phases/PHASE_3R_hypothesis_cards.md'] = '0' * 64
    fake = tmp_path / 'lock.json'; fake.write_text(_json.dumps(rec))
    monkeypatch.setattr(VC, 'RECEIPT', fake)
    r = VC.verify()
    assert r['status'] == 'FAIL' and any('hypothesis_cards.md' in e for e in r['errors'])
    with pytest.raises(SystemExit): VC.create('HEAD')          # receipt already exists: no silent overwrite
