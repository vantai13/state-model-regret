# c_sw > 0 ở vùng harm — kết quả run01 (14/11/2026)

Doan Van Tai — **AI (Claude) thiết kế, khóa, chạy và chấm theo ủy quyền** ("tự thiết kế và kiểm tra… bằng chứng thật
mạnh"). Không mentor review, không dự đoán do tác giả viết. Exploration, G1.

## Trình tự (có thể kiểm bằng Git)

1. Thiết kế → panel → 720 dự đoán zero-fit → thẻ → lock. Tất cả commit `8e6a8f4a` **trước** truth.
2. Truth một lần (local, `env.sh`): 180/180 job COMPLETED, 7.595 CPU-s, 15,8 phút wall.
3. Kiểm MC định trước: 6/6 PASS, |z| tối đa 1,35.
4. Raw commit `6a87ce69` **trước** khi chấm. Sau đó mới chạy `score` dưới lock (hash khớp).

## 1. Chấm theo thẻ

| Mục | Ngưỡng | Kết quả | Verdict |
|---|---|---|---|
| Control | ≥ 90% job; F/z_∞ khớp; tỷ lệ Switch theo h khớp; MC | 180/180; sai khác 0,0; 0,0; 6/6 | PASS |
| **S1** độ chính xác tuyệt đối | \|G_S − z_pred1\| ≤ 0,1 pp ở ≥ 90% của 450 ô | **85,6%** (385/450) | **FAIL** |
| **S2** thắng null dùng truth | trung vị sai số luật ≤ 0,5 × null **và** luật gần hơn ≥ 80%, 288 ô | **0,0003 pp so với 1,31 pp**; luật gần hơn ở **288/288** | **PASS** |
| S3 đổi dấu | — | 0 ô, đúng như luật dự đoán trước | NOT_EVALUABLE |
| K7 (mô tả) | harm ở c = 0 còn hay mất khi c > 0 | mất ở 6,9% theo truth (luật: 8,1%); luật đúng trạng thái ở **98,8%** của 335 ô | — |

## 2. Đọc theo luật đã khai

- **S2 PASS (mạnh).** Có 288 ô mà luật bậc một dự đoán, chỉ từ M0, rằng c làm harm đổi ≥ 0,25 pp. Ở đó luật:
  - sai trung vị 0,0003 pp;
  - trong khi null được dùng truth ở c = 0 sai 1,31 pp;
  - gần hơn null ở **mọi** ô.

  Theo design §5: cơ chế "gộp quyết định + bias" dự đoán đúng, trước truth, cách một can thiệp mới thay đổi harm ở vùng harm.
- **S1 FAIL, theo đúng luật khóa.**
  - **Cả 65 ô trượt đều ở h = 3 T_int** (65/150). Sai số tương đối trung vị 3,6%, trên những harm lớn tới −23% Cref.
  - Ở 10 T_int và 30 T_int: **300/300** ô nằm trong 0,1 pp (sai tối đa 0,002 pp).
  - Ô c = 0 (không chấm) cũng trượt 17/90 ở 3 T_int. Chỗ yếu là tốc độ hội tụ của luật ở 3 T_int khi stake lớn, không phải c.
  - Dung sai tuyệt đối 0,1 pp thừa kế từ Stage F, nơi harm nhỏ, nên quá chặt cho vùng harm. Đây là lỗi chọn thước của AI. Không đổi sau khi chạy.
- **S3:** luật dự đoán 0 ô đổi dấu, nên không chấm được.

## 3. Sau khi chấm (mô tả, không đổi verdict)

**S2 theo h:**

| h | n | sai số trung vị: luật / null | luật gần hơn |
|---|---|---|---|
| 3 T_int | 81 | 0,18 / 1,10 pp | 81/81 |
| 10 T_int | 101 | 0,0005 / 1,34 pp | 101/101 |
| 30 T_int | 106 | 0,0000 / 1,37 pp | 106/106 |

**Hướng:**
- Luật dự đoán c làm harm **tăng** ở 119 ô; truth tăng ở đúng 119/119, tăng tối đa 9,3 pp.
- Luật dự đoán harm **giảm** ở 169 ô; truth giảm ở 169/169.

**Harm ở c = 0** có ở 24/30 regime mới (h ≥ 3 T_int).

## 4. Câu thay thế đề xuất cho THREATS K7 (tác giả quyết; file THREATS chưa sửa)

> Stage F (6 base trong dải giúp) cho thấy c_sw không *tạo* harm trong CTMC.
> Ở vùng harm (30 regime mới, c ≤ 4, h ≥ 3 T_int), c_sw **không** xóa harm: harm còn ở 93% ô có harm tại c = 0, và
> tăng ở 119/288 ô mà c có tác dụng.
> Luật bậc một zero-fit dự đoán đúng hướng ở 288/288 ô và đúng trạng thái còn/mất harm ở 98,8% ô.
> Độ chính xác tuyệt đối: ≤ 0,002 pp từ 10 T_int; ~4% tương đối ở 3 T_int.
> Claim C3 không còn bị giới hạn ở c_sw = 0 trong ctmc-v1, với c ≤ 4.

## 5. Giới hạn

- Chỉ ctmc-v1 (a = 6, τ = 1), c ≤ 4, 30 regime. Plant fluid chưa kiểm.
- Luật bậc một đã có (C1, T11). Đây là kiểm can thiệp mới và miền mới, không phải luật mới. Không novelty.
- AI thiết kế và tự chấm. Phần dự đoán là số máy tính, nhưng các lựa chọn panel, lưới c và luật chấm vẫn do AI.
- MC chỉ ở 6 ô (h = 3 T_int).

## 6. File

- `run01/`: `jobs/` (180), `mc.json`, `score.json`, `table.csv`, `environment.json` (lock), `done.json`.
- Log: `results/explore_ctmc/logs/csw_harm_run01.log`, `csw_harm_mc.log`.
