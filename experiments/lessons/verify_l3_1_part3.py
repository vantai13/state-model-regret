"""Doan Van Tai — numerical migration/provenance checks for L3.1 Part 3.

Run after pytest has written full_pytest.xml and migration_pytest.xml.
Writes measurements/report; no action costs, predictions or held-out D.
"""
import ast
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

import numpy as np

from smr.cells import make_cell, queue_D
from experiments.explore.reformulate_grid import make_cell as original_make_cell
from experiments.lessons.run_v1_1_a2 import queue_D as original_queue_D
from tests.test_v1_2_cells import GRID, calibration_or_control, main_cell

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/l3_1/part3'


def original(path, revision):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)


def function_ast(text, name):
    return ast.dump(next(n for n in ast.parse(text).body
                         if isinstance(n, ast.FunctionDef) and n.name == name))


def pytest_result(name):
    suite = ET.parse(OUT / name).getroot().find('testsuite')
    assert suite is not None
    result = {k: int(suite.attrib[k]) for k in ('tests', 'failures', 'errors', 'skipped')}
    result['seconds'] = float(suite.attrib['time'])
    assert result['tests'] > 0 and not any(result[k] for k in ('failures', 'errors', 'skipped'))
    return result


def main():
    config = json.loads((OUT / 'config.json').read_text())
    rebuilt = (ROOT / 'src/smr/cells.py').read_text()
    for path, sha in config['origins'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha
        assert (ROOT / path).read_bytes() == original(path, config['baseline_commit'])
    for name, path in config['functions'].items():
        assert function_ast(rebuilt, name) == function_ast((ROOT / path).read_text(), name)
    assert not re.search(r'^from experiments|^import experiments', rebuilt, re.M)
    assert hashlib.sha256((OUT / 'lesson_source.txt').read_bytes()).hexdigest() == config['lesson_source_sha256']
    assert hashlib.sha256((OUT / 'lesson_source.txt').read_bytes().replace(b'\n', b'\r\n')).hexdigest() == config['lesson_source_original_sha256']

    protected = ['notes/01_definitions_v1_2.md', 'notes/design/grid_v1_2.json',
                 'notes/design/v1_2_protocol.md', 'notes/01_claim_boundary_v1_2.md',
                 'notes/00_research_brief_v1_2.md', 'notes/00_history.md',
                 'notes/meetings/2026-10-23_headsup.md', 'src/smr/design.py',
                 'src/smr/stationary_v2.py', 'notes/phases/PHASE_1_closeout.md',
                 'notes/phases/PHASE_2_closeout.md', 'notes/literature/prior_predictions.md']
    protected_hashes = {}
    for path in protected:
        data = (ROOT / path).read_bytes()
        assert data == original(path, config['baseline_commit']), path
        protected_hashes[path] = hashlib.sha256(data).hexdigest()
    for path in protected[:2]:
        assert (ROOT / path).read_bytes() == original(path, 'contract-v1.2'), path

    old_readme = original('README.md', config['baseline_commit']).decode()
    def relocate(match):
        link = match[1]
        return match[0] if '://' in link or link.startswith(('#', 'mailto:')) else '](' + '../' + link + ')'
    historical = re.sub(r'\]\(([^)]+)\)', relocate, old_readme)
    assert (ROOT / 'notes/00_progress_log.md').read_text().endswith(historical)

    for c in GRID['main']:
        new = main_cell(c, make_cell)
        assert new == main_cell(c, original_make_cell), c['id']
        assert all(str(new[k]) == str(c[k]) for k in ('yA', 'yB', 'h', 'H_coarse'))

    rows = []
    for cid in config['calibration_ids'] + config['control_ids']:
        c = calibration_or_control(cid)
        for which in config['queues']:
            for ref in config['refinements']:
                unit, mass, support, error = queue_D(c, which, ref)
                old_unit, old_mass, old_support, old_error = original_queue_D(c, which, ref)
                assert unit == old_unit and mass.shape == old_mass.shape
                diff = np.max(np.abs(mass - old_mass))
                mismatch = np.count_nonzero(support != old_support)
                norm = abs(mass.sum(dtype=np.longdouble) - 1)
                assert diff == 0 and mismatch == 0 and error == old_error
                assert norm < 1e-12 and error <= 1e-8
                rows.append(dict(cell=cid, queue=which, refinement=ref, dt_s=str(1 / (120 * ref)),
                                 unit_packet=str(unit), array_rows=len(mass), supported_states=int(support.sum()),
                                 old_total_mass=str(old_mass.sum(dtype=np.longdouble)),
                                 new_total_mass=str(mass.sum(dtype=np.longdouble)),
                                 max_abs_mass_difference=float(diff), support_mismatches=int(mismatch),
                                 normalization_residual=float(norm), old_D_error_bound=old_error,
                                 new_D_error_bound=error))
    with (OUT / 'D_comparison.csv').open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    invariant = queue_D(calibration_or_control('N01'), 'A', 1)[1]
    assert np.array_equal(invariant, np.array([[.5, .5]], dtype=np.longdouble))

    migration, full = pytest_result('migration_pytest.xml'), pytest_result('full_pytest.xml')
    result = dict(status='PASS', responsible='Doan Van Tai', date=config['date'],
                  evidence='migration verification only; not a hypothesis test',
                  baseline=config['baseline_tests'], migration_tests=migration, full_tests=full,
                  main_constructors_checked=len(GRID['main']), constructor_mismatches=0,
                  D_comparisons=len(rows), max_abs_mass_difference=max(r['max_abs_mass_difference'] for r in rows),
                  support_mismatches=sum(r['support_mismatches'] for r in rows),
                  max_normalization_residual=max(r['normalization_residual'] for r in rows),
                  max_old_D_error_bound=max(r['old_D_error_bound'] for r in rows),
                  max_new_D_error_bound=max(r['new_D_error_bound'] for r in rows),
                  N01_A_probability_at_q0=[.5, .5], function_AST_matches=len(config['functions']),
                  protected_files_sha256=protected_hashes, history_preserved=True,
                  V9='OPEN: not sent; A04 waits', P0_V10='OPEN: Phase 4 HOLD', L8='OPEN',
                  ownership='OPEN', lesson_understanding='not assessed',
                  A01='NOT RUN', A04='NOT RUN', A05_F='NOT FROZEN', A05_T='NOT RUN',
                  heldout_D_generated=0, new_grid_outcomes_computed=0, seed=None)
    report = f'''# L3.1 Part 3 — kết quả triển khai và kiểm chứng

Người phụ trách: **Doan Van Tai** · 27/10/2026. AI thực hiện theo lesson được cung cấp;
không ghi thay trải nghiệm tự học hoặc phản hồi của người thật.

## A. Đã thực hiện

- DL-044 có bốn dòng trạng thái: V9, người đọc, tự viết, provenance; làm rõ P0-V10
  đọc v1.2 và hai nghĩa V9. Giữ điều kiện V9(c); chưa gửi GVHD, A04 chờ.
- Tạo PHASE_3 từ phạm vi lesson, con trỏ README ≤15 dòng, experiment index và bảng
  Keep/Reference/Archive/Rebuild. Bản plan PHASE_3 v2.0 đầy đủ chưa có trong workspace;
  không nhận đã đối chiếu bảng gốc. Bổ sung reader packet 30–45 phút/sáu câu.
- Chuyển nguyên nội dung README cũ sang progress log, chỉ sửa đích link. History giữ nguyên.
- Rebuild lattice/law_for/queue_D/make_cell vào src/smr/cells.py; body bốn hàm khớp AST,
  ba file experiments gốc giữ nguyên byte. Module mới không import experiments.
- Contract D1–D25 và grid khớp nguyên byte tag contract-v1.2; claims, thresholds, closeouts,
  forecast, heads-up cũ và nhãn PC không đổi. Không đọc/tìm paper trong phiên này.

## B. Command và trạng thái thực chạy

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest tests/test_v1_2_cells.py -q --junitxml=results/lessons/l3_1/part3/migration_pytest.xml > results/lessons/l3_1/part3/migration_pytest.log 2>&1
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_1/part3/full_pytest.xml > results/lessons/l3_1/part3/full_pytest.log 2>&1
.venv/bin/python -m experiments.lessons.verify_l3_1_part3 > results/lessons/l3_1/part3/verification.log 2>&1
git diff --check
```

Baseline **202 PASS**, 26,46 s. Test migration **{migration['tests']} PASS**;
full regression **{full['tests']} PASS**; failures/errors/skips đều **0**.
Verification **PASS**; log và XML là output thực. Không chạy A01/A04/A05 hoặc simulation
outcome Phase 3. Các tests cũ có toy outcomes và design screen M31, không là experiment mới.
Kiểm whitespace trên bản lesson gốc ban đầu FAIL vì CRLF; snapshot lưu đã chuẩn hóa LF,
giữ SHA-256 gốc và kiểm tái tạo CRLF đúng byte. Kiểm cuối PASS.

## C. Số đo thực tế

Điều kiện: main-cell construction toàn bộ 38 ô; D trên M01/M09/M22/N01, queue A/B,
ref 1/2/4 (dt=1/120,1/240,1/480 s), age=1 s, capacity=10 packet/s.
Deterministic spectral law + finite propagation; không random seed/Monte Carlo/CI thống kê.

| Kiểm | Bản gốc | Bản Rebuild / so sánh |
|---|---|---|
| Main constructors | 38 | 38 khớp; 0 mismatch |
| D tách queue | {len(rows)} trường hợp | {len(rows)} khớp |
| Sai lệch probability lớn nhất | Reference | {result['max_abs_mass_difference']:.1f} |
| Support mismatch | Reference | {result['support_mismatches']} |
| Cận sai số D lớn nhất (probability) | {result['max_old_D_error_bound']:.8e} | {result['max_new_D_error_bound']:.8e} |
| Residual normalization lớn nhất | — | {result['max_normalization_residual']:.8e} |
| N01 A, q=0, mode OFF/ON | Analytic 1/2,1/2 | 1/2,1/2 |
| Tests toàn repo | 202 PASS trước đổi | {full['tests']} PASS sau đổi |

So sánh implementation với reference giữ nguyên là bằng chứng migration, không phải
validation độc lập toàn bộ plant. Invariant N01 bổ sung một kiểm analytic riêng.
Không có số baseline/new-method regret để báo: Part 3 không đo đại lượng nghiên cứu.

## D. File lưu

- Source: [cells.py](../../../../src/smr/cells.py), [tests](../../../../tests/test_v1_2_cells.py),
  [verification runner](../../../../experiments/lessons/verify_l3_1_part3.py).
- Điều kiện và index: [PHASE_3](../../../../notes/phases/PHASE_3.md),
  [DL-044](../../../../notes/02_decision_log.md#dl-044--mở-phase-3-điều-kiện-còn-mở-và-bản-hiện-hành-2026-10-27),
  [README](../../../../README.md), [index](../../../../notes/03_experiment_index.md),
  [progress log](../../../../notes/00_progress_log.md),
  [reader packet](../../../../notes/meetings/phase2_reader_packet.md),
  [exposure](../../../../notes/00_exposure_register.md).
- [Config và SHA nguồn](config.json), [lesson chuẩn hóa LF](lesson_source.txt),
  [số đo từng trường hợp](D_comparison.csv), [verification JSON](verification.json).
- Log: [baseline](baseline_pytest.log), [migration](migration_pytest.log),
  [full regression](full_pytest.log), [verification](verification.log).
- XML: [migration](migration_pytest.xml), [full](full_pytest.xml).
Không tạo biểu đồ, PDF, output A01/A04/A05, record buổi đọc hoặc xác nhận đã gửi GVHD.

## E. Kết luận và tự kiểm kỹ thuật

**Xác nhận:** con trỏ đúng phiên bản; four-function migration giữ nguyên behavior trên
miền đã kiểm; tests PASS. Chưa xác nhận engine L3.2 tích hợp, hypothesis/novelty,
Understanding của tác giả, V9, P0-V10 hoặc L8. Phase 4 vẫn HOLD.

Bốn câu tự kiểm được AI trả lời về kỹ thuật (không là tác giả tự làm): (1) εR đổi
nhãn, D13 đổi J/oracle/regret nên phải tính lại. (2) Bạn học giảm ER3 nhưng không
loại ER8 từ người định hướng đề tài. (3) Toy tests có thể nhất quán với plant sai;
cần kiểm D và con trỏ contract. (4) Lý do DL-038 đo ownership, card đo validity của
dự đoán trước outcome nên AI có thể hỗ trợ soạn card với provenance trung thực.

Bài tự chấm năm dòng: **chưa có lời tác giả**. Tác động nếu đổi đã phân tích: D13,
D20, D21 và luật chọn lưới cần tính/chọn lại; εR chủ yếu relabel và ghi post hoc.
Không tự kết luận tác giả bảo vệ được dòng nào. Tác giả vẫn cần viết lý do DL-038
và §1–2 closeouts; người thật vẫn cần đọc. Có thể học L3.2 ngay; trước A01 phải
commit L3.3, trước A04 cần record V9 theo điều kiện hiện có.
'''
    (OUT / 'report.md').write_text(report)
    docs = ['README.md', 'notes/00_progress_log.md', 'notes/03_experiment_index.md',
            'notes/phases/PHASE_3.md', 'notes/02_decision_log.md', 'notes/00_exposure_register.md',
            'notes/meetings/phase2_reader_packet.md', 'results/lessons/l3_1/part3/report.md']
    links = 0
    expected_outputs = {OUT / 'verification.json', OUT / 'verification.log'}
    for path in docs:
        doc = ROOT / path
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
            if '://' in link or link.startswith(('#', 'mailto:')):
                continue
            target = (doc.parent / unquote(link.split('#', 1)[0].strip('<>'))).resolve()
            assert target.exists() or target in expected_outputs, (path, link)
            links += 1
    result['local_links_checked'] = links
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    (OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
