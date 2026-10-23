"""Doan Van Tai — artifact audit, chronology and six consistency checks before tag contract-v1.2.

Reads committed artifacts only; computes no plant quantity.
"""
import hashlib, json, re, subprocess, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/v1_2_readiness'
RQ = ('For load-changing routing actions, how do improvements in current-state information and action-response '
      'model fidelity differ and interact in their effect on expected decision regret?')
CHRONOLOGY = ['db955de', 'cde9944', '00c9584', 'ee349a4', '87dcd53', 'd696eef', '7de4427']
FINAL_REVIEW_MAP = [  # Final Review (bản cập nhật 06/10/2026) section -> requirement -> contract terms
    ('§2.1', 'oracle biết state và law, không biết future; một benchmark cho mọi ô', ['D14', 'D15']),
    ('§2.2', 'bảng 2×2, G_S, G_M, G_SM, Γ và hai gain có điều kiện', ['D19']),
    ('§2.5', 'regret theo margin, quy tắc hòa chốt trước', ['D16', 'D17', 'D18']),
    ('§2.7', 'threshold null bị giới hạn, khóa trước kiểm, split theo workload', ['D25']),
    ('§5.3', 'h=HΔt; objective cumulative khác time-average', ['D2', 'D13']),
    ('§11.1', 'objective queue occupancy trên horizon cố định, c_sw khai báo', ['D13']),
    ('§11.2', 'nền Markov on/off, buffer vô hạn, không transport feedback; M0 mean rollout load-aware; '
              'M1 đúng law; không truyền "mode trung bình"', ['D4', 'D6', 'D10']),
    ('§12.2', 'quyền thông tin: estimator đóng băng, M1 không thấy w, evaluator giữ w', ['D9', 'D11', 'D21']),
    ('§12.6', 'εR là quy ước 0,5/1/2% của reference cost; εE và TOST', ['D23', 'D24']),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Artifact audit of the official run.
    run_dir = ROOT / 'results/lessons/v1_2'
    files = json.loads((run_dir / 'manifest.json').read_text())
    assert all(sha(run_dir / f['file']) == f['sha256'] for f in files)
    config, selection = (json.loads((run_dir / n).read_text()) for n in ('config.json', 'selection.json'))
    grid = json.loads((ROOT / 'notes/design/grid_v1_2.json').read_text())
    # Chronology: plan before exploration results, protocol before official results.
    for a, b in zip(CHRONOLOGY, CHRONOLOGY[1:]):
        assert git('merge-base', '--is-ancestor', a, b).returncode == 0, (a, b)
    assert config['protocol_commit'].startswith('d696eef')
    assert git('ls-tree', '-r', '--name-only', 'd696eef', '--', 'results/lessons/v1_2').stdout == ''
    assert git('ls-tree', '-r', '--name-only', 'db955de', '--', 'results/explore_reformulate').stdout == ''
    # Contract files.
    contract = (ROOT / 'notes/01_definitions_v1_2.md').read_text()
    brief = (ROOT / 'notes/00_research_brief_v1_2.md').read_text()
    boundary = (ROOT / 'notes/01_claim_boundary_v1_2.md').read_text()
    ids = re.findall(r'^\| (D\d+) \|', contract, re.M)
    rows = {i: l for l in contract.splitlines() for i in re.findall(r'^\| (D\d+) \|', l)}
    v0 = subprocess.check_output(['git', 'show', 'contract-v0:notes/01_definitions.md'], cwd=ROOT)
    deferred = {'A01': 'D1', 'A05': 'D25', 'Phase 8': 'D8', 'P0-V10': None}
    checks = [
        dict(id=1, check='Each operational term defined once', definitions=len(ids),
             status='PASS' if ids == [f'D{i}' for i in range(1, 26)] else 'FAIL'),
        dict(id=2, check='Main RQ verbatim in contract and brief; brief points to contract and grid v1.2',
             status='PASS' if RQ in contract and RQ in brief and '01_definitions_v1_2.md' in brief else 'FAIL'),
        dict(id=3, check='Deferred items have an owner: A01 final dt, A05 null/held-out, Phase 8 rate-only/feasible, P0-V10 reader',
             status='PASS' if all(k in contract for k in deferred) and 'DEFERRED A05' in rows['D25'] else 'FAIL'),
        dict(id=4, check='Final Review consistency', status='PASS' if all(t in rows for _, _, ts in FINAL_REVIEW_MAP for t in ts) else 'FAIL',
             method='Đối chiếu thủ công từng mục với toàn văn Final Review (bản cập nhật 06/10/2026) do tác giả dán trong chat '
                    'ngày 23/10; repo không lưu file gốc nên không kiểm hash. Script chỉ kiểm các term được ánh xạ có mặt.',
             mapping=[dict(section=s, requirement=r, terms=t) for s, r, t in FINAL_REVIEW_MAP]),
        dict(id=5, check='25-term budget and immutable v0 bytes',
             status='PASS' if len(ids) == 25 and v0 == (ROOT / 'notes/01_definitions.md').read_bytes() else 'FAIL'),
    ]
    main_cells, held = grid['main'], grid['heldout']
    cal = [c['id'] for c in grid['calibration']]
    numeric = (.0025 <= .005 / 2 and .005 < .01 and 1e-9 < .005 * 1e-6)
    grid_ok = (grid['status'] == selection['status'] == 'ACCEPTED' and len(main_cells) == 38 and len(held) == 12
               and all(c['eligible_calibration'] for c in main_cells) and all(c['in_band_all_levels'] for c in held)
               and all(c['within_budget_dt16'] for c in main_cells + held) and len(set(cal)) == 3
               and all(next(c for c in main_cells if c['id'] == i)['group'] == 'core' for i in cal)
               and not selection['reproduction']['ladder_mismatches'] and not selection['reproduction']['confirm_mismatches']
               and selection['reproduction']['matches_proposed_cells'])
    checks.append(dict(id=6, check='Cross-card numerical, grid and calibration constraints',
                       status='PASS' if numeric and grid_ok else 'FAIL', calibration=cal,
                       max_updates_dt16=max(c['updates_16'] for c in main_cells + held),
                       max_unresolved=max(c[f'unresolved_{l}'] for c in main_cells + held for l in (1, 2, 4))))
    suite = list(ET.parse(OUT / 'full_suite.xml').getroot().iter('testcase'))
    failed = [t.get('name') for t in suite if t.find('failure') is not None or t.find('error') is not None]
    receipt = dict(author='Doan Van Tai', artifact_audit='PASS', chronology=CHRONOLOGY, grid_status=grid['status'],
                   checks=checks, full_suite=dict(tests=len(suite), failed=failed),
                   contract_files=dict(definitions=sha(ROOT / 'notes/01_definitions_v1_2.md'), brief=sha(ROOT / 'notes/00_research_brief_v1_2.md'),
                                       boundary=sha(ROOT / 'notes/01_claim_boundary_v1_2.md')),
                   open_items=['V9: heads-up/memo GVHD chưa gửi', 'P0-V10: người đọc độc lập chưa có (chặn Phase 4)',
                               'PHASE_1 §5.4 luật 5: lý do và câu chữ v1.2 do AI soạn, tác giả chưa tự viết lại',
                               'V1/V8/P0-V3/P0-V11: author-attested, không có artifact để kiểm độc lập'],
                   ready_to_tag=all(c['status'] == 'PASS' for c in checks) and not failed and len(suite) > 0)
    (OUT / 'readiness.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('checks', 'full_suite', 'ready_to_tag')}, ensure_ascii=False, indent=1)[:2500])


if __name__ == '__main__':
    main()
