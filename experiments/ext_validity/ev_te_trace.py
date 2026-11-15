"""Doan Van Tai — EV-TE Arm R, train-only OLS and descriptive TM replay.

The Arm R v2 brief authorizes train, run and descriptive summary locally.
Training never evaluates test actions. Arm S and historical Arm R stay separate.
Physical Arm R units: rates converted Mb/s -> Mb/min; cost Mb*minutes.
"""
import argparse
from datetime import datetime, timedelta
import json
import math
from pathlib import Path
import re
import time

import numpy as np

from experiments.ext_validity import ev_te as S

OUT = S.OUT / 'arm_r_v2'
BIN = 5.
AGES = (1, 2)
HORIZONS = (1, 2, 3, 6, 12)


class NodeOutageError(ValueError):
    """A node lacks source or destination entries; the whole bin is missing."""


def parse_tm(path, od_ids, *, counts=None):
    """Fill omitted ODs with zero only when every node has entries both ways.

    Presence of an explicit zero entry counts as coverage, not as an outage.
    Optional counters distinguish omissions in files from zeros actually used.
    """
    match = re.fullmatch(r'demandMatrix-abilene-zhang-5min-(\d{8}-\d{4})\.txt', Path(path).name)
    if not match:
        raise ValueError('malformed TM timestamp')
    timestamp = datetime.strptime(match[1], '%Y%m%d-%H%M')
    if timestamp.minute % 5:
        raise ValueError('TM timestamp is off the 5-minute grid')
    ss = S.sections(Path(path).read_text())
    expected = set(od_ids)
    nodes = {node for name in od_ids for node in name.split('_')}
    values, sources, targets = {}, set(), set()
    for line in ss['DEMANDS']:
        m = re.fullmatch(r'(\S+)\s*\(\s*(\S+)\s+(\S+)\s*\)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if not m:
            raise ValueError('malformed TM demand')
        name, source, target, unit, value, _ = m.groups()
        value = float(value)
        if name not in expected or name in values or name != source+'_'+target or float(unit) != 1 or not math.isfinite(value) or value < 0:
            raise ValueError('invalid or duplicate TM OD')
        values[name] = value
        sources.add(source)
        targets.add(target)
    absent = len(expected)-len(values)
    if counts is not None:
        counts['absent_od_entries_in_files'] += absent
    missing_sources, missing_targets = sorted(nodes-sources), sorted(nodes-targets)
    if missing_sources or missing_targets:
        raise NodeOutageError(f'node outage: no source entries {missing_sources}; no destination entries {missing_targets}')
    if counts is not None:
        counts['absent_od_entries_filled_with_zero'] += absent
    return timestamp, np.array([values.get(name, 0.) for name in od_ids])


def load_trace():
    net = S.parse_native(S.data_root() / 'sndlib-networks-native/abilene.txt')
    ids = [d['id'] for d in net['demands']]
    rows, malformed, all_stamps, outages = {}, [], [], []
    counts = dict(absent_od_entries_in_files=0, absent_od_entries_filled_with_zero=0)
    files = S.tm_files()
    for path in files:
        try:
            stamp = datetime.strptime(path.stem.rsplit('5min-', 1)[1], '%Y%m%d-%H%M')
            all_stamps.append(stamp)
            stamp, row = parse_tm(path, ids, counts=counts)
            if stamp in rows:
                raise ValueError('duplicate TM timestamp')
            rows[stamp] = row
        except NodeOutageError as error:
            outages.append(dict(file=path.name, reason=str(error)))
        except (ValueError, OSError) as error:
            malformed.append(dict(file=path.name, reason=str(error)))
    if not rows:
        raise ValueError('no valid TMs')
    first, last = min(all_stamps), max(all_stamps)
    count = int((last-first).total_seconds()/300)+1
    times = [first+timedelta(minutes=5*i) for i in range(count)]
    values = np.full((count, len(ids)), np.nan)
    valid = np.zeros(count, dtype=bool)
    for i, stamp in enumerate(times):
        if stamp in rows:
            values[i], valid[i] = rows[stamp], True
    # First two calendar months, not a fixed number of days.
    end_month = first.year*12+first.month-1+2
    split = datetime(end_month//12, end_month%12+1, 1)
    train = np.array([stamp < split for stamp in times])
    return net, times, values, valid, train, dict(
        **counts, file_count=len(files), valid_file_count=len(rows), valid_bins=int(valid.sum()),
        node_outage_bins=len(outages), node_outage_files=outages,
        malformed_count=len(malformed), malformed_files=malformed,
        missing_file_count=count-len(set(all_stamps)), absent_file_bins=count-len(set(all_stamps)),
        missing_or_malformed_bins=int((~valid).sum()),
        first=first.isoformat(), last=last.isoformat(), train_end_exclusive=split.isoformat(),
        train_bins=int(train.sum()), train_valid_bins=int((train & valid).sum()),
        test_bins=int((~train).sum()), test_valid_bins=int((~train & valid).sum()))


def longest_valid(valid):
    padded = np.r_[False, valid, False].astype(int)
    starts, ends = np.flatnonzero(np.diff(padded) == 1), np.flatnonzero(np.diff(padded) == -1)
    if not len(starts):
        raise ValueError('no valid contiguous segment')
    j = int(np.argmax(ends-starts))
    return slice(int(starts[j]), int(ends[j]))


def route_arrays(prepared, managed):
    # Reuse exactly the Arm S routing and action bit convention, without its
    # synthetic high-mode reduction. TM rates have their own observed support.
    spec = dict(network=prepared, managed=managed, beta=0., slow=0)
    m = S.make_model(spec, reduced=False)
    mean = np.array([d['value'] for d in prepared['demands']]) * prepared['alpha']
    incidence = np.zeros_like(m.weights)
    np.divide(m.weights, mean, out=incidence, where=mean != 0)
    # Zero-mean ODs cannot be silently dropped if their test rate is nonzero.
    if np.any(mean == 0):
        links = {(e['source'], e['target']): i for i, e in enumerate(prepared['links'])}
        for j in np.flatnonzero(mean == 0):
            d = prepared['demands'][j]
            for a in range(len(incidence)):
                bit = managed.index(d['id']) if d['id'] in managed else None
                route = d['switch'] if bit is not None and (a >> bit) & 1 else d['stay']
                for u, v in zip(route[:-1], route[1:]):
                    incidence[a, links[u, v], j] = 1
    return incidence, m.capacity


def replay_stay(rates, incidence, cap, valid):
    """End-of-bin queue. Gaps reset an unknowable queue to zero, recorded.

    Evaluation subsequently requires an uninterrupted stale/forward window;
    a reset is a descriptive initialization limitation, not an imputation.
    """
    queues = np.full((len(rates), len(cap)), np.nan)
    q = np.zeros(len(cap))
    for i in range(len(rates)):
        if not valid[i]:
            q[:] = 0
            continue
        q, _ = S.fluid_step(q, incidence @ rates[i], cap, BIN)
        queues[i] = q
    return queues


def backlog_stats(rates, queues, incidence, cap, valid, mask):
    """Stay backlog occupancy within valid bins, with the replay's gap resets.

    Each bin has constant load. If any link grows, total backlog is positive
    for the entire bin except possibly its initial instant. Otherwise the last
    initially nonempty link determines the time until total backlog vanishes.
    """
    ix = np.flatnonzero(valid & mask)
    if not len(ix):
        return dict(valid_bins=0, observed_minutes=0., backlogged_minutes=0.,
                    fraction_time_backlogged=None, fraction_end_bins_backlogged=None)
    before = np.zeros_like(queues[ix])
    continuing = (ix > 0) & valid[np.maximum(ix-1, 0)]
    before[continuing] = queues[ix[continuing]-1]
    drift = rates[ix] @ incidence.T-cap
    drain = np.divide(before, -drift, out=np.zeros_like(before), where=drift < 0)
    drain[(before > 0) & (drift == 0)] = BIN
    duration = np.minimum(BIN, drain.max(axis=1, initial=0.))
    duration[np.any(drift > 0, axis=1)] = BIN
    return dict(valid_bins=len(ix), observed_minutes=len(ix)*BIN,
                backlogged_minutes=float(duration.sum()),
                fraction_time_backlogged=float(duration.mean()/BIN),
                fraction_end_bins_backlogged=float(np.any(queues[ix] > 0, axis=1).mean()))


def relaxation(rates, valid):
    pairs = valid[1:] & valid[:-1]
    old, fresh = rates[:-1][pairs], rates[1:][pairs]
    old, fresh = old-old.mean(axis=0), fresh-fresh.mean(axis=0)
    denom = np.sqrt((old*old).sum(axis=0)*(fresh*fresh).sum(axis=0))
    corr = np.divide((old*fresh).sum(axis=0), denom, out=np.zeros(len(denom)), where=denom > 0)
    tr = np.full(len(corr), BIN)
    positive = (corr > 0) & (corr < 1)
    tr[positive] = -BIN / np.log(corr[positive])
    tr[corr >= 1] = 1440.
    return np.clip(tr, BIN, 1440.), corr


def ols3(x1, x2, y):
    """Column-wise OLS using train data only; standardize to handle Mb scales."""
    coefficients = []
    for j in range(x1.shape[1]):
        x = np.column_stack([np.ones(len(x1)), x1[:, j], x2[:, j]])
        scale = np.r_[1., np.maximum(np.std(x[:, 1:], axis=0), 1e-12)]
        coefficients.append(np.linalg.lstsq(x/scale, y[:, j], rcond=None)[0]/scale)
    return np.array(coefficients)


def train(out=OUT):
    S.new(out / 'train.json')
    start = time.process_time()
    net, times, rates, valid, train_mask, parsing = load_trace()
    means = rates[valid & train_mask].mean(axis=0)
    ids = [d['id'] for d in net['demands']]
    tr, corr = relaxation(rates[train_mask], valid[train_mask])
    regimes = []
    for rho in (.8, .9):
        prepared = S.prepare_network(net, rho, dict(zip(ids, means)))
        scaled = rates * prepared['alpha'] * 60  # Mb/s -> Mb/min
        mean_scaled = means * prepared['alpha'] * 60
        for set_i in (1, 4):
            managed = prepared['managed_sets'][set_i-1]
            incidence, cap = route_arrays(prepared, managed)
            cap = cap*60
            maxima = np.max([np.nanmax(scaled @ route.T, axis=0) for route in incidence], axis=0)
            active = maxima > cap
            relevant = np.any(incidence[:, active] != 0, axis=(0, 1))
            inc, cp, rr = incidence[:, active][:, :, relevant], cap[active], scaled[:, relevant]
            q = replay_stay(rr[train_mask], inc[0], cp, valid[train_mask])
            segment = longest_valid(valid[train_mask])
            ti, censored, error = S.estimate_tint(q[segment].sum(axis=1), BIN)
            fits = {}
            for age in AGES:
                ix = np.arange(age+1, int(train_mask.sum()))
                ok = np.array([valid[i-age-1:i+1].all() for i in ix])
                ix = ix[ok]
                coeff_rate = ols3(rr[ix-age], rr[ix-age-1], rr[ix])
                loads = rr[ix-age] @ inc[0].T
                coeff_q = ols3(q[ix-age], loads, q[ix])
                fits[str(age)] = dict(rate=coeff_rate.tolist(), backlog=coeff_q.tolist(), n_train=len(ix))
            regimes.append(dict(id=f'R{set_i}_r{round(100*rho)}', rho=rho, managed=managed,
                alpha=prepared['alpha'], bottleneck=prepared['bottleneck'],
                network=prepared, active_indices=np.flatnonzero(active).tolist(),
                relevant_indices=np.flatnonzero(relevant).tolist(),
                active_links=[prepared['links'][i]['id'] for i in np.flatnonzero(active)],
                T_int_minutes=ti, T_int_censored=censored, T_int_error=error,
                tint_segment_start=times[segment.start].isoformat(),
                tint_segment_bins=segment.stop-segment.start,
                mean_rates=mean_scaled[relevant].tolist(), relaxation_minutes=tr[relevant].tolist(),
                OLS=fits))
    result = dict(author='Doan Van Tai', parsing=parsing, regimes=regimes,
                  lag1_autocorrelation=corr.tolist(),
                  units=dict(rate='Mb/min (native Mb/s multiplied by 60)', backlog='Mb', cost='Mb*min'),
                  limitations=['Gaps reset backlog; unknown carry-in after missing data.',
                               'T_int uses the longest uninterrupted training segment; no gap interpolation.',
                               'Active support uses observed train-plus-test loads as required; OLS and means use train only.',
                               'Nonpositive lag-1 correlation gives minimum relaxation 5 min.'],
                  CPU=time.process_time()-start, test_costs_computed=False)
    S.write_json(out / 'train.json', result)
    print(json.dumps(dict(command='Arm R train', parsing={k: v for k, v in parsing.items() if k not in ('malformed_files', 'node_outage_files')},
                          regimes=[{k: r[k] for k in ('id', 'managed', 'T_int_minutes', 'T_int_censored')} for r in regimes],
                          CPU=result['CPU'])), flush=True)


def mean_costs(rates, queues, mean, tr, incidence, cap):
    """Relax observed rates at step starts; horizon and integration in minutes."""
    n, a = len(rates), len(incidence)
    q = np.repeat(queues[:, None, :], a, axis=1)
    costs, out = np.zeros((n, a)), np.empty((n, a, len(HORIZONS)))
    for t in range(max(HORIZONS)):
        rr = mean + (rates-mean)*np.exp(-t*BIN/tr)
        loads = np.einsum('nd,aed->nae', rr, incidence, optimize=True)
        q, cc = S.fluid_step(q, loads, cap, BIN)
        costs += cc.sum(axis=2)
        if t+1 in HORIZONS:
            out[:, :, HORIZONS.index(t+1)] = costs
    return out


def apply_ols(coef, x1, x2):
    coef = np.array(coef)
    return np.maximum(0., coef[:, 0] + x1*coef[:, 1] + x2*coef[:, 2])


def day_stats(values, days):
    unique = np.unique(days)
    means = np.array([values[days == d].mean() for d in unique])
    return dict(mean=float(values.mean()), se=float(means.std(ddof=1)/np.sqrt(len(means))) if len(means) > 1 else None,
                n_days=len(means), n_instances=len(values))


def run(out=OUT):
    training = S.read_json(out / 'train.json')
    targets = [out / 'raw' / f"{r['id']}.npz" for r in training['regimes']]
    S.new(*targets, out / 'run.json')
    _, times, rates, valid, train_mask, _ = load_trace()
    start, counts = time.process_time(), []
    for regime, path in zip(training['regimes'], targets):
        inc, cap = route_arrays(regime['network'], regime['managed'])
        active, relevant = regime['active_indices'], regime['relevant_indices']
        inc = inc[:, active][:, :, relevant]
        cp = cap[active]*60
        rr = rates[:, relevant] * regime['alpha']*60
        q = replay_stay(rr, inc[0], cp, valid)
        ix = np.array([i for i in range(3, len(rr)-max(HORIZONS))
                       if not train_mask[i] and valid[i-3:i+max(HORIZONS)+1].all()])
        costs = np.empty((len(ix), len(AGES), 4, len(HORIZONS)))
        stays = np.empty((len(ix), len(HORIZONS)))
        for left in range(0, len(ix), 512):
            at = ix[left:left+512]
            fresh = mean_costs(rr[at], q[at], np.array(regime['mean_rates']),
                               np.array(regime['relaxation_minutes']), inc, cp).argmin(axis=1)
            action_costs, cq = np.zeros((len(at), len(inc))), np.repeat(q[at, None], len(inc), axis=1)
            realized = np.empty((len(at), len(inc), len(HORIZONS)))
            for step in range(max(HORIZONS)):
                load = np.einsum('nd,aed->nae', rr[at+step+1], inc, optimize=True)
                cq, cc = S.fluid_step(cq, load, cp, BIN)
                action_costs += cc.sum(axis=2)
                if step+1 in HORIZONS:
                    realized[:, :, HORIZONS.index(step+1)] = action_costs
            stays[left:left+len(at)] = realized[:, 0]
            for t, age in enumerate(AGES):
                sm, sq = rr[at-age], q[at-age]
                fit = regime['OLS'][str(age)]
                now_r = apply_ols(fit['rate'], sm, rr[at-age-1])
                now_q = apply_ols(fit['backlog'], sq, sm @ inc[0].T)
                old = mean_costs(sm, sq, np.array(regime['mean_rates']), np.array(regime['relaxation_minutes']), inc, cp).argmin(axis=1)
                now = mean_costs(now_r, now_q, np.array(regime['mean_rates']), np.array(regime['relaxation_minutes']), inc, cp).argmin(axis=1)
                for p, choice in enumerate((old, fresh, now, fresh)):
                    costs[left:left+len(at), t, p] = realized[np.arange(len(at))[:, None], choice, np.arange(len(HORIZONS))]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            np.savez_compressed(f, V=costs, V_stay=stays,
                                days=np.array([times[i].strftime('%Y-%m-%d') for i in ix]),
                                timestamps=np.array([times[i].isoformat() for i in ix]),
                                pipelines=np.array(['P_old', 'P_new', 'N_old', 'N_new']))
        occupancy = {name: backlog_stats(rr, q, inc[0], cp, valid, mask) for name, mask in (
            ('train', train_mask), ('test', ~train_mask), ('evaluated_windows', np.isin(np.arange(len(rr)), ix)))}
        counts.append(dict(id=regime['id'], n_instances=len(ix), backlog_occupancy=occupancy))
    S.write_json(out / 'run.json', dict(regimes=counts, CPU=time.process_time()-start, descriptive=True))


def summary(out=OUT):
    S.new(out / 'summary.json', out / 'summary_cells.csv')
    training, rows = S.read_json(out / 'train.json'), []
    for r in training['regimes']:
        with np.load(out / 'raw' / f"{r['id']}.npz", allow_pickle=False) as raw:
            v, stay, days = raw['V'], raw['V_stay'], raw['days']
        for t, age in enumerate(AGES):
            for j, h in enumerate(HORIZONS):
                ref = stay[:, j].mean()
                for twin, old, fresh in (('P', 0, 1), ('N', 2, 3)):
                    paired = v[:, t, old, j]-v[:, t, fresh, j]
                    stats = day_stats(paired, days)
                    rows.append(dict(regime=r['id'], tau_minutes=age*BIN, h_minutes=h*BIN, twin=twin,
                        h_over_T_int=h*BIN/r['T_int_minutes'] if r['T_int_minutes'] else None,
                        E_stay=float(ref), GS=stats['mean'], GS_se=stats['se'],
                        z_percent_E_stay=100*stats['mean']/ref if ref > 0 else None,
                        se_percent_E_stay=100*stats['se']/ref if ref > 0 and stats['se'] is not None else None,
                        n_days=stats['n_days'], n_instances=stats['n_instances']))
    S.write_csv(out / 'summary_cells.csv', rows)
    S.write_json(out / 'summary.json', dict(descriptive=True, rows=rows, no_hypothesis_verdicts=True))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('train', 'run', 'summary'))
    args = p.parse_args(argv)
    {'train': train, 'run': run, 'summary': summary}[args.command]()


if __name__ == '__main__':
    main()
