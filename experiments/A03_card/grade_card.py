"""Doan Van Tai — grade registered main-cell forecasts from supplied A04 output.

This command never constructs D or runs an engine. A03 must pass Git/hash checks
before the command reads any outcome file. L3.3 tests use only synthetic records.
"""
import argparse
import json
from pathlib import Path

from experiments.A03_card.grading import combine, grade_cell, carry_rule, STANDS, FAILS, UNKNOWN, EXCLUDED
from experiments.A03_card.provenance import ROOT, CARD, metadata, verify_receipt


def grade_main(spec, fine, coarse):
    def group(kind, ids, quantifier):
        rows = {}
        for cid in ids:
            rows[cid] = (grade_cell(kind, fine[cid], coarse.get(cid)) if cid in fine else
                         dict(verdict=UNKNOWN, reason='missing_cell', sensitive_to_dt=None))
        verdicts = [v['verdict'] for v in rows.values()]
        counts = {label: verdicts.count(label) for label in (STANDS, FAILS, UNKNOWN, EXCLUDED)}
        return dict(verdict=combine(verdicts, quantifier), counts=counts, cells=rows)
    p = spec['predictions']
    result = {name: group(name, p[name]['ids'], p[name]['quantifier']) for name in ('P2', 'P3', 'P6')}
    K, Q = group('P5_K', p['P5']['K_ids'], 'all'), group('P5_Q', p['P5']['Q_ids'], 'any')
    result['P5'] = dict(verdict=combine([K['verdict'], Q['verdict']]), K=K, Q=Q)
    for prediction in result.values():
        prediction['mechanism_verdict'] = 'NOT_PREREGISTERED: forecast without mechanism'
    # Only P5-rule was adopted. Other coordinate rules remain candidates.
    result['carry_to_A05_F'] = dict(rule='P5_rule', total_locked_rules=1,
                                  carry=carry_rule(result['P5']['verdict']),
                                  reason='carry every non-refuted rule, including unresolved')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='JSON with fine/coarse dictionaries keyed by cell ID')
    args = parser.parse_args()
    receipt = verify_receipt()
    spec = metadata((ROOT / CARD).read_text())
    data = json.loads(args.input.read_text())
    result = grade_main(spec, data['fine'], data['coarse'])
    print(json.dumps(dict(provenance=receipt, grades=result), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
