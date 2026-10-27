"""Doan Van Tai — read-only A04 audit and report from recorded outcomes.

Created after the score checkpoint; not a preregistered prediction generator.
Never invokes grid/D/engine evaluation, changes card labels or opens held-out.
"""
import csv
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.A03_card.provenance import ROOT, CARD, metadata
from experiments.A03_card.grade_card import grade_main
from experiments.A03_card.grading import get, ratio, judge
from experiments.A04_discovery.provenance import verify, validate_run_inputs, require_score_commit, sha
from experiments.A01_null_refinement.run import write

OUT = ROOT / 'results/A04/20261027_01'
REPORT = ROOT / 'results/lessons/l3_5'


def read(p):
    return json.loads(Path(p).read_text())


def csv_rows(p):
    with Path(p).open() as f:
        return list(csv.DictReader(f))


def number(r, key):
    return float(F(str(r[key])))


def main():
    receipt = verify()
    hashes = validate_run_inputs(OUT)
    checkpoint = require_score_commit(OUT)
    data = read(OUT / 'grading_input.json')
    grades = read(OUT / 'card_scores.json')['grades']
    assert grade_main(metadata((ROOT / CARD).read_text()), data['fine'], data['coarse']) == grades
    prior_audit = read(ROOT / 'results/lessons/l3_4/artifact_audit.json')['sha256']
    assert all(sha(ROOT / p) == h for p, h in prior_audit.items())
    protected = read(REPORT / 'preflight/verification.json')['protected_sha256']
    assert all(sha(ROOT / p) == h for p, h in protected.items())
    independent = read(REPORT / 'independent_review.json')
    comparison = {}
    for cid, kind in (('M09', 'P2'), ('M17', 'P6')):
        a, b = independent['cells'][cid], grades[kind]['cells'][cid]
        comparison[cid] = a['final_label'] == b['verdict'] and a['dt_sensitive_label'] == b['sensitive_to_dt']
    assert all(comparison.values())
    assert all(sha(ROOT / p) == h for p, h in independent['inputs_sha256'].items())
    calibration_equal = []
    for cid in ('M01', 'M09', 'M22'):
        for m in (1, 2):
            previous = read(ROOT / f'results/A01/20261027_03/calibration_{cid}_m{m}.json')
            current = read(OUT / f'raw/{cid}_m{m}.json')['engine']
            assert previous == current, (cid, m)
            calibration_equal.append(f'{cid}/m{m}')
    raw = sorted((OUT / 'raw').glob('*.json'))
    expected = {f'{c}_m{m}.json' for c in [*[f'M{i:02}' for i in range(1, 39)],
                 'N01', 'N02', 'N03', 'N04', 'W01', 'S01', 'P01', 'P02'] for m in (1, 2)}
    assert {p.name for p in raw} == expected
    validity = read(OUT / 'validity_status.json')
    assert validity['status'] == 'PASS' and not validity['dt_flagged_cells']
    vrows = csv_rows(OUT / 'validity.csv')
    assert all(r['hard_pass'] == 'True' for r in vrows) and len(vrows) == 92
    primary = csv_rows(OUT / 'main_final.csv')
    controls = csv_rows(OUT / 'controls_final.csv')
    assert len(primary) == 38 and len(controls) == 8
    per = {r['cell']: r for r in primary}
    pattern_checks = csv_rows(OUT / 'pattern_checks.csv')
    assert len(pattern_checks) == 190
    pattern_results = {}
    for check in pattern_checks:
        pid, cid = check['pattern'], check['cell']
        r = per[cid]
        in_scope = {
            'D1': True, 'D2': r['kappa'] == '1' and r['h_s'] == '8',
            'D3': r['h_s'] == '2', 'D4': True,
            'D5': cid in ('M19', 'M20', 'M21', 'M22'),
        }[pid]
        assert (check['in_scope'] == 'True') == in_scope
        if not in_scope:
            assert check['status'] == 'OUT_OF_SCOPE'
            continue
        if pid == 'D5':
            assert check['status'] == 'NOMINAL_ZERO'
            assert all(F(r[k]) == 0 for k in ('G_S', 'F', 'V'))
        else:
            band = ratio(get(data['fine'][cid], check['metric']), get(data['fine'][cid], 'C_ref'))
            assert (str(band.lo), str(band.hi)) == (check['lower'], check['upper'])
            assert judge(band, check['relation'], check['threshold']) == check['status']
        pattern_results.setdefault(pid, []).append(check)
    assert len(pattern_results['D2']) == 16
    assert all(r['status'] == 'STANDS' for r in pattern_results['D2'])
    carry = read(OUT / 'carry_to_A05_F.json')
    card_meta = metadata((ROOT / CARD).read_text())
    assert carry['original_K5_rule_unchanged'] == card_meta['K5_rule']
    assert carry['original_P5_branches_unchanged'] == card_meta['predictions']['P5']
    assert carry['carry'] == grades['carry_to_A05_F']['carry']
    # Re-check independent review script unchanged, and all explicitly reported outputs exist.
    assert sha(REPORT / 'independent_review.py') == independent['script_sha256']
    figures = [OUT / 'figures' / (name + extension) for name in
               ('H1_decision_plane', 'H2_six_contrasts', 'H3_headroom') for extension in ('.png', '.pdf')]
    assert all(p.is_file() and p.stat().st_size > 0 for p in figures)
    audit = dict(status='PASS', responsible='Doan Van Tai', checked_utc=datetime.now(timezone.utc).isoformat(),
                 prereg_commit=receipt['prereg_commit'], receipt_commit=receipt['receipt_commit'], score_commit=checkpoint,
                 card_sha256=receipt['prediction_card_sha256'], inherited_source_hashes_checked=37,
                 A04_source_hashes_checked=len(receipt['source_sha256']), protected_files_checked=len(protected),
                 A01_artifact_hashes_checked=len(prior_audit), A04_output_hashes_checked=len(hashes),
                 score_replay_matches=True, independent_review_matches=comparison,
                 calibration_engine_records_equal_to_A01=calibration_equal,
                 raw_levels=92, controls_exact_zero_entries=60, WD_exact_zero_entries=6,
                 all_46_pairs_certified=True, full_suite_passed=348, new_A04_tests=12,
                 test_runtime_s=60.71, experiment_runtime_s=validity['wall_s'],
                 no_new_heldout_D_or_outcomes=True, pattern_checks=190, candidate_patterns_considered=5,
                 candidate_patterns_retained=1, figures=len(figures), registered_A04_or_inherited_source_changed_after_run=False,
                 compiler=subprocess.check_output(['g++', '--version'], text=True).splitlines()[0],
                 precision_scope='conditional numerical bounds, not independent proof or continuum limit')
    write(REPORT / 'verification.json', audit)
    summary = read(OUT / 'discovery_summary.json')
    cheap = read(OUT / 'cheap_kill.json')
    # Human-readable values are rounded for display; machine artifacts retain endpoints.
    lines = [
        '# L3.5 / A04 — kết quả và cách đọc', '',
        'Người phụ trách: **Doan Van Tai** · run27/10, tổng kết28/10/2026. **Hoàn tất kỹ thuật L3.5**;',
        'không tự nhận tác giả Understanding PASS hoặc đóng human-reader gates.', '',
        '**Kết luận chính:** engine/validity PASS; P5 đứng, P2/P3/P6 không đứng;',
        'không claim chưa phân giải. Đây là kết quả của card trên đúng danh sách,',
        'không xác nhận cơ chế hoặc hiệu quả trong mạng thật. Kết quả âm được giữ.', '',
        '## 1. Đã thực hiện và thứ tự bằng chứng', '',
        f'- Prereg/source/exposure commit `{receipt["prereg_commit"]}`.',
        f'- Receipt commit `{receipt["receipt_commit"]}`; nguồn A01/A03 không đổi.',
        '- Run `20261027_01`: 38main+8controls/probes×2 mức,92cell-levels mới.',
        '- Đọc validity trước, console chưa in contrast.',
        f'- Chấm card và commit `{checkpoint}` trước mở bảng/phân tích discovery.',
        '- Reviewer phiên AI mới kiểm tay M09/P2,M17/P6 mà chưa xem nhãn grader:2/2khớp.',
        '- Tạo ba hình (PNG+PDF), bảng headroom/route/margin, xét5patterns/giữ1candidate.',
        '- Sàng literature20records/2queries có mục tiêu;1đề xuất mới,0PDF/0note mới.',
        '- Không amend card, thay ô/ngưỡng/dt, promote engine vào src hoặc mở A05-T.', '',
        '## 2. Validity và độ chính xác', '',
        '| Kiểm | Kết quả | Giới hạn |', '|---|---:|---|',
        '| Full tests |348PASS,12test A04 mới|60.71s; không rerun11mutants lịch sử|',
        '| Cell-level |92/92BOUNDED,92hard checks PASS|38main+8controls×2mức|',
        '| Controls |60/60zero D19;6/6zero WD GS_M1|SD/conservation vàWD có scope khác|',
        '| Adjacent pairs |46/46đạt;0flag|dt1/120→1/240; không chứng minh dt→0|',
        f'| max e_num/Cref_lower |{100*validity["max_e_over_Cref_lower"]:.8f}%|cap.25%; M24/ref1|',
        f'| max unresolved mass |{100*validity["max_unresolved_mass"]:.8f}%|cap1%; M24/ref1,oracle/M0|',
        f'| max pair change upper/Cref_fine |{100*validity["max_pair_change_upper_ratio"]:.8f}%|cap.25%; M24|',
        f'| Thời gian A04 |{validity["wall_s"]:.6f}s|6worker; chưa bao gồm tests/plots/review|',
        '| Calibration replay |6/6engine records trùng A01|M01/M09/M22,ref1/ref2;tính mới|', '',
        'Primary dt=1/240s≈4.166667ms là **bước thời gian mô phỏng**, không phải packet delay.',
        'H giữ theo ô: h8→1920slot,h2→480slot ởref2. Exact finite-law expectation,',
        'long double64-bit mantissa, seed=None; không Monte Carlo/CI. Các enclosures',
        'có điều kiện theo input/kernel bounds; validity consistency không là formal proof.', '',
        '## 3. Chấm card [PREREG-CARD]', '',
        '| Prediction | Yêu cầu | Kết quả | Bằng chứng tại dt cuối |',
        '|---|---|---|---|',
        '| P2 |≥1% ở mọi M09–M12|**Không đứng**;2/4đứng|M09=.831493%,M10=.705873%;M11=1.495685%,M12=1.620398%|',
        '| P3 |Γ>.5% ở M19,M21|**Không đứng**;0/2đứng|.109601%,.126042%, upper vẫn dưới.5%|',
        '| P5-K |GM≤.5% ở mọi M19–M22|**Đứng**;4/4|0%,.074096%,0%,.025051%|',
        '| P5-Q |Ít nhất1ô M01–M04 GM≥1%|**Đứng**;2/4witness|M01=1.973020%,M03=2.396501%;M02/M04=0|',
        '| P5 tổng |K AND Q|**Đứng**|Hai vế đều đạt|',
        '| P6 |V>0 AND V>F ở M17,M18|**Không đứng**;0/2|V=-.402691/-2.548076 packet·s, cả haiV−F<0|', '',
        'Các số phần trăm chia Cref=L11 **của chính ô và dt**, không chia L00.',
        'Không dùng “2/4P2đứng” thay yêu cầu ALL. Không loại ô;0HOLD,0excluded.',
        'Các nhãn card không nhạy coarse/fine. Forecast A03 **không có cơ chế preregister**;',
        'không chấm “đúng con đường/sai con đường”, chỉ mô tả route bên dưới.',
        'Chi tiết khoảng có đủ trong [card_details.csv](../../A04/20261027_01/card_details.csv).', '',
        '## 4. Baseline và các repair, cùng đơn vị packet·s', '',
        'L00=hiện trạng;L01=model repair;L10=state repair;L11=joint repair/oracle trong mô hình.',
        'Cost thấp hơn là tốt hơn. Bảng chọn cả gain lớn và state-harm; toàn38ô ởCSV/phụ lục.', '',
        '| Ô |L00 baseline|L01 model|L10 state|L11 joint/Cref|GS|GM|GSM|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for cid in ('M01', 'M03', 'M18', 'M19', 'M20', 'M22', 'M28'):
        r = per[cid]
        lines.append('|'+cid+'|'+'|'.join(f'{number(r,k):.9f}' for k in ('L00','L01','L10','L11','G_S','G_M','G_SM'))+'|')
    lines += ['',
        '**Ví dụ M03:** baseline43.848902→joint41.147593, giảm2.701309packet·s',
        '(6.564927%Cref). Model riêng giảm.986102packet·s=2.396501%Cref.',
        'Không diễn giải6.564927%thành tỷ lệ giảm so baseline hoặc delay dài hạn.', '',
        '**Ví dụ M18:** state repair tăng cost1.864530packet·s (GS=-.558006%Cref).',
        'Joint repair vẫn giảm.902842packet·s=.270197%Cref. Γ=2.767372packet·s',
        '(.828203%Cref) lớn hơn headroom; đó là phục hồi harm trên nhánh state-only,',
        'không phải có thêm2.767372packet·s lợi ích khả thi từ baseline00.', '',
        '## 5. Điều tôi thấy [DISCOVERY]', '',
        '- GM>0 và action flip ở4ô M01,M03,M20,M22. ChỉM01/M03đạt1%;M20/M22',
        '  đổi quyết định nhưng margin nhỏ, vẫn equivalent_point ở.5%.34ô còn lạiGMnominal0.',
        '- 18/38ô GS≥1%;2ôGSâm làM18/M28;không ôGS≤−1%.',
        '- 22/38ô GSM≥1%;Gamma chỉ1ô≥1% (M07), không suy queue mechanism.',
        '- 16/38ô R00 upper<1%, nhưng **0/3miền cheap kill**: điều kiện là mọi ô',
        '  của miền đã đăng ký, không chia lại miền sau khi nhìn kết quả.',
        '- Tất cả số đếm practical/equivalent trong mô tả là point labels; card và',
        '  cheap kill dùng numeric intervals. Không tự đổi εR để tăng số ô đạt.', '',
        '| Miền cheap kill | Số ô | upper(R00/Cref)<1% | max upper | Kết luận |',
        '|---|---:|---:|---:|---|']
    for group, d in cheap.items():
        upper = 100*max(x['upper'] for x in d['cells'])
        lines.append(f'|{group}|{d["n"]}|{d["certified_below"]}|{upper:.6f}%|Không cheap-kill cả miền|')
    lines += ['',
        'Không cần DL NARROW do cheap kill vì không miền nào đáp ứng. R00 chặn',
        'GS/GM/GSM/GS_M1 và repair khả thi từ00; không chặn GM_S1/Gamma.', '',
        '## 6. Đọc ba hình và diagnostics', '',
        '[H1 mặt phẳng quyết định](../../A04/20261027_01/figures/H1_decision_plane.png):',
        'trục X=EΔ/Cref,trục Y=EΔhat/Cref (%). Khác dấu là action flip; ở tie0',
        'chọnStay. M01/M03nằm góc phải-dưới;M20/M22nằm trên trụcY=0 vớiX<0.',
        'Màuκ,markerqB,floor*,h2táchpanel. Các điểm sát0có nhãn chồng, traCSV',
        'để phân biệt. T01 giải thích regret từ flip và margin, chưa giải thích vật lý.', '',
        '[H2 sáu contrast](../../A04/20261027_01/figures/H2_six_contrasts.png):',
        'X=ô theo thứ tự thiết kế,Y=%Cref;dải xám±.5%,đường±1%.Ba nhóm táchpanel;',
        'không nối điểm, không đọc thành tác động riêngκ/η/quantile. Error bars',
        '=100e_num(G)/Cref dùng mẫu số điểm; interval của **tỉ số đầy đủ** traCSV/card.', '',
        '[H3 headroom](../../A04/20261027_01/figures/H3_headroom.png):',
        'X=ô theo ba miền,Y=R00/Cref,đường1%;một miền cần mọi upper dưới đường để',
        'cheap kill. Cột lỗi thường nhỏ hơn marker; luôn đọc bảng interval khi sátbiên.', '',
        'Margin table báo q50/q90/q99|Δ|,bias,|EΔ|,E|eM|,E|IΔ| vàF/V ở đủ38ô.',
        'Đây là stratification/diagnostics, không điều chỉnh nhân quả hoặc decomposition',
        'củaGamma thành “phần queue” và “phần geometry”. Flip-mass2D vẫn chưa tính.',
        'D22: F+V=GS dưới fixed-M0;V không là giá trị refresh backlog riêng. M17/M18',
        'cóVâm, bácforecastP6; không phải phát hiện rằng information có thể làm hại.',
        'R04 diagnostic GS=predicted_gain+δold−δnew có max residual0 trong arithmetic',
        'đã chạy; đây là bookkeeping dùng truecost, không feature hợp lệ cho A05.', '',
        '## 7. Candidate và prior', '',
        '**5 phát biểu đã xét,1giữ C1** — [hồ sơ đầy đủ](patterns.md).',
        'C1:κ=1,h8 có16/16ô quan sátGM=0; gợi ý kiểm equivalence ở tọa độ nội suy',
        'R05–R08. Không outcome held-out nào được dùng. Candidate là post-discovery,',
        'chưa freeze;λA/MT5/identity/design/precision/horizon đều được ghi giới hạn.',
        'C1 không là bằng chứng mechanism, không thay K5đã khóa trướcA04.',
        'D3 bịM38bác,D4bịM18/M28bác,D1/D5chỉ giữ mô tả. Không chọn lại miền/ngưỡng.',
        '[Tìm có mục tiêu](literature/screening_summary.md):20keywordrecords,1proposal',
        'networking mới,khôngPDF/note/catalog update,không saturation/novelty.', '',
        '## 8. Điều kết quả KHÔNG có nghĩa', '',
        'So sánh cùng độ khó không cùngλA;ψ∈[−.2,.05];near-boundary không theo tầnsuất;',
        'p_swthực vàfloorM11/M17/M18hiển thị;h2chỉκ=.3;ĐK1candidate vàcontrols riêng.',
        '**Kết quả định giá cửa sổ [t0,t0+h], không phải long-run loss.** D13 đã có',
        'dt·qH, không có xả sauh/terminal surcharge. Mọi kết luận phụ thuộcD(SR8),',
        'không samplingpopulation/networkdeployment/novelty. AI review không là GVHD.', '',
        '## 9. Exposure, carry và lesson gate', '',
        '38main+8controls/probes cảref1/ref2đã được tính và xem sau checkpoint chấm.',
        'A01đã lộ3calibration từ trước;A03card vẫn có trướcA01. Trong chuẩn bị đã',
        'hiện public held-out design λA/p_sw khi đọc bảngcũ; ghi thật trong exposure,',
        '**không** dùng làmfeature và **không** có D/J/gap-magnitude/regret/contrast',
        'held-out mới. Không blanket nói chưa thấy bất kỳ metadata held-out nào.', '',
        'K5rule duy nhất chưa bịbác nên **carry nguyên văn,m=1** sangA05-F, kể cả',
        'Q-witness chỉM01–M04. [Handoff](../../A04/20261027_01/carry_to_A05_F.json)',
        'không làA05freeze. C1post-discovery táchriêng;H0/H1/metric/budget/split cònchưa khóa.',
        'Track thực thiL3.6mở: đãnote/card/exposure;nhưng không tựchạyA05-T hoặcPhase4.',
        'L8/P0-V10/T05tựviết/Understanding tácgiả giữmở. MemoGVHD chưa gửi,V9waivedDL054.', '',
        '## 10. Lệnh đã chạy, artifacts', '',
        '```bash',
        '.venv/bin/python -m pytest tests/test_a04.py tests/test_card_grading.py tests/test_card_batch.py -q',
        '.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_5/preflight/full_suite.xml',
        '.venv/bin/python -m experiments.A04_discovery.run --run-id 20261027_01 --allow-grid --workers 6',
        '.venv/bin/python -m experiments.A04_discovery.score_card --run-dir results/A04/20261027_01',
        '# git commit score checkpoint7005a3b, trước hai lệnh tiếp:',
        '.venv/bin/python -m experiments.A04_discovery.discovery --run-dir results/A04/20261027_01',
        '.venv/bin/python -m experiments.A04_discovery.plots --run-dir results/A04/20261027_01',
        'python3 results/lessons/l3_5/independent_review.py',
        '.venv/bin/python -m experiments.lessons.report_l3_5',
        '```', '',
        'Toàn bộrun/raw/config/manifest/intervals: `results/A04/20261027_01/`.',
        'Source: `experiments/A04_discovery/`; tests:`tests/test_a04.py`.',
        'Log:`results/lessons/l3_5/A04_run01.console.log`,card_scoring.log,discovery.log,plots.log.',
        'Checks:`verification.json`,preflight/full_suite.log,independent_review.json/.md/.py.',
        'Sốliệu:`cells.csv`(92rows),main_final.csv(38),controls_final.csv(8),',
        'card_scores.csv,card_details.csv,cheap_kill.csv,margin_route_diagnostics.csv.',
        'Figures:H1/H2/H3PNG+PDF. Literature:rawqueries/screen.csv/search_log.',
        'Không cóMonteCarlo log/seed/CI hoặc held-out output vì không chạy những tác vụ đó.', '',
        '## Phụ lục — đủ38ô tại dt cuối (%Cref)', '',
        '|Ô|Nhóm|GS|GM|GSM|Gamma|GS_M1|GM_S1|', '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in primary:
        lines.append('|'+r['cell']+'|'+r['group']+'|'+'|'.join(f'{number(r,g+"_pct_Cref"):.6f}' for g in
                     ('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1'))+'|')
    (REPORT / 'report.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
