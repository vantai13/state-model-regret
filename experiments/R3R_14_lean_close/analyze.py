"""Doan Van Tai — apply the preregistered lean-closure rules to saved rows (DL-095). AI (Claude) theo ủy quyền.

Reads only saved JSON (native05 reference and lean_close outputs) and calls the hash-pinned rules in
checks.py; writes write-once reports. No engine call.

  python -m experiments.R3R_14_lean_close.analyze replay
  python -m experiments.R3R_14_lean_close.analyze represent
  python -m experiments.R3R_14_lean_close.analyze select
"""
import argparse
from fractions import Fraction as F
import glob
import json
from pathlib import Path

from experiments.R3R_05_contract.rules import CONTRASTS
from experiments.R3R_14_lean_close import checks
from experiments.R3R_14_lean_close.engine import write_once
from experiments.R3R_14_lean_close.run import OUT, ROOT, case_table, load_prereg, r_tag

NATIVE05 = ROOT / 'results/R3R_population_numerics/20261030_05'


def native05_rows():
    """case id -> {(K, ref): row} from every native05 stage."""
    out = {}
    for f in glob.glob(str(NATIVE05 / '*' / '*' / 'result.json')):
        r = json.loads(Path(f).read_text())
        for key, row in r.get('levels', {}).items():
            out.setdefault(r['id'], {})[tuple(map(int, key.split(':')))] = row
    return out


def replay(cfg):
    ref = native05_rows()
    rows, ok = [], True
    for c in cfg['environment_replay']['cases']:
        K, rf = c['level']
        local = json.loads((OUT / 'replay' / c['id'] / f'level_{K}_{rf}.json').read_text())
        old = ref[c['id']][(K, rf)]
        C = F(old['Cref'])
        diff = max(abs(F(local[k]) - F(old[k])) / C for k in ('Cref', *CONTRASTS))
        passed = local['status'] == 'COMPLETED' and diff <= F(1, 10**9)
        ok &= passed
        rows.append(dict(id=c['id'], level=[K, rf], max_relative_difference=float(diff), passed=passed,
                         local_cpu_seconds=local.get('call_cpu_seconds')))
    report = dict(rule=cfg['environment_replay']['pass'], cases=rows, passed=ok)
    write_once(OUT / 'replay_report.json', report)
    return report


def represent(cfg):
    ref = native05_rows()
    K, rf = cfg['representation']['level']
    per_r, selected = [], None
    for r in cfg['representation']['candidates_r']:
        cases, ok = [], True
        for c in cfg['representation']['cases']:
            path = OUT / 'represent' / r_tag(r) / c['id'] / f'level_{K}_{rf}.json'
            coarse = json.loads(path.read_text()) if path.exists() else None
            if coarse is None or coarse.get('status') != 'COMPLETED':
                cases.append(dict(id=c['id'], status='MISSING_OR_UNRESOLVED'))
                ok = False
                continue
            res = checks.representation(ref[c['id']][(K, rf)], coarse)
            ok &= res['ok']
            cases.append(dict(id=c['id'], rounded=coarse['parameters'], ok=res['ok'],
                              max_normalized_delta_pp=float(res['max_normalized_delta']) * 100,
                              criterion_flips=res['criterion_flips'],
                              G_M_pct=[float(checks.normalized(ref[c['id']][(K, rf)], 'G_M')) * 100,
                                       float(checks.normalized(coarse, 'G_M')) * 100],
                              G_S_pct=[float(checks.normalized(ref[c['id']][(K, rf)], 'G_S')) * 100,
                                       float(checks.normalized(coarse, 'G_S')) * 100],
                              cpu_seconds=coarse.get('call_cpu_seconds')))
        per_r.append(dict(r=r, passed=ok, cases=cases))
        if ok and selected is None:
            selected = r
    report = dict(rule=cfg['representation']['pass'], selection_rule=cfg['representation']['selection'],
                  level=[K, rf], candidates=per_r, selected_r=selected,
                  status='SELECTED' if selected else 'HOLD_NO_r_PASSES')
    write_once(OUT / 'representation_selection.json', report)
    return report


def select(cfg):
    cases = case_table(cfg)
    levels = {}
    for cid in cases:
        for f in (OUT / 'calibration' / cid).glob('level_*.json'):
            row = json.loads(f.read_text())
            if row.get('status') == 'COMPLETED':
                K, rf = map(int, f.stem.split('_')[1:])
                levels.setdefault(cid, {})[(K, rf)] = row
            else:
                levels.setdefault(cid, {})
    for cid in cases:
        levels.setdefault(cid, {})
    level, report = checks.select_level(levels, cfg['calibration']['candidates'])
    return level, report


def main():
    p = argparse.ArgumentParser()
    p.add_argument('step', choices=['replay', 'represent', 'select'])
    a = p.parse_args()
    cfg = load_prereg()
    if a.step == 'replay':
        print(json.dumps(replay(cfg), indent=1))
    elif a.step == 'represent':
        print(json.dumps(represent(cfg), indent=1))
    else:
        level, report = select(cfg)
        for r in report:
            print(r['level'], 'cases', r['cases'], 'missing', len(r['missing']), 'failing', len(r['failing']))
            for cid, why in list(r['failing'].items())[:12]:
                print('   ', cid, why[:3])
        print('selected level:', level)


if __name__ == '__main__':
    main()
