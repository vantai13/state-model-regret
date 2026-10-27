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

### DL-051 — A01 run01 FAIL, arrêt avant PartB; correction certificate (2026-10-27)

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
