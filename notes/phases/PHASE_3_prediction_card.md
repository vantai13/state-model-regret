# Phase 3 — Prediction card (A03)

Người phụ trách: **Doan Van Tai** · 27/10/2026 · contract-v1.2 · grid_v1_2.json.
Trạng thái: **FROZEN — snapshot A03 v1, trước mọi lần chạy A01**.

<!-- A03_METADATA
{
  "card_id": "A03",
  "version": 1,
  "status": "FROZEN",
  "responsible": "Doan Van Tai",
  "date": "2026-10-27",
  "contract": "contract-v1.2",
  "already_implied_readback": "AUTHOR_ATTESTED",
  "engine_readback": "AUTHOR_ATTESTED",
  "author_attestation_sha256": "9bfe297e7c2e0ed7c10cce677ad892fd75838c75575eb01c9baedb484c93e965",
  "claims_sha256": "1041245560213f74e3988f05baea69a6c1033bec9239d96cab5e9af0181dd9d3",
  "grid_sha256": "7f7552f82926276ad9258a7b917832d29cfa3eba1d82dfdce636881838a21a56",
  "K5_rule_key": "K5_kge2",
  "adopted_rule_count": 1,
  "optional_P2_P3_rules_adopted": false,
  "mechanism_provenance": "FORECAST_WITHOUT_MECHANISM",
  "reviewer": "AI self-check in same session; not independent human review",
  "predictions": {
    "P2": {
      "source": "PC2",
      "ids": [
        "M09",
        "M10",
        "M11",
        "M12"
      ],
      "metric": "(L01-L10)/Cref",
      "relation": ">=",
      "threshold": "1/100",
      "quantifier": "all"
    },
    "P3": {
      "source": "PC3",
      "ids": [
        "M19",
        "M21"
      ],
      "metric": "Gamma/Cref",
      "relation": ">",
      "threshold": "1/200",
      "quantifier": "all"
    },
    "P5": {
      "source": "PC5",
      "K_ids": [
        "M19",
        "M20",
        "M21",
        "M22"
      ],
      "Q_ids": [
        "M01",
        "M02",
        "M03",
        "M04"
      ],
      "K_relation": "<=",
      "K_threshold": "1/200",
      "K_quantifier": "all",
      "Q_relation": ">=",
      "Q_threshold": "1/100",
      "Q_quantifier": "any"
    },
    "P6": {
      "source": "PC6",
      "ids": [
        "M17",
        "M18"
      ],
      "metric": "V>0 AND V>F",
      "quantifier": "all"
    }
  },
  "K5_rule": {
    "kappa_min": "2",
    "alphaA": "9/10",
    "alphaB": "9/10",
    "h_s": "8",
    "eta": [
      "1/2",
      "3/4"
    ],
    "targets": [
      "3/10",
      "7/10"
    ],
    "main": [
      "M19",
      "M20",
      "M21",
      "M22"
    ],
    "heldout": [
      "R03",
      "R04"
    ],
    "carry": "all non-refuted rules, including unresolved; unchanged into A05-F",
    "Q_witness_scope": "M01-M04 only; no new heldout Q claim"
  }
}
-->

Trạng thái exposure: chưa có J, margin, **độ lớn gap**, contrast hoặc regret của
bất kỳ ô grid nào trong các artifact/record hiện có. Dấu gap đã được dùng trong
p_sw screen để dựng lưới từ Phase1: không ghi “chưa thấy gap” theo nghĩa phủ nhận
exposure sign đó. Không xác nhận hoạt động ngoài repo/máy chưa được kiểm.
Phiên L3.3: chỉ toy và membership tọa độ; không dựng D hoặc tính outcome grid mới.
Regression có D-only và screen M31 cũ đã exposed, được ghi riêng trong register.

AI tham gia: giữ/trích forecasts AI-assisted đã exposed ngày24/10, gom sanity,
viết luật chấm và code; tác giả chọn hai mức K5 và author-attested hai read-back.
Không có cơ chế do tác giả viết. Mọi P là **forecast không cơ chế**, không tự gán
con đường A/B/i/ii/iii/a/b. Điều này là lựa chọn được phép ở Lesson Part3 §5.2.
Đứng về contrast không được dùng làm evidence cho một cơ chế chưa preregister.

Quy tắc sửa: không amend/rebase/force qua freeze commit. Không sửa các phần đã
khóa. Chỉ được thêm ở mục cuối với exposure và hash mới, không chấm phần bổ sung
như dự đoán trước dữ liệu. Full-file SHA thay đổi thì grader/guard dừng; phải đọc
lại blob freeze để chấm bản v1 và ghi amendment riêng, không âm thầm đổi receipt v1.

## 1. Danh sách sanity — KHÔNG phải prediction

| # | Câu và điều kiện | Nguồn E0 / nơi kiểm |
|---|---|---|
| 1 | R11=0; L11≤Lsm với cùng true oracle | D15/D18; A01/A04 |
| 2 | GSM, GSgivenM1, GMgivenS1, GM≥0 khi b=D và M1 đúng | D9/D19; A01/A04 |
| 3 | GSgivenM1=min(EΔ+,EΔ−)=EVPPI(x given y) | T01/T03; PC1 framing, không contribution |
| 4 | GMgivenS1=E_D[VSS(x)] dưới G2–G5 | T03; PC1 framing |
| 5 | GM=abs(EΔ)·1[a00≠a01]≤abs(bias) | T01; A01/A04 |
| 6 | Γ=GSgivenM1−GS=GMgivenS1−GM | D19; identity báo cáo |
| 7 | F+V=GS | D22 fixed-M0; identity báo cáo |
| 8 | Sáu contrast=0 ở SD/conservation đã chứng nhận cho cả model | D16, contract§8/DL-030; A01/A04 |
| 9 | GSgivenM1=0 ở WD; GM có thể >0 nên WD không là zero control | T01; A01/A04 |
| 10 | Jhat_M0≤J theo Jensen, cùng conditional mean/fixed state | T05; A01/A04 |
| 11 | Regret=abs(Δ)·1[action khác oracle], kể cả tie Stay | F5; A01/A04 |
| 12 | E[I_delta]=0 với b=D và shared belief | L1.5; diagnostic, không tự chứng nhận estimator |
| 13 | GS<0 ⇒ Γ>0 là đại số, không discovery | D19 + dòng2; A04 |
| 14 | GMgivenS1≤E abs(e_M), e_M=Δhat−Δ | L3.3 Part2§7.2/F5; A01/A04 |

Dòng6/7 là bookkeeping. Verification cần bất đẳng thức có thể bị bug phá và đường
kiểm chéo độc lập. Không nhận EVPPI/VSS, generic2×2, fidelity≠decision-quality,
information-harm hay model sufficiency là mới; áp claim boundary Phase2/DL-043.

## 2. Luật chấm khóa trước outcome

- Mọi metric dùng enclosure do engine trả, e_num **thực**, không thay bằng budget.
  Không gọi numeric enclosure là CI. Phải báo số STANDS/DOES_NOT_STAND/UNRESOLVED
  và EXCLUDED_ZERO_REFERENCE cho từng vế, không chỉ nhãn gộp.
- Với G∈[gL,gU], Cref∈[cL,cU], cL>0: lấy min/max của **bốn** thương gL/cL,
  gL/cU, gU/cL, gU/cU. Công thức hai endpoint trong lesson chỉ an toàn với dấu phù hợp;
  ví dụ [-2,-1]/[1,2]=[-2,-1/2], không phải [-1,-1]. Đây là sửa enclosure, không đổi contract.
- Với `≤`: đứng nếu upper≤threshold; không đứng nếu lower>threshold. Với `≥`:
  đứng nếu lower≥threshold; không đứng nếu upper<threshold. Với `<`/`>` dùng strict
  ở phía đứng và closed ở phía bác. Còn lại chưa phân giải.
- Cref đúng bằng0: giữ absolute output, loại relative label theo D23. Cref interval
  cắt0: chưa phân giải. Không loại ô khỏi denominators mà không báo. Nếu tất cả ô
  bị loại hoặc miền rỗng: không được gọi prediction đứng.
- Gộp Kleene: “mọi ô” đứng khi tất cả đứng, sai khi có counterexample chắc chắn;
  “ít nhất một ô” đứng khi có witness chắc chắn, sai khi tất cả sai. Còn lại unknown.
  Ô excluded tương đương unknown trong phép gộp, vẫn đếm riêng. PC5 chấm K, Q, rồi AND.
- HOLD_PRECISION, budget chưa đạt, hoặc bất kỳ unresolved mass oracle/M0/D22>0.01:
  ô chưa phân giải. Cref của chính ô, chính refinement phải bằng L11 cùng row/context.
- Cặp adjacent (2·dt_final,dt_final) phải certify D1 trên **sáu contrast D19**:
  abs-difference interval nằm trọn trong 0.0025·Cref_fine (dùng lower Cref để certify),
  không đổi dấu ngoài vùng ±0.005 của Cref ở mỗi mức. Không certify được ⇒ chưa phân giải.
  Trong dung sai: chấm tại dt_final; nếu nhãn coarse/fine khác nhau, gắn “nhạy với dt”.
  Không tự chọn mức có nhãn thuận lợi. Check này không chứng minh giới hạn dt→0.
- P2 dùng trực tiếp (L01−L10)/Cref để triệt tiêu L00 trước propagation sai số.
  PC6 tách V>0 và V−F>0 rồi AND, không cần relative label.
- Claim và cơ chế chấm tách: các P hiện không preregister route/mechanism, nên
  route diagnostics ở A04 chỉ là mô tả. Không nhận claim đứng là cơ chế đúng.

## 3. Prediction trên danh sách khóa

### P2 — từ PC2

Trích nguyên dòng claims.md (24/10, AI-assisted/exposed):

```text
| PC2 | Trong K2=M09–M12, (GS−GM)/Cref≥.01 ở từng ô | Characterization | Có ít nhất một ô không đạt hướng/ngưỡng sau tính sai số; chưa chạy |
```

- Quyết định: **GIỮ** forecast, không đổi tập/ngưỡng/hướng. Diff claim: không.
- Miền: K2=M09–M12, mọi ô.
- Đại lượng/dự đoán: (GS−GM)/Cref≥.01; tương đương (L01−L10)/Cref≥.01.
- Cơ chế/con đường dự đoán: **forecast không cơ chế; chưa preregister route**.
- Diagnostics phân biệt: GS, GSgivenM1, GMgivenS1, bias, abs(EΔ), E abs(e_M), F,V,a00,a01.
  Chúng không là features để chọn miền hoặc lý do đổi tập trước/sau outcomes.
- Bác bỏ cụ thể: Có một ô K2 với upper của ratio <.01. Khoảng cắt biên/HOLD thì unknown.
- Ranh giới prior/claim: Đặc trưng theo ô dưới D20/D21 và non-clairvoyant oracle; không claim câu hỏi repair nào đáng hơn là mới.
- Provenance: forecast/miền do AI hỗ trợ24/10; nhãn Phase2 được tác giả xác nhận DL-043;
  bản card/luật chấm do AI soạn theo yêu cầu, không ghi tác giả đã viết cơ chế.
- Loại: **[PREREG-CARD] sau freeze**; chấm contrast ở A04 trên đúng danh sách.

### P3 — từ PC3

Trích nguyên dòng claims.md (24/10, AI-assisted/exposed):

```text
| PC3 | Trong K3={M19,M21}, Γ/Cref>.005 ở từng ô; khả năng giải thích/dự đoán ngoài discovery phải kiểm riêng với null | Interaction candidate | Prediction K3 sai ở bất kỳ ô nào; nếu chỉ đạt K3 thì vẫn chưa chứng minh mechanism, cần kiểm PC4 |
```

- Quyết định: **GIỮ** forecast, không đổi tập/ngưỡng/hướng. Diff claim: không.
- Miền: K3={M19,M21}, mọi ô.
- Đại lượng/dự đoán: Γ/Cref>.005, giữ nguyên câu chữ; không thêm GS≥0.
- Cơ chế/con đường dự đoán: **forecast không cơ chế; chưa preregister route**.
- Diagnostics phân biệt: GS, GSgivenM1, GMgivenS1, bias, abs(EΔ), E abs(e_M), F,V,a00,a01.
  Chúng không là features để chọn miền hoặc lý do đổi tập trước/sau outcomes.
- Bác bỏ cụ thể: Có một ô K3 với upper của ratio ≤.005.
- Ranh giới prior/claim: D19 Γ trong queue plant với current-state/law oracle không biết w; không claim generic harm/2×2 là mới. GS<0⇒Γ>0 vẫn là đại số.
- Provenance: forecast/miền do AI hỗ trợ24/10; nhãn Phase2 được tác giả xác nhận DL-043;
  bản card/luật chấm do AI soạn theo yêu cầu, không ghi tác giả đã viết cơ chế.
- Loại: **[PREREG-CARD] sau freeze**; chấm contrast ở A04 trên đúng danh sách.

### P5 — từ PC5

Trích nguyên dòng claims.md (24/10, AI-assisted/exposed):

```text
| PC5 | Trong K5=M19–M22, GM/Cref≤.005 ở mọi ô; trong Q5=M01–M04 có ít nhất một ô GM/Cref≥.01 | Equivalence boundary | Có ô K5 vượt biên hoặc không ô Q5 nào đạt relevance; numeric error phải tính trước khi gán nhãn |
```

- Quyết định: **GIỮ** forecast, không đổi tập/ngưỡng/hướng. Diff claim: không.
- Miền: K5=M19–M22 mọi ô; Q5=M01–M04 ít nhất một ô.
- Đại lượng/dự đoán: K: GM/Cref≤.005; Q: GM/Cref≥.01; verdict tổng=K AND Q.
- Cơ chế/con đường dự đoán: **forecast không cơ chế; chưa preregister route**.
- Diagnostics phân biệt: GS, GSgivenM1, GMgivenS1, bias, abs(EΔ), E abs(e_M), F,V,a00,a01.
  Chúng không là features để chọn miền hoặc lý do đổi tập trước/sau outcomes.
- Bác bỏ cụ thể: Có ô K5 với lower>.005, hoặc tất cả Q5 có upper<.01. Chấm và báo từng vế.
- Ranh giới prior/claim: Chỉ vị trí ranh giới operational ε-regret equivalence dưới S0 trên finite queue coordinates; không claim model sufficiency/VE là mới.
- Provenance: forecast/miền do AI hỗ trợ24/10; nhãn Phase2 được tác giả xác nhận DL-043;
  bản card/luật chấm do AI soạn theo yêu cầu, không ghi tác giả đã viết cơ chế.
- Loại: **[PREREG-CARD] sau freeze**; chấm contrast ở A04 trên đúng danh sách.

### P6 — từ PC6

Trích nguyên dòng claims.md (24/10, AI-assisted/exposed):

```text
| PC6 | Trong K6={M17,M18}, fixed-M0 D22 split F=L00−Lcb0, V=Lcb0−L10 có V>0 và V>F | Conditional characterization | Có ô không đạt một trong hai bất đẳng thức; không diễn giải V thành lợi ích chỉ refresh backlog |
```

- Quyết định: **GIỮ** forecast, không đổi tập/ngưỡng/hướng. Diff claim: không.
- Miền: K6={M17,M18}, mọi ô.
- Đại lượng/dự đoán: D22 fixed-M0: V>0 AND V>F, giữ nguyên; không thêm GS>0.
- Cơ chế/con đường dự đoán: **forecast không cơ chế; chưa preregister route**.
- Diagnostics phân biệt: GS, GSgivenM1, GMgivenS1, bias, abs(EΔ), E abs(e_M), F,V,a00,a01.
  Chúng không là features để chọn miền hoặc lý do đổi tập trước/sau outcomes.
- Bác bỏ cụ thể: Có một ô K6 với upper(V)≤0 hoặc upper(V−F)≤0.
- Ranh giới prior/claim: Split backlog rồi mode dưới fixed-M0 trong D22, không claim giá trị freshness theo decision là mới. Không kiểm được ngoài mẫu.
- Provenance: forecast/miền do AI hỗ trợ24/10; nhãn Phase2 được tác giả xác nhận DL-043;
  bản card/luật chấm do AI soạn theo yêu cầu, không ghi tác giả đã viết cơ chế.
- Loại: **[PREREG-CARD] sau freeze**; chấm contrast ở A04 trên đúng danh sách.

## 4. Hai mức K5 và carry sang A05-F

Tác giả đã chọn hai mức, xác nhận nguyên văn được lưu trong author_attestation.json:

- Danh sách: M19–M22 (K); Q5=M01–M04 (witness chỉ ở tập đó), chấm A04.
- Luật: eligible candidate, κ≥2, A/B q90, h=8s, η∈{0.5,0.75}, target thiết kế∈{0.3,0.7}.
  Candidate dùng labels đã khóa của thiết kế; không loại/thay ô vì outcome hay precision sau này.
  Main M19–M22; held-out R03/R04 tại κ=2, η=0.5. Thực nghiệm hữu hạn, không khẳng định
  mọi κ≥2 hoặc η=.75 ở κ=2. Không dùng p_sw thực/lambdaA held-out làm features.
- P5-rule là K-uniform trên main+R03/R04 **AND** Q-witness trên M01–M04 đã khóa.
  Vế Q không được mở rộng sang held-out hoặc thay witness bằng ô thuận lợi khác.
- Khóa carry trước A04: **mọi luật trong card có main chưa bị bác (kể cả unknown)
  được đưa nguyên văn sang A05-F**. Nếu phần main bị bác, ghi refuted, không mở held-out
  chỉ để cứu luật. Không chọn riêng “luật đẹp”; A05-T báo k/m và toàn bộ trạng thái của m=1 luật.
  Đây là accounting, không là bằng chứng cơ chế khi m=1 hoặc khi Q chỉ có main witness.
- Luật này **không tiêu vào quota 1–3 H1/null predictions mới** của A05-F; A05-F phải
  giữ nguyên và báo riêng “khóa trước A04”. Rule mới/sửa sau A04 phải mang nhãn riêng.
  H1/null/metric/fit/split của A05 chưa được chọn hoặc khóa ở card này (D25).
- Các mở rộng P2→R07/R08 và P3→R03 chỉ là **candidate chưa adopt**, không thuộc card
  formal claims/denominator/carry. Không âm thầm thêm chúng sau khi thấy main outcomes.
- P6: **không có kiểm ngoài mẫu** trong held-out hiện tại. Không tự sinh/thay ô.

## 5. Hệ quả chung và witness nhất quán

K3⊂K5; nếu P3 và K-branch P5 cùng đứng tại M19/M21 thì
Γ≤GMgivenS1≤Γ+.005Cref và E abs(e_M)≥GMgivenS1>.005Cref.
Đây là hệ quả điều kiện, không là forecast mới.

Các bảng dưới là **witness tưởng tượng**, không phải số ô grid hoặc dự báo độ lớn:

| Vai trò witness | L00 | L01 | L10 | L11=Cref | Giải thích |
|---|---:|---:|---:|---:|---|
| K2/P2 | 102.25 | 101.75 | 100 | 100 | (GS−GM)/Cref=.0175≥.01 |
| K3⊂K5 | 102 | 101.8 | 101 | 100 | Γ=.8>.5; GM=.2≤.5 |
| Q5 | 104.5 | 103.5 | 100 | 100 | GM=1≥1 |
| K6/P6 | 101.125 | 100.875 | 100 | 100 | Lcb0=100.75; F=.375,V=.75 |

K2 và K3 là các ô khác nhau, không ép cùng một bảng thỏa hai tập rời nhau.
Mỗi P có countermodel ở hồ sơ kiểm; không có identity nào được đếm là prediction.

## 6. Không có trong card

PC1 ở sanity/framing. PC4 → A05-F sau discovery, cần null theo D25; không chốt null dễ thắng.
Không claim novelty, effect riêng κ/quantile/η hoặc network operational benefit.
Cùng độ khó không đồng nghĩa cùng tải; không dùng anchored p_sw/lambdaA làm cơ chế.

## 7. Reviewer và điều kiện trước freeze

Reviewer kỹ thuật: **AI tự kiểm cùng phiên đã soạn card**, không reviewer độc lập.
Sáu kiểm: falsifiable; coordinate-only; refutation cụ thể; scope theo prior boundary
chính thức DL-043; không identity; consistent joint witnesses. Ghi số liệu kiểm thật
ở results/lessons/l3_3, không gọi self-check là người thật hoặc phiên AI độc lập.
Hai read-back: author-attested theo câu trả lời trực tiếp ngày27/10, ngoài repo;
không có transcript hoặc cơ chế mới do tác giả viết trong repo.
P0-V10/L8 chưa có người đọc; V9 chưa gửi. Không điều kiện nào ở đây mở Phase4 hoặc A04.
Đã kiểm trước freeze: 324 toàn repo PASS; 29 tests card/guard PASS; 11/11 mutant bị bắt.
Sáu self-check có giới hạn scope/algebraic như hồ sơ review, không thay người đọc độc lập.

## Bổ sung sau A01

Chưa có. Phần này không phải nơi sửa forecast v1 hoặc thay nhãn provenance.
