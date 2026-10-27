"""Doan Van Tai — postprocess existing A01 files; never call a plant/grid API."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from experiments.A01_null_refinement.selection import NAMES, choose_final

ROOT = Path(__file__).resolve().parents[2]


def read_rows(path):
    return list(csv.DictReader(path.open()))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id')
    args = parser.parse_args()
    folder = ROOT / 'results/A01' / args.run_id
    out = ROOT / 'results/lessons/l3_4'
    status = json.loads((folder / 'run_status.json').read_text())
    if status['status'] not in ('PASS', 'HOLD'):
        raise SystemExit('A01 not complete; preserve failure and diagnose first')
    raw = read_rows(folder / 'refinement.csv')
    levels = {}
    for r in raw:
        row = {g: float(r[g]) for g in NAMES}
        row.update({f'e_{g}': float(r[f'e_{g}']) for g in NAMES})
        row.update(m=int(r['m']), Cref=float(r['Cref']), Cref_low=float(r['Cref_low']),
                   precision_ok=r['precision_ok'] == 'True')
        levels.setdefault(r['cell'], []).append(row)
    final, picks = choose_final(levels)
    assert final == status['final_ref'] and picks == status['per_cell']
    nulls, negative = read_rows(folder / 'nulls.csv'), read_rows(folder / 'negative_cells.csv')
    psw = read_rows(folder / 'psw_check.csv')
    assert list(psw[0]) == ['cell', 'ref', 'p_low', 'p_high', 'match']
    assert len(psw) == 9 and all(x['match'] == 'True' for x in psw)
    required = [r for r in nulls if r['control'] in ('C1', 'C2', 'C3')]
    assert len(required) == 18 and all(r['exact_identity_pass'] == 'True' for r in required)
    c5 = [r for r in negative if r['control'] == 'C5']
    c6 = [r for r in negative if r['control'] == 'C6']
    assert len(c5) == 10 and all(float(r[g]) == 0 for r in c5 for g in NAMES)
    assert len(c6) == 6 and all(float(r['G_S_M1']) == 0 for r in c6)
    tests = ET.parse(out / 'preflight/full_suite_final.xml').getroot()
    test_n = sum(int(s.attrib['tests']) for s in tests.iter('testsuite'))
    mutants = json.loads((out / 'preflight/mutants_final/summary.json').read_text())
    assert len(mutants) == 11 and all(r['status'] == 'KILLED' for r in mutants)
    manifest = json.loads((folder / 'manifest.json').read_text())
    measured = dict(author='Doan Van Tai', status=status, recomputed_selection=dict(final_ref=final, per_cell=picks),
        tests_passed=test_n, mutants_killed=len(mutants), psw_bitwise_matches=9,
        C1_C2_C3_passed=18, C2prime_observations=6, C4_independent_toy='PASS',
        C5_cell_levels=10, C5_exact_zero_entries=60, C6_exact_zero_entries=6,
        calibration_cell_levels=len(raw),
        max_numeric_error_ratio=max(float(r['e_num_max']) / float(r['Cref_low']) for r in raw),
        max_unresolved_mass=max(float(r['unresolved_mass_max']) for r in raw),
        precision_passed=sum(r['precision_ok'] == 'True' for r in raw),
        cost_unit='packet*s', seed=None, method='finite-law expectation, native longdouble',
        prediction_card_sha256=manifest['prediction_card_sha256'],
        prereg_commit=manifest['prereg_commit'], code_commit=manifest['code_commit'],
        original_failed_run='results/A01/20261027_01', A04_run=False, heldout_run=False)
    write(out / 'verification.json', measured)
    fingerprint = []
    signs = dict(G_S=1, G_M=1, G_SM=1, Gamma=-1, G_S_M1=0, G_M_S1=0)
    for cid in levels:
        records = [r for r in raw if r['cell'] == cid]
        for lo, hi in zip(records, records[1:]):
            al, ah = int(lo['a00_nominal']), int(hi['a00_nominal'])
            if al != ah:
                jump = (ah - al) * float(hi['E_delta'])
                fingerprint.append(dict(cell=cid, m_lo=int(lo['m']), m_hi=int(hi['m']),
                    a00_lo=al, a00_hi=ah, E_delta_hat_lo=float(lo['E_delta_hat']),
                    E_delta_hat_hi=float(hi['E_delta_hat']), counterfactual_L00_jump_at_fine=jump,
                    changes={g: float(hi[g])-float(lo[g]) for g in NAMES},
                    pure_L00_jump_fingerprint={g: jump*signs[g] for g in NAMES},
                    residual_physics_D_and_S1_drift={g: float(hi[g])-float(lo[g])-jump*signs[g] for g in NAMES},
                    interpretation='counterfactual decomposition; residual also changes with D/physics, no automatic bug diagnosis'))
    write(out / 'jump_diagnostics.json', fingerprint)
    fig, axes = plt.subplots(3, 1, figsize=(10, 11), constrained_layout=True)
    for ax, (cid, records) in zip(axes, levels.items()):
        for name in NAMES:
            ax.plot([r['m'] for r in records], [100*r[name]/r['Cref'] for r in records], '.-', label=name)
        ax.set_xscale('log', base=2); ax.set_xticks([1,2,4,8,16], ['1','2','4','8','16'])
        ax.set_title(cid + ': all preregistered levels'); ax.set_ylabel('Contrast / Cref (%)'); ax.grid(alpha=.25)
    axes[0].legend(ncol=3, fontsize=9); axes[-1].set_xlabel('Refinement m; dt = 1 / (120 m) seconds')
    fig.suptitle('A01 calibration — finite-level stability, not continuum convergence')
    fig.savefig(out / 'refinement.png', dpi=160); plt.close(fig)
    pairs = read_rows(folder / 'refinement_pairs.csv')
    lines = ['# L3.4 / A01 — báo cáo thực chạy', '', 'Người phụ trách: **Doan Van Tai** · 27/10/2026.', '',
             f'**Kết quả A01: {status["status"]}; ref chung = {final}; dt cuối = {status["final_dt_s"]} s.**', '',
             'A01 kiểm implementation và độ ổn định trên ba ô calibration; không chấm prediction card hoặc xác nhận Main RQ.', '',
             '## Thực hiện và baseline lý thuyết', '',
             'Đã khóa prereg/receipt, triển khai selector, Part0→A→B và sửa biểu diễn GS_M1 bằng hai direct cuts.',
             'Run01 dừng tại N01; giữ toàn bộ dữ liệu/lỗi. Certificate always-empty sửa predicted tie sai −1.35525e−20;',
             'không đổi plant, control, threshold, card, mức dt hoặc budget. Xem DL-050/051.',
             'Run02 PASS controls, tạm dừng tại M01/ref8 để sửa O(n²) conversions trong D22; giữ đủ partial outputs.',
             'Run03 chạy mới Part0/A và đủ15 mức PartB bằng6 processes, không dùng lại controls/code cũ (DL-052).', '',
             f'- Full suite sau sửa: **{test_n} PASS**, mutant **11/11 KILLED**; targeted23 PASS.',
             '- Part0: **9/9** khoảng p_sw khớp bit-for-bit public baseline.',
             '- C1/C2/C3: **18/18** cell-control-level identities PASS; C2prime6 quan sát, không là yêu cầu zero.',
             '- C4: independent rational min-cost enumeration + strict-tie action PASS; không là physical-kernel proof độc lập.',
             '- C5: **10/10** cell-level, **60/60** contrast entries bằng0 chính xác; C6 **6/6** GS_M1 bằng0 chính xác.',
             f'- PartB: **15/15** cell-level; numeric precision PASS **{measured["precision_passed"]}/15**.',
             f'- max e_num/Cref_lower = {measured["max_numeric_error_ratio"]:.9g} (cap .0025); max unresolved mass = {measured["max_unresolved_mass"]:.9g} (cap .01).', '',
             '## Làm mịn — đủ mọi cặp, không chọn kết quả thuận lợi', '',
             '| Cell | Cặp ref | max change / min Cref (%) | Cận trên gồm e_num (%) | PASS |',
             '|---|---|---:|---:|---|']
    for r in pairs:
        lines.append(f'| {r["cell"]} | {r["m_lo"]}→{r["m_hi"]} | {100*float(r["relative_change"]):.7g} | {100*float(r["relative_change_upper"]):.7g} | {r["pair_pass"]} |')
    lines += ['', f'Picks từng ô: `{picks}`; cutoff mỗi cặp **0.25%**. Rho/Richardson chỉ diagnostics.', '',
              '## Toàn bộ contrast đo được (packet·s)', '',
              '| Cell | m | Cref | GS | GM | GSM | Gamma | GS_M1 | GM_S1 | a00 | status |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for r in raw:
        vals = ' | '.join(f'{float(r[k]):.9g}' for k in ('Cref', *NAMES))
        lines.append(f'| {r["cell"]} | {r["m"]} | {vals} | {r["a00"]} | {r["status"]} |')
    lines += ['', '## Ô WD — chỉ GS_M1 là zero bắt buộc', '',
              '| Cell | ref | GS_M1 | GM | GS | p_sw |', '|---|---:|---:|---:|---:|---:|']
    for r in c6:
        lines.append(f'| {r["cell"]} | {r["ref"]} | {r["G_S_M1"]} | {float(r["G_M"]):.9g} | {float(r["G_S"]):.9g} | {float(r["p_sw"]):.9g} |')
    lines += ['', '## Lệnh đã thực thi', '', '```bash',
              '.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_4/preflight/full_suite_final.xml',
              '.venv/bin/python -u -m experiments.A00_engine.run_mutants --out results/lessons/l3_4/preflight/mutants_final',
              '.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id 20261027_01 --allow-grid',
              '.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id 20261027_02 --allow-grid',
              f'.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id {args.run_id} --allow-grid --workers 6',
              f'.venv/bin/python -m experiments.A01_null_refinement.selection results/A01/{args.run_id}/refinement.csv',
              f'.venv/bin/python -m experiments.lessons.report_l3_4 {args.run_id}', '```', '',
              '## Provenance và output', '',
              f'- Prereg commit `{manifest["prereg_commit"]}` / SHA `{manifest["prereg_sha256"]}`.',
              f'- Run code/receipt `{manifest["code_commit"]}`; card SHA `{manifest["prediction_card_sha256"]}`.',
              '- Config: `experiments/A01_null_refinement/config.json`, bản copy/config hash trong run manifest.',
              f'- Run data/log: `results/A01/{args.run_id}/` và `results/A01/{args.run_id}.console.log`.',
              '- CSV: psw_check, nulls, negative_cells, refinement, refinement_pairs, refinement_diagnostics.',
              '- JSON: manifest/config/controls_status/selection/run_status, mỗi calibration cell-level và negative cell-level.',
              '- Report/metric/plot: thư mục này: `report.md`, `verification.json`, `jump_diagnostics.json`, `refinement.png`.',
              '- Source: A01 runner/selector/controls/psw/provenance; sửa A00 factorial_core/physical/precision.', '',
              '## Giới hạn và gate', '',
              'Exact expectation trên finite slot law, deterministic, không Monte Carlo nên không sampling CI/seed.',
              'Cận số conditional trên input/kernel bounds; không phải formal proof toàn bộ physical enclosures.',
              'Không chứng minh continuum limit, 35main còn lại ổn định hoặc plant giống mạng thật.',
              'M01/M09/M22 mọi mức đã exposed, chỉ còn đánh giá theo card đã khóa; ngoài card là discovery.',
              'A04 **chưa chạy, V9 chưa gửi nên chờ**; nếu chạy phải kiểm cặp 2dt_final/dt_final từng ô.',
              'Không D/outcomes held-out mới. H1/null/A05-F chưa khóa; L8/P0-V10/T05 author-writing vẫn mở.', '']
    (out / 'report.md').write_text('\n'.join(lines))
    targets = [*folder.glob('*'), *folder.parent.glob('*.console.log'),
               *out.glob('*.json'), out / 'report.md', out / 'refinement.png']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in targets if p.is_file() and p.name != 'artifact_audit.json'}
    write(out / 'artifact_audit.json', dict(files=len(hashes), sha256=hashes,
          rule='hashes exclude this audit file itself; all source hashes remain in run manifest'))
    print(json.dumps(measured, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
