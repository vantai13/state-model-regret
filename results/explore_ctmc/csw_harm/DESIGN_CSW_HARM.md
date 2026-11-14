# Thiết kế: switching cost c_sw > 0 ở vùng harm — phép thử zero-fit của cơ chế "gộp quyết định + bias"

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** ("tự thiết kế và kiểm tra thí nghiệm giúp tôi… bằng chứng thật mạnh",
14/11/2026). Exploration trên ctmc-v1 (a = 6, μ = 10, τ = 1). Không phải thẻ tác giả, không mentor review, không đổi
RQ/contract/PC/Gate/G1. File này viết trước panel, dự đoán và mọi truth của
[csw_harm.py](../../../experiments/explore_ctmc/csw_harm.py).

## 1. Vì sao chọn thí nghiệm này

- **Lấp chỗ trống K7.** Stage F chỉ đặt c > 0 lên 6 base trong dải giúp. Câu THREATS K7 "harm biến mất khi c > 0" chưa từng được kiểm ở nơi có harm (review 14/11; [MECHANISM_IDELTA_CE.md](../../../notes/synthesis/MECHANISM_IDELTA_CE.md) §4).
- **Kiểm cơ chế M4 bằng một can thiệp mới.** Dạng định lượng của "gộp quyết định + bias" ở h dài là luật bậc một (C1, T11):

  z_pred1(c, h) = 100·[h·s·(F_old(c) − F_new(c)) + B(c)] / [h·r_min + β_C(c)]

  - F_old, F_new: tỷ lệ Switch của M0 trên state cũ và mới, với c tính trong quyết định.
  - B: phần bị chặn.
  - Mọi đại lượng chỉ từ M0 và phân phối dừng (`ctmc.evaluate_m0`). Không chạm truth.

  Cơ chế nói rằng c chỉ dời ngưỡng của M0. Truth ở h dài gần như không đổi vì h·s áp đảo c, nên harm phải đi theo đúng đường z_pred1(c) mà M0 vạch ra.

## 2. Vì sao đây là bằng chứng mạnh (thiết kế chống tự lừa)

1. **Dự đoán là con số do code tính, không phải ngưỡng do AI chọn.** Mỗi ô (regime, c, h) có một z_pred1. File dự đoán được ghi một lần, hash, và **commit vào Git trước khi có bất kỳ truth nào**.
2. **Dung sai thừa kế** từ thẻ đã khóa trước: 0,1 pp và 90% (F-R1/L72-2); 0,25 pp (F-R2). Không chọn mới.
3. **Hai đối thủ có dự đoán khác:**
   - **K7 nghĩa đen:** c > 0 xóa harm.
   - **Null thực nghiệm:** G_S(c, h) = G_S(0, h). Null này được *dùng truth* ở c = 0, nên mạnh hơn mọi baseline zero-fit.

   Luật phải thắng null đúng ở những ô mà nó dự đoán c có tác dụng.
4. **Dự đoán đổi dấu.** Những ô mà luật dự đoán harm ↔ help khi tăng c là dự đoán mới, dễ sai nhất.
5. **Panel mới:** seed 20261141 (bản đầu dùng seed 20261117; seed đó trùng chuỗi Sobol của các panel trước nên đã bỏ trước mọi dự đoán; file `discarded_seed20261117_*`), chỉ vùng harm (neg: x ∈ [−1,5; −0,1]; pos: x ∈ [0,4; 1,5]), 0 trùng với mọi case list cũ.
6. **Kiểm truth độc lập** bằng Monte Carlo (V3 có thêm c) trên 6 ô chọn bằng luật cố định trước truth.
7. Một run, không chạy lại, không đổi ngưỡng sau khi chạy. Raw được commit trước khi chấm.

## 3. Panel và lưới

- 30 regime (neg 15, pos 15), cùng miền và cách Sobol như I_Δ vòng 3.
- Bộ lọc chi phí: N ≤ 2500 mỗi path.
- c ∈ {0; 1/4; 1/2; 1; 2; 4} packet·s; h ∈ {1; 3; 10; 30} × T_int_max.
- Luật chỉ được chấm từ h ≥ 3 T_int (AS-R1). Hàng h = T_int chỉ để mô tả.
- **Một sửa đổi được phép, trước khóa, chỉ dựa trên số zero-fit:** nếu S2 có ít hơn 10 ô, thêm c ∈ {8; 16} một lần và ghi lại.

## 4. Chấm

Phạm vi: các ô h ≥ 3 T_int và c > 0.

| ID | Câu hỏi | Ngưỡng |
|---|---|---|
| **S1** | Luật zero-fit đúng tới 0,1 pp | \|G_S − z_pred1\| ≤ 0,1 pp ở ≥ 90% ô |
| **S2** | Luật thắng null thực nghiệm ở nơi nó nói c có tác dụng (\|z_pred1(c) − z_pred1(0)\| ≥ 0,25) | trung vị sai số của luật ≤ 0,5 × của null **và** luật gần hơn ở ≥ 80% ô; cần ≥ 10 ô |
| **S3** | Dự đoán đổi dấu so với c = 0 (cả hai \|z_pred1\| ≥ 0,25, khác dấu) | dấu truth trùng dấu luật ở ≥ 90%; cần ≥ 5 ô |
| K7 | Ở ô có harm tại c = 0, harm còn hay mất | mô tả: tỷ lệ mất harm theo truth và theo luật, theo từng c |

**Control (một control fail thì mọi verdict INCONCLUSIVE):**
- ≥ 90% job COMPLETED.
- F_old/F_new ở h = ∞ và z_∞ trong file dự đoán khớp với lần chạy truth ≤ 1e−9.
- Tỷ lệ Switch của M0 ở từng h khớp ≤ 1e−9.
- MC: \|z\| ≤ 3,5 cho G_S và M ở 6 ô.

## 5. Cách đọc

| Kết quả | Nghĩa |
|---|---|
| S1 và S2 PASS | Cơ chế M4 dự đoán đúng, trước khi thấy truth, cách một can thiệp mới thay đổi harm ở vùng harm. Bằng chứng định lượng mạnh nhất hiện có cho M4 trong ctmc-v1 |
| S1 PASS, S2 FAIL | Luật đúng, nhưng c gần như không tác dụng: không phân biệt được với null |
| S1 FAIL | Luật bậc một không chuyển sang vùng harm khi có c: M4 phải co phạm vi |
| S3 | PASS: đổi dấu đến đúng chỗ luật nói. FAIL: đổi dấu do thứ luật bỏ qua |
| K7 | Câu thay cho THREATS K7, *đề xuất*, tác giả quyết |

## 6. Không nhận

- Chỉ ctmc-v1; chưa có plant fluid.
- Luật bậc một đã có từ L7.1 (C1); đây là kiểm phạm vi mới và can thiệp mới, không phải luật mới.
- Không novelty: re-solving và CE dưới bias có prior (R01/R02/R04, R34, CEH23).
- AI soạn và tự chấm, nhưng dự đoán là số máy tính trước truth.
