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
