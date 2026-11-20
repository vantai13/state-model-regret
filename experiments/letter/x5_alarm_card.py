"""Doan Van Tai — mechanical T1--T4 and tables for the immutable CARD_X5.

Pure scoring functions accept raw arrays; the commit/lock guards live in X5.
Importing this module never opens outcomes or calls an engine.
"""
import math

import numpy as np

from experiments.letter import x4b as B

SHORT_H = (300, 600, 900, 1200, 1800)
REGIMES = ('NEWB1', 'NEWB2', 'NEWB3')
STANDS, FALLS, NA = 'ĐỨNG', 'ĐỔ', 'NOT_EVALUABLE'


def pooled(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError('finite daily values required')
    return (float(values.mean()) if len(values) else None,
            float(values.std(ddof=1)/np.sqrt(len(values))) if len(values) > 1 else None)


def t1_reading(mean, se):
    if not math.isfinite(mean) or not math.isfinite(se) or se < 0:
        raise ValueError('finite daily mean and nonnegative SE required')
    if mean <= -.05 and mean+2*se < 0:
        return 'GAIN'
    if mean >= .05 and mean-2*se > 0:
        return 'LOSS'
    return 'UNRESOLVED'


def t1_result(cells):
    eligible = [r for r in cells if r['eligible']]
    counts = {label: sum(r['reading'] == label for r in eligible) for label in ('GAIN', 'LOSS', 'UNRESOLVED')}
    verdict = NA if len(eligible) < 3 or any(r['reading'] == NA for r in eligible) else (
        STANDS if counts['GAIN'] >= math.ceil(len(eligible)/2) and counts['LOSS'] == 0 else FALLS)
    return dict(verdict=verdict, eligible_cells=len(eligible), counts=counts,
        gain_required=math.ceil(len(eligible)/2), threshold_pp=.05, SE_unit='days, ddof=1',
        cells=cells, D_range_pp=[min((r['D_pp'] for r in eligible if r['D_pp'] is not None), default=None),
                                max((r['D_pp'] for r in eligible if r['D_pp'] is not None), default=None)])


def unique(rows, fields):
    keys = [tuple(r[f] for f in fields) for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError('duplicate scoring unit: '+repr(fields))


def strict_summary(rows):
    total = sum(r['regret_sum_Mbit_s'] for r in rows)
    strict = sum(r['strict_regret_sum_Mbit_s'] for r in rows)
    tie = sum(r['tie_regret_sum_Mbit_s'] for r in rows)
    return dict(cases=len(rows), instances=sum(r['instances'] for r in rows),
        regret_sum_Mbit_s=total, strict_regret_sum_Mbit_s=strict, tie_regret_sum_Mbit_s=tie,
        strict_regret_share=None if total == 0 else strict/total,
        signed_MC_estimates_preserved=True,
        scope='Evaluable regime/day,h; fresh M0 once, never duplicated by stale age.')


def evaluate(rows, paired_rows, tie_rows):
    """Daily statistics from B.descriptive_rows; no simulator or file access."""
    unique(rows, ('regime', 'date', 'rule', 'tau_s', 'h_s'))
    unique(paired_rows, ('regime', 'date', 'side', 'h_s'))
    unique(tie_rows, ('regime', 'date', 'side', 'h_s'))
    if any(r['regime'] not in REGIMES for r in paired_rows):
        raise ValueError('unexpected X5 regime')
    fresh = [r for r in paired_rows if r['side'] == 'fresh']
    cells = []
    for regime in REGIMES:
        for h in SHORT_H:
            daily = [r for r in fresh if (r['regime'], r['h_s']) == (regime, h)]
            num, den = sum(r['disagreement_numerator'] for r in daily), sum(r['instances'] for r in daily)
            eligible = len(daily) >= 5 and den > 0 and 20*num >= den
            values = [r['paired_Hybrid_minus_Stationary_pct'] for r in daily]
            mean, se = pooled(values) if values and all(v is not None for v in values) else (None, None)
            cells.append(dict(regime=regime, h_s=h, days=len(daily),
                disagreement_numerator=num, instances=den, disagreement_share=num/den if den else None,
                eligible=eligible, D_pp=mean, SE_over_days_pp=se,
                reading=NA if not eligible or mean is None or se is None else t1_reading(mean, se),
                evaluable_days_descriptive=sum(r['evaluable'] for r in daily)))
    long = [r for r in fresh if r['h_s'] == 7200]
    den = sum(r['instances'] for r in long)
    same = den-sum(r['disagreement_numerator'] for r in long)
    t2 = dict(verdict=NA if not den else (STANDS if 20*same >= 19*den else FALLS),
        coincident=same, instances=den, share=same/den if den else None, threshold=.95)
    tie_num = sum(r['tie_instances'] for r in tie_rows)
    tie_den = sum(r['instances'] for r in tie_rows)
    m0 = [r for r in rows if r['rule'] == 'M0' and r['h_s'] == 7200 and r['tau_s'] == 300]
    m0_regimes = []
    for regime in REGIMES:
        daily = [r for r in m0 if r['regime'] == regime]
        values = [r['regret_fresh_pct'] for r in daily]
        mean = float(np.mean(values)) if values and all(v is not None for v in values) else None
        m0_regimes.append(dict(regime=regime, days=len(daily), mean_fresh_regret_pct=mean,
            exceeds_half_percent=mean is not None and mean > .5))
    over = sum(r['exceeds_half_percent'] for r in m0_regimes)
    t3 = dict(verdict=NA if not tie_den or any(r['mean_fresh_regret_pct'] is None for r in m0_regimes) else (
        STANDS if 10*tie_num <= tie_den and over >= 2 else FALLS),
        tie_numerator=tie_num, tie_denominator=tie_den, tie_share=tie_num/tie_den if tie_den else None,
        tie_threshold=.10, regimes_over_half_percent=over, minimum_regimes=2, regimes=m0_regimes,
        tie_scope='All seven holds, fresh once per instance,h; no evaluability filter.',
        regret_aggregation='Equal weight per daily percentage within regime; no evaluability filter.')
    groups = {}
    for r in rows:
        if r['rule'] == 'Hybrid' and r['h_s'] == 7200 and r['evaluable']:
            groups.setdefault((r['regime'], r['date']), []).append(r)
    cases = []
    for (regime, date), daily in sorted(groups.items()):
        if {r['tau_s'] for r in daily} != {300, 900}:
            raise ValueError('T4 requires both stale ages per record')
        vals = [r['both_side_regret_pct'] for r in daily]
        if any(v is None for v in vals):
            raise ValueError('evaluable T4 record requires positive C_ref')
        worst = max(vals)
        cases.append(dict(regime=regime, date=date, max_all_sides_regret_pct=worst, meets=worst <= .5))
    ok, count = sum(r['meets'] for r in cases), len(cases)
    t4 = dict(verdict=NA if not count else (STANDS if 5*ok >= 4*count else FALLS),
        meets=ok, evaluable_records=count, share=ok/count if count else None,
        threshold=.80, regret_limit_pct=.5, rows=cases,
        unit='regime/day, all three side mean regrets <=0.5%, X4b evaluability gate at 7200s')
    gs_groups = {}
    for r in rows:
        if r['rule'] in ('M0', 'Hybrid') and r['evaluable']:
            gs_groups.setdefault((r['regime'], r['rule'], r['tau_s'], r['h_s']), []).append(r)
    gs = []
    for key, daily in sorted(gs_groups.items()):
        mean, se = pooled([r['G_S_Mbit_s'] for r in daily])
        gs.append(dict(regime=key[0], rule=key[1], tau_s=key[2], h_s=key[3], days=len(daily),
            mean_G_S_Mbit_s=mean, SE_over_days_Mbit_s=se,
            mean_daily_G_S_pct=float(np.mean([r['G_S_pct'] for r in daily]))))
    d3600 = []
    for regime in REGIMES:
        daily = [r for r in fresh if r['regime'] == regime and r['h_s'] == 3600]
        values = [r['paired_Hybrid_minus_Stationary_pct'] for r in daily]
        mean, se = pooled(values) if values and all(v is not None for v in values) else (None, None)
        d3600.append(dict(regime=regime, days=len(daily), D_pp=mean, SE_over_days_pp=se))
    strict = [r for r in tie_rows if r['evaluable']]
    return dict(owner='Doan Van Tai', T1=t1_result(cells), T2=t2, T3=t3, T4=t4,
        descriptive=dict(G_S=gs, strict_fresh_M0=strict_summary(strict),
            strict_fresh_M0_by_h={str(int(h)): strict_summary([r for r in strict if r['h_s'] == h]) for h in B.H_SECONDS},
            D_at_3600s=d3600),
        counts_are_not_independent_trials=True, G_S_sign='L_stale-L_fresh; negative=fresh hurts',
        hypotheses_unchanged=True)


def evaluate_raw(records):
    """Input: iterable of (raw NPZ arrays, per-record metadata), non-RARE only."""
    rows, pairs, ties, alarms, seen = [], [], [], [], set()
    for raw, meta in records:
        key = meta['regime'], meta['date']
        if key in seen:
            raise ValueError('duplicate raw record')
        seen.add(key)
        if not np.array_equal(raw['h_seconds'], B.H_SECONDS) or not np.array_equal(raw['tau_seconds'], B.S.TAU_SECONDS):
            raise ValueError('X5 full horizon/age grid required')
        if tuple(raw['pipelines']) != B.PIPES or tuple(raw['sides']) != B.SIDES:
            raise ValueError('X5 rule/side axes required')
        if len(raw['decisions']) < 8:
            raise ValueError('ALARM_RARE must not enter card scoring')
        r, p, t = B.descriptive_rows(raw, meta)
        rows.extend(r); pairs.extend(p); ties.extend(t)
        alarms.append(dict(regime=key[0], date=key[1], alarms=meta['alarms'],
            candidates=meta['candidates'], selected=len(raw['decisions'])))
    result = evaluate(rows, pairs, ties)
    result['descriptive']['truth_alarm_records'] = alarms
    result['records'] = len(seen)
    return result


def report(result):
    """Numerical tables only; no scientific interpretation or paper edits."""
    def fmt(value):
        if value is None:
            return 'NA'
        return f'{value:.9g}' if isinstance(value, float) else str(value)
    lines = ['# X5', '', 'Người phụ trách: Doan Van Tai.', '',
        '| Test | Verdict | Numerator | Denominator | Share |', '|---|---|---:|---:|---:|']
    for name, num, den, share in (
        ('T1', result['T1']['counts']['GAIN'], result['T1']['eligible_cells'], None),
        ('T2', result['T2']['coincident'], result['T2']['instances'], result['T2']['share']),
        ('T3 tie', result['T3']['tie_numerator'], result['T3']['tie_denominator'], result['T3']['tie_share']),
        ('T4', result['T4']['meets'], result['T4']['evaluable_records'], result['T4']['share'])):
        verdict = result['T3' if name == 'T3 tie' else name]['verdict']
        lines.append(f'| {name} | {verdict} | {num} | {den} | {fmt(share)} |')
    def table(title, data, keys):
        lines.extend(['', title, '', '| '+' | '.join(keys)+' |', '| '+' | '.join('---' for _ in keys)+' |'])
        for row in data:
            lines.append('| '+' | '.join(fmt(row[k]) for k in keys)+' |')
    table('T1; D, SE in percentage points of C_ref; SE over days, ddof=1', result['T1']['cells'],
        ('regime', 'h_s', 'days', 'disagreement_share', 'eligible', 'D_pp', 'SE_over_days_pp', 'reading'))
    table('T3; daily mean M0 fresh regret (% C_ref)', result['T3']['regimes'],
        ('regime', 'days', 'mean_fresh_regret_pct', 'exceeds_half_percent'))
    table('T4; one evaluable record, max(fresh, stale_300, stale_900)', result['T4']['rows'],
        ('regime', 'date', 'max_all_sides_regret_pct', 'meets'))
    table('G_S = L_stale-L_fresh; evaluable records', result['descriptive']['G_S'],
        ('regime', 'rule', 'tau_s', 'h_s', 'days', 'mean_G_S_Mbit_s', 'SE_over_days_Mbit_s', 'mean_daily_G_S_pct'))
    table('Strict contributions; signed sums in Mbit*s',
        [dict(h_s=h, **row) for h, row in result['descriptive']['strict_fresh_M0_by_h'].items()],
        ('h_s', 'cases', 'regret_sum_Mbit_s', 'strict_regret_sum_Mbit_s', 'tie_regret_sum_Mbit_s', 'strict_regret_share'))
    table('D at 3600s, percentage points of C_ref', result['descriptive']['D_at_3600s'],
        ('regime', 'days', 'D_pp', 'SE_over_days_pp'))
    table('Alarm counts in truth records', result['descriptive']['truth_alarm_records'],
        ('regime', 'date', 'alarms', 'candidates', 'selected'))
    if 'alarm_screen' in result:
        screen = result['alarm_screen']
        table('Step0; all 60 records including ALARM_RARE', [screen],
            ('records', 'alarms', 'candidates', 'alarm_rate', 'ALARM_RARE'))
    return '\n'.join(lines)+'\n'
