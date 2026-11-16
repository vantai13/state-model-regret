"""Doan Van Tai — LETTER-W2 CLI (full computation is launched on GCP).

    python3 -m experiments.letter.w2_run run --workers 4 --limit 2 --families asym --out /tmp/w2_smoke
    python3 -m experiments.letter.w2_run run --workers 8 --families asym,zf_a3_asym,zf_a7p5_asym
    python3 -m experiments.letter.w2_run analyze
    python3 -m experiments.letter.w2_run figure_e1

W2 is exploratory. Resumption skips only validated COMPLETED JSONs; it never
replaces a file. Importing this module does not run or analyze anything.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import sys
import time

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np

from experiments.letter.shat import FAMILIES, ROOT, load_cases
from experiments.letter.w2_eval import LEVELS, THETAS, e1_regimes, run_regime, write_json_once

OUT = ROOT/'results/letter/w2'
SIDES = ('new', 'old')
IMPLEMENTATION_CONVENTIONS = [
    'theta chosen separately for true_s and mm1, equal weight to both telemetry sides, both ages and every asym horizon; exact objective ties choose smaller theta',
    'P14 reports fresh/stale separately and pooled; P15/P16 held only if both levels and both sides meet their respective fraction thresholds',
    'P15 compares each candidate side to fresh M0, literally following the card; P16 compares to the matching plain-hybrid side',
    'P20 uses every positive recoverable regret-gap row, separately by estimator and telemetry side; nonpositive gaps are listed, not divided by',
    'arrival variance uses ddof=0, covariance uses global mean and denominator n-k; final partial bin is recorded but excluded from equal-width-bin estimates',
    'design kappa supplies the 50*kappa_guess computational lag cap, not the estimate; no projection of invalid parameters and no fallback',
    'actual disagreement uses the joint old/current Markov law; same-index policy distance is retained separately',
    'E1 retains both actions and each path, plus joint states pairing matching Stay quantiles; true slope means its asymptotic limit',
]


def _load_completed(path, case):
    record = json.loads(Path(path).read_text())
    if (record.get('status') != 'COMPLETED' or record.get('id') != case['id']
            or record.get('family') != case['family'] or record.get('case') != case):
        raise ValueError('existing raw is not this completed case: '+str(path))
    if len(record.get('evaluations', [])) != 2:
        raise ValueError('completed raw lacks both ages: '+str(path))
    for ev, label in zip(record['evaluations'], ('seconds_1', 'Tint_1')):
        if ev['age_label'] != label or [r['h'] for r in ev['h']] != [str(F(h)) for h in case['hs']]:
            raise ValueError('completed raw has wrong age/grid: '+str(path))
    if not math.isfinite(record['cpu_seconds']) or record['cpu_seconds'] <= 0:
        raise ValueError('invalid CPU timing: '+str(path))
    return record


def run(args):
    families = args.families.split(',')
    if len(set(families)) != len(families) or set(families)-set(FAMILIES):
        raise ValueError('unknown or duplicate family')
    if args.workers < 1 or (args.limit is not None and args.limit < 1):
        raise ValueError('workers and limit must be positive')
    cases = [c for c in load_cases() if c['family'] in families]
    if args.limit is not None:
        cases = cases[:args.limit]
    selected_e1 = e1_regimes()
    pending, receipts = [], []
    for case in cases:
        path = args.out/(case['id']+'.json')
        if path.exists():
            data = _load_completed(path, case)
            receipts.append(dict(id=case['id'], cpu_seconds=data['cpu_seconds'], skipped=True))
        else:
            pending.append(case)
    print(json.dumps(dict(event='START', selected=len(cases), pending=len(pending),
                          skipped=len(receipts), workers=args.workers, e1_regimes=selected_e1)), flush=True)
    start = time.monotonic()
    if pending:
        with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
            jobs = {pool.submit(run_regime, c, args.out, selected_e1): c['id'] for c in pending}
            for future in as_completed(jobs):
                result = future.result()
                receipts.append(result)
                print(json.dumps(dict(event='DONE', **result)), flush=True)
    mean = float(np.mean([r['cpu_seconds'] for r in receipts]))
    result = dict(event='RUN_COMPLETE', regimes=len(receipts), skipped=sum(r.get('skipped', False) for r in receipts),
                  cpu_seconds=sum(r['cpu_seconds'] for r in receipts), mean_cpu_seconds=mean,
                  projection_93_cpu_seconds=93*mean, projection_93_cpu_hours=93*mean/3600,
                  projection_note='linear mean extrapolation only; two-regime smoke is not representative of stiffness/state-size tails',
                  invocation_wall_seconds=time.monotonic()-start)
    print(json.dumps(result), flush=True)
    return result


def choose_theta(raws):
    """Selection reads asym only; held-out values cannot influence theta."""
    training = [d for d in raws if d['family'] == 'asym']
    if not training:
        raise ValueError('asym training data required')
    scores, chosen = {}, {}
    for level in LEVELS:
        values = {f'{theta:g}': [] for theta in THETAS}
        for data in training:
            for ev in data['evaluations']:
                for row in ev['h']:
                    for theta in values:
                        values[theta].extend(row['onset'][level][theta]['regret_'+side] for side in SIDES)
        scores[level] = {theta: dict(mean_regret_pct_Cref=float(np.mean(v)), rows=len(v)) for theta, v in values.items()}
        chosen[level] = min(scores[level], key=lambda t: (scores[level][t]['mean_regret_pct_Cref'], float(t)))
    return chosen, scores


def _fraction(flags, required):
    n, ok = len(flags), sum(bool(v) for v in flags)
    return dict(held=bool(n and ok/n >= required), meets=ok, denominator=n,
                fraction=ok/n if n else None, required_fraction=required,
                status=('held' if ok/n >= required else 'not held') if n else 'NOT_EVALUABLE')


def _joint_verdict(clauses):
    eligible = bool(clauses) and all(c.get('status') != 'NOT_EVALUABLE' for c in clauses)
    held = eligible and all(c['held'] for c in clauses)
    return dict(held=held, status=('held' if held else 'not held') if eligible else 'NOT_EVALUABLE')


def analyze_data(raws):
    """Mechanical card scoring; no engine calls, fits, or held-out selection."""
    chosen, scores = choose_theta(raws)
    nonzero = [d for d in raws if d['s'] != 0]
    valid = [d for d in nonzero if d['estimator']['status'] == 'VALID']
    sign_clause = _fraction([d['estimator']['sign_correct'] is True for d in nonzero], .95)
    # Missing estimates cannot silently disappear from the P13 denominator.
    errors = sorted([d['estimator']['relative_error'] for d in valid]
                    +[math.inf]*(len(nonzero)-len(valid)))
    median_error = float(np.median(errors)) if errors else None
    relative_clause = dict(held=median_error is not None and median_error <= .25,
                           median_relative_error=median_error if median_error is not None and math.isfinite(median_error) else None,
                           invalid_count=len(nonzero)-len(valid), denominator=len(nonzero), threshold=.25,
                           status='NOT_EVALUABLE' if not errors else 'held' if median_error <= .25 else 'not held')
    predictions = {'P13': dict(**_joint_verdict([sign_clause, relative_clause]), sign=sign_clause,
                               relative_error=relative_clause, zero_s_regimes=len(raws)-len(nonzero))}
    p14, p15, p16, p20 = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    p20_nonpositive = defaultdict(int)
    p17, p18 = [], []
    p17_failures = []
    p17_skipped = []
    by_table = defaultdict(list)
    for data in raws:
        tint_rows = next(ev['h'] for ev in data['evaluations'] if ev['age_label'] == 'Tint_1')
        p18.append(any(r['h_Tint'] <= 4 and r['bound']['D'] < .01 for r in tint_rows))
        for row in tint_rows:
            test = row['bound']['P17_holds']
            if test is None:          # Claude 16/11: joint mass skipped (LETTER_W2_SKIP_JOINT); not evaluated, not a failure
                p17_skipped.append(data['id']); continue
            p17.append(test is True)
            if test is not True:
                p17_failures.append(dict(id=data['id'], h=row['h'], **row['bound']))
            if row['h_Tint'] >= 4:
                for side in SIDES:
                    v = row['hybrid']['mmpp']['regret_'+side]
                    p14[side].append(v is not None and v <= .1)
        for ev in data['evaluations']:
            for row in ev['h']:
                for level in LEVELS:
                    onset = row['onset'][level][chosen[level]]
                    for side in SIDES:
                        key = level+'_'+side
                        if data['family'] != 'asym':
                            if row['h_Tint'] < 1:
                                p15[key].append(onset['regret_'+side] <= row['M0']['regret_new']+.05)
                            if row['h_Tint'] >= 4:
                                p16[key].append(onset['regret_'+side] <= row['hybrid'][level]['regret_'+side]+.05)
                        if row['h_Tint'] >= 1:
                            gap = row['M0']['regret_'+side]-row['hybrid'][level]['regret_'+side]
                            recovery = row['M0']['regret_'+side]-row['tie_break'][level]['regret_'+side]
                            if gap > 0:
                                p20[key].append(recovery/gap)
                            else:
                                p20_nonpositive[key] += 1
                variants = dict(M0=row['M0'])
                variants.update({'hybrid_'+k: v for k, v in row['hybrid'].items()})
                variants.update({'onset_'+level: row['onset'][level][chosen[level]] for level in LEVELS})
                variants.update({'tie_'+level: row['tie_break'][level] for level in LEVELS})
                for name, value in variants.items():
                    for side in SIDES:
                        v = value['regret_'+side]
                        if v is not None:
                            by_table[data['family'], ev['age_label'], side, name].append((v, value['G_S']))
    p14_groups = {side: _fraction(p14[side], .95) for side in SIDES}
    predictions['P14'] = dict(**_joint_verdict(list(p14_groups.values())), by_side=p14_groups,
                              pooled=_fraction(p14['new']+p14['old'], .95), age='Tint_1', h_Tint_min=4)
    for label, source, threshold in (('P15', p15, .8), ('P16', p16, .9)):
        groups = {level+'_'+side: _fraction(source[level+'_'+side], threshold) for level in LEVELS for side in SIDES}
        predictions[label] = dict(**_joint_verdict(list(groups.values())), by_variant_and_side=groups,
                                  held_out_families=list(FAMILIES[1:]))
    predictions['P17'] = dict(**_fraction(p17, 1.), counterexamples=p17_failures, regimes_not_evaluated=sorted(set(p17_skipped)))
    predictions['P18'] = _fraction(p18, .8)
    figures = [d for d in raws if d.get('e1') is not None]
    p19_clauses = [dict(held=d['e1']['P19_flat'] and d['e1']['P19_slope_identity'], status='EVALUATED') for d in figures]
    predictions['P19'] = dict(**_joint_verdict(p19_clauses), regimes=len(figures),
                              checks=[dict(id=d['id'], flat=d['e1']['P19_flat'], slope_identity=d['e1']['P19_slope_identity']) for d in figures],
                              meaning='finite drain plateau; asymptotic true-value slope, not exact linearity at finite h')
    recovery_groups = {}
    for level in LEVELS:
        for side in SIDES:
            key = level+'_'+side
            values = p20[key]
            recovery_groups[key] = dict(**_fraction([v < .2 for v in values], 1.),
                                        median_recovered_fraction=float(np.median(values)) if values else None,
                                        max_recovered_fraction=max(values) if values else None,
                                        excluded_nonpositive_gaps=p20_nonpositive[key])
    predictions['P20'] = dict(**_joint_verdict(list(recovery_groups.values())), by_variant_and_side=recovery_groups)
    tables = [dict(family=family, age=age, side=side, variant=name,
                   available_rows=len(v), mean_regret_pct_Cref=float(np.mean([x[0] for x in v])),
                   mean_G_S_pct_Cref=float(np.mean([x[1] for x in v])))
              for (family, age, side, name), v in sorted(by_table.items())]
    return dict(owner='Doan Van Tai', wave='W2 exploratory', regimes=len(raws),
                families={f: sum(d['family'] == f for d in raws) for f in FAMILIES},
                selection=dict(training_family='asym', held_out_families=list(FAMILIES[1:]),
                               chosen_theta=chosen, training_scores=scores,
                               objective='mean regret across all training h, both ages, fresh and stale; per s-hat level'),
                conventions=IMPLEMENTATION_CONVENTIONS, predictions=predictions, tables=tables,
                estimator_invalid_ids=[d['id'] for d in raws if d['estimator']['status'] != 'VALID'],
                cpu_seconds=sum(d['cpu_seconds'] for d in raws),
                statistical_scope='finite design rows with shared regimes; fractions are not independent-trial confidence estimates')


def analyze(args):
    cases = load_cases()
    paths = [args.raw/(case['id']+'.json') for case in cases]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise ValueError(f'analysis requires all 93 completed regimes; missing {len(missing)}')
    raws = [_load_completed(path, case) for path, case in zip(paths, cases)]
    result = analyze_data(raws)
    result['raw_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if (args.out/'summary.json').exists() or (args.out/'README.md').exists():
        raise FileExistsError('analysis outputs already exist')
    lines = ['# LETTER-W2 — Doan Van Tai', '',
             'Exploratory CTMC, age-only information. Regret and G_S are % C_ref; fresh = new, stale = old.', '',
             'θ selection uses asym only; zf_a3_asym and zf_a7p5_asym are held out.', '',
             '| Prediction | Mechanical verdict |', '|---|---|']
    lines.extend(f'| {key} | {value["status"]} |' for key, value in result['predictions'].items())
    lines += ['', 'Chosen θ: '+json.dumps(result['selection']['chosen_theta'])+'.', '',
              'Full numerators, denominators, exceptions and every per-side verdict are in summary.json.', '',
              '| Family | Age | Side | Variant | Available rows | Mean regret (% C_ref) | Mean G_S (% C_ref) |',
              '|---|---|---|---|---:|---:|---:|']
    lines.extend(f'| {r["family"]} | {r["age"]} | {r["side"]} | {r["variant"]} | {r["available_rows"]} | {r["mean_regret_pct_Cref"]:.9g} | {r["mean_G_S_pct_Cref"]:.9g} |' for r in result['tables'])
    lines += ['', 'Implementation conventions / card ambiguities:', '']+['- '+s for s in IMPLEMENTATION_CONVENTIONS]
    lines += ['', 'Rows share regimes and are not independent trials. INVALID estimates stay visible in the prediction denominators.', '']
    write_json_once(args.out/'summary.json', result)
    with (args.out/'README.md').open('x') as stream:
        stream.write('\n'.join(lines))
    print(json.dumps(dict(chosen_theta=result['selection']['chosen_theta'], predictions={k: v['status'] for k, v in result['predictions'].items()})), flush=True)
    return result


def figure_e1(args):
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/letter_w2_mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for suffix in ('eps', 'pdf'):
        if (args.out/('fig_e1.'+suffix)).exists():
            raise FileExistsError('E1 output already exists')
    selected = e1_regimes()
    records = []
    for family in FAMILIES:
        raw = json.loads((args.raw/(selected[family]+'.json')).read_text())
        if raw.get('e1') is None or raw.get('status') != 'COMPLETED':
            raise ValueError('missing E1 data for '+family)
        records.append(raw)
    with plt.rc_context({'font.family': 'DejaVu Serif', 'font.size': 8,
                         'axes.labelsize': 8, 'axes.titlesize': 8, 'legend.fontsize': 6,
                         'xtick.labelsize': 7, 'ytick.labelsize': 7, 'pdf.fonttype': 42,
                         'ps.fonttype': 42}):
        fig, axes = plt.subplots(3, 1, figsize=(3.5, 5.4), sharex=True)
        colors = ('#0072B2', '#D55E00', '#009E73')
        for ax, raw in zip(axes, records):
            e1 = raw['e1']
            for action, width, marker in (('stay', .8, None), ('switch', 1.2, 'o')):
                values = e1['actions'][action]
                for i, color in enumerate(colors):
                    label = e1['state_labels'][i] if action == 'stay' else None
                    ax.plot(e1['h_Tint'], values['V'][i], color=color, lw=width,
                            marker=marker, markersize=2, markevery=12, label=label)
                    ax.plot(e1['h_Tint'], values['V_hat'][i], color=color, lw=width, ls='--')
            ax.set_xscale('log')
            ax.set_ylabel('Cost (packet s)')
            ax.set_title(raw['family']+f'; s = {raw["s"]:.3g}')
            ax.grid(True, lw=.3, color='.85')
        axes[0].legend(loc='upper left', frameon=False)
        axes[-1].set_xlabel(r'$h/T_{\rm int}$')
        fig.text(.5, .005, 'Solid: true V; dashed: mean rollout. Circles: Switch; thin: Stay.', ha='center', fontsize=6)
        fig.tight_layout(rect=(0, .02, 1, 1), pad=.6)
        args.out.mkdir(parents=True, exist_ok=True)
        for suffix in ('eps', 'pdf'):
            fig.savefig(args.out/('fig_e1.'+suffix), format=suffix)
        plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    run_parser = sub.add_parser('run')
    run_parser.add_argument('--workers', type=int, default=4)
    run_parser.add_argument('--families', default=','.join(FAMILIES))
    run_parser.add_argument('--out', type=Path, default=OUT/'raw')
    run_parser.add_argument('--limit', type=int)
    for command in ('analyze', 'figure_e1'):
        child = sub.add_parser(command)
        child.add_argument('--raw', type=Path, default=OUT/'raw')
        child.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)
    return {'run': run, 'analyze': analyze, 'figure_e1': figure_e1}[args.command](args)


if __name__ == '__main__':
    main()
