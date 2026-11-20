"""Doan Van Tai — mechanical B1/B2/B3 readings from CARD_X4B.md.

No traffic, simulator, or outcome is accessed on import, lock, or verify.
B1 is exploratory; B3(b) is descriptive. G_S = L_stale - L_fresh.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/x4b'
LONG_H = (3600, 7200)
B1_SHARE = .01
B2_MARGIN_PP, B2_SHARE, B2_MIN = .05, .95, 20
B3_RESOLUTION_PCT, B3_ACCURACY, B3_MIN = .25, .80, 4


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def predicted_signs(path):
    with Path(path).open(newline='') as f:
        return {(r['regime'], r['rule'], int(r['tau_s']), int(r['h_s'])):
                int(r['predicted_G_S_sign']) for r in csv.DictReader(f)}


def pooled(values):
    n = len(values)
    mean = sum(values)/n
    se = math.sqrt(sum((v-mean)**2 for v in values)/(n-1)/n) if n > 1 else None
    return mean, se


def unique(rows, fields):
    seen = set()
    for row in rows:
        key = tuple(row[k] for k in fields)
        if key in seen:
            raise ValueError('duplicate scoring unit: '+repr(key))
        seen.add(key)


def b1_reading(mean, se):
    if not math.isfinite(mean) or not math.isfinite(se) or se < 0:
        raise ValueError('finite paired mean and nonnegative instance SE required')
    if mean < 0 and abs(mean) >= 2*se:
        return 'GAIN'
    if mean > 0 and mean >= 2*se:
        return 'LOSS'
    return 'UNRESOLVED'


def b2_result(cases):
    n = len(cases)
    ok = sum(c['not_worse'] for c in cases)
    share = ok/n if n else None
    return dict(verdict='NOT_EVALUABLE' if n < B2_MIN else
                ('STANDS' if share >= B2_SHARE else 'DOES_NOT_STAND'),
        cases=n, not_worse=ok, share=share, minimum_cases=B2_MIN,
        required_share=B2_SHARE, margin_percentage_points_C_ref=B2_MARGIN_PP, rows=cases,
        unit='record,tau,h; both-side=max(fresh regret,stale_tau regret), as X-GEANT')


def strict_summary(rows):
    total = sum(r['regret_sum_Mbit_s'] for r in rows)
    tie = sum(r['tie_regret_sum_Mbit_s'] for r in rows)
    strict = sum(r['strict_regret_sum_Mbit_s'] for r in rows)
    share = strict/total if total != 0 else None
    return dict(cases=len(rows), instances=sum(r['instances'] for r in rows),
        tie_instances=sum(r['tie_instances'] for r in rows),
        strict_instances=sum(r['strict_instances'] for r in rows),
        regret_sum_Mbit_s=total, tie_regret_sum_Mbit_s=tie, strict_regret_sum_Mbit_s=strict,
        strict_regret_share=share, strict_regret_pct=None if share is None else 100*share,
        sum_scope='Sum of instance regrets over evaluable record,h; fresh occurs once per h.',
        signed_MC_estimates_preserved=True)


def evaluate(rows, signs, paired_rows=(), tie_strict_rows=()):
    """Pure card arithmetic; tests pass only synthetic descriptive rows."""
    unique(rows, ('regime', 'date', 'rule', 'tau_s', 'h_s'))
    unique(paired_rows, ('regime', 'date', 'side', 'h_s'))
    unique(tie_strict_rows, ('regime', 'date', 'side', 'h_s'))
    # B1 has NO evaluability gate in the card. The 1% condition is local to
    # record,side,h, and SE is computed over paired instances in x4b.py.
    b1 = []
    for r in paired_rows:
        if r['h_s'] <= 1800 and r['instances'] > 0 and r['disagreement_numerator']/r['instances'] >= B1_SHARE:
            mean = r['paired_Hybrid_minus_Stationary_Mbit_s']
            se = r['paired_Hybrid_minus_Stationary_SE_Mbit_s']
            b1.append(dict(r, reading=b1_reading(mean, se)))
    # B2 uses the same max of the two mean regrets as x_geant.score.
    groups = {}
    for r in rows:
        if r['h_s'] <= 1800 and r['evaluable'] and r['rule'] in ('Hybrid', 'Stationary'):
            groups.setdefault((r['regime'], r['date'], r['tau_s'], r['h_s']), {})[r['rule']] = r
    b2 = []
    for key, values in sorted(groups.items()):
        if set(values) != {'Hybrid', 'Stationary'}:
            raise ValueError('missing Hybrid/Stationary pair for B2')
        h, s = values['Hybrid'], values['Stationary']
        if h['C_ref_Mbit_s'] != s['C_ref_Mbit_s'] or h['both_side_regret_pct'] is None or s['both_side_regret_pct'] is None:
            raise ValueError('B2 requires a common positive C_ref')
        hv, sv = h['both_side_regret_pct'], s['both_side_regret_pct']
        b2.append(dict(regime=key[0], date=key[1], tau_s=key[2], h_s=key[3],
            side=f'fresh+stale_{key[2]}', Hybrid_both_side_regret_pct=hv,
            Stationary_both_side_regret_pct=sv, difference_percentage_points=hv-sv,
            not_worse=hv <= sv+B2_MARGIN_PP))
    # B3(a): equally pool daily G_S means; the SE is over DAYS, not instances.
    cells = {}
    for r in rows:
        if r['rule'] == 'M0' and r['h_s'] in LONG_H and r['evaluable']:
            cells.setdefault((r['regime'], r['rule'], r['tau_s'], r['h_s']), []).append(r)
    b3a = []
    for key, rs in sorted(cells.items()):
        if key not in signs:
            raise ValueError('missing train prediction for B3(a): '+repr(key))
        pred = signs[key]
        mean, se = pooled([r['G_S_Mbit_s'] for r in rs])
        cref = sum(r['C_ref_Mbit_s'] for r in rs)/len(rs)
        # Match X-GEANT: zero train prediction is abstention, not a trial.
        resolved = pred != 0 and se is not None and abs(mean) >= 2*se and cref > 0 and abs(mean) >= B3_RESOLUTION_PCT/100*cref
        observed = 1 if mean > 0 else -1 if mean < 0 else 0
        b3a.append(dict(regime=key[0], rule='M0', tau_s=key[2], h_s=key[3],
            days=len(rs), mean_G_S_Mbit_s=mean, SE_over_days_Mbit_s=se,
            mean_C_ref_Mbit_s=cref, G_S_pct=None if cref <= 0 else 100*mean/cref,
            predicted=pred, observed=observed, abstention=pred == 0,
            resolved=resolved, correct=resolved and observed == pred))
    resolved = [r for r in b3a if r['resolved']]
    correct = sum(r['correct'] for r in resolved)
    accuracy = correct/len(resolved) if resolved else None
    # B3(b) has no sign/resolution gate: all evaluable long-h fresh regrets.
    b3b = [r for r in tie_strict_rows if r['side'] == 'fresh' and r['h_s'] in LONG_H and r['evaluable']]
    return dict(owner='Doan Van Tai', sign='G_S=L_stale-L_fresh; negative=fresh hurts',
        B1=dict(kind='EXPLORATORY_NOT_PASS_FAIL', cases=len(b1),
            counts={label: sum(r['reading'] == label for r in b1) for label in ('GAIN', 'LOSS', 'UNRESOLVED')},
            SE_unit='paired instances within record,side,h', rows=b1),
        B2=b2_result(b2),
        B3a=dict(verdict='NOT_EVALUABLE' if len(resolved) < B3_MIN else
                 ('STANDS' if accuracy >= B3_ACCURACY else 'DOES_NOT_STAND'),
            resolved=len(resolved), correct=correct, accuracy=accuracy,
            minimum_resolved=B3_MIN, accuracy_threshold=B3_ACCURACY,
            resolution_pct_C_ref=B3_RESOLUTION_PCT, SE_unit='days within regime,tau,h', cells=b3a),
        B3b=dict(kind='DESCRIPTIVE', **strict_summary(b3b),
            by_h={str(h): strict_summary([r for r in b3b if r['h_s'] == h]) for h in LONG_H},
            rows=b3b), counts_are_not_independent_trials=True)


def lock_files(out):
    out = Path(out)
    return dict(card=out / 'CARD_X4B.md', scorer=Path(__file__).resolve(), lock=out / 'lock.json')


def lock(out=OUT):
    from experiments.letter import x4b
    out = Path(out)
    x4b.verify_lock(out)
    x4b.T.new(out / 'truth')
    value = dict(owner='Doan Van Tai', schema='x4b-card-lock-v1',
                 sha256={k: sha(v) for k, v in lock_files(out).items()})
    x4b.C.write_json(out / 'lock_card.json', value)
    return value


def verify(out=OUT):
    out = Path(out)
    locked = json.loads((out / 'lock_card.json').read_text())
    current = {k: sha(v) for k, v in lock_files(out).items()}
    if locked.get('schema') != 'x4b-card-lock-v1' or locked['sha256'] != current:
        raise ValueError('X4b lock_card mismatch')
    return dict(verified=True, lock_card_sha256=sha(out / 'lock_card.json'))


def score(out=OUT):
    from experiments.letter import x4b
    out = Path(out)
    verify(out)
    token = x4b.verify_lock(out)
    data = json.loads((out / 'score.json').read_text())
    if data['lock_sha256'] != token.digest:
        raise ValueError('descriptive score belongs to another lock')
    result = evaluate(data['rows'], predicted_signs(out / 'predictions.csv'),
                      data['paired_rows'], data['tie_strict_rows'])
    result.update(descriptive_score_sha256=sha(out / 'score.json'), lock_sha256=token.digest)
    x4b.C.write_json(out / 'card_verdicts.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('lock', 'verify', 'score'))
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)
    result = dict(lock=lock, verify=verify, score=score)[args.command](args.out)
    if args.command == 'score':
        result = {k: result[k]['verdict'] if 'verdict' in result[k] else result[k]['kind']
                  for k in ('B1', 'B2', 'B3a', 'B3b')}
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
