"""Doan Van Tai — V7-3 congested business-hours variant (Claude implemented after the Codex quota, 17/11/2026).

Author choice 17/11 (notes/ops/codex/V7_3_congested_decision.md): two pre-declared daytime scenarios. This module
builds the congested one from the provisioned configuration in results/letter/v7_3/day_train: the same window,
managed flows, paths, train days and profile; only the uniform capacity changes, so that the busiest Stay link's
train-window mean utilization equals RHO = 0.9 (the rho definition of Section V). Training data only. The
provisioned files are read, never written. Training and pilot reuse v7_3_day.train/pilot unchanged.

    python3 -m experiments.letter.v7_3_cong configure|train|pilot
"""
import argparse
import subprocess

import numpy as np

from experiments.letter import v7_3_day as A2

RHO = 0.9
SRC = A2.OUT
OUT = A2.D.OUT / 'day_train_congested'
DECISION = 'notes/ops/codex/V7_3_congested_decision.md'


def congested_capacity(window_days, stay, busiest, rho=RHO):
    """Capacity that puts the busiest link's mean Stay load (over days and window slots) at utilization rho."""
    load = np.einsum('nsd,ed->nse', np.asarray(window_days, dtype=float), stay, optimize=True)
    return float(load[:, :, busiest].mean() / rho)


def configure(src=SRC, out=OUT):
    T, E, D = A2.T, A2.E, A2.D
    T.new(out / 'protocol.json', out / 'configuration.json', out / 'configuration.npz')
    for path in (DECISION, 'experiments/letter/v7_3_cong.py'):
        if subprocess.check_output(['git', 'show', 'HEAD:' + path]) != (T.ROOT / path).read_bytes():
            raise ValueError('working file differs from HEAD: ' + path)
    training, arrays, config = A2.load(src)          # verifies the provisioned provenance
    net = D.topology()
    _, stay = D.routes_and_incidence(net)
    ids = [link['id'] for link in net['links']]
    busiest = ids.index(config['busiest_Stay_link'])
    old = float(arrays['capacity'].item())
    cap = congested_capacity(training['days'], stay, busiest)
    infos, incs, bottleneck = A2.regimes_for(net, training['days'], cap)
    if bottleneck != busiest or not np.array_equal(incs, arrays['incidence']):
        raise ValueError('congested variant must keep the provisioned busiest link and paths')
    profile = arrays['profiles'][0]
    new = dict(config)
    new.update(
        scenario='congested_business_hours', rho=RHO, capacity_Mbps=cap, provisioned_capacity_Mbps=old,
        capacity_rule='busiest Stay link train-window mean utilization = 0.9 (Section V rho); training data only',
        regimes=infos,
        warmup_Stay_modulated_upper_utilization=float(
            ((1 + A2.S.BETA) * np.einsum('nsd,ed->nse', training['warm'], stay, optimize=True) / cap).max()),
        forecast_modulated_upper_utilization_by_regime=[
            float(((1 + A2.S.BETA) * np.einsum('sd,aed->sae', profile, inc, optimize=True) / cap).max())
            for inc in incs],
        busiest_link_window_mean_utilization=float(
            np.einsum('nsd,d->ns', training['days'], stay[busiest]).mean() / cap))
    protocol = T.read_json(src / 'protocol.json')
    protocol['scenario'] = 'congested_business_hours'
    protocol['rules'] = dict(protocol['rules'], capacity=new['capacity_rule'])
    protocol['source_sha256'] = dict(protocol['source_sha256'],
                                     **{p: T.sha256(T.ROOT / p) for p in (DECISION, 'experiments/letter/v7_3_cong.py')})
    protocol['implemented_by'] = 'Claude after the Codex quota (author rule 17/11/2026)'
    E.write_json(out / 'protocol.json', protocol)
    E.write_npz(out / 'configuration.npz', dict(arrays, capacity=np.array(cap)))
    E.write_json(out / 'configuration.json', new)
    print(E.json_bytes({k: new[k] for k in ('scenario', 'capacity_Mbps', 'provisioned_capacity_Mbps',
                                             'busiest_link_window_mean_utilization',
                                             'forecast_modulated_upper_utilization_by_regime')}).decode(), flush=True)
    return new


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['configure', 'train', 'pilot'])
    args = parser.parse_args()
    dict(configure=configure, train=lambda: A2.train(OUT), pilot=lambda: A2.pilot(OUT))[args.command]()
