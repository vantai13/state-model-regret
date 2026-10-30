"""Doan Van Tai — card-v2 numerics receipt, lean adapter, dry-run B and the one-shot CF parameter draw (DL-095).

AI (Claude) theo ủy quyền. Mirrors experiments/R3R_07_confirmation/frame.py (gates, write-once, consumed attempt
directory) for card v2 and the lean numerics receipt. The original sampler is used unchanged; its module-level
STEP is set to the card-v2 rounding only while drawing (sampler.py stays byte-identical to native05's manifest).

The adapter turns engine rows into scorer input: arithmetic_pass is the preregistered lean rule (normalized
arithmetic width <= 1/4000 and tolerance consistency on main and both neighbours), and R3 escalation runs at
most two shared steps (K,ref) -> (2K,ref) -> (2K,2ref) for regimes left UNRESOLVED near a threshold.
The scorer (score.label_result / score_batch, verdict.py) is unchanged.
"""
from contextlib import contextmanager
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess

from experiments.R3R_07_confirmation import sampler as S
from experiments.R3R_07_confirmation import score
from experiments.R3R_07_confirmation.common import ORDER, TEST_RANGE, check_committed, digest, environment, write_once
from experiments.R3R_07_confirmation.frame import validate_rows
from experiments.R3R_07_confirmation.inventory import reserved_keys, seen_regimes
from experiments.R3R_07_confirmation.power import select_allocation
from experiments.R3R_14_lean_close import cards_v2, checks

NUMERICS_TAG = 'numerics-v1.3.1-lean'
NUMERIC_SPEC = 'notes/design/numerics_v1_3_1_lean.json'
NUMERIC_RECEIPT = 'notes/phases/numerics_v1_3_1_lean.lock.json'


def _git(*a):
    return subprocess.check_output(['git', *a], stderr=subprocess.PIPE)


def card_steps(card):
    rounding = card['measure_rules']['rounding']
    return {key: F(rounding[key]) for key in S.STEP}


@contextmanager
def card_rounding(card):
    old = S.STEP
    S.STEP = card_steps(card)
    try:
        yield
    finally:
        S.STEP = old


def validate_numerics_spec(spec):
    required = ('K_star', 'ref_star', 'dt_star', 'S1_route', 'quadrature_tail_policy', 'p95_bundle_cpu_seconds',
                'fixed_validation_cpu_seconds', 'r_coverage_report', 'card_version')
    if spec.get('status') != 'CLOSED_WITH_DECLARED_SCOPE' or any(spec.get(k) in (None, '', False) for k in required):
        raise ValueError('lean numerics spec incomplete')
    K, ref = spec['K_star'], spec['ref_star']
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 2 or x % 2 for x in (K, ref)) or F(spec['dt_star']) != F(1, 120 * ref):
        raise ValueError('invalid global levels/dt')
    if F(str(spec['p95_bundle_cpu_seconds'])) <= 0 or F(str(spec['fixed_validation_cpu_seconds'])) < 0:
        raise ValueError('invalid measured timing')
    for key in ('kappa_3_h_16', 'rational_rate_resolution_1_100', 'interior_lattice_feasibility'):
        if spec.get('coverage', {}).get(key) is not True:
            raise ValueError('missing numerics coverage: ' + key)


def verify_numerics_lean():
    cards_v2.verified_card()
    if _git('cat-file', '-t', NUMERICS_TAG).decode().strip() != 'tag':
        raise ValueError('annotated lean numerics tag required')
    commit = _git('rev-parse', NUMERICS_TAG + '^{commit}').decode().strip()
    _git('merge-base', '--is-ancestor', commit, 'HEAD')
    receipt = json.loads(Path(NUMERIC_RECEIPT).read_text())
    spec = json.loads(_git('show', f'{commit}:{NUMERIC_SPEC}'))
    if receipt.get('commit') != commit:
        raise ValueError('lean numerics tag/receipt mismatch')
    paths = spec.get('freeze_paths')
    import hashlib
    expected = {p: hashlib.sha256(_git('show', f'{commit}:{p}')).hexdigest() for p in paths}
    if expected != receipt.get('source_sha256') or any(digest(p) != h for p, h in expected.items()):
        raise ValueError('lean numerics manifest/blob mismatch')
    validate_numerics_spec(spec)
    return spec


def adapter_result(levels, main):
    """Scorer input for one regime from rows at main (K, ref) and its two neighbours."""
    K, ref = main
    rows = [levels.get(main), levels.get((K // 2, ref)), levels.get((K, ref // 2))]
    if any(r is None or r.get('status') != 'COMPLETED' for r in rows):
        return dict(main=rows[0] or dict(Cref='1'), coarse_K=None, coarse_dt=None, arithmetic_pass=False)
    lean_ok = all(checks.arithmetic_ok(r) and not checks.consistency(r) for r in rows)
    return dict(main=rows[0], coarse_K=rows[1], coarse_dt=rows[2], arithmetic_pass=lean_ok)


def escalation_plan(K, ref):
    return [(K, ref), (2 * K, ref), (2 * K, 2 * ref)]


def label_with_escalation(criterion, levels, K, ref):
    """R3: label at (K,ref); if UNRESOLVED and a further step was computed, use the next step's label."""
    trail = []
    for main in escalation_plan(K, ref):
        if main not in levels:
            break
        label = score.label_result(criterion, adapter_result(levels, main))
        trail.append((list(main), label))
        if label != 'UNRESOLVED':
            break
    return (trail[-1][1] if trail else 'UNRESOLVED'), trail


def generate(prereg_path, attempt_dir):
    """One-shot CF parameter list for card v2. No engine is imported or run."""
    card = cards_v2.verified_card()
    numerics = verify_numerics_lean()
    prereg_path = Path(prereg_path)
    check_committed(prereg_path)
    prereg = json.loads(prereg_path.read_text())
    if prereg.get('status') != 'LOCKED_BEFORE_SAMPLING' or tuple(prereg['regions_order']) != ORDER:
        raise ValueError('locked prereg and fixed region order required')
    if Path(attempt_dir).resolve() != Path(prereg['generation_dir']).resolve():
        raise ValueError('only the committed one-shot generation directory is allowed')
    for role, path in prereg['artifacts'].items():
        check_committed(path['path'])
        if digest(path['path']) != path['sha256']:
            raise ValueError(f'{role} hash mismatch')
    if prereg.get('n_rule_status') != 'AUTHOR_ADOPTED':
        raise ValueError('sample-size rule not adopted by author')
    allocation = select_allocation(prereg['budget_cpu_hours'], numerics['p95_bundle_cpu_seconds'],
                                   numerics['fixed_validation_cpu_seconds'], numerics_closed=True)
    if allocation['status'] == 'HOLD_BUDGET' or allocation['n'] != prereg['n']['scored'] or allocation['bnd'] != prereg['n']['bnd']:
        raise ValueError('n does not follow committed budget rule')
    root = prereg['seed']['root']
    if isinstance(root, bool) or not isinstance(root, int) or root < 0 or root in TEST_RANGE or 318300000 <= root <= 318409999:
        raise ValueError('confirmation root invalid or reserved for tests')
    record = json.loads(Path(prereg['seed']['allocation_path']).read_text())
    if record.get('root') != root or record.get('status') != 'COMMITTED_BEFORE_DRAW':
        raise ValueError('confirmation root not allocated before draw')
    inventory = json.loads(Path(prereg['artifacts']['inventory']['path']).read_text())
    out = Path(attempt_dir)
    out.mkdir(parents=True, exist_ok=False)                  # a consumed directory records even a failed attempt
    write_once(out / 'attempt.json', dict(status='STARTED', root=root, prereg_sha256=digest(prereg_path),
                                          environment=environment(), engine_runs=0))
    with card_rounding(card):
        rows, redraws = S.sample_all(root, card, prereg['n']['scored'], prereg['n']['bnd'],
                                     reserved_keys(inventory), purpose='COMMITTED_CONFIRMATION')
    counts = validate_rows(rows, card, prereg['n']['scored'], prereg['n']['bnd'], inventory, purpose='COMMITTED_CONFIRMATION')
    steps = card_steps(card)
    for row in rows:
        for key, step in steps.items():
            if (F(row['regime'][key]) / step).denominator != 1:
                raise ValueError('drawn value off the card-v2 grid')
    seen = seen_regimes(inventory)
    for row in rows:
        row['distance_to_seen'] = S.distances(row['regime'], seen, card['regions'][row['origin_region']])
    write_once(out / 'regimes_cf.json', dict(prereg_sha256=digest(prereg_path), card_version=2, rows=rows))
    write_once(out / 'generation_log.json', dict(status='GENERATED_ONCE_NO_ENGINE', counts=counts, redraws=redraws,
                                                frame_sha256=digest(out / 'regimes_cf.json')))
    return counts


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--prereg', type=Path, required=True)
    p.add_argument('--attempt-dir', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(generate(a.prereg, a.attempt_dir), indent=2))
