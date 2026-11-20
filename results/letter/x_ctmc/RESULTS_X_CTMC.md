# X-CTMC (X1, X1b, X3): kết quả (Claude, 20/11/2026)

- **Người phụ trách:** Doan Van Tai. Claude thiết kế, viết thẻ và chấm theo ủy quyền toàn quyền; Codex code và pilot.
- **Không có:** mentor review, dự báo của tác giả.
- **Trạng thái chấm lại độc lập (Codex):** chờ Codex có quota lại; mục này sẽ được cập nhật.

## Quy trình
| Bước | Commit / tệp |
|---|---|
| Design và phụ lục A (namespace `x-ctmc-v1` trên `mmpp`, không bypass guard) | letter_smr `581e769`, `ad3db0d` |
| Thẻ nháp (test, ngưỡng, luật đưa vào paper) trước pilot | letter_smr `ad3db0d` |
| Code, pilot (4 regime, bị loại khỏi test), dự đoán seed train, lock, thẻ chính, lock thẻ | `1c1d38065` |
| Truth một lần, laptop 8 worker: 63/63 COMPLETED, 1048,9 s wall, 6531 CPU-s | raw `544925fcc` (commit trước khi chấm) |
| Chấm bằng scorer đã khóa (`x_ctmc_card.py`) | `card_verdicts.json` |
| Ledger letter tính lại độc lập từ raw (`v88_evidence.py`), khớp verdict | 4102 kiểm đạt |

## Verdict (thẻ khóa trước truth)
| Test | Kết quả | Verdict |
|---|---|---|
| T1: dấu harm của rule theo tải (TH_θ, MLU) dự đoán từ dữ liệu nhà mạng | 558/618 = 0,903 (38 regime; 34/38 đúng theo đa số) | **ĐỨNG** (sát ngưỡng 0,90) |
| T2: tầng disagree, law so với null không hàng đợi | 234/257 = 0,911 so với 116/257 = 0,451 | **ĐỨNG** |
| T3: độ dốc ở 100 T_int | sai số trung vị 0,268 > 0,25 | **KHÔNG ĐỨNG** |
| T4: dấu M0 trên lưới dị biệt | 136/146 = 0,932 | **ĐỨNG** |
| T5: Hybrid_hat ≤ 0,5% khi dấu ŝ đúng | 146/148 = 0,986 | **ĐỨNG** |
| T6: C5 dự đoán dấu harm M0 | 146/146 | **ĐỨNG** |
| T6b: rule stale tập trung hơn fresh | 146/146 | **ĐỨNG** |

## Mô tả
- **D1: số regime có harm** (G_S < −0,5% C_ref, 30 T_int, τ = T_int; trên 60 regime):
  - M0: 42 (trung vị −3,98%);
  - MLU: 31; TH_0,5: 32; TH_0,65: 30; TH_0,8: 19; TH_0,9: 5;
  - Hybrid, luật tĩnh và Pool: 0.
- **D2:** tie share trung vị: M0 0,14; các rule khác 0.
- **D3:** 12 ô dấu ŝ sai, regret both-side trung vị 4,17%.
- **D4: Hybrid_hat − Stationary_hat** ở 1–10 T_int, cả hai phía, 480 ô:
  - không ô nào tệ hơn quá 0,05 điểm;
  - tốt hơn ở 28/80 ô phía fresh tại 1 T_int, 18/80 tại 3 T_int, 8/80 tại 10 T_int;
  - lợi nhất 17,8 điểm.
- Estimator ŝ invalid ở 20/63 regime. Theo design, không dùng fallback, nên regime đó không có dự đoán vận hành và không có Hybrid_hat.

## Dự báo của Claude (ghi trước) và kết quả
| F | Dự báo | Kết quả |
|---|---|---|
| F1 | TH có harm ở ≥ 30% regime với θ ∈ {0,8; 0,9}, ít hơn với θ = 0,5 | **Sai hướng:** θ = 0,5 có harm nhiều nhất (32/60), θ = 0,9 ít nhất (5/60); θ = 0,8 đúng (19/60 = 32%) |
| F2 | T1 khoảng 0,9–0,95; tầng disagree thấp hơn agree | Mức đúng (0,903); **sai** phần tầng (disagree 0,911 > agree 0,898) |
| F3 | Null ≤ 0,5 ở tầng disagree | Đúng (0,451) |
| F4 | M0 có harm ở ≥ 50% regime | Đúng (42/60) |
| F5 | T5 sát ngưỡng | **Sai:** 0,986, cao hơn nhiều |
| F6 | T6, T6b đứng | Đúng |

## Phân tích nguyên nhân (post hoc, không đổi verdict)
- **T3:** tách sai số độ dốc ở 100 T_int trên 305 ô:

  | Thành phần | Sai số trung vị |
  |---|---|
  | s·ΔF chính xác (đồng nhất thức, h hữu hạn) | 1,1% |
  | s·ΔF̂ (share lấy mẫu) | 4,0% |
  | ŝ·ΔF chính xác | 28,8% |
  | khóa ŝ·ΔF̂ | 26,8% |

  Vậy sai số độ dốc đến từ **độ lớn** của ŝ ước lượng từ bản ghi 100 T_int. Luật theo horizon và phần lấy mẫu share đều chính xác. Dấu của ŝ thường đúng,
  nên T1 và T4 đứng.
- **F1 sai hướng:** θ thấp khiến rule chuyển ở cả mode thấp. Phía fresh phản ứng theo mode tức thời nên dễ chọn sai action dài hạn hơn. Phía stale gộp về
  mode trung bình. Đây là giải thích, chưa kiểm.
- **T6 = 146/146:** cơ chế C5 khớp ở mọi ô M0 eligible, trên lưới mới chưa thấy trước. Nhãn C5 nâng thành **"đứng có điều kiện"** (AI quyết theo ủy
  quyền): đứng trên CTMC dị biệt, chưa kiểm trên GÉANT.

## Giới hạn
- Các ô cùng regime, cùng τ và h không độc lập; T1 sát ngưỡng.
- Mô hình CTMC hai path cách điệu.
- Estimator invalid ở 20/63 regime.
- Pilot loại 4 regime nặng nhất; XCTMC_028 NOT_RUN theo cap chi phí.
- Sanity θ ≥ 1 XFAIL do lỗi viết design (không ảnh hưởng θ ≤ 0,9).

## Đưa vào paper (theo luật thẻ)
- T1, T2 đứng: V-A có câu mới; Intro nâng câu phân biệt; contribution 1.
- T3: con số 27% kèm phân tích post hoc.
- T4, T5: một câu lưới dị biệt.
- T6: câu "consistent with" về gộp quyết định.
- D1, D4: trong cùng đoạn.
