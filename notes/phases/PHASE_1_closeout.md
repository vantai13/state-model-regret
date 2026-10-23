# Phase 1 Closeout — GO có điều kiện

> Ngày: 23/10/2026 · Người phụ trách: **Doan Van Tai** · Contract: `contract-v1.2` · Tag: `phase-1-closeout`
>
> **Provenance.** AI soạn theo yêu cầu thực hiện của tác giả. Theo PHASE_1 §21, hai mục đầu phải do tác giả tự viết; chúng còn trống. Bản HOLD trước đó (B4 rejected) xem trong lịch sử git của file này.

## What I understood

⟨Tác giả tự viết — chưa có.⟩

## What changed in my mental model

⟨Tác giả tự viết — chưa có.⟩

## Decisions made

| DL | Quyết định |
|---|---|
| DL-011 – DL-025 | L1.8 C–E: ngưỡng, $C_{\text{ref}}$, B2, R2, lưới v1, khóa `contract-v1` có điều kiện |
| DL-026 – DL-028 | Lưới v1 có 13 ô Stay áp đảo; điều kiện thiết kế ĐK1–ĐK8; HOLD theo nguồn gate |
| DL-029 – DL-031 | Mốc 2: một observation mỗi ô, idle-gap, A có mode ON/OFF |
| DL-032 – DL-037 | Phần A: solver phổ 20/20; lưới v1.1 8/22 → 11/22, bị từ chối |
| DL-038 | REFORMULATE hệ tọa độ lưới: neo theo ranh giới quyết định, horizon vật lý |
| DL-039 | Lưới v1.2 ACCEPTED: 38 ô chính, 12 held-out, calibration M01/M09/M22 |

## Evidence created

E0 và E1 trên một mô hình lý tưởng đã khai báo: ví dụ chuẩn sinh từ plant, các identity và bất biến (L1.2–L1.7), chứng chỉ prior dừng, engine idle-gap, và chẩn đoán thiết kế ($p_{\text{sw}}$, nhãn ĐK1, budget) cho lưới v1.2. 193/193 test đạt; sáu kiểm nhất quán đạt ([readiness](../../results/lessons/v1_2_readiness/readiness.json)). **Không có** network evidence; chưa tính contrast hay regret ở ô nào của lưới.

## Assumptions still open

- Plant lý tưởng: nền ngoại sinh, buffer vô hạn, action có hiệu lực ngay, A/B độc lập (AS1–AS9 của master plan). Kiểm ở Phase 7–8.
- dt cuối chưa chọn: A01 phải cho contrast ổn định khi làm mịn trên M01, M09, M22.
- Rủi ro nhất: so sánh "cùng độ khó" có thể che hiệu ứng của tải. Kiểm ở A04 bằng cách báo $\lambda_A$, $\psi$ và $p_{\text{sw}}$ thực cùng mọi contrast.

## Risks still open

| Risk | Lộ ra ở |
|---|---|
| Gain nhỏ hơn $\varepsilon_R$ ở mọi ô (kết quả hợp lệ, không phải lỗi thiết kế) | A04 |
| Threshold null giải thích hết pattern | A05, Phase 6 |
| P11 (EVPPI) đã trả lời phần chính của $G_{S\mid M_1}$ | Phase 2a |
| GVHD đổi objective, đơn vị hoặc hướng sau khi đã chạy | Khi gửi memo |
| Contrast không hội tụ trong budget khi làm mịn | A01 |

## What I am allowed / NOT allowed to claim

Xem [claim boundary v1.2](../01_claim_boundary_v1_2.md). Tóm tắt: chỉ các hệ quả E0 và chẩn đoán thiết kế trong mô hình đã khai báo. Không claim giá trị của $G_S$, $G_M$, $\Gamma$; không claim hiệu ứng riêng của một trục; không claim cho vùng A nặng hơn B; không claim về mạng thật, novelty hay khuyến nghị vận hành.

## Gate decision

| Điều kiện (PHASE_1 §17.1) | Trạng thái |
|---|---|
| V1 tay = code, golden set | AUTHOR-ATTESTED (không có artifact để kiểm độc lập); phía code có test |
| V2 negative controls | Đạt ở mức thiết kế: N01, N02 SD; N03, N04, P01 conservation. Contrast bằng 0 chính xác được kiểm ở A01 |
| V3 ví dụ chuẩn sinh từ plant, không suy biến | Đạt (L1.3) |
| V4 đặc tả $S_0$ | Đạt (D9, D10, D12) |
| V5 thời gian khai báo bằng giây, kiểm refinement | Đạt cho thiết kế: horizon vật lý, $p_{\text{sw}}$ ổn định tới dt/4. dt cuối ở A01 |
| V6 lưới khóa trước mọi contrast | Đạt: protocol `d696eef` trước lần chạy; không contrast nào được tính |
| V7 contract đầy đủ, nhất quán | Đạt: sáu kiểm PASS |
| V8 giải thích cho người thật | AUTHOR-ATTESTED |
| **V9 GVHD nhận heads-up và memo** | **Chưa đạt: chưa gửi** |
| P0-V3 read-back RQ | AUTHOR-ATTESTED |
| P0-V11 understanding artifacts | AUTHOR-ATTESTED |
| **P0-V10 người đọc độc lập** | **Chưa có: chặn Phase 4** |

**Quyết định của tác giả (23/10/2026): GO có điều kiện** sang Phase 3 (PHASE_1 §18). Outcome O1: contract khóa, lưới có quyết định thật ở mọi ô chính, có dt ứng viên khả thi.

Điều kiện:
1. **HOLD Phase 4** tới khi có người đọc độc lập (P0-V10).
2. Gửi heads-up và memo cho GVHD **trước A04**, để phản hồi về objective, đơn vị và hướng đến trước khi có kết quả.
3. Tác giả tự viết lại lý do của DL-038 và hai mục đầu của file này (PHASE_1 §5.4, luật 5). Viết lại câu chữ không đổi nội dung kỹ thuật thì không cần phiên bản mới.

## Next phase

Phase 3 bắt đầu bằng **A01** trên M01, M09, M22: chọn dt cuối và kiểm các ô kiểm âm cho sáu contrast bằng 0. Sau đó A04 trên 38 ô chính; A05 khóa $H_0/H_1$ trước khi chạm held-out R01–R12. Phase 2a (P11–P13) đọc song song, phải xong trước A05.
