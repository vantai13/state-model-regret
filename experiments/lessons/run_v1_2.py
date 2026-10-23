"""Doan Van Tai — grid v1.2 official run under notes/design/v1_2_protocol.md (committed first).

Reproduces the explored main anchors bit-for-bit, anchors the declared held-out slices with the
same rule, screens controls and structural probes, and selects the A01 calibration cells.
Outputs only sign probabilities, DK1 labels and budgets: never J, L*, margins or contrasts.
"""
from experiments.lessons.v1_1_a_common import *
from experiments.lessons.run_v1_1_a2 import flags
from experiments.explore.reformulate_grid import task, ladder, screen, budget
from smr.anchoring import anchor, in_band, midpoint, TARGETS
from smr.gap_screen import library
import argparse, hashlib, itertools, multiprocessing, subprocess

OUT = ROOT / 'results/lessons/v1_2'
EXPLORE = ROOT / 'results/explore_reformulate'
PROTOCOL = 'notes/design/v1_2_protocol.md'
CAP_UPDATES, CAP_BYTES = 2e11, 4 * 1024 ** 3


def sl(name, kappa, alpha_a, alpha_b, eta, h, group):
    return dict(slice=name, kappa=F(kappa), alphaA=F(alpha_a), alphaB=F(alpha_b), eta=F(eta), horizon=str(h), group=group)


def main_slices():
    out = []
    for k, b, e in itertools.product(('3/10', '1', '3'), ('1/2', '9/10'), ('1/2', '3/4')):
        out.append(sl(f'V{len(out) + 1:02}', k, '9/10', b, e, 8, 'core'))
    for b, e in itertools.product(('1/2', '9/10'), ('1/2', '3/4')):
        out.append(sl(f'V{len(out) + 1:02}', '1', '1/2', b, e, 8, 'spoke_A50'))
    for b, e in itertools.product(('1/2', '9/10'), ('1/2', '3/4')):
        out.append(sl(f'V{len(out) + 1:02}', '3/10', '9/10', b, e, 2, 'spoke_h2'))
    return out


def heldout_slices():
    return [sl('H01', '3/5', '9/10', '1/2', '1/2', 8, 'heldout_kappa'),
            sl('H02', '2', '9/10', '9/10', '1/2', 8, 'heldout_kappa'),
            sl('H03', '1', '9/10', '3/4', '1/2', 8, 'heldout_quantile'),
            sl('H04', '1', '9/10', '1/2', '5/8', 8, 'heldout_eta'),
            sl('H05', '3/5', '9/10', '9/10', '1/2', 4, 'heldout_horizon'),
            sl('H06', '3/10', '9/10', '9/10', '1/2', 12, 'heldout_horizon_extrapolation')]


PROBES = [('P01', sl('PS1', '3', '9/10', '9/10', '1/2', 2, 'structural_probe'), F(7)),
          ('P02', sl('PS2', '1', '9/10', '9/10', '1/2', 2, 'structural_probe'), F(8))]
COORDS = ('kappa', 'alphaA', 'alphaB', 'eta', 'horizon')


def key(row):
    return tuple(str(row[k]) for k in COORDS) + (str(row['lambdaA']),)


def pool_map(tasks, workers):
    with multiprocessing.get_context('fork').Pool(workers) as pool:
        return list(pool.imap(task, tasks, chunksize=1))


def control_row(c):
    c = dict(c)
    for k in ('lambdaA', 'kappa', 'eta', 'u', 'yA', 'yB', 'h', 'age'):
        c[k] = F(c[k])
    c['ratesA'], c['ratesB'] = tuple(map(F, c['ratesA'])), tuple(map(F, c['ratesB']))
    row = dict(id=c['id'], role=c['role'], kappa=c['kappa'], eta=c['eta'], yA=c['yA'], yB=c['yB'], h=c['h'],
               H_coarse=c['H_coarse'], ratesA=c['ratesA'])
    for ref in (1, 2):
        r, parts = screen(c, ref)
        row.update({f'{k}_{ref}': v for k, v in r.items()})
        fa = flags(c, 'A', ref, parts['A'][0], parts['A'][2])
        fb = flags(c, 'B', ref, parts['B'][0], parts['B'][2])
        sd, wd = fa[1] or fb[0], fa[0] or fb[1]
        row[f'label_{ref}'] = ('conservation-cell' if fa[0] and fb[0] else 'SD-cell' if sd
                               else 'WD-cell' if wd else 'candidate')
    for ref, (updates, peak) in budget(c).items():
        row[f'updates_{ref}'], row[f'peak_{ref}'] = updates, peak
    return clean(row)


def anchored_cells(slices, ladders):
    """Apply the protocol rule per slice and target; deduplicate shared ladder points."""
    cells, failures = [], []
    for s in slices:
        rows = [r for r in ladders if r['slice'] == s['slice']]
        assert rows and all(r['status'] == 'OK' for r in rows), s['slice']
        chosen = {}
        for t in TARGETS:
            a = anchor(rows, t)
            record = dict(slice=s['slice'], target=t, lambdaA=a['lambdaA'], p_coarse=a['p_coarse'],
                          deviation=a['deviation'], bracketing=a['bracketing'], at_ladder_floor=a['at_ladder_floor'],
                          at_ladder_ceiling=a['at_ladder_ceiling'])
            if a['accepted']:
                chosen.setdefault(a['lambdaA'], []).append(record)
            else:
                failures.append(record)
        for lam, records in sorted(chosen.items()):
            cells.append(dict(slice=s, lambdaA=lam, anchors=records))
    return cells, failures


def check_main_reproduction(ladders, confirms):
    explored = {key(r): r for r in map(json.loads, (EXPLORE / 'ladder_rows.jsonl').read_text().splitlines())}
    explored_c = {key(r): r for r in map(json.loads, (EXPLORE / 'confirm_P4.jsonl').read_text().splitlines())}
    fields = ['yA', 'yB', 'H_coarse', 'updates_16', 'peak_16'] + [f'{p}_{l}' for p in ('p_low', 'p_high') for l in (1, 2)]
    mismatch = [key(r) for r in ladders if any(r[f] != explored[key(r)][f] for f in fields)]
    cfields = fields + [f'{p}_4' for p in ('p_low', 'p_high')] + ['label_1', 'label_2']
    cmismatch = [key(r) for r in confirms if any(r[f] != explored_c[key(r)][f] for f in cfields)]
    return dict(ladder_rows=len(ladders), ladder_mismatches=mismatch, confirm_rows=len(confirms),
                confirm_mismatches=cmismatch)


def proposed_cells():
    rows = list(csv.DictReader((EXPLORE / 'proposed_v1_2_cells.csv').open()))
    explored = {r['slice']: r for r in map(json.loads, (EXPLORE / 'ladder_rows.jsonl').read_text().splitlines())}
    out = set()
    for r in rows:
        e = explored[r['slice']]
        out.add(tuple(str(e[k]) for k in COORDS) + (str(F(r['lambdaA']).limit_denominator(8)),))
    return out


def calibration(main):
    """Protocol §6: three distinct core cells; ties to the smallest ID."""
    pool = [c for c in main if c['group'] == 'core' and c['eligible_calibration']]
    by_id = lambda c: int(c['id'][1:])
    import math as m
    c1 = min(pool, key=lambda c: (F(c['kappa']), F(c['yB']) / (2 - F(c['u'])), by_id(c)))

    def dist(c):
        x = [(m.log(float(F(c['kappa']))) - m.log(.3)) / (m.log(3) - m.log(.3)), (float(F(c['eta'])) - .5) / .25,
             (float(F(c['alphaB'])) - .5) / .4, (min(a['target'] for a in c['anchors']) - .3) / .4]
        return sum((v - .5) ** 2 for v in x)

    rest = [c for c in pool if c['id'] != c1['id']]
    c2 = min(rest, key=lambda c: (dist(c), by_id(c)))
    rest = [c for c in rest if c['id'] != c2['id']]
    c3 = min(rest, key=lambda c: (-c['updates_16'], by_id(c)))
    return [dict(id=c['id'], reason=r) for c, r in ((c1, 'smallest kappa, then smallest B post-switch drain/dt'),
                                                      (c2, 'closest to the core centre (normalized axes)'),
                                                      (c3, 'largest A01 budget at dt/16'))]


def describe(cell, conf, cid, role):
    s = cell['slice']
    row = dict(id=cid, role=role, group=s['group'], slice=s['slice'], kappa=s['kappa'], alphaA=s['alphaA'],
               alphaB=s['alphaB'], eta=s['eta'], u=2 * s['eta'], h=conf['h'], horizon=s['horizon'],
               H_coarse=conf['H_coarse'], lambdaA=cell['lambdaA'], psi=(cell['lambdaA'] - 8) / 10,
               delta=(cell['lambdaA'] + 2 * s['eta'] - 8) / 10, yA=conf['yA'], yB=conf['yB'], anchors=cell['anchors'])
    for l in (1, 2, 4):
        row[f'p_{l}'] = [conf[f'p_low_{l}'], conf[f'p_high_{l}']]
        row[f'unresolved_{l}'] = conf[f'unresolved_{l}']
    row.update(label_1=conf['label_1'], label_2=conf['label_2'],
               **{f'updates_{l}': conf[f'updates_{l}'] for l in (1, 2, 4, 8, 16)},
               **{f'peak_{l}': conf[f'peak_{l}'] for l in (1, 2, 4, 8, 16)})
    row['in_band_all_levels'] = in_band(conf, (1, 2, 4))
    row['within_budget_dt16'] = conf['updates_16'] <= CAP_UPDATES and conf['peak_16'] <= CAP_BYTES
    row['eligible_calibration'] = (row['in_band_all_levels'] and row['within_budget_dt16'] and
                                   conf['label_1'] == conf['label_2'] == 'candidate' and
                                   max(conf[f'unresolved_{l}'] for l in (1, 2, 4)) <= .01)
    return clean(row)


def run(workers):
    if OUT.exists():
        raise SystemExit('preserve v1.2 evidence; choose a fresh checkout')
    protocol_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PROTOCOL], text=True, cwd=ROOT).strip()
    assert protocol_commit, 'protocol must be committed before the run'
    dirty = subprocess.run(['git', 'diff', '--quiet', 'HEAD'], cwd=ROOT).returncode != 0
    assert not dirty, 'run from a clean committed tree'
    OUT.mkdir(parents=True)
    sources = ('src/smr/anchoring.py', 'src/smr/gap_screen.py', 'src/smr/native/idle_backward.cpp',
               'src/smr/stationary_spectral.py', 'experiments/lessons/run_v1_1_a2.py',
               'experiments/explore/reformulate_grid.py', 'experiments/lessons/run_v1_2.py')
    write(OUT / 'config.json', dict(author='Doan Van Tai', protocol=PROTOCOL, protocol_commit=protocol_commit,
          head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=ROOT).strip(),
          levels_screen=[1, 2], levels_check=[1, 2, 4], targets=list(TARGETS), window=.15,
          caps=dict(updates=CAP_UPDATES, bytes=CAP_BYTES), outputs='sign intervals, DK1 labels, budgets only',
          source_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}))
    library()
    mains, helds = main_slices(), heldout_slices()
    # 1. Ladders (levels dt, dt/2).
    ladder_tasks = [(s, lam, (1, 2), False) for s in mains + helds for lam in ladder(s['eta'])]
    ladders = pool_map(ladder_tasks, workers)
    for r in ladders:
        r['group'] = next(s['group'] for s in mains + helds if s['slice'] == r['slice'])
    with (OUT / 'ladders.jsonl').open('w') as h:
        h.writelines(json.dumps(r) + '\n' for r in ladders)
    main_l = [r for r in ladders if r['slice'].startswith('V')]
    held_l = [r for r in ladders if r['slice'].startswith('H')]
    # 2. Anchoring with the protocol rule.
    main_cells, main_fail = anchored_cells(mains, main_l)
    held_cells, held_fail = anchored_cells(helds, held_l)
    # 3. Checks at dt, dt/2, dt/4 with DK1 labels.
    confirm_tasks = [(c['slice'], c['lambdaA'], (1, 2, 4), True) for c in main_cells + held_cells]
    confirms = pool_map(confirm_tasks, workers)
    with (OUT / 'checks.jsonl').open('w') as h:
        h.writelines(json.dumps(r) + '\n' for r in confirms)
    conf = {(r['slice'], str(r['lambdaA'])): r for r in confirms}
    main_rows = [describe(c, conf[(c['slice']['slice'], str(c['lambdaA']))], f'M{i:02}',
                          'main') for i, c in enumerate(main_cells, 1)]
    held_rows = [describe(c, conf[(c['slice']['slice'], str(c['lambdaA']))], f'R{i:02}',
                          'heldout') for i, c in enumerate(held_cells, 1)]
    # 4. Controls (v1.1 definitions, unchanged) and structural probes.
    v11 = json.loads((ROOT / 'notes/design/grid_v1_1_redesign_candidate.json').read_text())['cells']
    controls = [control_row(c) for c in v11 if c['role'] in ('negative', 'wd_probe', 'stress')]
    probes = pool_map([(s, lam, (1, 2), True) for _, s, lam in PROBES], workers)
    for (pid, _, _), r in zip(PROBES, probes):
        r['id'] = pid
    # 5. Reproduction and acceptance.
    rep = check_main_reproduction(main_l, [r for r in confirms if r['slice'].startswith('V')])
    official = {tuple(str(c['slice'][k]) for k in COORDS) + (str(c['lambdaA']),) for c in main_cells}
    rep['main_cells'] = len(main_cells)
    rep['matches_proposed_cells'] = official == proposed_cells()
    accepted = (not rep['ladder_mismatches'] and not rep['confirm_mismatches'] and rep['matches_proposed_cells']
                and len(main_rows) == 38 and all(r['eligible_calibration'] for r in main_rows))
    cal = calibration(main_rows) if accepted else []
    for r in main_rows:
        r['calibration'] = any(c['id'] == r['id'] for c in cal)
    selection = dict(author='Doan Van Tai', status='ACCEPTED' if accepted else 'NOT_ACCEPTED', reproduction=rep,
                     main_cells=len(main_rows), main_failures=main_fail, heldout_cells=len(held_rows),
                     heldout_failures=held_fail, heldout_slices_without_cell=sorted(
                         {s['slice'] for s in helds} - {r['slice'] for r in held_rows}),
                     calibration=cal, controls={c['id']: c['label_1'] for c in controls},
                     probes={p['id']: p.get('label_1') for p in probes})
    write(OUT / 'selection.json', selection)
    write(ROOT / 'notes/design/grid_v1_2.json', dict(author='Doan Van Tai', status=selection['status'],
          protocol=PROTOCOL, protocol_commit=protocol_commit, main=main_rows, heldout=held_rows,
          heldout_failures=held_fail, main_failures=main_fail, controls=controls, probes=probes, calibration=cal))
    manifest(OUT)
    print(json.dumps(selection, indent=1, ensure_ascii=False, default=str))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=8)
    run(p.parse_args().workers)
