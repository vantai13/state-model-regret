"""Doan Van Tai — final lean L3R.7 steps (DL-095/096). AI (Claude) theo ủy quyền.

  python -m experiments.R3R_14_lean_close.close timing        # p95, fixed cost, n by DL-077 -> timing_summary.json
  python -m experiments.R3R_14_lean_close.close spec          # numerics_v1_3_1_lean.json (commit, then tag)
  python -m experiments.R3R_14_lean_close.close receipt       # lock over the tagged spec commit
  python -m experiments.R3R_14_lean_close.close dryrun        # dry-run B on DL-093 discovery corners + validity checks
  python -m experiments.R3R_14_lean_close.close seed          # confirmation root from the OS CSPRNG (commit before draw)
  python -m experiments.R3R_14_lean_close.close prereg        # cf_prereg.json LOCKED_BEFORE_SAMPLING
The CF draw itself is frame_v2.generate (one shot). No engine call on any CF regime anywhere in this module.
"""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys

import numpy as np

from experiments.R3R_07_confirmation import score
from experiments.R3R_07_confirmation.common import ORDER, TEST_RANGE, digest
from experiments.R3R_07_confirmation.power import select_allocation
from experiments.R3R_14_lean_close import checks, frame_v2
from experiments.R3R_14_lean_close.engine import write_once
from experiments.R3R_14_lean_close.run import OUT, ROOT, case_table, load_prereg

BUDGET_CPU_HOURS = 48
SPEC = Path(frame_v2.NUMERIC_SPEC)
RECEIPT = Path(frame_v2.NUMERIC_RECEIPT)
SEED = OUT / 'seed_allocation.json'
CF_PREREG = Path('experiments/R3R_14_lean_close/cf_prereg.json')
GENERATION_DIR = 'results/lessons/l3r_7/lean_close/cf_generation/attempt01'


def _git(*a):
    return subprocess.check_output(['git', *a], stderr=subprocess.PIPE)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def selected_level():
    sel = json.loads((OUT / 'numerics_selection.json').read_text())
    return tuple(sel['selected_level'])


def timing(cfg):
    K, ref = selected_level()
    corner = cfg['timing']['cases_corner']
    rrate = [c['id'] + '_R' for c in cfg['representation']['cases']] + [d['id'] for d in cfg['calibration']['r_interior_designs']]
    bundles = {}
    for cid in corner + rrate:
        b = json.loads((OUT / 'timing' / cid / 'bundle.json').read_text())
        if b['status'] != 'COMPLETED' or b['level'] != [K, ref]:
            raise SystemExit(f'timing bundle not usable: {cid}')
        bundles[cid] = b['bundle_cpu_seconds']
    p95 = {name: float(np.percentile([bundles[c] for c in ids], 95, method='higher'))
           for name, ids in (('corner_audit', corner), ('r_rate', rrate))}
    planning = max(p95.values())
    max_corner, max_rrate = max(bundles[c] for c in corner), max(bundles[c] for c in rrate)
    fixed = 2 * max_corner + 3 * 2 * max_corner + 4 * max_rrate
    allocation = select_allocation(BUDGET_CPU_HOURS, F(planning).limit_denominator(10**6),
                                   F(fixed).limit_denominator(10**6), numerics_closed=True)
    out = dict(level=[K, ref], bundles_cpu_seconds=bundles, p95_by_class=p95, planning_p95_bundle_cpu_seconds=planning,
               fixed_validation_cpu_seconds=fixed, fixed_rule=cfg['timing']['fixed_validation_seconds'],
               budget_cpu_hours=BUDGET_CPU_HOURS, allocation=allocation, rule='DL-077 via power.select_allocation',
               caveat='cold cache per bundle, local WSL2 machine, one call per bundle level; not a population p95')
    write_once(OUT / 'timing_summary.json', out)
    return out


def spec(cfg):
    K, ref = selected_level()
    t = json.loads((OUT / 'timing_summary.json').read_text())
    if t['allocation']['status'] == 'HOLD_BUDGET':
        raise SystemExit('HOLD_BUDGET: n < 30 under B = 48 CPU-hours; L3R.7 cannot close without a DL raising B')
    cases = case_table(cfg)
    rows = lambda cid, lv: json.loads((OUT / 'calibration' / cid / f'level_{lv[0]}_{lv[1]}.json').read_text())
    levels = [(K, ref), (K // 2, ref), (K, ref // 2)]
    k3h16 = [c for c, p in cases.items() if F(p[2]) == 3 and F(p[4]) == 16]
    rint = [d['id'] for d in cfg['calibration']['r_interior_designs']]
    coverage = dict(
        kappa_3_h_16=bool(k3h16) and all(rows(c, lv)['status'] == 'COMPLETED' for c in k3h16 for lv in levels),
        rational_rate_resolution_1_100=json.loads((OUT / 'representation_selection.json').read_text())['selected_r'] == '1/100',
        interior_lattice_feasibility=all(rows(c, lv)['status'] == 'COMPLETED' for c in rint for lv in levels))
    any_row = rows(next(iter(cases)), (K, ref))
    native05 = json.loads(Path('experiments/R3R_11_native_population/prereg.json').read_text())
    freeze = [str(SPEC), 'experiments/R3R_14_lean_close/prereg.json', 'results/lessons/l3r_7/lean_close/numerics_selection.json',
              'results/lessons/l3r_7/lean_close/timing_summary.json', 'results/lessons/l3r_7/lean_close/representation_selection.json',
              'results/lessons/l3r_7/lean_close/replay_report.json', 'notes/phases/PHASE_3R_hypothesis_cards_v2.lock.json',
              'experiments/R3R_14_lean_close/checks.py', 'experiments/R3R_14_lean_close/engine.py',
              'experiments/R3R_14_lean_close/run.py', 'experiments/R3R_14_lean_close/analyze.py',
              'experiments/R3R_14_lean_close/frame_v2.py', 'experiments/R3R_08_population_numerics/population.py',
              'experiments/R3R_10_interval_evaluation/evaluator.py', 'experiments/R3R_05_contract/rules.py']
    doc = dict(owner='Doan Van Tai', status='CLOSED_WITH_DECLARED_SCOPE', version='v1.3.1-lean', card_version=2,
               decision=['DL-095', 'DL-096'], contract='contract-v1.3',
               K_star=K, ref_star=ref, dt_star=str(F(1, 120 * ref)),
               S1_route=any_row['S1_route'], stay_cost_route=any_row['stay_cost_route'],
               quadrature_tail_policy=native05['tail_policy'],
               acceptance='contract R1 (both coarse axes) + normalized arithmetic width <= 1/4000 + consistency within TOL_NUM=1/400 of Cref',
               calibration_cases=len(cases), calibration_all_pass=True,
               p95_bundle_cpu_seconds=t['planning_p95_bundle_cpu_seconds'],
               fixed_validation_cpu_seconds=t['fixed_validation_cpu_seconds'],
               allocation=t['allocation'], r_coverage_report='results/lessons/l3r_7/lean_close/representation_selection.json',
               coverage=coverage, freeze_paths=freeze,
               scope=['card v2 frame only (rates on the 1/100 grid); card v1 numerics stay open',
                      'R1/R7: refinement differences are diagnostics, not certified error bounds',
                      'escalation R3 for scoring: (640,4) -> (1280,4) -> (1280,8), computed only for regimes left UNRESOLVED',
                      'no CF outcome computed or read'])
    if not all(coverage.values()):
        raise SystemExit(f'coverage incomplete: {coverage}')
    SPEC.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    return doc


def receipt():
    if RECEIPT.exists():
        raise SystemExit('receipt exists')
    commit = _git('rev-parse', frame_v2.NUMERICS_TAG + '^{commit}').decode().strip()
    doc = json.loads(_git('show', f'{commit}:{SPEC}'))
    files = {p: hashlib.sha256(_git('show', f'{commit}:{p}')).hexdigest() for p in doc['freeze_paths']}
    rec = dict(owner='Doan Van Tai', tag=frame_v2.NUMERICS_TAG, tag_object=_git('rev-parse', frame_v2.NUMERICS_TAG).decode().strip(),
               commit=commit, source_sha256=files, created_utc=datetime.now(timezone.utc).isoformat(),
               decision='DL-096', scope='lean numerics v1.3.1 for card v2 only')
    RECEIPT.write_text(json.dumps(rec, indent=1) + '\n')
    return rec


DRY_ROWS = [('CAL_CORNER_033', 'MV+A'), ('CAL_CORNER_034', 'MV+A'), ('CAL_CORNER_001', 'SH+A'), ('CAL_CORNER_002', 'SH+A')]
IDENTICAL = ['RATE_MV_EDGE_K1_10_H16_R', 'RATE_MV_EDGE_K3_H16_R', 'RATE_SH_EDGE_K1_10_H16_R', 'RATE_SH_EDGE_K3_H16_R']


def dryrun(cfg):
    """Pipeline check on seen discovery corners (DL-093): saved engine rows -> lean adapter -> unchanged scorer.
    Plus validity: zero controls exactly zero; identical models give G_M = G_M|S1 = 0 exactly. Not evidence."""
    spec_doc = frame_v2.verify_numerics_lean()
    K, ref = spec_doc['K_star'], spec_doc['ref_star']
    cases = case_table(cfg)
    def levels_of(cid):
        out = {}
        for f in (OUT / 'calibration' / cid).glob('level_*.json'):
            r = json.loads(f.read_text())
            out[tuple(map(int, f.stem.split('_')[1:]))] = r
        return out
    rows, results, trails = [], {}, {}
    for cid, origin in DRY_ROWS:
        p = cases[cid]
        reg = dict(id=cid, lambdaA=p[0], lambdaB=p[1], u=str(2 * F(p[3])), kappa=p[2], h=p[4], c_sw=p[5])
        rows.append(dict(regime=reg, origin_region=origin, purpose='DRY_RUN_DISCOVERY_NOT_EVIDENCE'))
        lv = levels_of(cid)
        criterion = 'effect' if origin.startswith('MV') else 'harm'
        label, trail = frame_v2.label_with_escalation(criterion, lv, K, ref)
        results[cid] = frame_v2.adapter_result(lv, (K, ref))
        trails[cid] = dict(label=label, trail=trail,
                           metric_pct=float(F(lv[(K, ref)]['G_M' if criterion == 'effect' else 'G_S']) / F(lv[(K, ref)]['Cref']) * 100))
    scored = score.score_batch(rows, results)
    zero = {}
    for cid in ('ZERO_MV', 'ZERO_SH'):
        row = json.loads((OUT / 'calibration' / cid / f'level_{K}_{ref}.json').read_text())
        score.require_zero_control({k: row[k] for k in checks.CONTRASTS})
        zero[cid] = 'EXACT_ZERO'
    from experiments.R3R_08_population_numerics import population
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    identical = {}
    for cid in IDENTICAL:
        p = cases[cid]
        r = population.evaluate((cid, p[0], p[1], p[2], p[3], p[4], ref, K, p[5]), Path.home() / '.cache/smr_lean_close',
                                identical_models=True)
        score.require_identical_models({k: str(r[k]) for k in ('G_M', 'G_M_S1')})
        identical[cid] = 'G_M = G_M|S1 = 0 exactly'
    anchors = {a: json.loads(Path(f'results/R3R_population_numerics/20261030_05/marginal/{a}/anchor_comparison.json').read_text())['status']
               for a in ('X2065', 'X1008', 'X1009')}
    out = dict(level=[K, ref], scope='pipeline check on seen discovery/calibration; NOT evidence (lesson Part F)',
               rows=[dict(id=r['regime']['id'], origin=r['origin_region']) for r in rows], labels=trails,
               scorer=scored, zero_controls=zero, identical_models=identical, anchors_native05=anchors,
               engine_on_CF=0)
    write_once(OUT / 'dry_run_B.json', out)
    return out


def seed():
    if SEED.exists():
        raise SystemExit('root already allocated')
    while True:
        root = secrets.randbits(63)
        if root not in TEST_RANGE and not 318300000 <= root <= 318409999:
            break
    rec = dict(owner='Doan Van Tai', stage='confirmation', root=root, status='COMMITTED_BEFORE_DRAW',
               method='secrets.randbits(63), OS CSPRNG; drawn once after numerics and n', decision='DL-096',
               created_utc=datetime.now(timezone.utc).isoformat())
    write_once(SEED, rec)
    return rec


def prereg():
    if CF_PREREG.exists():
        raise SystemExit('CF prereg exists')
    t = json.loads((OUT / 'timing_summary.json').read_text())
    seed_rec = json.loads(SEED.read_text())
    paths = dict(inventory='results/lessons/l3r_7/lean_close/collision_inventory_v3.json',
                 card_receipt='notes/phases/PHASE_3R_hypothesis_cards_v2.lock.json',
                 card='notes/phases/PHASE_3R_hypothesis_cards_v2.md',
                 sampler='experiments/R3R_07_confirmation/sampler.py',
                 scorer='experiments/R3R_06_cards/verdict.py', score_adapter='experiments/R3R_07_confirmation/score.py',
                 frame='experiments/R3R_14_lean_close/frame_v2.py', checks='experiments/R3R_14_lean_close/checks.py',
                 numerics_receipt=str(RECEIPT), numerics_spec=str(SPEC),
                 seed_allocation=str(SEED.relative_to(ROOT)), dry_run='results/lessons/l3r_7/lean_close/dry_run_B.json')
    doc = dict(owner='Doan Van Tai', status='LOCKED_BEFORE_SAMPLING', decision=['DL-095', 'DL-096'], card_version=2,
               regions_order=list(ORDER), generation_dir=GENERATION_DIR,
               artifacts={k: dict(path=v, sha256=sha(v)) for k, v in paths.items()},
               n=dict(scored=t['allocation']['n'], bnd=t['allocation']['bnd']), budget_cpu_hours=BUDGET_CPU_HOURS,
               n_rule_status='AUTHOR_ADOPTED', n_rule='DL-077',
               seed=dict(root=seed_rec['root'], allocation_path=str(SEED.relative_to(ROOT))),
               adapter='frame_v2.adapter_result + label_with_escalation (lean rule DL-095, R3 two shared steps)',
               forbidden=['engine on CF before Gate 3R / Phase 4', 'R09/R10', 'changing card, numerics, n, root or rules after the draw',
                          'regenerating the list except through the deviation policy (new attempt, same root, DL)'])
    CF_PREREG.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    return doc


if __name__ == '__main__':
    step = sys.argv[1]
    cfg = load_prereg()
    fn = dict(timing=lambda: timing(cfg), spec=lambda: spec(cfg), receipt=receipt, dryrun=lambda: dryrun(cfg),
              seed=seed, prereg=prereg)[step]
    print(json.dumps(fn(), indent=1, ensure_ascii=False, default=str)[:4000])
