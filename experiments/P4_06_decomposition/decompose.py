"""Doan Van Tai — AI-assisted L4.6 analysis of saved discovery outputs.

Scientific purpose: separate GS|M1 and Gamma without changing the estimand.
Run from repo root: python -m experiments.P4_06_decomposition.decompose --out DIR
"""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

from experiments.P4_01_recount import recount_map as R
from experiments.P4_03_map_audit.common import cf_keys, canonical

ROOT = R.ROOT
METRICS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')
NONNEGATIVE = ('G_M', 'G_SM', 'G_S_M1', 'G_M_S1')
TOL_PP = 1e-9  # algebra only; never an approximation/convergence certificate
COLORS = dict(A='#0072B2', B='#E69F00', AB='#009E73', J='#CC79A7', C='#D55E00', D='#888888')


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def read_json(path):
    return json.loads((ROOT / path).read_text())


def from_losses(losses):
    """Compute all six contrasts by a separate path through exported costs."""
    a, b, c, d = (F(losses[k]) for k in ('00', '01', '10', '11'))
    return dict(G_S=a-c, G_M=a-b, G_SM=a-d, Gamma=c+b-a-d,
                G_S_M1=b-d, G_M_S1=c-d)


def check_identities(row):
    """Check independent fields; reconstructing GS|M1 alone is tautological."""
    z = {m: row[m + '_pctC'] for m in METRICS}
    errors = dict(state=abs(z['Gamma']-z['G_S_M1']+z['G_S']),
                  model=abs(z['Gamma']-z['G_M_S1']+z['G_M']),
                  joint=abs(z['G_SM']-z['G_S_M1']-z['G_M_S1']+z['Gamma']))
    if not all(math.isfinite(v) for v in z.values()) or max(errors.values()) > TOL_PP:
        raise ValueError(f'identity/unit mismatch: {row["id"]}: {errors}')
    return errors


def physical_key(a, b, k, eta, h, age=F(1)):
    return tuple(map(str, (F(a), F(b), 2*F(eta), F(k)/F(age), F(h)/F(age), F(0))))


def pilot_rows(sources):
    """Read only amp6 map1/2/3age; dedup physical coordinates retaining age."""
    raw = []
    for batch in ('map1', 'map2', 'map3age'):
        path = f'results/explore_v13/{batch}/regimes.csv'
        blob = R.git('show', f'{R.COMMIT}:{path}')
        sources[f'{R.COMMIT}:{path}'] = digest(blob)
        raw.extend(r for r in R.read_rows(blob.decode(), batch) if r['_key'][6] == 6)
    table, duplicates = R.dedup(raw)
    rows = []
    for r in table:
        a, b, k, e, h, age, amp = r['_key']
        row = dict(id=r['id'], engine='pilot', cohort='pilot', batch=r['batch'],
                   key='|'.join(physical_key(a, b, k, e, h, age)), age=float(age),
                   lambdaA=float(a), lambdaB=float(b), kappa_tau=float(k/age),
                   h_tau=float(h/age), delta=float(b-a), eta=float(e), Cref=r['Cbar'],
                   K=40, ref=1, dt='1/120', old_class=R.cls(r), label_origin='pilot',
                   native_class='', arithmetic_pass='', validity_errors='',
                   bundle_status='PILOT_NOT_NATIVE_AUDITED', native_ready='',
                   source=f'{R.COMMIT}:results/explore_v13/{r["batch"]}/regimes.csv',
                   source_sha256=sources[f'{R.COMMIT}:results/explore_v13/{r["batch"]}/regimes.csv'])
        row.update({m+'_pctC': r[m+'_pctC'] for m in METRICS})
        check_identities(row)
        rows.append(row)
    return rows, dict(raw=len(raw), unique=len(rows), exact_duplicates=len(duplicates),
                      dedup='unscaled lambdaA,lambdaB,kappa,eta,h,age,amp; keep age experiments distinct')


def native_row(raw, case, level, run_id, path, comparison, pilot_labels):
    if (raw.get('id') != case['id'] or raw.get('parameters') != case['parameters']
            or (raw.get('K'), raw.get('ref')) != level
            or raw.get('status') != 'COMPLETED' or raw.get('CF_computed') is not False):
        raise ValueError(f'wrong/incomplete native row: {path}')
    c = F(raw['Cref'])
    if c <= 0 or F(raw['losses']['11']) != c:
        raise ValueError('Cref must equal positive L11')
    z = {m+'_pctC': float(100*F(raw[m])/c) for m in METRICS}
    cost_values = from_losses(raw['losses'])
    cost_error = max(float(100*abs(cost_values[m]-F(raw[m]))/c) for m in METRICS)
    if cost_error > TOL_PP:
        raise ValueError(f'export disagrees with losses: {case["id"]}')
    a, b, k, e, h, _ = map(F, case['parameters'])
    key = '|'.join(canonical(case['parameters']))
    cls = R.cls(z)
    labels = sorted(pilot_labels.get(key, set()))
    # Old classes are used wherever an archived pilot key exists. Otherwise label
    # explicitly as the class of this saved native estimate, never an old label.
    old_class = labels[0] if len(labels) == 1 else cls
    row = dict(id=case['id'], engine='native', cohort=run_id, batch='', key=key,
               age=1.0, lambdaA=float(a), lambdaB=float(b), kappa_tau=float(k),
               eta=float(e), h_tau=float(h), delta=float(b-a), Cref=float(c),
               K=level[0], ref=level[1], dt=raw['dt'], old_class=old_class,
               label_origin='pilot' if len(labels) == 1 else 'native_estimate',
               native_class=cls, arithmetic_pass=raw['arithmetic_pass'],
               validity_errors='|'.join(raw['validity_errors']),
               bundle_status=comparison['status'],
               native_ready=not comparison['native_readiness_reasons'],
               source=str(path), source_sha256=digest((ROOT/path).read_bytes()),
               loss_export_max_error_pp=cost_error, **z)
    for m in METRICS:
        row[m+'_error_pp'] = float(100*F(raw['normalized_error'][m]))
    check_identities(row)
    return row


def load_all():
    sources = {}
    rows, pilot_counts = pilot_rows(sources)
    pilot_labels = defaultdict(set)
    # Full amp6 recount is used for labels only, including pilot stage1/2 aliases.
    from experiments.P4_02_reading.read_map import load_table
    for r in load_table():
        a, b, k, e, h, age, amp = r['_key']
        if amp == 6:
            pilot_labels['|'.join(physical_key(a, b, k, e, h, age))].add(r['class'])
    label_path = 'results/P4_01_recount/20261030_01/recounted_regimes.csv'
    sources[label_path] = digest((ROOT/label_path).read_bytes())
    park_path = 'results/lessons/l4_5_v2/parking.json'
    parking = read_json(park_path)
    sources[park_path] = digest((ROOT/park_path).read_bytes())
    counts = {}
    for name, level in (('L43_A1_SV', (640, 4)), ('L44_A3', (640, 4)), ('SUB_BOX', (640, 8))):
        prereg_path = f'experiments/P4_A1/runs/{name}/prereg.json'
        prereg = read_json(prereg_path)
        sources[prereg_path] = digest((ROOT/prereg_path).read_bytes())
        cases = prereg['cases']
        if name == 'SUB_BOX':
            kept = set(parking['preserved_complete_ids'])
            cases = [c for c in cases if c['id'] in kept]
            if len(cases) != parking['completed_keys']:
                raise ValueError('parked SUB subset mismatch')
        seen = set()
        for case in cases:
            key = canonical(case['parameters'])
            if key in seen:
                raise ValueError(f'duplicate within {name}: {key}')
            seen.add(key)
            folder = Path(prereg['output'])/'native'/case['id']
            path = folder/f'level_{level[0]}_{level[1]}.json'
            raw = read_json(path)
            if raw['a1_prereg_sha256'] != sources[prereg_path]:
                raise ValueError(f'wrong source prereg: {path}')
            comparison_path = folder/'comparison.json'
            comparison = read_json(comparison_path)
            row = native_row(raw, case, level, name, path, comparison, pilot_labels)
            row['comparison_sha256'] = digest((ROOT/comparison_path).read_bytes())
            row['cohort'] = ('SV+' if 'SV+' in case['supports'] else 'SV-') if name == 'L43_A1_SV' else (
                'MV' if 'MV+A' in case['supports'] else 'SH') if name == 'L44_A3' else 'SUB'
            rows.append(row)
        counts[name] = len(cases)
    forbidden = {'|'.join(k) for k in cf_keys()}
    if any(r['key'] in forbidden for r in rows):
        raise ValueError('CF collision in analysis inputs')
    return rows, dict(sources_sha256=sources, pilot_counts=pilot_counts, native_counts=counts,
                      CF_coordinate_keys_checked=len(forbidden), CF_collisions=0)


def quantiles(rows, field):
    values = [r[field] for r in rows]
    return {f'q{p}': R.q_linear(values, p/100) for p in (10, 50, 90)} if values else None


def distribution(rows):
    return dict(n=len(rows), **{m: quantiles(rows, m+'_pctC') for m in METRICS})


def summarize(rows):
    """Descriptive design quantiles, without sampling CI or prevalence claims."""
    by = defaultdict(list)
    for r in rows:
        by[r['cohort']].append(r)
    groups = {c: distribution(rs) for c, rs in by.items()}
    classes = {c: {label: distribution([r for r in rs if r['old_class'] == label])
                   for label in COLORS if any(r['old_class'] == label for r in rs)}
               for c, rs in by.items()}
    negatives = []
    for r in rows:
        for m in NONNEGATIVE:
            value = r[m+'_pctC']
            if value < -TOL_PP:
                error = r.get(m+'_error_pp')
                negatives.append(dict(id=r['id'], cohort=r['cohort'], metric=m, value_pp=value,
                                      reported_error_pp=error,
                                      exceeds_reported_error=None if error is None else -value > error,
                                      within_historical_point25pp_scale=-value <= .25,
                                      arithmetic_pass=r['arithmetic_pass'], source=r['source']))
    pilot = by['pilot']
    k_values = sorted({r['kappa_tau'] for r in pilot})
    k_summary = [dict(kappa_tau=k, **distribution([r for r in pilot if r['kappa_tau'] == k])) for k in k_values]
    delta = {sign: distribution([r for r in pilot if (r['delta'] < 0 if sign == 'negative' else
                                                    r['delta'] > 0 if sign == 'positive' else r['delta'] == 0)])
             for sign in ('negative', 'zero', 'positive')}
    # Positive Gamma <= GM|S1; negative magnitude <= GM. The max bound does
    # NOT imply that large |Gamma| requires large GM|S1 on the negative side.
    bound_violations = [r['id'] for r in rows if abs(r['Gamma_pctC']) >
                        max(r['G_M_pctC'], r['G_M_S1_pctC']) + TOL_PP]
    bad_native = [r for r in rows if r['engine'] == 'native' and not r['arithmetic_pass']]
    good_sv = [r for r in by['SV+'] if r['arithmetic_pass'] and r['native_ready']]
    peak = max(k_summary, key=lambda d:d['G_S_M1']['q50'])
    cp = classes['pilot']
    p1 = (cp['A']['G_S_M1']['q50'] > max(cp['AB']['G_S_M1']['q50'], cp['C']['G_S_M1']['q50'])
          and cp['AB']['Gamma']['q50'] < 0 < cp['C']['Gamma']['q50'])
    difference = groups['SV+']['G_S_M1']['q50']-groups['SV+']['G_S']['q50']
    return dict(status='DESCRIPTIVE_WITH_NUMERICAL_FLAGS' if negatives else 'DESCRIPTIVE',
                groups=groups, by_old_class=classes, pilot_by_kappa_tau=k_summary,
                pilot_by_delta_sign=delta, numerical_negatives=negatives,
                raw_native_arithmetic_false=[f'{r["cohort"]}/{r["id"]}' for r in bad_native],
                max_bound_violation_ids=bound_violations,
                max_identity_error_pp=max(max(check_identities(r).values()) for r in rows),
                SV_plus_sensitivity_no_raw_flags_native_ready=distribution(good_sv),
                SV_plus_difference_of_medians_pp=difference,
                forecasts=dict(P1=p1, P2=.1 <= peak['kappa_tau'] <= .3,
                               P3=delta['negative']['Gamma']['q50'] > delta['positive']['Gamma']['q50'],
                               P4=abs(difference) <= .25),
                pilot_peak_marginal_median=peak,
                native_rows=sum(r['engine']=='native' for r in rows),
                native_distinct_keys=len({r['key'] for r in rows if r['engine']=='native'}),
                new_physical_evaluations=0, new_CF_outcomes=0, new_sealed_outcomes=0,
                seed=None, uncertainty='design quantiles only; no sampling CI or certified numerical interval')


def d22_counterexample():
    """Exact stationary joint toy: X=(constant Q,mode), old Y informs mode.

    Costs given X are Markov. Stationarity of the current marginal does not
    erase information in Y conditional only on Q. This is not a native probe.
    """
    atoms = [(0, 0, F(9,20)), (0, 1, F(1,20)), (1, 0, F(1,20)), (1, 1, F(9,20))]
    true, model = (F(-1), F(1)), (F(-2), F(1))
    def loss(group):
        sums = defaultdict(lambda: [F(0), F(0)])
        for y, m, p in atoms:
            key = group(y, m)
            sums[key][0] += p*model[m]
            sums[key][1] += p*true[m]
        return F(10)+sum(d for h, d in sums.values() if h < 0)
    l00 = loss(lambda y,m:y)
    l10 = loss(lambda y,m:m)
    correct = loss(lambda y,m:(y,0))
    q_only = loss(lambda y,m:0)
    return dict(status='EXACT_SEMANTIC_COUNTEREXAMPLE', L00=str(l00), L10=str(l10),
                correct_Lcb0=str(correct), wrong_Q_only_Lcb0=str(q_only),
                correct_F=str(l00-correct), correct_V=str(correct-l10),
                wrong_F=str(l00-q_only), wrong_V=str(q_only-l10),
                both_telescoping=True, Q_only_one_hot_recovers_L10=loss(lambda y,m:(0,m))==l10,
                native_D22='DEFERRED_MISSING_Y_Q_MODE_JOINT', native_F=None, native_V=None,
                native_probe_calls=0, units='toy cost; not packet·s measurements')


def figures(rows, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm, Normalize
    from matplotlib.lines import Line2D
    plt.rcParams.update({'font.size': 10, 'savefig.dpi': 160})
    panels = [('Pilot map1/2/3age (amp6)', [r for r in rows if r['engine']=='pilot']),
              ('SV native 640/4', [r for r in rows if r['cohort'] in ('SV+','SV-')]),
              ('MV/SH 640/4 + SUB 640/8', [r for r in rows if r['cohort'] in ('MV','SH','SUB')])]
    for number in (1, 2, 3):
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), layout='constrained')
        hnorm = LogNorm(min(r['h_tau'] for r in rows), max(r['h_tau'] for r in rows))
        mnorm = Normalize(min(r['G_M_S1_pctC'] for r in rows), max(r['G_M_S1_pctC'] for r in rows))
        for ax, (title, rs) in zip(axes, panels):
            if number == 1:
                for label in COLORS:
                    subset = [r for r in rs if r['old_class']==label]
                    ax.scatter([r['G_S_M1_pctC'] for r in subset], [r['Gamma_pctC'] for r in subset],
                               c=COLORS[label], s=16, alpha=.6, label=label)
                ax.axvline(1, c='black', ls=':', lw=.8)
                ax.axhline(0, c='black', lw=.7)
                ax.set(xlabel='GS|M1 (% Cref)', ylabel='Gamma (% Cref)')
            elif number == 2:
                sc = ax.scatter([r['kappa_tau'] for r in rs], [r['G_S_M1_pctC'] for r in rs],
                                c=[r['h_tau'] for r in rs], norm=hnorm, cmap='viridis', s=17, alpha=.65)
                ax.axhline(1, c='black', ls=':', lw=.8)
                ax.set(xscale='log', xlabel='kappa / tau', ylabel='GS|M1 (% Cref)')
            else:
                sc = ax.scatter([r['delta'] for r in rs], [r['Gamma_pctC'] for r in rs],
                                c=[r['G_M_S1_pctC'] for r in rs], norm=mnorm, cmap='plasma', s=17, alpha=.65)
                ax.axhline(0, c='black', lw=.7)
                ax.set(xlabel='delta = lambdaB - lambdaA (packet/s)', ylabel='Gamma (% Cref)')
            flagged = [r for r in rs if r['arithmetic_pass'] is False]
            if flagged:
                x = 'G_S_M1_pctC' if number == 1 else 'kappa_tau' if number == 2 else 'delta'
                y = 'G_S_M1_pctC' if number == 2 else 'Gamma_pctC'
                ax.scatter([r[x] for r in flagged], [r[y] for r in flagged], marker='x', c='red', s=34, linewidths=.8)
            ax.set_title(f'{title}\nn={len(rs)}; red x = raw arithmetic flag')
            ax.grid(alpha=.15)
        if number == 1:
            handles = [Line2D([],[],color=color,marker='o',ls='',label=label) for label,color in COLORS.items()]
            fig.legend(handles=handles, loc='outside lower center', ncol=6)
        else:
            fig.colorbar(sc, ax=axes, label='h / tau' if number == 2 else 'GM|S1 (% Cref)', shrink=.8)
        fig.suptitle(f'L4.6 P{number}: exposed discovery; classes from pilot when available; no prevalence inference')
        for ext in ('png', 'pdf'):
            fig.savefig(out/f'P{number}.{ext}')
        plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        raise FileExistsError('use a new output directory; historical outputs are preserved')
    # Existing verifiers protect saved source/history; they do not run the plant.
    from experiments.P4_A1.config import verify_run
    for name in ('L43_A1_SV', 'L44_A3', 'SUB_BOX'):
        verify_run(name)
    rows, provenance = load_all()
    summary = summarize(rows)
    summary['D22'] = d22_counterexample()
    args.out.mkdir(parents=True)
    provenance['analysis_commit'] = R.git('rev-parse', 'HEAD').decode().strip()
    fields = sorted({k for r in rows for k in r})
    with (args.out/'rows.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    for name, doc in (('summary.json', summary), ('provenance.json', provenance)):
        (args.out/name).write_text(json.dumps(doc, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    figures(rows, args.out)
    print(json.dumps(dict(status=summary['status'], groups={k:v['n'] for k,v in summary['groups'].items()},
                          forecasts=summary['forecasts'], negative_estimates=len(summary['numerical_negatives']),
                          raw_native_flags=len(summary['raw_native_arithmetic_false']),
                          physical_calls=0, output=str(args.out)), indent=2))


if __name__ == '__main__':
    main()
