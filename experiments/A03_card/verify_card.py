"""Doan Van Tai — A03 technical replay and post-registration Git audit.

Prepare: toy math, scoring, protected files, six self-checks. Registered: verify
two distinct commits, annotated tag and card hashes; never run grid D/outcomes.
"""
import argparse
import csv
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from fractions import Fraction as F

from experiments.A00_engine.factorial_core import aggregate
from experiments.A03_card.membership import coordinates, all_memberships
from experiments.A03_card.toy_checks import E8, persistence_rows, check_ledger_bound
from experiments.A03_card.review import six_checks
from experiments.A03_card.provenance import ROOT, CARD, LOCK, metadata, verify_receipt
from experiments.A03_card.grading import Interval, ratio, judge

OUT = ROOT / 'results/lessons/l3_3'


def clean(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [clean(v) for v in value]
    return value


def write(name, value):
    (OUT / name).write_text(json.dumps(clean(value), ensure_ascii=False, indent=2) + '\n')


def csvwrite(name, rows):
    with (OUT / name).open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(clean(rows))


def xml(name):
    suite = ET.parse(OUT / name).getroot().find('testsuite')
    result = {k: int(suite.attrib[k]) for k in ('tests', 'failures', 'errors', 'skipped')}
    result['seconds'] = float(suite.attrib['time'])
    assert not any(result[k] for k in ('failures', 'errors', 'skipped'))
    return result


def prepare():
    config = json.loads((OUT / 'config.json').read_text())
    protected = {}
    for path, sha in config['protected_sha256'].items():
        data = (ROOT / path).read_bytes()
        assert hashlib.sha256(data).hexdigest() == sha
        assert data == subprocess.check_output(['git', 'show', f'{config["base_commit"]}:{path}'], cwd=ROOT)
        protected[path] = sha
    card_tests, full = xml('card_pytest.xml'), xml('full_pytest.xml')
    assert full['tests'] == config['baseline_tests'] + card_tests['tests'] - 5  # five existing guard tests rerun
    mutants = json.loads((OUT / 'mutants/summary.json').read_text())
    assert len(mutants) == 11 and all(m['status'] == 'KILLED' for m in mutants)
    review, good, bad = six_checks()
    write('six_checks.json', review)
    write('witnesses_not_grid.json', {'kind': 'synthetic algebraic witnesses/countermodels, NOT grid outcomes',
                                      'standing': good, 'refuting': bad})
    members = all_memberships()
    write('memberships.json', members)
    write('coordinate_whitelist.json', coordinates())
    csvwrite('membership.csv', [dict(rule=k, scope=section, ids=' '.join(ids), count=len(ids),
                                    adopted=(k == 'K5_kge2'))
                                for k, scopes in members.items() for section, ids in scopes.items()])
    random = check_ledger_bound(config['ledger_cases'], config['ledger_seed'])
    assert random['violations'] == random['independent_abs_error_mismatches'] == 0
    write('ledger_bound.json', random)
    rows = persistence_rows()
    csvwrite('persistence_toys.csv', [dict(toy=r['toy'], keep=r['keep'], mode=r['mode'],
                                         Delta=r['Delta'], Delta_hat=r['Delta_hat'], e_M=r['e_M'],
                                         jA_St=r['jA']['St'], jA_Sw=r['jA']['Sw'],
                                         jB_St=r['jB']['St'], jB_Sw=r['jB']['Sw'],
                                         oracle=r['oracle'], S1M0=r['S1M0']) for r in rows])
    E8_result = aggregate(*E8())
    write('E8_ledger_toy.json', E8_result)
    examples = []
    for label, n, d, relation, threshold in (
            ('within_equivalence', Interval('.42', '.48'), Interval('99.75', '100.25'), '<=', F(1, 200)),
            ('crossing_equivalence', Interval('.46', '.52'), Interval(100, 100), '<=', F(1, 200)),
            ('negative_numerator_correction', Interval(-2, -1), Interval(1, 2), '>', F(1, 200))):
        r = ratio(n, d)
        examples.append(dict(example=label, numerator_lo=n.lo, numerator_hi=n.hi, Cref_lo=d.lo, Cref_hi=d.hi,
                             ratio_lo=r.lo, ratio_hi=r.hi, relation=relation, threshold=threshold,
                             verdict=judge(r, relation, threshold)))
    csvwrite('grading_examples.csv', examples)
    card = (ROOT / CARD).read_bytes()
    info = metadata(card.decode())
    result = dict(status='PASS', stage='technical_before_registration', responsible='Doan Van Tai', date=config['date'],
                  baseline_tests=config['baseline_tests'], card_and_existing_guard_tests=card_tests,
                  new_test_count=card_tests['tests'] - 5, full_tests=full, mutants_killed=11,
                  sanity_items=14, forecast_count=4, mechanism_forecasts=0, adopted_rules=1,
                  K5_main=members['K5_kge2']['main'], K5_heldout=members['K5_kge2']['heldout'],
                  metadata_rows=50, ledger_bound=random, E8_G=E8_result['G'], persistence_rows=len(rows),
                  reviewer=review['reviewer'], protected_sha256=protected,
                  card_content_sha256=hashlib.sha256(card).hexdigest(), card_status=info['status'],
                  already_implied_readback='AUTHOR_ATTESTED', engine_readback='AUTHOR_ATTESTED',
                  grid_outcomes_computed=0, new_grid_D_generated=0, A01='NOT RUN', A04='NOT RUN',
                  A05_F='NOT FROZEN', A05_T='NOT RUN', registration='PENDING_TWO_COMMIT_PROTOCOL')
    write('verification.json', result)
    print(json.dumps(clean(result), ensure_ascii=False, indent=2))


def registered():
    result = verify_receipt()
    changed = subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r',
                                       result['prediction_card_commit']], cwd=ROOT, text=True).splitlines()
    assert changed == [CARD], changed
    card_blob = subprocess.check_output(['git', 'show', result['prediction_card_commit'] + ':' + CARD], cwd=ROOT)
    assert hashlib.sha256(card_blob).hexdigest() == result['prediction_card_sha256']
    # Exercise actual guards only; guard never loads D or computes action costs.
    from experiments.A00_engine.guard import guard
    main = guard('M01', allow_grid=True, purpose='A01')
    assert main['prediction_card_commit'] == result['prediction_card_commit']
    denied = []
    for cid, flags in [('M31', dict(allow_grid=True, purpose='A01')),
                       ('R03', dict(allow_grid=True, purpose='A01', allow_heldout=True)),
                       ('R03', dict(allow_grid=True, purpose='A05-T', allow_heldout=True))]:
        try:
            guard(cid, **flags)
        except PermissionError:
            denied.append(cid + ':' + flags['purpose'])
        else:
            raise AssertionError('expected guard to reject missing A05-F/non-calibration access')
    result.update(status='PASS', card_commit_changed_files=changed, guard_A01_card_requirement='PASS_READ_ONLY',
                  expected_denials=denied, grid_D_or_outcome_calls=0)
    write('registration_verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('prepare', 'registered'), required=True)
    args = parser.parse_args()
    prepare() if args.stage == 'prepare' else registered()
