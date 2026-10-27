"""Doan Van Tai — replay toy evidence and D-only migration, write the L3.2 report.

Run only after both pytest XML files and the mutation summary exist and pass.
No named grid cell is sent to side_table/evaluate_cell by this script.
"""
import ast
import csv
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from experiments.A00_engine.factorial_core import aggregate
from experiments.A00_engine.cells_adapter import load_cell, queue_law, GRID_PATH
from experiments.A00_engine.toy_refinement import solve_toy_level
from experiments.lessons.run_v1_1_a2 import queue_D
from experiments.lessons.l1_8_refinement import solve_level
from tests.test_engine_core import canonical, E7, side
from tests.test_engine_physics import canonical_native
from experiments.A00_engine.evaluate import evaluate_sides

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/l3_2'


def clean(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def write(name, value):
    (OUT / name).write_text(json.dumps(clean(value), ensure_ascii=False, indent=2) + '\n')


def csvwrite(name, rows):
    with (OUT / name).open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(clean(rows))


def xml_result(name):
    suite = ET.parse(OUT / name).getroot().find('testsuite')
    r = {k: int(suite.attrib[k]) for k in ('tests', 'failures', 'errors', 'skipped')}
    r['seconds'] = float(suite.attrib['time'])
    assert not any(r[k] for k in ('failures', 'errors', 'skipped'))
    return r


def main():
    config = json.loads((OUT / 'config.json').read_text())
    engine, full = xml_result('engine_pytest.xml'), xml_result('full_pytest.xml')
    assert full['tests'] == engine['tests'] + config['baseline_tests']
    mutants = json.loads((OUT / 'mutants/summary.json').read_text())
    assert len(mutants) == 11 and all(m['status'] == 'KILLED' for m in mutants)
    protected = ['notes/01_definitions_v1_2.md', 'notes/design/grid_v1_2.json',
                 'notes/01_claim_boundary_v1_2.md', 'notes/00_research_brief_v1_2.md',
                 'src/smr/cells.py', 'src/smr/idle_gap.py', 'src/smr/gap_screen.py',
                 'src/smr/native/idle_backward.cpp', 'notes/literature/prior_predictions.md']
    hashes = {}
    for path in protected:
        data = (ROOT / path).read_bytes()
        assert data == subprocess.check_output(['git', 'show', f'{config["base_commit"]}:{path}'], cwd=ROOT)
        hashes[path] = hashlib.sha256(data).hexdigest()
    checker = ast.parse((ROOT / 'tests/engine_checker.py').read_text())
    assert not any(isinstance(n, ast.ImportFrom) and n.module and 'factorial_core' in n.module
                   for n in ast.walk(checker))
    for source in config['sources']:
        assert hashlib.sha256((OUT / source['file']).read_bytes()).hexdigest() == source['stored_sha256']

    examples = {'canonical': aggregate(*canonical()[:2]), 'E7_offsets_K0': aggregate(*E7),
                'E2': aggregate(side([F(1, 2)] * 2, [0, 4], [0, 3], [10, 10]), side([1], [-3], [-1])),
                'E5': aggregate(side([F(1, 2)] * 2, [0, 3], [F(3, 2), 0], [10, 10]),
                                side([1], [-1], [-F(1, 2)]))}
    rows = []
    for name, r in examples.items():
        rows.append(dict(example=name, **{'L' + k: r['L'][k] for k in ('00', '01', '10', '11', 'cb0')},
                         **r['G'], E_abs_I_delta=r['E_abs_I_delta'], p_sw=r['p_sw']))
    csvwrite('golden_results.csv', rows)
    write('golden_results.json', examples)
    numeric = evaluate_sides(*canonical_native()[:2], refinement=1, dt=F(1))
    write('canonical_numeric.json', numeric)
    error_rows = []
    for key, radius in numeric['e_num'].items():
        exact = examples['canonical']
        true = (exact['L'][key[1:]] if key.startswith('L') else
                exact['R'][key[1:]] if key.startswith('R') else exact.get(key, exact['G'].get(key)))
        lo, hi = numeric['intervals'][key]
        assert lo <= float(true) <= hi, key
        error_rows.append(dict(quantity=key, exact=true, e_num=radius, lower=lo, upper=hi))
    csvwrite('canonical_enclosures.csv', error_rows)

    refinement = []
    name_map = {'G_S': 'G_S', 'G_M': 'G_M', 'G_SM': 'G_SM', 'Gamma': 'Gamma',
                'G_S_M1': 'G_S|M1', 'G_M_S1': 'G_M|S1'}
    for ref in config['L18_refinements']:
        new = solve_toy_level(ref)
        old = solve_level(ref, dtype=np.longdouble)['summary']
        row = dict(ref=ref, dt_s=str(F(1, ref)), old_C_ref=old['Lstar'], new_C_ref=float(new['C_ref']))
        differences = []
        for new_key, old_key in name_map.items():
            row['old_' + new_key], row['new_' + new_key] = old[old_key], float(new['G'][new_key])
            differences.append(abs(row['old_' + new_key] - row['new_' + new_key]))
        row['max_abs_contrast_difference'] = max(differences)
        row.update(F=float(new['G']['F']), V=float(new['G']['V']), status=new['status'])
        assert row['max_abs_contrast_difference'] < 1e-11
        refinement.append(row)
    csvwrite('L18B_refinement.csv', refinement)

    migration = []
    for cid in config['migration_ids']:
        c = load_cell(cid)
        for which in 'AB':
            for ref in config['migration_refs']:
                new, old = queue_law(c, which, ref), queue_D(c, which, ref)
                difference = float(np.max(abs(new[1] - old[1])))
                mismatch = int(np.count_nonzero(new[2] != old[2]))
                assert difference == 0 and mismatch == 0 and new[0] == old[0] and new[3] == old[3]
                migration.append(dict(cell=cid, queue=which, ref=ref, probability_difference=difference,
                                      support_mismatches=mismatch, old_D_error=old[3], new_D_error=new[3]))
    csvwrite('D_migration.csv', migration)
    assert len(migration) == config['migration_comparisons'] == 32
    grid = json.loads(GRID_PATH.read_text())
    assert sum(len(grid[k]) for k in ('main', 'heldout', 'controls', 'probes')) == 58
    for section in ('main', 'heldout', 'controls', 'probes'):
        for c in grid[section]:
            load_cell(c['id'])  # metadata only, including held-out
    result = dict(status='PASS', responsible='Doan Van Tai', date=config['date'],
                  base_commit=config['base_commit'], engine_tests=engine, full_tests=full,
                  baseline_tests=config['baseline_tests'], mutants_killed=len(mutants), mutants_total=11,
                  random_ledger_cases=300, random_physical_cases=400, key_perturbation_trials=2000,
                  joint_probability_value_interval_trials=40, schema_records=58, D_migration_cases=len(migration),
                  max_D_probability_difference=0., D_support_mismatches=0,
                  L18_refinements=len(refinement), max_L18_contrast_difference=max(r['max_abs_contrast_difference'] for r in refinement),
                  canonical_L=examples['canonical']['L'], canonical_G=examples['canonical']['G'],
                  canonical_E_abs_I=examples['canonical']['E_abs_I_delta'],
                  E7_G=examples['E7_offsets_K0']['G'], E7_E_abs_I=examples['E7_offsets_K0']['E_abs_I_delta'],
                  protected_sha256=hashes, T05_author='OPEN', source_promotion='NOT DONE: new engine stays in experiments',
                  grid_outcomes_computed=0, heldout_D_generated=0, A01='NOT RUN', A04='NOT RUN',
                  A05_F='NOT FROZEN', A05_T='NOT RUN', L33='NOT COMMITTED',
                  Phase4='HOLD: P0-V10', independent_checker_core_imports=0)
    write('verification.json', result)
    report = f'''# L3.2 — engine exact cho bốn ô: báo cáo thực chạy

Người phụ trách: **Doan Van Tai** · 27/10/2026. AI triển khai bốn phần lesson;
đây là verification kỹ thuật, chưa là Understanding/ownership của tác giả.

## A. Đã thực hiện

Engine mới ở [experiments/A00_engine](../../../experiments/A00_engine/): core Side/cut/aggregate,
toy Fraction, native side_table, mean-path vectorized, D22, per-quantity numeric enclosures,
quantile intervals, adapter ba schema, evaluate_cell và guard. Tất cả dùng chung aggregate,
không dựng tích D_A×D_B; chỉ checker toy được phép liệt kê cặp.
Có [T05 AI hỗ trợ + phần tác giả còn trống](../../../notes/theory/T05_exact_engine.md).
Chưa promote source vì T05 author-owned/author-attested còn OPEN. Src/kernel gốc giữ nguyên.

Đính chính lesson: cells.py đã có; baseline 228; idle tính trước update q; guard kiểm
commit A05-F thật. E3/E6 giữ là arrival-law toys ngoài D7; D7 H=1 với mode biết trước
phải cho M0=M1. Float cut mẫu thiếu value/probability/conditional-posterior/rounding errors,
nên đã bổ sung. Bốn lỗi ở lượt native/float đầu đã sửa; [record](development_checks.json).
Nháp đếm migration 48 là lỗi số học: 8×2×2=32; không đổi IDs/ref, giữ bản expected gốc.

## B. Commands và trạng thái

```bash
.venv/bin/python -m pytest tests/test_engine_core.py tests/test_engine_extended.py tests/test_engine_float.py tests/test_engine_physics.py tests/test_engine_refinement.py tests/test_engine_guard.py tests/test_cells_migration.py -q --junitxml=results/lessons/l3_2/engine_pytest.xml > results/lessons/l3_2/engine_pytest.log 2>&1
.venv/bin/python -m experiments.A00_engine.run_mutants > results/lessons/l3_2/mutation_run.log 2>&1
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_2/full_pytest.xml > results/lessons/l3_2/full_pytest.log 2>&1
.venv/bin/python -m experiments.A00_engine.report_verification > results/lessons/l3_2/verification.log 2>&1
git diff --check
```

Engine tests **{engine['tests']} PASS** ({engine['seconds']:.3f} s), toàn repo
**{full['tests']} PASS** ({full['seconds']:.3f} s), baseline trước thay đổi **228 PASS**
tại commit f465db1 ([log trước](../l3_1/part3/full_pytest.log)). Không failures/errors/skips
ở lượt cuối. Mutation **11/11 KILLED**, không tính collection/setup error là kill.
M4 tương đương trong Fraction; bị bắt bằng float conservation tại backlog lớn.
Raw traceback logs/XML giữ nguyên byte; [.gitattributes](../../../.gitattributes) chỉ bỏ
kiểm blank-at-eol cho hai pattern mutant output vì pytest tự in trailing spaces.
Source vẫn kiểm whitespace bình thường; xem development_checks.json.

Đã kiểm: 300 ledger ngẫu nhiên (seed 20261027), 400 plant synthetic (20261028),
2.000 key-perturbation trials (20261029), 40 trials biến đổi probability/value/D22 (20261030).
Các số case là số vòng thực trong test, không phải 300/400 pytest test cases riêng.
Ba loại kiểm được tách: identity báo cáo; bất đẳng thức (oracle/Jensen/sign); đường độc lập
(brute, Fraction DP/idle, native/reference, golden). Identity không được tính là validation.

## C. Số đo

Golden canonical: H=2, dt=1, c=3 packet/slot, u=2; A nền1, B nền0/5,
Pkeep=1/2; D theo golden Phase1. Cost/contrast: packet·s trong toy time scale.
E7 là ledger offsets với K=0, không phải cost queue tuyệt đối.

| Toy | L00 | L01 | L10 | L11 | GS | GM | Γ | F | V | E abs I_delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Canonical | 7.375 | 7.125 | 6.25 | 6.25 | 1.125 | .25 | -.25 | .375 | .75 | .25 |
| E7 offsets | -.25 | -.25 | -.875 | -1 | .625 | 0 | .125 | .375 | .25 | 1.125 |

E2: GS=1.5, GM=1, Γ=−1. E5: GS=−1, GM=0, Γ=1.5. Các giá trị tính thật bằng Fraction.
Canonical/native khớp và từng khoảng chứa đáp án Fraction; cận từng đại lượng ở CSV/JSON.
Không gọi e_num là CI, không suy dt-convergence hoặc validity trên grid từ toy.

| L1.8B toy | Bản cũ GS | Engine mới GS | Cref cũ | Cref mới |
|---|---:|---:|---:|---:|
| ref1, dt=1 s | {refinement[0]['old_G_S']:.12g} | {refinement[0]['new_G_S']:.12g} | {refinement[0]['old_C_ref']:.12g} | {refinement[0]['new_C_ref']:.12g} |
| ref128, dt=1/128 s | {refinement[-1]['old_G_S']:.12g} | {refinement[-1]['new_G_S']:.12g} | {refinement[-1]['old_C_ref']:.12g} | {refinement[-1]['new_C_ref']:.12g} |

Đủ 8 mức ref1…128, max absolute contrast difference={result['max_L18_contrast_difference']:.8e}
packet·s. Đây là tái lập teaching cell L1.8B; không phải A01/final dt của v1.2.

Migration: 58 record metadata; 32 D-only cases trên 8 IDs đã khai báo, A/B, ref1/2.
Probability difference=0, support mismatch=0; không D held-out. Regression cũ còn rerun D-only
L3.1 và screen M31; không gọi những phép đó là “chỉ toy”. Không J/gap/contrast grid mới.

## D. Output và source

- Tài liệu: [README](../../../README.md), [AGENTS](../../../AGENTS.md),
  [DL-045/046](../../../notes/02_decision_log.md), [Phase3](../../../notes/phases/PHASE_3.md),
  [exposure](../../../notes/00_exposure_register.md), [progress](../../../notes/00_progress_log.md),
  [index](../../../notes/03_experiment_index.md), [T05](../../../notes/theory/T05_exact_engine.md).
- [Config, seeds, source hashes](config.json), [expected trước code](expected_before_code.json).
- [Golden CSV](golden_results.csv), [JSON](golden_results.json), [canonical numeric](canonical_numeric.json),
  [per-quantity enclosures](canonical_enclosures.csv), [L1.8B old/new](L18B_refinement.csv),
  [D-only old/new](D_migration.csv), [verification JSON](verification.json).
- Logs: [engine](engine_pytest.log), [full](full_pytest.log), [mutation](mutation_run.log),
  [mỗi mutant + test bắt lỗi](mutants/summary.json), [verification](verification.log).
- XML: [engine](engine_pytest.xml), [full](full_pytest.xml); mỗi mutant có log/XML riêng.
- Source/test: [engine](../../../experiments/A00_engine/), [core tests](../../../tests/test_engine_core.py),
  [checker độc lập](../../../tests/engine_checker.py), [physics](../../../tests/test_engine_physics.py),
  [intervals](../../../tests/test_engine_float.py), [refinement](../../../tests/test_engine_refinement.py),
  [guard](../../../tests/test_engine_guard.py), [migration](../../../tests/test_cells_migration.py),
  [extended golden](../../../tests/test_engine_extended.py).
Không tạo plot/PDF, output A01/A04/A05, prediction card hay record người đọc.

## E. Kết luận

**Technical verification PASS** trong phạm vi đã kiểm. Engine v1 thực nghiệm có đủ
giao diện để chuẩn bị A01; chưa đo/verify grid, không kết luận hypothesis/novelty/network gain.
Bounds là enclosure có điều kiện theo input/kernel và giả định arithmetic finite; test containment
không thay một proof độc lập toàn bộ hệ sai số. Guard kiểm commit sạch/thứ tự, không kiểm nội dung
card hoặc thay runner thực thi các điều kiện V9/A01. Low-level synthetic APIs không là security boundary.

Chưa tính EVPI_w/flip mass 2D. T05 tác giả, ownership/read-back còn OPEN nên code giữ experiments;
không nhận Understanding PASS. L3.3 card chưa commit; A01/A04/A05 chưa chạy. V9 giữ điều kiện(c),
A04 chờ; P0-V10/L8 còn mở, Phase4 HOLD. Có thể học/soạn L3.3 tiếp theo.
'''
    (OUT / 'report.md').write_text(report)
    print(json.dumps(clean(result), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
