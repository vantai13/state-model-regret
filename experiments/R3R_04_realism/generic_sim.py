"""Doan Van Tai — event-driven formula check, independent of queue/decision engine."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from experiments.R3R_04_realism.implied import fluid_queue, delay_exceedance, window_cv


def positive_area(q, slope, dt):
    stop = dt if slope >= 0 else min(dt, q / -slope)
    return q * stop + .5 * slope * stop * stop


def above_time(q, slope, dt, threshold):
    if slope > 0: return max(0., dt - max(0., (threshold - q) / slope))
    if slope < 0: return max(0., min(dt, (q - threshold) / -slope))
    return dt if q > threshold else 0.


def simulate(case, spec, seed):
    rng = np.random.default_rng(seed)
    lam, a, c, T = (case[k] for k in ('lambda', 'amplitude', 'capacity', 'T_s'))
    burn, duration = spec['burn_s'], spec['measure_s']
    end = burn + duration
    events = [0.]
    while events[-1] < end:
        draws = rng.exponential(T, max(1024, int((end - events[-1]) / T * 1.05)))
        times = events[-1] + np.cumsum(draws)
        events.extend(times[times < end].tolist())
        if times[-1] >= end: break
    starts = np.asarray(events)
    stops = np.r_[starts[1:], end]
    initial_mode = rng.integers(2)
    rates = lam + a * (2 * ((np.arange(len(starts)) + initial_mode) % 2) - 1)
    q = area = busy = tail = 0.
    for lo, hi, rate in zip(starts, stops, rates):
        dt, slope = hi - lo, rate - c
        if hi > burn:
            cut = max(0., burn - lo)
            qobs, obsdt = max(0., q + slope * cut), dt - cut
            area += positive_area(qobs, slope, obsdt)
            busy += above_time(qobs, slope, obsdt, 0.)
            tail += above_time(qobs, slope, obsdt, c * spec['tail_delay_s'])
        q = max(0., q + slope * dt)
    result = {'mean_virtual_delay_s': area / duration / c,
              'atom_zero': 1 - busy / duration, 'delay_tail': tail / duration}
    cumulative = np.r_[0., np.cumsum(rates * (stops - starts))]
    for w in spec['windows_s']:
        n = round(duration / w)
        edges = burn + np.arange(n + 1) * w
        indices = np.minimum(np.searchsorted(starts, edges, side='right') - 1, len(starts) - 1)
        totals = cumulative[indices] + rates[indices] * (edges - starts[indices])
        averages = np.diff(totals) / w
        result[f'CV_{w}s'] = float(averages.std() / averages.mean())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='results/lessons/l3r_4/generic')
    args = parser.parse_args()
    specpath = Path(__file__).with_name('generic_prereg.json')
    spec = json.loads(specpath.read_text())
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    reps, comparisons = [], []
    for ci, case in enumerate(spec['cases']):
        law = fluid_queue(case['lambda'], case['amplitude'], case['capacity'], case['T_s'])
        theory = {'mean_virtual_delay_s': law['virtual_delay_time_mean_s'],
                  'atom_zero': law['atom_zero'],
                  'delay_tail': delay_exceedance(law, case['capacity'], spec['tail_delay_s'])}
        theory.update({f'CV_{w}s': window_cv(case['lambda'], case['amplitude'], case['T_s'], w) for w in spec['windows_s']})
        observations = []
        for ri in range(spec['replicates']):
            seed = 318400000 + 1000 * ci + ri
            obs = simulate(case, spec, seed); observations.append(obs)
            reps.append(dict(case=case['name'], seed=seed, **obs))
        for metric, target in theory.items():
            data = np.array([o[metric] for o in observations])
            mean, se = float(data.mean()), float(data.std(ddof=1) / math.sqrt(len(data)))
            tolerance = 4 * se + .01 * abs(target) + 1e-8
            comparisons.append(dict(case=case['name'], metric=metric, formula=target,
                                    measured=mean, replica_SE=se, abs_error=abs(mean-target),
                                    tolerance=tolerance, pass_check=abs(mean-target) <= tolerance))
    for name, rows in [('replicates', reps), ('comparisons', comparisons)]:
        with (out / f'{name}.csv').open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary = dict(owner=spec['owner'], spec_sha256=hashlib.sha256(specpath.read_bytes()).hexdigest(),
                   cases=len(spec['cases']), replicates=len(reps), checks=len(comparisons),
                   passed=sum(r['pass_check'] for r in comparisons),
                   burn_s=spec['burn_s'], measured_s_per_replica=spec['measure_s'],
                   scope=spec['scope'], limitation=spec['limitations'])
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
