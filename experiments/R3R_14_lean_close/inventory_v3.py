"""Doan Van Tai — collision inventory v3 for the card-v2 CF draw (DL-095). AI (Claude) theo ủy quyền.

v3 = the committed inventory v2 (pilot stages, v1.2 grid, L3R.3 audit, conservative zero variants, the 114
native05 calibration designs) plus every coordinate seen after it:
  * the regime-map exploration (branch explore/v13-regime-map, commit 574a36f). The fluid plant is invariant to
    scaling age, kappa and h together, so a regime run at age a is the age-1 regime (kappa/a, h/a); +/-6 runs go
    to the v1.3 namespace, other amplitudes to a separate namespace;
  * the lean-closure representation points (four r) and calibration v2 points (_R, RINT);
  * probe regimes computed in the AI session whose numbers were seen but never saved.
Parameters only; no outcome is read.

  python -m experiments.R3R_14_lean_close.inventory_v3
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.R3R_05_contract.schema import IDENTITY
from experiments.R3R_14_lean_close.engine import round_rates, write_once
from experiments.R3R_14_lean_close.run import OUT, case_table, load_prereg

V2 = Path('results/lessons/l3r_7/full_numerics/collision_inventory_v2.json')
MAP_COMMIT = '574a36fb4213a79d3d2aa305a489701cfc3059f2'
MAP_STAGES = ('map1', 'map1robustK', 'map1robustdt', 'map2', 'map3age', 'map4amp', 'plantrobust', 'jointrobust')
# Regimes evaluated during the AI session (29-30/10) whose values were displayed but not saved:
# (lambdaA, lambdaB, kappa, eta, h, age, amp).
SESSION_PROBES = [('6', '8', '1/5', '7/8', '4', '1', '6'), ('6', '15/2', '1/20', '7/8', '8', '1', '6'),
                  ('13/2', '7', '1/10', '3/4', '8', '4', '6'), ('13/2', '7', '1/10', '3/4', '8', '1/4', '6'),
                  ('13/2', '7', '3/10', '3/4', '2', '4', '6'), ('15/2', '8', '3/10', '3/4', '4', '2', '4'),
                  ('15/2', '8', '3/10', '3/4', '4', '2', '7'), ('13/2', '8', '1/10', '1/2', '8', '2', '6')]


def key_of(lamA, lamB, u, kappa, h, c):
    coords = dict(zip(IDENTITY, (F(lamA), F(lamB), F(u), F(kappa), F(h), F(c))))
    return {k: str(v) for k, v in coords.items()}, '|'.join(str(coords[k]) for k in IDENTITY)


def record(source, rid, lamA, lamB, eta, kappa, h, c='0', age='1', amp='6', note='', reservation='observed_or_design_reserved'):
    age, amp = F(age), F(amp)
    coords, key = key_of(lamA, lamB, 2 * F(eta), F(kappa) / age, F(h) / age, c)
    namespace = 'v1.3_fixed_plant' if amp == 6 else f'explore_amplitude_{amp}'
    if age != 1:
        note = (note + '; ' if note else '') + f'run at age {age}, rescaled to age 1'
    return dict(source=source, source_id=rid, namespace=namespace, note=note, reservation_type=reservation,
                coordinates=coords, key=key)


def build():
    cfg = load_prereg()
    v2 = json.loads(V2.read_text())
    records = list(v2['records'])
    sources = dict(v2['sources'])
    sources[str(V2)] = hashlib.sha256(V2.read_bytes()).hexdigest()
    counts = dict(v2['source_record_counts'])
    for stage in MAP_STAGES:
        path = f'results/explore_v13/{stage}/specs.json'
        blob = subprocess.run(['git', 'show', f'{MAP_COMMIT}:{path}'], capture_output=True, check=True).stdout
        sources[f'{MAP_COMMIT}:{path}'] = hashlib.sha256(blob).hexdigest()
        specs = json.loads(blob)
        for s in specs:
            rid, a, b, k, e, h, _ref, _K, *rest = s
            c = rest[0] if rest else '0'
            age = rest[1] if len(rest) > 1 else '1'
            amp = rest[2] if len(rest) > 2 else '6'
            records.append(record(f'regime_map/{stage}', rid, a, b, e, k, h, c, age, amp))
        counts[f'regime_map/{stage}'] = len(specs)
    for r in cfg['representation']['candidates_r']:
        for c in cfg['representation']['cases']:
            lamA, lamB, kappa, eta, h, cs = round_rates(c['parameters'], r)
            records.append(record(f'lean_close/represent_{r}', c['id'] + '_R', lamA, lamB, eta, kappa, h, cs))
    counts['lean_close/represent'] = 4 * len(cfg['representation']['cases'])
    extra = {cid: p for cid, p in case_table(cfg).items() if cid.endswith('_R') or cid.startswith('RINT_')}
    for cid, (lamA, lamB, kappa, eta, h, cs) in sorted(extra.items()):
        records.append(record('lean_close/calibration_v2', cid, lamA, lamB, eta, kappa, h, cs))
    counts['lean_close/calibration_v2'] = len(extra)
    for i, (a, b, k, e, h, age, amp) in enumerate(SESSION_PROBES):
        records.append(record('ai_session_probe_unsaved', f'XT{i}', a, b, e, k, h, '0', age, amp,
                              note='values displayed in the AI session, never saved'))
    counts['ai_session_probe_unsaved'] = len(SESSION_PROBES)
    v13 = {r['key'] for r in records if r['namespace'] == 'v1.3_fixed_plant'}
    return dict(owner='Doan Van Tai', status='PARAMETER_ONLY_INVENTORY_V3_CARD_V2', decision='DL-095',
                identity=list(IDENTITY), parent=str(V2), sources=sources, records=records,
                source_record_counts=counts, distinct_v13_keys=len(v13),
                limitations=list(v2['limitations']) + [
                    'age-rescaled regime-map keys rely on the fluid time-scaling equivalence (exact in the model, '
                    'approximate in the dt discretisation)',
                    'other-amplitude runs are a different plant: kept in their own namespace, not reserved in v1.3 keys',
                    'session probes are listed from the conversation record, not from saved files'])


if __name__ == '__main__':
    inv = build()
    write_once(OUT / 'collision_inventory_v3.json', inv)
    print(json.dumps(dict(status=inv['status'], counts=inv['source_record_counts'], distinct_v13_keys=inv['distinct_v13_keys']), indent=1))
