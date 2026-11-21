"""Doan Van Tai — render preparation measurements, without scientific scoring."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(p):
    return json.loads(p.read_text())


def fraction(n, d):
    return 'NA' if not d else f'{n}/{d} = {100*n/d:.6f}%'


def run():
    audit = read(OUT / 'preparation_audit.json')
    workspace = read(OUT / 'workspace_audit.json')
    assert all(v['status'] == 'PASS' for v in audit['arms'].values())
    assert workspace['status'] == 'PASS'
    configs = {arm: read(OUT / f'arm_{arm}/configuration.json') for arm in ('A', 'B')}
    lines = ['# X5c — báo cáo chuẩn bị', '', 'Người phụ trách: **Doan Van Tai**.', '',
        'Triển khai và đo theo DESIGN_X5C_ALARM.md, CARD_X5C.md và T1–T4 nguyên từ CARD_X5.md.',
        'Không commit, push hoặc SSH. Không chạy experiment truth/score. Công việc triển khai không phải tác giả tự viết/đọc.', '',
        'M=512, N≤32, MIN_ALARMS=8, K=64, R_dec=64, R_eval=128. Cùng 60 test-S regime/day của X4b.',
        'h=300/600/900/1200/1800/3600/7200 s; stale ages=300/900 s; dt=0,05 s.',
        'Các mẫu chia sẻ ngày, instance và h; các mẫu số không phải số thử nghiệm độc lập.', '',
        '## Slope và link cảnh báo', '',
        '| Nhánh | Regime | η | ŝ pooled train (Mbit) | Luật tĩnh | Link index / tên | Ngưỡng (Mbit) |',
        '|---|---|---:|---:|---|---|---:|']
    for arm, c in configs.items():
        for info in c['regimes']:
            lines.append(f"| {arm} | {info['id']} | {c['parameters']['beta']} | {c['s_hat_pooled_Mbit'][info['id']]:.12f} | {info['alarm_action']} | {info['alarm_link_index']} / {info['alarm_link']} | {info['alarm_threshold_Mbit']:.12f} |")
    lines += ['', 'Nhánh A nhập nguyên ŝ X4b. Nhánh B gọi đúng B.train_record trên đủ 26 weekday × 3 regime, gồm S và O,',
        'N32 và 6 h rollout, seed train 7200005, namespace X5C-B|regime|date. Pool daily slopes với trọng số đều.',
        'train/summary.json đã được đóng và hash trước khi mở test plan hoặc test TMs.', '',
        '## Đo theo nhánh']
    compact = {}
    for arm, config in configs.items():
        out = OUT / f'arm_{arm}'
        s = read(out / 'step0/summary.json')
        train = read(out / 'train/summary.json') if (out / 'train/summary.json').exists() else None
        pilot = read(out / 'pilot/summary.json') if (out / 'pilot/summary.json').exists() else None
        by_regime = []
        lines += ['', f'### Nhánh {arm}: {s["gate"]["verdict"]}', '',
            f"Seed test {config['parameters']['test_seed']}, pilot {config['parameters']['pilot_seed']}; namespace X5C-{arm}|regime|date.", '',
            '| Regime | Cảnh báo / ứng viên | ALARM_RARE / bản ghi | Không RARE | Instance dùng quyết định |',
            '|---|---:|---:|---:|---:|']
        for info in config['regimes']:
            rs = [m for m in s['records'] if m['regime'] == info['id']]
            num, den = sum(m['alarms'] for m in rs), sum(m['candidates'] for m in rs)
            rare = sum(m['status'] == 'ALARM_RARE' for m in rs)
            selected = sum(m['N'] for m in rs if m['status'] != 'ALARM_RARE')
            row = dict(regime=info['id'], alarms=num, candidates=den, rare=rare,
                records=len(rs), nonrare=len(rs)-rare, selected=selected)
            by_regime.append(row)
            lines.append(f"| {info['id']} | {fraction(num,den)} | {rare}/{len(rs)} | {len(rs)-rare} | {selected} |")
        lines += [f"| Tổng | {fraction(s['alarms'],s['alarm_candidates'])} | {s['alarm_rare_records']}/60 | {60-s['alarm_rare_records']} | {s['selected_instances']} |", '',
            '**Share bất đồng Hybrid ≠ Stationary theo regime × h × side:**', '',
            '| Regime | h (s) | Fresh | Stale 300 | Stale 900 |', '|---|---:|---:|---:|---:|']
        for info in config['regimes']:
            for h in config['parameters']['h_seconds']:
                vals = []
                for side in ('fresh', 'stale_300', 'stale_900'):
                    row = next((r for r in s['disagreement'] if (r['regime'],r['h_s'],r['side']) == (info['id'],h,side)), None)
                    vals.append('NA' if row is None else fraction(row['numerator'],row['denominator']))
                lines.append(f"| {info['id']} | {h} | " + ' | '.join(vals) + ' |')
        lines += ['', '**Share tie M0 tươi:**', '', '| h (s) | NEWB1 | NEWB2 | NEWB3 |', '|---:|---:|---:|---:|']
        for h in config['parameters']['h_seconds']:
            vals = []
            for regime in ('NEWB1','NEWB2','NEWB3'):
                row = next((r for r in s['M0_fresh_ties'] if (r['regime'],r['h_s']) == (regime,h)), None)
                vals.append('NA' if row is None else fraction(row['numerator'],row['denominator']))
            lines.append(f'| {h} | ' + ' | '.join(vals) + ' |')
        t = s['M0_fresh_tie_pooled']
        lines += ['', f"Tie gộp: **{fraction(t['numerator'],t['denominator'])}**, fresh một lần cho mỗi instance × h, không lặp theo stale age.",
            f"Step0: {s['CPU_s_records']:.9f} CPU-s cộng qua các bản ghi; {s['wall_s']:.9f} wall-s.",
            f"Preflight step0: {read(out/'step0/preflight.json')['projected_wall_s']:.6f} wall-s với 8 worker (ước lượng, không guarantee/CI)."]
        if train:
            lines += [f"Train B: {train['CPU_s_records']:.9f} CPU-s, {train['wall_s']:.9f} wall-s; 78/78 bản ghi."]
        if pilot:
            lines += [f"Pilot: {pilot['CPU_s_records']:.9f} CPU-s cho hai bản ghi; mean {pilot['mean_CPU_s']:.9f}, max {pilot['max_CPU_s']:.9f} CPU-s/bản ghi.",
                f"Dự phóng truth {pilot['actual_truth_eligible_records']} bản ghi: {pilot['projected_CPU_hours']:.9f} CPU-h theo mean, {pilot['projected_max_pilot_CPU_hours']:.9f} CPU-h theo max; ideal 30-worker wall {pilot['ideal_wall_hours_30_workers']:.9f} h.",
                'Ngoại suy tuyến tính từ hai pilot local; chưa đo GCP, không CI/guarantee; không chấm card trên pilot.']
        elif s['gate']['verdict'] == 'NOT_ENOUGH_SIGNAL':
            lines += ['Pilot **NOT_RUN** theo cổng; CPU pilot và dự phóng truth **NA**; không tạo lock.']
        else:
            lines += ['Pilot chưa có summary hoàn chỉnh; xem pilot/preflight.json hoặc runtime_stop.json. Chưa tạo lock.']
        lines += ['Truth/score **NOT_RUN**; T1–T4 chưa được xác nhận bằng truth. Không tạo raw truth/card_verdicts.json/REPORT_X5C.md.']
        compact[arm] = dict(gate=s['gate'], by_regime=by_regime, alarms=s['alarms'],
            candidates=s['alarm_candidates'], rare=s['alarm_rare_records'], ties=t,
            disagreement=s['disagreement'], slopes=config['s_hat_pooled_Mbit'],
            CPU_s_step0=s['CPU_s_records'], wall_s_step0=s['wall_s'],
            pilot=pilot, train_CPU_s=train['CPU_s_records'] if train else None)
    lines += ['', '## Kiểm chứng và lỗi đã giữ', '',
        '- 158/158 PASS ở lượt đầu (8,98 s); bổ sung kiểm mean/warmup: 159/159 PASS (6,76 s).',
        '- Configure B lần đầu FAIL trước simulator vì parent arm_B chưa tồn tại. Không có train outcome/test B; giữ configure_B.log.',
        '- Chỉ sửa mkdir(parents=True) trong module mới; snapshot source_at_arm_A_step0.py giữ source A. Không rerun A.',
        '- Regression sau sửa: **160/160 PASS, 7,35 s**; thêm test tạo parent trước first worker.',
        '- Audit độc lập không import experiment/scorer: ' + '; '.join(f"{a}: {v['records']} records, {v['candidate_queues_checked']} candidate queues, {v['decision_and_tie_values_checked']} decision/tie values, {v['train_records_checked']} train records" for a,v in audit['arms'].items()) + '.',
        '- Audit A kiểm snapshot đúng SHA lúc bắt đầu và chứng minh source hiện hành khác đúng một dòng mkdir. B kiểm source hiện hành đúng SHA.',
        f"- SHA-256 **{workspace['preexisting_files_checked']} file có sẵn PASS**, không sửa/xóa; HEAD giữ nguyên {workspace['HEAD_after']}.",
        '- bash -n PASS. Shell harness dùng stub kiểm A/B chạy nối tiếp, log riêng, A lỗi không chặn B và poweroff đúng một lần cuối; không gọi cloud/poweroff thật.', '',
        'Lệnh chính (đã source .venv/bin/activate và experiments/explore_ctmc/env.sh, đặt PYTHONDONTWRITEBYTECODE=1, TMPDIR/MPLCONFIGDIR trong build):', '', '```bash',
        'python3 -m pytest -q -p no:cacheprovider --basetemp=results/letter/x5c_alarm/pytest_parent_fix tests/test_x5c_alarm.py tests/test_x5_alarm.py tests/test_x4b.py tests/test_x4b_card.py tests/test_x4b_truth.py',
        'bash -n experiments/letter/x5c_gcp.sh',
        'python3 -m experiments.letter.x5c_alarm configure --arm A',
        'python3 -m experiments.letter.x5c_alarm step0 --arm A --workers 8',
        'python3 -m experiments.letter.x5c_alarm configure --arm B --workers 8',
        'python3 -m experiments.letter.x5c_alarm step0 --arm B --workers 8',
        'python3 results/letter/x5c_alarm/audit_preparation.py', '```', '',
        '## Những chỗ phải chọn vì brief chưa chỉ rõ', '',
        '1. Dùng trực tiếp x5_alarm_card; không cần x5c_card riêng. T1–T4 và các quy ước X5 được áp riêng từng nhánh: SE qua ngày ddof=1, tie fresh không lặp theo stale, T3 mean daily percentages, T4 một regime/day cần cả fresh và hai stale ages đạt.',
        '2. ŝ=0 chọn Stay theo nhánh “ngược lại” trong brief. Alarm threshold dùng capacity của đúng link đã chọn, không capacity đồng nhất.',
        '3. Train B dùng 8 worker local, cùng giới hạn step0. Preflight tái dùng record có input-work proxy cao nhất, không rerun record đầu; thứ tự deterministic theo work/regime/date. Slope là mean đều 26 ngày.',
        '4. Pilot, nếu cổng qua, chọn hai record theo work proxy đầu vào và screen bằng pilot seed; không chọn theo regret. Dự phóng local trước pilot từ phép đo X4b, rồi kiểm lại bằng pilot thứ nhất trước bản ghi thứ hai.',
        '5. Lock là content lock chưa commit. Brief snapshot nguyên byte giúp verify trên GCP; nguồn gốc và hash brief vẫn lưu. Không coi lock là quyền tự chạy truth.',
        '6. ARMS="A B" chạy hai nhánh độc lập nối tiếp. Nhánh lỗi giữ exit code và log, nhánh kia vẫn được verify/run; chỉ poweroff sau nhánh cuối. Script chưa được thực thi với engine thật.', '',
        '## File', '',
        '- Source mới: experiments/letter/x5c_alarm.py; experiments/letter/x5c_gcp.sh; tests/test_x5c_alarm.py.',
        '- Cấu hình và số liệu mỗi nhánh: arm_A/ hoặc arm_B/: configuration.json; step0/summary.json, alarms.csv, disagreement.csv, M0_fresh_ties.csv, preflight.json, test/*.npz và *.json.',
        '- Train B: arm_B/train/summary.json, preflight.json, started.json, training_rates/*.npz và *.json.',
        '- Audit: audit_preparation.py, preparation_audit.json, arm_A_audit.json, preexisting_inventory.json, workspace_audit.json; rà η: BETA_AUDIT.md.',
        '- Log: configure_A.log, step0_A.log, configure_B.log (FAIL), configure_B_parent_fix.log, step0_B.log, pytest_initial.log, pytest_regression.log, pytest_parent_fix.log, preparation_audit.log.',
        '- Báo cáo này: PREPARATION_REPORT.md; số gọn: measured_summary.json. Không tạo biểu đồ.', '',
        '## Kết luận', '',
        'Đã kiểm implementation, runtime η, selection, train/test order và cổng bằng dữ liệu lưu thật. Kết quả cổng mỗi nhánh giữ nguyên; không đổi seed, threshold, regime hoặc h để cứu tín hiệu.',
        'T1–T4, regret thực nghiệm và hiệu quả correction chưa được xác nhận khi chưa có truth/score. Các ngày test vốn đã exposed từ X4b; X5c không phải dữ liệu traffic mới.']
    with (OUT / 'PREPARATION_REPORT.md').open('x') as f:
        f.write('\n'.join(lines) + '\n')
    with (OUT / 'measured_summary.json').open('x') as f:
        json.dump(compact, f, indent=2, sort_keys=True)
        f.write('\n')


if __name__ == '__main__':
    run()
