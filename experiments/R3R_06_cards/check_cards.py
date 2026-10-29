"""Doan Van Tai — L3R.6 nine pre-freeze checks on the hypothesis card set (no outcome).

Reads only: the card file, contract tag, forking log/candidates already committed,
v1.2 grid coordinates. Writes results/lessons/l3r_6/card_checks.json.
"""
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from experiments.R3R_05_contract.schema import validate, IDENTITY
from experiments.R3R_06_cards import stats, verdict as V
from experiments.R3R_06_cards.regions import Box, COORDS, DesignView, in_region, sealed_and_exposed
from experiments.R3R_06_cards.run_discovery import CANDIDATES

CARD = Path('notes/phases/PHASE_3R_hypothesis_cards.md')
OUT = Path('results/lessons/l3r_6/card_checks.json')
GRID_VALUES = {'lambdaA': {'6', '13/2', '7', '15/2', '8'}, 'lambdaB': {'6', '7', '8'}, 'u': {'1', '3/2'},
               'kappa': {'1/10', '3/10', '1', '3'}, 'h': {'2', '8', '12', '16'}, 'c_sw': {'0'}}
VERDICTS = {'PASS', 'WEAKEN', 'INCONCLUSIVE', 'FALSIFY'}
SCORE = {'PASS': 3, 'WEAKEN': 2, 'INCONCLUSIVE': 1, 'FALSIFY': 0}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_card(path=CARD):
    m = re.search(r'<!-- L3R6_CARDS\n(.*?)\n-->', path.read_text(), re.S)
    if not m: raise SystemExit('machine block missing')
    return json.loads(m.group(1))


def box_of(rid, spec):
    return Box(rid, tuple((c, lo, hi) for c, (lo, hi) in spec['bounds'].items()), role=spec['role'])


def corners(spec):
    keys = list(spec['bounds'])
    for vals in product(*[spec['bounds'][k] for k in keys]):
        yield dict(zip(keys, vals))


def check_regions(card):
    out, boxes = {}, {}
    logged = {b.rule_id: b for b in CANDIDATES}
    for rid, spec in card['regions'].items():
        b = box_of(rid, spec); boxes[rid] = b
        r = dict(design_only=all(c in COORDS for c in spec['bounds']),
                 identity_complete=set(spec['bounds']) == set(IDENTITY))
        errs = []
        for c in corners(spec):
            try: validate(dict(id='corner', contract_id='contract-v1.3', role='confirmation', **c), primary=True)
            except ValueError as e: errs.append(str(e))
        r['all_corners_valid_primary'] = not errs
        r['round_or_grid_bounds'] = all(lo in GRID_VALUES[c] and hi in GRID_VALUES[c] for c, (lo, hi) in spec['bounds'].items())
        meas = spec['measure']; res = card['measure_rules']['rounding']
        free = [c for c, (lo, hi) in spec['bounds'].items() if F(lo) != F(hi)]
        r['measure_covers_free_coords'] = sorted(meas) == sorted(free)
        r['rounding_divides_bounds'] = all((F(v) / F(res[c])).denominator == 1 for c in free for v in spec['bounds'][c])
        r['matches_logged_rule'] = (rid in logged and sorted(logged[rid].bounds) == sorted(b.bounds)) if rid != 'SH-BND' else 'DECLARED_NO_DATA'
        se = sealed_and_exposed(b)
        r['sealed_inside'] = se['sealed_inside']; r['v12_cells_inside'] = se['v12_cells_inside']
        out[rid] = r
    return out, boxes


def check_verdict_coverage(nmax=60):
    seen, bad = set(), []
    pairs = [(n, k) for n in range(1, nmax + 1) for k in range(n + 1)]
    states = {p: (V.plus_state(*p), V.minus_state(*p)) for p in pairs}
    for (n1, k1) in pairs:
        if n1 not in (1, 5, 10, 20, 30, 40, 60): continue
        for (n2, k2) in pairs:
            if n2 not in (1, 5, 10, 20, 30, 40, 60): continue
            v, code = V.PRIMARY_TABLE[(states[(n1, k1)][0], states[(n2, k2)][1])]
            seen.add(v)
            if v not in VERDICTS or (v == 'WEAKEN') != (code in ('W1', 'W2', 'W3')): bad.append((n1, k1, n2, k2))
            if k1 < n1 and SCORE[V.primary_map(n1, k1 + 1, n2, k2)[0]] < SCORE[v]: bad.append(('mono+', n1, k1, n2, k2))
            if k2 < n2 and SCORE[V.primary_map(n1, k1, n2, k2 + 1)[0]] > SCORE[v]: bad.append(('mono-', n1, k1, n2, k2))
    full = []
    for m1, u1, m2, u2 in product(range(0, 31), range(0, 5), range(0, 31, 2), range(0, 5)):
        r = V.primary_verdict(dict(MEETS=m1, FAILS=30 - m1, UNRESOLVED=u1), dict(MEETS=m2, FAILS=30 - m2, UNRESOLVED=u2))
        full.append(r['verdict'])
        if r['verdict'] not in VERDICTS: bad.append(('full', m1, u1, m2, u2))
    two = sum(1 for m1, u1, m2, u2 in product(range(0, 31), range(1, 4), range(0, 31, 2), range(1, 4))
              if (lambda r: r['r4'] and r['verdict'] != V.combine([tuple(r['r4']['corners']['MEETS/MEETS']),
                                                                   tuple(r['r4']['corners']['FAILS/FAILS'])])[0])(
                  V.primary_verdict(dict(MEETS=m1, FAILS=30 - m1, UNRESOLVED=u1), dict(MEETS=m2, FAILS=30 - m2, UNRESOLVED=u2))))
    return dict(table_cells=len(V.PRIMARY_TABLE), verdicts_reached=sorted(seen), violations=bad[:10], n_violations=len(bad),
                full_pipeline_cases=len(full), full_pipeline_verdicts=sorted(set(full)),
                four_corners_vs_two_uniform_differences=two)


def check_power():
    rows = []
    for n in (20, 30, 40, 60):
        for pp, pm in product(('0.6', '0.7', '0.8'), ('0.1', '0.2', '0.3')):
            rows.append(dict(n_each=n, p_plus=pp, p_minus=pm,
                             P_PASS=round(float(V.primary_pass_power(n, F(pp), n, F(pm))), 4),
                             P_S_plus=round(float(V.plus_power(n, F(pp))), 4),
                             P_N_minus=round(float(V.minus_power(n, F(pm))), 4)))
    null = {n: round(float(V.plus_power(n, F(1, 2))), 4) for n in (20, 30, 40, 60)}
    plan = [r for r in rows if r['p_plus'] == '0.7' and r['p_minus'] == '0.2']
    feasible = [r['n_each'] for r in plan if r['P_PASS'] >= 0.5]
    return dict(rows=rows, false_pass_plus_at_p_half=null, planning_point='p+=0.7 (below discovery), p-=0.2',
                smallest_n_each_with_P_PASS_ge_half=min(feasible) if feasible else None,
                note='preliminary; L3R.7 picks n after numerics v1.3.1 and runtime; unresolved/undefined assumed 0')


def main(argv=None):
    card = load_card()
    tag_commit = subprocess.run(['git', 'rev-list', '-n1', card['contract']], capture_output=True, text=True).stdout.strip()
    regions, boxes = check_regions(card)
    cand = json.load(open('results/lessons/l3r_6/discovery/candidates.json'))
    disc = {c['rule']['rule_id']: c for c in cand['candidates']}
    cards = card['cards']
    mv, sh = cards['Hyp-MV'], cards['Hyp-SH']
    flips = {}
    for name, c in cards.items():
        p, m = card['regions'][c['regions']['plus']]['bounds'], card['regions'][c['regions']['minus']]['bounds']
        flips[name] = sorted(k for k in p if p[k] != m[k])
    lb = {rid: [F(x) for x in s['bounds']['lambdaB']] for rid, s in card['regions'].items()}
    disjoint = min(lb[r][0] for r in lb if r.startswith('MV')) > max(lb[r][1] for r in lb if r.startswith('SH'))
    coverage = check_verdict_coverage()
    power = check_power()
    checks = {
        '1_falsifiable': dict(ok=V.primary_map(30, 9, 30, 0)[0] == 'FALSIFY' and V.primary_map(30, 9, 30, 30)[0] == 'FALSIFY',
                              detail='n=30: <=9 MEETS in plus gives R+ -> FALSIFY for any minus state'),
        '2_not_identity': dict(ok=mv['criterion'] == 'effect' and sh['criterion'] == 'harm'
                               and disc['MV-i']['n'] - disc['MV-i']['counts']['MV'] > 0
                               and disc['SH+A']['n'] - disc['SH+A']['counts']['SH'] > 0,
                               detail=dict(MV='identity only gives 0<=G_M<=sigma; >=1% Cref fails in discovery (MV-i 32/32 below)',
                                           SH='identity only bounds |G_S|<=sigma; SH+A has 15/72 FAILS in discovery',
                                           excluded='Gamma>0 in harm, G_M|S1, G_S|M1 not used as card metrics')),
        '3_couplings_declared': dict(ok=disjoint, detail='Gamma>=-min(G_S,G_M); MV regions lambdaB=8 vs SH regions lambdaB in [6,7]: disjoint'),
        '4_prior_filtered': dict(ok=True, detail=dict(MV='P11/P12/AIS22/P13; axes E,M,R; obviousness handled by kappa-only flip',
                                                      SH='K-RM1/K-RM3/V1; axes M,E,R; claim only where/how much')),
        '5_design_only_regions': dict(ok=all(r['design_only'] and r['identity_complete'] and r['round_or_grid_bounds']
                                             and r['all_corners_valid_primary'] and r['measure_covers_free_coords']
                                             and r['rounding_divides_bounds'] for r in regions.values())
                                      and all(len(card['regions'][c['regions']['plus']]['active']) <= 3 for c in cards.values()),
                                      detail=regions),
        '6_control_can_fail': dict(ok=all(f == ['kappa'] for f in flips.values()) and V.minus_state(30, 21) == 'Y'
                                   and disc['MV-ii']['n'] == 0 and disc['SH-ii']['n'] == 0,
                                   detail=dict(flipped=flips, Y_minus_at_n30='>=21 MEETS',
                                               discovery_in_minus=dict(MV=disc['MV-ii']['n'], SH=disc['SH-ii']['n']))),
        '7_mechanism': dict(ok=True, status='MET_AS_AI_DRAFTED_AUTHOR_APPROVED; AUTHOR_OWN_WORDS_OPEN',
                            detail='source vs magnitude separated in both cards; magnitude marked untested'),
        '8_verdict_table_covers_all': dict(ok=coverage['n_violations'] == 0 and set(coverage['full_pipeline_verdicts']) <= VERDICTS,
                                           detail=coverage),
        '9_can_pass': dict(ok=power['smallest_n_each_with_P_PASS_ge_half'] is not None, detail=power),
    }
    extra = dict(contract_tag_commit_ok=tag_commit == card['contract_commit'],
                 author_choices_sha_ok=sha(card['provenance']['author_choices']) == card['provenance']['author_choices_sha256'],
                 forking_log_sha_ok=sha(card['forking_log']['path']) == card['forking_log']['sha256'],
                 forking_log_entries_ok=len(Path(card['forking_log']['path']).read_text().splitlines()) == card['forking_log']['entries'],
                 sealed_none=all(not r['sealed_inside'] for r in regions.values()),
                 v12_claim_ok=all(regions[k]['v12_cells_inside'] == v for k, v in card['v12_cells_inside'].items())
                 and all(not r['v12_cells_inside'] for k, r in regions.items() if k not in card['v12_cells_inside']),
                 no_secondary=card['allocation']['secondary'] is None)
    result = dict(owner='Doan Van Tai', card=str(CARD), card_sha256=sha(CARD), checks=checks, extra=extra,
                  all_ok=all(c['ok'] for c in checks.values()) and all(extra.values()),
                  outcomes_read=False, label='pre-freeze card checks; not evidence')
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str))
    print(json.dumps(dict(all_ok=result['all_ok'], checks={k: c['ok'] for k, c in checks.items()}, extra=extra,
                          card_sha256=result['card_sha256']), ensure_ascii=False, indent=1))
    return 0 if result['all_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
