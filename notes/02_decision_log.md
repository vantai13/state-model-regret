# Decision log

Tác giả: **Doan Van Tai**.

Quyết định ghi theo thời điểm; phê duyệt của tác giả khác phê duyệt của GVHD.

### DL-000 — Genesis (2026-10-07)
- Decision: đóng băng switch-or-stay tại `archive-switch-or-stay-2026-10-02` / `e669f5c8053a81d6de192de9f9d0d6304ee67802`, giữ local WIP bằng `archive-switch-or-stay-2026-10-02-wip-local-2026-10-07` / `2e7543b2794a85645d60c0a55afb5a670166a099`, mở workspace riêng cho State×Model Main RQ. Nguồn RQ: Final Review cập nhật 06/10 và tiền thân N0/N1/N2 ngày 02/10; xem inventory EV-05/13/14.
- Why: historical snapshot cố định tránh citation drift; ghi seed/workload/config đã nhìn để confirmation tương lai thật sự held-out. Chọn e669f5c vì nó giữ cả 10 nhánh remote ban đầu; main cũ dừng ở `7c60c76630de0e4bd6459b00d201fa2e744a46fe`.
- Alternatives: tag main không giữ toàn rollout work; merge mọi nhánh tạo project state chưa từng ở đó; tiếp tục phát triển RQ mới ngay repo cũ khó tách assumptions/objective/scope đang đổi; không archive làm trôi trích dẫn và mất exposure history. Biện minh estimand chi tiết dành L0.5.
- Consequence: historical citation dùng immutable tag:path; không phát triển old project như Main RQ hiện tại; giữ scope result cũ; ghi exposed seed/config; artifact mới vào workspace mới.
- Revisit when: GVHD yêu cầu bổ sung NCKH từ old project → branch từ đúng archive tag và decision entry; không sửa/di chuyển tag.
- Tác giả quyết định; GVHD chưa xác nhận Main RQ. Tại genesis remote tạo tự động gặp HTTP 403 và heads-up chưa gửi; các thay đổi sau ghi entry riêng.

### DL-001 — Publish notes sau xác nhận public (2026-10-07)
- Decision: tác giả xác nhận trực tiếp “Tôi xác nhận push lên repo public”; dùng `https://github.com/vantai13/state-model-regret` public thay mặc định private.
- Why: tác giả đã tạo remote; API chuyển private trả HTTP 403, sau đó tác giả chọn giữ public.
- Consequence: main và `l0.1-genesis-2026-10-07` đã push, clone từ GitHub kiểm đủ nội dung; tag genesis giữ commit `e0e563375b143da5d6ce472d9e82c28a3ebc752b`.
- Tác giả quyết định việc publish; không phải GVHD duyệt RQ hoặc nghiên cứu. Heads-up vẫn chưa gửi.

### DL-002 — Tích hợp nội dung tác giả xác nhận và sửa nguồn (2026-10-07)
- Decision: khôi phục A1 nguyên văn; tích hợp understanding/judgment tác giả cung cấp, B6 và nhãn history; lập inventory EV-01…EV-19, exposure, G-level, claim boundary v0 và closeout; bỏ các tên công cụ theo yêu cầu biên tập của tác giả.
- Why: tách đối chiếu nguồn khỏi hiểu bài, giữ scope old-world, sửa source discrepancies và làm bằng chứng nhỏ có thể mở từ repo public.
- Consequence: G1 giữ nguyên; không nâng lên G2; full study HOLD. Understanding tích hợp theo xác nhận tác giả, không giả có vấn đáp/read-back độc lập. Chỉ nội dung hiện hành được sửa; archive và genesis tags không bị di chuyển.
- Verification: script archive portable chạy từ clone mới; hashes/CI/source metadata được commit dưới notes/verification. Ba bundle có bản sao thứ hai trùng SHA-256 trên filesystem khác cùng máy; chưa phải off-site backup.
- Public scope: chỉ summary/metadata; không chép nguyên văn private feedback, email/address/token hay transcript nhạy cảm. Full raw/review/bundles local-only có limitation rõ.
- Status: SCIENTIFIC/UNDERSTANDING PASS — PRACTICAL PENDING theo rubric tích hợp tác giả yêu cầu; heads-up chưa gửi. Không bắt đầu L0.2.
- Tác giả xác nhận nội dung trong prompt; chưa có source mới xác nhận GVHD approve hướng này.

## Bổ sung File 6 — 08/10/2026

Nội dung DL-003…DL-009 được tích hợp từ File 6 tác giả cung cấp và đối chiếu với [RQ card](lessons/L0.2_rq_card.md), [contract](01_definitions.md), [inventory](00_evidence_inventory.md), [claim boundary](01_claim_boundary_v0.md), [T00](theory/T00_timescale_sanity.md) và [legacy map](../legacy/INDEX.md). Ngày 08/10 là ngày tích hợp, **không phải ngày tác giả xác nhận từng quyết định**. Ownership Review bổ sung cùng ngày ghi tác giả đã nêu chọn B2 và domain hai neo ở DL-008; các phần còn lại của DL-003…DL-008 vẫn DRAFT, DL-009 đã ghi closeout phương án B theo yêu cầu ngày 08/10, mang V3/V10/V11; việc tự kiểm vẫn chờ. Các nguyên tắc LOCKED trong contract vẫn giữ nhãn riêng của chúng.

Sổ có **11 mã DL-000…DL-010**: 3 entry lịch sử có ngày, 6 bản nháp, 1 quyết định gate có điều kiện (DL-009) và 1 bản ghi review chuyển phase (DL-010). Chưa phải 11 quyết định đã chốt; vẫn trong ngân sách Phase 0 khoảng 12 entry. Chỉ lập entry cho lựa chọn có phương án thay thế đáng cân nhắc; sửa lỗi diễn đạt hoặc đổi tên tránh trùng mã không tự tạo entry mới.

### DL-003 — Giữ Main RQ làm working RQ (DRAFT; ngày xác nhận: ⟨chưa có⟩)

- Decision: giữ nguyên văn Main RQ của Final Review cập nhật 06/10 làm **working RQ**, như [RQ card](lessons/L0.2_rq_card.md) và contract §0; đọc nó như câu hỏi factorial về **giá trị của hai can thiệp**, không phải chia lỗi theo nguyên nhân.
- Why: “state hay model quan trọng hơn” không có đáp án chung; giá trị mỗi repair phụ thuộc repair kia, điểm xuất phát và phân phối $D$ (L0.2; EV-01, EV-25).
- Alternatives: viết lại thành “nút thắt ở đâu” (không chọn trong bản nháp vì dễ thành câu hỏi chia lỗi); thu hẹp ngay về một sub-RQ (chưa đủ evidence để chọn).
- Consequence: estimand là $G_S,G_M,G_{SM},\Gamma$ và hai gain có điều kiện; báo kết quả theo điều kiện, cùng objective, oracle và $D$.
- Revisit when: Phase 2 tìm thấy closest work cùng estimand (K1), hoặc Gate A không có prediction vượt identity (K8).
- Ai quyết: **Doan Van Tai — chờ xác nhận**. Chưa có record tác giả tự diễn giải/read-back đạt yêu cầu ở L0.2.

### DL-004 — Phân loại đối tượng và quyền thông tin (DRAFT; ngày xác nhận: ⟨chưa có⟩)

- Decision: giữ mặc định capacity là parameter cố định trong episode; mode hiện tại là state, law chuyển mode thuộc $\theta$, chuỗi mode tương lai thuộc $w$; utilization theo cửa sổ là thống kê của observation. Ba luật chống rò ở contract §3 là **LOCKED**: không ô nào/oracle nhận $w$; chỉ $S_1$/oracle nhận $x$ trong nhánh quyết định; $S$ giống hệt giữa các ô cùng chỉ số $s$.
- Why: chọn phân loại trước khi có kết quả để không tạo attribution mong muốn; tách state/observation/parameter/future theo Final Review §2.0 và contract D3–D4, D7–D11.
- Alternatives: capacity biến đổi theo mode, đưa capacity hiện tại vào state và law của nó vào $\theta$ (xem lại nếu Phase 8 cần); mode quan sát được (làm $S_0$ mạnh hơn nhưng chưa có telemetry phù hợp trong thiết kế hiện tại).
- Consequence: quyền $S_1$ biết mode thật chỉ phục vụ diagnostic; không tự coi refresh backlog khả thi cũng đo được mode. Đổi quyền thông tin phải sửa bảng contract §3 và kiểm rò.
- Revisit when: dữ liệu cho thấy capacity trôi trong episode, hoặc có telemetry đo được mode.
- Ai quyết: **Doan Van Tai — chờ xác nhận các lựa chọn DRAFT**. Việc thêm entry này không đổi nhãn LOCKED của ba luật chống rò.

### DL-005 — Objective, benchmark, regret và quy tắc báo cáo (DRAFT; ngày xác nhận: ⟨chưa có⟩)

- Decision: primary objective là tổng thời gian chờ tích lũy trong horizon của mọi packet trên cả hai queue, kể cả packet chưa xong (packet·s); kèm quy đổi ms/packet khi đã đặc tả mẫu số/tập packet. Một oracle không thấu thị cho cả bốn ô; tie → Stay; $c_{\text{sw}}=0$ ở diagnostic; $\varepsilon_R$, $\varepsilon_E$ theo tỉ lệ reference cost dương, chọn trước confirmation. Mẫu số quy đổi, reference cost và mức ngưỡng vẫn **OPEN**, chưa tự điền.
- Why: đếm packet chưa xong và traffic nền bị ảnh hưởng để giữ construct validity (contract D13–D18, §4/§6; L0.4 còn chờ bài làm). Oracle nhìn trước tương lai sẽ phạt twin vì thông tin không được cấp.
- Alternatives: mean delay của packet đã xong (không chọn vì có thể ưu ái action để lại backlog); ms/packet làm primary (để câu hỏi cho người đọc độc lập, cần quy tắc chuẩn hóa nhất quán).
- Consequence: mọi contrast hiện có đơn vị packet·s; không so trực tiếp với ngưỡng %. Đổi objective/primary phải ghi REFORMULATE, kiểm lại oracle, regret, contrasts, L0.2/L0.4 và các tài liệu liên quan; không chỉ thay nhãn đơn vị.
- Revisit when: người đọc độc lập đề xuất primary khác, hoặc mẫu số/quy tắc chuẩn hóa không giữ đúng construct cần đo.
- Ai quyết: **Doan Van Tai — chờ xác nhận**; câu hỏi đơn vị cho người đọc độc lập vẫn mở, chưa có record phản hồi.

### DL-006 — Hai repair card và sửa logic cheap kill (DRAFT; ngày xác nhận: ⟨chưa có⟩)

- Decision: State repair = $S_0\to S_1$ (dose tối đa, gộp ba thành phần, gọi là “thông tin state hiện tại đầy đủ”); Model repair = $M_0$ load-aware → $M_1$, giữ $S$ kể cả mô hình bên trong; giữ ô chẩn đoán phụ $S_0^{\tau=0}$ ở D22. Cheap kill và K10 dựa trên $R_{00}$, không dùng gain của từng oracle repair làm cận trên feasible gain cùng loại. Câu quy tắc đầy đủ (sửa theo DL-010) nằm ở contract §7(f): cận trên khoảng tin cậy của $100R_{00}/C_{\text{ref}}$ dưới $\varepsilon_R$ trên một miền → NARROW/dừng miền đó; cận chỉ giữ khi cùng $D$, objective, tập action và thời điểm hiệu lực của action.
- Why: dùng hai endpoint diagnostic tối đa và ghi rõ thứ giữ cố định (contract D20–D22, §5); không suy hai repair có chi phí triển khai ngang nhau. EV-26 cho phản ví dụ bù sai số: oracle State gain 0, sửa nửa sai số State gain 1; contract §7(f) cho cận chung $R_{00}$.
- Alternatives: so theo “giảm RMSE 50%” (không chọn vì đơn vị/vai trò sai số khác nhau); giữ cận “feasible ≤ gain của một oracle repair” được dẫn từ master plan V.3 (bị EV-26 bác với pipeline cố định). Oracle quyết định chung vẫn là benchmark hợp lệ.
- Consequence: nếu không giữ được estimator cố định khi đổi model, phải đổi tên estimand thành **pipeline repair** (K5). Bỏ D22 sẽ mất diagnostic tách freshness khỏi mode visibility. Đây là đề xuất sửa quy tắc cheap kill; chưa ghi master plan đã được sửa hoặc đối chiếu câu gốc đầy đủ.
- Revisit when: Phase 3 cho thấy hai repair không tách được, hoặc feasible operator không thể so trên cùng $D$, objective và tập action.
- Ai quyết: **Doan Van Tai — chờ xác nhận**; bài tự tính EV-26/L0.4 và lựa chọn giữ D22 còn chờ.

### DL-007 — Bản đồ legacy và lý do repo mới (DRAFT; ngày xác nhận: ⟨chưa có⟩)

- Decision: áp bảng Keep/Reference/Archive/Rebuild/Unknown và danh sách “không mang sang” trong [legacy/INDEX.md](../legacy/INDEX.md); repo mới không import code từ repo cũ. Migrate chỉ khi có experiment cần, byte-exact kèm PROVENANCE riêng, checksum, test checksum và decision-log entry; không chèn header làm đổi byte của bản gốc.
- Why: action, objective, oracle và loại model đổi so với RQ cũ (contract D5, D10, D13–D15; L0.3–L0.4). Giả định managed không đổi tải nằm ở chỗ gọi engine trong `des_world.py`, không ở engine workload tổng quát (EV-30). Đây là biện minh theo estimand mà DL-000 dành cho L0.5.
- Alternatives: phát triển tiếp trong repo cũ (không chọn vì dễ mang mặc định cũ sang RQ mới); bỏ toàn bộ code cũ (không chọn vì engine workload và dữ liệu AoI vẫn có giá trị đối chiếu có provenance; AoI chỉ là điểm dữ liệu prototype, không dùng làm neo).
- Consequence: khung `smr` tối thiểu đã được tạo ở File 4; 8 test đạt khi kiểm File 4 (7 timescale + 1 smoke), sau phương án A là 11 (10 + 1). Chưa migrate file cũ, chưa tạo module nghiên cứu trước khi có câu hỏi cần nó. Triển khai kỹ thuật này không thay bài tác giả tự kiểm 5 dòng legacy.
- Revisit when: Phase 7 cần representation độc lập hoặc một experiment cụ thể cần artifact Keep.
- Ai quyết: **Doan Van Tai — chờ xác nhận lý do/lựa chọn nghiên cứu**. Repo và khung code đã triển khai; bài tự kiểm L0.5 chưa có record.

### DL-008 — Scope, domain, estimator $S_0$ và nguyên tắc sinh $D$ → contract v0 (DRAFT; B2 và phương án A/hai neo đã được nêu chọn 08/10/2026; chi tiết và tự kiểm còn chờ)

- Decision: scope theo contract §8; domain báo theo tỉ số không thứ nguyên; $\tau_{\text{eff}}+d_{\text{act}}$ là trục quét qua bốn chế độ có nguồn (ms, dưới 1 s, vài giây, từ vài chục giây), giữ **cả hai neo (a)** ms + datacenter 1–10 Gb/s và **(b)** polling 0,1–1 s + edge 10–100 Mb/s. Phương án A do tác giả cung cấp ngày 08/10/2026. $S_0$ belief trên $(q,m)$ dùng chung cho $M_0/M_1$ (B2) đã được nêu chọn trong [Ownership Review](PHASE_0_ownership_review.md); schema/triển khai và tự kiểm vẫn OPEN, B1 giữ cho sensitivity cần đặc tả; $D$ sinh theo law plant, báo theo tọa độ quan sát trước action. **Chưa gắn tag** `contract-v0`; chỉ thực hiện sau khi đủ điều kiện §10.
- Why: EV-31 cho thang thời gian measurement/polling/control trải ms tới phút, không tự là tuổi thông tin; T00 nối qua $P/2+L+W/2$ dưới giả định đã khai báo. EV-28 sàng lọc theo $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$, không riêng tốc độ link và không chứng minh gain. EV-10 là prototype Ditto, không đại diện nên bỏ vai trò neo; EV-29 cho gap confirmation/data plane ở switch cụ thể, chưa là timing use case. Observation backlog/rate còn OPEN. Final Review §11.2 yêu cầu baseline bù tuổi; ghép state/observation tùy ý có thể làm méo $G_S$.
- Alternatives: B1 làm bản chính (không chọn theo Ownership Review vì nguy cơ baseline yếu; không mặc định luôn thổi phồng $G_S$); chốt số tuổi từ testbed dt4n (không chọn: một prototype không đại diện); chốt một chế độ telemetry duy nhất (không chọn theo phương án A: cần so tương phản hai neo trên cùng trục tuổi).
- Consequence: nếu belief là posterior chính xác, prior khớp $D$, $M_1$ tích phân đúng và nhóm báo cáo theo thông tin trước action, $G_M\ge0$ là hệ quả Bayes-optimal và $G_{S\mid M_1}$ có diễn giải EVPI (EV-27). $G_{S\mid M_1}\ge0$ riêng nó còn đúng do ô 11 = oracle. Literature value-of-information thành prior phải kiểm ở Phase 2. Posterior chính xác/xấp xỉ, prior, schema, cách $M_0$ dùng belief và lưới $D$ vẫn OPEN ở L1.6–L1.8; model baseline trung gian đề xuất trong Ownership Review cần đặc tả ở L1.8; chưa khóa các con số của contract v1.
- Revisit when: L1.6–L1.8 cho thấy posterior chính xác quá đắt; có nguồn tuổi telemetry nhanh; có số đo $d_{\text{act}}$ thật; hoặc sinh $D$ không khớp prior đã dùng.
- Ai quyết: **Doan Van Tai** — đã nêu chọn B2, phương án A và giữ cả hai neo ngày 08/10/2026; chi tiết triển khai, các lựa chọn còn lại và bài tự kiểm còn chờ. DL-009 cho đóng băng bản kỹ thuật có điều kiện B; không thay bài làm của tác giả.

### DL-009 — Gate Phase 0: GO có điều kiện, phương án B (2026-10-08)

- Căn cứ: [closeout §6](phases/PHASE_0_closeout.md), review kỹ thuật DL-010 và hướng dẫn tác giả cung cấp. Không suy tác giả đã tính tay, read-back hoặc được GVHD duyệt từ yêu cầu đóng phase.
- Decision: **đóng Phase 0 theo phương án B — GO có điều kiện, mang V3/V10/V11**. Thực hiện yêu cầu tác giả “bây giờ đóng phase đi, thực hiện theo hướng dẫn”; B phù hợp record hiện tại vì chưa có bài tự làm đủ cho A. Đóng băng bản kỹ thuật tại `contract-v0`, ghi quyết định tại `phase-0-closeout`; cho phép phân tích/exact nhỏ Phase 1, **HOLD Phase 4 tới khi V10 đạt**.
- Why: các artifact kỹ thuật và năm sửa đổi đã có; kiểm hữu hạn và tests đạt. V3/V10/V11 còn mở nên không chọn GO trơn hoặc giả phần lõi V11 đã xong. B cho phép học/phân tích đảo ngược được, giữ nguyên G1.
- Alternatives: A cần record phần lõi V11 và xác nhận DL-003…DL-008, hiện chưa đủ; C giữ formal closeout mở, không đáp ứng yêu cầu đóng ngay. B được dùng để thực hiện yêu cầu trong điều kiện đang có.
- Consequence: V11 — bài tự giải thích/tính tay/lesson phải bổ sung trước khi khóa contract-v1 ở L1.8; V3 — read-back trước Gate 1; V10 — người đọc độc lập trước Phase 4. Chưa có record gửi heads-up hoặc GVHD duyệt. DL-003…DL-008 giữ phần chưa xác nhận; các mục OPEN tiếp tục đúng nơi quyết.
- Revisit when: điều kiện đạt/không đạt, Phase 1 lộ lỗi contract hoặc người đọc/GVHD yêu cầu đổi hướng. Ghi record mới; không di chuyển tag.
- Ai quyết: **Doan Van Tai**, ngày **08/10/2026**, qua yêu cầu đóng Phase 0 theo hướng dẫn; không phải phê duyệt GVHD hoặc xác nhận understanding artifacts.


<a id="dl-010"></a>
### DL-010 — Review chuyển phase kỹ thuật: GO WITH CAUTION sang Phase 1; năm sửa đổi bắt buộc (2026-10-08)

- Nguồn: văn bản “DL — Phase 0 Technical Transition”, ngày 08/10/2026, do tác giả cung cấp. Văn bản **tự mô tả là review kỹ thuật tự động**; đây là tóm tắt, không phải biên bản GVHD.
- Decision (theo văn bản): **GO WITH CAUTION** sang Phase 1 về kỹ thuật; **giữ G1**.
- Why (theo văn bản): hai bản review Phase 0 thấy framing và diagnostic contract đủ mạch lạc để đi tiếp **phần phân tích**. Chưa xác lập novelty hay cơ chế ở tầng mạng.
- Sửa đổi bắt buộc → nơi đã sửa:

| # | Sửa đổi | Nơi sửa |
|---|---|---|
| 1 | Sửa quy tắc cheap kill theo oracle repair | Contract §7(f); DL-006 |
| 2 | Làm rõ objective cumulative queue occupancy và ngữ nghĩa slot | Contract D1, D13, ghi chú dưới bảng §2 |
| 3 | Chống chỉnh timescale nhân tạo | Contract §6 quy tắc 7; §9 |
| 4 | Thêm null tương đương quyết định dựa trên bảo toàn | Contract §7(g)–(h), §6 quy tắc 8, §9; inventory EV-32/33; claim C10 |
| 5 | Làm rõ phạm vi mean → stochastic | Contract §0, D21, §5; claim NC16; brief |

- Cam kết Phase 1: (i) dựng và kiểm một ví dụ Stay/Switch không suy biến ($\Delta\ne0$, sinh từ plant); (ii) làm rõ cách $S_0$ xử lý belief, observation schema, baseline $M_0/M_1$; (iii) kiểm mode persistence và co giãn thời gian vật lý.
- Giới hạn scope: không mô phỏng quy mô lớn, không claim novelty mạnh, không khuyến nghị vận hành trước khi có evidence hỗ trợ.
- Tách gate: văn bản chỉ chấp thuận **tiến kỹ thuật**. Đóng Phase 0 chính thức (DL-009, closeout) và phê duyệt thật của GVHD là hai record riêng; entry này không thay record nào.
- Alternatives (văn bản không ghi; gợi ý để tác giả sửa): HOLD tới khi V3/V10/V11 đạt — không chọn vì Phase 1 là phân tích rẻ, đảo ngược được; GO trơn — không chọn vì chưa có novelty hay cơ chế mạng.
- Consequence: Phase 1 chỉ làm phân tích và exact nhỏ. Năm sửa đổi là làm rõ và hệ quả E0, không phải kết quả. Bản kỹ thuật đóng băng tại `contract-v0` theo DL-009/B, sau kiểm kỹ thuật; bài tác giả tự rà giữ ở V11.
- Revisit when: Phase 1 không dựng được ví dụ không suy biến trong domain (→ NARROW/REFORMULATE); người đọc độc lập hoặc GVHD yêu cầu khác.
- Ai quyết: tiến kỹ thuật — review kỹ thuật tự động tác giả cung cấp; chấp nhận và áp sửa đổi — **Doan Van Tai**, ngày áp dụng theo yêu cầu đóng phase: **08/10/2026**; bài tự kiểm còn V11.

## Kiểm tác động nếu đảo ngược — gợi ý cho bài tự kiểm

Bảng này là đối chiếu phụ thuộc tài liệu, **chưa phải bài tác giả tự làm**. Tác giả tự viết một dòng cho mỗi DL-003…DL-008, so lại với nguồn rồi ghi chỗ khác; khi thật sự xác nhận quyết định thì điền ngày và cập nhật trạng thái entry tương ứng.

| Entry | Nơi cần kiểm/sửa nếu đảo ngược |
|---|---|
| DL-003 | RQ card; contract §0/§4; brief, claim boundary và closeout; README nếu Main RQ thay đổi |
| DL-004 | Contract D3–D4/D7–D11, §3 và assumptions; lesson L0.3; interface và test quyền thông tin khi có code |
| DL-005 | Contract D13–D19, §4/§6 và reference cost ở §9; brief, claim boundary C7–C9, lesson L0.4, closeout; evaluator/oracle/contrasts khi có code |
| DL-006 | Contract D20–D22, §5/§7(f); inventory EV-26, claim C7/NC11; repair cards, cheap-kill/K10 trong plan khi có bản gốc; lesson L0.4 và thiết kế code Phase 3 |
| DL-007 | Legacy map, danh sách không mang sang, README/cách cài, provenance và dependency/import của khung code; thêm entry giải thích hướng mới, giữ nguyên genesis/archive tags |
| DL-008 | Contract D9/D12, §5/§7(c)/§8–§10; T00 nếu domain/giả định đổi; inventory EV-10/27/28/31, claim C9/NC12–13/NC15/U8–9; brief, lesson L0.6 và closeout; nếu đã tag thì tạo phiên bản mới, không di chuyển tag |
| DL-010 | Contract D1/D13/D21, §0/§5/§6 (7–8)/§7(f)–(h)/§8 AS3/§9; inventory EV-32/33; claim C10/NC16–17; brief; closeout; nếu đã tag thì tạo `contract-v0.1` |

[Brief File 7](00_research_brief.md) và khung lesson File 8 ([L0.3](lessons/L0.3_objects.md), [L0.4](lessons/L0.4_estimand.md), [L0.5](lessons/L0.5_legacy.md), [L0.6](lessons/L0.6_scope.md), [L0.7](lessons/L0.7_review.md)) đã tồn tại; bài tự làm/xác nhận còn chờ. Closeout File 9 đã ghi **phương án B/GO có điều kiện** tại [phases/PHASE_0_closeout.md](phases/PHASE_0_closeout.md); V3/V10/V11 mang sang Phase 1. Những chỗ master plan/PHASE_0 được dẫn theo File 6 vẫn cần đối chiếu bản gốc trước khi ghi đã sửa hoặc đã kiểm.


## L1.8 C–E — quyết định kỹ thuật ngày 22/10/2026

Tác giả **Doan Van Tai** đã chọn cấu hình đề xuất và “khóa v1 có điều kiện” trong phiên thực hiện. Không suy đó là bài tự làm, read-back hoặc independent approval. Mỗi entry dưới dẫn tới thẻ có đủ Decision/Why/Alternatives/Consequence/Test/Status.

### DL-011 — Reference Lstar (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **1**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-012 — Practical threshold1% (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **2**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-013 — Equivalence.5% / numerical budget.25% (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **3**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-014 — Packet·s và ratio-of-expectations (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **4**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-015 — Observation backlog/timestamp hidden mode (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **5**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-016 — S0 B2/shared belief (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **6**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-017 — Conditional stationary D / selected rates (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **6b**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-018 — Intermediate models DEFERRED (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **7**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-019 — Stage×role RNG schema, roots unallocated (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **8**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-020 — IΔ threshold εE*Cref (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **9**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-021 — R2/grid/calibration/reserve (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **10**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-022 — Feedback pending / conditional freeze (2026-10-22)

- Decision và năm trường kiểm chứng còn lại: thẻ **11**, [decision cards](lessons/L1.8D_decision_cards.md).
- Ai quyết: **Doan Van Tai**; adoption kỹ thuật theo profile/ngưỡng đã chọn, phần deferred/pending giữ đúng trạng thái thẻ.
- Revisit: khi A01/A04 phát hiện sai số, thiếu budget, hoặc có phản hồi độc lập; ghi version mới, không sửa tag cũ.

### DL-023 — Physical embedding và sửa kiểm refinement (2026-10-22)

- Decision: R2 exact symmetric embedding; λ0 teaching không có finite Tmode. Giữ A/B artifacts lịch sử; v1 dùng per-cell same-dt Cref, error budget.25%, fine-level reporting và triplet diagnostic.
- Why: Part B đã kiểm GS/gap/action có thể đổi theo slot; old toy tolerance1% không chứng nhận v1. M0 fixed split17.81% ởm128 khác hybrid≈11%; không đổi endpoint để khớp nguồn.
- Alternatives: R1 hoặc lấy Richardson làm proven limit bị loại. Consequence: final grid dt chờ A01, không tự mở contrast để khóa.
- Test: A/B audits, new tests và report CDE; trạng thái protocol LOCKED, convergence main-grid PENDING.
- Ai quyết: **Doan Van Tai**, theo yêu cầu thực hiện CDE trên nền A/B; không gán kết quả toy cho mạng thật.

### DL-024 — Contract-v1 conditional technical freeze, ngoại lệ V11 (2026-10-22)

- Decision: tạo annotated tag contract-v1 sau commit clean, push main và tag theo yêu cầu tác giả; G1/conditional GO cho chuẩn bị Phase2a/Phase3, A01 còn gate; HOLD Phase4 tới P0-V10.
- Why: tác giả chọn rõ “khóa v1 có điều kiện”; Part E cho phép tag trước P0-V11 khi ghi ngoại lệ, kế thừa closeout B. Công việc chuẩn bị được hoàn tất, không giả human feedback.
- Alternatives: unconditional GO hoặc tuyên bố V3/V11 đã pass bị loại. Consequence: P0-V3/P0-V10/P0-V11 và human/external feedback còn mở; source comparison partial; final dt/budget A01 chưa chứng nhận.
- Test: six consistency checks, actual JUnit/artifact audits, tag ancestry/remote checks ở verification receipt. Trạng thái thực tế theo closeout/report/receipt, không chỉ entry kế hoạch này.
- Ai quyết: **Doan Van Tai**; đổi sau feedback bằng phiên bản mới, không force tag, không gửi thông điệp cho người khác trong tác vụ này.

### DL-025 — Đối chiếu riêng DL-003…008; không thay lịch sử xác nhận (2026-10-22)

| Entry cũ | Kết quả đối chiếu kỹ thuật và adoption v1 | Còn thiếu |
|---|---|---|
| DL-003 | KEEP Main RQ nguyên văn; không khóa HC1 shape trước discovery | Tác giả tự diễn giải/read-back |
| DL-004 | KEEP tách plant/evaluator/estimator/model/oracle; hidden future, shared S | Tác giả tự làm bài phân loại |
| DL-005 | KEEP endpoint occupancy/oracle/regret; CHỐT conversion/Cref/threshold theo cards1–4 | Human construct review |
| DL-006 | KEEP endpoints/tie/cheap kill R00; làm rõ fixed-model D22, model randomness scope | Bài tự tính counterexample, feasible Phase8 |
| DL-007 | KEEP repo mới và legacy map; không migrate code cũ; thêm package kernels có tests | Bài tự kiểm legacy của tác giả |
| DL-008 | KEEP B2/hai neo; CHỐT schema, conditional D, stable grid và R2; intermediate DEFERRED | Final dt A01, primary-source/telemetry validation và self-check |

Ai chịu trách nhiệm: **Doan Van Tai**. Đây là đối chiếu và thực thi kỹ thuật trên các lựa chọn đã có/chọn trong phiên22/10, không ghi tác giả đã tự đọc lại hoặc hoàn thành bài. Entries lịch sử DRAFT giữ nguyên, P0-V11 không tự đóng.

### DL-026 — Post-hoc: lưới v1 có vùng Stay áp đảo theo từng path (2026-10-22)

> Soạn bởi Claude (AI) theo yêu cầu của tác giả; tác giả chưa xác nhận. Nhãn: **post hoc** — phát hiện sau khi khóa v1, **trước** mọi outcome trên lưới.

> **Tích hợp/kiểm chứng: Doan Van Tai, 23/10/2026.** Giữ ngày/provenance bản nguồn 22/10; không ghi lùi ngày chạy kiểm hoặc commit. HOLD A01/A04 trên v1 có hiệu lực theo kiểm kỹ thuật; các lựa chọn lưới v1.1 ở DL-027 vẫn DRAFT.

- Decision: giữ nguyên tag `contract-v1` (không di chuyển); **HOLD A01/A04 trên lưới v1**; chuẩn bị `contract-v1.1` theo [điều kiện thiết kế ĐK1–ĐK8](design/design_conditions_v1_1.md) (DL-027).
- Phát hiện gì: ở M01–M12 và S01 (13/28 ô), cả ba ô calibration (M01, M02, M10) và 6/12 ô held-out của reserve, $q_A(t_0)=\max(0,y_A-(5-u)\cdot\text{age})=0$ và lượng đến A dưới capacity dưới cả hai action. Theo tính đơn điệu, $C(\text{Switch},w)\ge C(\text{Stay},w)$ với mọi $w$; cả bốn pipeline chọn Stay; mọi regret và contrast bằng 0 theo cấu trúc. $s_{bt}$ không bắt được vì chỉ kiểm khả năng idle (tầng 1), không kiểm sự tồn tại của bài toán quyết định (tầng 2).
- Phát hiện bằng cách nào: một mock review do AI viết ngày 22/10 (không phải người đọc độc lập, không thay P0-V10); xác nhận bằng phân tích **chỉ dùng tham số** và support của $D$ đã có ([test](../tests/test_dominance_v1_1.py) `test_v1_grid_classification_documents_dl026`). Không tính $J$, gap, margin hay contrast nào trên ô lưới v1: `results/lessons/l1_8_cde` chỉ chứa support của $D$ và $s_{bt}$.
- Exposure: mock review đã tính **dấu** của $C(\text{Sw})-C(\text{St})$ trên 200 path ngẫu nhiên cho mỗi ô trong 13 ô bị áp đảo (contrast của các ô này bằng 0 theo cấu trúc, không lộ thông tin thêm). Ghi ở exposure register.
- Nguyên nhân thiết kế: (i) A tất định với $\rho_A<1$ và $y_A$ nhỏ; (ii) $\psi=(\lambda_A-\lambda_B)/\mu=-0{,}3$ ở mọi ô, làm lệch tải trung bình (không chứng minh Stay tối ưu ở mọi ô còn lại); (iii) $h=z/(1-\eta)$ gộp trục horizon vào $z$; (iv) $y_A=y_B$; (v) calibration chọn ở $z$ nhỏ nhất; (vi) screen chỉ có tầng 1. Một phần đến từ hướng dẫn L1.8 Part C (AI).
- Không đổi: ngưỡng, dung sai, $C_{\text{ref}}$, R2, B2, objective, luật hoà (ĐK8).
- Ai quyết: **Doan Van Tai — chờ xác nhận**.

### DL-027 — Điều kiện thiết kế v1.1 và nới quy tắc chẩn đoán (2026-10-22)

> Soạn bởi Claude (AI) theo yêu cầu của tác giả; mọi lựa chọn là đề xuất, chờ xác nhận ([§11 của file điều kiện](design/design_conditions_v1_1.md)).

- Decision: thêm tầng 2 của không suy biến bằng **ĐK1** (bốn điều kiện áp đảo giải tích SD1, SD2, WD1, WD2; code `src/smr/dominance.py`) và **ĐK2** (chẩn đoán chỉ dùng plant $p_{\text{sw}}=P_D(a^*=\text{Switch})$, khoảng chấp nhận đề xuất $[0{,}1;0{,}9]$, bảy luật chống chọn lọc). Tách $y_A$ khỏi $y_B$ (ĐK3) và $h$ khỏi $z$ (ĐK4, toạ độ $r_h$). Thêm trục $\psi$ với mức hai phía của 0 và nền ON/OFF cho A (ĐK5). Ô kiểm âm chỉ là ô SD; ô WD là "oracle-hằng" (ĐK6). Calibration chỉ trong ô `candidate` có $p_{\text{sw}}$ trong khoảng (ĐK7).
- Why: DL-026. Riêng ĐK2 nới quy tắc "không tính giá trị action thật để chọn thiết kế" của `grid_v1.md`, **chỉ cho $p_{\text{sw}}$**, vì nó đo sự tồn tại của bài toán quyết định chứ không đo contrast; $G_{S\mid M_1}\le\min(p_{\text{sw}},1-p_{\text{sw}})\cdot\max\lvert\Delta\rvert$.
- Alternatives: giữ lưới v1 và chỉ đổi calibration (bị loại: các ô còn lại có $\psi=-0{,}3$, chưa biết có bài toán quyết định); chỉ dùng ĐK1 không có ĐK2 (bị loại: ĐK1 chỉ là điều kiện đủ, không kết luận được M13–M24); A tất định với $y_A$ transient (giữ làm phương án yếu, chỉ dùng nếu tác giả chọn).
- Consequence: lưới v1.1 chọn ở B2–B4 theo thứ tự commit trong file điều kiện; tag `contract-v1.1` sau sáu kiểm nhất quán; A01 chạy lại trên calibration mới.
- Test: 5 test ĐK1 (vét cạn 9.216 state, $M_0$, luật hoà, phân loại v1, input lỗi); ba mutant bị bắt. ĐK2 chưa được tính trên ô nào.
- Ai quyết: **Doan Van Tai — chờ xác nhận**.

**Bổ sung tích hợp 23/10/2026:** 5 test nguồn cộng3 test edge cases; số thực chạy và mutation checks ở [report B1](../results/lessons/l1_8_v1_1_b1/report.md). Không dùng `tol` để bỏ state probability>0 khi gán nhãn ô. R2 có probabilities từ exp; phương pháp xác nhận dấu J/độ chính xác và Δt screen **chưa chọn**, không ghi Fraction(float) là exact physical law. Nhãn ngoài khoảng nhưng p_sw chưa bằng0/1 là oracle-lệch/gần-hằng, không phải hằng đúng nghĩa. B3 HOLD trước khi chốt các lựa chọn và commit protocol. Không chạy p_sw hoặc chọn số lưới ở B1.

**Sửa kết luận coverage của nguồn:** trong9.216 cases gốc, SD1/WD1 có3.456 cases mỗi điều kiện nhưng SD2/WD2 đều0. Vì vậy claim “đã vét cạn cả bốn điều kiện” chưa được chứng minh bằng bộ đó. Runner đã FAIL ở coverage assertion dù154 tests PASS; log/JUnit giữ trong first_run. Thêm3.456 verification cases low-arrival/H1 để kiểm đủ cả bốn điều kiện; không đổi grid/threshold/ĐK8.

### DL-028 — Sửa căn cứ của DL-024 về P0-V11 (2026-10-22)

> Soạn bởi Claude (AI) theo yêu cầu của tác giả.

- Decision: ghi nhận **xung đột nguồn do mock review báo**: Part E cho phép ghi ngoại lệ tag trước P0-V11, còn review dẫn PHASE_1 §17.1 yêu cầu HOLD khi V11 chưa đạt. Bản đầy đủ PHASE_1 chưa có để đối chiếu câu gốc, nên không tuyên bố đã xác minh trực tiếp mâu thuẫn. Tag `contract-v1` giữ nguyên như một bản đóng băng kỹ thuật có ngoại lệ đã biết; không dời tag.
- Consequence: trước khi tag `contract-v1.1`, phải xử lý trạng thái P0-V11 và đối chiếu nguồn gate. Attachment bổ sung nhắc bài tự tính ngoài vở ngày22/10; đây là lời trong nguồn, phiên tích hợp23/10 chưa có ảnh/bài làm hoặc record read-back để kiểm. Không tạo commit `[kín sách]` thay tác giả; P0-V11 vẫn OPEN. B1 không tạo tag mới.
- Ai quyết: **Doan Van Tai — chờ xác nhận**.

**Cập nhật có hiệu lực 23/10/2026, Doan Van Tai:** hai review mới cùng xác nhận câu ngoại lệ đến từ lesson Part E và người soạn lesson nhận đó là lỗi. Áp dụng **HOLD** theo master-plan được review dẫn; ngoại lệ Part E không còn là căn cứ mở gate hoặc tag mới. Review nêu PHASE_1 v1.0, SHA rút gọn `47f9a335…d4d7ba`, dòng332/1953, nhưng full file chưa có: đây là provenance do reviewer báo, chưa phải hash/câu gốc tự kiểm. Tag lịch sử giữ tại `6bb631f`, không di chuyển. [Closeout active](phases/PHASE_1_closeout.md), README và DL-031 cùng ghi HOLD. Tác giả yêu cầu heads-up giữ nội bộ, chưa gửi.


### DL-029 — N2(a): một observation mỗi ô, bổ đề E0 (2026-10-23)

- Decision: giữ một observation/cell, b=D; bổ đề và các companion diagnostics ở [mốc2](design/decisions_v1_1_m2.md). Tác giả giao thực hiện phần kỹ thuật/lựa chọn có căn cứ trong review; không suy thành understanding artifact.
- Why: conditional map theo observable y, attribution rõ. GM là0 hoặcabs(EΔ) tùy action; không đọc GM0 là mean model đủ cho mọi tình huống. EΔ0 có thể làm GM0 dù action khác nhau.
- Alternatives: trộn observations làm S0 policy thay theo y; giữ cho sensitivity sau này, cần nhiều hơn hai quantile để tái dựng đúng law.
- Consequence: A04 phải kèm EΔ, model gap bias, EΔ+/EΔ−. Bổ đề/proof lập trình là reference, không tạo commit kín sách thay tác giả.
- Test: canonical rational và exact exhaustive/mixture/tie cases trước mở B2; kết quả trong report mốc2.
- Ai chịu trách nhiệm: **Doan Van Tai**; bài tự chứng minh/read-back còn OPEN.

### DL-030 — N1: idle-based gap, certificates và precision alarm (2026-10-23)

- Decision: gap theo weighted idle identity; rational/integer coordinates; assert conservation==0, SD≥0, WD≤0. eps_num=1e−9*Cref, alarm uncertified near-zero mass>.01; numeric band không tự thay strict true oracle.
- Why: subtraction hai tổng có thể chọn Switch trên structural ties. Gán Stay cho mọi small negative gap sẽ đổi estimand/R11 và điều kiện bổ đề; certificate/error escalation bảo vệ định nghĩa thay vì sửa kết quả.
- Alternatives: clamp dấu theo chứng chỉ hoặc gọi Fraction(float) exact physical R2 bị loại. High-precision phải phân biệt rounded-input law với exp law thật. B3 không tính Lstar chỉ để đặt band.
- Consequence: unresolved precision phải HOLD và tăng precision; báo riêng structural ties và uncertified mass. B3 chỉ p_sw/numerical diagnostics, companion margins chờ A04.
- Test: deterministic structural tie fixtures, SD/WD signs, exact rational path reference và mutant subtraction phải fail. Không dùng số105/114/183 từ review làm số đo của phiên nếu script nguồn chưa có.
- Ai chịu trách nhiệm: **Doan Van Tai**, theo ủy quyền triển khai; D16 v1 giữ lịch sử, supplement v1.1 ở mốc2/protocol.

### DL-031 — N3–N6 và quyết định trước grid, mốc2 (2026-10-23)

- Decision: toàn bộ11 lựa chọn tại [mốc2](design/decisions_v1_1_m2.md), A/B độc lập ON/OFF, stationary có conditional prior, nền A amplitude±6 không đổi theou; ψ sign hai phía0 ở ηcore; highηspoke center ổn định; inverseκ là relative-age axis, z derived.
- Why: tránh nền A phụ thuộc managed load để ép dạng đóng, tránh confound u và background. Generic feasibility không thay fixed-amplitude feasibility. Sửa claim reviewer: η.9 cho postload.9+.1ρB, không luôn≥.95. Quantile scaling chỉ gần đúng finite slot.
- Consequence: plant D4/D7/D12/D20/D22 đổi, splits không so trực tiếp với v1; p_sw hai mức phải ổn định để calibration; selected grid không đại diện prevalence mạng thật. Numeric stationary solver cần tail/law/posterior error và budget. Vượt budget không bỏ ô để đẹp.
- Gate: cập nhật active Phase1 closeout HOLD; PHASE_1 source có SHA rút gọn47f9a335…d4d7ba và line332/1953 do hai review báo, chưa có byte gốc để tự kiểm. Không dùng ngoại lệ Part E làm căn cứ GO. Tagv1 tại6bb631f không di chuyển.
- Ai chịu trách nhiệm: **Doan Van Tai**. Không gửi heads-up theo chỉ dẫn23/10; lưu draft. Commit mốc2 trước candidate computations; chưa tạo grid/contrast/tagv1.1 tại mốc này.

### DL-032 — Phần A: author attestation và budget trước screen (2026-10-23)

Doan Van Tai xác nhận trực tiếp đã hoàn thành V1/V8/P0-V3/P0-V11 ngoài repository, không lưu artifact. Ghi **author-attested**, không phải independently verified. Protocol/budget/center/reserve/control và quy tắc giữ observation vật lý qua refinement tại [Phần A](design/v1_1_A_protocol.md). Ưu tiên solver sparse rồi spectral, giữ nguyên10 bộ chính; thay thiết kế nếu có phải có DL trước outcome. Không bịa full SHA/câu gốc PHASE_1 chưa có. Gate kỹ thuật và P0-V10 giữ theo điều kiện thực đạt.

### DL-033 — A1: dùng spectral certificate, giữ nguyên20 trường hợp (2026-10-23)

Sparse longdouble đã chạy: reference(-2,+1) đạt law bound; (-17,+7),keep.99 có cận2.293e−10 vượt1e−10. Không bỏ rounding guard để qua test. Chọn phương án phổ trước candidate J, giữ nguyên10 bộ ×2 mức. Spectral approximation được chứng nhận bằng interval balance/normalization, independent Lyapunov tail và explicit hitting-time bound; không gọi root finder chính xác. 20/20 law/posterior/quantiles PASS, 10/10 đối chiếu v1 có allowance riêng cho chuyển thành mảng. Test bỏ gamma bị bắt. Proof T04 và results/lessons/v1_1_a1. Cap50.000 thay bằng4GiB/1200s đã khai báoC0; không nới sai số hoặc đổi thiết kế.

### DL-034 — B2: control SD1 cần tách khỏi conservation (2026-10-23)

ĐK1 trước mọi J cho thấy N02 với A90/B100,h.25 là conservation-cell vì A cũng không thể idle. Đặt yA=0 (observation có xác suất dừng dương), giữ B100 vàh.25 để chứng nhận SD-cell riêng. Giữ toàn bộ lần dựng đầu và support/labels; không thay main λA, không dùng lượt redesign B4. Các main M13/M15/M17/M20 là WD-cell vẫn giữ, chỉ loại khỏi calibration sau screen theo protocol.

### DL-035 — B4: dùng đúng một lượt redesign tải A sau screen đầu (2026-10-23)

Initial8/22 in, cần15/22. Chọn duy nhất λA={7;7.2;8.1}, center7.2, trước mọi p_sw mới. Căn cứ chỉ là screen đã khai báo: B90 ởλ6.5 thường dưới.1, B50 ởλ7.5 và mọi mứcλ8.5 thường trên.9. Nâng mức thấp, hạ mức giữa và mức dương; ψ={−.1;−.08;+.01} giữ hai phía0; highηcenter pre-load.9<1. Biên độ±6, κ/quantile/r_h/η và threshold không đổi. Chọn mức có lattice đơn giản để không gây nổ solver/DP; không quét thử nhiều λ. Controls/reserve giữ thiết kế trước. Đây là redesign hậu screen được protocol cho phép, không pretended preregistration ban đầu. Giữ đủ22 main và mọi out; nếu lần hai không đạt15 thì NARROW/REFORMULATE, không lượt thứ hai, không formal freeze/tag v1.1.

### DL-036 — B4 kết thúc: REJECTED / NARROW REQUIRED (2026-10-23)

Đã dùng đúng một redesign:8/22→11/22, yêu cầu15/22. Không unstable/precision unresolved trong88rows; kết quả không đạt là screen thiết kế, không phải lỗi số học. Giữ toàn bộ28ô+6reserve trong grid_v1_1 decision record; không chọn calibration khi grid rejected. N01/N02 SD-cell,N03/N04 conservation-cell; chưa chạy contrast. Không thử lầnλ thứ hai, không bỏκ3 hoặc ôout sau khi xem outcomes để gọi PASS. B5 đánh giá readiness nhưng không được nâng draft thành contract chính thức hoặc tagv1.1. Cần một protocol NARROW/REFORMULATE mới trước nghiên cứu tiếp; không xem thất bại của screen convention là bác bỏ hypothesis của MainRQ.

### DL-037 — B5 readiness: không promote khi B4 rejected (2026-10-23)

Sáu kiểm thực chạy:4PASS,1PARTIAL(full Final Review source chưa có),1FAIL(grid11/22<15/22 và chưa calibration; numeric cross-constraintsPASS). Solver20+20certificates, full177/177PASS, law error max1.02853e−29/posterior4.000001e−16,88screenrows unresolved0. Native subtraction mutant lọt test dyadic đầu; giữ PASS, thêm97/100 vào cùng test đã có, mutantFAIL; không thay kernel hoặc candidate outcomes.136B reference comparisons maxTV1.31666e−14. Draft definitions/boundary/brief đã cập nhật, không promote thành bản chính thức hoặc gắn tagv1.1. Author-attested human gates giữ đúng xác nhận trực tiếp; nguồn digest chưa tự kiểm full, heads-up chưa gửi. Báo cáo/results/config/plot và các log tại results/lessons/v1_1_a6, index notes/verification/v1_1_part_a/README.md. Bước tiếp theo phải là protocol NARROW/REFORMULATE mới, không lượt redesignλ thứ hai.

### DL-038 — REFORMULATE hệ tọa độ lưới: neo theo ranh giới quyết định, horizon vật lý (2026-10-23)

> Văn bản do AI soạn theo yêu cầu thực hiện của tác giả. Tác giả quyết định áp dụng; lý do chưa được tác giả tự viết lại (PHASE_1 §5.4, luật 5) — mục mở.

- **Decision:** nhãn **REFORMULATE**, không phải NARROW, vì trục so sánh đổi định nghĩa chứ không chỉ thu hẹp vùng. $\lambda_A$ thôi là trục thiết kế và được neo cho từng lát (mục tiêu $p_{\text{sw}}$ 0,3/0,7, thang 0,25, cửa sổ ±0,15 ở dt và dt/2, kiểm dải ở dt/4, nhãn ĐK1 `candidate`). Horizon là số giây cố định: 8 s ở lõi, 2 s ở nan hoa. Bỏ yêu cầu "ψ hai phía của 0" và luật "≥ 15/22, một lượt redesign"; thay bằng luật neo có điểm dừng. Held-out được neo bằng cùng luật. Luật calibration mới. Chi tiết: [protocol v1.2](design/v1_2_protocol.md).
- **Why:** [thử nghiệm](explore/reformulate_grid_report.md) cho thấy ranh giới dịch theo $y_B$ và $\kappa$ (ví dụ $p_{\text{sw}}=0{,}5$ tại $\lambda_A\approx7{,}38$ so với $\approx6{,}56$), nên một $\lambda_A$ chung không thể đặt mọi ô vào dải. P4 là thủ tục duy nhất có mọi ô chính vừa trong dải vừa trong budget. 38 ô đề xuất vẫn trong dải tới dt/4 (trôi ≤ 0,003) và đều `candidate`.
- **Đổi ý nghĩa phép so sánh:** từ "cùng tải" thành "cùng độ khó". $\lambda_A$ đồng biến với điều kiện, nên khác biệt giữa hai lát không được quy riêng cho một trục. 34/38 ô có $\psi<0$, 3 ô $\psi=0$, 1 ô $\psi>0$; khoảng $[-0{,}2;+0{,}05]$. Mọi kết quả có điều kiện gần ranh giới quyết định, không đại diện tần suất.
- **Ghi trung thực:**
  1. $h=8$ s ở lõi và $h=2$ s ở nan hoa được chọn **sau khi** thấy $p_{\text{sw}}$. Đây là lựa chọn hậu nghiệm; chấp nhận được vì $p_{\text{sw}}$ là đại lượng thiết kế, không phải outcome.
  2. Thông điệp commit `cde9944` ghi "before stage-1 results" là không chính xác: lúc đó đã có 5/480 dòng (chưa xem). Đính chính tại đây và trong §8 của kế hoạch; không viết lại lịch sử git.
  3. Nhánh thử nghiệm đã được push công khai ngày 23/10. Các giá trị $p_{\text{sw}}$, nhãn và budget của thử nghiệm đã công khai (ghi trong exposure register). Chưa ai thấy contrast.
  4. Có 3 ô nằm ở đáy thang $\lambda_A=6$ (từ các lát thử nghiệm S05, S18, S27). Protocol ghi rõ: đáy 6 là giới hạn vật lý, không mở thang; báo `bracketed`/`floor`/`ceiling` cho từng ô.
  5. "Cùng độ khó" chỉ là xấp xỉ: 3 ô lệch mục tiêu hơn 0,1 (nhiều nhất 0,13). Phase 3 báo $p_{\text{sw}}$ thực của từng ô.
  6. Bốn commit thử nghiệm giữ nguyên hash (và dòng co-author trong message) vì các file config trích dẫn chúng làm bằng chứng thứ tự thời gian. Từ merge `87dcd53`, commit chỉ đứng tên tác giả.
- **Alternatives:** NARROW về 11 ô của v1.1 (mất trục tải; còn ô vượt budget); thiết kế đối xứng P1/P2 (≤ 63% ô đạt); neo với $r_h=1$ (P3, 7 ô vượt budget).
- **Consequence:** contract v1.2 thay bản nháp v1.1 ở D1, D2, D4 và phần lưới; ĐK8 và plant v1.1 không đổi. Held-out được neo lúc chốt lưới; $p_{\text{sw}}$ của held-out bị cấm làm biến cho $H_0/H_1$. G1 giữ nguyên.
- **Ai quyết:** **Doan Van Tai** (yêu cầu thực hiện ngày 23/10, sau khi đọc báo cáo thử nghiệm và một review riêng).

### DL-039 — Chạy chính thức lưới v1.2: ACCEPTED (2026-10-23)

- **Kết quả:** chạy theo [protocol v1.2](design/v1_2_protocol.md) (commit `d696eef`, trước lần chạy). Tái lập **tuyệt đối** thử nghiệm: 200 dòng thang và 38 ô kiểm ở dt/4, **0 chỗ lệch**; tập ô trùng `proposed_v1_2_cells.csv`. Lưới **ACCEPTED**: 38 ô chính, mỗi ô trong $[0{,}1;0{,}9]$ ở dt, dt/2, dt/4, nhãn `candidate`, budget tối đa $6{,}8\times10^{10}$ ở dt/16. Hai mục tiêu không neo được đúng như dự kiến: lát V09 và V10 ($\kappa$ 3, B q50), mục tiêu 0,3, kiểu `floor`. [Bảng lưới](design/grid_v1_2.md).
- **Held-out:** 6/6 lát neo được cả hai mục tiêu, thành 12 ô (R01–R12). Tất cả trong dải ở ba mức, `candidate`, có điểm kẹp, budget tối đa $8{,}7\times10^{10}$ ở dt/16. Đây là exposure mới (chỉ $p_{\text{sw}}$, nhãn, budget).
- **Ô kiểm âm và đầu dò:** nhãn đúng kỳ vọng: N01, N02 SD-cell; N03, N04 conservation-cell; W01, S01 WD-cell; P01 conservation-cell; P02 WD-cell.
- **Calibration A01: M01, M09, M22** ($\kappa$ 0,3 / 1 / 3). **Lỗi đã sửa:** lần chọn đầu cho M10 thay vì M09, vì khoảng cách tới tâm được tính bằng số thực và $(0{,}7-0{,}3)/0{,}4=0{,}9999999999999999$ làm vỡ một trường hợp hòa chính xác. Protocol quy định hòa thì chọn mã nhỏ hơn. Code được sửa để dùng phân số chính xác và chỉ chạy lại bước chọn (`--reselect`); **không tính lại gì trên plant**. Lần chọn đầu được giữ trong `results/lessons/v1_2/selection_first_attempt.json`.
- **Không có:** $J$, $L_*$, margin, belief, pipeline, contrast hay regret ở bất kỳ ô nào.
- **Consequence:** đủ điều kiện khóa contract v1.2 (§8 của protocol). A01 chạy trên M01, M09, M22.
- **Ai quyết:** **Doan Van Tai** (yêu cầu thực hiện ngày 23/10).

### DL-040 — L2.1–L2.3: lưu artifact sau exposure, formal gate còn HOLD (2026-10-24)

- **Người phụ trách:** Doan Van Tai, theo yêu cầu “hoàn tất hết” sau khi đối chiếu
  checklist; AI thực hiện code, lookup và note, không ghi là tác giả đã tự đọc.
- **Decision:** hoàn thiện literature scaffold/claims/forecasts, T03 v2, code
  tái lập, CSV/JSON/log/tests, matrix/boundary/source notes và đáp án tham khảo.
  Bootstrap commit5ab4750; proof commit3870931. Giữ deviation dự đoán đã exposed
  trước lưu, không backdate/fake prereading tag hoặc tính blind calibration.
- **Kết quả thực chạy:** 21.952 exact toys, I1–I6 mỗi invariant0 violations;
  wrong-belief410, mean-state3528, ignored-mode5730, tie-control0;
  17/17 P11 checks, 9/9 lesson tests và 202/202 full-suite tests PASS.
- **Nguồn:** P11/SOB14 AI targeted primary reading; B82/MAB11 PDF403, B82 OA
  fallback không có PDF; E07/SOC12 abstract-only. Note giữ mức thật. Không dùng
  theorem chưa đọc hoặc tạo L-self thay người thật.
- **Corrections:** P11 Eq2.7 là EVPI(delta) diễn giải upper bound EVMI; D21 khác
  estimand. Biết theta chưa có nghĩa biết delta(x) ở hidden x. C7 giới hạn cho
  state repair fixed-M0; matched same-info M1 tối ưu nên GM/GMgivenS1 vẫn bound
  model repair. Giữ Main RQ, contract/grid/thresholds và historical tags.
- **Consequence:** technical artifact hoàn thành; formal Part A HOLD do L-self,
  proof/read-back/đọc lại, missing prereading commit và source-reading limits.
  G1/HOLD Phase4 giữ nguyên. Không tự freeze L3.3, chạy Phase3, gửi heads-up
  hoặc push từ nhiệm vụ này. Học tiếp L2.4 được.
- **Evidence:** [report](../results/lessons/part_a/report.md),
  [prior boundary](literature/prior_boundary.md),
  [artifact audit](../results/lessons/part_a/artifact_audit.json).

### DL-041 — L2.6 Part B: prior và interpretation threat (2026-10-26)

- **Người phụ trách:** Doan Van Tai. AI triển khai theo attachment được yêu cầu;
  không ghi tác giả đã tự đọc P13 hoặc qua Understanding/Gate.
- **Decision:** lưu note P13 journal/numbering, phép nhân T và examples;
  append T-H1 để diễn giải đúng D13, không sửa cost/horizon/law/thresholds.
- **Evidence:** bản journal CWI36trang, Eq2.4/2.7, Theorem1, Prop4–5,
  §5.1–5.3 và §6/tr289 targeted. Arxivv1 chỉ kiểm numbering/đoạn tương ứng.
  122exact teaching checks PASS; không P13 replication hoặc grid outcomes.
- **Corrections:** ON overload không tự global instability; D13 có endpoint qH;
  S1 quadratic cần density/bias assumptions; M0 fluid-like time-varying không
  đồng nhất constant-drift Lévy. K-F levels kế thừa PartA, không downgrade/mạo nhận.
- **Consequence:** K-F1…3/K-H1…4 và H1-Q02 được ghi trước A05; chưa chọn H1.
  Q-L27-01 về decision geometry/Γ chuyển L2.7. G1/HOLD Phase4 giữ nguyên;
  scientific dependency A4/L2.9, human L-self và formal Gate còn mở.
- **Artifact:** [report](../results/lessons/l2_6/part_b/report.md),
  [P13](literature/papers/P13.md), [boundary T-H1](01_claim_boundary_v1_2.md#t-h1--giới-hạn-diễn-giải-do-horizon-hữu-hạn-26102026).

### DL-042 — Gate L (Phase 2): nhãn Main RQ và trạng thái Gate (2026-10-26)

- **Người phụ trách / quyết định:** Doan Van Tai. **AI (Claude) soạn và chọn nhãn tạm
  theo ủy quyền tác giả** ("đóng vai tác giả và thực hiện mọi thứ cần tác giả thực hiện",
  hội thoại 26/10). Tác giả chưa tự chấm, chưa tự đọc nguồn quyết định nhãn; AI đã thấy
  nhãn tạm của mentor trước khi chấm (exposure).
- **Main RQ:** **KEEP** — chưa thấy nguồn đã đọc trùng cả E, M, R; nguồn gần nhất WM26
  dùng repair nhập tương lai thật (F.1 Eq10 PDF22, §9 PDF9), khác D20/D15 và khác regime.
- **Nhãn claim (tạm, AI ủy quyền):** PC1 DROP (giữ framing), PC2 NARROW, PC3 KEEP câu chữ
  / framing NARROW, PC4 HOLD (chờ A05), PC5 NARROW, PC6 NARROW. Chi tiết và "sẽ đổi nếu":
  [prior_boundary](literature/prior_boundary.md#l29--nhãn-tạm-do-ai-chấm-theo-ủy-quyền-tác-giả-26102026).
- **Gate L: HOLD.** L1 ⚠️ (nhãn tạm do AI ủy quyền, tác giả chưa tự chấm) · L2 ❌
  (L-self 0/19) · L3 ⚠️ (code/mutant PASS, phép dẫn T03 do AI) · L4 ✅ (OεRE draft) ·
  L5 ⚠️ (4 phiên có log; Tier1 AI-T; **deviation:** Part2 không lưu log từng rank,
  follow-up 157 record có raw; luật dừng 2×20 chưa đạt; forward P07 chưa chạy được) ·
  L6 ✅ (DL này) · L7 ✅ (claim boundary, inventory EV-37…45, exposure cập nhật 26/10) · L8 ❌.
  HOLD là hệ quả của luật PHASE_2 §17 (thiếu điều kiện validity), không phải lựa chọn.
- **Điều kiện để đổi trạng thái:** tác giả tự chấm hoặc xác nhận nhãn; L-self tối thiểu
  WM26 §5/F.1, R02 §5, R04 §3, P11 §2.4, P02 §2.2.4/§3.3, S11 §III, P12 Def1 (ghi vào
  [author_reading_record](literature/author_reading_record.md)); tác giả tự dẫn T03 kín
  sách; một người thật đọc prior boundary (L8) để có thể lên GO có điều kiện.
- **Hệ quả cho Phase 3:** được học Phase 3 và viết **nháp** prediction card; **không commit
  L3.3** trước khi có nhãn do tác giả xác nhận và L-self WM26; prereg A05 cần nhãn PC4/PC5
  chính thức; mọi pattern từ A04 theo luật post-discovery. Không gắn tag `phase-2-closeout`.
- **Không thay đổi:** contract v1.2, lưới, thresholds, D25, held-out, G1, HOLD Phase 4,
  bảng forecast PC (byte-unchanged).
- **Evidence:** [prior_boundary](literature/prior_boundary.md),
  [related work](literature/related_work_skeleton.md),
  [claim boundary Phase 2](01_claim_boundary_v1_2.md#ranh-giới-với-prior-phase-2--26102026),
  [literature_audit_part2](literature/literature_audit_part2.md), [search_log](literature/search_log.md),
  [closeout](phases/PHASE_2_closeout.md), [report](../results/lessons/l2_9/part2/report.md).

- **Đính chính DL-042 (26/10/2026):** "§9 PDF9" ở mục Main RQ phải đọc là **§8 PDF9** (WM26 Limitations and Conclusion); quyết định không đổi. [Chi tiết](../results/lessons/l2_9/wm26_author_reading/check.md).

### DL-043 — Gate L: GO có điều kiện (2026-10-26)

- **Người phụ trách / quyết định:** Doan Van Tai, yêu cầu "mở tất cả cái chặn… tiếp theo tôi sẽ
  sang phase 3". Tác giả xác nhận trực tiếp (author-attested, cơ chế DL-032) đã tự đọc ngoài vở
  WM26 §4.1/§5/F.1, R02 §5, R04 §3, P11 §2.4, P02 §2.2.4/§3.3/Bảng 2, S11 §III Eq10, P12 Def1/§3.1,
  đã **tự dẫn T03**, và **xác nhận nhãn tạm**; chưa có người đọc thật. Lời giải nằm trong vở,
  không có artifact trong repo, không kiểm độc lập. [Xác nhận nguyên văn](../results/lessons/l2_9/gate_l/author_attestation.json).
- **Main RQ: KEEP.** Nhãn chính thức: PC1 DROP (framing), PC2 NARROW, PC3 KEEP câu chữ/framing
  NARROW, PC4 HOLD (A05), PC5 NARROW, PC6 NARROW ([prior_boundary](literature/prior_boundary.md)).
- **Gate L: GO có điều kiện.** L1 ✅ (author-attested) · L2 ✅ bộ tối thiểu author-attested; SOB14/
  P04/P13/P03/R06 giữ AI-T với lập luận bền nhãn · L3 ✅ (author-attested) · L4 ✅ · L5 ⚠️ deviation
  (Part2 thiếu raw từng rank; follow-up có raw; luật dừng chưa đạt; forward P07 chưa chạy) ·
  L6 ✅ (DL này) · L7 ✅ · **L8 ❌** → theo PHASE_2 §15/§17 tối đa GO có điều kiện. Thay HOLD của DL-042.
- **Điều kiện kèm theo:** (1) một người thật đọc prior boundary + related work (L8, [gói](meetings/phase2_reader_packet.md));
  (2) tác giả tự viết hai mục đầu của [PHASE_2_closeout](phases/PHASE_2_closeout.md) và có thể chép
  lời giải ngoài vở vào [author_reading_record](literature/author_reading_record.md);
  (3) bản journal R01 (Springer) và R34 (IEEE TAC 1995) khi lấy được — không chặn.
- **Hệ quả cho Phase 3:** mở. L3.3 prediction card được commit (chỉ chứa phần claim còn đứng,
  theo danh sách "không được claim là mới"); **A01 chỉ sau khi L3.3 đã commit** (M01/M09/M22 nằm
  trong vùng K2/K5/Q5); A05 khóa H1/null/metric/split trước held-out (D25); pattern mới từ A04 theo
  luật post-discovery. Điều kiện Phase 1 còn nguyên: gửi heads-up/memo GVHD **trước A04** (V9);
  **HOLD Phase 4** tới khi có người đọc độc lập (P0-V10).
- **Không thay đổi:** contract v1.2, lưới, thresholds, D25, held-out, G1, bảng forecast PC.
- **Tag:** `phase-2-closeout` gắn trên commit ghi DL này.

### DL-044 — Mở Phase 3: điều kiện còn mở và bản hiện hành (2026-10-27)

Người phụ trách: **Doan Van Tai**. AI triển khai theo lesson L3.1 Part 3 được tác giả
cung cấp; không có xác nhận mới về tự viết, người đọc hay gửi GVHD.

1. **V9: chưa gửi; giữ điều kiện (c), A04 chờ.** Không sửa điều kiện DL-043 hoặc nhận GVHD đã đồng ý.
2. **Người đọc: P0-V10 và L8 OPEN.** Chưa có buổi đọc; có thể chung buổi 30–45 phút nếu đủ phạm vi.
3. **Các mục tự viết: OPEN.** Lý do DL-038 và hai mục đầu closeout Phase 1/2 chưa có lời tác giả; AI không điền thành ownership evidence.
4. **Luật provenance:** L3.3 commit trước mọi A01; A05-F khóa trước A05-T; A04 là discovery; giữ exposure thật, không gọi dự đoán sau outcome là confirmatory.

- **Làm rõ P0-V10:** người thật đọc contract **v1.2 đang thực thi** (D1–D25 ở tag
  `contract-v1.2`), brief và claim boundary cùng addendum Phase 2 hiện hành; ghi commit
  đọc và phản hồi. Điều kiện gốc nói v0; đọc riêng bản đã thay không đủ. P0-V10 chặn
  **thực thi Phase 4**, không chặn học/triển khai Phase 3. L8 cần prior boundary và related work.
- **Hai nghĩa V9:** P0-V9 = timescale có nguồn/nhãn chưa có nguồn; P1-V9 = heads-up/memo
  GVHD trước A04. Không chuyển trạng thái giữa hai nghĩa. Read-back với bạn học giảm
  ER3, không loại ER8; nếu sau này sửa V9 phải ghi chấp nhận rủi ro tính lại A04 khi hướng đổi.
- **Bản hiện hành:** thêm [PHASE_3](phases/PHASE_3.md), [experiment index](03_experiment_index.md),
  khối con trỏ README; chuyển bản README cũ sang progress log, không dùng history làm nhật ký.
  Plan v2.0 đầy đủ không có trong workspace: PHASE_3 mới ghi rõ phạm vi tái dựng từ lesson.
- **Rebuild:** bốn hàm dựng cell/law/D từ experiments vào `src/smr/cells.py`, giữ nguyên
  file nguồn; so khớp trên main/calibration/control, không dựng D held-out. Không triển khai
  engine L3.2 hoặc tính outcome Phase 3. Contract/grid/thresholds/nhãn PC/G1 giữ nguyên.
- **Evidence:** [lesson và report thực chạy](../results/lessons/l3_1/part3/report.md).
  Mục tự viết không chặn bước thực thi; chưa có evidence để gắn Understanding PASS.

### DL-045 — L3.2: phạm vi trước chạy, precision và ownership (2026-10-27)

Người phụ trách: **Doan Van Tai**. Triển khai bốn phần lesson được cung cấp.
Ghi trước các lần chạy mới: [config](../results/lessons/l3_2/config.json),
[kết quả mong đợi trước code](../results/lessons/l3_2/expected_before_code.json).

- Engine mới ở `experiments/A00_engine/`: chưa có T05 do tác giả viết/author-attested
  nên chưa promote vào `src/` (Part4 §4/X.3 #2). `src/smr/cells.py` đã tồn tại từ L3.1;
  giữ nguyên body và provenance. T05 AI hỗ trợ không tính là lời giải của tác giả.
- Chỉ chạy J/gap/contrast trên toy. Bước migration theo Part4 §11 là ngoại lệ **D-only**:
  M01/M09/M22/N01/N02/N03/N04/W01 × A/B × ref1/2 = **32** đối chiếu (đính chính lỗi
  đếm 48 trong bản nháp, không đổi danh sách hoặc mức ref); adapter 58 record chỉ
  metadata. Regression cũ gồm D-only của L3.1 và screen M31 đã exposed. Không chạy engine
  trên M/R/N/P; không dựng D held-out; không A01/A04/A05 hoặc chọn H1/null/K5.
- Precision báo riêng oracle Δ, M0 Δ-hat, D22; hai nhánh M0 kèm cận ảnh hưởng phần chưa
  phân giải. E[Δ-hat] chưa phân giải thì trả cả hai L00 khả dĩ và HOLD, không kẹp dấu.
  Báo cận từng đại lượng; dt-discretization để A01, không gọi numeric bound là CI.
- Phân biệt identity đại số, bất đẳng thức có thể bị bug phá, và kiểm chéo độc lập.
  Checker brute không import core. Mutant subtraction tương đương ở Fraction, cần
  float conservation để bắt; không nhận số mutant/test từ lesson là số đã chạy phiên này.
- Sửa pseudocode idle: tính idle từ backlog **trước** update; float cut phải cộng sai số
  value/probability/rounding; guard held-out phải kiểm commit A05-F thật, không chỉ cờ.
  Đây là sửa implementation/verification, không đổi contract, threshold hoặc estimand.
- Guard theo grid ID; card L3.3 sạch và nằm trong HEAD trước mọi grid evaluation;
  held-out cần A05-F committed + purpose A05-T. V9/A04, P0-V10/Phase4 giữ nguyên.

### DL-046 — Engine exact v1: phạm vi đã kiểm và việc chưa xác nhận (2026-10-27)

Người phụ trách: **Doan Van Tai**. Theo DL-045, engine mới được giữ ở experiments/A00_engine;
`src/smr/cells.py`, kernel và các reference trước đó nguyên byte. [Report](../results/lessons/l3_2/report.md)
và [verification](../results/lessons/l3_2/verification.json) là output thực của phiên.

- **Technical verification PASS:** 72 tests mới, 300 toàn repo; failures/errors/skips=0.
  300 ledger và 400 physical toys đối chiếu đường độc lập; 2.000 perturbation trials,
  40 joint probability/value/conditional-posterior trials; 11/11 mutant KILLED bằng
  test-call failure, không dùng collection/setup error. M4 được bắt bằng float conservation.
- **Đã tái lập:** golden canonical/E2/E5/E7, L1.5 E|I_delta|, D22 fixed-M0, chuỗi L1.8B
  8 mức ref1…128 qua cùng aggregate; adapter58 records, 32 D-only comparisons đúng unit/mass/
  support/error. Canonical GS=9/8, GM=1/4, Γ=−1/4, F=3/8,V=3/4; E7 Γ=1/8,E|I|=9/8.
- **Numeric:** trả cận từng L/R/contrast, oracle/M0/D22 unresolved riêng, M0/D22 impact,
  hai L00 khả dĩ khi gh unresolved và quantile intervals. Bound có điều kiện theo cận input,
  kernel và arithmetic finite; test containment không là proof độc lập toàn bộ floating system.
  Không coi e_num là CI, không đổi epsilon hoặc dùng nhãn điểm thay khoảng.
- **Không xác nhận:** grid outcomes/feasibility/dt, hypothesis, novelty/network validity,
  tác giả đã tự giải thích code. E3/E6 là arrival-law toys ngoài D7, không hợp thức bằng đổi D7.
  EVPI_w và flip mass 2D chưa tính. Chưa có T05 tác giả/attestation nên **chưa promote src**.
- **Gate giữ nguyên:** L3.3 chưa commit; không A01/A04/A05. V9 chưa gửi nên A04 chờ;
  P0-V10/L8 OPEN, Phase4 HOLD. Engine guard không thay điều kiện của runner hoặc semantic
  review card. Có thể học/soạn L3.3; không nhận Understanding/ownership PASS.

### DL-047 — L3.3: phạm vi soạn card trước chạy và các quyết định còn chờ (2026-10-27)

Người phụ trách: **Doan Van Tai**. Đọc ba phần lesson, đối chiếu claims/contract/DL-043.
[Config](../results/lessons/l3_3/config.json), [đáp án toy đã exposed ghi trước code](../results/lessons/l3_3/expected_before_code.json).

- Giữ nguyên byte claims.md, already_implied.md, contract/grid/thresholds/nhãn Phase2.
  P2/P3/P5/P6 giữ forecast cũ trên đúng danh sách; P1 vào sanity, P4 chờ A05-F.
  Chưa có cơ chế do tác giả viết: dùng nhãn **forecast không cơ chế**, không giả tác giả viết.
- Đã hỏi tác giả lựa chọn K5 và read-back already_implied/T05; chưa có câu trả lời tại
  thời điểm ghi DL này. Chuẩn bị card **DRAFT, chưa freeze**, không tạo tag/receipt A03
  chính thức hoặc ghi author-attested từ yêu cầu “tiếp tục”. Các luật mở rộng chỉ là candidates.
- Sửa enclosure G/Cref: khi C_low>0 lấy min/max **bốn** thương. Công thức hai đầu
  trong lesson không đúng cho numerator âm. Không đổi ngưỡng; denominator cắt 0 → chưa phân giải.
  Chấm theo e_num thực, tách vế/Kleene; HOLD numeric/dt → chưa phân giải; không dùng empty-set
  vacuous truth để gọi một prediction “đứng”. Cref=0 loại relative label, giữ trong báo cáo.
- Bổ sung diagnostic E|e_M| và sanity G_M|S1≤E|e_M|; chỉ chạy toy (4.000 ledger,
  E8, persistence). Membership chỉ đọc whitelist tọa độ/target thiết kế, không p_sw thực
  hoặc lambdaA held-out. Không dựng D mới, không chạy J/gap/contrast grid; regression cũ
  vẫn có D-only và screen M31 đã exposed, phải ghi riêng.
- Guard phải trỏ đúng card path trong lesson, từ chối DRAFT và kiểm card commit + SHA-256
  trong receipt commit tiếp theo trước A01. Hai commit/tag/push chỉ thực hiện khi điều kiện
  freeze thực sự có record. Engine/T05, V9/A04, P0-V10/Phase4 giữ nguyên.

### DL-048 — L3.3: tác giả chọn K5 và xác nhận hai read-back (2026-10-27)

Doan Van Tai trả lời trực tiếp: **“Cả danh sách và luật κ≥2, q90/q90, h=8”**;
và với câu hỏi already_implied kín sách + engine/T05 read-back: **“Đã tự hoàn thành
cả hai ngoài repo”**. [Câu hỏi và trả lời nguyên văn](../results/lessons/l3_3/author_attestation.json).
Ghi author-attested theo DL-032; không independently verified, không có transcript
hoặc lời giải mới của tác giả trong repo. Không suy rằng tác giả viết phần AI hỗ trợ.

- K5 khóa hai mức: danh sách M19–M22 và luật κ≥2, A/B q90, h=8, η∈{.5,.75},
  target thiết kế∈{.3,.7}; main M19–M22, held-out R03/R04 (chỉ η=.5).
- Giữ nguyên câu forecast PC2/3/5/6; dùng lựa chọn hợp lệ “forecast không cơ chế”
  của Part3 §5.2, không tự chọn con đường A/B/i/ii/iii/a/b thay tác giả. Chỉ được
  claim verdict contrast; route diagnostics sau này là mô tả, không support mechanism.
- Chỉ luật K5 được adopt mức ngoài mẫu trong lượt này. PC2/PC3 coordinate extensions
  là tùy chọn của lesson, giữ ở candidate record, không tự mở rộng claim do tác giả xác nhận.
- Hai read-back chuyển AUTHOR-ATTESTED; T05 chưa có văn bản tự viết trong repo.
  Chưa promote engine hoặc chạy A01. Sau các checks PASS được thực hiện quy trình
  commit chỉ card → commit receipt/exposure → tag/push theo Part3 §9; không amend/force.


### DL-049 — A03: card v1, nội dung và thứ tự trước A01 (2026-10-27)

Người phụ trách: **Doan Van Tai**. Tác giả chọn K5 và xác nhận read-back ở DL-048.
Card commit **chỉ một file**: `b05ed70bd4e93544bccefc975cdc452ad40d1380`; SHA-256 `14021a83c6d45a3fbeba6b7cbe27e9c8c0e572734557af1598cf79b819f34639`.
Receipt/exposure được ghi ở commit kế tiếp, tag có chú thích `a03-card-v1` trên commit receipt;
không amend/rebase/force. Kiểm Git sau đăng ký được lưu riêng, không chèn hash commit vào chính nó.

- 14 sanity,4forecast P2/P3/P5/P6,1luật K5; giữ nguyên claims/miền/ngưỡng chính, PC1 sanity/PC4A05-F.
  Không cơ chế do tác giả viết: ghi forecast không cơ chế; không chọn route thay tác giả.
- K5 hai mức được chọn trước outcome; vế Q5 chỉ witness main M01–M04, không mở rộng Q-held-out.
  Carry mọi luật chưa bị bác nguyên văn, kể cả unknown; không tiêu vào quota1–3 luật H1/null mới.
  Optional P2/P3 rules không adopt; P6 không có kiểm ngoài mẫu.
- Luật chấm ba trạng thái theo e_num thực, signed ratio4corners, Cref0excluded/cắt0unknown,
  đóng/mở đúng toán, Kleene từng vế, dt/HOLD; thiếu precision evidence không được autoPASS.
- Technical checks:29tests card+guard (5 cũ+24mới),324full PASS;11/11mutant KILLED;
  4000ledger có0vi phạm/0sai khác với enumeration. Sáu kiểm là AI self-check có giới hạn scope/
  algebra, không independent review, novelty audit hoặc chứng nhận feasibility đúng tham số grid.
- Guard trỏ đúng card và kiểm full SHA/card commit/receipt commit khác nhau/tag có chú thích
  cùng dependencies sạch. A05-T vẫn cần A05-F committed. Thay đổi card sau khóa làm guard/grader dừng.
- Chưa A01/A04/A05; V9/A04, P0-V10/L8/Phase4 và nhãn PC/G1 giữ nguyên. T05 read-back author-attested,
  chưa có văn bản tác giả mới trong repo; phiên này không promote engine vào src.
[Report](../results/lessons/l3_3/report.md) · [receipt](phases/PHASE_3_prediction_card.lock.json).


**Audit sau khóa DL-049:** receipt commit `bcd1941a5a00718d68886866ba667b9fa2d6ea97`; annotated tag
`a03-card-v1` trỏ đúng receipt, remote main/tag đã được Git xác nhận sau push. Card
commit1 đúng một file, SHA khớp; guard kiểm card PASS chỉ đọc, các truy cập M31/A01,
R03/A01 và R03/A05-T chưa A05-F bị từ chối như dự kiến. Lưu ở
[registration audit](../results/lessons/l3_3/registration_verification.json),
[remote anchor](../results/lessons/l3_3/external_anchor.json). Commit audit riêng sau đó
không sửa card/receipt/tag; không outcome/D grid mới được tính.

### DL-050 — A01 prereg trước outcome, làm rõ D1 (2026-10-27)

Người phụ trách: **Doan Van Tai**. Theo yêu cầu triển khai L3.4, áp dụng năm
làm rõ thủ tục của lesson Part2 §7.6 trước khi chạy: (a) min Cref hai mức;
(b) mọi cặp trong suffix đến ref16 đều đạt, báo endpoint mịn; (c) dt chung là
max ref ba ô; (d) không ngoại lệ lưỡi dao, HOLD khi không có suffix hợp lệ;
(e) cặp cuối không đạt thì HOLD, không thêm ngân sách hoặc nới dung sai.
Dung sai .0025/εE .005/miền/plant/D1–D25 giữ nguyên. Pair certification dùng
error upper bounds và Cref lower bound, báo cả nominal; rho/Richardson chỉ chẩn đoán.

Prereg commit riêng `81233ef9478e88f03b548c6bef21b9fa98b51a25`, SHA256
`9b8dc2f358792f4ac1e7df146ca8dc334599773f7de60378999a86efe5debe0f`.
Receipt/code/config commit tiếp theo, trước lần chạy đầu. A03 card/tag nguyên byte.
Part0 bitwise p_sw public trước cost; PartA C1–C6 bắt buộc trước B đủ15cell-level.
C5 và GS_M1 WD ==0 exact, direct EΔ± không clamp; C3 control11 không gọi true oracle.
C4 independent aggregation toy và strict tie action riêng. C1 dựng lại D khi u=0.
Native longdouble từ đầu cho costs, không tự tăng ref>16. Không Monte Carlo.

Lỗi synthetic fixture trước grid: đặt perturbation tại ref8 làm final pair fail
nhưng expected16; sửa fixture perturbation tại ref4. Giữ log1FAIL/26PASS, rerun
27PASS; không thay selector/threshold/cell. Kiểm full/mutant và kết quả A01 được
lưu riêng, chưa suy PASS trước khi chạy. T05 read-back author-attested đủ theo
prerequisite lesson; engine giữ experiments, không giả có văn bản tự viết mới.
V9 chưa gửi/A04 chờ; không held-out/A04 hoặc đổi nhãn PC/H1/null trong A01.

### DL-051 — A01 run01 FAIL, dừng trước PartB; sửa certificate (2026-10-27)

Người phụ trách: **Doan Van Tai**. Run `results/A01/20261027_01/`, code/receipt
`7e1c2acee23a59ea9c9ac6093b95bae77c72b06d`. Part0 **9/9 bitwise PASS**; C1/C2/C3
trên3calibration×2ref PASS. C5 N01/ref1 **FAIL**: GS=−0.0006173588649464212155,
GM_S1=+0.0006173588649464212155 packet·s. Runner STOP trước PartB; không A04.
Diagnosis guarded N01:4false-switch pairs, mass0.27182620215275735497;
minimum predicted gap −1.3552527156068805425e−20, true excess cost
0.0006173588649464211951 packet·s. Không xem đó là hiệu ứng thật hay nới ==0.

Nguyên nhân: ở mean paths cả hai actions luôn empty, idle-difference phải bằng
±u·dt²·H(H+1)/2. Hai idle totals cộng riêng tạo predicted tie âm một ulp;
conditional true gap vẫn dương vì B có future randomness. Sửa bằng **certificate
always-empty** và closed form chung, không epsilon/clamp. Mean no-idle có
certificate riêng từ linear-path minimum trừ roundoff/probability bound, để
exact mean ties không bị gán arbitrary action hoặc unresolved mass giả. Cặp
saturated A/B có common rational cap đối nhau là exact tie; bounded_cut loại
chúng khỏi *uncertainty bound*, không đổi gap theo threshold.

Thêm regression synthetic SD2 ref1/2, float64/longdouble. Vòng đầu guard certificate
so với cap longdouble bitwise làm2float64tests fail; đổi kiểm consistency theo
input bound, giữ log, không đổi certificate toán. Tất cả sửa đều trong implementation;
plant/control/metric/levels/tol/card/prereg giữ nguyên. Receipt mới ghi source hashes
và previous receipt, commit trước retry; receipt gốc giữ ở failed run. Full rerun
Part0→A→B, chỉ tớiB nếu controlsPASS. Exposure M01/M09/M22 ref1/2 và N01/ref1
đã có; failed artifacts được giữ, không xóa/làm lại thành PASS.

### DL-052 — A01 performance correction, không đổi luật nghiên cứu (2026-10-27)

Run02 code `c5fd6b0`: Part0/A PASS; B hoàn thành M01/ref1,2,4 BOUNDED.
Tạm dừng khi M01/ref8 đang ở precision.group_side, giữ console/JSON và đánh dấu
INTERRUPTED; chưa có output hoàn chỉnh ref8. Profiling traceback chỉ ra loop
chuyển **toàn bộ** array(s.p) lại cho từng phần tử của mỗi group → O(n²) conversions.
Hoist immutable conversion ra ngoài loop, giữ nguyên từng số và thứ tự cộng;
không thay toán/cận/precision hoặc dữ liệu. Bổ sung --workers1..6 cho các level
độc lập; tính **đủ15** tasks, sắp xếp CSV theo cell/ref, selector sau khi đủ bảng.
Per-cell/level resource caps không đổi; không adaptive levels/early stop.

Commit receipt source mới trước run03. Run03 tính lại Part0/A bằng cùng engine
mới, không mượn controls khác source; tính lại đủ PartB, không dùng cached output
cũ để né kiểm. Run01 FAIL và run02 INTERRUPTED giữ nguyên. C5/C6 thresholds/card/
prereg không sửa. Không thêm mức ngoài1,2,4,8,16 hoặc outcome held-out/A04.

### DL-053 — A01 PASS: dt cuối = 1/240 s, ref2 (2026-10-27)

Người phụ trách: **Doan Van Tai**. Prereg commit81233ef, source/receipt60a1032;
A03 commitb05ed70/SHA14021a83… giữ nguyên. Run03 mới hoàn toàn Part0→A→B,
longdouble,6processes, deterministic finite law, không sampling CI/seed.
Kết quả: **9/9** public p_sw intervals bitwise; **18/18** C1/C2/C3 cell-control-level
identities; C4 independent toy oracle/tie PASS; **60/60** C5 contrast entries
(5cells×2ref×6G) bằng0 chính xác; **6/6** C6 GS_M1 bằng0 chính xác.
C2prime6 rows chỉ observations, không zero requirement. P02/ref1 GM=
0.12821501861993288285 packet·s; WD không phải all-zero control.

B tính đủ3cells×5levels **15/15 BOUNDED**; **12/12 adjacent pairs PASS** theo
DL-050. max e_num/Cref_lower=2.5115774765507683e−5 (budget.0025), max unresolved
mass=1.715862486941145e−5 (cap.01). Cặp1→2 có cận relative-change upper:
M01 **0.0244213218934%**, M09 **0.00891751012970%**, M22 **0.000436969036553%**,
đều dưới0.25%; mọi cặp mịn hơn cũng đạt. Không a00 flip giữa5levels trong cả3cells.

Selector all-finer-suffix chọn M01=2/M09=2/M22=2; **dt cuối=Δt/2=1/240 s ≈
4.1666667 ms**, H=1920 cho h8s. CSV replay từ process khác ra cùng2.
Đây là quyết định dt cho Phase3 theo D1; **không** chứng nhận continuum limit,
35 ô khác ổn định hoặc hypothesis RQ. A04 cần kiểm **1/120→1/240** riêng từng ô.

Full suite cuối **336 PASS**/65.84s,11/11mutants KILLED. Optimization6synthetic
sizes trùng bits; 512states:1.78417→0.0107671s (single timing165.7×, không benchmark
CPU tổng quát). Run03 calibration JSON M01/ref1/2/4 và4control artifacts trùng
byte run02 tuần tự; computation mới, không đọc cache. Run03 wall265.686110563s,
không gồm preflight/debug/retries. Run01FAIL/run02INTERRUPTED giữ nguyên.

[Run manifest](../results/A01/20261027_03/manifest.json),
[CSV](../results/A01/20261027_03/refinement.csv),
[selection](../results/A01/20261027_03/selection.json),
[report](../results/lessons/l3_4/report.md),
[metrics](../results/lessons/l3_4/verification.json),
[plot](../results/lessons/l3_4/refinement.png).
A04/A05 chưa chạy, card forecasts chưa chấm; không H1/null/A05-F hoặc held-out outcomes.
V9 **chưa gửi, A04 chờ**, L8/P0-V10 và T05 author-writing giữ OPEN. L3.4 hoàn thành
kỹ thuật, không tự xác nhận tác giả đã làm tự kiểm/Understanding.

### DL-054 — Tác giả gỡ V9 bằng waiver trước L3.5/A04 (2026-10-27)

**Người phụ trách/quyết định: Doan Van Tai.** Yêu cầu trực tiếp hiện tại:
“sửa lại mở để tôi có thể chạy lesson 5 đi”. Thực hiện phần yêu cầu bỏ chặn bằng
**quyết định tác giả miễn điều kiện gửi heads-up/memo trước A04**, tương ứng
phương án(b) đã nêu trong Phase3. Quyết định này thay điều kiện(c) của DL-044
cho các bước tiếp theo; không viết lại lịch sử DL-043/044.

**Trạng thái: `WAIVED_BY_AUTHOR`, không phải `GVHD_APPROVED` hoặc `SENT`.**
Memo chưa gửi, không có phản hồi GVHD thật được ghi nhận. Bản nhận xét tác giả
cung cấp là review mô phỏng do AI, được lưu nguyên byte/disclaimer ở
[review_original.txt](reviews/2026-10-27_pre_A04/review_original.txt) và có
[provenance](reviews/2026-10-27_pre_A04/provenance.json). Không đổi nguồn thành
GVHD hoặc tạo bằng chứng human review. Việc ghi waiver không là xác nhận mới
về tác giả đã đọc kín sách, tự hiểu hoặc GVHD đã đồng ý.

**Rủi ro chấp nhận cùng yêu cầu tiếp tục của tác giả:** A04 có thể được triển khai theo
contract hiện hành trước khi có góp ý GVHD. Nếu GVHD yêu cầu đổi RQ/D13/D20/D21,
miền lưới hoặc điều kiện đánh giá sau A04, phải giữ kết quả cũ theo estimand cũ,
ghi rõ thời điểm đã thấy outcome, tạo design/amendment mới có lý do và tính lại
phần chịu ảnh hưởng. Không sửa card/ngưỡng sau outcome để làm kết quả thuận lợi;
prereg/card cũ không thành preregistration cho estimand mới. Chi phí tính lại
không khôi phục tính mù hoặc quyền nhận novelty/confirmation.

**Phạm vi gỡ chặn:** chỉ P1-V9 trước A04. P0-V9 về timescale không bị đổi.
L3.5 được tiếp tục triển khai; vẫn phải hoàn thành/commit prereg A04, ghi exposure,
kiểm runner/card/dt trên synthetic/toy trước run. A01/dt1/240s và bắt buộc kiểm
pair1/120→1/240 từng ô giữ nguyên. H phụ thuộc h của từng ô.
A05-F vẫn khóa trước held-out; L8/P0-V10/T05 author-writing giữ OPEN; Phase4
HOLD tới P0-V10. Không có A04/held-out run trong nhiệm vụ này.

**Đối chiếu review:** reviewer chỉ thấy publicf72306f nên324tests và20.000toy
là reviewer-reported, chưa được replay trong phiên tiếp nhận. Local source60a1032/
closeoutb9a176c có A01; guards và51artifact hashes được kiểm lại, CSV selector
cần giữ ref2. [Intake](reviews/2026-10-27_pre_A04/intake.md) tách findings khỏi đề
xuất chưa adopt. Γ=GM_S1−GM là identity; dấu Γ không tự chứng minh cơ chế, nhưng
không phủ nhận nghĩa superadditivity theo D19. Không adopt tiêu chí kill chỉ vì
GM luôn thuộc{0,|EΔ|}: đây vốn là hệ quả T01. Không tự thêm ref4/flip mass hoặc
đổi cách chấm P6/H0 chỉ dựa vào review.

[Gate record đọc được bằng máy](phases/A04_execution_gate.json) ·
[preflight L3.5](lessons/L3.5_preflight.md).

### DL-055 — Prereg A04/L3.5 trước 92 cell-levels (2026-10-27)

- Người phụ trách: **Doan Van Tai**; triển khai theo yêu cầu tiếp tục hai phần L3.5.
- Chạy38main+8controls/probes tại ref1/ref2, dt chính1/240s DL-053; gate V9
  WAIVED_BY_AUTHOR DL-054. Không thay engine/card/lưới/threshold.
- Khóa `experiments/A04_discovery/prereg.md`, config, source, exposure trước run;
  receipt ở commit kế tiếp. Grader A03 đọc metadata đã nằm trong card, không
  sửa card để thêm khối JSON mới. Validity→score→commit→discovery.
- Miền cheap kill cố định core22/spoke_A50 8/spoke_h2 8. Cận R00 cho gain từ00,
  không cho Gamma/GM_S1; strict upper<1% ở mọi ô eligible. DL-006 lịch sử vẫn
  DRAFT; đây là đăng ký cụ thể cho A04 theo lesson, không ký thay học/hiểu của tác giả.
- Giữ epsE=.5%; ở sensitivity epsR=.5%, closed-equivalence được xét trước để
  hai nhãn không chồng nhau. Primary/luật chấm card không đổi.
- H1/H2/H3, margin quantiles50/90/99% sẵn có, D22/R04 diagnostic; flip mass2D
  vẫn deferred. Hai ô kiểm tay M09/P2 và M17/P6 chọn trước, reviewer phiên riêng.
- Exposure kế hoạch ghi cả public held-out design metadata vừa hiện khi đọc
  bảng cũ; không D/cost/gap-magnitude/contrast held-out mới. A05-T chưa mở.
- Không tự đóng human-reader, Understanding, author-writing hoặc Phase4.

### DL-056 — Kết quả A04 và hoàn tất kỹ thuật L3.5 (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Run27/10, tổng kết28/10; kết quả giữ nguyên.
- Prereg56c4141,receipt0eb42f2 trước outcomes; score checkpoint7005a3b trước discovery.
  Card A03 không đổi. V9 WAIVED_BY_AUTHOR DL-054, không memo gửi/GVHD phản hồi.
- 92/92cell-level BOUNDED;46/46pairs đạt,0HOLD/cờdt;60zeroD19+6zeroWD;
  348tests PASS;6calibration records tính lại trùng A01. Review phiênAI độc lập
  M09/P2 và M17/P6 khớp; không thay human L8/P0-V10.
- P2 không đứng(2/4);P3 không đứng(0/2);P5 đứng(K4/4,Q2/4witness);P6 không đứng(0/2).
  Không claim unresolved/excluded, không cơ chế preregister. Không sửa threshold/miền.
- Cheap kill:0/3miền đạt điều kiện; **không NARROW theo cheap kill**.16ô có upper
  R00/Cref<1% được báo nhưng không chọn lại miền để dừng.
- Discovery:5phát biểu đã xét,1candidate C1 (κ1,h8;16/16ô GMnominal0) đề cử xem
  ở A05-F. Chưa xác nhận interpolation/queue mechanism;null/fit/split/metric chưa khóa.
- K5rule chưa bị bác,carry **nguyên văn,m=1** theo A03;Q-witness chỉM01–M04.
  CandidateC1 hậu discovery không thay/mở rộng K5 và không tự là A05prediction.
- Tìm có mục tiêu:20title/snippet,1proposal mới (arXiv2511.19961v2;
  DOI10.1109/MWC.2026.3712294),khôngPDF/note mới. Không novelty/saturation.
- Exposure:toàn38main+8controls/probes đã xem cả2dt;public held-out design
  metadata hiện khi đọc bảngcũ được ghi thật,không dùng làmfeatures;khôngD/J/
  gap-magnitude/regret/contrast held-out mới. A05-T chưa mở.
- L3.5 hoàn tất **kỹ thuật**; tiếp theo L3.6/A05-F. Không tự đóng Understanding,
  T05author-writing,L8/P0-V10 hoặc Phase4. A04_execution_gate.json giữ byte
  snapshot trước run; A04_completion.json là trạng thái sau run.
- Evidence: notes/lessons/L3.5_A04_note.md;results/lessons/l3_5/report.md;
  results/A04/20261027_01/. Không claim runtime/CI/statistical inference ngoài scope.

### DL-057 — Tác giả chọn D25(ii) và thiết kế A trước prereg A05-F (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Câu trả lời trực tiếp của tác giả:
  “Dùng λA cho cả hai theo D25(ii), chỉ kết luận về chênh lệch dự báo H1−H0
  (khuyến nghị của lesson)”; “Đồng ý theo phương án này; bạn chốt các chi tiết
  kỹ thuật và ghi rõ trong prereg”. Nguyên văn lưu author_choices.json.
- Định nghĩa lambdaA là tham số plant cho cả38main+12held-out theo cùng công thức,
  không dùng p_sw thực. H0/H1 có cùng quyền input trước action. DL này thay cách
  đọc chặt trong hàng đợi/exposure cũ cho bước A05, không sửa D25/contract/lưới.
- Claim chỉ là paired predictive comparison có điều kiện trên thiết kế neo.
  Cùng input không tự chứng minh hết leakage/endogeneity hoặc cơ chế nhân quả;
  không dùng độ chính xác tuyệt đối như evidence độc lập.
- Thiết kế A: sổ cái Gauss/tầng identity chung, cùng ngân sách và thủ tục fit.
  Carry K5 nguyên văn,m=1; khóa thêm C1 equivalence sau discovery và nhánh PC4.
  Universe12ô;8ô nội suy một trục là verdict chính;R09/R10,R11/R12báo riêng.
  Không mở comparison D<m. Các chi tiết kỹ thuật do AI chốt theo ủy quyền này
  trong prereg trước fit/predictions; không ghi chúng là tác giả tự dẫn/viết.
- Bản ghi này commit trước prereg, không author-attest Understanding hoặc human
  review, không quyết định chạy A05-T. A05-T là bước khác, chưa thực hiện.

### DL-058 — A05-F đã khóa dự báo và khả năng phân biệt (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Theo tác giả chọn D25(ii)/thiết kếA ởDL-057.
  Author decision commit:51c926fda9a2442c02b320d6dad1063def91d075;prereg:57d84c66fc2cfca6de6fbbda662918959cd99fc5;
  theta:6aa696a958ec0ee09242812c94762a0f42927f89;predictions+discrimination:3c75aecd720ef688923d818bc41f3db4a82742ec.
- predictions_heldout.json SHA256: `9b93e3f3445d4ebc2fbda96f72988bc3bc78c5524df05825405c73f83093bb80`.
- discrimination.json SHA256: `cbd0851a47e5939a9ae68e342befdcb8171f5722c169f00cf77c66b86310afe5`.
  Freeze receipt giữsource/K5copy/theta/input/outputhashes;khôngamend/force.
- H0coordinates_0,H1dynamics_1,12hệsố/model,2candidate/2start,rho0;chọnbằng
  20foldLOSO trên38main;khôngheld-outoutcome. LOSO làdiscovery,nothing confirmed.
- Metricchính MAEđềuGS/GM/Gamma,margin .25điểm%Cref. Dprimary8ô=.5912388743,
  DweakR09/R10=.2122970451,DextraR11/R12=.4749516655(điểm%Cref).
  Theo luật trướcprediction: primary/extra đủD;**weak không mởcomparison**.
  Đăngkýuniverse12nhưngactualoutcomeIDs cần10:R01–R08,R11/R12;R09/R10giữchưamở.
  Khônghạmargin hoặcđổi modelđểcứu nhómweak saukhithấypredictions.
- K5carry nguyênvăn,m=1,R03/R04,QscopecũM01–M04. C1equivalence≤.005tạiR05–R08
  khóa sauA04,báoriêng;baserate36/38,heuristic4ô .8055186808 khôngphảixácsuấtthật.
  Có nhãnheadroom trướcoutcomes;chưatínhheadroomheld-out đểgắnnhãn.
- Featuresheld-outbậc0–2 tạo 2026-10-28T00:50:16.694515+00:00;**khôngD/cost/gap/Cref/outcomes**.
  λA dùngchung theoDL-057,khôngp_swthực. Nguồnengine/card/A04giữnguyên.
- Hoàn tấtA05-F/L3.6sau receiptcommit;chưachấmH0/H1held-out,chưanhậnSUPPORT/
  WEAKEN/FALSIFY từtruth. **Chưa thực hiện quyết định không đảo ngược A05-T**;
  L3.7 cần ghi quyết định đó trước run. Không tự đóngL8/P0-V10/T05/Phase4.

Báo cáo kết thúc L3.6: [freeze_report](../results/lessons/l3_6/freeze_report.md),
[freeze_verification](../results/lessons/l3_6/freeze_verification.json).369testsPASS;
80LOSO/24model-cellpredictionsreplaykhớp;164starts đều thànhcông.

### DL-059 — Quyết định không đảo ngược: mở A05-T đúng một lần (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Yêu cầu trực tiếp nguyên văn: “hãy làm theo
  hướng dẫn và thực hiện lesson 7 cho tôi đi”. AI (Claude) soạn dòng này và thực hiện
  **theo ủy quyền**; đây không phải câu tác giả tự viết, không author-attest
  Understanding L3.7 hay kỳ vọng trước run.
- 2026-10-28T08:31:52+07:00: mở **10 ô R01–R08, R11, R12** cho A05-T, **đúng một lần**.
  **R09/R10 giữ niêm phong** (D_weak = 0,2123 < m, DL-058); trục h = 4 s không được kiểm.
- Neo: freeze `5f20103`; predictions SHA256 `9b93e3f3…bb80`; discrimination SHA256
  `cbd0851a…afe5`; engine, card, A01 và A04 không đổi kể từ `0eb42f2` (git diff rỗng);
  runner, gate và rescorer ở commit `72903b7`, SHA nguồn đăng ký trong
  [decision.json](../experiments/A05_test/decision.json).
- Chấm ở dt 1/240 s; kiểm cặp 1/120→1/240 cho từng ô; luật prereg A05-F §7 qua
  `score_test.score` nguyên vẹn; chấm lại độc lập bằng `rescore.py`. Kiểm p_sw công
  khai ở ref 1/2 bitwise trước cost; lệch thì dừng.
- Cam kết: không đổi dt, margin, metric, trọng số, danh sách ô, mô hình hay cổng
  precision sau khi thấy outcome. Ô trượt cổng là unavailable, không chạy lại ở dt khác.
  Chỉ sửa bug validity chứng minh được mà không cần verdict; khi đó cần DL mới,
  decision mới và mục Deviations.
- Chẩn đoán khai trước, `DIAGNOSTIC_NOT_VERDICT`, tính cho mọi ô đã mở bất kể verdict:
  bất biến tầng 1; regime (a00/a01, G_M bằng 0 cấu trúc, R00/C_ref, p_sw engine so với p_2);
  vị trí truth so với hai dự báo và đóng góp d; phân rã level/shape theo contrast.
- Đọc kết quả: SUPPORT chỉ nghĩa H1 gần sự thật hơn H0 ít nhất m (|d| ≤ D); luôn báo
  MAE0 và MAE1. "H0 đủ tốt" chỉ được ghi dưới nhãn Inference. K5/C1 báo kèm base rate
  heuristic (0,8975 / 0,8055) và nhãn headroom. Bốn nhánh báo riêng, không gộp.
- Chưa có: kỳ vọng trước run do tác giả viết ([claim sheet](lessons/A05_T_claim_sheet.md)
  để trống phần đó); người đọc thật trước A05-T (khuyến nghị của PHASE_3 v2.0).
  A05-T không là network evidence, cơ chế hay G2. Phase 4 vẫn HOLD tới P0-V10;
  L8, T05 author-writing và Understanding giữ OPEN.

### DL-060 — Kết quả A05-T và hoàn tất kỹ thuật L3.7 (2026-10-28)

- Người phụ trách: **Doan Van Tai**. AI (Claude) chạy và chấm theo ủy quyền DL-059;
  không human review, không author-attest Understanding hay kỳ vọng trước run.
- Thứ tự: freeze `5f20103` → runner `72903b7` (391 tests PASS) → quyết định `146169d`
  → run một lần → output `e719157`. Engine, card, A01, A04 và A05-F không đổi.
- Validity: p_sw công khai bitwise 20/20; 20/20 cell-level BOUNDED và hard_pass; 10/10 cặp
  1/120→1/240 STANDS; max e_num/C_ref = 7,26·10⁻⁶; unresolved mass ≤ 4,59·10⁻⁶. Cổng
  precision PC4 10/10. `rescore.py` chấm lại độc lập: **agreement PASS**.
- **PC4 nội suy (verdict chính): WEAKEN.** 8/8 eligible; d = 0,247036 điểm % C_ref,
  thấp hơn m = 0,25; MAE0 = 0,690, MAE1 = 0,443.
- **PC4 ngoại suy R11/R12: FALSIFY.** d = −0,141751; MAE0 = 2,047, MAE1 = 2,188.
  R09/R10 DO_NOT_OPEN, niêm phong, không có outcome.
- **K5: DOES_NOT_STAND.** R03 STANDS (headroom-limited). R04 có G_M/C_ref = 0,527926% > 0,5%.
  Luật tọa độ K5 bị bác ở held-out; claim mức danh sách M19–M22 từ A04 không bị ảnh hưởng.
- **C1: STANDS** ở R05–R08 (G_M = 0 danh nghĩa, headroom không chứng nhận). Luật
  post-discovery, base rate heuristic ≈ 0,81, nên là bằng chứng yếu.
- Chẩn đoán khai trước, không đổi verdict:
  - R01 đóng góp khoảng 72% của d nội suy.
  - Lợi thế của H1 chủ yếu nằm ở mức (sai số có dấu G_S: −0,74 so với −0,01; Γ: +1,01 so với +0,36);
    phần shape-only nhỏ hơn.
  - Γ thật âm ở R01 và R11, không mô hình nào dự báo Γ âm.
- Deviations: không có. 10 ô đã mở nay là dữ liệu đã thấy. Nhãn Gate A dành cho tác giả ở L3.8;
  dòng này không chọn nhãn. Phase 4 HOLD tới P0-V10; L8, T05 author-writing và Understanding OPEN.
  [Report](../results/lessons/l3_7/report.md) · [số đo](../results/lessons/l3_7/verification.json).

### DL-061 — Gate A REFORMULATE và closeout Phase 3 theo ủy quyền (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Tác giả chọn nguyên văn **“REFORMULATE — chuẩn bị
  thiết kế mới”**, thay khuyến nghị NARROW ban đầu của AI; [record nguyên văn/timestamp](phases/PHASE_3_author_decision.json).
- **Một nhãn: REFORMULATE. Một claim:** Trong contract v1.2 một observation cố định
  mỗi ô ở dt 1/240 s, estimand có điều kiện và các kết quả A04/A05-T chưa xác nhận
  một quy luật dự báo khái quát, nên theo quyết định REFORMULATE của tác giả, contract
  mới phải định nghĩa gain/Γ trung bình trên một phân phối observations trước khi
  thực thi Phase 4.
- Scope evidence:38main A04 và10R đã mở; [Gate note](phases/PHASE_3_gate.md) link từng
  validity/outcome. Theo khung§18 của lesson: GO(a)/(b) không đạt, không có lỗi validity
  buộc HOLD, chưa đủ PIVOT/DROP; NARROW là phương án giữ estimand tác giả không chọn.
  Không suyΓvô nghĩa hoặc bắt buộc đổi thiết kế từ T01; ghi đúng ngoại lệ EΔ=0.
- Tác giả yêu cầu **“tôi yêu cầu bạn hãy đóng vai là tôi và ghi cho tôi đây là yêu cầu”**
  đối với hai mục closeout. Yêu cầu này thay quy tắc khôngủyquyền của lesson cho việc
  soạn/đóng hồ sơ: AI viết ngôi “tôi” có provenance rõ. Không ghi thành bài tự viết,
  kỳ vọng trước run, human review hoặc author-attested Understanding. Ownership vẫn OPEN.
- [Contractv1.3 proposal](01_definitions_v1_3_draft.md) và [brief proposal](00_research_brief_v1_3_draft.md)
  chỉ DRAFT: cần chốt joint law P(Y,X), support/tail/weights, normalization, grid,
  metric/margin/models/budget và split mới trước computation. Không tự khóa contract,
  không đổi D13/D21/engine/card hoặc estimand của kết quả v1.2, không rerun held-out.
- **Phase4 thực thi HOLD tới P0-V10 và contract mới được khóa.** Được học/chuẩn bị tiếp.
  V9 WAIVED_BY_AUTHOR chỉ cho memo trước A04; L8/T05/Understanding và các mục tự viết
  Phase1/2 không tự đóng.10ôR đã mở là dữ liệu đã thấy; R09/R10 vẫn niêm phong.
- [Closeout](phases/PHASE_3_closeout.md), claim boundary, README/current pointers,
  index/exposure/inventory/progress được cập nhật. Full suite local391/391 PASS;
  [audit/log](../results/lessons/l3_8/report.md) kiểm nguồn/hash/chấm lại/link.
  Commit closeout trước tag `phase-3-closeout`, không force; tag không nhận ownership PASS.

### DL-062 — v1.3 bước 1: kiểm hình học chế độ sai số trên 38 ô discovery (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Yêu cầu trực tiếp nguyên văn: “bạn hãy tự kiểm tra và thực
  hiện hãy làm theo hướng dẫn trên viết 3 prediciton rồi chạy kiểm tra thử cho tôi trước để xem v3
  liệu ổn và đáng theo không, thực hiện cho tôi đi”. AI (Claude) viết ba dự đoán và chạy **theo ủy
  quyền**; đây không phải dự đoán tác giả tự viết, không là understanding artifact.
- Nguồn: AI review Phase 3 do tác giả dán (commit `1f620ec`); số liệu và hai script đã kiểm lại,
  [intake](../results/reviews/phase3_20261028/intake.md). Không thay P0-V10/L8.
- Nhãn **[DISCOVERY]**: chỉ 38 ô main đã lộ ở A04, ref 2, dt 1/240 s. Không dùng 10 ô R đã mở,
  không chạm R09/R10, không đổi engine, card, contract hay ngưỡng cũ. Nhãn ba chế độ ở mức ô đã được
  thấy trước khi viết dự đoán, nên kết quả chỉ là kiểm tính nhất quán, không phải xác nhận.
- Ba dự đoán, định nghĩa và tiêu chí PASS/FAIL ở
  [predictions.md](../experiments/V13_step1/predictions.md), commit cùng DL này **trước** mọi
  phép tính theo từng state: P(a) mù do cả hai đường fluid không chạm rỗng; P(b) đảo dấu khi M0 chỉ
  thấy một phía trade-off; P(c) lens sai số tại biên giải thích G_M|S1 tốt hơn lens bias trung bình.
- Guard đã khóa chỉ biết A01/A04/A05-T và nằm trong receipt A01, nên không sửa. Runner dùng mức
  truy cập "A04", chỉ mở ô main; manifest ghi study V13-STEP1-DISCOVERY.
- Kết quả bước này chỉ là đầu vào cho bước 2 (thiết kế v1.3). v1.3 vẫn DRAFT; Phase 4 HOLD tới
  P0-V10 và contract mới được khóa. Ghi lúc 2026-10-28T18:24:00+07:00.

### DL-063 — Kết quả v1.3 bước 1: P(a) PASS, P(b) FAIL, P(c) FAIL (2026-10-28)

- Người phụ trách: **Doan Van Tai**. AI (Claude) chạy và báo cáo theo ủy quyền DL-062; không human review.
  Dự đoán commit `81b1c3f` trước run. Run `results/V13_step1/20261028_01`, một lần, exit 0;
  validity PASS (G_M|S1 tính lại khớp A04 38/38; khối lượng chưa phân giải bằng 0).
- **P(a) PASS:** ở M19–M22, cả hai đường fluid không chạm rỗng trên toàn support; không có triệt tiêu.
- **P(b) FAIL:** M01, M03 không phải "một phía" (I_A = I_B = 1); M0 phóng đại cả hai phía nhưng không đều.
- **P(c) FAIL:** Spearman lens biên 0,163 < 0,6; lens bias trung bình −0,701.
- Theo bảng khai trước, hướng tương ứng là fallback (population characterization hoặc NARROW); không
  đặt v1.3 quanh "fluid một phía" hay "fidelity tại biên". Hai quan sát post-hoc (đảo dấu ở biên tương
  đối nhỏ nhất kèm phóng đại B > A; thiệt hại đến từ sai số lớn xa biên) chỉ là ứng viên, chưa kiểm.
- Quyết định bước 2 thuộc tác giả. v1.3 vẫn DRAFT; Phase 4 HOLD tới P0-V10 và contract mới được khóa.
  [Report](../results/V13_step1/report.md).


### DL-064 — Mở Phase 3R; đóng băng pilot population v1.3 làm discovery (2026-10-28)

- Người phụ trách: **Doan Van Tai**. Thực hiện theo yêu cầu trực tiếp triển khai L3R.1;
  phần tổng hợp/bài học được soạn theo ủy quyền, không tự ghi Understanding PASS.
- **Decision.** Mở Phase3R theo [plan](phases/PHASE_3R.md); đóng băng branch pilot tại
  `a7435e9a3cb0d1625479c942041ec6748444014a` bằng annotated tag `explore-v13-pilot`.
  Không merge hoặc xóa branch; SUMMARY và raw giữ nguyên byte. Chạy lại phép đếm **một lần**
  theo [khai trước](../experiments/R3R_01_recount/prereg.json), sau commit này và sau khi tag lên remote.
- **Why.** Tài liệu cung cấp đã nêu sai lệch SUMMARY/raw và các phát hiện trùng ID/tọa độ;
  cần kiểm tại máy này trước khi dùng số cho hypotheses. Đây là verification trên discovery
  đã thấy, không phải prereg cho hypothesis chưa thấy outcomes.
- **Alternatives.** Merge pilot sẽ nhập engine chưa audit; xóa branch mất provenance;
  ghi summary mà không chạy lại không xác nhận được số; đổi raw để khớp summary không hợp lệ.
- **Consequence.** Kết quả/errata ghi ở [discovery record](phases/PHASE_3R_discovery_record.md),
  tạo danh sách tham số đã exposed cho L3R.7. Bất kỳ trùng tọa độ phát hiện được đều giữ và báo,
  không ép dữ liệu thỏa câu “mọi regime đều mới”. Không engine/CF outcomes hoặc quét mới.
- **Trạng thái mang sang.** V9=WAIVED_BY_AUTHOR (DL-054, chỉ memo trước A04);
  P0-V10/L8/T05 author-writing/Understanding và tự viết Phase1/2 OPEN. Hai mục closeout Phase3
  soạn theo ủy quyền DL-061, không thành tự viết. v1.3 chỉ DRAFT; thực thi Phase4 HOLD tới
  P0-V10 và contract mới khóa. R09/R10 vẫn niêm phong; 38 main +10 R đã mở là dữ liệu đã thấy.
- **Provenance §0.5.** Giữ nguyên attribution nguồn được cung cấp, ghi người phụ trách là
  Doan Van Tai; phân biệt triển khai theo ủy quyền, tự viết và human review. Không suy ra
  tác giả đã tự dự đoán, đọc hết raw hoặc hiểu chỉ từ yêu cầu thực hiện thay.
- Ghi lúc 2026-10-28T21:35:45.066305+07:00. Nguồn script/test từ ZIP tác giả cung cấp; đã kiểm trước khi chạy.
  ZIP được đọc, giải nén tạm và xóa theo yêu cầu, không commit/push; hash ở
  [intake](../results/lessons/l3r_1/bundle_intake.json). Một đường dẫn attachment không tồn tại;
  hướng dẫn Part2 đầy đủ trong ZIP được dùng thay, không nhận đã đọc attachment thiếu đó.


### DL-065 — T07 và golden reference trước audit population (2026-10-28)

- Người phụ trách/người soạn: **Doan Van Tai**. Triển khai L3R.2 theo ba phần lesson và
  ủy quyền soạn thay đã có trong phiên; không nhận author-attested tự dẫn hoặc tự viết.
- **Decision.** Lưu [T07](theory/T07_population_estimand.md), sanity list/proofs/toys và
  [golden](../tests/test_population_toys.py); commit bản định nghĩa trước mọi kết luận
  audit L3R.3. Chỉ chạy toy hữu hạn Fraction, 500 joint laws seed20261028, kiểm 5 mutant.
  [Spec](../experiments/lessons/l3r_2_spec.json) không là prereg hypothesis v1.3.
- **Why.** Cần đặc tả độc lập với engine làm đáp án audit; phân biệt identity, quan sát
  discovery và claim có thể sai. Lesson có vài chỗ cần điều kiện/đính chính bên dưới.
- **Alternatives.** Chép nguyên lời nguồn sẽ giữ nhận định sai chiều về Γ/harm; suy
  engine đúng từ golden là không hợp lệ. Chờ tự viết không cần thiết cho việc soạn
  reference theo ủy quyền, nhưng Understanding vẫn cần tác giả tự làm/xác nhận riêng.
- **Consequence.** T07 là reference cho kỹ thuật; không đóng self-understanding hoặc
  promote engine vào src. Target law, εR, primary scale, η và numerical policy v1.3
  giữ OPEN cho L3R.5; v1.2/claims/pilot raw/freeze giữ nguyên. Không audit engine, không
  mở R09/R10, không CF outcome ở lesson này.
- **Đính chính nguồn.** L3R.1/tag/exposure đã hoàn tất (bf3915e), không còn treo. S1
  invariance cần marginal X/J/policy cố định; đổi p/trigger có thể đổi marginal. Chiều
  harm⇒Γ>0 là hệ quả; chiều Γ lớn⇒harm là discovery, không phải định lý. Bảng bias
  hữu hạn không bảo đảm tính trơn; bound Γ theo shared belief còn chặt hơn bound
  lesson: [−σ̄,σ̄] nằm trong [−σ̄,2σ̄]. F/V có thể âm nhưng vẫn bị stakes chặn.
  Golden nguồn gán cb0=0 khi thiếu q: sửa thành không tính cb0/F/V để tránh chẩn đoán
  giả. Không đổi công thức/8 đáp án nguồn hoặc tiêu chí khoa học.
- Understanding/P0-V10/L8/T05 author-writing OPEN; V9 waived theo DL-054, G1 không đổi,
  Phase4 thực thi HOLD. T07 soạn theo ủy quyền không tự biến thành tác giả tự viết.


### DL-066 — Khai trước audit engine population L3R.3 (2026-10-28)

- Người phụ trách: **Doan Van Tai**; triển khai/soạn theo ủy quyền, chưa human read-back.
- **Decision.** Audit snapshot byte-identical từ tag explore-v13-pilot ở experiments/;
  khai T1–T7/12mutants,8discovery regimes,MC C1–C3/seeds/luậtN/rerun trước run ở
  [prereg](../experiments/R3R_02_audit/prereg.json). T07 bổ sung S1/S2/S4/S6 từ
  tài liệu cũ trước pilot, không tự thay model. Phiên MC mới chỉ nhận đặc tả/contract,
  không source engine; provenance của phiên lưu riêng. Không promote lên src.
- **Why.** L3R.1 chỉ kiểm raw/summary; L3R.2 chỉ reference toy. Cần kiểm khâu law,
  posterior,union-DP,averaging,numerics và tái lập trên inputlambdaB6/7/8.
- **Alternatives.** Chỉ kiểm identity không bắt consistent bugs. Dùng engine helpers
  trongMC sẽ mất độc lập. Không coi failuremonotone refinement là bằng chứng bug
  hoặc coi bin-policyMC tự cùng measure với point quadrature.
- **Consequence.** Không dùng CF hoặc R09/R10. Mọi run là verification discovery đã
  thấy; numerical policy chỉ proposal choL3R.5. Nếu bug: regression đỏ trước sửa,
  giữpilotv1,preregister dự đoán tác động và chạy lại toàn216ID ở outputv2; không
  chỉ rerun vùng thuận lợi. Kết luận cuối ghiDL khác theo kết quả, không định sẵnPASS.
- T07 authored-understanding/P0-V10/L8/T05 vẫnOPEN; V9WAIVED_BY_AUTHOR,G1,Phase4HOLD.
- Khai lúc 2026-10-28T23:15:51.002242+07:00, trước mọi engine outcome mới của phiên L3R.3.


### DL-067 — Khóa N MC; mở rộng chẩn đoán số sau quan sát (2026-10-28)

- Người phụ trách Doan Van Tai. Ghi 2026-10-28T23:37:52.565845+07:00.
- **Decision.** Khóa [N MC](../experiments/R3R_02_audit/MC_N_selection.json) theo
  SD từ N0=2048 và luậtDL-066, trước C3 production. Không đổi ngưỡng/luậtseed/rerun.
  Khai thêm K320 tạiX1008/X1009 trong [extension](../experiments/R3R_02_audit/prereg_extension.json).
- **Why.** K160 còn lệchS1~.32ppC ởκ3; đây là chẩn đoán sau outcome, không giả
  vờpreregister trước. Giữ originalUNRESOLVED; cần biết có co tiếp và chi phí.
- **Alternatives.** Không nới.25ppC, không bỏ regime khó, không gọi flat/nonmonotone
  là bug tự động. C2có3alarm sau4N ở busy side, chênh~1e−15/SE~1e−17; kiểm
  conservation/arithmetic củaMC trước khi kết luận lỗiengine.
- **Consequence.** Kết quả mới báo riêng. Adaptertoy đã sửa bằngintegercount để
  giữ exactrationaltie, không sửaphysicalpilot. 1mutant bị mathguard từ chối phải
  ghi rõ cơ chế, không lẫn với runtimeerror hoặc assertionkill.
- Audit chưa đóngPASS; Understanding/read-backOPEN,Phase4HOLD,G1giữ nguyên.


Bổ sung DL-067 ngày29/10/2026: tiếp tục sau lần tác giả ngắt phiên. Không rerun
các job đã hoàn tất. C3stationary X2065khớp vềmean nhưng SE=.103446939ppC>.1,
giữ nguyênUNRESOLVED. Khai [precision extension](../experiments/R3R_02_audit/precision_extension.json)
N=4×262144,seed mới đã cấp, trước khi chạy thêm. Đây là kiểm thêm sau quan sát,
không sửaNđãkhóa hoặc ngưỡng, không gọi kết quả cũ là PASS.


### DL-068 — Audit population: HOLD; KEEP lõi với lớp test/API (2026-10-29)

- Người phụ trách: **Doan Van Tai**; triển khai/soạn theo ủy quyền, chưa human read-back.
- **Decision.** Audit tổng thể **HOLD**; evidence kỹ thuật **PASS có giới hạn**. KEEP
  lõi và snapshot pilot nguyên byte, thêm test/API ở experiments/R3R_02_audit; không
  promote src, không merge branch, không khóa numerics/contractv1.3.
- **Đã kiểm.** 467tests full PASS,19test gốc riêng PASS,12mutants bị bắt (1 bởi
  Jensen mathguard); T2prob16side PASS; T6 8pairs PASS; C1 80/80; C2 77/80 ban đầu
  +3 exact-conservation arithmetic checks PASS; C3nodes8/8,max|z|2.313697. Full
  stationary means khớp trong3SE+allowance; X2065 SE .103447ppC ban đầuUNRESOLVED,
  extension khai trước lần bổ sung cho .051907ppC. Repro19/19 exact numeric values.
- **Giới hạn.** K160 S1cost κ3 còn .316–.327ppC; K320 extension sau quan sát cho
  .218–.229ppC.5/16 atom cases chưa đạt.01 ởref1,ref2 16/16 đạt/co. MC8regimes
  production ởref1; ref2 chỉ probe/repro. Full-stationary allowance là estimate
  refinement, sparse/finite-cap arithmetic chưa interval-certified. Population
  precision/HOLD near ties, D22outcome/N3 còn OPEN. Original UNRESOLVED không sửa.
- **Why.** Số kiểm ủng hộ cách tính trên scope đã audit; chưa đủ tự nhận global
  numerics certificate hoặc author understanding. Read-back do tác giả làm cònOPEN.
- **Alternatives.** Không gộp tests xanh thành auditPASS vô điều kiện; không nới
  tol hoặc chọn bỏ regime khó; không rewrite lõi đã tái lập nếu chưa xác nhậnbug.
- **Consequence.** Chưa kích hoạt rerun216ID/pilotv2: lỗi đã xác nhận ở adapter và
  MC checker, không productionpilot. Nếu enginebug thật được xác nhận sau này,
  vẫn giữv1 và chạy lại toàn216ID theo lesson. N7 được tái lập mới8pairs, không
  backdate claim gốc. L1.5 có report/replayP4 checker chung; đính chính nguồn lesson.
- P0-V10/L8/T05author-writing/Understanding OPEN; V9 waiver chỉ phạm viDL-054; G1
  giữ nguyên,Phase4HOLD. L3R.4 học/thực hiện theo scope được; L3R.5 numerics không
  tự freeze từ audit này. [Report](../results/lessons/l3r_3/report.md),
  [completion](phases/L3R_3_completion.json),[code map](verification/l3r_3/code_map.md).


Bổ sung kết quả DL-068: áp dụng đúng escalation đã khai từDL-066, X2065K40→K80/ref2
cho maxdelta.050360895ppC, đạt.25 và không signflip ngoàiεE. Giữ cặpK20→K40
ban đầuUNRESOLVED.19lầnrepro là9tọa độ vật lý với các mức số khác nhau, không19
regimesđộclập;57.808snapshot-pair records khớp. Integrity auditorPASS chỉ xác nhận
artifact/test/hash khớp, không đổi audit verdictHOLD hoặc author read-backOPEN.


### DL-069 — Realism v1: khóa nguồn/luật trước bảng216 (2026-10-29)

- Người phụ trách/người soạn: **Doan Van Tai**; triển khai L3R.4 theo ủy quyền.
- Giữ hai bối cảnh của DL-008. Tác giả duyệt cả3nguồn BAM10/ZLK17/LTWW94;
  targeted reading, chưa author L-self. Worksheet không đổi egress burst thành
  hidden-mode holding time, không biến polling thành AoI, không đoán buffer.
- [Envelope](realism/envelope_v1.json), [worksheet](realism/worksheet_v1.md),
  [luật](realism/rules_v1.md): k1,f2,sensitivity1.5/3. Thiếu một range bắt buộc
  thì UNSOURCED; không chọn anchor để cứu nhãn. Illustrativeτ10ms/100ms không
  là nguồn. Commit toàn bộ trước implied216; checkpoint labels trước overlay.
- A1generic đã khai ởcbed2bc rồi chạy:24replicates/18comparisons PASS theo
  tolerance khai trước. Chỉ stationary law tại3discoveryIDs đã khai; không
  J/gap/action/regret/contrast mới. CF/R09/R10 giữ niêm phong.
- L3R.3 HOLD và numerics NOT_FROZEN giữ; contractv1.3 DRAFT, G1,Phase4HOLD.
  Understanding/read-back/P0-V10/L8/T05 không tự đóng. Chưa chọn CFframe.


### DL-070 — Realism v1: MV(d) HOLD · SH(d) HOLD (2026-10-29)

- Người phụ trách/người soạn: **Doan Van Tai**, triển khai theo ủy quyền.
- Envelope/rules6bef959 trước bảng216; exportfirstrowFAIL(kappa) không tạo labels;
  regression đỏ rồi fix830a187 giữ nguyên science. Labels1164500 trước saved-overlay.
- a/b đều216/216UNSOURCED (210distinct);f1.5/2/3 không đổi vì thiếu source ranges.
  Không coi là robustness evidence hoặc OUT. MV20ID/20distinct;SH80/78;giao14/14.
- **MV(d) HOLD_REALISM_UNSOURCED;SH(d) HOLD_REALISM_UNSOURCED.** Cần source/schema
  backlogAoI/holdh/offeredinputCV/buffer-time/d_act tương thích. Không đổi RQ/plant
  hoặc chọn context cứu effect. Không claim prevalence từ discovery thích nghi.
- 491full/24targetedtestsPASS,18/18genericMCchecks;stationary-only12rows,fluidapprox
  không exactslot. Review riêng chỉ5input,consistencyPASS,không human/L-self.
- Buffer/actuationUNSOURCED,modeoracleTRUE. Infinite-queue tail sensitivity không
  finitebufferdrop; postloadproxy không transient; không suy dấuGS từmodecorr.
- Trước envelopev2 cần khóa granularity mean/peak và phép nới định tính;v1frozen
  không sửa. Nguồn mới có version sau labels. [Note](realism/realism_note_v1.md),
  [report](../results/lessons/l3r_4/report.md),[completion](phases/L3R_4_completion.json).
- L3R.5 học/soạn được;chưa contractadoption/CFframe/CFoutcomes. L3R.3HOLD,numerics
  NOT_FROZEN,v1.3DRAFT,G1/Phase4HOLD;Understanding/P0-V10/L8/T05OPEN giữ.


### DL-071 — Tác giả chọn khóa contract v1.3 với mục DEFERRED (2026-10-29)

- Người phụ trách: **Doan Van Tai**. L3R.5 cả4phần được yêu cầu triển khai.
- Tác giả chọn nguyên văn: “Đồng ý; bạn chốt chi tiết kỹ thuật theo lesson” cho
  P1stationary,RoE Ḡ/C̄ref primary,stakes descriptive,εR1%(sensitivity.5/2%chỉmô tả),
  εE.5%,c_sw0primary,λA không outcome-anchor. Chọn sau pilot,trước confirmation;
  không so các phương án theo tỷ lệPASS để chọn thước.
- D22: “Cam kết làm D22; implementation và audit phải xong trước Phase 4”. Khóa
  định nghĩa/cam kết; chưa tuyên bố implementation/audit xong trong lesson này.
- Tag: “Phương án A: tạo tag contract-v1.3 sau kiểm chứng; phần DEFERRED có mốc đóng”.
  Tag sau tests/schema/consistency; không mở Phase4 hoặc đóng auditL3R.3/realism.
- Chi tiết kỹ thuật theoủyquyền: u_max=.10,fixed finite escalation trướcCF; khóa
  rule và điều kiện unresolved, không gán K*/dt* khi auditHOLD. H0/H1fitbudget→Phase5.
- Sửa lý luận lesson: refinement gap không chứng nhận total error hoặc chống mọi
  verdict flip; invarianceS1 chỉ khiπ/J/policycốđịnh, không mặc định khiκđổi.
- Tác giả chưa attest tự đọc/read-back; Understanding/P0-V10/L8/T05OPEN,G1,Phase4HOLD.
  [Lựa chọn nguyên văn](../results/lessons/l3r_5/author_choices.json).


### DL-072 — Contract v1.3 đã tag; deferred có deadline (2026-10-29)

- Người phụ trách/người soạn: **Doan Van Tai**. Tag annotated `contract-v1.3`
  tại `3d2359b32d7bd24f9e9072d5b5b8131bd33fffa0` sau41targeted/532fulltests vàmetadata/toy/integrity checks.
- 21frozen inputs khớpbyte/hash. [Contract](01_definitions_v1_3.md),
  [receipt](phases/contract_v1_3.lock.json),[report](../results/lessons/l3r_5/report.md).
- Khóa21inventory rows:18LOCKED,2DEFERRED,1LOCKED-definition/DEFERRED-execution.
  P1,RoE/C̄ref,εR1%/εE.5%,stakesdescriptive,c_sw0primary theo lựa chọnDL071.
  u_max=.10,finiteescalation2bướcdùngchung;R6xửlýsát+εR/−εR/±εE.
- DEFERRED: K*/dt*/S1route/quadrature-tail/auditcoverage→v1.3.1 trướcL3R.7CFsampling;
  D22engine/audit→trướcPhase4;H0/H1fitbudget→Phase5. Không sửatag hoặcđiềnnullngầm.
- Schema234recordsPASS,216mainID/210physicalkeys;quênc_sw162,thêmK/ref228.
 144λB8eta=φchecks;3D22goldens khôngthayproductionaudit. Khôngnewengineoutcomes.
- ĐãđạttiềnđềcontractchoL3R.6,khôngphảicardđãfrozen hayCFđãđượcsinh. “interact”
  chỉdiagnostictrừprimaryslotL3R.6;RQ2Phase5,RQ3Phase7. Khôngnovelty/evidenceupgrade.
- GiữauditL3R.3HOLD,realismHOLD_UNSOURCED,Phase4HOLD,G1;P0-V10/L8/T05/UnderstandingOPEN.
  Author science choices khôngthànhself-readback/human review.


### DL-073 — L3R.6: phân suất D, vùng lật κ và gói luật card theo lựa chọn tác giả (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Tác giả chọn nguyên văn qua hộp chọn trong phiên, sau khi xem
  số discovery đã log và trước khi viết card: “MV+SH primary; Γ diagnostic (Recommended)”, “MV+A, MV−
  lật κ (Recommended)”, “SH+A, SH− lật κ (Recommended)”, “Theo lesson, AI soạn (Recommended)”.
  [Record nguyên văn](../results/lessons/l3r_6/author_choices.json). Đây là **phương án D** của lesson
  Part1 §11 (không secondary); “interact” chỉ mô tả qua Γ̄, chưa có phép kiểm có thể sai.
- **Vì sao không cấp suất Γ.** Γ̄=ḠS|M1−ḠS=ḠM|S1−ḠM (T07 S11) và các contrast oracle ≥0 cho
  **Γ̄≥−min(ḠS,ḠM)**; lesson Part1 §9.2 chỉ ghi cận −ḠM nên đánh giá rộng quá phía substitution.
  Discovery (162 cấu hình c_sw0, log #19): Γ̄≥−.5% ở 162/162, chỉ **3/162** có min(ḠS,ḠM)>.5%;
  73 có ḠS≥0 nhưng 70 trong đó tự đạt do identity. Card Γ theo lesson gần như không thể sai; lọc đúng
  thì gần như không đạt N_min. Đây là discovery thích nghi, không phải bằng chứng “không substitution”.
- **Vùng (chỉ tọa độ, c_sw=0, u∈[1;3/2]).** Ω_MV⁺: λB=8, λA∈[7;15/2], κ∈[1/10;3/10], h∈[12;16];
  Ω_MV⁻ lật κ∈[1;3] (pilot chưa thử, ngoại suy); Ω_MV_BND κ∈[3/10;1] mô tả. Ω_SH⁺: λB∈[6;7],
  λA∈[7;8], κ∈[1/10;3/10], h∈[8;16]; Ω_SH⁻ lật κ∈[1;3] (ngoại suy). Discovery 16/16 và 57/72 là
  hộp vẽ sau khi thấy dữ liệu; kỳ vọng tỉ lệ CF thấp hơn. 13 luật đã tóm tắt, 5 giữ, 7 bỏ (log #20).
- **Gói luật.** π₀=1/2, CP một phía 97,5% (Bonferroni 2 primary), AND trong card không chia α;
  measure khóa trong card; R4 xét bốn góc (Ω⁺,Ω⁻ × MEETS/FAILS) thay hai kịch bản đồng loạt; R5
  u_max=1/10 mỗi vùng chấm; SH không có WEAKEN-theo-dấu; dấu E[Δ̂−Δ] chỉ đo. Card ghi “AI soạn,
  tác giả duyệt”, không ghi tác giả dự đoán/tự viết cơ chế.
- **Đính chính lesson đã kiểm.** §16(b) Part3: 20/30 có cận dưới 97,5%=.472 → U⁻ → WEAKEN-W2
  (không W1). Part1 tự kiểm3: Γ̄=ḠS|M1−ḠS=0,1% xác định, không là khoảng. Part2: h=2 là 0/30,
  không 0/20; góc λA=8 có 1/12 cấu hình λB7 ḠM>.09%. Bảng CP/power/coverage khác khớp.
- Không engine/CF/R09/R10; card chưa frozen ở DL này. Contract v1.3 giữ nguyên; G1, Phase4 HOLD,
  Understanding/P0-V10/L8/T05 OPEN; numerics v1.3.1 vẫn là điều kiện trước L3R.7 sampling.


### DL-074 — Cards v1 L3R.6 đã đóng băng; L3R.7 phải verify receipt trước frame (2026-10-29)

- Người phụ trách/người soạn: **Doan Van Tai**; AI soạn, tác giả duyệt theo DL-073.
  Freeze commit **`1414d9299d767b2abd56642c4d56048867b83095`**: [cards](phases/PHASE_3R_hypothesis_cards.md),
  [forking log](phases/PHASE_3R_forking_paths.md) (22 dòng, 13 luật tóm tắt + 1 khai không nhìn dữ liệu),
  [claim boundary](01_claim_boundary_v1_3.md), card checks, verdict/stats/regions code. Card SHA-256
  `248d9165…7117`; [receipt](phases/PHASE_3R_hypothesis_cards.lock.json) giữ hash 10 file.
- **Hyp-MV** primary1 (ḠM/C̄ref≥1%, Ω⁺ MV+A, Ω⁻ lật κ∈[1;3]) và **Hyp-SH** primary2 (ḠS/C̄ref≤−1%,
  Ω⁺ SH+A, Ω⁻ lật κ∈[1;3]); không secondary. π₀=1/2, CP 97,5%, Bonferroni, AND, bảng primary_v1,
  R4 bốn góc, R5 u_max=1/10. Measure khóa trong card; L3R.7 chỉ chọn n, seed, cơ chế va chạm.
- Chín phép kiểm PASS (phép7 ở mức “AI soạn, tác giả duyệt”; bằng lời tác giả OPEN; phép9 sơ bộ:
  p⁺=.7,p⁻=.2 → P(PASS) .553/.690/.837 với n=30/40/60 mỗi vùng). Bảng verdict 12 ô, 0 vi phạm phủ/
  đơn điệu, 12.400 trường hợp pipeline; R4 bốn góc khác hai kịch bản đồng loạt 0 lần trong lưới quét.
- Full suite **549/549 PASS**, targeted 17/17, contract freeze PASS, receipt verify PASS.
- Không CF/sample/seed/engine/MC; R09/R10 không nằm trong vùng nào. R11 nằm trong MV+A/MV-BND (đã mở
  ở A05-T): L3R.7 loại tuple trùng. Ω⁻ hai card là ngoại suy; κ=3,h=16 là góc số khó (L3R.3), cần
  v1.3.1 phủ trước sampling, nếu không R5 có thể cho INCONCLUSIVE.
- Card là prediction, không phải evidence; G1 không đổi. Phase4 HOLD (numerics v1.3.1, D22 audit,
  P0-V10/L8, Gate3R); audit L3R.3 HOLD; realism HOLD_UNSOURCED; Understanding/T05 OPEN.

### DL-075 — Sửa checker receipt card trước frame L3R.7 (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Review af65dbc tái hiện receipt sao chép có
  sha256={} hoặc chỉ1file vẫn PASS. Receipt thật đủ10file vẫn đúng; không evidence
  card đã bị sửa. Giữ log failure trước sửa trong results/lessons/l3r_7/logs/.
- Sửa duy nhất checker verify_cards.py (không thuộc manifest10file): bắt exact
  FROZEN set,valid SHA/schema/fullcommit,JSONunique keys vàfail closed.10negative
  cases bị reject; receipt/card/forkinglog/scorer frozen giữ byte,không tạo v2.
- Đây là sửa correctness của kiểm chứng, không thay RQ/measure/ngưỡng/verdict
  hoặc tự cấp science/human clearance.21contract+10card inputs verify PASS.

### DL-076 — L3R.7 chuẩn bị confirmation; không cấp n/root/CF trước numerics (2026-10-29)

- Người phụ trách/người soạn: **Doan Van Tai**; triển khai theo yêu cầu thực hiện
  ba phần lesson, không nhận tác giả tự read-back/dự đoán/human review mới.
- Design/sampler/power/inventory/distance/formatadapter/runnerguard/tests đã có;
  587full/38targetedPASS;10kdraws root test318700001,khôngengine;308source records,
  245reservedv1.3keys (có8u0variants bảo thủ),generic/incompatible namespace tách riêng.
- Luật n{30,40,60}/p95+30%/BND15hoặc0 là **đề xuất chờ trả lời tác giả**; B/threads/n/
  rootconfirmation=null. Không coi user chưa trả lời là đã duyệt; chưa có final
  prereg/list/executionreceipt. Code rule evaluator không phải adoption hoặc n thật.
- Chỉnh giải thích lesson: heuristic power×P(quaR5) bỏR4; n40,p+.7,p−.2,r+.02,r−.05
  cho.655709heuristic/.561573joint theo mô hình giả định,khôngđo. INCONCLUSIVE còn
  PRECISION/R4,không tựcho phép rerun. Không đổi scorer/card để có kết quả đẹp.
- Sampling còn chờnumericsv1.3.1 (K*/ref*/S1route/tail/coverage/timing/r). Thêm
  coverageinterior1/1000:degree12000 ởλA7.123/u1.234,maxpilot24;chỉarithmetic,
  chưađo engine/time/RAM. Khôngđổi rounding/measure hoặcbenchmark trêntrialCF.
- Bảng discovery16MV/72SH đãlessonđưa vàreplaycólog mới nối parenthash;frozenlog
  giữ nguyên.88oldrows thiếucoarsepairs→UNRESOLVED.3CLIrefusals/engine0; backend
  thực vàdry-runB DEFERRED. Khôngpilotmerge/srcpromotion/tagmới/CF/MC/R09R10outcomes.
- G1/Phase4HOLD,Understanding/P0-V10/L8/T05OPEN;auditL3R.3HOLD,D22DEFERRED,
  realismHOLD_UNSOURCED. L3R.8học/soạnđược; Gate3R/human không tự đóng.
- [Thiết kế](design/confirmation_v1_3.md),[report](../results/lessons/l3r_7/report.md),
  [completion](phases/L3R_7_completion.json).

### DL-077 — Tác giả duyệt luật n; ủy quyền chọn ngân sách theo máy (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Trả lời tới sau commit chuẩn bịc4b4bf5:
  luật n: “Đồng ý khóa luật này”; B/concurrency: “tùy theo ý bạn, bạn có thể xem
  máy củ tôi mà chạy”. [Nguyên văn](../results/lessons/l3r_7/author_choices.json).
  Không diễn giải thành tác giả trực tiếp chọn48CPU-giờ hoặc tự read-back.
- Khóa luật bốn vùng cùng n∈{30,40,60},lớnnhất vừaB theo p95bundle+fixedvalidation,
  dựphòng30%; BND15/vùng nếu cảhai vừa,khôngthì0; n30khôngvừa→HOLD/DL tăngB.
  Con sốn chỉchốt sau verifiednumericsv1.3.1,không từtiming cũ/phân bốtrialCF.
- ĐãđọcmáyWSL2: Ryzen57535HS,10logicalCPU/affinity0–9,RAM13.65GiB/available9.50GiB,
  load1min≈.184,CPUusage1s≈.49%,swap4GiBchưadùng. Snapshot15:00:53Asia/Saigon.
  cgroup2mount có nhưngcpu.max/memory.max khôngexposed; khôngcoi đó làvôhạn hoặc
  đãkiểmRAM/SSDhostWindows. Đâyresourceprobe,khôngenginebenchmark.
- Chọn theoủyquyền **B=48CPU-giờ tổng**,đãgồmdựphòng30%; profile1worker trước,
  khởiđầu2/tốiđa4workerprocesses theopeakRSS/load;1BLAS/OpenMPthread/worker.
  Pooltarget6GiB,chừa3GiBavailable/0.5GiBpooloverhead. Policy chưaOS-enforced,
  sẽtíchhợpbackend audited sau; chưalaunchjobs. 48/4=12h chỉlýtưởng,khôngETA đo.
- B làgiớihạnvậnhànhđượcchọn,khôngsốđo khảthi hoặc lýdocứu n60/PASS. ĐổiB cần
  version+DL; nếu budgethết thìpausekhôngchấmpartial,khôngbỏregime/đổicard.
- n/n_bnd/root/CF vẫnnull/0; numerics/D22/backend/human/Gate3R cònchờ.
  G1/Phase4HOLD giữ; checklist không còn author n-rule/B pending. Khôngpapersearch,
  calibration hoặc research engine run mới. Auditmetadata/receiptPASS; fullsuite
  587PASS ởc4b4bf5 làkếtquảkếthừa,khôngreruncho cậpnhậtmetadata.
- [Budget](design/confirmation_compute_budget_v1.json),
  [máy](../results/lessons/l3r_7/resources/20261029_01/snapshot.json).

### DL-078 — Đăng ký calibration numerics trước chạy (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu “bạn thực hiện cho tôi đi”
  sau khi được báo numericsv1.3.1 chặn phần thực thi còn lại củaL3R.7. Tiến hành
  calibration/audit trong scope hiện tại, không waive điều kiện khoa học/human.
- [Prereg](../experiments/R3R_07_numerics/prereg.md) vàJSON khai trước computation:
  3legacyanchorsK40/ref1,sáu stationarymarginalprobes cố định,312conditionalglobal
  jobs phủ96corners+8auditIDs ởmain/coarseK/coarsedt. Không seed/sampleCF.
- Stage0 phảiPASS trước activationfullglobalnumericsaudit. Bất kỳ error/resource
  ceiling/anchormismatch→HOLD,khôngglobalrun/tagv1.3.1/n/root/CF. Tail/route cũ
  chỉbaseline; fullaudit còncostmomenttail/S1/quadrature,R1–R8,κ3h16 vàruntime/r.
- Ceiling1worker,120CPU-s/180wall-s/4GiBRSS/5GiBAS mỗijob,1CPU-hour totalattempt;
  giới hạnCPU/AS thực bằngrlimit vàparentmonitorCPU/RSS/wall. Không nới theo outcome.
  Giữ failed/partial vàtracephase. Đâybudgetcalibration riêng,khôngđổi B48CPUhCF.
- Giữcard/contract/enginecore byte; khônghạ rategrid1/1000 hoặc tựđổi phươngpháp.
  Nếu khôngđạt, báoHOLD chứkhônggánconvergence smallness thànhtotalerrorbound.

### DL-079 — Calibration đã chạy; giữ HOLD theo stop rule (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Prereg commit **0efddcc** trước mọi run;
  full595/8numerics testsPASS. Đã hoàn tất9jobattempts trong1worker theoceiling.
- X2065/X1008/X1009 replayPASS,scalarsvà**4879pairs** khớp, numericpaircolumns
  theobitpattern sauparse. Không phải NPZcontainerbytes hoặc fullframeverification.
- Stationary3/6complete(base,degree120,κ3/ref2);degree1200 vàhai degree12000
  **UNRESOLVED/CPU_LIMIT**. Degree1200 dừngkhiLU437×437;degree12000A/B dừng
  khinumpy_roots,CPU120.406/120.449s,RSSmẫu2267.4/2267.5MiB. KhôngvượttrầnRSS4GiB.
- Tổng396.116CPU-s/394.422elapsed-s nối tiếp. Đâykhôngp95bundletime,khôngr của
  measureCF,không chứng minh mọithuậttoán bấtkhảthi hoặcB48CPUh khôngđủ.
- **HOLD_NUMERICS_FEASIBILITY** theo stoprule đãkhai:312conditionalglobaljobs
  chưamở,khôngtagv1.3.1 hoặc K*/ref*/n/root/CF. Khôngnới ceiling sauquan sát,
  khôngthay rounding/measure/route đểlấyPASS. Tailcost/fullaccuracy/dry-runB
  vàD22/human/Gate3R giữmở. Muốnmethod/ceilingmới phải cóversion/DL trước runmới.
- Tất cảfailed/partial/stdout/progress/resource được giữ. Cần engineering/audit
  thuậttoán stationary ởresolutionđãkhóa trướcfullglobalaudit;κ3marginalcomplete
  khôngchứng nhậnκ3h16costs. KhôngchấmHyp-MV/Hyp-SH hoặcđóngrealism/novelty.
- Kiểm sau run phát hiện cut_value helperV13_step1/regime.py thiếu explicit45-file
  manifest. Hash hiện tại khớp runcommit0efddcc;3anchorbitwisereplays cungcấp thêm
  evidence. Ghi làpost-runcheck,khôngsửaprereg hồi tố. Fullaudit phải khóa complete
  dependencyclosure; provenance này không đủ mởv1.3.1.
- [Report](../results/lessons/l3r_7/numerics_report.md),
  [CSV](../results/R3R_numerics/20261029_01/metrics.csv),
  [JSON](../results/R3R_numerics/20261029_01/verification.json).

### DL-080 — Tác giả yêu cầu đo dài hơn trên máy hiện tại; GCP là phương án dự phòng (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Yêu cầu nguyên văn: “vậy bạn chạy xong luôn đi,
  kiểm tra máy tôi có khả năng chạy không để tôi tắt app các thứ, nếu không ỏn thì
  tôi có server gcp á, bạn muốn cái nào”. Tiếp tục kỹ thuật,không hỏi lại quyền nới
  ceiling khi tác giả vừa yêu cầu. Không sửa/giấu kết quảv1 hoặcđổi card/measure.
- Resource WSL hiện tại10CPUlogic,RAMavailable≈10.62GiB,swap0. Chọn chạy1worker
  local trước để đo thực,ceiling1800CPU-s/2400wall-s/6GiBRSS/7GiBAS mỗi job;
  total7200CPU-s cho3marginals đãCPU-limit,giữexactparametersv1. Chính thức là
  resourceextension SAU outcomesv1,khôngclaim đãkhai mức này từtrước.
- [Configv2](../experiments/R3R_07_numerics/prereg_extended_v2.json) vàmd sẽcommit
  trước attempt mới; giữ solver/kernel hiện tại. Reuse3anchor+3lawpassv1; khôngCF.
- Read-only GCP: gcloudchưacóproject,aliasdt4n-gcpSSHtimeout20s; đã hỏi VM/capacity/
  access trong lúc tiếp tục local. Không tựcreate/start/resizeVM. Nếu cócloudrun,
  táchenvironment/version/manifest vàđo,không suy chỉcầnthêmvCPU làgiảiquyết.
- n/root/CF/tagv1.3.1 giữchưa cấp; callbackfullaudit/D22/human/Gate3R không đổi.

### DL-081 — Candidate hệ số tương đương khi baseline v2 đang chạy (2026-10-29)

- Người phụ trách: **Doan Van Tai**. V1đãcho thấyLU437×437vượt120CPU-s;v2đangchạy
  dài hơn, đãhơn7phút ởLU. Pháttriển numericalcandidate trongexperiments riêng,
  khôngsửa source/môi trường/ceiling hoặc dừngbaselinev2.
- Cùng spectralroots,v_j vànormalization, dùngnullvector Vandermonde
  c_j tỷlệr_j^(b-1)/(v_j P'(r_j)); khôngdenseLU. [Derivation](design/stationary_barycentric_candidate.md).
  Giữđúngintervalcertificate80digits/1e-10cũ, khônghạprecision/threshold/cardgrid.
- 8targeted tests so coefficientvớidenseLU,law/quantilevớireference,closedform
  vàcorruptionrejection. Test đầu lỗiAPI midpoint interval,đãgiữfailurelog vàsửa
  helpertest;khôngphải sửa science hoặc nới tolerance đểPASS.
- [Prereg candidate](../experiments/R3R_07_fast_stationary/prereg.json) chỉbenchmark
  cùngCAL_RATE_100_A;1800CPU-s/2400wall-s/1GiBRSS/2GiBAS,1worker. Táchsourcehash,
  committrước benchmark;notadoptedvào src/CF. CPUtime/wall ghi riêng vìbaseline
  cóthểcùngchạy. Candidate chưa giải quyếtnumpy_roots degree12000 hoặcfullaudit.
- Đo sánhimplementation tươngđương,khôngnewhypothesisoutcome hoặc seed/CF.
  GCPgiữSTOPPED theo thôngtintácgiả;khôngcloudmutation.

### DL-082 — Sparse-root/algebraic-certificate candidate trước profile degree12000 (2026-10-29)

- Người phụ trách: **Doan Van Tai**. Baselinev2 đã hoàn tấtdegree1200 sau806.568s;
  candidateLU-free hoàn tấtcùngpoint199.590s,quantiles5647/25370 vàposteriorerrors
  khớp,lawerror≈1.42415e-32;cảhai đượccertificategốc chấpnhận. Đâybenchmark
  numerical,sau khiđãthấyv1/v2partial,khôngpredictionkhoahọc.
- Tạo candidate riêng đểgiảm hai costkhác: rootproposals sparseNewton(double)
  vẫnphảirefine80digits/countb; certificate dùngVandermondeidentity,geometric
  residualsum vàintervalenclosure củaexacttargetcoefficients. Giữtailplan/
  returnboundvà1e-10;accountstoredcoefficientL1error. Đây **certificateevaluation
  mới**,khônggọi “codecũkhôngđổi”;fullaudit/adoption cònchờ.
- [Proof/scope](design/stationary_algebraic_certificate_candidate.md). 9root
  tests so densecompanion độc lập;9certificate tests gồmexactFractiondirectbalance,
  fullclosedformTV+tail,originalcertificateparity vàcorruptionrejection. Test
  helpercomplexparserbanđầulỗi,giữfailurelog rồi sửahelper,khôngnới acceptance.
- [Prereg profile](../experiments/R3R_07_fast_stationary/prereg_sparse_candidate_02.json)
  cốđịnhCAL_RATE_1000_A,1800CPU-s/2400wall-s/1GiBRSS/2GiBAS,1worker. Commitcode/
  sourcemanifest trước profile;baselinev2 source/environment khôngsửa hoặcdừng.
- Khôngsrcpromotion,CF/n/root hoặcclosurev1.3.1. Candidatepassmộtlaw khôngtựđóng
  globalcostaccuracy,tailmoment,arrayconversion,D22/Gate3R/human. GCPvẫntắt.

### DL-083 — Khóa hai kiểm tra tiếp theo cho candidate, chưa chạy (29/10/2026)

- Người phụ trách: **Doan Van Tai**. Trong lúc candidate02 và baseline v2 đang
  chạy, đăng ký hai probe với đúng implementation/source manifest của DL-082.
  Không sửa 59 source files đã khóa hoặc thay ngưỡng sau quan sát.
- Candidate03: cùng CAL_RATE_100_A đã có đáp án baseline; ceiling120CPU-s/
  180wall-s/1GiBRSS/2GiBAS. Đối chiếu quantiles chính xác và posterior trong
  error bounds cũ; certificate vẫn phải đạt1e-10. Đây kiểm reference parity của
  cả root proposal lẫn certificate mới, không chỉ công thức hệ số candidate01.
- Candidate04: cùng CAL_RATE_1000_B chưa giải xong bằng baseline; ceiling1800CPU-s/
  2400wall-s/1GiBRSS/2GiBAS. Chỉ chạy nếu candidate02 complete/certified và03
  đạt reference parity; các fast probes chạy nối tiếp, baseline v2 không dừng.
- Hai JSON prereg_sparse_candidate_03/04 sẽ commit trước mọi execution mới.
  Bất kỳ failure giữ raw và dừng chuỗi; không tự mở312global jobs, đổi source,
  tạo n/seed/CF/tagv1.3.1 hoặc suy certificate một law thành full accuracy.
  Đây tiếp tục calibration theo ủy quyền đo máy; GCP không khởi động.
- Làm rõ trước execution03/04: raw worker chỉ lưu `posterior_errors`, không lưu
  posterior point estimates. Vì vậy chỉ kiểm quantiles khớp và các error bounds
  posterior đạt1e-8/law đạt1e-10; không tuyên bố posterior point estimates đã
  đối chiếu trực tiếp. Không yêu cầu hai thuật toán có error bound bằng nhau.

### DL-084 — Candidate02 không chứng nhận được; khóa balanced candidate và chuyển profile nặng sang GCP (29/10/2026)

- Người phụ trách: **Doan Van Tai**. Candidate02 dừng sau1260.709wall-s,
  1260.656CPU-s,peak98.262MiB: `normalizer not certified nonzero`. Không phải
  thiếuRAM; không suy normalizer thật bằngzero. Theo DL-083,03/04 KHÔNG chạy.
- Tác giả đã bật VM và yêu cầu chuyển nếu local không chạy được. API xác nhận
  RUNNING,8vCPU/~31.3GiB. Tìm project trong Terraform; SSH timeout vì egressIP
  hiện tại khác hai /32 trong firewall. Tạo rule TẠM chỉ currentIP/32,tcp22,
  tagdt4n-research-vm; giữ rule cũ, xóa rule tạm sau lấy kết quả. Không start/
  resize VM hoặc sửa hệ thống/Conda environments đang có. GCP không tự sửa lỗi số.
- Tạo implementation riêng `balanced_certificate.py`: dùng cây tích khoảng
  cho cùng derivatives, không left-fold dài. Giữ80digits, mọi residual/tail/
  stored-error terms và threshold. [Proof](design/stationary_balanced_certificate_candidate.md).
  12targeted và633fulltestsPASS trước profile; regression1024factor chứng minh
  wrapping có thể làm left-fold baozero trong khi balanced vẫn chặt.
- Prereg05 local CAL_RATE_100_A,120CPU-s/180wall-s; phải khớp quantiles baseline
  và đạt error limits. Chỉ sau đó06/07 chạy trên GCP với hai marginalrate1000
  A/B đãkhóa,3600CPU-s/4800wall-s mỗi job,2GiBRSS/3GiBAS,<=2workers/1thread.
  Profilecloud ceiling được khai mới trước computation, không thay v1/v2 hoặc02.
- Checkout/venv riêng trên GCP;Python3.13.13 khác local3.14.5, sáu package pin
  theo local và kiểm633tests tại server trước profile. Mỗi worker lưu và kiểm
  environment khớp prereg. Source63files commit trước computation.
- Sau khi phiên bị ngắt, baselinev2 B không có finalresource/summary; lastsample
  CPU1815.55s vượt1800s, sau đó worker mất. Giữ recovered partial, không ghi
  ceiling-enforcementPASS hoặc biến1815.55 thànhfinalCPUtime. Không rerun B cũ.
  Mediumv2complete,A CPU-limit córeceipt vẫn giữ nguyên.
- Candidate vẫn NOT_ADOPTED; không CF/n/root/tagv1.3.1, không mở312globaljobs
  hoặc đóng costaccuracy/D22/human/Gate3R. Đây calibration, không hypothesis run.
- Trước cloud06/07, bổ sung controller `cloud_pipeline.py` vào manifest (64files
  cho cloud,63cho local05). Controller chạy độc lập SSH để tránh mất monitor khi
  client bị ngắt; preflight633tests + versions + local05parity trước hai jobs.
  Không sửa bất kỳ implementation nào đã chạy05 hoặc raw của05.

### DL-085 — Hai probe GCP hoàn tất; giữ HOLD cho adoption/full audit (29/10/2026)

- Người phụ trách: **Doan Van Tai**. Local05 theo prereg1c469c7; cloud06/07
  theo source/prereg269bed8, sau preflight633/633testsPASS (81.146s). Local
  balancedfull633PASS (83.38s),12balancedtargetedPASS;31frozenfiles giữbyte
  (21contract+10card). Không mở hoặc đổi các tag đã khóa.
- Medium cùng đầu vào: baseline806.568wall-s/806.161CPU-s; balanced05
  19.926wall-s/19.902CPU-s,peak71.211MiB. Quantiles5647/25370 khớp. Wallratio
  40.479 lần từ một attempt mỗi phiên bản trên local, không p95. Posterior chỉ
  đối chiếu savederrorbounds, không tuyên bố pointestimates đãcompare.
- GCP06 CAL_RATE_1000_A:902.514wall-s/902.461CPU-s,peak137.922MiB,
  lawerrorupper1.40770e-32,quantiles55424/251343. GCP07 B:329.654wall-s/
  329.601CPU-s,peak108.883MiB,lawerrorupper2.45347e-33,quantiles10172/77322.
  Maxposteriorerror mỗi ca≤4.01e-16<1e-8. Cloud2jobs chạy song song, tổng
  CPU1232.062s; không so crosshardware như isolatedalgorithm speedup.
- Balanced currentversion3/3complete; candidatehistory4/5complete (01+05–07),
  02ERRORgiữraw,03/04NOT_RUN. Baselinev2 mediumcomplete,A CPUlimit;
  Bpartial/thiếufinalreceipt vàlastCPU1815.55s vượtceiling,không tô thànhPASS.
  Do missingreceipt không có totalCPU chính xác; savedlowerboundallattempts
  7531.007s. Không thay số unknown thành số ceiling hoặc sample cuối.
- Đã tải29raw/log/metafiles từ server và soSHA256 khớp. Auditbookkeeping/
  frozen/source/artifactPASS; đây không đóng engineauditL3R.3. Đã xóa vàverify
  ruleSSH tạm bằngAPI; rulecũ giữnguyên,VMvẫnRUNNING do tácgiả bật,không tựtắtVM.
- Những kết quả này xác nhận khả năng tính các stationarymarginals đãđăngký.
  Không phải bound tổngsaisốphysicalcost/gain hoặc hypothesisconfirmation.
  Candidate chưaadopt vào src/globalbackend;312globaljobs/fulltail-moment/
  S1quadrature-arrayconversion/D22/dry-runB/p95+r cònchờ. Không v1.3.1/K*/ref*/
  n/root/CF mới. B48CPUhCF giữnguyên;calibration táchriêng. G1/Phase4HOLD,
  human/Understanding/P0-V10/L8/T05OPEN không tựđóng.
- [Report](../results/lessons/l3r_7/extended_capacity/candidate_report.md),
  [CSV](../results/lessons/l3r_7/extended_capacity/candidate_metrics.csv),
  [verification](../results/lessons/l3r_7/verification.json),
  [baseline partial](../results/lessons/l3r_7/extended_capacity/report.md).

### DL-086 — Thực hiện đầy đủ L3R.7: đăng ký full population numerics trước chạy (29/10/2026)

- Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu “chạy đầy đủ hoàn thành
  lesson này cho tôi đi”. Tiếp tục phần kỹ thuật còn DEFERRED; không biến yêu
  cầu này thành xác nhận Understanding, human review hoặc quyền chạyCFPhase4.
- Numerics route vẫn là lựa chọn mở trong contractv1.3. Chọn S1directπ, Stay
  cost hEπQ có separate moment certificate, và K-quadrature giữ atom/tail đầy đủ.
  Kernel Bellman giữ integer lattice/dynamics; piecewise compression có uniform
  error riêng. Native dyadic products giữ80digits, residual và acceptance1e-10.
  [Đặc tả/proof/phạm vi](design/population_numerics_v1_3_1_candidate.md).
- 33tests component mới và2tests arithmetic/R6; **668fulltestsPASS local**.
  Lỗi test ban đầu dùng decimal display thay exactbinary đã giữlog và sửa test;
  cacheAPI duplicatekeyword đã sửa trước physicalcalibration, giữfailurelog.
  Không nới probability/posterior/R1 thresholds hoặc đổi metric/card/measure.
- [Prereg full01](../experiments/R3R_08_population_numerics/prereg.json):3legacy
  replays +6native marginal regressions trước fullpopulation.114cases gồm104
  corner/auditrecords đãkhai,8rational-rate designs cốđịnh (khôngrandomCFtrial),
  2zero controls theo design. Mọicase cómain/coarseK/coarsedt. Globalcandidates
  hữu hạn80/2→160/2→160/4; chọnfirstallready, nếukhông thìHOLD khôngtag/seed.
- Chỉ xem numerical readiness/coverage/timing để chọnmức; không dùng tỷlệ
  effect/harm thuậnlợi đểchọnn. Timing cold-componentcharges theo unique cache
  keys; p95(methodhigher) của hai lớp corners/audit vàrationalrate lấy lớn hơn,
  khai trước outcomes, không nhận là populationp95. B48CPUh vàluật n giữnguyên.
- Calibration budget riêng12CPUh,3600CPU-s/4800wall-s/3GiBRSS/6GiBAS mỗijob.
  Controllerđộc lập mỗi job tránh doublecount RUSAGE_CHILDREN; durable cloud
  parent, đơnluồngBLAS; profile1→2 rồi tốiđa4 theo measuredmemorypool6GiB.
  CF0/root0/nnull tới lúc cóclosure thật; không tự mởPhase4 hoặc sửa tags cũ.
- GCPđangRUNNING do tácgiả bật. SSHrule tạmchỉcurrentIP/32,tcp22,targetVM;
  sẽxóa saucollection. Builddependency libboost1.74-dev lấy quaapt vàextract
  vào workspace riêng (khônginstallsystem/đổiCondaenvcũ),debSHA ghi prereg.
  Môi trường riêngPython3.13.13/sáupackagepin; GCPphảiPASS668tests trướcrun.
- Exposure mới chỉcác calibration đãkhai; sẽ reserve toàn bộjointkeys mới
  trong collisioninventory trướcCFdraw. R09/R10giữniêmphong; frozen card/contract
  và scorerprimary giữbyte. Thiết kế/nguồn đượccommit trước physicalrun mới.

### DL-087 — Dừng full01 vì dispatch bug; giữ records sai và đăng ký full02 cùng designs (29/10/2026)

- Người phụ trách: **Doan Van Tai**. Trong giám sát full01 phát hiện mapjobs
  dùng chungID legacy/calibration: ba X2065/X1008/X1009 bịoverwritten bởicase
  global, stage marginal khôngcólevels nên falselyCOMPLETED vớilevels{}. Đây
  lỗi điều phối, không phải ba anchor đã replayPASS. Không dùng chúng đểclosure.
- Đã dừng riêng controller/worker full01, giữ toàn bộpartial/caches/raw và
  stoprecord trênGCP. Tại snapshot13receipts,131.075CPU-s đãghi; worker đang
  chạy observed117.78CPU-s rồiSIGTERM; không gán nó finalCPU hoặc PASS. Có
  marginal/native và một số calibration đãexposed; không quay lại trạngthái
  chưa thấy. CF0/n/root vẫnnull.
- Sửa dispatch theo namespace stage và thêm guardkhôngchoemptygloballevels;
  resourcecontroller còn kiểm kind/payload trướcCOMPLETED.2regressiontests
  bổ sung. [Prereg02](../experiments/R3R_08_population_numerics/prereg_02.json)
  giữ nguyên114cases,9reference/marginaljobs,candidates/rules/budget; source107
  files và670fulltests trênGCP trước rerun. Không sửa prereg01/oldraw hồi tố.
- Full02 chạy lại toànregistered batch; cacheπ/profile chỉreuse khi source/
  parameters/SHA khớp, khôngreuse các empty anchor records. Actuallegacyreplay
  vẫn bắtbuộc. Rawđợt1 vàđợt2 táchdir; không chọn case/kếtquảthuậnlợi. Source
  sẽcommit trướcfull02. Không tagv1.3.1, n/root hoặcCF từđợt1.

### DL-088 — Giữ full02 và nâng độ chính xác posterior khi fast bound chưa đạt (29/10/2026)

- Người phụ trách: **Doan Van Tai**. Full02 dừng theo stoprule sau15receipts:
  3legacyreplaysPASS,6marginalsPASS,5globalbundlescomplete,1globalERROR;
  108globalcases chưa chạy. Tổng464.154668CPU-s; không CPU/RAMlimit.
  RATE_SH_BASE_K3_H16 báo `fast posterior error exceeds1e-8` sau171.006578CPU-s.
  Không gọi việc này hypothesisFAIL hoặc toànnumericsPASS; chưa chọnK*/dt*/n/seed/CF.
- Diagnostic cùng law/cachedprofile tìm binaryforwardbound max1.53536e-7;
  ba điểm q916318/1341550/1450400 có original80digitsposterior bounds khoảng4e-16.
  Đây là lỗi không có precisionfallback, không cho phép nới ngưỡng1e-8.
  Thêm fallback tới `SpectralLaw.posterior`, giữ certificate/acceptance nguyên;
  nếu originalinterval cũng khôngcertify thì tiếp tụcFAIL. Cache kết quả cùngq.
- Hai regressiontests: binarybound lớn nhưng80digits đạt; conditioningevent
  khôngcertify ở80digits vẫn phải reject. [Prereg03](../experiments/R3R_08_population_numerics/prereg_03.json)
  giữ114designs/3candidates/budget/metric/card; rerun registeredbatch ởdir03,
  source108files,672fulltests trênGCP. Không ghi đè02, khôngtag/CF trướcclosure.
- Diagnostic đầu nhầm costprofile tolerance so với cache đã đăng ký; dừng riêng
  process237625 sau khoảng26CPU-s, không coi là prereg experiment hoặcPASS.
  Diagnostic sau chỉ đọc completedprofiles; không có profileB thì ghi chưa có.
  Các diagnostic không phải dữ liệu confirmation. Raw/diagnostic được giữ riêng.

### DL-089 — Tác giả yêu cầu hoàn tất L3R.7; khôi phục full03 trên GCP (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu “tôi muốn chạy và hoàn thành
  lesson 7 luôn ... cá nhân hay server gcp của tôi và tự bạn hoàn thiện luôn đi”.
  Chọn GCP đang có môi trường/cache; không resize/start VM hoặc mở Phase4.
- Kiểm trực tiếp: VM đã stop/start, SSH hiện PASS, không controller/worker;
  122 receipts COMPLETED =9 reference/marginal+113/114 base, chưa refinement,
  chưa final summary. Vì sao VM dừng chưa xác định. Giữ nguyên interrupted03.
  Sao lưu1087files từ03/preflight, SHA256 khớp; SCP từng file timeout được giữ
  partial, chuyển tar stream thành công. Không biến progress cũ thành live state.
- Đăng ký recovery04 trước execution, controller mới ở
  `experiments/R3R_09_numerics_resume/`;108 estimator files cũ giữ byte. Kiểm
  snapshot/receipt/kind/level trước reuse, ca hạ tầng ngắt chạy lại ở output04;
  sau đó thực hiện đúng schedule80/2→160/2→160/4,114cases, ngưỡng và stoprule cũ.
  Không reuse failed/empty payload. Parent raw không sửa/ghi đè.
- Bảo toàn budget12CPUh: tính4060.270453CPU-s của122receipt cũ và dự phòng
  3605CPU-s cho ca ngắt thiếu final CPU; CPU thật của ca này vẫn unknown.
  Dùng luật RAM đã khóa, tốiđa4workers/1BLASthread. Cloud phải PASS680tests
  (672 cũ+8 recovery regression) trước computation. Code/prereg commit trước run.
- Exposure hiện gồm toàn bộ calibration03 đã lưu; không CF/R09/R10 mới,
  không chọn mức bằng effect/harm thuận lợi. Nếu ba candidate không đủ thì
  báo HOLD đúng evidence; chưa tạo tag/n/root/CF khi numerics chưa đóng.

### DL-090 — Candidate interval point evaluator và benchmark trên cache đã thấy (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Tiếp tục theo ủy quyền hoàn thiệnL3R.7;
  recovery04 vẫn chạy nguyên source/prereg. Candidate riêng
  `experiments/R3R_10_interval_evaluation/` đánh giá cùng stored-decimal spectral
  sums bằng dyadic384bits, giữ law/certificate/posterior1e-8, không thay estimand.
- Đã có12targetedtests so Fraction/reference/guards/fast-path; đây chưa là adoption hoặc
  fullnumericsPASS. [Derivation/scope](design/native_point_evaluation_candidate.md).
- Trước benchmark khóa ba q916318/1341550/1450400 từ diagnosticDL088, cachedlaw
  lambda7123/1000,managed617/500,kappa3,ref2; ba lượt mỗi evaluator trênlocal,
  báo toàn bộ CPU/wall,median vàsetupcompile riêng. Chỉ đọc cache đã có và
  kiểmSHA/source; không tạo law/jointoutcome/CF/seed mới, không claim cloudp95.
- Candidate NOT_ADOPTED. Muốn dùng trong population phải version/prereg mới và
  kiểm toàn batch; không đổi source114files của recovery04 hoặc sửa card/ngưỡng.

- DL-090 execution note: lần chuẩn bị đầu gọi systemPython thiếu mpmath; prereg
  chưa được ghi nên benchmark entrypoint từ chối ở check_committed trước đọc law.
  Giữ benchmark_resource/WORKER_FAILED (0.333CPU-s), không có phép đánh giá mới.
  Đã chuyển đúng .venv, commit prereg trước lần đánh giá lại; không sửa run lỗi.

### DL-091 — Chuyển full calibration sang native interval evaluator, replay toàn batch (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Theo ủy quyền tự hoàn thiệnL3R.7. Candidate
  có13targeted/integration và693fulltestsPASS local. Benchmark đã prereg trên
  cachedlaw4357terms/3q đã thấy,3repeat/method: medianCPU reference10.257424s,
  native0.681295s,ratio15.0558; values khớp trong bounds. Chỉ componentlocal,
  không claim speedup toàn engine/GCP hoặc thay infinite-law certificate.
- Để tránh tiếp tục trả chi phí evaluator cũ trong calibration, pause riêng
  controller04, giữ các worker/receipt tới checkpoint; sau tests sẽ dừng riêng
  jobs còn thiếu với stoprecord và export toàn partial. Giữ đúng COMPLETED,
  INTERRUPTED/UNRESOLVED và missing summary; không biến04 thành numericalPASS.
- Đăng ký full05 ở `experiments/R3R_11_native_population/`, injection tường minh
  `law_cache.FastLaw=NativePosteriorFastLaw` trước computation, graph đượchash.
  Rerun toàn9reference/marginal+114cases, cùng80/2→160/2→160/4, sameplant/metric/
  thresholds/cards/rounding. Không reuse old population results, chỉ cache law/
  profiles có cùngparameters/source/SHA. Native chỉ đánh giá precisionfallback
  của cùng storeddecimal sums; arithmetic/posterior acceptance giữ nguyên.
- Giữ calibrationbudget12CPUh, carry CPU receipts03/04 thực ghi được và reserve
  cho interruption03 chưa biết CPU. Resourceledger ghi riêng measured/reserve,
  không coi declaredceiling là đo CPU. Cloud phải PASS693tests trước full05;
  source/prereg commit trước execution. Không start/resize VM hoặc đổienv.
- Đây numerical engineering trướcCF, không chấm card/pickn theo tỷ lệ effect/
  harm. Candidate chỉ adopt/freeze nếu toàn registered accuracy audit đủ.
  Hếtcandidate/budget thì HOLD, không mở CF/seed hoặc nới ngưỡng để hoàn tất.

### DL-092 — Khai thêm mức global K/ref trong numerics còn DEFERRED, trước full05 (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Đã thấy calibration03/04: base80/2 không
  đạt toàn bộ R1/validity (71/113completedbase ready khi kiểm lại03). Đây là
  numerical calibration exposure, không CF. Chọn resolution bằng accuracy,
  không bằng tỷ lệ effect/harm. Không nhận proposal này đã có trong prereg03/04.
- Để hoàn thiện phần numerical levels cònDEFERRED theo ủy quyền, full05 khai
  một lịch hữu hạn trước computation:80/2→160/2→160/4 (ba mức cũ), rồi chỉ khi
  chưa đóng được mới320/4→640/4→640/8. Mỗi mức có hai coarse-axis neighbours;
  vẫn chọn **mức đầu mọi114case đạt** cùng ngưỡng R1/arithmetic/validity cũ.
  Không thêm framecases, bỏ ca khó, giảmprecision/threshold hoặc đổi plant/card.
- Đây mở rộng **calibration global resolution search trước numerics freeze**,
  không tăng R3 cho mỗi regimeCF: R3 vẫn đúng hai bước từ K*/ref* cuối. Thay đổi
  được version trong prereg05, không sửa historicalprereg hoặc coi là confirmation.
- Giữ tổng calibration budget12CPUh với carryledger03/04; tốiđa13levels/case
  (1482populationevaluations nếu chạy hết), stopbudget/resource/error cũ vẫn có
  hiệu lực. Nếu không đủ thì ghi HOLD có evidence; không tự tạo v1.3.1/n/root/CF.

### DL-093 — Khóa design validation/timing còn thiếu trước khi chọn global levels (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Trong khi full05 còn chạy, chốt design-only
  cho bước sau numerical selection; chưa chạy engine bổ sung hay tạo freeze/n/seed.
  File `full_numerics/native05/fixed_validation_design_v2.json` giữ checksum bảnv1.
- Dry-run B chỉ dùng bốn discovery coordinates đã có trong pilot: hai ID
  lexicographic đầu, không trùng physical key, trong mỗi MV+A/SH+A và đồng thời
  nằm trong calibration. Kết quả chọn bằng metadata: CAL_CORNER_033/034 và001/002.
  Không chọn theo giá trị gain/harm; không dùng mẫu thử từ measure hoặc CF.
- Timing bookkeeping identical-model dùng bốn rational-rate edge designs đã
  đăng ký: MV/SH × kappa.1/3,h16. Đây stress/timing trên calibration đã thấy,
  không là dry-runB hoặc estimatep−. Dùng same validated levels/source sau selection;
  GM vàGM|S1 phải zero chính xác. Ghi actual và cold-component planning charges
  riêng; fixed planning cho bốn checks lấy4×maximum cold-adjusted measuredcall.
- Cộng controls/anchors hai mức từ real receipts và measured candidate timings;
  không điền số giả vào fixedcost. Chỉ freezev1.3.1 khi fullaudit/coverage/validations
  đủ evidence; dry-runB/scorer sau freeze, rồi mới áp luật n/commitroot/prereg/CFlist.
- R1/card/CF-R3/B48/Phase4/human/Understanding giữ nguyên. Bản này không phải
  confirmation prereg hoặc evidence hypothesis; mọi physical call sau phải có
  source/design/levels/resource prereg cụ thể commit trước execution.


### DL-094 — Tạm dừng sau native05 và push toàn bộ code/artifacts (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu nguyên văn “bạn chạy xong
  tạm dừng lại đi, và push hết code lên cho tôi”. Không mở physicalrun tiếp.
- Native05 đãkếtthúcHOLD:286COMPLETED/2UNRESOLVED ởCAL_CORNER_049/050 raise_ref,
  lỗiJSON NumPybool. CPU6972.840511s,peak183.691MiB; khôngCPU/RAMlimit. Chẩnđoán
  tái hiệnFalse serialization, chưa productionfix; phảigiữ arithmeticFalse khi sửa.
- Local701testsPASS/GCPpreflight693PASS; export2410files khớpSHA; đốichiếu3948
  values03/04với05 khôngdisagreement ngoài combined arithmeticbounds. Đây không
  lànumericalreadiness/hypothesisPASS. Giữ raw/log nguyênbyte và cả các runcũ.
- R12validation/R13budgetresume chỉguardedpreparation, khôngprereg/run hoặcadopt
  24CPUh. Parentfailed bịbudget-only tool từchối. Khôngv1.3.1/n/root/CF;Phase4HOLD,
  human/UnderstandingOPEN; không đổi card/contract hoặcsealedR09/R10.
- Kiểmkhôngownedworkers/controllers. TemporarySSHrule đãxóa/APIxácnhận;VMvẫn
  RUNNING,agentkhôngstart/resize/stopVM. Pushmain thường, khôngforce/amendtag.
  [Pause report](../results/lessons/l3r_7/pause_report_20261030.md).

### DL-095 — Đóng L3R.7 bằng đường gọn: card v2 đổi bước làm tròn tốc độ, numerics theo R1 của contract (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Tác giả dán một hướng dẫn do phiên AI khác viết ("confirmation vẫn
  giữ, nhưng làm gọn"; card v2 nếu lưới 1/1000 là nguyên nhân bùng nổ chi phí) và yêu cầu nguyên văn
  “bạn hãy làm theo hương dẫn và đống lesson này giúp tôi đi”, rồi chốt phạm vi “tôi chỉ muốn đóng lesson 7
  này thôi, làm sao cho phù hợp đi”. VM GCP: “tôi đã tắt rồi bạn yên tâm”. AI soạn và chạy theo ủy quyền;
  không phải human review, không ghi tác giả đã dự đoán hay đọc card ([nguyên văn](../results/lessons/l3r_7/lean_close/author_choices.json)).
- Lý do đo được: trên native05 ca tốc độ lưới thô 0,2–1 s/mức, ca tốc độ 1/1000 230–780 s/mức; theo luật
  DL-077 (n ≥ 30, 48 CPU-giờ) card v1 sẽ HOLD_BUDGET kể cả khi numerics đóng. Tính lại native05 chỉ bằng
  R1 của contract: (160,2) 107/114 đạt, (160,4) 49/49 đạt, không ca nào vi phạm đồng nhất thức > 0,25 pp.
- Quyết định:
  - **card v2** = card v1, chỉ đổi bước làm tròn λA/λB/u thành r chọn theo luật khai trước (thô nhất trong
    {1/10, 1/20, 1/40, 1/100} mà 8 ca tốc độ lẻ lệch ≤ 1/400 và không đổi tiêu chí);
  - **numerics** chọn mức đầu tiên trong thứ tự native05 mà mọi ca calibration qua R1 (hai trục),
    sai số số học ≤ 1/4000 và kiểm nhất quán theo TOL_NUM × C̄ (thay cho cận số học);
  - n, kiểm cố định và dry-run theo đúng DL-077/DL-093.

  Mọi luật nằm trong [prereg](../experiments/R3R_14_lean_close/prereg.json) và
  [ghi chú](design/l3r7_lean_close.md), commit **trước** mọi phép tính của bước này.
- Giữ nguyên: card v1 byte; claim, vùng, measure, ngưỡng, α, π₀, R4/R5, verdict; contract v1.3; code tính
  122 file native05 (kiểm hash). Không engine trên CF, không R09/R10, không đổi r/mức/n/root sau khi rút.
  L3R.8 (D22, người đọc thật, realism, Gate 3R) và Phase 4 HOLD giữ nguyên. Cơ chế/validation là lesson sau.

### DL-096 — Kết quả đóng gọn L3R.7: r = 1/100, card v2, numerics v1.3.1-lean (640, 4), n = 60 (30/10/2026)

- Người phụ trách: **Doan Van Tai**. AI (Claude) chạy theo DL-095; mọi luật đã commit ở `1c0cab0` trước khi tính.
- Đối chiếu môi trường: 4 ca chạy lại trên local (Python 3.14) trùng **chính xác** native05 (GCP, Python 3.13).
- Chọn r: 1/10, 1/20, 1/40 rớt vì RATE_MV_EDGE_K1_10_H16 (λA 7,483 → lưới) đổi Ḡ_S 0,66/0,66/0,41 pp;
  **1/100 đạt** (lệch tối đa 0,145 pp, không đổi tiêu chí). Lưới 1/100 rẻ hơn 1/1000 khoảng 4–8 lần, không phải
  1000 lần như kỳ vọng ban đầu.
- Card v2 (`b62f329`, lock `dcfa01c`) = card v1 với bước λA/λB/u = 1/100; 9/9 kiểm L3R.6 đạt; card v1 nguyên byte, verify PASS.
  Thay đổi sampler (`ebe81c9`) đã **revert** (`fc6accd`) vì sampler nằm trong manifest hash native05; card v2 dùng
  sampler gốc với bước làm tròn đặt tạm trong `frame_v2.card_rounding`.
- Numerics: 118 ca calibration (106 ca thô native05, 8 ca tốc độ lẻ làm tròn về 1/100, 4 điểm nội vùng bậc lớn nhất),
  1062 phép tính, 0 UNRESOLVED.
  - Theo luật đã khai, các mức (80,2), (160,2), (160,4), (320,4) lần lượt rớt ở 17, 9, 6, 2 ca. Ở (320,4) chỉ còn
    CAL_CORNER_049/050, rớt vì cận số học ở láng giềng (160,4) là 2,77·10⁻⁴ > 1/4000.
  - **(640, 4) đạt cả 118 ca** (dt = 1/480).
- Thời gian (cache lạnh, local): p95 bundle 59 s (góc) / 457 s (tốc độ lẻ); chi phí cố định 2301 s.
  `power.select_allocation` cho **n = 60, BND = 15**, dự toán 45,4 CPU-giờ ≤ 48.
- Spec `notes/design/numerics_v1_3_1_lean.json`, tag `numerics-v1.3.1-lean` (local, chưa push), receipt riêng.
  Phạm vi: chỉ cho card v2; numerics của card v1 vẫn mở. R1/R7: chênh lệch làm mịn là chẩn đoán, không phải cận
  sai số được chứng nhận.
- Chưa có outcome CF nào. L3R.8 (D22, người đọc thật, realism, Gate 3R) và Phase 4 HOLD giữ nguyên.
- Đính chính (AI, cùng ngày): số phép tính calibration là **1298** (118 ca × 11 mức), không phải 1062 như dòng trên.

### DL-097 — D22 chuyển từ điều kiện vào Phase 4 sang Phase 5; contract-v1.3-amend1 (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu nguyên văn "… bạn hãy mở ra và đống lesson cho tôi đi đây là
  yêu cầu" ([attestation](../results/lessons/l3r_8/author_attestation.json)). AI (Claude) chọn theo khuyến nghị lesson
  L3R.8 §4.1 và ghi đây là **quyết định AI theo ủy quyền**, không phải lựa chọn tác giả tự viết.
- Mâu thuẫn G4: contract §7 đòi D22 implement + audit trước Phase 4; card v2 dòng 191 cho F̄/V̄ = null nếu chưa có.
- Quyết định: Phase 4 chạy không có D22, F̄/V̄ = null. Hạn D22 dời sang trước Phase 5
  ([amend1](design/contract_v1_3_amend1.md), tag `contract-v1.3-amend1`; tag `contract-v1.3` nguyên byte).
  Câu SH giữ "state repair (backlog + mode oracle) dưới M0"; không nói "backlog tươi/telemetry tươi có hại".
- D22 **chưa được implement**; đây là việc của Phase 5. Không đổi card, numerics, n, root hay danh sách CF.

### DL-098 — Realism HOLD_UNSOURCED là outcome; Phase 4 claim ở mức mô hình (30/10/2026)

- AI theo ủy quyền (cùng yêu cầu), khuyến nghị lesson §4.3 (b).
- HOLD_UNSOURCED là outcome của L3R.4, không phải lỗi validity: envelope `6bef959` có trước nhãn `1164500` (ancestry đã kiểm).
- Phase 4 không bị chặn. Mọi claim kèm câu phạm vi contract §6. Không claim realism, tần suất ngoài đời hay vận hành.
  Realism chuyển Phase 6/7.

### DL-099 — P0-V10 giữ OPEN làm điều kiện trước lần chạy Phase 4 (30/10/2026)

- P0-V10 cần **một người khác** có quyền nói "không" đọc contract/card; tác giả hoặc AI không thay được (rủi ro ER3).
- AI **không tự miễn** luật tác giả đặt. Trạng thái: OPEN. Phase 4 Bước 0 (nối và kiểm runner) được làm; **lần gọi CF
  đầu tiên chờ** P0-V10 đạt (a, có người đọc) hoặc tác giả tự miễn bằng DL (b, như V9/DL-054).

### DL-100 — L8 dời sang Phase 8 (30/10/2026)

- AI theo ủy quyền, khuyến nghị lesson §4.2. L8 (người đọc ranh giới prior/novelty) ảnh hưởng claim novelty, không
  ảnh hưởng validity Phase 4. Dời tới final novelty audit Phase 8. Không claim novelty trước đó; Gate L giữ "GO có điều kiện".

### DL-101 — Đóng audit engine L3R.3 có phạm vi (card v2) (30/10/2026)

- AI theo ủy quyền. Bốn lý do HOLD của DL-068:
  - (i) read-back của tác giả: phủ bởi xác nhận ngoài vở chung của tác giả (attestation; nội dung không ở repo);
  - (ii) numerics và chi phí S1 ở κ = 3 vượt 0,25 pp ở K160: giải cho card v2 bằng engine native, lối S1 trực tiếp,
    mức (640, 4) đạt R1 trên 118 ca, gồm κ = 3, h = 16 (DL-096);
  - (iii) cận population: engine native có cận số học từng contrast (≤ 1/4000);
  - (iv) D22: dời Phase 5 (DL-097).
- Trạng thái: **CLOSED_WITH_SCOPE_CARD_V2**.
- Giới hạn còn ghi:
  - chênh lệch làm mịn là chẩn đoán, không phải cận được chứng nhận;
  - chưa chạy MC độc lập trên engine native ở (640, 4);
  - numerics card v1 (lưới 1/1000) vẫn mở.

### DL-102 — Gate 3R: NARROW (30/10/2026)

- AI chọn nhãn theo ủy quyền "đóng lesson cho tôi", khuyến nghị lesson §4.4. Tác giả xác nhận ngoài vở các phần tự
  đọc/tự viết (attestation).
- **Claim gắn kèm:** Phase 4 kiểm Hyp-MV và Hyp-SH (card v2, sha `60335b61…`) trên 270 regime CF, ở mức mô hình
  (plant fluid đã khai báo, contract §6). Không claim realism hay vận hành. S1 là benchmark có quyền oracle.
  D22 chuyển Phase 5.
- Vì sao NARROW:
  - không phải GO, vì realism chưa IN/EDGE ở bối cảnh nào (UNSOURCED);
  - không phải HOLD, vì những gì còn thiếu (runner, P0-V10) là điều kiện vào Phase 4, không phải lỗi validity
    của Phase 3R;
  - không phải REFORMULATE/PIVOT/DROP, vì không có bằng chứng estimand sai hay tín hiệu đã mất.
- Ba bảng, hash và điều kiện vào Phase 4: [gate note](phases/PHASE_3R_gate_note.md).
- G1 không đổi. Phase 4 mở sau Bước 0 (runner) và P0-V10.

### DL-103 — Mở Phase 4 (hợp nhất discovery), numbering v1.2 (30/10/2026)

- Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu triển khai cả ba phần L4.1;
  AI soạn [entry decision](phases/PHASE_4_entry_decision.md), trình hai phương án
  rồi nhận lựa chọn nguyên văn **“Chọn v1.2: Phase 4 hợp nhất, Phase 5 confirmation,
  Phase 6 mechanism (khuyến nghị)”** ([record](../results/lessons/l4_1/author_decision.json)).
  Đây là lựa chọn của tác giả; phần lời giải/record do AI soạn không được nâng
  thành tác giả tự viết hoặc Understanding PASS.
- Có hiệu lực từ DL này: **Phase 4 (hợp nhất discovery)** → **Phase 5 (confirmation)**
  → **Phase 6 (mechanism)** → Phase 7 (independent validation) → Phase 8 (practical
  relevance) → Phase 9 (synthesis + final novelty audit) → Phase 10 (paper).
  Bảng ánh xạ sáu dòng ở entry decision; số cũ trong DL-097–102, contract/card
  frozen và MASTER PLAN v1.1 ngoài repo giữ nguyên. Luôn đọc kèm tên phase.
- D22 có hạn **trước phase mechanism**, nay Phase 6; L8 trước final novelty audit,
  nay Phase 9; P0-V10 OPEN trước lần tính CF đầu tiên ở Phase 5 (confirmation).
  Đây là ánh xạ tên, không thay nội dung amendment hay scientific thresholds.
- Baseline và luật đọc; số/vùng card mới; ngân sách CF-v3; nhãn Gate 4 là **bốn
  quyết định dành cho tác giả**, AI chỉ chuẩn bị. DL này không chọn chúng.
- [Discovery record](phases/PHASE_4_regime_map_discovery_record.md) commit `7385015`
  trước DL: raw1430→1376,54duplicate khớp,10/10recountchecksPASS. Chỉ câu6/7
  là discovery ứng viên; chưa native/baseline/novelty, G1 giữ nguyên.
- Không có `PHASE_4.md` v1.1/gói kiểm đi kèm trong input; entry này áp phạm vi ba
  lesson đã cung cấp, không giả đã tiếp nhận full plan. Exposure/forking phải
  commit trước L4.3 Part B hoặc hộp mới L4.5. Không CF/R09/R10 outcomes mới.


### DL-104 — Baseline margin + Stay, luật đọc do tác giả duyệt (30/10/2026)

- Tác giả chọn nguyên văn “Chọn gói đặc tả đã soạn (khuyến nghị)” trước outcomes;
  spec/author choice/prereg commit75037cc. [Decision note](phases/PHASE_4_baseline_reading_decision.md).
- ρ={0,.005,.01,.02,.05}; tune riêng18MV/72SH với target00/10, đều distinct keys,
  regret/Cref, tieρnhỏ. θ từStay, khôngoracle hoặc cộngvàocost.
- MVmedianR_M≥.5 và SHmedian|GSθ|/Cref<.005 kèmmedianΔL10<0 làluật câuclaim;
  không đổi verdictv2. Forecast AIsoạn theoủyquyền cụthể, khôngselfprediction.
- Run dừngsanityHOLD ởSH đầu; **chưa chọn/freezeρ***, chưa dùng luật mô tả để
  kết luận toànvùng/CF. Giữfailure/threshold, không thêmcard hoặc gỡL4.3HOLD.
- [Results](../results/lessons/l4_4/report.md), G1; DL103decision#2–4 còn tácgiảchọn.


### DL-105 — L4.5 Part A vàluật sàng, chưaquyết sốcard (chốt31/10/2026)

- Tácgiả chọn “Giữ SV và SUB có điều kiện (khuyến nghị)” và “Chọn gói luật sàng
  đã soạn (khuyến nghị)”; [record](../experiments/P4_05_candidates/author_choices.json).
- Proposal736633a; rules/source624a9be trước realp-hat. n60,α1/40,π0.5,
  haircut.1,robustpower≥.5,U≤.05,max3boxes; r_minus riêng, F1khôngđổi.
- [Decisionnote](phases/L4_5_screening_decision.md) và [PartA](phases/PartA_candidate_filters.md)
  giữ prior/câuclaim cóphạmvi, không nângnovelty hoặcdouble dissociation tựđộng.
- Exactdesign tables14/14,16targeted/813fullPASS; realboxes0. PartBblocked bởi
  native/baseline/rhopolicy/bounds, không suy0card từ thiếudữliệu.
- DLcuối về0/1/2card, vùng, CFv3budget vàGate4 cònOPEN. G1/cardv2/HOLD cũ giữ.


### DL-106 — L4.4-A1 theo ủy quyền rõ ràng trước plant (31/10/2026)

Người phụ trách: **Doan Van Tai**. Người dùng trả lời cả ba câu hỏi bằng lệnh ủy quyền lưu ở notes/phases/P4_A1_author_delegation.json. AI soạn và chọn chi tiết theo ủy quyền; không tác giả tự dự đoán/tự viết, không human Understanding.
Premise: diagnosis commit1a8d83a sau HOLD cũ, codeec5fd62; mới0engine/0CF. File choices L44_A1 chứa forecast trước run và cap1/10 mỗi support/8CPUh.
Đổi: theta0 bit check trước, same-route/S11 invariants, raw cross-route flags chỉ report/lean; NOT_READY dừng khi vượt cap*N kế hoạch. Giữ lưới rho/argmin formula/tie/read DL104,90điểm/4benchmark/budgetrule và frozen engine/card/CF.
**Đổi phạm vi selection:** rho* và mô tả trên READY subset nếu NOT_READY>0; ghi N/N_ready/exclusions, không nhận giữ nguyên full-scope DL104. Không coi sàn mới luôn cao hơn sàn cũ. Bất kỳ BUG thì dừng, không sửa code sau freeze; root cause chưa xác nhận.

### DL-107 — SV combined native+baseline, đối chứng và luật đọc theo ủy quyền (31/10/2026)

AI chọn theo cùng lệnh ủy quyền; choices L43_A1_SV trước outcomes. SV+=450A keys trừ sealed R10; SV−kappa[2,3],h[1,4],eta>=1/2,amp6,lambda không chặn thêm, chỉ exposed keys. Target00; narrow khi median GS_theta/Cref<.5% và median deltaL00<0. Caps NOT_READY/pilot1/10 mỗi support,8CPUh; selected rho trên READY subset và báo exclusions.
Không sàng hộp/p-hat/card; manifest NOT_READY phải UNRESOLVED; L45 còn cần readiness mọi candidate. K6 vẫn UNVERIFIED, không dùng input khẳng định K6 đã tái lập. Forecast AI đã ghi trước run, không author-independent.

### DL-108 — SUB phương án B, probe5 theo ủy quyền (31/10/2026)

AI chọn theo lệnh ủy quyền, không tác giả tự chọn độc lập.5AB points kappa1/20 đều trên sorted exact key, gồmP43_0000; main640/ref8,neighbors320/ref8 và640/ref4. Caps NOT_READY/pilot1,2CPUh; BUG dừng ngay.
Luật trước run:>=4/5 đạt **native** R1 hai trục+width+lean và max bundleCPU<=600s thì đề xuất giữkappa>=1/20 cho coverage L4.7 tiếp, ngược lại đề xuất thu hẹp>=1/10. Baseline readiness báo riêng, không thay native criterion bằng combined status; không claim coverage toàn vùng hoặc hiệu ứngSUB. Cardv2/CF giữ nguyên, chưa có cardv3/runSUBcombined/readiness receipt.


### DL-109 — L44_A1 dừng theo cap, F1 baseline vẫn HOLD (31/10/2026)

ControlPASS;benchmark3PASS/1NR;budget2.929164CPUh/8commit3cef246 trướcfull. Full16/90:8PASS/8NOT_READY,SH8/72>10%,0BUG. Tổng19observed(11PASS/8NR),71NOT_RUN;19native-ready nhưngbaseline9arithmetic/12R1events. Khôngrho/claimnarrow/forecastmedian toànvùng;guard summarizeexit1 giữlog.829.655796evalCPU-s gồmcontrol. Khôngrerun/nới tolerance;newcompletion khôngđèhistory.

### DL-110 — SV combined A1 hoàn tất kỹ thuật, baseline không narrow (31/10/2026)

Full497/497:496PASS/1NOT_READY(P43_0605,baselineR1 rho5%);449SV+ gồm448READY,48minusREADY. Prereg7c7c956,budget5.539996CPUh/8commit4bf82f8;5821.730407evalCPU-s gồmcontrol. Rho1% chọnđúngargmin/tie trên448READY:medianGS/Cref.97184136495%→1.02154525679%,medianΔL00+.000505476packet·s. KhôngnarrowtheoluậtSV;khôngsuykémmọiregimevìmeanargmin khácmedian. Map5physicalclassflips,19full-classR6unknown,0pilotflagcases;criterionGS uncertainty9/449(1NR+8near),minus0/48. Đây numericaldiagnostic trênsupport đãkhai,khôngboxMEETSfrequency hoặccardconfirmation.
Export497rows/hash/deltas/scoring kiểm độc lập về phép tính PASS;0boxcounts. ExtraΔL00diagnostic chỉfail đúngP43_0605 đãNOT_READY,448READY đềuđạt; không đổi readinesscriterion sauoutcome. ForecastAI R6 10–30% khôngđứng ở dữliệu support đãkhai(~2% tổngU),khôngđổi luật đểcứuforecast.

### DL-111 — Áp nguyên văn luật SUBprobe; chưa globalcoverage (31/10/2026)

Preregbf767f2,budget.348006CPUh/2commit6686b28. Full5/5complete,4PASS/1NR,0BUG;native4/5ready,maxbundle164.404769CPU-s<=600;425.712089evalCPU-s gồmcontrol. Đềxuấtgiữκ>=1/20 choL4.7coverage tiếp,theo DL108;khôngnativePASSmọivùng/SUBeffect. P43_0595 failR1K/dt/width;Crefdt tấtcả5đạt khôngthaythếmọiR1. XM2X000Crefdt .310539%→.077918% ởref8,khôngsuyglobalconvergenceorder.
F1baselineHOLD,combinedSUB/candidate_readiness/L45PartB/0-1-2cards/Gate4 cònmở.0CF/sealedoutcomes/boxcounts,cardv2/contract/F1/ngưỡng giữ nguyên;G1/P0V10/L8/Understanding khôngnâng.


### DL-112 — A2 probe R3 cho đủ8 baseline failures, trước engine (31/10/2026)

Người phụ trách: **Doan Van Tai**. Tiếp diễn ủy quyền AI của tác giả và yêu cầu hiện tại; evidence notes/phases/P4_A2_author_delegation.json. AI soạn/chọn chi tiết/forecast, không tác giả tự viết hoặc human review.
Diagnosis885401d:19points/95pairs,8fails mỗi1rho,W3/K6/D3,L00/GS_theta;upper-middle diagnostic đã sửa thànhmedianchuẩn,khôngđổi readiness. Khôngước lượngSHprevalence từ8/72.
Probe đủ8×7level theoR3(6404→12804→12808),mọirho,mỗi main có2coarseneighbors,khôngearlystopREADY. Controlu0finest,1worker/BLAS1;case3600CPU-s/4800wall-s/3GiB,overall3CPUh tínhuniqueeval gồmcontrol,checks giữađiểm. Replay24savednumerical/error/baseline fields+reparsedbits,holdhistSHA;BUG/replay/guard/execution/cap thìdừng vàkhôngdecidepartial.
Ngưỡng>=7/8LADDER_RESOLVES;<=4/8B1_CLAIM_LEVEL_ROBUSTNESS;5-6INCONCLUSIVE,DLmớinếutiếp. B1địnhnghĩađủtrongamendment: A3riêng full90,giữmọiđiểm,3levelρ/reading phải trùng;khôngtươngđươngcertificate/R1perpoint vàkhôngsửaprimarycard/scorer. A2chỉkhóanhánh,chưachạyA3/rho/regionalmedians.
ForecastAI:4/8READY,nghiêngH_cliff trongfinite ladder,K dễcảithiệnhơnW,cóít nhất1rho failuremới;0BUG,replay24/24. SourceA1/SV/SUB/contract/PC/ngưỡng giữ;G1/P0V10/L8/UnderstandingOPEN,0CF/sealed/boxcounts.


### DL-113 — Kết quả A2 áp nhánh B1 đã khóa trước run (31/10/2026)

Người phụ trách: **Doan Van Tai**. Ghi sau thực thi, không backdate thành prereg.
Choices/forecast do AI soạn theo ủy quyền; không tác giả tự viết/human review.
Prereg b5ae553 trước control/probe; 870 full tests PASS 86,83 s, 28 targeted PASS
1,48 s. Đủ 8×7 discovery levels +1 control =57 calls, 1.280,950894 evaluation
CPU-s gồm control 16,556818 s, dưới cap 10.800 s. Control PASS, replay 24/24 saved
numerical fields/significant bits parse lại khớp, 0 BUG/mismatch/execution failure.

Native readiness 8/8 ở cả ba bậc; baseline toàn bộ ρ cùng READY lần lượt 0/8,
2/8, 0/8. P44_006/P44_007 READY tại 1280/4 nhưng fail K trở lại tại 1280/8,
chênh L00 tương ứng 0,269075%/0,264282% Cref >0,25%. First-READY vẫn đếm 2/8
theo luật đã khóa; không che kết quả 0 READY ở bậc cuối. W3→3→3, K6→3→6,
D3→1→4; lỗi refinement vẫn chỉ L00/GS_theta. Không có failing ρ mới.

Vì 2≤4, quyết định đúng DL-112 là **B1_CLAIM_LEVEL_ROBUSTNESS**. F1 baseline
vẫn HOLD chờ A3 validity. A3 cần package/prereg riêng và full 90 keys, giữ mọi
điểm; cùng ρ* và cùng quyết định đọc trên 640/4, 320/4, 640/2 mới được gọi
aggregate stable. Đây không tương đương certificate hoặc R1 per-point; ba mức
có thể cùng bias. A2 chưa chạy A3 hoặc tính ρ*/regional medians.

Forecast AI 4 READY sai (thực tế 2); dự đoán có ρ fail mới sai (0). K giảm ở
bậc giữa nhưng không bền ở bậc cuối; W giữ nguyên. Dự đoán 0 BUG/24 replay
khớp. Kết quả phù hợp hướng nghiêng H_cliff trong finite ladder, không physical
mechanism proof hoặc kết luận mọi refinement sâu hơn đều thất bại.

Audit Fraction độc lập PASS, 14 source +80 history SHA khớp, ba preregs A1/SV/SUB
giữ nguyên. Raw arithmetic False/validity flags 37/57 vẫn được báo riêng theo A1,
không đồng nghĩa BUG hoặc lean readiness FAIL. G1, card v2/contract/ngưỡng,
SV/SUB giữ nguyên; 0 CF/sealed/new coordinates/box counts. L4.5 Part B/combined
SUB/readiness/Gate 4/P0-V10/L8/Understanding còn mở. Report:
`results/lessons/p4_a2/report.md`; completion `notes/phases/P4_A2_completion.json`.


### DL-114 — A3/B1 chốt baseline và đóng nhánh numerical (31/10/2026)

MV/SH đều STABLE ở3mức: rho5%/0, MV narrow với medianR_M.862967–.867986; SH khôngnarrow.
Không readiness reason nào tại rho*; gap runner-up MV>=.94165%Cref/SH>=3.65091%, max score drift từmain .03352%/.01323%.
Đây finite sensitivity, không convergence proof; không giả recovery đơn điệu theo rho. Không A4, giữ mọi failure lịch sử.

### DL-115 — Part B: một hộp mỗi candidate, SV không chờ SUB (31/10/2026)

Tác giả chọn “Chạy một hộp SUB (khuyến nghị)”; AI theoủyquyền soạn chi tiết/forecast,khônghuman-selfwork. Hai hộp+76SUBkeys+luật0/1/2card khóa trước mọi count; SV chỉ449/48keys registered,7keys khác trongplus-envelope chưa cócoverage. Chỉ đổi screen/test để preflight riêng từngcandidate, kernel/threshold/power v1 nguyênbyte;0hộpthật lúcrelock. SUB dùngexplicit-case loader/runnerA1,main640/8+neighbors320/8,640/4,target00/readingMV+A,cap8CPUh,giữNR. MỗiPASS_SCREEN thêm1cardtheoủyquyền,baseline narrow chỉđổiwording;khôngthêmhộp/rerefine đểcứu,khôngCF.


### DL-116 — SV FAIL_SCREEN; SUB tạm dừng theo yêu cầu, chưa quyết sốcard

SV trial1: plus216MEETS/224FAILS/9UNRESOLVED trên449,minus0/48MEETS; p_cond27/55,r_plus9/449,p_plan43/110,power≈2.5655e-5<.5 ->FAIL_SCREEN. KhônghộpSVbổsung. Tácgiảyêucầu tạmdừngjobdài vàpush: SUBđã10/76completePASS,2inflight/64notstarted,group257934SIGSTOP. SUBchưa baseline/rho/manifest/screen;finalcardcount=null,khôngsuy0card. Checkpoint/report results/lessons/l4_5/part_b/. Chỉresume khi tácgiảyêucầu;khôngCF.


### DL-117 — L4.5 (v2): đổi loại evidence, park SUB và gói CF-v2 (31/10/2026)

Người phụ trách: **Doan Van Tai**. Trạng thái **ADOPTED_BY_AUTHOR_DELEGATION**.
Tác giả yêu cầu “bạn hãy thực hiện yêu cầu của lesson giống yêu cầu thực hiện các
lesson ở trên đi”; AI theo ủy quyền tiếp diễn chọn phương án khuyến nghị (a),
soạn chi tiết và learning note. Không giả tác giả tự viết/ký hoặc human review.

**Thiết kế hiện hành:** 0 card mới/F2, không card-v3/CF-v3. Park gói MV/SH
CF-v2 (270 tham số, chưa outcomes) để có thể xem lại riêng như kiểm phụ; giữ
nguyên card/prereg/numerics/CF list và P0-V10 gắn với gói đó, không đánh dấu
gate đã qua. Giữ Main RQ, contract v1.3, engine, S01–S18, toys và baseline A3/SV.
Thay đường chạy tiếp của DL-115/116 bằng tách nguồn → clipping/mechanism →
realism → freeze hypothesis/held-out điều kiện. Không đóng toàn Phase4 tại đây.

**Lịch sử đã thấy khi quyết định:** SV FAIL_SCREEN (DL-116) được giữ/báo đầy đủ;
216MEETS/224FAILS/9U trên449plus,0/48MEETS ởminus. Đây là feasibility fail
theo haircut/power/unresolved, không chứng minh không có state effect và không
tương đương một phép kiểm median. Riêng median SV+≈.97% là observation.
A3 MV recovery≈86%/rho5% nên narrow; SH rho0 không narrow. Không tuyên bố đổi
hướng là trước discovery: nó diễn ra sau SV FAIL và10SUB native keys đã lộ.

**SUB10/76 được park làm discovery.** Kết thúc processgroup257934 khi còn STOP,
không SIGCONT;10keys/30levels đã lưu giữ nguyên byte,2calls chưa ghi kết quả
bị hủy,66keys còn lại không có evaluation hoàn chỉnh. SUB chưa có rho/manifest,
p-hat hoặc screen verdict;0card là quyết định scope/design, không phải SUBFAIL.
Các lệnh resume trong pause snapshot cũ được nghỉ dùng, không xóa snapshot.

**Lý do và giới hạn:** ưu tiên effect distribution/boundary, cơ chế và prediction
có thể sai trên điều kiện mới. Card/CP cũ vẫn hợp lệ cho câu hỏi prevalence theo
measure đã khóa; deterministic không là exact/continuous hoặc lý do làm thống
kê mất hiệu lực. Held-out condition chưa chọn, realism/D22/mechanism chưa làm,
nên chưa có evidence thay thế, G1/ownership/Understanding/L8 không tự nâng.
Báo cả lịch sử này trong freeze L4.9; không đọc R09/R10 hoặc outcomesCF.

**Thực thi:** [bảng giữ/park và learning note](phases/PHASE_4_v2.md),
[parking record](../results/lessons/l4_5_v2/parking.json). Không tìm thấy bản gốc
PHASE_4.md v1.1/PHASE_4_v2; tạo pointer và bản triển khai tối thiểu từ lesson,
không giả đã sửa toàn văn/Phụ lục B. Chỉnh lý toán học được ghi riêng với raw
lesson nguyên byte. Lesson này không tạo scientific evidence; tiếp theo L4.6.


### DL-118 — L4.6 (v2): decomposition discovery, chỉnh lý D22 và bound (31/10/2026)

Người phụ trách: **Doan Van Tai**. Thực hiện theo yêu cầu tiếp lesson6 và ủy
quyền trước đó; AI soạn predictions/learning note, không author-self hoặc human
review. Predictions59971ae trước phân tích; source cuối56b6090. Không đổi Main
RQ, contract, bốn costs, metric/normalization, reading thresholds hoặc baseline.

Đọc được Part1/Part2; attachment code ở UUIDa33f61c8 không có tại đường dẫn
được cung cấp. Dựng script theo đặc tả hai phần, không nhận đã chạy code thiếu.
Pilot map1/map2/map3age amp6:1136raw→1118unique,18duplicates khớp, giữ các age
experiments. Native597keys riêng:449SV+/48SV−,18MV/72SH tại640/4;10SUBpark
tại640/8. Không pool resolution/engine vào một prevalence estimate.

Kết quả median%Cref: SV+GS|M1=1.169907,GS=.969564,Gamma=.126433. Pilot
A/AB/C medianGS|M1=1.677613/.682230/.013852; ABq10–q90=.026992–2.583081
không được gom toàn bộ thành “chỉ tương tác”. SUB10medianGS=6.775916,
GS|M1=.056896,Gamma=−6.683420. P1/P3/P4 đúng theo prediction đã ghi; P2 sai,
peak median marginal ởkappa/tau=.075,n18,không chứng nhận S10mechanism.

Identity/export/source/quantile checks PASS; giữ97negative metric estimates
trên54keys(3SV+/51SH),50rawarithmeticFalse. MinimumGS|M1=−.104205109pp ở
P44_009; nhỏ hơn.25pp không là certified error bound hay S07PASS. Khôngclamp
hoặc refine/A4 để cứu. Fulltests/commands/diagnostics xem report.

Hai chỉnh lý logic: |Gamma|<=max(GM,GM|S1) không suy |Gamma|lớn⇒GM|S1lớn
khiGamma<0. D22contract giữY trongE[gap_hat|Y,Q], không phảiP(mode|Q).
Finite stationary Markov toy cócùngY/Qmarginals chohaiLcbs khác nhau dù cả
haiqua telescoping/one-hot; đây chỉ làsemantic counterexample, khôngfluid
measurement. Savedoutputs khônggiữjointcầnthiết nên nativeD22/F/V vẫn
DEFERRED/null,0probes. Khôngsửa frozencontract đểkhớp policyQ-only.

0physicalcalls/CF/sealedoutcomes mới; chỉ10SUBdiscoveryđãpark, không66keys.
G1/Understanding/T07authoraddendum/L8vàCF-v2parkinggiữ. Được tiếpL4.7;
khôngnângclaim practicalfreshness khiD22chưacó. [Report](../results/lessons/l4_6_v2/report.md),
[learningnote/chỉnh lý](lessons/L4.6_v2_learning_note.md),
[CSV/JSON/figures](../results/lessons/l4_6_v2/analysis/summary.json).


### DL-119 — L4.7 (v2): P-clip, native checks và dừng predictor constant (31/10/2026)

Người phụ trách: **Doan Van Tai**. User yêu cầu tiếp lesson; AI triển khai
PartA/B/C theo ủy quyền, không author-self proof/Understanding/human review.
Protocol29d5422trước diagnostic; source1aca4a4. Không đổi frozencontract,
M0/M1/metric/threshold, không khởi động lạiSUB/CF.

T08chứng minh slottedP-clip/conditionalJensen vàGM|S1<=S_clip. Chỉnh hai lỗi
hướng dẫn: initialmodeON bắt buộcslot0 nên exactthreshold=max(0,hD−12dt),
không iff q<hD cho mọimode; saturation_OFF áp meanqueues rỗng, khôngbusy.
Weightedidlecost cópacket·s, khác totalunusedcapacity(packet). Pathd/dh chỉ
idlecostdifferences; networklinearparts triệt tiêu khi chuyển cùngu.

Finiteenumeration512paths tái lậpsuppliedexample; maxoutsidecostdifference
1.11e−14packet·s. PartB48states trên3oldkeys/cả2paths:24/24outside cód−dh=0,
96/96per-actionJensenPASS;insideabs(d−dh)max3.757970725packet·s, gaperrorhai dấu.

PartC đủ50prespecifieddiscoverykeys(18A/16AB/16C),34.530743CPU-s,khôngnew
law/Bellman/fullregimeevaluation. Bound50/50khôngvi phạm cùngquadrature;
replayGM|S1max7.4476e−18pp. P_cliprange.9964763→1,35/50near1within1e−9.
SpearmanvớiGM|S1/absGamma=.775788/.762484chỉdescriptive,496/1225rankpairs
khôngtáchtheoCDFerrors. Giữ8rawflags;khôngchứngnhậntotalnumerics đãsolved.

Sau diagnostic bổ sungproof36d32c0: ngoàiClip, tổngbacklogcost không đổi theo
action vàc_sw0 nênDelta0. **S_clip=sigma** trongprimary;ratio1ở50/50làidentity,
khôngfinding/predictormới. Cậnchínhlàstakesboundđãcó,khôngtựnhậnchặt. Không
đổi cost/plant/refine đểcứupredictor,khôngkhóaH-cliphoặctạoalternativemới.
GiữP-cliplàm mỏneo giải thích/test; predictorheldout/null1NN/knockout chưa làm.

34targeted/930fulltestsPASS; source/history/ruleschecksPASS.0CF/sealedoutcomes,
SUBdùng9keys từ10đãpark,không66keys. D22nativeF/Vnull/G1/Understanding/L8giữ;
L4.8đượctiếp. [Report](../results/lessons/l4_7_v2/report.md),
[proof](theory/T08_clipping_anchor.md), [protocol](lessons/L4.7_v2_protocol.json).


### DL-120 — L4.8 scope/domain, empirical mapping chưa xác nhận (31/10/2026)

Người phụ trách: **Doan Van Tai**. Theo user“tiếp tục” sauL4.7, AIthực hiện
roadmaprealism/declareddomain,khôngcófulllesson4.8mớiđểchấmchecklist. Không
author-self/humanreview/UnderstandingPASS. GiữtheoremP-clip,khôngtuneclip
predictorhoặcfreezeH-clipthànhmagnitudehypothesis.

Workingnarrative:DC-inspiredone-shotmanagedaggregatesteering trênhaiqueue
equalcapacitytrongfrozenplant. Giữcontexta/bDL008/realismv1;DCchỉlànarrative
ưu tiên,khôngdeploymentvalidation. Physicaldomainvẫncontract;Bpostoverload
finiteh đượcphép,currentenginechỉsupportBpoststable. Khôngchọnhộp/heldoutmới.

Skillpaper-research,đọcprotocol/catalog26/logtrước;lookup3existingDOIs và
reread15PDFpages từZLK17/BAM10/NDT1,AI-T.0newsource/0download/0proposal,
catalog/Excel/authorlevels nguyênbyte. Sourcesupportcontext/motivation nhưng
khôngjointbacklogage/hold/inputmode/buffer/actuation.10Gb/sserver-ToR không
tựthànhcặpalternativeuplinks40/100Gb/s. Empiricalrangesnull/UNRESOLVED,không
IN/OUTmớihoặcđổithành0feasibleregimes. Khôngclaimlatestrepresentativeness.

Sourcead78946 chiếu597designkeys(497SV,90MV/SH,10SUBpark),khôngoutcomesmới:
physical/currentengine/lattice597/597. Illustrativeanchor10Gb/s,tau10ms:
managed1–1.75Gb/s,T.5–30ms,h10–160ms,backlogunit1.25MBfluidwork. Rate×r,
time×s,backlog×rs,cost×rs²;ratioinvariancekhôngempiricalvalidation. Giữtau
measurednull;khôngchọnanchorđểcứukếtquả. Miềnmin/maxkhônglàsamplingboxmới.

12new/33combinedrealism/942fulltestsPASS;source/oldlabel/freezerulechecksPASS.
0simulation/CF/sealedoutcomes,SUB/CFpark,D22nativeF/Vnull,G1/Understanding/L8
giữ. **Scopingcomplete;empiricaldomainunresolved**,khôngtựđóngtoànL4.8hoặc
Gate4. L4.9cóthểchuẩnbịmodel-conditionedprediction;applicationclaims cần
measurementbridge đúngschema,khôngchỉtheorem/saturationidentity.
[Report](../results/lessons/l4_8_v2/report.md),[domain](realism/declared_domain_l4_8.json),
[source review](realism/L4_8_source_review.md).

### DL-121 — L4.9(v2): H-L1 primary, dừng fit H-L2, freeze trước truth (31/10/2026)

Người phụ trách: **Doan Van Tai**. Tác giả chọn thresholds đã sửa, lưu nguyên
văn ở `results/lessons/l4_9_v2/author_choice.json`, commit834b4074 trước
predictor mới. T09 sửa pointwise O(1)→uniform h* và exact ties; không đổi
frozen plant hoặc nhận author-self proof. H-L1≤.5% trên≥90% finite panel;
không h*/exact finite zero. Giữ H-L2≥.7/MedAE giảm30%, bỏ H-L3.

Part B86/86:rho.549016,MedAE5.267210vs1NN1.517567pp;41rawflags giữ/no-flag45
vẫnthua.4meanprofilechecksdiff0. Tác giả chọn **H-L1 primary; H-L2 exploratory,
không fit thêm** sau PartB, trước truth; không sửa predictor hoặc thresholds.
20new/962fulltestsPASS90.36s; giữ first adapter error1FAIL/961PASS/empty attempt.

Planfaa4f848 trước12parameter-only predictions(2.309191CPU-s),0held-outM1.
N12freshkeys ratios320/640,levels6404/3204/6402,futurecap8CPUh,khôngđổiN/
mẫu số READY/refineđểcứu. Disclosure đủ SV FAIL/10SUB/L46–48/inputtable/PartB;
replay26slices24trends/2exceptions.3warmh16benchmarks complete; h32calibration
ratio106.67 SIGXCPU60.552639CPU-s, khôngcompletedrow/retry. **PartCpartial,
feasibilityUNRESOLVED/Gate4chưaGO**,khôngPhase5run. SUB/CFpark,D22native
DEFERRED,P0V10/L8/Understanding giữ; khôngnovelty/empiricalvalidation.
[Report](../results/lessons/l4_9_v2/report.md),[plan](design/analysis_plan_v1.md),
[lock](design/analysis_plan_v1.lock.json).


### DL-122 — Dọn repo, hợp nhất exploration và đính chính exposure (02/11/2026)

Người phụ trách: **Doan Van Tai**. AI thực hiện và chọn phương án kỹ thuật theo
ủy quyền trực tiếp trong chat: dọn repo, đưa exploration mới nhất vào main,
kiểm tra trước Phase 5 và dạy lesson đầu; kết quả/lesson in trong chat,
không tạo file lesson/report mới. Không ghi AI-work thành author-self hoặc
human review. Commit 6ffe8e84 của bản trả lời Claude không có trong local/
remote tại đầu lượt; không nhận đã audit được một tree không tồn tại.

Đã giữ 5 tag archive ngày 02/11 trước thay đổi; gộp mechanism-regime-v2
c1726c80 và p4-regions 8f382293. Archive lesson/code/result/tests lịch sử
không còn áp dụng; giữ source frozen, dependencies, guards, 597 raw native
nguồn và các mức refinement Phase 4. Không rewrite history/attribution.

**Exposure cross-branch được xác nhận:** 77 dòng wide có h/κ>160;
W0347 = P5_08: (lambdaA7,lambdaB8,kappa1/10,eta1/2,h32,c_sw0), level160/2.
Raw có G_S_M1=0, G_M_S1=6.2304028835861359273, Cref=38.427771391756293123:
S=0,0%Cref; M=16,21328184783235%Cref. Bản trả lời Claude nhầm M thành S,
nên suy luận đã dùng một suất FAIL H-L1 là sai. Git commit p4-regions
19:17:11+07 ngày31/10 đứng trước freeze faa4f848 21:38:13+07.
Không suy commit timestamp là bằng chứng tác giả/agent chọn panel đã đọc row.
Audit L4.9 chỉ bao phủ inventory/main thời điểm đó, bỏ sót nhánh song song.
Các câu 12 fresh/0 truth trong frozen artifacts giữ như lịch sử và bị đính
chính bởi record này; hash đúng không chứng minh panel hoàn toàn unseen.
Chỉ đọc thêm metadata của 76 dòng còn lại, không mở outcomes của chúng.

**Quyết định theo ủy quyền:** giữ toàn bộ freeze/panel/N12/threshold/budget;
không bỏ P5_08, thay điểm hay đổi mẫu số READY. Bài H-L1 giữ luật chấm gốc
nhưng nhãn evidence là validation có exposure một phần, không confirmation
độc lập chỉ dựa vào panel này; H-L2 vẫn exploratory/no-refit. Một kiểm mới
ở điều kiện thật sự chưa dùng cần prediction trước run riêng. Gate4 giữ
HOLD đến lesson preflight/feasibility; chưa chạy Phase5 hoặc miễn human
review ngầm. SUB66/CF270 park, R09/R10 sealed, D22 native deferred, G1 và
Understanding giữ. Master numbering DL103: P5 confirmation, P6 mechanism,
P7 independent validation, P8 practical relevance, P9 synthesis/novelty,
P10 paper; không đổi P7 thành paper như bản trả lời Claude.

Lesson4.10: kiểm P-clip/Jensen bằng helper 512 paths và teaching toy lan
truyền phân phối hữu hạn, kappa1/4,dt1/8, không MC và không native panel.
AI soạn lời giải/đáp án, không chứng nhận tác giả đã tự dẫn hay tự hiểu.
Chi tiết và lộ trình ngắn được in trong chat, không thêm framework/lesson files.


Bổ sung cùng phiên sau khi tác giả gửi bundle và Parts4.10.2/4.11:
- Bundle hợp lệ, đã import6ffe8e84 vào branch archive/claude-cleanup-2026-11-02
  để audit riêng, không merge đè provenance/errata. Bundle chỉ chứa một branch
  ref; không chứa5tag như lời mô tả. Tự giữ5tag archive của workspace trước dọn.
- Audit độc lập treeClaude:2614files,541testsPASS39.06s;16/16freezehash và
  guardL43_A1_SV/L44_A3/SUB_BOX/verify_preregPASS;597native sources byte khớp.
  src/P4_09/theory không khác trước dọn. Lỗi16.2% trong lời giải là nhầmM/S,
  không phải lỗi frozen engine hoặc bằng chứngH-L1FAIL.
- Bản hiện hành giữ thêm5test modules còn áp dụng (native budget continuation,
  candidate labels/preflight, population resume, recount và selected validation)
  cùng calibration/refinement corpora.587testsPASS38.58s trước analyzer guards.
  Lần dọn đầu6FAIL/581PASS do thiếuPartA rules/grid/calibration; trả lại đúng
  dependency, không sửa assertion để né lỗi. Targeted100PASS/1FAIL tiếp theo
  phát hiệnl3r_2_spec metadata; trả lại, test đóPASS. Không sửa test nội dung.
- Sau chuyển cache ra ngoài, read-onlyL49 replay:86 NN references/1231training
  rows và4mean-profilechecks khớp savedJSON, không ghi lại output/plots.
  SavedCSV replay khớp toàn bộP1–P5/C1–C3/X1–X3; giữ cả forecastFAIL.
  H1filterP>=30,S+M>=.5:693/0/0;82/162/9;521/0/1 theo ba vùngx.
- Hai analyzer exploration cũ có thể ghi đè CSV/score khi raw đã archive.
  Thêm kiểm raw thiếu/partial trước đọc cost hoặc ghi output; regression
  missing/partial/complete trên cảhai helpersPASS, CSV giữ byte. Không đổi
  metric/prediction/engine; raw-to-metric recomputation cần restoretag.
- Công thứcEQ2 của lesson4.11 khớp stationaryzero-flux trong continuous time
  stable0<mu-lambda<a:0.96/0.27/3.6 ở ba ví dụ, sai sốroundoff<=1.78e-15.
  Không rerun các mô phỏng được kể hoặc xác nhận bảngF thiếu implementation.
  CrossingPr_Y(E[Delta_hat|Y]<0)=.5 khácE[Delta_hat]=0; chưa kết luận error
  cancellation hoặc exactboundary từ exactmarginalmoments.
- 9ignorednativecaches2636796623bytes,7retiredleftoverfolders55963086bytes,
  ba worktrees vàbundle tác giả chuyển ra /home/vantai/state-model-regret-archive/2026-11-02/.
  Symlinkignored giữreplaylocal; không coi đây là giảm tương ứng tổngdisk.
  Câytracked sau dọn5609files/~52.5MB, trước31900/~256.9MB; không rewriteGit.


### DL-123 — L4.12: exposure A, local probe và scope Gate 4 (02/11/2026)

Người phụ trách: **Doan Van Tai**. AI chọn và thực hiện theo ủy quyền tác giả
trong chat; không phải author-self learning hoặc human review. Nội dung yêu cầu
là lesson4.12 tác giả gửi ngày02/11; giữ source/protocol/analysis plan frozen.

**Quyết định trước probe:**
1. Chọn exposureA: giữ N12 và verdict frozen, báo riêng P5_08 cùng số M/F/U
   và nhận xét phụ thuộc mang tính mô tả; không thêm verdictN11, thay point,
   threshold hoặc budget. Nhãn vẫn partial-exposure validation, không confirmation
   độc lập. Input lesson nhầm z16.2%: rawW0347 choS0%,M16.2133%; chưa biết
   nhãnP5_08 ở ba numericallevels đã khóa. Không mở76outcomes khác trước score.
2. Chọn chạy ở máy hiện tại của tác giả (phương ánB trong input), không remote
   Claude container hoặc gửi kết quả qua bundle. Engine deterministic, seed N/A.
3. Bỏ amplitude test trướcPhase5: profiles.py dùng cố địnhs*6; không đổi engine/
   contract. X1 có10 observedcrossings+5no-crossing, không14 measured errors.
4. P0-V10 vẫnOPEN trướcCF;L8OPEN trướcfinalnovelty;memoV9 vẫnchưa gửi, điều
   kiệnpre-A04 đãwaivedDL054, không tự phục hồi thànhgate mới. Không tạo bằng
   chứng người đọc thật hoặc Understanding. Lesson4.12 không cho truepanelcalls;
   Gate4 cuối cùng vẫn chờ runner/dryrunLesson5.1 và review/waiver được ghi rõ.

**Resource-only calibration follow-up đã khai trước call:** đúngCAL_L49_H32
parameters[7,6,3/10,1/2,32,0],level(640,4),ratio320/3<160,disjointN12/CF/sealed.
Chỉ1attempt,không automaticretry. Cap300CPU-s tổng nhóm /420wall-s;
1worker/1BLASthread, không outcome panel. Đây làfollow-upL4.12 riêng,không
sửa timing cap60/90 trong frozenL49protocol hoặc overwrite oldSIGXCPU.
Cache stationary+profiles mới trống tại
/home/vantai/state-model-regret-archive/2026-11-02/l4_12_calibration_cold_01/;
giữ cache và failed/partial nếu có, không xóa để cheattempt. Binarybuildcache
hệ thống có thể reuse: cold ở data cache, không nhận cold toàn môi trường.
Output timing/status/hash in chat và appendrecord này; không file lesson/report
mới, không công bố hoặc phân tích calibrationloss/contrasts.

Trước engineimport: kiểm16freezehash,verify_run ba run,verify_prereg, canonical
point disjointpanel/CF/sealed. Nativecall dùng nguyênengine.evaluate_level;
đoCPU gồm parentworker+descendants,walltime vàcache hash. No statistic/CI.
CPUfit chỉdùng savedmech-v2sobol4 timing16384rows,K160/ref2,haihosts8192/8192:
OLSlogCPU~1+logh+logkappa+loginverseminpostactionheadroom cho coefficients
h.7358058256,kappa.05775835067,headroom.04848658982,residualsd.48568266694;
exp(2sd)=2.641548594. Không gọi đây là đảm bảo hoặc95%predictioninterval.
Fit phụ thuộcresolution/hardware vàkhông được đọctruth/p_sw của76p4rows.
Con số105.3CPU-s ởcontainerClaude chỉ reviewer-reported,không nhận localPASS.


**Kết quả thực tế của đúng1attempt (sau commitf2123d89):**
- Nativeengine.evaluate_level đã return; wrapper sau call truy cập row['status']
  và FAIL KeyError. Sourcepopulation.evaluate không trảstatus/parameters;
  run.py/_job mới là nơi bổ sunghai trường đó. Không lỗi engine exception,
  khôngSIGXCPU,không hếtbudget; workerexit1 là lỗi post-callvalidation.
  Không rerun native,không ghi jobPASS hoặc có validatedresultrow/hash khi chưacó.
- Worker+descendantsCPU96.797796s;controllerCPU1.881762870s;
  totalCPU98.679562036s;wall97.16974229499829s;cap300CPU/420wall.
  Đây là thời gian toànworker,không có riêngnativecallCPU được serialized.
  Nativecomputefeasibility singlecall OBSERVED; validatedrow/arithmeticverdict
  NOT_VERIFIED; fullpanelcost vẫnINFERRED, không guaranteedCOMPLETES.
- Cache ngoàiGit giữ12files/14502995bytes,không đọc/calibreportcost contrasts:
  stationary2metadata/hash/source/certificatePASS;profiles2npzshaPASS,
  40arraysfinite/monotonicknotsPASS. Hai costprofileconstructCPU40.235170596s
  và54.686348524s. Không lưu row.json hoặc scientificresulthash vìwrapperfail;
  stdout/traceback/receipt đã inchat, numericreceipt ghi recordhiệncó này.
- Correctedwrapperschema kiểm bằng fakepopulationreturnPASS,0truecalls;
  phải đưa regressionstatus/parameters do caller gán vàoLesson5.1dryrun.
  Nativeengine/score/protocol/plan giữ byte, không sửa backend để hợp wrapper.
- Savedtimingfit choh16≈59.255353s theoobservedtotalh32;
  24h32calls+12h16calls≈3079.373723CPU-s=.855381590CPUh;
  xexp(2sd)≈8134.315320CPU-s=2.259532036CPUh. Đây chỉ là inference
  crossresolution/hardware,không95%interval hoặc bảo đảm khôngINCONCLUSIVE.
  Budget8h và stop rule gốc giữnguyên; calibration này không phải paneloutcome.
- 20targetedtestsPASS1.12s; bốnlabelcases bằng frozenstate_verdict:
  11M/1F→PASS;10M/1F/1U→INCONCLUSIVE;10M/2F→FAIL;11M/1U→PASS.
  Freeze16/16 vàrun/preregguards kiểmtrước callPASS. 0panel/CF/sealedcalls.

**Chốt quyết định đọc/gate theo ủy quyền:** không thêmP0-V10/L8/V9 làm
prerequisite mới cho việc chuẩn bị runner/fixed-panelvalidation cóexposure.
P0-V10 vẫnOPEN trướcCF, L8OPEN trướcfinalnovelty, V9waiver chỉscopeDL054;
không gán humanreviewPASS, author-self hoặc blanketwaiver cho các gate đó.
Phầnđo/choices củaL4.12 đã kết thúc với caveatwrapperFAIL công khai;
Gate4 giữHOLD tới runner+dryrunLesson5.1PASS, chưatruecallPhase5.
Không làm lạiprobe đểcứuPASS,không thêmamplitude/SUB/CF/newgrid.
NguồnP5_08state0% chỉoldlevel160/2,không tự gán nhãn ở3levelsplanned.


### DL-124 — L5.1: runner, positive control và khai báo trước Phase 5 (02/11/2026)

Người phụ trách: **Doan Van Tai**. AI soạn và chọn chi tiết theo ủy quyền
trong chat: “chỗ nào cần làm gì để tôi tự làm thì bạn đống vai trò là tác giả
là tôi tự ra quyết định luôn”. Không nhận tác giả đã tự viết, kín sách,
human review hoặc Understanding PASS. Scope hiện tại: hoàn tất cả3PartL5.1,
dừng ở Gate4; không chạy Lesson5.2 hoặc bất kỳ P5_xx truecall nào.

**Khai trước positive control (entry này cùng commit runner/tests):**
- Tạo đúngexperiments/P5_panel/__init__.py,run.py vàtests/test_p5_panel.py;
  không đổi frozenengine/plan/score/protocol.32targetedtestsPASS2.81s;
  fullsuite619PASS37.35s.16/16freezehash khớp.
- Chọn STRICT_NO_RETRY đúnganalysis_plan_v1§6. Không adopt đề xuất resume
  khi thiếu row hoặc rerun toànbatch sau lỗirunner. Native có thể đã tạo
  outcome trong memory/cache dù row chưa ghi (bài họcL4.12).
- B=28800CPU-s làcap tổng,không chấpnhận vượt thêm1call nhưbản nháp.
  Mộtworker/1BLASthread; percallcap1800CPU/3600wall; parentgiám sát cả
  processgroup và giới hạn thêm theo budgetcòn lại, chừa1CPU-s cho
  finalization. CPUbao gồm guards/controller,children,failedcalls,cache.
  Linuxsubreaper thuCPU children bịorphan khi worker chết; khôngledger/
  lockframework mới: resources trong từngrow vàcalls trongsummary.
- Chọn fullguards trongparent vàworker trướcmọitruecall:16hash,
  verify_run cảL43_A1_SV/L44_A3/SUB_BOX,verify_prereg,panel/CF/sealed,
  trackedtreeclean,runner/testscommitted. Panel phải có DLGateGO gắn
  codecommit+anchorreport. Outputexclusive đượcreserve trước nativecall;
  worker cần inheritedFD của parent,không chạy riêng đểné vòngđiều phối.
- Anchor qua đúnglaunch→worker→evaluate nhưpanel:1truecallP43_0379
  parameters[13/2,7,1/5,7/8,2,0],level640/4. Cachecold riêng tại
  /home/vantai/.cache/state-model-regret/phase5/anchor/, ngoàiGit và
  disjointpanel. Anchor không tính vào8CPUh panel.
- Kỳ vọng đã khai: replay10/10FIELDS(losses,cost_error,Cref,sáucontrasts,
  normalized_error) khớp đúng savedrow; khôngalgebra/same-routeBUG.
  Label3savedlevels:P43_0379DOES_NOT_MEET,z3.5566941650250357%,
  d.01707593689734002pp;P44_025MEETS,z0%,d2.8302924627120256e-8pp
  (khác0,không làm tròn thànhexactzero). AnchorFAIL→GateHOLD,khôngpanel.
- Sourcecode vàtests sẽđượccommit trướcanchor;SHA chính xác ghi trong
  anchorreport và đoạnGateGO sau. Chưa cópositivecontrolresult ởentrynày.
- R6 chỉdiagnostic,khôngcertifiedbound; sốâm giữnguyên. Thêm kiểm metric
  so với losses theođịnhnghĩa đểbắtfalsezero, khôngthêmmetric/threshold.
  Testboundary sửa coherentlosses+contrasts,không giảidentity khi testU.
- Nhãn/score dùng nguyênrow_readiness,d_normalized,state_verdict,
  model_verdict. Uthứ2→dừng;Fthứ2khôngdừng. Rescore chỉđọc dữliệu,
  kiểm codecommit,không engine/ghi đè. M/F/U mẫu số12;NOT_RUN táchriêng.

**Bảng đọc kết quả trước outcome:**
- H-L1PASS: chỉtạiít nhất11/12tọa độkhai trước,plantv1.3,a/mu.6,c_sw0,
  đúngM1,h/kappa320/640,statevalue<=.5%Cref;P5_08 cóexposure. Khôngnói
  all12,bằng0,hstaruniform,mọi cáchupdate theo thời gian,realism/novelty.
- H-L1FAIL: quy tắc>=90% khôngđứng trênpanel;mô tảít nhất2DNM theo
  luật numericalđãkhóa. Không nhậnđãbiếtcơchế hoặcstate luônquantrọng.
- INCONCLUSIVE: nêuU/budget/execution/BUG cụthể;không “gầnPASS”,không
  chạy thêmđểchốt. Rawcrossrouteflags báo riêng,không tựthêmBUGcriterion.
- H-L2 mọioutcome đềuexploratory,soSpearman/MedAE với1NN tại3levels,
  đủ12READY mới chấm;khôngrefit,nângnhãn hoặcgiấuoutcome khôngthuận.
- ExposureA: nhãnP5_08 vàM/F/U của11điểm khác làmô tả,khôngverdictN11.
- ForecastAI soạn theoủyquyền,khôngnhậnauthor-self: dựđoánH-L1PASS do
  discoveryS/Cref nhỏởh/kappa cao. RủirochínhlàINCONCLUSIVE doR1/width
  tạinhóm tải7/8 hoặc8/7,kappa1/20,h32;không đọcoutcome mới đểđổi dựđoán.

**Gate4 hiện tại: HOLD tới khi anchorPASS và declarationGO đượccommit.**
KhôngtạoPHASE_5.md/reportlesson mới;planinput vànội dung học ởchat.


**Kết quả positive control và chốt Gate4 — sau commit runner/tests `3331d16350b6b1a9f3fdf892b965e48ea442fc80`:**
- Lệnhđãchạy: `.venv/bin/python -m experiments.P5_panel.run anchor`.
  Đúng1nativecallP43_0379,640/4 qua cùnglaunch/worker/evaluate củapanel.
  Preflight trướcanchorPASS;preflightpanel khi chưa cóGateGO đã từchối
  GATE4_DECLARATION_REQUIRED trước engine,không tạoattemptpanel.
- Replay10/10nhóm trườngkhớp savedvalues,field_mismatch=[],replay_bugs=[],
  statusPASS. Worker+descendantsCPU11.555570s,wall11.731516614s;
  nativecallselfCPU9.226440s (không lấy số này làm toànbudget).
- Hai nhãn từ3savedlevels: P43_0379DOES_NOT_MEET,z3.5566941650250357%,
  d.01707593689734002pp;P44_025MEETS,z0%,d2.8302924627120256e-8pp.
  M tương ứng .1682020388572474% và13.701436692427485%,bắt lỗi đọc nhầmM/S.
- Raw `results/phase5/gate4_anchor/P43_0379_level_640_4.json` vàreport.json
  đượcgiữ. ReplaySHA256=0ff857da494027fb5d2a33fde4ee297bd5b111431afa842ca35fffd2234cc6a3.
  Cache ngoàiGit/home/vantai/.cache/state-model-regret/phase5/anchor:
  12files/6448424bytes;cachepanel vẫnchưatạo.0truecallsP5/CF/sealed,
  khôngmở76outcomes khác. CácP5IDs trongtests làfake discovery rows ởtmp.
- 32tests mớiPASS;619fullPASS37.35s,không testfailedattempt ởversioncuối.
  Giaiđoạnđầutrướcbổsungcoverage:24/611PASS,không nhận reviewer15/602
  là kết quảlocal. Frozen16hash vàsourcebytes vẫnnguyên.
- Root.gitignore đã có `results/**/native_cache`;cachemới ngoàiGit nên
  không thêm patterntrùng. Không tạoPHASE_5.md,reportlesson hayframeworkmới.

**Read-back AI soạn theoủyquyền,không phải artifact tácgiảtựviết:**
Tôi đoS=L01-L11 khi modelđúngM1,rồi chuẩn hóa bằngL11 tại main640/4.
Tôi giữ mẫu số12,kểcảU;thiếupanel thì INCONCLUSIVE,khôngfillmissingbằng0.
Tôi kiểm readiness trước,vùngbiên|z-.005|<=d sau,rồi mới MEETS/DNM.
11M1F và11M1U PASS;10M1F1U INCONCLUSIVE;10M2F FAIL.
Uthứ2 phải dừng,Fthứ2 khôngdừng vì còn dữliệu H-L2 vàbáocáo.
BUG,execution/resource hoặcbudget dừng,no retry;rescore từsavedrows
khác với chạy lạiengine. Positivecontrol kiểm đườngnối vàtrường dữliệu,
khôngchứngminh numerics ởpanel hoặcH-L1đúng. P5_08 luônbáoriêng;
khôngN11verdict,khôngclaimall12refreshbounds hoặcnovelty.

**Gate4: GO theoủyquyền cho đúngfixedpanel đãkhóa.** ScopeL5.1đãhoàn tất
kỹthuật;Understanding/L-self/humanreview/G1 không tựđổi. Dừng tạiđây,
khôngtựthực thiL5.2; cần yêu cầu tiếp của tácgiả. Lệnhfutureduynhất:
`.venv/bin/python -m experiments.P5_panel.run panel`.
Sourcecommittrướcanchor;commitrawanchor+DL124này phải trướctruepanelcall.

<!-- P5_GATE4
{
  "status": "GO",
  "policy": "STRICT_NO_RETRY",
  "runner_commit": "3331d16350b6b1a9f3fdf892b965e48ea442fc80",
  "call_cpu_cap": 1800,
  "call_wall_cap": 3600
}
-->

### DL-125 — Phase 5 L5.2: chạy panel một lần (fact, chưa diễn giải) (02/11/2026)

Người phụ trách: **Doan Van Tai**. Thực thi bằng AI theo yêu cầu tiếp tục
Lesson 5.2 của tác giả; không ghi nhận author-self/Understanding hoặc human review.

- Code đã chạy: `8a8644f1ddc872988dec135f79d73714f964230b`, chứa
  DL-124/Gate 4 GO và anchor PASS; local và GitHub cùng SHA trước run.
  Preflight PASS, tracked tree sạch, không có panel/summary/cache panel hoặc
  P5 worker cũ. Panel dùng cache cold riêng, một worker/1 BLAS thread.
- Đúng một lệnh `.venv/bin/python -m experiments.P5_panel.run panel`.
  Đủ 6 calls theo thứ tự P5_01 rồi P5_02, mỗi điểm 640/4 → 320/4 → 640/2;
  cả 6 status COMPLETED. Runner tự dừng `SECOND_U`, exit 0; không BUG,
  execution/resource failure hoặc terminal failure được ghi nhận.
- Raw data và summary đã commit ngay trước khi đọc/chấm kiểm độc lập:
  `5a2f0bafc788c95e0c4171ed6d95a6bc49cc43c3`, message
  `Phase 5 L5.2: frozen panel run once (raw rows and summary; no interpretation)`.
  Có 6 raw JSON rows; 2/12 điểm đã chấm, 10 NOT_RUN.
- Tổng CPU **360,523961130 giây = 0,100145545 CPU-giờ**, budget 28.800 giây.
  Child/descendant CPU của 6 calls: 330,525408 giây; phần còn lại
  controller/guards: 29,998553130 giây. Tổng wall của 6 calls là
  331,541969231 giây, không phải wall toàn phiên.
- H-L1 theo luật frozen: **INCONCLUSIVE**, reason `INCOMPLETE_OR_INVALID_PANEL`.
  Số đếm từ nhãn đã ghi: M/F/U = **0/0/2**; phép tính verdict độc lập khớp.
  Giữ mẫu số 12 và 10 NOT_RUN, không điền missing bằng 0 hoặc dùng N=2.
- P5_08: **NOT_RUN**. Trong 11 điểm còn lại: M/F/U = 0/0/2, 9 NOT_RUN;
  chỉ là số đếm mô tả theo exposure A, không có verdict N=11.
- H-L2 exploratory: **INCONCLUSIVE**, reason
  `NEED_COMPLETE_READY_PANEL_AND_THREE_LEVELS`; không chấm rho/MedAE
  trên subset và không fit lại.
- Kiểm sau data commit: `run rescore` → `RESCORE_MATCH`; `check_frozen()`
  PASS, **16/16 hash** nguyên. Source runner/tests giữ byte tại `3331d163`;
  không đổi engine, panel, levels, metric, threshold, prediction hoặc budget.
- Deviation so với DL-124: **không có**. `SECOND_U` là luật dừng đã khai;
  không dừng tay, retry/resume/refine hoặc tính P5_03…P5_12. Trong run chỉ
  theo dõi stdout trạng thái/CPU và process metadata, không mở raw rows/summary.
  Lỗi helper đọc-only trước launch và helper metadata sau data commit đã được
  sửa; các lệnh này không gọi native, tạo panel attempt hoặc đổi artifact.
- Đính chính input lesson: trạng thái Gate HOLD tại `271819f9` đã cũ;
  Gate GO thực tế ở commit chạy nêu trên. Không áp dụng đề xuất resume của
  draft vì DL-124 đã chọn `STRICT_NO_RETRY`. Resources lưu trong từng raw row
  và `summary.calls`; không có `ledger.jsonl` riêng, như đã khai ở L5.1.
- Forecast trước run trong DL-124 (AI soạn theo ủy quyền, không author-self):
  “dự đoán H-L1 PASS do discovery S/Cref nhỏ ở h/kappa cao”; rủi ro chính đã
  ghi là “INCONCLUSIVE do R1/width” tại nhóm tải/kappa/h nêu trong DL-124.
  Giữ nguyên forecast; chưa đối chiếu nguyên nhân U hoặc diễn giải kết quả.
- Output: `results/phase5/summary.json`, 3 raw rows trong mỗi thư mục
  `results/phase5/panel/P5_01/` và `results/phase5/panel/P5_02/`.
  Cache ngoài Git: `/home/vantai/.cache/state-model-regret/phase5/panel/`,
  48 files, 49.577.973 bytes. Không tạo report, CSV, plot hoặc log riêng.
- **L5.2 hoàn tất thực thi và kiểm chứng; dừng trước L5.3.** Chưa đọc z/d
  từng điểm để diễn giải, chưa quyết định Gate C/claim/prior. CF/SUB vẫn park,
  R09/R10 sealed; không mở 76 p4-regions outcomes khác. G1, D22 native
  DEFERRED, L8, realism và Understanding không tự nâng.


### DL-126 — Đóng v1 INCONCLUSIVE; một lần sửa thiết kế có khai báo (Phase 5 v1.1) (02/11/2026)

Người phụ trách: **Doan Van Tai**. AI soạn và quyết định chi tiết theo ủy quyền
trước đó của tác giả và yêu cầu mới “tiếp tục đi” kèm quy trình phương án B.
Không ghi đây là tác giả tự viết/đọc, human review hoặc Understanding PASS.

**Đóng v1.** H-L1 v1 = INCONCLUSIVE, SECOND_U tại P5_01/P5_02; DL-125 và
raw commit 5a2f0baf giữ nguyên. Không retry/refine/đổi verdict hoặc chạy tiếp v1.

**Diagnostic post-hoc, đã kiểm raw.** G_S|M1 numerical estimates = 0 ở cả
6 rows; refinement delta = 0, width ≤ 1,523846e-9 Cref, không phải proof
estimand thật bằng 0. Cost error L00/Cref tại main là 0,000474808567493 và
0,0184545735101 > 1/4000; P5_01 có Cref dt delta 0,00319552070563 > 1/400.
Raw readiness đúng như DL-125, v1 rescore MATCH. Sai số L00 khác khoảng
38,87 lần giữa hai điểm nhưng cả h/κ thay đổi; chưa xác nhận riêng cơ chế
aging hoặc quy tăng width cho h. Không chạy diagnostic native mới.

**Quyết định dùng một lần design revision.** Thực hiện B trong tài liệu tác
giả cung cấp, CREF_DELTA_GATES=False; lý do nêu trước mọi call mới. Amendment
`notes/design/phase5_v1_1_amendment.md` quy định acceptance theo estimand,
Cref gate report-only, N10=P5_03…P5_12, H-L1 PASS≥9 với U≤1; H-L2 vẫn
exploratory N10 và readiness theo G_M|S1. Không nói chỉ sửa code: acceptance,
Cref gate và N đều thay đổi. Các tolerances, threshold, levels, engine,
predictions, BUG/stop/no-retry giữ nguyên. Luật mới được test mở khóa cả
MEETS và DOES_NOT_MEET khi chỉ L00 nhiễu; test đối xứng không xóa post-hoc
selection hoặc chứng minh unbiased confirmation. Budget panel còn chính
xác 28.439,476038870 CPU-s, một budget chung; anchor riêng như DL-124.
Không v1.2, không tăng budget. Full master plan chưa có trong repo hiện hành;
“reformulation budget” ở đây là một lần sửa theo input tác giả, không tuyên
bố đã audit/adopt đầy đủ điều khoản master chưa cung cấp.

**Exposure.** Đã mở outcomes P5_01/P5_02 trong diagnostic: S estimates=0,
M tại main 4,512214533% và 4,531047968% Cref. Hai điểm chỉ mô tả trong
v1.1, không đếm lại. P5_03 chung cặp tải; P5_08 exposure A giữ nguyên.
76 p4-regions outcomes khác chưa mở. Evidence: validation sau một lần sửa
thiết kế có khai báo, exposure một phần; không independent confirmation.

**Forecast trước run (AI theo ủy quyền):** H-L1 v1.1 PASS, rủi ro INC do
contrast-specific width/refinement vẫn còn; H-L2 FAIL exploratory, dựa trên
magnitude errors ở discovery. Không dùng outcomes mới để đổi forecast.

**Kiểm code mẫu trước thực thi.** Rescore mẫu chỉ duyệt IDs trong summary,
chưa replay thứ tự calls/stop/resources/budget; sẽ tái dựng từ raw theo
protocol, dùng terminal failure receipt khi output chưa lưu. Bổ sung raw
anchor SHA guard và kiểm v1 artifacts nguyên byte. Không thêm framework.

**Gate v1.1: HOLD** tới test + positive control PASS và phần B commit.


**DL-126 phần B — positive control và Gate v1.1, trước panel.**
- Source/amendment commit A `6058b077a126063a06e4354d98012484fa39d944`. Trên máy tác giả: 31 tests v1.1
  PASS 5,22s; full suite **650 PASS 41,87s**. Trước commit A có một synthetic
  interruption test FAIL do floating subtraction tạo CPU âm cực nhỏ; sửa
  kế toán CPU, không sửa metric/tolerance, rồi 28/28 PASS trước khi bổ sung
  3 guard/descendant tests. Không nhận 11/630 reviewer-reported là local.
- CLI `P5_v11.run panel` khi chưa marker đã exit 1 với
  V11_GATE_DECLARATION_REQUIRED trước engine; không tạo attempt/cache panel.
- `.venv/bin/python -m experiments.P5_v11.run anchor`: **PASS**, đúng
  1 native call P43_0379,640/4 qua chính launch/worker/evaluate v1.1.
  Khớp 10/10 field groups, field_mismatch=[], replay_bugs=[].
  Child/descendant CPU 11.715562s, ngoài panel budget như amendment.
  P43_0379=DOES_NOT_MEET, P44_025=MEETS; P5_01/P5_02=MEETS theo v1.1,
  strict v1 vẫn UNRESOLVED. Hai điểm này chỉ đọc saved rows, không native mới.
- Report `results/phase5_v1_1/gate_anchor/report.json`; raw SHA256
  `069a06ccecd2fba670b51db27a8cb27dc44e81492ef8c7a09fe64371d4de95cb`. Amendment SHA256
  `147273a1ed2ff5d97dde206f636a36a7e7b937c69ecf0c86f5a8d35ed2947014`. Frozen v1 source/tests/data nguyên byte; 16 hashes vẫn đúng.
- **Gate v1.1: GO theo ủy quyền phương án B.** Sau commit phần B và push,
  đúng một lệnh `.venv/bin/python -m experiments.P5_v11.run panel`.
  Chỉ P5_03…P5_12, cold cache riêng, budget còn 28439.476038870 CPU-s,
  CREF_DELTA_GATES=False. No retry/resume/refine/v1.2; no live outcome reading.
  Chạy xong commit raw/summary trước đọc, rescore cả hai versions, DL-127 fact;
  dừng trước nội dung L5.3/closest-prior/Gate C. Không human review/G-level nâng.

<!-- P5_GATE_V11
{
  "status": "GO",
  "policy": "STRICT_NO_RETRY",
  "runner_commit": "6058b077a126063a06e4354d98012484fa39d944",
  "cref_delta_gates": false,
  "amendment_sha256": "147273a1ed2ff5d97dde206f636a36a7e7b937c69ecf0c86f5a8d35ed2947014"
}
-->


### DL-127 — Phase 5 v1.1: panel chạy một lần (fact, chưa diễn giải) (02/11/2026)

Người phụ trách: **Doan Van Tai**. Thực thi bằng AI theo ủy quyền phương án B;
không author-self/Understanding hoặc human review.

- Source/amendment commit A `6058b077a126063a06e4354d98012484fa39d944`.
  Gate GO/code đã chạy: `f14ef9c69af22466812fa3afe0f404b39048c5d4`, đã push trước launch.
  Preflight PASS, local/GitHub cùng SHA, tracked tree sạch, cold cache panel
  riêng chưa tồn tại, không P5 worker cũ. Panel P5_03…P5_12 theo đúng parameters.
- Lệnh duy nhất sau Gate GO: `.venv/bin/python -m experiments.P5_v11.run panel`.
  **30/30 calls COMPLETED**, đúng 10 IDs × (640/4 → 320/4 → 640/2);
  stop_reason=null, terminal_failure=null, exit 0. Không BUG hoặc resource/
  execution failure ghi nhận. Không retry/resume/refine/native diagnostic mới.
- Raw và summary được commit ngay trước đọc kết quả:
  `a609e79bdf6ba430d22e4ef08f1933736e6ad9b8`, message `Phase 5 v1.1: panel run once (raw rows and summary; no interpretation)`.
  30 raw JSON rows và 1 summary. Trong run chỉ đọc stdout tiến độ/CPU và
  process metadata, không mở rows/summary hoặc xem z.
- CPU v1.1 **1269.059224554 giây = 0.352516451 CPU-giờ**,
  budget 28439.476038870 CPU-s. Child/descendant CPU
  1168.571749s; controller/guards còn lại
  100.487475554s.
  Tổng wall riêng 30 calls 1174.683928491s.
  Tổng panel CPU v1+v1.1=1629.583185684s < 28.800s;
  anchor riêng như DL-126, không gộp child-only CPU làm toàn budget.
- **H-L1 v1.1 PASS**, M/F/U=**10/0/0**, đủ N10, 10/10 READY.
  Tính verdict độc lập bằng số đếm khớp state_verdict(planned=10).
  Theo luật v1 chặt, sensitivity mô tả: **3 MEETS / 0 DOES_NOT_MEET / 7 U**;
  không đổi verdict v1 hoặc đưa sensitivity thành một test mới.
- **P5_08 MEETS**; 9 điểm còn lại: 9/0/0, chỉ mô tả, không verdict N9.
  P5_01/P5_02 theo luật mới: MEETS/MEETS, đã thấy, chỉ mô tả, không đếm N10.
- **H-L2 v1.1 PASS exploratory**, đủ 10/10 READY riêng G_M|S1,
  cả 3 levels đạt ngưỡng frozen. Không refit predictor/1NN hoặc predictions.
  Metric MedAE đơn vị percentage points của %Cref, trên fixed panel N10;
  không population CI/p-value. Fact metric của cả predictor và baseline:

| K/ref | Spearman | Stationary MedAE (pp) | 1-NN MedAE (pp) | Theo ngưỡng |
|---|---:|---:|---:|---|
| 640/4 | 0.975627893311 | 1.143553011773 | 2.918238638929 | PASS |
| 320/4 | 0.975627893311 | 1.146219825008 | 2.915975242226 | PASS |
| 640/2 | 0.975627893311 | 1.163940597764 | 2.970591140141 | PASS |

- Tính lại H-L2 độc lập từ (L10−L11)/L11 của raw rows, median absolute
  errors và correlation của average ranks: khớp summary cả 3 levels
  (sai khác floating ≤1e-12 chỉ là kiểm replay, không tolerance thí nghiệm mới).
- `.venv/bin/python -m experiments.P5_v11.run rescore` → **RESCORE_MATCH**;
  `.venv/bin/python -m experiments.P5_panel.run rescore` → **RESCORE_MATCH**.
  check_frozen PASS **16/16 hash**; v1 source/tests/data giữ nguyên byte,
  v1 H-L1 vẫn **INCONCLUSIVE**. Source v1.1/amendment giữ byte từ commit A;
  rescore replay calls/identity/stop/resources/budget từ raw, không gọi engine.
- Giữ nguyên **4/30 rows** có raw validity_errors: negative_nonnegative_contrast
  G_SM và G_S_M1, mỗi loại ở 4 rows. Đây là flags report-only theo amendment;
  numerical negatives không clamp, BUG/readiness vẫn chấm theo luật đã khai.
  Không suy numerical zero hoặc small negative là exact population value.
- Forecast trước run (DL-126, AI theo ủy quyền) giữ nguyên: **H-L1 PASS,
  H-L2 FAIL exploratory**, rủi ro INC do width/refinement. Fact hiện tại
  H-L1 PASS/H-L2 PASS; chưa giải thích vì sao hoặc sửa forecast.
- Deviation vận hành so với amendment/DL-126: **không có**. Design revision
  từ v1 (acceptance, Cref gate, N10) là thay đổi post-hoc đã khai trước, không
  xóa bằng PASS hoặc test đối xứng. Evidence vẫn validation sau một lần sửa
  thiết kế có khai báo, exposure một phần; không independent confirmation.
- Output `results/phase5_v1_1/summary.json`, raw trong
  `results/phase5_v1_1/panel/P5_03/`…`P5_12/`; anchor trong `gate_anchor/`.
  Cache ngoài Git `/home/vantai/.cache/state-model-regret/phase5_v1_1/panel/`,
  204 files/197.419.208 bytes. Không tạo report, CSV, plot hoặc stdout log riêng;
  provenance/resources trong raw, summary và DL này.
- **Phương án B hoàn tất tới bước 7.** Chưa thực hiện nội dung L5.3,
  closest-prior check, claim hoặc Gate C. Không v1.2. CF/SUB vẫn park,
  R09/R10 sealed, 76 p4-regions outcomes khác chưa mở; D22/G1/L8/realism/
  Understanding không tự nâng.


### DL-128 — Phase 5 Gate C: NARROW (02/11/2026)

Người phụ trách: **Doan Van Tai**. Claim, Gate C và G-level do AI chốt theo
ủy quyền hiện có của tác giả (“đóng vai trò là tác giả…tự ra quyết định”) và
yêu cầu thực hiện L5.3. Đây là quyết định sau outcome; không ghi tác giả tự
chọn/tự viết, author-attested, L-self hoặc Understanding PASS. Chưa có xác
nhận tác giả tự đọc P13 Thm1/Prop5 trong lượt này. Thiết kế v1.1 vẫn mang
provenance AI theo ủy quyền của DL-126, không đổi thành lựa chọn tác giả trước run.

**Kết quả đọc:** closeout `notes/phases/PHASE_5_closeout.md` gộp cả report.
V1 INCONCLUSIVE/SECOND_U (2/12), v1.1 PASS10/0/0 (10/10). PASS v1.1 cần
cả hai thay đổi: sáu contrast+Cref gate3/0/7; chỉ bỏ Cref3/0/7; chỉ scope7/0/3;
cả hai10/0/0. Ba biến thể đầu mô phỏng U2 tại P5_04; không là các lần run mới.
Đã kiểm bỏ Cref bằng Fraction trên raw, không dựa reason string làm tròn.
S_est tuyệt đối [-0.002471699394,0] packet·s, |z_est|max0.006272935744%;
Cref4.123705271–39.402593852 packet·s. Numeric S nhỏ, không chỉ do mẫu số;
không suy mọi tải monotone hoặc true error được bound. P5_08MEETS,
9điểm khác9/0/0 chỉ mô tả; P5_01/02 không gộp vào N10.

H-L2 PASS exploratory ba levels; main rho0.975628, MedAE1.143553vs1NN2.918239pp.
Load-mean diagnostic rho0.962950 dùng chính truth: in-sample, không baseline
prospective. RatioMedAE x320=.726166, x640=.164582, all=.391864, bỏ08=.290328;
subset chỉ mô tả. Predictor cao hơn truth10/10; forecastH-L2FAIL giữ nguyên.

**Closest prior:** kiểm 3 Crossref DOI và targeted9pages của3PDF đã có,
SHA khớp catalog; AI-T, không L-self hoặc full reading. P13§2.1/tr272,
Eq2.4/2.7/tr275, Thm1/tr276, Prop4–5/tr282 là analog transient/stationary;
Lévy/continuous capacity/average objective khác correlated ON/OFF/binary
routing/cumulative regret, không transfer theorem hoặc rate. M00§3.4/PDF10,12
là repeated-dispatch herding, khác one-shot information value; P04§III-A/B,
tr166/168/170 giới hạn timescale wording, không đồng nhất holding time vớiκ.
T09§1–3 vẫn conditional mechanism, chưa chứng minh expansion/integrability.
Không tìm nguồn mới, không novelty/field-absence conclusion.

**Claim được chọn:** Trong plant v1.3, a/μ=.6,u1,c_sw0, action giữ suốt h,
model đúng M1, numerical state value đạt≤.5%Cref tại10tọa độP5_03…12,
h/κ320/640 theo acceptancev1.1; v1 chính thứcINC và PASS phụ thuộc cả hai
thay đổi. Cùng tọa độ, model gain khi stateoracle4.4096–17.5633%Cref là
simple effect. Đây là lượng hóa finite-panel phù hợp stationary/transient
intuition với analogP13 dưới giả định khác; chưa contribution/novelty được
xác nhận. Claim đầy đủ, exposure, negative estimates/d và giới hạn ở closeout.

**Đính chính lesson:** numerical0 không phải exact0; S=0 đòi policy cũ tối
ưu almost surely, kể cả ties, không buộc mọi state cùng một action. T09
khônguniformaction cũng chưa chứng minhS>0 mọi finiteh. P5_11 |z_est|=.006273pp
>d=.004033pp cho lower bound sai khác, không upper bound; “80lần” không là
certificate. Denominator-only change cho Δz=−zε/(1+ε), không chính xácεz.
Predictor dùng finite-h a_M0,h, không thuần hằngM∞. IdentityΓ=S|M1−G_S|M0
đúngmọiregime; nhỏS chỉ approximatecancellation. Không nhận interaction đã
validate toànpanel hoặc tự gán transition mọi effect≠0. Rootcause sốâm chưa xác nhận.

**Validity:** 7/7 mục execution/reporting/prior đã kiểm (chi tiết closeout);
không đồng nghĩa mathematical error certificate, human ownership hoặc novelty.
**Gate C: NARROW → bàn giao Phase6**, giữ câu claim hẹp vì v1INC, design
revision post-hoc/exposure, sensitivity và thiếu validation toànpanelΓ.
**PIVOT-watch** giữ: xem lại contribution nếu kiểm sau chỉ còn hệ quả lý
thuyết đơn giản; chưa kết luận prior ngụ ý toàn bộ con số hữu hạn.
**G-level: G1 giữ nguyên** vì realism chưa xác nhận, evidence exposure một
phần và boundary còn phù hợp kỳ vọng nội bộ. Không G2-candidate tự động.

**Kiểm local:** hai printers Part1/2 read-only chạy đúng;63Phase5testsPASS7.31s;
rescorev1/v1.1MATCH;16hash unchanged. Thêm helper read-only có SyntaxError
trước thực thi, đã sửa và chạy PASS; không tạo native call hoặc đổi dữ liệu.
Không full-suite rerun cho docs-only;650PASS41.87s là kết quả trước ởDL126.
Không code/results/plan/threshold changes. Literature log ghi3lookup,
4PDFcalls/9pages,0new/download; catalog/Excel/author progress giữ nguyên.

**Bàn giao:** transition discovery7/8x6.67–40,6.5/6x6.67–13.33;
G_S|M0/Γ nơi L00 đủ đo, hệ sốgap c/x post-hoc và numericsL00. G_S/Γ của
10rawv1.1nay exposed choPhase6, đã ghi register. Chưa tạoPHASE_6.md hoặc
chạy Phase6; khôngv1.2/CF/SUB/sealedR09R10/76p4outcomes. CloseoutAI-readback
không thay tácgiảtựviết/hiểu; D22native/L8/realism/Understanding giữ trạng thái.


### DL-129 — Phase 6 L6.1: chọn câu hỏi cơ chế, H1, H0 và can thiệp (02/11/2026)

Người phụ trách: **Doan Van Tai**. Quyết định do AI thực hiện theo ủy quyền
hiện có (“đóng vai trò là tác giả…tự ra quyết định”) và yêu cầu thực hiện
hai phần L6.1. Không ghi tác giả tự chọn/tự tính/đã hiểu, author-attested
hoặc human review. Gate C=NARROW/G1/PIVOT-watch từ DL-128 giữ nguyên.

**Câu hỏi được chọn — A:** Trong plant v1.3, một action giữ suốt h, M0 là
conditional-mean rollout và state oracle gồm backlog+mode: thêm switching
cost có làm dấu G_S=L00−L10 đổi như H1 dự đoán ở vùng truth/model có ranh
giới khác nhau, vượt sức dự đoán của một threshold null theo hình học tải?
Chỉ dùng điều kiện chưa dùng sau collision audit; P lớn tự nó chưa đủ.
Γ=S−G_S là identity mọi regime; S,M,Γ chỉ báo kèm, không evidence độc lập.

**H1 (ứng viên, chưa kiểm):** Khi horizon đủ dài cho phần lớn mass liên quan,
chi phí M0 bão hòa theo state trong khi truth giữ phần h·r. c_sw có thể làm
M0 với state cũ chuyển sang Stay trước M0 với state mới, còn truth chưa đổi;
điều đó tạo/dịch dải G_S>0 sang x<0 và có thể đảo dấu ở phía x>0. Điều kiện
thứ tự chuyển và độ lớn effect phải được kiểm bằng predictor ở L6.2, không
suy từ toy. Chọn đường **M0-only, 0 tham số empirical fit**, bổ sung đúng
posterior S0, không thay average-forecast bằng forecast tại mean state.
Stationary laws/mean profiles được dùng, finite-h M1 truth không được dùng
để dựng H1/panel. Không tự fallback sang calibration fit nếu đường này thất
bại: STOP/HOLD và ghi trước probe/panel. T09 vẫn cần stability/moment/
integrability; không uniform finite-h saturation trên unbounded support.

**H0 chính — H0a đã fit:** dự đoán G_S>0 iff
`0 < x < theta(u)`, **theta(u)=27/50−(7/100)u = 0.54−0.07u**;
ngoài dải dự đoán âm, ties tại hai ranh giới thuộc ngoài dải. Không phụ thuộc
c_sw/h/kappa: đây là hypothesis bất biến của **geometry-only null**, không
phải cấm đối thủ nhận metadata hoặc tuyên bố nó là null cost-aware mạnh nhất.
Hai bên có cùng quyền biết design và discovery; H0 dùng 2 hệ số fit, H1 dùng
0 hệ số empirical fit. Thắng H0a chỉ bác sự đủ của luật đó, không loại mọi
heuristic có c_sw hoặc nhận diện duy nhất causal mechanism.

Recipe fit H0, đủ để tái lập trước outcomes Phase6:
- Source `results/explore_mech/sobol4/metrics.csv` SHA256
  `37cf369bf87cb34fe65b3339806d1f8984f695eb929359181e62bcda718a4d1c`.
- Giữ P=(h/kappa)*abs(lambdaB−lambdaA)≥30, abs(G_S_pctC)≥0.5 và x!=0:
  **1448 rows = 164 positive +1284 negative**, từ16384 discovery rows.
  Giữ đúng filter trên, không lọc thêm theo arith/flags để tăng score;
  1043arithTrue/405False,
  368rows có raw flags. Các labels là exploratory estimates ở160/2,
  không được gọi ground truth đã certified hoặc independent validation.
- Grid duy nhất: alpha=j/100,j=0…100; beta=k/100,k=−50…50.
  Maximize số dấu đúng trên1448; tie chọn (abs(k),j,k) nhỏ nhất theo từ điển.
  Strict inequality0<x<alpha+beta*u. Fit cho alpha=.54,beta=−.07;
  **1418/1448=97.9281768%**, kiểm lại toàn bộ bằng Fraction khớp float count.
  Theta(1)=.47,theta(2)=.40; không dùng pilot c>0 để tối ưu alpha/beta.
- Đối chiếu số của lesson: hệ số .54−.08u cho1417/1448=97.8591160%;
  cả hai làm tròn97.9%, khác1row vì input không cho recipe optimizer.
  Dải cố định0<x<.5:1391/1448=96.0635359%.
- 1-NN chỉ mô tả: z-score population mean/std(ddof0) của
  (lambdaA,lambdaB,u,logkappa,logh) trên1448, Euclid, LOO theo row, ties ID:
  **1365/1448=94.2679558%**. Không nhận đã tái lập chính xác94.2% vì input
  không chốt feature scaling. Đây là diagnostic, không thêm đối thủ chính;
  0scalarfitparams không đồng nghĩa không model capacity (NN lưu labels).

**Đối thủ khác:** không chọn H0b ở phase này: thêm calibration/shift parameter
đổi sang câu hỏi mạnh hơn. Null “c_sw chỉ giảm |G_S|, không đổi dấu” chỉ báo
mô tả, không verdict thứ hai. Không gọi H0a công bằng với mọi cost-aware null.

**Can thiệp/phạm vi:** chọn c_sw, mức cụ thể và panel khóa ở L6.2. Chọn đúng
một SHOULD: **h-invariance**, ghép horizon trong cùng panel, báo phụ mô tả,
không thêm một lần run/verdict để thắng. Không knockout model-side. Không
D22, CF-v2/SUB, amplitude khác6, testc/x/P-collapse hoặc76p4outcomes.
Chọn A vì cho dự đoán can thiệp; B gần limit check chỉ mô tả; C kiểm prevalence
và CP machinery khác câu hỏi; D22 cần estimator khác và giữPhase8;
E c/x dạng đã kỳ vọng để sau; A++ code mới chưa cần cho claim hẹp.

**Mức claim mục tiêu:** đặc trưng dự đoán có can thiệp, có thể hỗ trợ cơ chế
“M0 mù horizon” **so với H0a này**, nếu vượt GateD; không chứng minh cơ chế
độc nhất, generic information-harm, novelty, realism hoặc RQ3.
**Budget chốt:** native Phase6 tổng≤14400CPU-s (4h), trong đó panel≤7200CPU-s
(2h); gồm probe/anchor và calibration nếu được duyệt riêng, guards/controller,
all descendants, failedcalls/cache creation. Một worker/1BLASthread. L6.2
phải đo và thực thi counters/caps trước call đầu tiên; không nới sau outcome.
No retry/resume/refine, **không có P6v1.1**. Không có cửa sổ hoặc probe không
đo được trong budget → STOP/HOLD, không thêm scan để cứu.

**Toy tính exact (relative to Stay, không Cref normalization):**

| c_sw | L11 | L01 | L00 | L10 | G_S | Gamma |
|---|---:|---:|---:|---:|---:|---:|
| 0 | −10 | −10 | −10 | −6 | −4 | +4 |
| 1 | −9 | −9 | 0 | −5.5 | +5.5 | −5.5 |
| 2 | −8 | −8 | 0 | −5 | +5 | −5 |
| 4 | −6 | −6 | 0 | 0 | 0 | 0 |

Bốn rows/assertions và identity khớp; tie chọnStay. Đây là illustration,
không simulation/native plant. c quá lớn có thể triệt cả effect.

**Bốn bậc / đính chính cách đọc:** x<0→G_S<0 là pattern, không identity;
G_S<0 và trueS≥0→Gamma>0 mới là hệ quả đại số. Exact accounting là weighted
regret difference E[|Delta_c|*(I_oldwrong−I_newwrong)] dưới joint law;
constant stake nhân chênh mismatch chỉ xấp xỉ. Mismatch không suy chính xác
từ marginal switch shares nếu truth chưa tập trung một action. f lồi chỉ cho
weak increasing differences; “iff signδ” còn cần strictness/guard stationary
sign, không lấy convexity đơn thuần làm proof. Shares1.000 làm tròn không
chứng minh tất cả states chọn giống nhau hoặc trueS exact0.

**Discovery đọc lại:** printer hslice chạy read-only. Tại x=−1/3,h/k160:
truth/M0old/M0new≈1/1/.626;
G_S=−6.05%Cref, accounting≈−6.04. Tại x=+1/3:≈.001/.947/.511,
G_S≈+9.36, accounting≈+8.08. M0new shares giữa58→160 đổi
+0.000116985669 (lambdaB6) và−0.000154161518 (lambdaB7): giống3digits,
**không bằng chính xác**; M0old hai dòng này không đổi trong CSV.
Trên5adaptive slices:325/329=98.7842% khiP≥30,508/538=94.4238% khiP≥10;
allP vớiabsGS≥.5,x!=0:602/781=77.0807%. Cùng event/nearby keys có thểlặp;
không coi các tỷ lệ này là prospective evidence cơ chế. Predictor accounting
ước stake từ M của cùng rows là in-sample, không prediction.

**Exposure pilot — sửa lỗi quan trọng của input:** đã đọc qua
`git show a7435e9:results/explore_v13/stage3/regimes.csv`, không restore file.
48rows,24pairs c1/4, một mứcK40/ref1, x∈[0,1.5],h/k≤26.6667,
**Pmax=40**, không phải mọi P<30. X3000–X3003 cóP40,c1/4,x1/1.5.
Inventory51records cost>0 chỉ49distinctkeys,48u>0 activekeys (pilot) và1u0
control key; không phải51active độc lập. Activekeys không cóx<0.
Vậy điều kiện “c>0,P≥30 chưa dùng” **sai**; L6.2 phải collision audit union
mọi inventory/exploration/probe, không chỉ đặt điểm mới dưới tên khác.
Ởc1:9+/1−/14deadband; c4:4+/0−/20deadband tại±.5pp. Có4/24raw sign
changes, **0** cặp đảo dấu vượt.5pp ở cả hai phía. Không xác nhận hay bácH1:
không có phía x<0, chỉ coarse labels, chưa kiểm điều kiện H1.
CSV historical SHA256 `3d4a7a648467f15987cdf69f88cefaa9a3441dd20e7d356e848d474a0a8dd624`.
76p4outcomes vẫn chưa mở; hslice/sobol4/5slices là old adaptive discovery.

**Prior và nguồn mới:** đọc lại note R02§5Example1,information_harm§1/3,
already_implied L2.8,T09§1–3 và CEH23§2/5.1/6.1/8: mức note-review,
không primary reread/L-self. Generic approximate-policy information harm đã
có prior; CEH23 trong26-source library đã hỗ trợ wording future uncertainty
→ nominal values, với assumptions khác plant; không áp bounds cho repo.
- #1 Veatch2001, DOI10.1109/9.940928: metadata checked, không full text;
  **hoãn PDF trong L6.1**, ưu tiên nếu cần trước claim cuối GateD.
- #2 Bozkurt2602.02814v1: official abstract-only, CE tại state estimate khác
  việc đơn giản đồng nhất với M0 mean-future; **không duyệt bổ sung PDF/note
  ởL6.1** vì wording đã có CEH23, chưa kiểmtheorem của nguồn mới.
- #3 chưa tên/DOI: **không duyệt** như một paper; không tự thêm nguồn trống.
Quyết định theoủyquyền: boundedpriorL6.1 dùng thư viện hiện có +metadata2ứng
viên, không download/note mới/catalog changes. Không nhận4searches củaClaude
là queries của phiên này, không field coverage hoặc novelty. Chi tiết searchlog.

**Forecast trước L6.2:** tác giả chưa gửi forecast/self-readback độc lập.
AI theoủyquyền dự đoán **H1_SUPPORTED là kịch bản ưu tiên nếu GateD-entry
thực sự GO**; rủi ro chính cửa sổ không tồn tại/effect bịc lớn triệt hoặc
L00notREADY. Không gán phần trăm giả để làm calibration; không nhận forecast
là tácgiảtựviết. Read-back trướcprinter đã thấy số từlesson nên khôngblind.

**Gate L6.1:** phần execution hoàn tất khi entry này commit; **0 native
Phase6 calls**, chưa có panel/runner/probe/predictions/freezev2 hoặcGateD-entryGO.
Ownership/Understanding vẫnOPEN. Chỉ bàn giao L6.2 PartA kiểm cửa sổ bằng
tham số trước probe; mọi labels/thresholds/panel/calibration phải chốt trước
truecalls tương ứng. Phase5 bytes/verdicts vàG1/R09R10/CF/SUB/D22 giữ nguyên.


### DL-130 — L6.2 Part A: predictor M0-only và cửa sổ bằng tham số (02/11/2026)

Người phụ trách **Doan Van Tai**. AI chốt theo ủy quyền; không tác giả tự
viết/hiểu/attest. Entry khởi tạo **trước mọi tính toán predictor/scan Part A**;
metadata-only đã đếm51base từ lưới bên dưới, chưa xem finite-h truth.

**Thay cách phát biểu cửa sổ:** g_old(Y) là phân phối forecast có điều kiện,
không phải một mean scalar duy nhất. Giữ H1 accounting củaDL129 nhưng chọn
điểm trực tiếp theo hiệu switch CDF, bỏ x*_M0 như tiêu chí bắt buộc. Đây là
làm rõ zero-fit predictor trước truth, không đổi H0a/estimand/engine hoặc
fit calibration. F(t)=Pr(g<t) là strict-left CDF (cần giữ atoms/ties), không
đồng nhất với standard Pr(g≤t). Certified gap bằng c; tie chọnStay.

**Choices khóa trước scan:** rho=1/4, Pmin=30, zmin=1%Cref; W1–W6 theo
lesson, W7/W8/W9 **bật**. minlambda≥6.5,max(lambda+u)<10,kappa∈[.1,.3],
h≤16, unequal loads. NhómDi x<0,stake<0,c>0,H1+,H0−,c≤rho*h*abs(s);
Dii0<x<theta(u),stake>0,c>0,H1−,H0+. W7 giữ dấu ở3c/4,5c/4;W8 cùng
basec0 H1=H0 (referencec0 có thể đã lộ, không dùng làm fresh panel).
Cần witness≥10D/≥5base,≤2cost/base,≥2/3Di và có ít nhất1Dii để giữ cả
hai hướng đã chọn. Chọn witnessD10 theo thứ tựbase/c cố định, round-robin
mỗi base1rồi2, ưu tiên allocation7Di/3Dii rồi8/2,9/1. Cần≥2A, một+/một−
nếu đủ pool. Witness chỉ chứng minh có cửa sổ, **chưa freeze panel**.

Lưới duy nhất: lambdaA{7,15/2},kappa{1/10,1/5},h{8,16},u{1,3/2},
x{−2/3,−1/2,−1/3,−1/4,1/6,1/4,1/3}; lambdaB=lambdaA+x*u,
lọcW1/W2 trước compute →51base (33negativex). Costgrid
{0,1/32,1/16,1/8,3/16,1/4,3/8,1/2,3/4,1}. K320/ref4; chỉ
replay expose H0015/H0143 ở160/2 choT2, khôngpredictor640/4.
Không mở rộng grid vòng này để cứu kết quả; không nới margins/fallback.

**Budget:** Part A cap≤1800CPU-s, nằm trong14400 củaPhase6, ngoài7200panel.
Tính controller+children/cache/failed computations, kể cả numeric tests và
đo firstbase. Test/verification CPU đo bằngtime; scan trừ priorcomputeCPU
và reserve trước khi chạy. Cache ngoàiGit,1worker/1BLASthread. ChạmcapSTOP.
Không finite-h M1 cost: cấm full evaluator/cost-profile get/true idle; cho
phép stationary laws,posterior,mean_idle và true aging củaS0 đúng contract.
Không cóprobe/panel/finite-h outcomes trongPartA,khôngsources mới/literature.

**Forecast trước compute — AI theoủyquyền, không tác giả tự dự đoán:**
1. Khả năng đủDi/cảwitness:70% chủ quanAI, không thống kê/calibration.
2. CDFcrossing c* có thể cùng scale nhưng không bằng abs(mean_gap);
   không kỳ vọng một scalar mean quyết định crossing.
3. |zH1| ởDi dự kiến nhỏ hơnDii do negative-tail mass.
4. h8→16: crossing thay đổi ít ở mass đãxả, không exact invariant toànstate.
5. Dự kiến3–10CPU-s/base trênmáy này, chưa đo. Không sửa forecast sau scan.

**Phạm vi claim:** zero-fit accounting với M0 numerical + stationary-action/
stake approximations A1/A2. Không chứng minh horizon-blindness là causal
mechanism; mẫu số làstationary approximation, khôngCref finite-h thật.
Convexorder/equalmeans là exact-law identity, quadrature là numerical estimate;
T3/variance checks không chứng nhận exact distribution hoặc A1/A2. Nếu tests
trượt chưa giải thích → BLOCKED; thiếucửa sổ STOP; chỉDii HOLD. G1 giữ.

**Trạng thái trước triển khai:** chưa test/scan, chưa PartB, chưaGateD-entryGO.
Kết quả và source SHA sẽ nối sau, commit entry này trước bất kỳ probe PartB.

**Kiểm tra và sửa implementation trước scan thành công:**
- Targeted lần1:16PASS/1FAIL,14.87CPU-s; T6 AST báo nhầm substring
  `population` trong package `R3R_08_population_numerics`. Sửa kiểm tên
  module/import/call thực sự; không mở quyền gọi truth. Lần2:17PASS,
  14.67CPU-s. Full suite tại d51f9dcd:667PASS,53.72CPU-s (56.43s pytest).
- T3 tại H0015/320/4: mean_new−.10838430076347272,mean_old−.10870702287920268,
  drift.0003227221157299648packet·s<.005. Varnew.07908737816645853,
  Varold.012674012045557827(packet·s)^2. Cold firstbase320/4:2.172391025
  và2.19065325CPU-s qua hai lần test; drift.00021201340275049663.
- Scan attempt01 tại d51f9dcd dừng EXECUTION_FAILURE trước ghi CSV:
  `dict(..., c=..., **prediction)` trùng keywordc. Summary gốc giữ tại
  `results/phase6/window_attempt01_failed/summary.json`; scanCPU5.085907069,
  priorCPUupper95, tổngupper100.085907069CPU-s. Không finite-h truecall.
  Sửa ghép row bằng update; thêm test synthetic fullCSV510rows. Targeted
  sau sửa:18PASS/14.57CPU-s. Đây là sửa bug IO trước truth, không đổi
  predictor/grid/margins hoặc retry native experiment; không cứu một verdict.

**Exposure ngoài ý muốn khi kiểm schema:** lệnhhead in dư dòngW0000/wide
  (a6,b6,u.5,k.03,h2,c0) vàS0000/short(a6,b6,u1,k.03,h.25,c0), gồm
  old outcome fields. Hai key ngoài W1 và grid đã khai báo trước đó; không
  dùng để chọn điểm hoặc sửaH1. Các lượt đọc CSV tiếp theo chỉ lấy design
  columns. Không mở76p4rows h/k>160/R09R10/CF/SUB. H0015/H0143 và hai
  L4.9 c0keys được dùng replay test vì đã lộ, không đưa thành fresh truth.

Full suite sau sửa IO:668PASS/55.71s pytest,53.40CPU-s (time wall56.29s).
Các numeric tests/full suite vàattempt01 có tổng CPU đo156.315907069s;
trước lượt scan sửa bug dành **priorCPUupper180s** để bao cả rounding,
guards và các thao tác kiểm phụ. Giữ tổngcap1800; không reset chi phí lỗi.

**Kết quả lượt scan050c173d — BLOCKED, không Part A PASS:**
Command thực tế:
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -B -m experiments.P6_band.window --spent-cpu-seconds 180`.
Worker dừng đúng mean guard tại B017:base(a7,b13/2,k1/5,u3/2,h16).
Meannew−1.3598211415040415,meanold−1.3680083682796684packet·s;
drift **.008187226775626888>.005**. Varnew11.64995116224382,
varold6.734093044974154(packet·s)^2. Không nới tau hay bỏ guard.
16base hoàn tất×10cost=160rows/510planned;17build đã hoàn tất gồm
base diagnosticfail,34base chưa bắt đầu. Field`bases_completed=17` của
receipt đếm builds, **không phải17base đầy đủ cost rows**. Không chạy tiếp.
`max_mean_drift=.0012212113460052798` là max16base đã xuất CSV,
không gồmB017; giá trịfail nằm riêng trong`diagnostic_failure`.

| Pool trên160rows partial | MUST | MUST+SHOULD W7/W8 | Số base sau SHOULD |
|---|---:|---:|---:|
| D(i) | 1 | 1 | 1 |
| D(ii) | 30 | 30 | 6 |
| A | 48 | 48 | — |

W9 chưa có witness10D/≥5base/≥2/3Di, dù có hai A khác dấu.
Đây không phảiHOLD_ONLY_DII vì đã có1Di, khôngSTOP_NO_WINDOW vì chưa đủ
grid, và khôngbằng chứng H1false/H1supported. Chỉ là predictor numerical
chưa vượt guard đã khai báo. H0 không thay đổi.

Hai ví dụ dự đoán, **không phải trueG_S**:
- B011C07:(7,6.5,.1,1.5,16,c.5),P80,stake−2.9292219363536525packet·s,
  Fnew.1816976441856727/Fold.12916926726639522,zH1+1.0324657830730326%Cref_H1,
  H1+/H0−. Cùng basec0z−7.72882089958; crossing chỉ khoanh(1/4,3/8),
  absmeannew.34010869968, không kết luận crossing bằng mean hoặc duy nhất.
- B004C04:(7,59/8,.1,1.5,8,c3/16),P30,stake+2.702129081389682,
  Fnew.2851124084700995/Fold.24641575961740436,zH1−1.0163958029979427%Cref_H1,
  H1−/H0+. Mẫu số cảhai làstationary approximation, khôngfinitehCref.

**Kiểm độc lập và diagnostic blocker:** inlineCSV audit tính lại exactH0,
physicalkey vớiη=u/2, W1–W8, group, strict sign và công thứcCDF/stake/z;
160rows/16bases,0duplicate/0W6collision trên union28158keys; sourceSHA khớp.
W3fail26/W4fail81/W7fail22, các W1/2/5/6/8 khôngfail; counts khớp receipt.
Tất cả16CSVbases đạt mean/variance checks. FullT2/T3tests vàCSV arithmetic
PASS không được dùng để ghi scanPASS.

SinglebaseB017 cùng320/4 tái lập đúng drift (CPUdiag2.36s đo bằngtime).
Mass freshA/B vàstaleA/B đều1, weightL1errors≈(2.33…3.39)e−13;
weighted profile errors fresh≈1e−9/stale≈5.11e−5 mỗi path. MeanA fresh
190.54886847626375→stale190.5394617907414; meanB−191.9086896177678→
−191.90747015902107. Freshcaps15556/54344,stalecaps17956/63464 vớiK320;
quadrature dùng representative bins, không exact integration. **Suy luận**:
discretization/integration có thể gây drift; các con số này chưa cô lập
rootcause hoặc loại trừ lỗi aging/posterior. Không gán chắc chắn làBUG nào,
không nângK/ref, không calibration/fit/đổi margins hoặc engine để cứu.
Chính phát biểu “M0 tính chính xác” trong lesson phải đọc như same semantic
functions, không exact numerical distribution trên mọi key; T2 chỉ kiểm2keys.

**Đối chiếu forecasts:** đủDi/witness chưa chấm do partialBLOCKED; giữ70%
forecast ban đầu. Ví dụB011 chỉ cho coarsecrossing, không scalar boundary.
MedianabszH1 củaDi1row=1.03246578%,Dii30rows=1.88196842% phù hợp hướng
forecast nhưng unequal/partial/designedpool, khôngpopulationevidence.
Không kết luận h-invariance từ partialgrid. Build+mean-diagnosticCPU/base
min/median/max1.640117805/2.105685852/3.160860894, thấp hơnforecast3–10;
scanoverall45.353949964CPU-s gồmcostpredictions/controller/children.

**Budget và artifacts:** scanreceipt totalupper225.353949964CPU-s gồm
priorupper180; thêmdiagnostic/guards/independentaudit sau scan, dành tổng
**upper240CPU-s** cho toànPartA closeout, thấp hơncap1800. Đây là bao bảo
thủ, không actualCPU240 hoặc reset chi phí; initialtestfailure/fullrerun/
attempt01 đều đã tính. No finite-h M1 calls trongpredictor/scan/diagnostic;
old fulltests vẫn có toyregressions như đãghi exposure.
- Source:`experiments/P6_band/{__init__,predictor,window}.py`,
  `tests/test_p6_predictor.py`; hashes trongsummary, sourcecommit050c173d.
- `results/phase6/window/scan.csv`,`summary.json`,`diagnostic_B017.json`.
- `results/phase6/window_attempt01_failed/summary.json` giữfailedattempt.
- Commands tests: `.venv/bin/python -B -m pytest -q -s -p no:cacheprovider tests/test_p6_predictor.py`
  (initialtargeted); saufix bỏ`-s`. Full: `.venv/bin/python -B -m pytest -q -p no:cacheprovider`.
  Đều cóOMP/OPENBLAS/MKL=1 và/usr/bin/time; full cuối668PASS55.71s.
  Diagnostic vàindependentaudit inline đã thực thi; output ghi ởchat/DL,
  không tạo report/log/plot riêng. Cache`~/.cache/state-model-regret/phase6/window/`ngoàiGit.
- Finalreadonlyguards:16freezehash/3nativepackages/preregPASS, P5v1 vàv11
  rescoreMATCH,1.89CPU-s. P5sources/tests/plans/data/thresholds không đổi.

**Quyết định theoủyquyền:** đóng phiên PartA tại **BLOCKED_MEAN_DIAGNOSTIC**;
không tự retry/expandgrid/đổi acceptance để cówitness. Bước tiếp theo vẫn là
kiểm correctness của mean-preserving forecast ởB017 trongPartA; chưa đủ
điều kiện probePartB/freezePartC/GateD-entry/L6.3. Không thêmlesson/framework.
G1/GateC=NARROW,ownership/UnderstandingOPEN,CF/SUBpark,R09R10sealed,
76highratiooutcomeschưađọc giữ nguyên. DL130 vàartifacts đượccommit trước
bất kỳ PartBprobe nào; khôngclaim H1valid,causalmechanism hoặcnovelty.


### DL-131 — L6.2 Part A: design revision của mean check, trước scan mới (02/11/2026)

Người phụ trách **Doan Van Tai**; choices doAI theoủyquyền, khôngauthor-self.
Input mới đề nghị lattice identity thay ngưỡng drift quadrature; số130CPU-s
trongcontainer khác là **nguồn báo**, chưa tái lập. Để bảo thủ cộng130 vào
upper240 cũ → **priorupper370CPU-s**, capPartA1800/P6total14400/panel7200
giữ nguyên. Không tiếp nhận kết luận “predictor không có bug” như chứng minh
toàn code/51base; cần phép kiểm thực tế và mutation.

**Khai trước triển khai/measurement:**
- R1: dùng OWN mean_side/stale_mean_side trên mọi queueindex trong finite
  nonzero-profile support + zero tail; bao negligible dropped mass và infinite
  law uncertainty. Đây là lattice-sum **có error bound**, không số thực exact.
  Gồm error fresh+stale profiles, stationary mass, dropped mass vàrounding;
  không chép nguyên bound bỏ fresherror hoặc cộng1e−9 tùy ý như input.
  Raw quadrature drift vẫn ghi trênmọibase; bỏ vai trò chặn củaτ.005 bằng
  designrevision công khai, không nângτ hoặc fit correction vàoH1.
- R2: kiểm B017 vàB011 tốt; đảo posterior phảifail, giữT2 exposedshares.
  Mean identity không phát hiện quênaging; không dùng nó thayT2 hoặc chứng
  nhận đủmọiaspect củapredictor. No M1 profiles/evaluator/finite-h truth.
- R3: đo B017 một lần trước quyết scope; capmeasurement90CPU-s. Nếu với
  t=CPU đo, estimate370+t+2*(54+4*t)+51*1.25*t+160+100+30≤1800 thì kiểm
  cả51base. Nếu không: chọn firstbase theo thứ tựDL130 trong mỗi ô(k,u,h)
  (8ô), cộngB011/B017 vàmọibase của witnessD/A cuối. Không dùng z/outcome
  để chọn strata. Chốt và commit scope sau measurement, trước scan mới.
- R4: chỉ nếu có witnessW9 tại320, kiểm chính witness10D+2A tại640/ref4;
  mỗi điểm phải giữ H1sign vàabsz≥1% ởcảhaiK. Không thay điểm bịfail để
  cứu witness; fail→HOLD_K_STABILITY. Không witness→khôngK640 vôích.
  Marginrho1/4,Pmin30,zmin1%,W7–9,10D/≥5base/≤2cbase/≥2/3Di/≥1Dii
  vàcontrols± giữ nhưDL130. Witness không phảifreezepanel/PartC.
- R5: scan51×10 từ đầu tại`results/phase6/window_revision01/`, khôngresume
  B017, không đụng3artifacts`results/phase6/window/` hoặcattempt01_failed.
  CSV ghi rawdrift,identity status/drift/bound; identityfail→BLOCKED.
  ChỉDii và0Di→HOLD_ONLY_DII; 0D→STOP_NO_WINDOW; cóD nhưng khôngđủW9→
  HOLD_INSUFFICIENT_DI_OR_DIVERSITY (không hạz để cứu). Khôngexpandgrid.
  Budgetstop/bug là trạng thái riêng, khôngwindowPASS. KhôngprobePartB,
  panelPartC/L6.3 hoặcGateD-entryGO tronglượt này.

**Scientific scope:** nếu bound-check vàmutations táilập input thì báo
drift quadrature làfalsealarm tạiđúng cácbase đãkiểm, khôngxóaDL130/
historicalBLOCKED vàkhôngclaim identity chứngminh H1/A1/A2/novelty.
G1/GateC=NARROW/UnderstandingOPEN,CF/SUBpark/R09R10sealed giữ nguyên.
Kết quả measurement/scope/tests/scan nối tiếp, không sửa choices hồi tố.

**Measurement và chốtR3 trước scan:** B017latticePASS,drift
−7.047367891754863e−7,bound.00010215740322989504packet·s; internalCPU
15.393267216,time user15.86+system.31=16.17CPU-s. Receipt tại
`results/phase6/identity_validation/measurement_B017.json`,0M1truecalls.
Theoformula đãkhai, estimateall51=1887.86019>1800 → chọnstratified-plus-final.
Firstbases metadata-only:B001,B002,B006,B011,B016,B017,B042. Có7ô khôngrỗng,
khôngphải8như ước đếm ởentryđầu: k.2/u1/h8 không cóbase thỏaW1/W2 trong
gridcốđịnh, không tạo điểm ngoài grid để lấp. B011/B017 đã nằm trong7.
Áp dụng rule mới cho toàngrid (rawdrift descriptive), nhưng identity certificate
chỉ khẳng định ở7sample vàmọibase thuộcwitnessD/A cuối; NOT_SAMPLED phải
ghi tườngminh. R3sampling không được mô tả thành51identityPASS.
Đo chưa chạyC>0, khôngfit/thresholdchange; chưamutations/B011/scanmới.

**Tests trước scanrevision:** targeted27PASS70.68s,time70.91CPU-s;
full677PASS114.87s,time112.09CPU-s. B017gooddrift−7.04736789175e−7,
bound.000102157403230; swappedposterior drift.102511084265094,
bound.000102157403230 → FAILđúngmutant. B011good−5.19589507933e−7,
bound.000102140086894; mutant+.020076604642795 → FAILđúngmutant.
Không đổiH1predictor/θ/grid/margins, originalT2 vẫnPASS≤1e−9.
Tests giữrawdrift>.005 vẫncho tiếp nếu identityPASS vàchặn trướcpredict
nếu identityFAIL; K640vetoz.99/signreverse vàcácnhánhHOLD/STOPPASS.
Historical4files vàH1predictor khớpe8d10927; measurementSHA khớpidentity.py.
Commandtests:OMP/OPENBLAS/MKL=1,/usr/bin/time,.venv/bin/python -B -m pytest
-q -s -p no:cacheprovider tests/test_p6_predictor.py; fullbỏ-s vàfilepath.

Priorupper trước scan mới **600CPU-s**:370cũ+measurement16.17+target70.91+
full112.09=569.17, còn30.83 đểbao guards/rounding/metadata. Không ghi600
làactualmeasured. Giữ cap1800; chưa native/probe/paneltruthPhase6.

**Kết quả scan revision01 tại6f6269ea:**
Command:`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -B -m experiments.P6_band.window --spent-cpu-seconds 600`.
Đủ51/51base,510/510rows, từB001khôngresume; khôngexception/budgetstop/
identityfailure. Status **HOLD_INSUFFICIENT_DI_OR_DIVERSITY** (exit2theorule,
khôngexecutionfailure). Finalwitness rỗng, controls± có nhưngchưađủW9.

| Pool | MUST W1–6 | MUST+W7/W8 | Bases sau W7/W8 |
|---|---:|---:|---:|
| D(i) | 3 | 3 | 2 |
| D(ii) | 70 | 43 | 10 |
| A | 272 | 270 | 48 |

N_D10 và≥2/3Di cầnít nhất7Di; poolchỉ3Di, nên không đủcửa sổtheo thiết
kế hiện tại, dùtổngD46 và12distinctbases. Không đổiN/rho/Pmin/zmin/W7–9.
Không gọiHOLD_ONLY_DII (có3Di), khôngH1false/true, khôngclaimkhôngcówindow
ởmọitham số. Chỉ kết luận **gridcốđịnh không cấp đủwitness yêu cầu**.

BaD(i) còn lại (mọisố làprediction, mẫu sốCref_H1stationary):
- B011C07:a7/b6.5/k.1/u1.5/h16/c1/2,z+1.0324657831%,H1+/H0−.
- B029C06:a7.5/b41/6/k.1/u1/h16/c3/8,z+1.0343365172%,H1+/H0−.
- B029C07:cùngB029,c1/2,z+1.0564035231%,H1+/H0−.
Không gọihai mức c củaB029 thành2base. TrướcW4,nhưng giữW1/2/3/5/6/7/8,
có27Dirow trongđó24absz<1%,median.7183390413%,max1.0564035231%.
Đây là mô tả finitegrid, không upperboundtoànplant hoặc effecttrueG_S.

**Identitychecks7/7PASS (drift,bound,packet·s):**
- B001:−7.14922633004e−8,2.55463204167e−5.
- B002:+1.37980381162e−7,2.53194063335e−5.
- B006:−1.89854657703e−6,1.02175645863e−4.
- B011:−5.19589507933e−7,1.02140086894e−4.
- B016:−1.96716436880e−6,1.02040967478e−4.
- B017:−7.04736789175e−7,1.02157403230e−4.
- B042:−1.64981686278e−7,2.55355289235e−5.
Maxabsdrift/bound=.0192781823. CSVidentity_checkedTrue đúng70rows từ7bases;
440rows còn lạiidentity_checkedFalse vàidentityfields trống: **NOT_SAMPLED**,
không51certificatesPASS. Khôngfinalwitness nên khôngcandidateidentity bổ
sung/K640:0calls, **R4chưađượcchạythật**, chỉunit-testvetoPASS. KhôngPartB.

Rawmean-drift vẫn nhưcũ, max.009820148462614142;11bases vượtτ.005:
B017/18/42/43/44/45/46/47/48/49/51. B017/B042trongmẫu mớiPASS dùvượtτ;
khôngsuy ra cácbasechưađượcsample đãđược kiểm lattice. Thayriêng gridtích
phân bằnglattice, giữcùngOWNbuilders, táilậpidentityvàdiệtmutants hỗtrợ
chẩnđoánfalsealarm củarawmeancheck tạicácbaseđãkiểm. Không chứngminh
mọihànhvi codeđúng, A1/A2đúng hoặc |G_S| finiteh đủvượtdeadband.
Không táilậpsweepK160/640/1280/2560 trongnguồnbáo; không nhận nó là sốlocal.

**Independent audit:** tínhlạiexactH0,group,keysη=u/2,W1–8,CDF/stake/z,
counts,identityfields/bounds,sourceSHAvàhistorySHA. 510uniquephysicalkeys,
0duplicates. Có7W6collisionsc0 đượcflagFalse vàloại; **0collision trongpool
đượcgiữ**. IDs B022C00/B025C00/B028C00/B030C00/B037C00/B041C00/B051C00,
chỉ đối chiếuparams, khôngđọcoldoutcomes. Union28158keys giữscopehiệncó.
160rows cũ khớp **toàn bộfield cũ nguyênstring**, không chỉtolerance;
predictor H1byte-identical e8d10927. OldBLOCKED3files+attempt01_failed
SHA/nguyênbytes giữ nguyên. AuditPASS1.09CPU-s;16frozenhash/3nativepackages/
prereg/P5bothrescoresMATCH2.08CPU-s. Không đổiP5source/tests/plan/results.

**Chi phí và artifact:** scancontroller+descendants240.34774032CPU-s;
receiptupper840.34774032 gồmpriorupper600. Dành **closeoutupper860CPU-s**
đểbao cả guards/audit/reporting nhỏ sau run, ≤cap1800. External130CPU-s
chỉ làreportedbudgetcharge; khôngclaimlocal đãđo. Có đầyđủfailed/blocked
historyvàtestcost, khôngresetcounter/khôngbùtrừcache đểđẹpbudget.
- `experiments/P6_band/identity.py` mới; `window.py`, `tests/test_p6_predictor.py`
  sửa; `predictor.py` giữbyte. SourceSHAs vàsourcecommit6f6269ea trongreceipt.
- Newscan `results/phase6/window_revision01/{scan.csv,summary.json}`.
- Measurement `results/phase6/identity_validation/measurement_B017.json`.
- Historical `results/phase6/window/` và`window_attempt01_failed/` nguyênvẹn.
- DL131/exposure/README/AGENTS cậpnhật; khôngreport/logfile/plot/frameworkmới.
  Tests/guard/audit outputđãinchat; meanlattice details lưu trongsummary.
  Cache`~/.cache/state-model-regret/phase6/window/`ngoàiGit.

**Quyết định theoủyquyền:** numericsBLOCKED cũ đượcgiải thích bằngrevision
meancheck; **giữ currentc_swdesign ởHOLD vìthiếuDi**. Dừngscanbranchvòngnày,
khôngtựmởrộnggrid/hạ1%/thayN hoặcchạyprobe đểcứu. R1/R2/R3/R5đãthực
hiện; R4cóimplementation/tests nhưngkhôngfinalcandidate đểchạy. Chưa đủ
điềukiện sangPartB/C/L6.3. Muốnthiếtkếcanthiệpkhác cầnrevisionkhoa học
riêng trước outcomes, khôngthêmlessonchỉđểvá. G1/GateC=NARROW,ownership/
UnderstandingOPEN,CF/SUBpark,R09R10sealed/76highratiooutcomesunread giữ.


### DL-132 — L6.2 Part A: mở rộng độ phủ c, khai trước sửa window.py (02/11/2026)

Người phụ trách **Doan Van Tai**; lựa chọn/forecast doAI theoủyquyền,
khôngauthor-self. User yêu cầu revision vềcoveragec, supersede quyếtđịnh
khôngexpand ởDL131 cho **một** lượt revision02; khôngđổi RQ/H1/H0/metric.
Entry này phải commit trước mọi sửa window.py và trước predictor ở c mới.

**Đối chiếu input chỉ từCSVrevision01:**33negative-xbases;17có signcross
quan sát giữa2mức c,16chưa thấy crossing≤1. Z-linear interpolation cho
c_hat/absmean∈[.789553422,1.157390338]; CDF-linear cho[.789032075,1.136862298].
Đó là interpolation estimate, không exactcrossing/CI/single-crossing theorem.
16khôngcross làright-censored, khôngchứngminh tấtcả cóc*>1 thayvìkhôngcross.
Tableinput(a)liệt kê15bases; B044/B045 nằmnhóm(b) nhưngđãcross ởđuôigrid,
nên17observedcross tổng cộng đúng. Không gọiheuristic b<1/4 là necessary
theorem: c*≈absmean chỉ làphỏng đoán; khôngthêm b-filter vàoW1–W9.
TrầnW3max=h|s|/4=5.554500057 tạiB046; c≤1 chưa phủthangM0/stake của
B017/B035–38/B044–45. Lýdocoveragehợp lý nhưng vẫn là adaptive design
dựa trênM0predictions đãthấy; chưaM1truth mới, khôngnhận là lựa chọnblind.

**Grid duy nhất mới:** giữ51base đúng thứtựDL130, giữ10cost cũ vàthêm
{5/4,3/2,7/4,2,5/2,3,7/2,4,5,6} →51×20=1020rows. Khôngchỉchọn8base
đẹp, khôngfit/hiệuchỉnh predictor. Giữrho1/4,Pmin30,zmin1%,W7–W9,
10D/≥5base/≤2cost-base/≥2/3Di/≥1Dii vàA±, cùngfixedround-robinwitness.
GiữOWNidentity.py (stratified-plus-final). Tái dùng7certificates từrevision01
nếu identity/predictor/source guards/ref/base/scope cònkhớp; khôngchạy lại
chúng vôích. Mọi finalwitnessbase chưa cócertificate phải tínhthêm.

**Invariant MUST trước finalchecks:** cả510oldrows phải khớp mọi oldfield
vớirevision01, không chỉfloat tolerance. ID của10cost cũ giữC00…C09,
costmớiC10…C19. CSV làscan-stage view: giữidentity_checked/bounds của7mẫu
vàK640fields cũ; finalidentity/K640proofs ghi **summary** riêng, khôngmutate
oldfields khiếninvariantgiảfail. DừngBLOCKED_REPLAY_INVARIANTnếu khác;
không lấy mismatchingrun làmPASS. Giữnguyênbytesmọi historyartifact.

**Sau scan:** chỉ cówitness320thỏaW9+A± mới kiểm cácfinalbases ởK640/ref4;
mọi chọnpoint phải giữsign vàabsz≥1% ởcả2K. Không thaypointfail bằngpoint
khác đểcứu. RuleK640vetoDL131giữ; nếu khôngđạt thìkhôngGO.

**Luật dừng:** <7Di hoặcW9/controls trượt saufullscan →
STOP_INSUFFICIENT_WINDOW, đóngnhánhc_swtronggridnày. K640veto→
HOLD_K_STABILITY nhưngdừng nhánh scan/thửlạilầnnày. Khôngrevisiongridthứba
hoặcretunewitness, trừkhi cólýdokhoa học độc lập mới đượckhai riêng.
Identityfail/replayfail/execution/budget làBLOCKED/RESOURCE, khôngH1false.
NếuSTOP chỉkếtluận grid1020khôngcấpđủwitness; khôngclaimplantuniversal,
H1“đúng” vềtrueG_S hoặcbiênđộfiniteh<1% khi chưađọctruth.

**Budget:** priorcloseoutupper860CPU-s, capPartA1800khôngreset/nới;
bao mọi tests/guards/cache/controller/children/K640/identity mới. Dùngtests
nhanh cho grid/reuse/replay vàmộtfullsuite phùhợp; CPUthật cộngtrướcscan.
Outputmới`results/phase6/window_revision02/{scan.csv,summary.json}`; không
resume hoặcghiđèrevision01/window/attempt01_failed. GiữP5frozenbytes.

**Forecast trướccompute mới — AI theoủyquyền,khôngauthorblindprediction:**
B035/B036 ưu tiên xuất hiệnDi z≈1–3%Cref_H1; B017/B044/B045 cóthể1–2%;
B037marginal, B018/B038 dễ thiếuW3/W7 room. Tin chủquan60% đủ≥7Di/W9
tại320, chưa calibration/statisticalprobability. B011/B029 dựkiến vẫnH1+
ở640, nhưngabsz≥1% mongmanh (oldz1.03–1.06), độtin60% giữthreshold.
Không sửaforecast khi thấy data. Existinginputforecast giữnguồnriêng,
khôngnhậnAI giải thích thành tácgiảtựhiểu.

**Giới hạn:** c/h|s| gầnW3cap làmA1rủi rohơn; điềuđó khôngtựxóaadaptive
selection. Cost1.5–2.8packet·s làrealismquestion, phầntrămchỉ stationary
denominator/case-specific chưaempiricalvalidation. Nếuđủwindow, PartB
phảiprobe ngoài panel đúngvùngpostload9/highload; **khôngchạyPartB/C/L6.3
tronglượt này**. G1/NARROW/UnderstandingOPEN/CF/SUBpark/R09R10sealed/
76highratiooutcomesunread giữ. Không thêmframework/lesson/report dư.

**Preflight trước revision02:** DL132commit`e3385598` trước sửa code.
10quicktestsPASS/25deselected2.05s (time1.97CPU-s); full685PASS116.17s
(time112.82CPU-s). Testskiểmexactcostgrid/oldIDs,certificateprovenance,
mọifieldreplay (kểcảmetadata),blockreplay trướcfinalchecks,khôngoverwrite
CSV khi thêm finalproofs; oldT2/identity/posteriormutants vẫnPASS.
Commands:OMP/OPENBLAS/MKL=1,/usr/bin/time,.venv/bin/python -B -m pytest
-q -p no:cacheprovider tests/test_p6_predictor.py -k 'expanded_cost or reuse or replay or final_checks_do_not or scan_serializes or window_stop'; fullbỏpath/-k.
SourceH1/identity và6historyfiles khớpbf972c9c. Trướcnewscan dành
**priorupper1000CPU-s** (860cũ+1.97+112.82=974.79,25.21reserveguards/
rounding/metadata), cap1800 giữ. 7certificate c-independent được táidùng,
khôngtựnhận là7lượt kiểm độc lập mới. Chưa tínhpredictor ởcost>1.

**Kết quả revision02 — STOP theo rule đã khai:**
Command thực tế:
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -B -m experiments.P6_band.window --spent-cpu-seconds 1000`.
Sourcecommit34ed25d0 trướccompute; đủ51/51base×20cost=1020rows,
K320/ref4,deterministic/khôngRNG. Status **STOP_INSUFFICIENT_WINDOW**,
exit2theoprotocol, khôngexception/budgetfailure/identityfailure. Lượt run
hoàn tất trước khi userinterrupt; khi “tiếp tục” chỉ audit/closeout, **khôngrerun**.

| Pool | Revision01 all | Revision02 MUST | Revision02 all | Base revision02 all |
|---|---:|---:|---:|---:|
| Di | 3 | 6 | 6 | 3 |
| Dii | 43 | 159 | 102 | 13 |
| A | 270 | 304 | 302 | 48 |

RawDi6 =B0111+B0292+B0353. Rule≤2cost/base cho tối đa **5Di** trong
witness; N_D10/≥2/3Di cần **7Di**. Vì vậy không đủW9, không được coi ba
costB035 làbaindependentbases. Dii nhiều khôngbù đượcDi-fraction đãkhóa.
ControlsA± vẫn có; chưa có finalwitness/panel, không K640/PartB/C/L6.3.

Ba Di mới đều ởB035 (a7.5,b6.5,k.1,u1.5,h16):
- c7/4:zH1+1.0273744363580057%Cref_H1, c/Cref_H1=9.6828462848%.
- c2:zH1+1.2968523496483868%, c/Cref_H1=10.9151250708%.
- c5/2:zH1+1.3078890257727096%, c/Cref_H1=13.2814836993%.
Mọi trường hợp H1+/H0−; đều làprediction/approxstationarynormalizer,
không trueG_S/Cref hoặc empiricalrealismvalidation. Ba Di cũ B011C07/
B029C06/C07 giữ nguyên nhưDL131. Không cónewbaseDikhác quaW3/W4/W7.

**Forecast review, khôngsửalạiforecast:** B035đúng cóDi1–3%; B036khôngđứng
(rawpositivepeak.9668484% tạic2.5 đãngoàiW3, không qua1% cảkhi bỏW3).
B017peak.4856823%c2 ngoàiW3; B018.3285699%c1.75ngoàiW3;
B037.6558515%c2/B038.4932133%c2đềungoàiW3; B044.5182507%c1.5trongW3
nhưngdưới1%; B045.3797530%c1.5ngoàiW3. Đây làrawpeaks trên20cost,
không phải certifiedcontinuousmax. Forecastđủ≥7Di/W9 khôngđứng.
B011/B029sign/threshold640 **NOT_EVALUATED**, khôngghiPASShayFAIL vì
không cówitness đểrun. Không gán statisticalcalibration cho60% chủquanAI.

**Invariant và independent audit:** receipt so510oldrows mọifieldpassedTrue,
0mismatch. Audit độc lập cũng so nguyênstringmọifieldcủa510oldrows; tính
lạiexactH0/group/η=u/2/physicalkeys,W1–W8,CDF-stake-z,counts vàidentity
metadata trên1020rows. 51base đủ20cost/base,1020uniqueIDs/physicalkeys,
0duplicate. 7W6collisionsc0flagFalse vàloại, **0acceptedcollision**;
union28158keys. Khôngđọcoldoutcomes đểchọnpoints. Samplecertificates và
SHA của identity/H1 khớp revision01;7certificates táidùng,140CSVrowsđượcgắncheck
do7base×20cost, không140checks hoặc51identityPASS. 880rowsnonsampled
ghiFalse/trống; nofinalidentity bổsung. K640_checks=[]; CSV K640fields
giữtrống, đúngscanstageinvariant.
6historicalfilesSHA/nguyênbyteskhớpbf972c9c. H1predictor/identity code
giữbyte;source/window/tests khớp34ed25d0. Frozen16hash/3nativepackages/
prereg/P5v1 vàv11rescoreMATCH. Audit1.50CPU-s,guards2.50CPU-s đo bằngtime;
khôngchạy lại685tests vìsourcekhôngđổi saufullPASS.

**Budget/artifacts:** controller+descendants **158.699150855CPU-s**,
receiptupper **1158.699150855CPU-s** gồmpriorupper1000; dành
**closeoutupper1180CPU-s** bao postrunchecks/ghi kết quả, dướicap1800.
Upper làbao bảo thủ,khôngactualCPU1158.7/1180; chi phícũ/test/failures và
externalreported130đãtínhmột lần,khôngreset. Cachecũđượcreuse cóprovenance.
Source sửa:`experiments/P6_band/window.py`,`tests/test_p6_predictor.py`;
configgrid/thresholds nằmtrongwindow.py vàruntime summary. Outputmới:
`results/phase6/window_revision02/scan.csv`,`summary.json`. Cập nhậtDL132,
README/AGENTS/exposureregister; không tạo logfile/reportfile/plot/configfile
riêng. Consolelogs/test output đãinchat; summary lưumetrics/config/sourceSHA.

**History thật:** IOattempt01EXECUTION_FAILURE→windowmeanBLOCKED→
revision01HOLD→revision02STOP; mọiartifactcũ giữnguyên, khôngrewritelịch sử.
**Quyết định theoủyquyền:** đóngnhánhc_sw/window hiện tại ởSTOP nhưDL132,
khôngthirdgrid/retunewitness/hạz_min1% hoặcđổiN đểcứu. Mởc đến6 tăngDi
3→6 nhưngkhông giải quyếtđượcW9; khôngcoi nhậnđịnh “chủyếudogrid” đãđược
chứngminh. Chỉkếtluận grid51×20 khôngđủwitness theo marginsđãkhóa; không
claim toànplantkhônghiệuứng/H1false/trueG_Sđãđượckiểm. PartB/C/L6.3
không mở. Cầnmộtdesignrevisionkhoa học riêng nếuđổi kiểmđịnhcơchế,
khôngtựthêmlessonframework. G1/GateC=NARROW/UnderstandingOPEN,
CF/SUBpark/R09R10sealed/76highratiooutcomesunread giữ nguyên.


### DL-133 — L6.2 Part A′: cửa sổ D(ii), khai trước code và kiểm số (03/11/2026)

Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu thực hiện lesson và ủy
quyền soạn, lựa chọn, dự đoán và triển khai D1–D6 trong phiên ngày 03/11.
Đây là quyết định triển khai theo ủy quyền; không phải bản xác nhận tác giả
đã tự viết, tự đọc hoặc vượt bài kiểm Understanding. Ownership/Understanding
giữ OPEN. Attribution và những xác nhận lịch sử được giữ nguyên.

**Bối cảnh và lý do sửa.** DL-132 đóng grid 51 × 20 ở
STOP_INSUFFICIENT_WINDOW: sáu dòng D(i) trên ba base chỉ cho tối đa năm
điểm khi áp dụng giới hạn hai cost/base, trong khi W9 cần bảy. D(ii) có
102 dòng trên 13 base qua W1–W8. Lượt này là sửa phạm vi kiểm định, không
chạy lại scan revision02 hoặc đổi predictor để cứu kết quả D(i).

Lý do ưu tiên D(i) để tránh pilot không đủ cơ sở từ metadata exposure:
inventory v3 có 48 physical keys active với c>0; sáu keys trong
0<x<27/50−(7/100)u đều có P thuộc {40/3,4,4/3}, dưới P_min=30.
Bốn keys P=40 nằm tại x thuộc {1,3/2}, ngoài dải đó. Không có pilot key
đồng thời thuộc dải D(ii) và P≥30. Đây là kiểm design metadata, không
phải đọc thêm truth để chọn điểm. Tuy vậy luật mới đã được chọn sau khi
xem predictor scan và đề xuất 13 ứng viên, nên phải công khai adaptive
selection; không gọi là lựa chọn blind hoặc bằng chứng prospective đã có.

**Giải thích B015 trong năm câu.** Ở c=0, stationary approximation cho
stake +7.681064 packet·s và giả định A1 dự đoán Stay, còn mean gap M0 chỉ
khoảng −0.170012 packet·s. M0 cũ Switch với share 0.821702, nhiều hơn
M0 mới 0.537967, nên accounting dự đoán state mới giúp +10.317115%Cref_H1.
Khi thêm c=1/4, hai shares giảm xuống 0.166562 và 0.241343, nên phía mới
còn Switch nhiều hơn và accounting đổi sang −2.807679%Cref_H1.
Phân phối forecast cũ có variance nhỏ hơn ở base này, nhưng variance hoặc
mean riêng lẻ không xác định vị trí giao CDF; phải giữ strict gap+c<0.
Đây là câu chuyện của predictor dưới A1/A2, chưa đo finite-h truth và chưa
chứng minh state mới thật sự gây hại.

**Sáu quyết định khóa trước code và compute mới.**

1. Bỏ tỷ lệ ít nhất 2/3 D(i) trong W9 cho phạm vi mới; giữ nguyên rho=1/4,
   P_min=30, z_min=1%Cref_H1, theta(u), W1–W8, ref=4 và code H1/identity.
   P≥30 là design restriction, không phải certificate của A1.
2. D(ii) là nhóm verdict chính. D(i) chỉ báo prediction: trên 627 dòng
   negative-x/c>0 đã lưu, đỉnh dương là +1.307889%Cref_H1 tại B035C14,
   c=5/2. Đây là max trên grid, không upper bound continuous/toàn plant;
   bỏ vế claim kiểm dải giúp dịch sang x<0.
3. Lấy một cost trên mỗi base và lấy tất cả 13 base có D(ii) qua W1–W8.
   Giữ ít nhất 10 điểm từ ít nhất 5 base sau veto; không coi các base chỉ
   khác h là independent replicates. Các cặp B004/B014, B005/B015 và
   B027/B040 chỉ hỗ trợ mô tả h-invariance đã chọn, không verdict mới.
4. Chọn c có |z_K320| lớn nhất trong pool hợp lệ của base; hòa lấy c nhỏ
   hơn bằng Fraction. Danh sách cố định: B004C07, B005C06, B010C02,
   B013C07, B014C06, B015C06, B019C12, B020C11, B027C12, B034C05,
   B039C14, B040C12, B050C19. Twin là C00 của từng base; A− là B001C00.
   B050 có c*=6 tại mép grid; không ngoại suy vị trí đỉnh liên tục.
5. Tính lattice identity mới cho cả 14 base (kể cả B001 đã có certificate,
   ghi rõ đây là kiểm lại). Tính predictor K640/ref4 cho đúng 27 members:
   D cần cùng dấu âm và |z|≥1% ở cả K320/K640; twin cần giữ dấu dương;
   A− cần giữ dấu âm và |z|≥1% ở cả hai K. Chỉ dùng D khi chính nó và twin
   qua; loại điểm trượt, không thay cost/base khác. Identity lỗi bất kỳ
   base nào → BLOCKED_EXACT_IDENTITY. PASS cần ≥10 D/≥5 base và A− qua;
   thiếu → HOLD_K_STABILITY. Missing/nonfinite check không được coi PASS.
6. Đây là revision cuối của cửa sổ c_sw. HOLD đóng nhánh để review PIVOT;
   không revision04, calibration fallback hoặc retune. BLOCKED/exception
   giữ attempt và dừng, không tự chạy lại. PASS chỉ cho phép chuẩn bị
   lesson Part B sau, không tự chạy Part B/C/L6.3 hoặc mở Gate D-entry.

**Công khai và đính chính lesson.** Truth c>0 đã có ở pilot lịch sử;
đúng hơn là chưa có finite-h M1 truth mới của 27 keys được chọn. Read-only
collision audit của lượt chuẩn bị cho 0 va chạm trên union 28.158 keys.
Chọn theo predictor không đồng nghĩa mọi adaptive-selection risk biến mất,
và winner's curse không bảo đảm chỉ làm giảm power. Kiểm K640 chỉ xác
nhận tiêu chí ổn định này, không phải proof hội tụ, A1/A2 hoặc causality.
PHASE_6 đầy đủ được đề cập trong tài liệu ngoài không có ở repo hiện hành;
không nhận đã đối chiếu §9 của văn bản đó. Main RQ giữ nguyên theo README.

**Dự đoán trước K640, được soạn theo ủy quyền.** Dự đoán 12/13 D giữ tiêu
chí; B013 có rủi ro nhất vì |z_K320|≈1.0593%, tiếp theo là B039/B019/B010.
Dự đoán cả 14 lattice identity qua vì cùng builders/laws đã qua các mẫu cũ,
nhưng đây chưa phải kiểm thực tế ở 13 D base. Không có cơ sở chọn một chiều
chung cho |z_K640|−|z_K320| vì quadrature indicator có thể dịch hai phía.
Cho truth tương lai, dự đoán định tính khoảng 10/13 ứng viên sẽ có G_S<0;
state đuôi có thể làm A1/A2 trượt, không gán xác suất hoặc lấy forecast này
làm threshold/verdict. Giữ nguyên cả bốn dự đoán sau khi thấy K640.

**Budget và thực thi.** Giữ tổng Phase6 14.400 CPU-s và panel subset
7.200 CPU-s, không reset chi phí cũ. Upper closeout trước là 1.180 CPU-s;
dành upper 20 CPU-s cho đọc/audit/preflight của phiên này trước tests.
Theo D6 của lesson mới, riêng tính parameter-only Part A′ không bị kill
bởi cap 1.800 CPU-s cũ; ghi actual CPU gồm tests/controller/descendants và
báo tổng upper, không mô tả upper là actual. Tổng cap Phase6 vẫn ràng buộc.
Không nới budget hoặc retry theo kết quả. Một worker, một BLAS thread.

Commit entry này trước khi tạo hai file mới select_dii.py/test_p6_select.py.
Targeted synthetic tests rồi một full suite trước commit code; tests không
chạy numerics Part A′ thật. Sau đó chạy đúng một lượt identity/K640 có
guards chặn finite-h truth. Reserve output trước call, giữ partial/failure
nếu có; commit raw candidates.csv/summary.json trước diễn giải. Không tạo
framework, report, plot hoặc config mới; chỉ cập nhật DL/exposure/pointers
cần thiết sau kết quả. H1, identity, window cũ và Phase5 frozen bytes giữ
nguyên. G1, Gate C=NARROW, D22 deferred, CF/SUB park, R09/R10 sealed,
76 high-ratio outcomes chưa mở và các xác nhận còn OPEN giữ nguyên.

**Điều chỉnh tương thích trước compute.** Full suite trên hai file mới đã
qua 709 tests (125.51 s). Khi rà guard ở window.py, phát hiện allowlist
certificate cũ sẽ từ chối cả module select_dii.py sau khi nó được commit,
mặc dù không có dependency tính số nào của certificate thay đổi. Cho phép
thêm đúng đường dẫn độc lập này trong allowlist; mọi thay đổi khác ở src/
experiments vẫn bị từ chối. Điều này thay thế yêu cầu giữ byte window.py
trong đoạn thực thi phía trên, chỉ cho đúng một thay đổi guard, không đổi
bases, costs, flags, witness, builder hay bất kỳ giá trị dự đoán nào.
Runner mới kiểm window.py khớp chính xác bản 34ed25d0 với một thay thế
allowlist đó; ghi SHA cũ/mới riêng. Predictor, identity, test cũ và sáu
artifact lịch sử vẫn phải khớp byte. Không sửa hash hoặc receipt lịch sử.
Thêm test cho allowlist và mutation ngoài dependency để không nới guard
chung. Chạy targeted sau thay đổi này; không lặp full numerics không cần
thiết khi chỉ allowlist thay đổi. Đây là sửa tương thích trước outcome,
không thay tiêu chí readiness hoặc chạy lại scan.

**Preflight trước lượt tính thật.** Targeted ban đầu 23/23 PASS (0.43 s,
0.73 CPU-s); thêm kiểm nonfinite/partial output rồi 24/24 PASS (0.48 s,
0.71 CPU-s). Full suite: 709 PASS trong 125.51 s, 122.24 CPU-s. Sau thay
đổi allowlist nói trên và thêm test mutation của guard: 52 PASS, 8 numeric
regressions deselected trong 1.26 s, 1.34 CPU-s. Tám regressions này đã
chạy trong full suite; không gọi lượt targeted cuối là full suite 710 tests.
Các tests mới dùng synthetic numerics, không chạy 14 identity/K640 thật.
Không có test failure trong các lượt này. Diff check PASS.

Commands thực tế: env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider
tests/test_p6_select.py; full suite bỏ filepath. Lượt targeted cuối dùng
cả test_p6_select.py và test_p6_predictor.py với -k loại T1, T2,
quadrature_mean, cold_first và lattice_identity_detects. Mỗi lượt có
/usr/bin/time để đo user+system CPU, tính cả descendants.

Tổng tests đo được 125.02 CPU-s. Prior upper 1.180 + preflight reserve 20
+ tests 125.02 = 1.325,02 CPU-s; dùng **prior upper 1.330 CPU-s** trước
run để bao thêm các guards/metadata. Không reset chi phí hay trừ cache.
Command run khóa: env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1 /usr/bin/time .venv/bin/python -B -m
experiments.P6_band.select_dii --spent-cpu-seconds 1330. Output reserve
trước call và source phải đã commit. Không identity/K640 thật hoặc probe
Part B nào đã chạy tại thời điểm entry preflight này.

**Kết quả duy nhất — Part A′ PASS, chưa có truth.** Decision d7308d01
trước code; source cc3b2623 trước run. Command đúng preflight, exit0,
không retry, đổi threshold hoặc thay điểm. Raw candidates.csv/summary.json
được commit **832c70ac** trước đọc bảng và rescore. Đủ 14 identity checks
(13 D base chưa có certificate, B001 kiểm lại), 13 D(ii), 13 twin và A−.
Identity đạt 14/14, D đạt 13/13, twin đạt 13/13 và A− đạt 1/1; có 13 D từ 13 base dùng được,
vượt readiness ≥10 điểm/≥5 base. Không có điểm bị loại.

Đơn vị các z là %Cref_H1 stationary approximation, không finite-h Cref.
Min/max |z_K640|=1.059109110/2.951998923%; max delta K=0.051110770 pp
tại B020, max relative change=2.864462% tại B034. B013 vẫn qua, với
z_K320−1.059323565 → z_K640−1.059109110%; B001C00 giữ dấu âm,
−5.166665601 → −5.165914795%. Max identity |drift|=7.592306955e−7
packet·s, max |drift|/bound=0.0248678914. Identity là lattice sum có
error accounting, không exact arithmetic hoặc proof mọi hành vi code.
Toàn bộ 27 cặp z và 14 identity details lưu trong hai output files.

**Audit độc lập.** Script inline chỉ đọc saved CSV/JSON, tự chọn lại
argmax/tie-break từ W1–W8, kiểm 27 members/14 bases, so từng field CSV
với JSON, tính lại H0 bằng Fraction và accounting z_K320, kiểm từng
identity/bound và tự tính K/paired-veto/status từ saved z_K640: PASS.
Không gọi builder/evaluator để audit; không tái tạo độc lập CDF K640.
Ba source hashes hiện hành và mười history/unchanged-source hashes MATCH;
window.py chỉ khác đúng allowlist đã khai. Frozen16/native3/prereg PASS;
Phase 5 v1 và v1.1 RESCORE MATCH. Không sửa source/data/verdict Phase 5.
Audit 0.05 CPU-s; guards và hai rescore 1.87 CPU-s. Logs ở console/DL,
không tạo logfile/report/plot/config riêng.

**CPU đo được và upper.** Runner/controller+descendants đo
390.830292857 CPU-s (display 390.8; làm tròn giây là 391). GNU time toàn
command: user 392.05 + system 1.20 = 393.25 CPU-s, wall 393.46 s. Chênh 2.42 s
là startup/preflight/serialization ngoài vùng runner, được bao trong
reserve, không mất khỏi budget. Receipt upper=1330+390.830292857=
1720.830292857 CPU-s; đây không phải actual tổng đo từ đầu Phase 6.
Dành **closeout upper 1750 CPU-s** bao startup/audit/guards/ghi kết quả,
giữ mọi charge cũ kể cả external-reported 130 CPU-s. Thấp hơn cap Phase 6 là 14400 CPU-s;
panel cap 7200 CPU-s giữ nguyên, chưa dùng. Cap Part A 1800 CPU-s
không là kill cap lượt này theo D6.

**Forecast.** Dự đoán 12/13 D thấp hơn observation 13/13, giữ nguyên
forecast. Dự đoán 14 identity qua được xác nhận ở phép kiểm này. Độ dịch
z có cả hai chiều; không forecast chiều chung. Forecast 10/13 dấu âm ở
truth vẫn NOT_EVALUATED: chưa chạy Part B/C/L6.3 hoặc finite-h M1 mới.

**Giới hạn và điểm dừng.** B050 vẫn ở mép c=6; c/Cref_H1 của 13 D nằm
trong 0.400561–10.684235%, chưa là chi phí nhỏ theo nghĩa vận hành.
B004/B014 chọn c khác nhau (1/2 và 3/8), nên không là matched comparison
chỉ thay h; hai cặp còn lại cùng c nhưng không tạo independence hoặc
verdict h-invariance. Chỉ kết luận 13 vị trí D(ii) đạt rule readiness ở
hai K; không H1_SUPPORTED, A1/A2 đúng, numerics-solved, causal mechanism
hoặc novelty. G1/GateC=NARROW, ownership/Understanding OPEN, realism/D22
và park/sealed giữ nguyên. **Part B, Part C và L6.3 NOT_RUN; Gate D-entry chưa GO.** Không tự chạy truth chỉ vì Part A′ PASS; không revision04/retune.

Source: experiments/P6_band/select_dii.py, tests/test_p6_select.py; sửa
một allowlist ở experiments/P6_band/window.py. Output:
results/phase6/window_revision03/candidates.csv và summary.json. Giữ
failed/blocked/HOLD/STOP artifacts DL130–132. README/exposure/AGENTS cập
nhật pointers; không thêm lesson/framework hoặc report riêng.


### DL-134 — L6.2 Part B: khóa luật đọc trước probe G_S có dấu (03/11/2026)

Người phụ trách: **Doan Van Tai**. Thực hiện và quyết định theo ủy quyền
hiện hành. Không bổ sung xác nhận tự đọc/tự viết hoặc Understanding PASS.
Entry này và PHASE_6.md được commit trước code probe và mọi truth mới.
PHASE_6.md là bản triển khai từ hai lesson vừa gửi, không giả là bản gốc
PHASE_6 chưa có. Lịch sử DL-129–133 và Main RQ giữ nguyên.

**Vì sao khóa sớm.** Probe tính truth tại ba base của panel nhưng c khác.
Ngay cả summary numerics cũng có thể ảnh hưởng lựa chọn thresholds hoặc
cách kể kết quả, nên khóa luật đọc trước probe. Sau probe chỉ có quyết
định class/twin bằng thuật toán đã khai; không tự sửa luật hoặc chọn probe
khác để có kết quả đẹp. Raw giữ kín G_S/z tới L6.4, audit chỉ đọc summary.

**B-D1, luật đọc.** READY chỉ xét G_S: tolerance R1=1/400 ở từng trục,
width≤1/4000 ở cả ba levels, sign-flip guard ngoài ±1/200. d là max hai
R1 deltas và main width, không certified bound. Nhãn '+' khi READY và
z≥1/200+d; '-' khi READY và z≤−1/200−d; còn lại U. G_S được phép âm.
Verdict chỉ dùng D với N_D cố định sau class filter: H1_SUPPORTED nếu
ít nhất ceil(4N_D/5) dấu '-' và U≤floor(N_D/10); H0_SUPPORTED tương tự
cho '+'. U quá cap → INCONCLUSIVE, còn lại MIXED. N=13 cần11 và U≤1;
N=10 cần8 và U≤1. Không chấm trên subset đã chạy nếu execution incomplete.
A− phải ra '-'; sai → dừng validity. Twin không '+' không là BUG. Cặp
can thiệp là twin '+' và D '-'; claim aggregate có chữ 'lật dấu' chỉ khi
H1_SUPPORTED và số cặp≥ceil(4N_D/5). Mọi claim phải ghi k/N, không biến
ngưỡng 80% thành kết quả đúng tại mọi điểm. U có thể do deadband dù READY.

Thứ tự tương lai: A−, rồi base ID tăng dần, twin trước D. Không dừng sớm
vì U: lịch cố định vẫn cho mô tả A2/twin, không chọn lại; CPU cap vẫn áp
dụng. Dừng vì BUG, execution/resource/budget hoặc A− failure. Không retry,
resume, refine hoặc P6 v1.1. Được báo mô tả z predicted/truth, signed và
absolute G_S, S/M/Gamma, sensitivity ε=1%; chỉ hai cặp cùng c B005/B015
và B027/B040 dùng mô tả h; B004/B014 c khác nhau. Không biến association
hoặc numerical readiness thành H1 validation/causality/novelty.

**B-D2–4, probe và sealing.** Đúng B027C02, B040C02, B050C02, c=1/16,
levels640/4,320/4,640/2; engine eta=u/2=3/4. Max postload9.375 cho cả ba.
H1 và H0a đều '+' theo scan; không phải chứng minh truth cũng '+'. Summary
không chứa G_S/z, không đọc raw trước L6.4. Ba keys sau tính là computed,
sealed; không gọi chúng là chưa từng dùng. Class đại diện và c nhỏ khó hơn
panel chỉ là assumptions; probe không phủ c lớn B050 và không chứng minh
mọi member trong class READY hoặc sai số chỉ làm giảm power.

**B-D5, quyết định cơ học.** Class không READY loại cả D/twin. Còn <10 D
hoặc <5 base → STOP_NUMERICS. Estimate=1.5×sum(cpu3_class cho từng member),
A− dùng class của nó hoặc worst class nếu thiếu. Nếu ≤7200 chạy mọi member
còn lại; nếu vượt bỏ toàn bộ twin và tính lại; vẫn vượt → HOLD_BUDGET.
PASS khi mọi class qua, PASS_REDUCED khi có class bị bỏ mà còn đủ D.
expected_U_hint dùng |z_K640|×0.85 với worst probe d, chỉ heuristic mô tả,
không điều chỉnh class, tolerance hoặc verdict. Không probe vòng hai.

**B-D6, budget.** Giữ prior upper1750 CPU-s từ DL-133; cộng tests và
preflight thực đo trước run, không reset failures/external130. Probe cap
1800 CPU-s, panel7200, tổng Phase6 cap14400. Theo dõi controller và child
CPU, RLIMIT_CPU trong worker là backstop; giữ partial/error receipts và
write-once trước call. Một worker/BLAS thread, cache probe riêng và ban
đầu chưa tồn tại. Chỉ chạy probe một lượt; Part B không PASS thì dừng C.

**Forecast trước probe.** Dự đoán cả ba class READY. Dự đoán d lần lượt
khoảng0.05/0.10/0.05 pp, main cold CPU khoảng50/90/70 CPU-s và plan
ALL_MEMBERS. C=1/16 có thể tăng ambiguous action mass; chưa có cơ sở rằng
đây luôn là worst case. Nếu d>0.4 pp thì B013 có rủi ro U dù predictor
âm; forecast này không được dùng để đổi threshold sau probe.

**Sửa kỹ thuật trước compute.** Mã mẫu cần validate row identity trước
khi gán metadata để không che lỗi tham số. Worker phải có parent reservation,
frozen/native checks trước evaluator; timeout phải kill/reap cả group và
giữ receipt. Dùng lại helpers Phase5 cho guards/evaluator/BUG/CPU tracking,
không sửa frozen engine. Cho phép thêm đúng probe.py và run.py độc lập
vào allowlist certificate cũ trong window.py; không đổi công thức hoặc
builders. Các artifact Part A′ và source predictor/identity/select giữ byte.
Trong Part C, Gate phải ràng buộc runner commit, SHA và report, không chỉ
tìm SHA ở bất kỳ chỗ nào trong log. Đây là fixes integrity trước dữ liệu.

Nhiệm vụ được phép tới Part B và, nếu dependency đạt, C.1–C.5 (một replay
probe c>0 và hai saved sign anchors). **Không chạy panel L6.3** trong lượt
này, kể cả Gate GO. Không tự mở các vùng park/sealed hoặc nâng G1.

**Preflight trước probe.** Targeted lần đầu 16 PASS,0.43 CPU-s; sau thêm
test identity/reservation đạt18 PASS trong0.92 s,0.95 CPU-s. Full suite
**728 PASS trong112.82 s**, user108.48+system1.87=110.35 CPU-s. Không
test failure; các tests mới chỉ dùng synthetic/saved exposed rows, chưa
gọi engine ở ba keys probe mới. Diff check PASS. Command tests là env
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_p6_probe.py;
full suite bỏ filepath; mỗi lượt đo bằng /usr/bin/time.

Tổng tests đo111.73 CPU-s. Prior upper1750 cộng reserve20 cho preflight,
đọc tài liệu và guards =1770; cộng tests111.73=1881.73. Dùng **prior upper
1910 CPU-s** trước probe để bao các thao tác phụ và startup, không reset
chi phí cũ. Lệnh một lượt: env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1 /usr/bin/time .venv/bin/python -B -m
experiments.P6_band.probe --spent-cpu-seconds 1910. Code và entry phải
commit trước call. Probe cap1800 và Phase6cap14400 giữ nguyên.

**Kết quả Part B.** Code cc4f0c30 trước run; raw và summary commit
dc460fdb trước khi đọc summary. Đủ9/9 calls, không BUG/execution/resource
failure. Cả3 class READY; quyết định PASS/ALL_MEMBERS, giữ13 D,13 twin,A−.
d lần lượt0.067131778/0.113556041/0.041615246 pp. Max width theo class
0.001205905/0.005981568/0.000978635 pp, đều dưới0.025 pp; mọi R1 delta
≤0.25 pp. CPU main lần lượt51.07/124.79/143.74 s; CPU3 lần lượt70.74/
160.77/193.92 s. Estimate panel5864.269366 CPU-s, dưới7200. expected_U_hint=0
chỉ là heuristic, không bảo đảm power hoặc loại trừ U ở panel c lớn.

Runner tính427.488188 CPU-s; GNU time user407.14+system20.88=428.02 CPU-s,
wall400.30 s (parent/controller và child có CPU cộng dồn, không phải wall).
Receipt upper2337.488188 CPU-s. Dành closeout/preparation upper2370 CPU-s
đến đầu Part C, bao startup và summary audit; không reset prior. Forecast
3 READY/ALL_MEMBERS đúng; forecast main50/90/70 đánh giá thấp hai class
h16, giữ nguyên forecast. d quan sát gần scale forecast, không calibration.

Audit chỉ đọc summary: tự kiểm widths/deltas/d, kept classes và budget;
raw chỉ đọc bytes để hash, không parse/in G_S/z. Cả9 raw SHA và2 source
SHA MATCH. Các keys probe là computed, sealed tớiL6.4, không là clean
held-out. Không nới tolerance, probe vòng hai hoặc xem panel truth.

**Chuyển Part C theo dependency đã đạt.** Freeze27 members, thứ tự A− rồi
twin/D theo base. Dùng lại signed G_S readiness của probe. Sửa mã mẫu để
rescore thực sự đi lại raw schedule, không tin saved stop/points bị sửa;
không chấm N=0 là H1_SUPPORTED. Gate ràng buộc committed runner/source,
predictions/plan/report hashes; workers cần parent reservation và guards.
Positive control duy nhất replay P6B_B027C02 tại640/4,c=1/16 qua runner
mới; machine chỉ so identity và scientific fields, không in outcome.
Hai saved anchors P43_0021/P43_0018 kiểm nhãn trái dấu. FAIL thì dừng.

Forecast trước positive control và L6.3, theo ủy quyền: nếu đủ N_D=13,
dự đoán MIXED với10 '-',2 '+',1 U; không gọi10/13 là H1_SUPPORTED.
Các D rủi ro U là B013/B039/B019; twin B020/B050 rủi ro không '+'.
Kỳ vọng descriptive mean |truth/prediction| khoảng0.85, chưa có bằng
chứng ở c>0 panel; không fit hệ số hoặc dùng forecast để chỉnh model.
Nếu H0_SUPPORTED, kiểm A1 ở state đuôi trước, rồi A2; không tự sửa H1.
Forecast control replay MATCH và hai nhãn anchor đúng. Các forecasts này
giữ nguyên khi lập DL-135; chưa có panel outcomes. Part C chỉ tới Gate,
không chạy L6.3 dù GO.

**Part C preflight trước positive control.** Freeze27 members từ đúng
ALL_MEMBERS, không đọc probe outcomes. Predictions SHA256
`b61efc7df3743ab027ccf5093070e123cc7e25e90173895db1a586268859353b`;
analysis_plan_v2 SHA256
`fedc00ae95ac2d795dc83949e6fbb8d2d6654fcc7de7ae1b12e7b3e1dc56112b`.
Audit27 unique physical keys, thứ tự A−/twin/D, roles/eta và disjoint với
ba probe keys và CF/R09/R10: PASS. Chỉ hash raw probe, không mở giá trị.

Targeted19 PASS/0.43 CPU-s, sau bổ sung guards24 PASS/0.51 CPU-s.
Mutant tests thực thi local bằng thay hàm trong memory:4/4 KILLED
(negative-G_S gate, D trước twin, nới U cap, bỏ A− stop),0.29 CPU-s.
Full suite **752 PASS trong117.26 s**,115.47 CPU-s. Tổng tests/mutations
116.70 CPU-s. Không test failure. Command targeted:
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_p6_run.py;
full bỏ filepath. Mutations chỉ synthetic, không sửa file source.

Prior preparation upper2370 cộng116.70 =2486.70 CPU-s; dành upper2520
trước positive control để bao guards/freeze/metadata. Chỉ một call anchor
với cap1800 CPU-s/3600 wall; tổng Phase6 vẫn14400, panel7200 chưa dùng.
Lệnh sau source commit: env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1 /usr/bin/time .venv/bin/python -B -m
experiments.P6_band.run anchor. Match identity và10 scientific fields của
V1.FIELDS, bỏ timing/resources khỏi so byte; không claim timing phải bằng
nhau. Hai saved sign anchors được label bằng cùng luật. Commit report/raw
trước đọc report; FAIL thì dừng, không sửa sau control để cứu Gate.


### DL-135 — Gate D-entry Phase 6: GO trước L6.3 (03/11/2026)

Người phụ trách: **Doan Van Tai**. Chốt kỹ thuật theo ủy quyền hiện hành;
không bổ sung xác nhận tác giả tự viết/tự đọc hoặc Understanding PASS.
Gate này xác nhận pipeline/freeze, không xác nhận H1; G1 giữ nguyên.

**Đóng băng.** Runner tại commit e3b0fa92be1d8bf412fe3a1c53fe4008d1643bbe.
Predictions27 members,13 D,13 twin,A−; thứ tự A− rồi twin/D theo base ID.
Predictions SHA256:
`b61efc7df3743ab027ccf5093070e123cc7e25e90173895db1a586268859353b`.
Analysis plan v2 SHA256:
`fedc00ae95ac2d795dc83949e6fbb8d2d6654fcc7de7ae1b12e7b3e1dc56112b`.
Code, helpers, tests, plan, predictions, probe summary và control report
được ràng buộc bằng SHA trong machine record bên dưới, không chỉ bằng
việc một SHA có xuất hiện đâu đó trong văn bản. Không sửa freeze sau Gate.

**Positive control.** Đúng một replay P6B_B027C02 tại640/4,c=1/16;
report PASS, field_mismatch=[], replay_bugs=[]. So10 scientific fields
và identity/parameters/CF flag, không yêu cầu runtime/resources bằng nhau.
P43_0021 → '-', P43_0018 → '+'. Raw/report commit094ff321 trước đọc report.
Không in G_S/z của probe/replay; raw tiếp tục sealed tớiL6.4.
Runner đo replay51.858484 CPU-s; GNU time toàn command53.69 CPU-s,
wall50.35 s; các con số không phải total Phase6 actual. Không retry.

**Luật đọc và stop.** Như DL-134 và analysis_plan_v2 §3–6: signed G_S
READY không có negative gate; primary epsilon0.5%, R1/width1/400 và1/4000,
nhãn theo z±d. Cần11/13 dấu cùng phía và U≤1; U≥2 INCONCLUSIVE.
Twin không vào verdict, chữ 'lật dấu' aggregate cần H1_SUPPORTED và11 cặp.
A− không '-' thì dừng validity. Không dừng sớm vì U: lịch mô tả vẫn cố
định, không chọn lại; vẫn dừng BUG/execution/resource/budget/A− failure.
Không retry, resume, refine hoặc P6 v1.1. INCONCLUSIVE có thể do numerics
hoặc deadband; không tự chuyển thành kết luận H1/H0 từ subset thuận lợi.

**Gián đoạn.** Mất điện/process kill: giữ mọi raw/partial, không resume
hoặc chạy lại. Ghi EXECUTION_INTERRUPTED; verdict INCOMPLETE. Write-once
reserve trước call và worker cần parent FD. Rescore đi lại raw schedule,
kiểm identity/BUG/stops/calls/labels, không gọi evaluator.

**Budget.** Trước anchor dùng upper2520 CPU-s; command anchor53.69,
cộng reserve cho guard/audit/freeze/ghi kết quả, chốt **prior upper2600
CPU-s** trước L6.3. Không reset các charges từ DL-129–134, kể cả failed
attempts và external-reported130 CPU-s. Panel cap7200, mỗi call≤1800 CPU-s
và3600 wall; Phase6 cap14400. Prior2600+panel7200=9800≤14400. Đây là
upper bảo thủ, không actual cumulative. CLI phải dùng đúng prior đã ghi,
không được giảm spent để làm mới budget. Probe estimate5864.27 CPU-s là
ước tính có hệ số1.5, không guarantee hoặc cho phép vượt cap.

**Forecast giữ nguyên trước panel.** MIXED:10 '-',2 '+',1 U; D rủi ro
U là B013/B039/B019; twin B020/B050 rủi ro không '+'. Descriptive mean
|truth/prediction| dự kiến khoảng0.85; nếu H0_SUPPORTED kiểm A1 ở state
đuôi trước rồi A2. Đây là dự đoán theo ủy quyền, không fitted calibration.
Chưa có panel truth để chấm forecasts này.

**Kiểm đã thực thi.** Part B18 targeted/728 full PASS; Part C24 targeted/
752 full PASS;4/4 local mutants KILLED. Freeze audit27 unique physical
keys/order/roles/eta/disjoint PASS; report audit PASS, raw chỉ hash.
Không thêm logfile/report riêng ngoài các artifacts lesson yêu cầu.

**Lệnh duy nhất dành cho lesson L6.3 sau yêu cầu tiếp theo:**
`env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -B -m experiments.P6_band.run run --spent-cpu-seconds 2600`
Lệnh này **chưa chạy**. Gate GO không tự kích hoạt panel trong nhiệm vụ
Part B/C. Panel output/cache chưa tồn tại; chưa có summary L6.3.
CF/SUB park,R09/R10 sealed,76 outcomes p4 chưa mở,D22 deferred,realism/
ownership/Understanding và G1 giữ nguyên. Không claim H1_SUPPORTED,
mechanism, novelty hoặc independent validation từ Gate này.

<!-- P6_GATE_D_ENTRY
{
  "status": "GO",
  "policy": "STRICT_NO_RETRY",
  "runner_commit": "e3b0fa92be1d8bf412fe3a1c53fe4008d1643bbe",
  "N_members": 27,
  "N_D": 13,
  "panel_budget": 7200,
  "phase_cap": 14400,
  "call_cpu_cap": 1800,
  "call_wall_cap": 3600,
  "prior_phase_CPU_upper": 2600,
  "files": {
    "experiments/P6_band/probe.py": "3a80d7bd1467cc050faebeff923c44c8fd94edf2447aeba9e530104e5c312e85",
    "experiments/P6_band/run.py": "62a533e56b6dee173fb61784d6c9529b2c1fdccbfec6343e26a290a8a08a8cc9",
    "experiments/P6_band/window.py": "fc2036350f1bc401c093fa08400a86548128fcfb93def2a64b51727e2da2620d",
    "notes/design/analysis_plan_v2.md": "fedc00ae95ac2d795dc83949e6fbb8d2d6654fcc7de7ae1b12e7b3e1dc56112b",
    "notes/phases/PHASE_6.md": "d0a67b65495e696ba8042d17213873eb78e58cc55efabebf57f03368209b6296",
    "results/phase6/gate_anchor/report.json": "082c14ed4b5f052463c8c3da668ec9768c79602e3aba2bd587341eda63d979ca",
    "results/phase6/predictions.jsonl": "b61efc7df3743ab027ccf5093070e123cc7e25e90173895db1a586268859353b",
    "results/phase6/probe/summary.json": "8ef543c116b5eabb59c673cd1275919bbae088ca46894d9113d1eb47d50c334b",
    "tests/test_p6_probe.py": "d41d8de776ac0f5e9636314c9e3c4bd5c23929659df1e83856bb2ddcc61ff9be",
    "tests/test_p6_run.py": "1d46b7c616bb4aaf465dbae47cdd9d4d6a8af8f522cae9cfcebcd5c324cd5696"
  }
}
-->


### DL-136 — L6.3: panel chạy một lần (fact, chưa diễn giải) (03/11/2026)

Người phụ trách: **Doan Van Tai**. Thực hiện lesson L6.3 theo yêu cầu.
Giữ forecast DL-135; không tạo thêm xác nhận tác giả tự viết forecast.
Source/plan/predictions và 10 frozen hashes khớp trước run; HEAD lúc chạy
là 8b37f559272b2692c3f25d51842fe96e188b0a6c. Panel output, summary và
cache panel đều chưa tồn tại trước lệnh. Không sửa frozen source/config.

**Lệnh đúng một lần, như DL-135:**
`env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 /usr/bin/time .venv/bin/python -B -m experiments.P6_band.run run --spent-cpu-seconds 2600`
Lệnh chạy trong tmux p6_l63_20261103, một worker/BLAS thread 1, không RNG.
WSL: systemd-inhibit bị từ chối; thay bằng process Windows keep-awake
tạm thời. Trước run, BatteryStatus=2 (AC), pin 96%; đĩa trống 862 GB, RAM
khả dụng 10 GiB. Không đổi power plan lâu dài; keep-awake đã giải phóng
khi xong. Operational wrapper chỉ gọi lệnh một lần và commit/push raw
ngay sau kết thúc, không mở panel files trong lúc chạy.

**Niêm phong dữ liệu trước đọc counts.** Commit
`d7a298f09f2d4a37c6f1dea1b4e9ebeb12609c67` gồm 81 raw JSON rows và
summary.json, đã push origin/main trước rescore. Console trong lúc chạy
chỉ progress/status; cuối command chỉ stop_reason, verdict và CPU.
Không retry, resume, refine hoặc sửa dữ liệu sau run.

**Fact.** stop_reason=null; calls 81/81, 27/27 members đã chấm;
noncompleted_calls=0. D có N_D=13: '-' 3, '+' 2, U 8. Verdict của runner:
**INCONCLUSIVE**. Tính độc lập từ counts, không gọi hàm verdict của
runner: ceil(4×13/5)=11, floor(13/10)=1; U 8 > 1 nên INCONCLUSIVE, khớp.
A− P6_B001C00 có nhãn '-'. Twin: '+' 11, '-' 0, U 2. intervention_pairs=2/13;
intervention_wording_allowed=false. Chỉ ghi số đếm, chưa diễn giải.

**Rescore và integrity.** Lệnh env/threads như trên, thay phần module
command bằng `experiments.P6_band.run rescore`: **RESCORE MATCH**, 0.16
CPU-s, không evaluator. 10 frozen hashes PASS; 81 raw rows và summary
khớp byte commit dữ liệu (82/82 files), chỉ kiểm bytes, không in outcomes.
Integrity audit 0.39 CPU-s. Không chạy lại pytest/full suite cho frozen
code không thay đổi; 752 full tests PASS là kiểm đã làm ở L6.2 Part C.

**CPU/budget.** Runner 1339.9 CPU-s trên panel cap 7200; GNU time toàn
command user 1237.35 + system 104.83 = 1342.18 CPU-s, wall 1252.36 s. Prior upper
đã khóa 2600 CPU-s; receipt-based phase upper 3939.9 CPU-s, không actual
tổng đo từ đầu phase. Dành closeout upper 4000 CPU-s bao startup/preflight,
rescore/integrity/operational logging và ghi kết quả. Giữ charges cũ,
không reset budget nhờ cache; Phase 6 cap 14400 giữ nguyên.

**Deviation thí nghiệm:** không. Không gián đoạn, BUG, resource failure
hoặc chỉnh source/threshold/order. Environment dùng tmux và process
keep-awake thay systemd-inhibit, không đổi các tham số tính toán.

**Paths.** Raw: results/phase6/panel/; số đếm/resources:
results/phase6/summary.json. Operational console log ngoài Git:
/home/vantai/.cache/state-model-regret/phase6/l6_3_ops_rusb0l0o/console.log;
status.json và supervisor.py cùng thư mục ghi việc gọi lệnh/commit, không
phải source khoa học. Không tạo CSV, plot hoặc report mới. README,
AGENTS và exposure register cập nhật checkpoint.

**Điểm dừng.** L6.3 execution COMPLETE; raw đã commit, rescore MATCH và
DL-136 có fact. L6.4 chưa thực hiện; chưa đọc z/lý do U theo từng điểm,
không prior check hoặc đổi G-level. Raw probe/replay tiếp tục niêm phong
tới L6.4; G1, D22/realism/ownership/Understanding và park/sealed khác
giữ nguyên. Không chạy lại panel dù Gate record lịch sử vẫn GO.
