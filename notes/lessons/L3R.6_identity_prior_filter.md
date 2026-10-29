# L3R.6 — Lọc identity, lọc prior và phân suất

Người phụ trách: **Doan Van Tai** · 29/10/2026 · DL-073. AI (Claude) soạn theo yêu cầu
triển khai lesson L3R.6 Part1–3; tác giả chọn phân suất/vùng/gói luật qua
[trả lời nguyên văn](../../results/lessons/l3r_6/author_choices.json). Không phải bài tác giả tự
viết hoặc read-back; Understanding OPEN. Số dưới đây là **discovery** (pilot tag `a7435e9`,
Stage1+2, c_sw=0, 162 cấu hình phân biệt), không phải evidence.

## 1. Kiểm kê và nhãn identity (lesson Part1 §8–9)

| # | Tín hiệu discovery | Nhãn | Lý do / nguồn |
|---|---|---|---|
| S1 | ḠM≥0 mọi regime | **Identity** | T07 S08 (true shared posterior, AS11) |
| S2 | ḠM≥1% chỉ ở λB=8 (20 cấu hình), max 13,41% X2065 | Có thể sai | Không identity nào buộc độ lớn/vị trí |
| S3 | Harm ḠS≤−1%: 77/162 (λB6/7/8: 36/21/20) | Có thể sai | Dấu ḠS không bị ràng buộc (S14 chỉ chặn \|ḠS\|≤σ̄) |
| S4 | 14 cấu hình có cả harm và ḠM≥1% | Mô tả | Giao của S2/S3 |
| S5 | 50/77 harm có \|ḠM\|,\|ḠSM\|<.05% | Có thể sai; gợi ý “lỗi bù trừ” | ḠS≈−ḠM\|S1 khi L00≈L01≈L11 |
| S6 | \|Γ̄\|≥1% chỉ khi ḠS<0 | Nửa đầu **hệ quả identity** (S12); nửa sau bị kẹp | Mục 2 |
| S7 | ḠS\|M1 max 1,753%, trung vị .1455% | Có thể sai | Chặn trên Γ̄ ngoài harm |
| S8 | min Γ̄=−.137% chỉ khi c_sw>0 | Có thể sai | Stage3, ngoài primary |
| S9 | Chỉ báo M0 Spearman .75 | **Không dùng** | N3: code không có tại tag; MI → Phase5 làm null |
| S10 | Step1: lens biên FAIL; ứng viên hậu nghiệm | Ứng viên chưa kiểm | DL-063 |

## 2. Γ bị kẹp — đính chính cận dưới

Từ T07 S11: Γ̄=ḠS|M1−ḠS=ḠM|S1−ḠM, và ḠS|M1,ḠM|S1≥0 (S07). Suy ra hai cận cùng lúc:

- Γ̄≥−ḠS và Γ̄≥−ḠM, tức **Γ̄≥−min(ḠS,ḠM)**; ngoài harm còn Γ̄≤ḠS|M1.
- Trong harm (ḠS<0): Γ̄≥\|ḠS\|>0 (S12), không thể sai.
- Substitution vượt ε_E (Γ̄<−.5%) **đòi cả ḠS>.5% và ḠM>.5%**. Lesson Part1 §9.2 chỉ ghi
  −ḠM≤Γ̄, nên ước “substitution có thể tới khoảng −13%” là quá rộng: nó còn bị ḠS chặn.
- Khi đã biết ḠS và ḠS\|M1, Γ̄ được **xác định** (S11). Bài tự kiểm 3 của Part1
  (ḠS=.1%, ḠS\|M1=.2%) cho Γ̄=.1% chính xác, không phải khoảng [−5%;.2%].

Discovery có log ([#19](../../results/lessons/l3r_6/forking_paths.jsonl)): Γ̄≥−.5% ở
162/162; ḠS≥0 ở 73; min(ḠS,ḠM)>.5% chỉ **3/162**; vì vậy 70/73 cấu hình ḠS≥0 đạt
“không substitution” do identity. Trong hộp MV+A chỉ 3/16 có ḠS≥0 và 1/16 có thông tin.
Card Γ theo lesson Part2/3 (lọc ḠS≥0, π₀=.8, N_min=30) gần như chỉ chấm đại số; lọc theo
vùng có thông tin thì N quá nhỏ để PASS. Đây là lý do kỹ thuật được trình cho tác giả.

## 3. Lọc prior và tính hiển nhiên (lesson Part1 §10)

| Ứng viên | Prior gần nhất (note Phase2) | Đã biết | Khác ở trục | Rủi ro hiển nhiên | Xử lý |
|---|---|---|---|---|---|
| MV | P11 §2.4 Eq2.7–2.8 (EVMI); P12 (value equivalence), AIS22; P13 (transient/horizon) | Giá trị cải thiện model; model không cần đúng toàn bộ dynamics | E: regret P1 với observation cũ, cùng posterior; M: mean rollout từng state vs expected cost thật, cùngθ; R: rerouting đổi tải | Cao nếu chỉ nói “B gần bão hòa” | Đối chứng giữ λB=8, lật κ |
| SH | K-RM1 (R02 §5 Ex1), K-RM3 (R04 Def2–5), toy V1 [information_harm](../literature/information_harm.md) | Harm do thông tin với policy xấp xỉ | M: lộ backlog+mode dưới M0 cố định; E/R như trên | Thấp–trung bình | Chỉ claim ở đâu/bao nhiêu; ánh xạ tới điều kiện R04 là suy luận của lesson, **chưa kiểm** |
| Γ (không substitution) | WM26 2×2 với oracle tương lai thật | Thứ tự ưu tiên repair; không thấy E−C−S+P | E: oracle không thấu thị | Thấp | Không cấp suất (mục 2) |
| MI | Threshold/margin, P04/M00 | Hình học quyết định | Gần như không khác | Trung bình–cao | Phase5, vai null |

Không có phiên tìm/đọc paper mới trong L3R.6; mọi dòng prior dựa note Phase2 hiện có.
Không suy novelty, không đổi nhãn PC/Gate.

## 4. Phân suất đã chọn

**Phương án D** (Part1 §11): Hyp-MV primary 1, Hyp-SH primary 2, **không secondary**. Γ̄,
ḠS\|M1, ḠM\|S1, ḠSM, D22 F̄/V̄, P(flip), %stakes là diagnostic khai trước. Hệ quả: chữ
“interact” chỉ được mô tả; claim boundary phải nói rõ. Câu cơ chế MV tách **nguồn** (clipping
tại biên rỗng, MASTER PLAN F9, cấu trúc của plant fluid tuyến tính khi không chạm rỗng) khỏi
**điều dự báo độ lớn** (chưa rõ; ứng viên hậu nghiệm Step1, chưa kiểm).
