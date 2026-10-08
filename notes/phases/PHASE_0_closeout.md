# Phase 0 Closeout — State × Model

Tác giả: **Doan Van Tai** · Ngày quyết định: **08/10/2026** · **GO có điều kiện — phương án B** · Bản kỹ thuật: `contract-v0` · Gate: `phase-0-closeout`.

Ngày 08/10, tác giả yêu cầu đóng Phase 0 theo hướng dẫn được cung cấp. Dùng **phương án B**, mang nguyên trạng V3/V10/V11; đây là quyết định quản lý phase, không phải record tác giả đã hoàn tất bài tự làm hoặc GVHD đã duyệt. DL-010 là review kỹ thuật tự động, không tính cho V10. Chi tiết quyết định ở [DL-009](../02_decision_log.md).

## 1. Nội dung kỹ thuật Phase 0 đã xác định

Main RQ đo lợi ích riêng và kết hợp của sửa thông tin state và sửa cách biểu diễn ngẫu nhiên trong response model khi routing đổi tải. Twin gồm estimator S và model M; luật chọn action giữ cố định, simulator đóng vai plant. State, observation, law và tương lai được tách riêng; oracle biết hiện tại/law, không thấy future realization. Primary cost là cumulative queue occupancy cuối slot của cả hai queue, không phải mean delay. Với traffic bảo toàn, không loss, cùng capacity, trọng số hai queue và switching cost bằng 0, action chỉ đổi cost qua capacity bỏ phí; không idle trên mọi path của cả hai action cho regret bằng 0. Kết quả phải báo theo điều kiện của D, giữ domain trục telemetry hai neo. Đây là tổng hợp tài liệu, **chưa thay bản tự giải thích RQ của tác giả**.

## 2. Những điều chỉnh thiết kế được lưu

Thiết kế dùng contrasts của can thiệp thay cho phân chia lỗi theo nguyên nhân. Dấu một số contrasts và null bảo toàn được ghi là hệ quả E0; chưa là novelty hoặc cơ chế mạng mới. “Model fidelity” được thu hẹp thành cách biểu diễn ngẫu nhiên với cùng tham số/law và recurrence. Timescale vật lý được khai báo trước khi quy đổi slot, có kiểm độ nhạy chia slot. Không gán những thay đổi tài liệu này thành record về mental model cá nhân; bài viết lại, tính tay và bốn câu tự kiểm DL-010 vẫn thuộc V11.

## 3. Output của Phase 0

| Output | Nơi lưu | Trạng thái khi rời Phase 0 |
|---|---|---|
| Archive bất biến, legacy map | [legacy/INDEX.md](../../legacy/INDEX.md), [history](../00_history.md) | Có; bài tự kiểm 5 dòng còn chờ |
| Evidence inventory EV-01…EV-33, exposure register | [inventory](../00_evidence_inventory.md), [exposure](../00_exposure_register.md) | Có; nhiều ô “tác giả giải thích lại” còn Chưa |
| Claim boundary C1–C10, NC1–NC17, U1–U9 | [claim boundary](../01_claim_boundary_v0.md) | Có; dòng 08/10 chờ tác giả xác nhận |
| Contract v0 (D1–D25, §0–§10, sửa đổi DL-010) | [contract](../01_definitions.md) | Đóng băng bản kỹ thuật `contract-v0` theo B; DRAFT/OPEN bên trong giữ nguyên, V11 mang sang |
| Research brief v0 | [brief](../00_research_brief.md) | Có; tác giả còn viết lại |
| Timescale sanity, script, 11 test | [T00](../theory/T00_timescale_sanity.md), `experiments/lessons/`, `tests/` | Có; 11 test đạt |
| Decision log DL-000…DL-010 | [decision log](../02_decision_log.md) | DL-003…DL-008 phần tự kiểm còn DRAFT; DL-009 chọn B ngày 08/10; DL-010 đã áp |
| Lesson notes L0.1–L0.7, Ownership Review | [lessons](../lessons/), [ownership review](../PHASE_0_ownership_review.md) | Có khung và mẫu; nhiều bài tự làm còn chờ |

Phase 0 **không** tạo network evidence cho Main RQ. Evidence mới gồm E0 (logic/đại số), đối chiếu hữu hạn E1 trên toy grid và thứ tự độ lớn có nguồn; không là network empirical evidence.

## 4. Gate V1–V11

Tên điều kiện theo bản mẫu File 9 trước đó; đối chiếu PHASE_0 §17 khi có bản gốc.

| ID | Điều kiện | Trạng thái | Record |
|---|---|---|---|
| V1 | Quá khứ đóng băng có địa chỉ; repo mới độc lập | Đạt | Tags + hash, legacy map; repo mới không import code cũ |
| V2 | Evidence có loại, nguồn, người kiểm; motivation không gọi là evidence | Đạt về tài liệu | EV-01…EV-33 |
| V3 | RQ viết bằng lời mình và truyền đạt được (read-back với người thật) | **MỞ — mang sang trước Gate 1** | [L0.2](../lessons/L0.2_rq_card.md) |
| V4 | Mỗi đối tượng có định nghĩa vận hành, không trùng | Đạt ở mức tài liệu | D1–D25; D1/D13 làm rõ theo DL-010 |
| V5 | Quyền thông tin không rò | Đạt ở mức thiết kế | Contract §3; ép bằng code ở Phase 3–4 |
| V6 | Estimand nối được RQ | Đạt, phạm vi đã thu hẹp | Contract §0, §4; “model fidelity” = biểu diễn ngẫu nhiên (DL-010) |
| V7 | Hai repair tách được, diagnostic dose tối đa; chưa quy đồng chi phí | Đạt có điều kiện | $S_1$ gộp ba thành phần; chi tiết belief OPEN; §5 |
| V8 | Mục còn mở có tên và nơi quyết | Đạt | Contract §9 |
| V9 | Con số timescale có nguồn hoặc nhãn “chưa có nguồn” | Đạt có điều kiện | T00, EV-31; số SNMP/streaming là nguồn thứ cấp |
| V10 | Người đọc độc lập đã xem contract v0 | **MỞ — phải đạt trước Phase 4** | [L0.7](../lessons/L0.7_review.md). Review DL-010 là review kỹ thuật tự động, **không** tính cho V10 |
| V11 | Understanding artifact là của tác giả | **MỞ — bổ sung trước khóa contract-v1 ở L1.8** | L0.2–L0.7; 4 câu tự kiểm DL-010 trong contract |

**Diễn giải outcome theo hướng dẫn (không xác nhận rubric gốc):** O2 — timescale chỉ hợp lý khi tỉ số $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$ đủ lớn, domain đã thu hẹp thành trục quét với hai neo; O6 — G1 dựa trên literature thứ cấp, ưu tiên Phase 2.

## 5. Review chuyển phase (DL-010) và sửa đổi đã áp

Văn bản ngày 08/10/2026, tự mô tả là review kỹ thuật tự động: **GO WITH CAUTION** sang Phase 1 về kỹ thuật, giữ G1. Năm sửa đổi bắt buộc đã đưa vào repo:

| # | Sửa đổi | Đã sửa ở | Record kỹ thuật; tự kiểm của tác giả |
|---|---|---|---|
| 1 | Quy tắc cheap kill theo oracle repair | Contract §7(f), DL-006 | Áp và kiểm kỹ thuật 08/10; bài tự kiểm còn V11 |
| 2 | Objective cumulative queue occupancy, ngữ nghĩa slot | D1, D13, ghi chú dưới bảng §2 | Áp và kiểm kỹ thuật 08/10; bài tự kiểm còn V11 |
| 3 | Chống chỉnh timescale nhân tạo | §6 quy tắc 7, §9 | Áp và kiểm kỹ thuật 08/10; bài tự kiểm còn V11 |
| 4 | Null tương đương quyết định dựa trên bảo toàn | §7(g)–(h), §6 quy tắc 8, EV-32/33, C10 | Áp và kiểm kỹ thuật 08/10; bài tự kiểm còn V11 |
| 5 | Phạm vi mean → stochastic | §0, D21, §5, NC16, brief | Áp và kiểm kỹ thuật 08/10; bài tự kiểm còn V11 |

## 6. Quyết định gate của tác giả (ghi vào DL-009)

| Phương án | Khi nào hợp | Hệ quả |
|---|---|---|
| **A. GO có điều kiện** (khớp GO WITH CAUTION) | Đã làm phần lõi V11 (viết lại RQ, tính tay 2×2 và một dòng timescale, câu tự kiểm DL-010 số 1–2, xác nhận DL-003…DL-008); V3/V10 mang theo làm điều kiện | Đóng Phase 0; tag `contract-v0` và `phase-0-closeout`; **HOLD Phase 4** tới khi V10 đạt |
| B. GO có điều kiện, mang cả V11 | Chưa làm bài tự làm nào nhưng muốn đi tiếp | Đóng với ba điều kiện mở; ownership yếu hơn, ghi rõ trong DL-009 |
| C. HOLD formal closeout | Muốn đóng chỉ khi V3/V10/V11 đều có record | Học Phase 1 theo DL-010; chỉ tag `contract-v0`; đóng Phase 0 sau |

**Phương án thực hiện: B — GO có điều kiện, mang cả V11**, ngày **08/10/2026**. Đây là cách thực hiện yêu cầu đóng phase trong khi record chưa đủ cho A; không giả đã có phần lõi V11.

| Điều kiện | Việc phải làm | Mốc xử lý |
|---|---|---|
| V3 | Tự viết lại RQ và read-back với người thật, ghi vai trò/ngày/kết quả ở L0.2 | Trước Gate 1 |
| V11 | Tính tay 2×2 và timescale, bài L0.3–L0.6, brief/contract, bốn câu DL-010; rà các quyết định DRAFT | Trước khóa contract-v1 ở L1.8 |
| V10 | Người đọc độc lập xem đúng commit/tag contract và ghi phản hồi tại L0.7 | Trước Phase 4; **HOLD Phase 4 khi chưa đạt** |

Người quyết định: **Doan Van Tai**, qua yêu cầu đóng Phase 0 theo hướng dẫn. Chấp nhận bản kỹ thuật để tiến Phase 1 không xác nhận tác giả đã làm bài hay được GVHD duyệt. Heads-up/pivot memo và phản hồi GVHD vẫn chưa có record gửi/nhận.

## 7. Sang Phase 1

**Nhận từ Phase 0:** `contract-v0` (LOCKED: oracle không thấu thị, ba luật chống rò, $w$ chỉ evaluator thấy; DRAFT: objective, repair cards, $S_0$ belief, domain; OPEN: §9), T00, exposure register, các ràng buộc E0 ở §7.

**Cam kết của DL-010 → nơi làm:**

| Cam kết | Nơi làm | Xong khi |
|---|---|---|
| Ví dụ Stay/Switch không suy biến | L1.2–L1.4 | Một episode sinh từ plant có $\Delta\ne0$, tính tay và bằng code; kiểm có idle với xác suất dương (§7g iv) |
| Cách $S_0$ xử lý belief, observation schema, baseline $M_0/M_1$ | L1.6–L1.8 | Contract §9 các dòng tương ứng có quyết định; §7(c) giữ hay không được ghi rõ |
| Mode persistence và co giãn thời gian vật lý | L1.8 | $T_{\text{mode}}$ khai báo bằng giây; kiểm $\Delta t$ / $\Delta t/2$ với dung sai chọn trước (§6 quy tắc 7) |

**Phải khoá ở L1.8 (thành `contract-v1`):** $\Delta t$, $H$, lưới $\tau$, $u$, capacity, tham số Markov, chi tiết $S_0$, lưới $D$ (kèm tỉ lệ vùng bảo toàn), reference cost, $\varepsilon_R$, $\varepsilon_E$, seed streams.

**Giới hạn scope (DL-010):** không mô phỏng quy mô lớn, không claim novelty mạnh, không khuyến nghị vận hành trước khi có evidence hỗ trợ.

## 8. Assumptions và risks còn mở

- **AS1** (traffic nền ngoại sinh) — rủi ro nhất cho external validity; Phase 7.
- **AS4** (action hiệu lực ngay) — rủi ro nhất cho giá trị State repair; Phase 8.
- **AS3** (buffer vô hạn) — nới ra thì objective thưởng cho loss; cần phạt loss trước (contract §8).
- Novelty: value-of-information (P11) có thể đã trả lời phần chính (K1) — Phase 2.
- Threshold null đóng băng đủ dự báo gain (K2) — A05 trước Phase 4.
- Domain gần như toàn vùng bảo toàn → mọi contrast tầm thường — kiểm khi chọn lưới $D$ ở L1.8.
- Không giữ được estimator cố định khi đổi model → pipeline repair (K5) — L1.6–L1.8.

## 9. Được và không được claim khi rời Phase 0

Danh sách đầy đủ ở [claim boundary](../01_claim_boundary_v0.md). Ngắn gọn: được nói C1–C10 trong đúng điều kiện ghi kèm; **không** được nói NC1–NC17, đặc biệt NC6 (G1 không phải novelty), NC16 ($G_M$ không phải model fidelity nói chung) và NC17 (GO WITH CAUTION không phải GVHD duyệt, không phải cơ chế mạng).

## 10. Sửa đổi plan tích luỹ (chép vào changelog master plan)

| # | Plan ghi | Sửa thành | Nguồn |
|---|---|---|---|
| 1 | Tag ở `7c60c76` | `archive-switch-or-stay-2026-10-02` @ `e669f5c` + tag phụ wip | DL-000 |
| 2 | Chỉ kiểm nhánh remote | Nhánh local N0–N2 giữ bằng tag phụ | Inventory sai lệch 4 |
| 3 | F6: 20000–29999 “chưa dùng” | 20001–20020 đã dùng/đã xem | Exposure register; sai lệch 3 |
| 4 | V.3, K10: oracle repair là cận trên của feasible | Cận trên chung là $R_{00}$; quy tắc cheap kill ở contract §7(f) | EV-26, DL-006, DL-010 |
| 5 | Part XI: `workload_after` Rebuild | Reference; giả định nằm ở `des_world.py` | EV-30 |
| 6 | Chưa nêu | Dấu của $G_{SM},G_{S\mid M_1},G_{M\mid S_1}$ là hệ quả thiết kế; VOI vào closest prior | EV-27 |
| 7 | Neo tuổi thông tin vào AoI testbed | Trục quét theo chế độ telemetry trong literature, hai neo | EV-31, DL-008 |
| 8 | Objective “tổng thời gian chờ” | Cumulative queue occupancy với ngữ nghĩa slot rõ | DL-010 |
| 9 | Chưa nêu | Null bảo toàn: action chỉ đổi cost qua capacity bỏ phí | EV-32, DL-010 |
| 10 | “Model fidelity” chung | Chỉ biểu diễn ngẫu nhiên, cùng $\theta$ | DL-010 |

## 11. Tag và provenance

Thực hiện theo quyết định B ở §6, sau khi kiểm kỹ thuật năm sửa đổi ở §5; V3/V10/V11 vẫn mở. Không dùng `git tag -f`; nếu cần sửa sau khi tag, tạo tag mới (ví dụ `contract-v0.1`) kèm DL entry.

```bash
git tag -a contract-v0 -m "Research contract v0 incl. DL-010 amendments. Numbers locked later in contract-v1 (L1.8)."
git tag -a phase-0-closeout -m "Phase 0 closeout: GO conditional B; conditions: V3,V10,V11. Technical transition DL-010 (review kỹ thuật tự động). Not supervisor approval."
git push origin main contract-v0 phase-0-closeout
```

Hai tag trỏ cùng commit closeout. Không di chuyển tag; thay đổi contract sau đóng băng tạo phiên bản mới. DRAFT/OPEN là trạng thái khoa học bên trong snapshot, không làm mất điều kiện mang sang.
