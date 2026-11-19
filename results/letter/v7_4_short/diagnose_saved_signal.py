"""Doan Van Tai — saved-decision diagnosis only; no simulation or true costs."""
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent


def main():
    signal = json.loads((OUT/'signal.json').read_text())
    regimes = {}
    margins = {}
    for meta in signal['records']:
        counts = regimes.setdefault(meta['regime'], dict(positive=0, negative=0, zero=0,
            unique_side_h_instances=0, gap_min_Mbit_s=0., gap_max_Mbit_s=0.))
        path = OUT/'decision_records'/f"{meta['regime']}_{meta['date']}.npz"
        with np.load(path, allow_pickle=False) as raw:
            costs = np.stack([raw['M0_predicted_fresh'], *np.moveaxis(raw['M0_predicted_stale'], 1, 0)], axis=1)
            gap = costs[:, :, 1]-costs[:, :, 0]
            counts['positive'] += int((gap > 0).sum())
            counts['negative'] += int((gap < 0).sum())
            counts['zero'] += int((gap == 0).sum())
            counts['unique_side_h_instances'] += gap.size
            counts['gap_min_Mbit_s'] = min(counts['gap_min_Mbit_s'], float(gap.min()))
            counts['gap_max_Mbit_s'] = max(counts['gap_max_Mbit_s'], float(gap.max()))
            if meta['regime'] in ('DAY1', 'DAY2'):
                for name, rate in zip(('pooled', 'stable_only'), raw['s_hat_Mbit']):
                    corrected = gap + rate*raw['h_seconds']
                    for i, h in enumerate(raw['h_seconds']):
                        key = f'{name}|{int(h)}'
                        candidate = float(corrected[:, :, i].max())
                        margins[key] = max(margins.get(key, -float('inf')), candidate)
    primary = [x for x in signal['by_h'] if x['population'] == 'DAY1_DAY2']
    fresh_pooled = [x for x in primary if x['side'] == 'fresh' and x['variant'] == 'pooled']
    f1 = all(.01 <= x['disagree_share'] <= .06 for x in fresh_pooled)
    f3 = all(x['M0_ties_share'] >= .70 for x in fresh_pooled)
    pooled_total = sum(x['disagree'] for x in primary if x['variant'] == 'pooled')
    stable_total = sum(x['disagree'] for x in primary if x['variant'] == 'stable_only')
    result = dict(owner='Doan Van Tai', stage='POST_SIGNAL_SAVED_DATA_ONLY',
        signal_verdict=signal['signal_gate']['verdict'], no_simulator_calls=True,
        no_true_costs_or_C_ref=True, no_changed_criteria=True,
        sign_counts_by_regime=regimes, maximum_corrected_gap_primary_Mbit_s=margins,
        forecasts=dict(F1='HELD' if f1 else 'DID_NOT_HOLD', F2='NOT_TESTED_NO_TRUTH',
            F3='HELD' if f3 else 'DID_NOT_HOLD', F4='HELD' if stable_total > pooled_total else 'DID_NOT_HOLD'),
        explanation='For negative s_hat, Stationary chooses Switch. Hybrid differs exactly when predicted_gap + h*s_hat >= 0 (including the exact tie, which chooses Stay). Every observed predicted gap is <=0 and every s_hat is negative. Absolute gap exceeding h*abs(s_hat) is not sufficient: here the exceedances have the Switch-favoring sign.',
        scope='Observed finite panel and these frozen pipelines only; no general no-advantage, no empirical cost comparison, no H-P1 verdict.',
        improvements='No retuning, seed/horizon/stratum change, additional diagnostic simulations or truth. Only the predeclared stable-only sensitivity was checked; it also has zero disagreements.')
    with (OUT/'diagnosis.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
    lines = ['# V7-4: giải thích signal từ raw đã lưu', '', 'Người phụ trách: Doan Van Tai.', '',
        '**NOT_ENOUGH_SIGNAL: 0/37.120 bất đồng pooled và 0/37.120 stable-only ở DAY1/DAY2.**', '',
        'Phân tích sau bước 0, chỉ dùng decision/prediction đã lưu; không simulation, rollout đánh giá, C_ref hay regret.', '',
        'Đặt Δ̂ = chi phí M0 dự đoán của Switch trừ Stay. Với ŝ<0, Stationary chọn Switch;',
        'Hybrid khác Stationary khi Δ̂+hŝ≥0, kể cả tie vì tie chọn Stay. Trong toàn bộ panel đã tính,',
        'Δ̂≤0. Vì thế hai Hybrid đều chọn Switch ở cả fresh/stale, tất cả τ và h.', '',
        'Thống kê |Δ̂|>h|ŝ| không phải điều kiện đủ cho bất đồng. Các exceedance ở đây mang dấu âm,',
        'ủng hộ cùng action Switch. Đây là điểm thiếu trong lập luận khả thi dựa trên trị tuyệt đối của Claude,',
        'không phải bằng chứng rằng seed/horizon mới tạo được action signal.', '',
        '| Miền | Δ̂>0 | Δ̂<0 | Δ̂=0 | Tổng (fresh không lặp theo τ) |',
        '|---|---:|---:|---:|---:|']
    for regime, c in regimes.items():
        lines.append(f"| {regime} | {c['positive']} | {c['negative']} | {c['zero']} | {c['unique_side_h_instances']} |")
    lines += ['', 'DAY1/DAY2: các thống kê sau giống nhau ở cả 5 horizon (5,10,15,20,30 phút),',
        'hai variant pooled/stable-only; mỗi phía và horizon có mẫu số 3.712 khi gộp τ.', '',
        '| τ (s) | phía | n/h/variant | % bất đồng | % tie M0 | % tie Hybrid | % abs(Δ̂)>h abs(ŝ) |',
        '|---:|---|---:|---:|---:|---:|---:|']
    for row in signal['by_h_tau']:
        if row['population'] == 'DAY1_DAY2' and row['variant'] == 'pooled' and row['h_s'] == 300:
            lines.append(f"| {row['tau_s']} | {row['side']} | {row['denominator']} | " +
                ' | '.join(f"{100*row[k+'_share']:.6f}" for k in ('disagree','M0_ties','Hybrid_ties','abs_gap_gt_h_abs_s')) + ' |')
    lines += ['', 'Dự báo: F1 không đứng (fresh=0%); F3 đứng (tie M0 fresh≈86,37% ở mọi h);',
        'F4 không đứng (cả hai variant đều 0 bất đồng). F2 chưa kiểm vì không truth.', '',
        'Kiểm triển khai: regression h=1 giờ/seed V7-3 tái lập đúng decisions, tie flags và trạng thái;',
        'audit độc lập raw toàn bộ 87 record khớp signal. Không thay seed, grid, metric hoặc ngưỡng.', '',
        'Đây là kết luận về signal của panel hữu hạn. Không kết luận chung “không có lợi thế”;',
        'chưa tính C_ref nên chưa biết số case evaluable, chưa đo Δc, se hoặc regret.', '']
    with (OUT/'diagnosis.md').open('x') as f:
        f.write('\n'.join(lines))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
