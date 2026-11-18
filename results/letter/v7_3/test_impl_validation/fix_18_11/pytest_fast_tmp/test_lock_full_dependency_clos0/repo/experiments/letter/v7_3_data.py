"""Doan Van Tai — V7-3 native GÉANT ingestion and train-only configuration.

No simulation or load calculation on test dates. Raw data/cache stay outside Git.
"""
import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import tarfile

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E

OUT = T.ROOT / 'results/letter/v7_3'
TM_NAME = 'directed-geant-uhlig-15min-over-4months-ALL-native.tgz'
URL = 'https://sndlib.put.poznan.pl/download/' + TM_NAME


def stamp(name):
    match = re.search(r'(\d{8}-\d{4})', name)
    if not match:
        raise ValueError('missing TM timestamp')
    return datetime.strptime(match[1], '%Y%m%d-%H%M')


def parse_tm(text, network):
    """Sparse native OD entries; absent pairs are zero. Preserve presence mask."""
    ss = T.sections(text)
    nodes = [line.split()[0] for line in ss['NODES']]
    if len(nodes) != len(set(nodes)) or set(nodes) != set(network['nodes']):
        raise ValueError('node set differs from topology')
    if not re.search(r'unit\s*=\s*MBITPERSEC', text):
        raise ValueError('expected MBITPERSEC')
    index = {d['id']: i for i, d in enumerate(network['demands'])}
    values, present = np.zeros(len(index)), np.zeros(len(index), dtype=bool)
    for line in ss['DEMANDS']:
        match = re.fullmatch(r'(\S+)\s*\(\s*(\S+)\s+(\S+)\s*\)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if not match:
            raise ValueError('malformed OD entry')
        name, u, v, unit, value, limit = match.groups()
        if name not in index:
            raise ValueError('unknown OD')
        j = index[name]
        d = network['demands'][j]
        z = float(value)
        if (present[j] or (u, v) != (d['source'], d['target']) or float(unit) != 1
                or not np.isfinite(z) or z < 0 or limit != 'UNLIMITED'):
            raise ValueError('duplicate/invalid OD')
        present[j], values[j] = True, z
    if not present.any():
        raise ValueError('empty TM')
    return values, present


def format_tm(values, present, network, when):
    lines = ['?SNDlib native format; type: network; version: 1.0',
             'META (', '  unit = MBITPERSEC', f'  time = {when:%Y%m%d-%H%M}', ')', 'NODES (']
    lines += ['  '+node for node in network['nodes']]
    lines += [')', 'LINKS (', ')', 'DEMANDS (']
    for value, include, d in zip(values, present, network['demands']):
        if include:
            lines.append(f"  {d['id']} ( {d['source']} {d['target']} ) 1 {value:.17g} UNLIMITED")
    return '\n'.join(lines + [')', ''])


def topology(root=None):
    return T.parse_native((root or T.data_root())/'sndlib-networks-native/geant.txt', uniform_capacity=1)


def split_calendar(all_days, complete, warm_complete):
    first = min(all_days)
    cutoff = first + timedelta(days=42)
    eligible = sorted(d for d in all_days if d in complete and d in warm_complete)
    return ([d.isoformat() for d in eligible if d < cutoff],
            [d.isoformat() for d in eligible if d >= cutoff], cutoff.isoformat())


def ingest(root=None, out=OUT):
    root = root or T.data_root()
    archive, net = root/TM_NAME, topology(root)
    E.T.new(out/'data_manifest.json', root/'v7_3_train.npz')
    records, invalid, hashes, duplicates = {}, [], [], set()
    # Only data validity, timestamps and hashes here. No routing/costs on test.
    with tarfile.open(archive) as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith('.txt'):
                continue
            when = stamp(member.name)
            payload = tar.extractfile(member).read()
            hashes.append((member.name, hashlib.sha256(payload).hexdigest()))
            if when in records:
                duplicates.add(when)
                continue
            try:
                if when.minute % 15 or when.second:
                    raise ValueError('off-grid timestamp')
                text = payload.decode('utf-8')
                meta_time = re.search(r'time\s*=\s*(\d{8}-\d{4})', text)
                if not meta_time or stamp(meta_time[1]) != when:
                    raise ValueError('filename/META time mismatch')
                values, present = parse_tm(text, net)
                records[when] = values
            except (ValueError, UnicodeError) as exc:
                invalid.append(dict(member=member.name, timestamp=when.isoformat(), error=str(exc)))
                records[when] = None
    for when in duplicates:
        records[when] = None
    first, last = min(records), max(records)
    all_days = [first.date()+timedelta(days=i) for i in range((last.date()-first.date()).days+1)]
    complete, warm, missing = set(), set(), []
    for day in all_days:
        midnight = datetime.combine(day, datetime.min.time())
        absent = [t.isoformat() for i in range(96)
                  if records.get(t := midnight+timedelta(minutes=15*i)) is None]
        if not absent:
            complete.add(day)
        if all(records.get(midnight-timedelta(minutes=15*i)) is not None for i in range(1, 9)):
            warm.add(day)
        if absent:
            missing.append(dict(date=day.isoformat(), missing_or_corrupt_slots=absent))
    train, test, cutoff = split_calendar(all_days, complete, warm)
    digest = hashlib.sha256(''.join(f'{n}\t{h}\n' for n,h in sorted(hashes)).encode()).hexdigest()
    manifest = dict(owner='Doan Van Tai', source_url=URL, sha256=T.sha256(archive),
                    bytes=archive.stat().st_size, version='SNDlib native 1.0; exact archive pinned by SHA256',
                    topology_sha256=T.sha256(root/'sndlib-networks-native/geant.txt'),
                    units='Mbit/s; source clock timezone unspecified',
                    date_range=[first.isoformat(), last.isoformat()],
                    n_tm_files=len(hashes), n_valid_tm=sum(v is not None for v in records.values()),
                    native_node_count=len(net['nodes']), native_directed_link_count=len(net['links']),
                    native_physical_link_count=len(net['links'])//2, od_universe=len(net['demands']),
                    canonical_member_sha256=digest, invalid=invalid,
                    duplicate_timestamps=sorted(t.isoformat() for t in duplicates),
                    missing_days=missing,
                    dropped_nights=[dict(date=d.isoformat(), reason='incomplete day' if d not in complete else 'incomplete 22:00 warmup')
                                    for d in all_days if d not in complete or d not in warm],
                    train_dates=train, test_dates=test, calendar_cutoff_exclusive=cutoff,
                    rule_file='results/letter/v7_3/PHASE_A_PROTOCOL.json',
                    test_access='integrity and calendar labels only; no test simulations or load summaries',
                    train_cache=str(root/'v7_3_train.npz'))
    # Deliberately cache ONLY train-day and train-night warmup demands.
    days = np.stack([np.stack([records[datetime.fromisoformat(d)+timedelta(minutes=15*i)] for i in range(96)]) for d in train])
    warms = np.stack([np.stack([records[datetime.fromisoformat(d)-timedelta(hours=2)+timedelta(minutes=15*i)] for i in range(8)]) for d in train])
    E.write_npz(root/'v7_3_train.npz', dict(days=days, warm=warms, dates=np.array(train)))
    manifest['train_cache_sha256'] = T.sha256(root/'v7_3_train.npz')
    E.write_json(out/'data_manifest.json', manifest)
    print(json.dumps({k:manifest[k] for k in ('n_tm_files','n_valid_tm','date_range','calendar_cutoff_exclusive')}),flush=True)
    print('train',len(train),'test',len(test),'dropped',len(manifest['dropped_nights']),flush=True)
    return manifest


def routes_and_incidence(net, removed=(), previous=None):
    removed = set(removed)
    graph = {node:set() for node in net['nodes']}
    edge_ix = {}
    for i,e in enumerate(net['links']):
        key = e['id'].split(':')[0]
        if key not in removed:
            graph[e['source']].add(e['target'])
        edge_ix[e['source'],e['target']] = i
    routes, incidence = [], np.zeros((len(net['links']),len(net['demands'])))
    for j,d in enumerate(net['demands']):
        old = previous[j] if previous else None
        if old and all(v in graph[u] for u,v in zip(old[:-1],old[1:])):
            route = old
        else:
            route = T.shortest(graph,d['source'],d['target'])
        if route is None:
            raise ValueError('disconnected')
        routes.append(tuple(route))
        for u,v in zip(route[:-1],route[1:]):
            incidence[edge_ix[u,v],j] = 1
    return routes, incidence


def capacity_rule(daytime, stay):
    peak = float((np.asarray(daytime) @ stay.T).max())
    if peak <= 0:
        raise ValueError('nonpositive daytime peak')
    return peak/.9


def consolidate(net, mean_night, capacity):
    stay_routes, stay = routes_and_incidence(net)
    load = stay @ mean_night
    ids = sorted({e['id'].split(':')[0] for e in net['links']})
    bidir = {name:sum(load[i] for i,e in enumerate(net['links']) if e['id'].split(':')[0]==name) for name in ids}
    order = sorted(ids,key=lambda key:(bidir[key],key))
    removed, history, routes, switch = [], [], stay_routes, stay.copy()
    stop = None
    for name in order:
        try:
            trial_routes, trial = routes_and_incidence(net,removed+[name],routes)
        except ValueError:
            history.append(dict(link=name,status='KEEP_BRIDGE'))
            continue
        maximum = float((trial @ mean_night).max()/capacity)
        history.append(dict(link=name,status='REMOVE' if maximum<=.8 else 'STOP_UTILIZATION',max_train_mean_utilization=maximum))
        if maximum > .8:
            stop = name
            break
        removed.append(name)
        routes, switch = trial_routes, trial
    return dict(removed=removed,order=order,history=history,stop_link=stop,
                stay_routes=[list(p) for p in stay_routes], switch_routes=[list(p) for p in routes]), np.stack([stay,switch])


def configure(root=None, out=OUT):
    root = root or T.data_root()
    with np.load(root/'v7_3_train.npz',allow_pickle=False) as f:
        days, dates = f['days'], f['dates']
    net = topology(root)
    _,stay = routes_and_incidence(net)
    cap = capacity_rule(days[:,24:88].reshape(-1,len(net['demands'])),stay)
    config, incidence = consolidate(net,days[:,:24].mean(axis=(0,1)),cap)
    load = np.einsum('nsd,aed->nsae',days[:,:24],incidence,optimize=True)
    profiles = np.stack([days[[datetime.fromisoformat(d).weekday()>=5 for d in dates] if weekend else
                              [datetime.fromisoformat(d).weekday()<5 for d in dates],:24].mean(axis=0)
                         for weekend in (False,True)])
    config.update(owner='Doan Van Tai',training_only=True,capacity_Mbps=cap,
                  daytime_peak_utilization=float((days[:,24:88].reshape(-1,len(net['demands']))@stay.T).max()/cap),
                  training_dates=dates.tolist(),train_nights=len(dates),
                  nighttime_utilization_mean_by_action=(load.mean(axis=(0,1))/cap).tolist(),
                  nighttime_utilization_max_by_action=(load.max(axis=(0,1))/cap).tolist(),
                  train_mean_night_max_by_action=(load.mean(axis=(0,1)).max(axis=1)/cap).tolist(),
                  path_rule='EV-TE min-hop, then complete node sequence lexicographic; preserve unaffected routes',
                  removal_rule='fixed initial bidirectional train-mean-load order; skip bridges, stop first capacity failure',
                  action_names=['Stay','Switch'],forecast_class_counts=[sum(datetime.fromisoformat(d).weekday()<5 for d in dates),sum(datetime.fromisoformat(d).weekday()>=5 for d in dates)])
    E.write_npz(out/'train/configuration.npz',dict(incidence=incidence,profiles=profiles,capacity=np.array(cap)))
    E.write_json(out/'train/configuration.json',config)
    rows = []
    for n,d in enumerate(dates):
        for a,action in enumerate(config['action_names']):
            rows.append(dict(date=d,action=action,mean_utilization=float(load[n,:,a].mean()/cap),
                             max_utilization=float(load[n,:,a].max()/cap),
                             max_mean_link_utilization=float(load[n,:,a].mean(axis=0).max()/cap)))
    T.write_csv(out/'train/night_utilizations.csv',rows)
    print(json.dumps(dict(capacity=cap,removed=config['removed'],max_night_utilization=config['nighttime_utilization_max_by_action'])),flush=True)
    return config


def load_training(root=None, out=OUT):
    root = root or T.data_root()
    manifest = T.read_json(out/'data_manifest.json')
    if T.sha256(root/'v7_3_train.npz') != manifest['train_cache_sha256']:
        raise ValueError('training cache fingerprint changed')
    with np.load(root/'v7_3_train.npz',allow_pickle=False) as f:
        training = {k:f[k] for k in f.files}
    if training['dates'].tolist()!=manifest['train_dates'] or set(training['dates']) & set(manifest['test_dates']):
        raise ValueError('training/test leakage')
    with np.load(out/'train/configuration.npz',allow_pickle=False) as f:
        config = {k:f[k] for k in f.files}
    return training,config


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['ingest','configure'])
    args=parser.parse_args()
    (ingest if args.command=='ingest' else configure)()
