# Gate 3R — NARROW · 30/10/2026 · DL-102

> Người phụ trách: **Doan Van Tai**. Provenance:
> - AI (Claude) soạn và chọn nhãn **theo ủy quyền** ("bạn hãy mở ra và đống lesson cho tôi đi đây là yêu cầu"), theo
>   khuyến nghị lesson L3R.8 (DL-097–102).
> - Tác giả xác nhận **ngoài vở** đã tự đọc card/contract và tự viết phần closeout của mình
>   ([author-attested](../../results/lessons/l3r_8/author_attestation.json), DL-032); nội dung đó không lưu trong repo.
> - Ba bảng dựng từ bằng chứng trong repo; AI tự kiểm hash, thứ tự commit và số đếm
>   ([freeze_check.json](../../results/lessons/l3r_8/freeze_check.json)).
> - Review của AI không tính là đọc độc lập (rủi ro ER3); P0-V10 còn mở.

## Claim gắn kèm

> Phase 4 kiểm Hyp-MV và Hyp-SH (card v2, sha `60335b61…`) trên 270 regime CF, ở **mức mô hình** (plant fluid đã
> khai báo trong contract §6). Không claim realism hay vận hành. S1 là benchmark có quyền oracle (biết mode).
> D22 chuyển sang Phase 5 (DL-097, `contract-v1.3-amend1`).

**Lý do** (AI soạn theo ủy quyền):
- Hai primary vẫn đứng và đã đóng băng trước dữ liệu CF; engine đạt verification có giới hạn; thiết kế phân biệt
  được trong ngân sách (n = 60).
- Realism UNSOURCED nên **miền claim thu hẹp về mức mô hình**; không claim mạng thực hay vận hành.
- Không phải GO, vì không vùng primary nào IN/EDGE ở bối cảnh nào.
- Không phải HOLD, vì phần còn thiếu (runner, P0-V10) là điều kiện vào Phase 4, không phải lỗi validity.

## Validity (V3R-1…V3R-10)

| ID | Đề xuất | Bằng chứng / giới hạn |
|---|---|---|
| V3R-1 Discovery đóng băng | PASS | Tag `explore-v13-pilot` → `a7435e9`; [discovery record](PHASE_3R_discovery_record.md); errata. Regime map: tag `explore-v13-regime-map` → `574a36f` (local, Bước 4) |
| V3R-2 Engine | **PASS có giới hạn** | L3R.3: 467 test, 12 mutant bị bắt, 19 lần tái lập, MC độc lập C1 80/80, C2 80/80, C3 8/8 ([report](../../results/lessons/l3r_3/report.md)). Engine native ở (640, 4) đạt R1 trên 118 ca calibration, gồm X2065/X1008/X1009; anchor pilot PASS; zero-action và identical-model ra 0 chính xác ([dry-run B](../../results/lessons/l3r_7/lean_close/dry_run_B.json)). **Conservation: không áp dụng dưới P1** (mọi regime có nguyên tử tại q = 0; thay bằng identical-model). Giới hạn: chênh lệch làm mịn là chẩn đoán, không phải cận được chứng nhận; **chưa chạy MC độc lập trên engine native ở (640, 4)**. **L3R.3 đóng có phạm vi card v2 (DL-101)** |
| V3R-3 Chính sách số | PASS | Contract R1–R8; [receipt numerics lean](numerics_v1_3_1_lean.lock.json); leo thang R3 trong `frame_v2.label_with_escalation` |
| V3R-4 Contract | PASS | Tag `contract-v1.3` → `3d2359b`; mục D22 theo DL-097, tag `contract-v1.3-amend1` |
| V3R-5 Realism | PASS về quy trình | Envelope `6bef959` có trước nhãn `1164500` (đã kiểm ancestry). **Outcome: UNSOURCED**, nằm ở bảng outcome, không phải lỗi validity |
| V3R-6 Card | PASS | 9/9 kiểm cho cả v1 ([checks](../../results/lessons/l3r_6/card_checks.json)) và v2 ([checks](../../results/lessons/l3r_7/lean_close/card_v2_checks.json)); forking log |
| V3R-7 Thiết kế | PASS | Root commit trước khi rút; 0 outcome CF; power; control; scorer có test; dry-run B. Runner là điều kiện vào Phase 4 (mục cuối) |
| V3R-8 Thứ tự commit | PASS | Ancestry: card v1 `1414d92` → card v2 `b62f329` → numerics `5d20cb8` → seed `ef6ca77` → prereg `16cfa60` → CF `7173d70` |
| V3R-9 Exposure | PASS | Register `38bc6d0`; inventory v3 có 1396 khóa. **G2:** trước khi rút đã có 24 khóa trong MV-ii và 45 trong SH-ii (card vẫn ghi Ω⁻ là "ngoại suy") |
| V3R-10 Provenance | PASS | Header từng file; `author_predicted: false` ghi trung thực |

## Điều kiện quy trình (tác giả tự đặt; báo riêng)

| Điều kiện | Trạng thái |
|---|---|
| Tác giả tự đọc card (Bước 1) | **Author-attested ngoài vở** (30/10); câu trả lời không lưu trong repo |
| P0-V10 người đọc độc lập | **OPEN** (DL-099): lần gọi CF đầu tiên chờ người đọc (a) hoặc DL miễn do tác giả (b) |
| V9 heads-up GVHD | WAIVED (DL-054) |
| L8 người đọc prior boundary | Dời sang Phase 8 (DL-100) |
| Closeout tự viết | **Author-attested ngoài vở**; nội dung không lưu trong repo |
| MASTER PLAN X.3 #2 | Engine giữ ở `experiments/`, cố định bằng hash; không cần promote để chạy Phase 4 |

## Outcome của Phase 3R

| ID | Kết quả |
|---|---|
| O1 Engine | Không có bug engine nào được xác nhận trong phạm vi đã audit; có giới hạn (V3R-2) |
| O2 Realism | Toàn bộ UNSOURCED, khác OUT |
| O3 Claim còn lại | 2 primary (MV, SH); Γ chỉ là diagnostic; MI chuyển Phase 5 |
| O4 Thiết kế | n = 60, BND = 15, dự toán 45,4 CPU-giờ ≤ 48. P(PASS) ≈ 0,836 nếu p⁺ = 0,7, p⁻ = 0,2; ≈ 0,256 nếu p⁺ = 0,6 (bảng power, chưa tính UNRESOLVED) |
| O5 Tín hiệu | Giữ nguyên; không có bug nào buộc chạy lại pilot |

## Hash đã đóng băng (đã kiểm ở máy local; bản đầy đủ trong freeze_check)

| Artifact | Giá trị |
|---|---|
| `contract-v1.3` | commit `3d2359b` (lock 21 file) |
| `numerics-v1.3.1-lean` | commit `5d20cb8` (receipt 15 file) |
| Card v2 | sha `60335b61…`, lock sha `4998f66a…` (12 file); card v1 lock 10 file, nguyên byte |
| `cf_prereg.json` | sha `966b476c…`, commit `16cfa60` |
| `regimes_cf.json` | sha `b1003a0f…`, 270 dòng, commit `7173d70`, chỉ attempt01 |
| Scorer / adapter / frame | `verdict.py` `f777cadb…` · `score.py` `5140a002…` · `frame_v2.py` `106da7cb…` |
| Inventory v3 | `085d41bc…` |

**Giới hạn của đóng băng.**
- Hash chứng minh nội dung không đổi; ancestry chứng minh thứ tự. Giờ ghi trên commit thì không chứng minh được gì.
- Git **không** chứng minh rằng không ai đã thử root khác ở ngoài repo. Phần đó dựa vào log cấp seed
  (`seed_allocation.json`, OS CSPRNG) và sự trung thực của người làm.

**Exposure cần biết.**
- Ω⁻ đã có điểm lộ trước khi rút: MV-ii 24 khóa (17 calibration, 4 regime map, 3 lưới 1/100); SH-ii 45 khóa
  (35 calibration, 10 lưới 1/100).
- Có 8 regime chạy thử trong phiên AI, đã thấy số nhưng không lưu file; cả 8 nằm ngoài vùng card.
- Các regime CF vẫn là điểm mới: 0 trùng chính xác, 0 lần rút lại.

## Điều kiện vào Phase 4 (không thuộc Gate 3R)

1. **Runner (Bước 0 của Phase 4).**
   - Đọc `regimes_cf.json`; với mỗi regime tính (640, 4) cùng hai láng giềng (320, 4) và (640, 2).
   - Leo thang R3; gắn nhãn bằng `frame_v2.label_with_escalation`; chấm bằng `verdict.py`.
   - Chỉ in tiến độ, không in giá trị; ghi một lần; chạy tiếp được nếu bị ngắt; từ chối chạy nếu hash lệch.
   - Kiểm trước trên 4 góc dry-run B, phải trùng **chính xác** `dry_run_B.json`. Commit và hash runner trước lần gọi CF
     đầu tiên.
2. Kiểm hash mọi file đã đóng băng ngay lúc bắt đầu.
3. Chạy control và anchor trước; sai thì dừng theo chính sách deviation.
4. D22: Phase 5 (DL-097). **P0-V10 OPEN (DL-099):** lần gọi CF đầu tiên chờ P0-V10.

## Phase 3R cho phép nói gì

**Được nói:**
- Engine population tính estimand v1.3 đúng trong phạm vi các kiểm đã làm, kèm giới hạn (chênh lệch làm mịn là chẩn
  đoán).
- Hai prediction đã được đóng băng (có hash) trước mọi dữ liệu CF.
- Pilot và regime map là discovery.

**Không được nói:**
- bất kỳ hypothesis nào đúng;
- tần suất ngoài đời thực;
- "telemetry tươi có hại";
- complementarity như một phát hiện riêng;
- kết quả bền với switching cost;
- novelty;
- G2;
- "Ω⁻ là ngoại suy hoàn toàn chưa thấy";
- "tác giả dự đoán" cho phần do AI soạn.
