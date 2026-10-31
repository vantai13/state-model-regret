"""Bước 1 — chẩn đoán read-only 8 điểm NOT_READY của L44_A1. Không import engine, không gọi engine.

Với mỗi cặp (điểm, rho): độ rộng sai số số học ở ba mức, chênh refinement theo trục K và trục dt
cho từng đại lượng baseline, khối lượng nút "mơ hồ" (ambiguous) và độ dốc của L00^theta theo rho.
python -m experiments.P4_A2.diagnose_l44   -> results/lessons/p4_a2/l44_diagnosis.json (ghi một lần)
"""
from fractions import Fraction as F
import json
import os
from pathlib import Path
from statistics import median

from experiments.P4_03_map_audit.common import ROOT, sha, write_once, require
from experiments.P4_A1.config import committed
from experiments.R3R_05_contract.rules import TOL_NUM
from experiments.R3R_14_lean_close.checks import ARITH_MAX

SRC = Path('results/lessons/l4_4/a1/native')
OUT = Path('results/lessons/p4_a2/l44_diagnosis.json')
LEVELS = {'main': '640_4', 'K': '320_4', 'dt': '640_2'}
FIELDS = {'L00': 'error00', 'L10': 'error10', 'GS_theta': 'GS_theta_error', 'deltaL10': 'deltaL10_error'}
INPUTS = {}


def load(path):
    path = Path(path)
    committed(path)
    INPUTS[str(path)] = sha(ROOT / path)
    return json.loads((ROOT / path).read_text())


def pair_record(rows, i):
    """Một cặp (điểm, rho): cùng công thức với P4_A1.checks.baseline_readiness, tách theo trục."""
    main = rows['main']; cf = F(main['Cref']); b = main['baseline'][i]
    rec = dict(rho=b['rho'])
    for name, row in rows.items():
        bb = row['baseline'][i]; c = F(row['Cref'])
        rec[f'width_{name}'] = max(F(bb[e]) / c for e in FIELDS.values())
        rec[f'width_fields_{name}'] = {field: float(F(bb[err])/c) for field,err in FIELDS.items()}
        rec[f'ambiguous00_{name}'] = bb['uncertain_action_mass']['00']
        rec[f'ambiguous10_{name}'] = bb['uncertain_action_mass']['10']
    for axis in ('K', 'dt'):
        coarse = rows[axis]; cc = F(coarse['Cref'])
        for field in FIELDS:
            gf, gc = F(b[field]), F(coarse['baseline'][i][field])
            rec[f'd_{axis}_{field}'] = max(abs(gf - gc) / cf, abs(gf / cf - gc / cc))
    curve = [F(x['L00']) / cf for x in main['baseline']]           # L00^theta / Cref trên lưới rho
    rec['jump_L00'] = max(abs(curve[i] - curve[j]) for j in (i - 1, i + 1) if 0 <= j < len(curve))
    kinds = []
    if any(rec[f'width_{n}'] > ARITH_MAX for n in LEVELS):
        kinds.append('W')                                          # độ rộng sai số số học
    if any(rec[f'd_K_{f}'] > TOL_NUM for f in FIELDS):
        kinds.append('K')                                          # refinement theo K
    if any(rec[f'd_dt_{f}'] > TOL_NUM for f in FIELDS):
        kinds.append('D')                                          # refinement theo dt
    rec['failure'] = ''.join(kinds)
    rec['fields_over_tol'] = sorted({f for f in FIELDS for a in ('K', 'dt') if rec[f'd_{a}_{f}'] > TOL_NUM})
    return rec


def main():
    INPUTS.clear()
    points, pairs = [], []
    ids = sorted(p.name for p in (ROOT / SRC).iterdir() if p.is_dir())
    for cid in ids:
        folder = SRC / cid
        comparison = load(folder / 'comparison.json')
        rows = {name: load(folder / f'level_{lv}.json') for name, lv in LEVELS.items()}
        recs = [pair_record(rows, i) for i in range(len(rows['main']['baseline']))]
        failing = [r for r in recs if r['failure']]
        points.append(dict(id=cid, status=comparison['status'], parameters=rows['main']['parameters'],
                           failing_rho=[r['rho'] for r in failing]))
        for r in recs:
            pairs.append(dict(id=cid, status=comparison['status'], **r))
    bad = [p for p in pairs if p['failure']]
    good = [p for p in pairs if not p['failure']]
    jump = lambda ps: sorted(float(p['jump_L00']) for p in ps)
    summary = dict(
        observed_points=len(points), observed_pairs=len(pairs), failing_pairs=len(bad),
        failing_points=len({p['id'] for p in bad}),
        failing_pairs_per_point={p['id']: p['failing_rho'] for p in points if p['failing_rho']},
        failure_kinds={k: sum(k in p['failure'] for p in bad) for k in 'WKD'},
        fields_over_tol=sorted({f for p in bad for f in p['fields_over_tol']}),
        jump_L00_median=dict(failing=float(median(p['jump_L00'] for p in bad)) if bad else None,
                             passing=float(median(p['jump_L00'] for p in good)) if good else None),
        median_method='standard median; average of middle two for even N (corrects supplied upper-middle statistic)',
        passing_pairs_with_jump_over_5pct=sum(p['jump_L00'] > F(1,20) for p in good),
        consistent_with_A1_status=all((p['status'] == 'NOT_READY') == bool(p['failing_rho']) for p in points))
    require(summary['observed_points']==19 and summary['failing_points']==8 and summary['failing_pairs']==8
            and summary['failure_kinds']=={'W':3,'K':6,'D':3}
            and summary['fields_over_tol']==['GS_theta','L00'] and summary['consistent_with_A1_status'],
            'DIAGNOSIS_DIFFERS_FROM_SUPPLIED_A1_BASE: stop before amendment')
    report = dict(responsible='Doan Van Tai', engine_calls=0, CF_outcomes=0, rho_selection_computed=False,
                  summary=summary, points=points,
                  pairs=[{k: (float(v) if isinstance(v, F) else v) for k, v in p.items()} for p in pairs],
                  limitations=['8/72 is a cap fraction against planned N, not an estimated SH prevalence',
                               'H_res/H_cliff remain hypotheses; no physical mechanism established'],
                  inputs_sha256=dict(sorted(INPUTS.items())))
    (ROOT / OUT).parent.mkdir(parents=True, exist_ok=True)
    if (ROOT / OUT).exists():
        require(json.loads((ROOT / OUT).read_text()) == json.loads(json.dumps(report)), 'diagnosis differs; never overwrite')
        return  # repeat is silent and never overwrites the write-once artifact
    else:
        write_once(ROOT / OUT, report)
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    print('\n id      lambdaA lambdaB kappa eta  h  | rho    loại  width(main)x1e4  dK_L00%  ddt_L00%  amb00  jump%')
    for p in bad:
        prm = next(x['parameters'] for x in points if x['id'] == p['id'])
        print(f" {p['id']}  {prm[0]:>4} {prm[1]:>5}  {prm[2]:>5} {prm[3]:>4} {prm[4]:>3} | {p['rho']:6} {p['failure']:4}"
              f"  {float(p['width_main'])*1e4:9.2f}  {float(p['d_K_L00'])*100:8.3f}  {float(p['d_dt_L00'])*100:8.3f}"
              f"  {p['ambiguous00_main']:.4f} {float(p['jump_L00'])*100:6.2f}")


if __name__ == '__main__':
    main()
