# Legacy index — kiểm ngày 07/10/2026

| Repo | Tag | Commit đầy đủ | Ghi chú |
|---|---|---|---|
| dt4n-decision-risk-project | [`archive-switch-or-stay-2026-10-02`](https://github.com/vantai13/dt4n-decision-risk-project/tree/e669f5c8053a81d6de192de9f9d0d6304ee67802) | `e669f5c8053a81d6de192de9f9d0d6304ee67802` | Annotated, push/peeled hash đạt; 10 nhánh remote ban đầu là ancestors. |
| dt4n-decision-risk-project | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07`](https://github.com/vantai13/dt4n-decision-risk-project/tree/2e7543b2794a85645d60c0a55afb5a670166a099) | `2e7543b2794a85645d60c0a55afb5a670166a099` | Giữ riêng 3 local commits N0–N2 ngày 02/10, nhánh wip-local-2026-10-07. |
| dt4n | [`archive-2026-09`](https://github.com/vantai13/dt4n/tree/d45cf4ff26d8c6204a181f0fa77887e087a4d381) | `d45cf4ff26d8c6204a181f0fa77887e087a4d381` | Remote hash đã kiểm; MAP.md mở được, tag không có README.md. |

Bốn tag cũ phase-0-complete, phase-0v2-complete, pre-pivot-v14, prereg-f7 đều IN archive chính. Tổng 11 nhánh được giữ bởi tag chính/tag phụ; không merge và không di chuyển tag.
Seeds đã xem: [registry immutable](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/seed_registry.md) và [sổ exposure bổ sung](../notes/00_exposure_register.md).

## Bằng chứng mở công khai

- [Inventory/source links](../notes/00_evidence_inventory.md), [source digests](../notes/verification/source_checks.json).
- [Script tái kiểm](../notes/verification/verify_archive.py), [JSON số liệu](../notes/verification/verification_results.json), [cách chạy](../notes/verification/README.md).
- [Bundle manifest](../notes/verification/bundle_manifest.json): metadata rút gọn từ manifest thật, không phải nội dung bundle.
- [Raw AoI manifest](../notes/verification/raw_backup_manifest.json): 30 aoi_*.jsonl, 71.674.153 byte không nén; cả tar có 1.141 file, 444.748.020 byte không nén, 58.057.695 byte nén. Không đồng nhất raw AoI với toàn tar hay bộ “427 MiB” chưa xác định.
- [Final Review reading note](../notes/verification/final_review_reading_note.md): tóm tắt sections đã đối chiếu; full snapshot có SHA-256 `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`, chưa công khai và chưa có byline rõ. Không phải bản gốc thay thế.

## Ngoài archive / nguồn chưa công khai

- dt4n có 4 local commits chưa nằm trên remote tại inventory đầu, tip d387f4df694a95719ce5287b99a1246c0060de94 và 2 stash; giữ bằng bundle local, không tuyên bố đã push.
- dt4n-core có remote riêng và bundle riêng, không thuộc hai tag switch-or-stay. Lỗi fetch SSH đã được kiểm lại qua HTTPS; không có local branch commits ngoài remote sau fetch.
- Ba bundles dt4n.bundle, dt4n-core.bundle, ndt-decision-risk.bundle đã verify và có bản sao thứ hai trên filesystem Windows cùng máy, SHA-256 trùng manifest. Chưa phải independent off-site backup; không upload bundle lên repo public.
- Inventory đầu ghi 16.380 ignored files trong working tree cũ, gồm venv/cache/raw results. Danh sách chi tiết vẫn local-only; tags không giữ ignored files. Không dùng con trỏ local làm bằng chứng có thể mở cho người đọc GitHub.
- Raw backup dt4n-raw-phase23-aoi-20260827.tar.gz và backup lớn dt4n-FULL-BACKUP-20260828.tar.gz vẫn local-only; backup lớn chưa audit nội dung ở L0.1. Metadata raw không thay remeasurement AoI.
- Sandbox/Colab/máy khác chưa kiểm được; không khẳng định lưu đủ mọi công việc hoặc mọi dữ liệu đã nhìn.
- PHASE_0/master plan v1.1 đầy đủ và bảng EV numbering gốc chưa có để đối chiếu. Primary literature chưa tự kiểm lại; giới hạn được giữ ở inventory.
- Không chép nguyên văn private feedback/biên bản GVHD vào repo public khi chưa có permission. Việc hỏi quyền chia sẻ tài liệu sẽ đưa vào memo; chưa có record đã hỏi/được đồng ý.

## Phân loại theo contract v0 (L0.5)

Tác giả: **Doan Van Tai** · Bổ sung: **08/10/2026**.

> Nhãn đo **mức khớp với contract**, không đo chất lượng công việc cũ. Nội dung tích hợp từ File 4 tác giả cung cấp; cột “Đã kiểm” ghi đối chiếu kỹ thuật thực sự đã làm với archive, không thay bài tự kiểm của tác giả. Chưa có record tác giả tự kiểm ít nhất 5 dòng trong `notes/lessons/L0.5_legacy.md`.
> Nhãn: **Keep** (dùng trực tiếp; migrate khi có experiment cần) · **Reference** (đọc để học, không import) · **Archive** (thuộc RQ cũ) · **Rebuild** (ý đúng, giả định sai; viết lại có test) · **Unknown** (chưa đủ thông tin).

Contract hiện hành: [D1–D25 và §0–§10](../notes/01_definitions.md), chưa gắn tag `contract-v0`. “Tag chính” và “wip” trong bảng dưới đây lần lượt là hai tag switch-or-stay ở đầu file, đã kiểm peeled commits ngày 08/10/2026. Các nhãn dựa trên file chỉ mới kiểm tồn tại vẫn là phân loại dự kiến; chưa là validation nội dung.

| Artifact (tag chính trừ khi ghi khác) | Nhãn | Lý do theo contract | Dùng khi | Đã kiểm |
|---|---|---|---|---|
| `experiments/f04b_des_gap.py::workload_after` | Reference | Engine workload nhận arrival stream, có phép cắt $[\cdot]^+$; buffer hữu hạn khác AS3 | Phase 7 | Đọc dòng 40–50: reflection ở 45, giới hạn nhận gói ở 47; không rerun DES |
| `experiments/scan/des_world.py` | Rebuild | Gói đến chỉ sinh từ tải nền; managed flow là probe đọc workload, action không chuyển tải theo D5 | Phase 7 nếu cần | Đọc `des_path`: arrivals ở 31–35, probe đọc ở 44–51 |
| `ndtrisk/theory/mdk.py` + `tests/test_mdk.py` | Reference | Nghiệm M/D/1/K dừng; chỉ cần nếu muốn comparator steady-state | Phase 4 (tuỳ) | Cả hai file tồn tại; chưa chạy test cũ |
| `experiments/scan/world.py` | Reference | Workload OU thay thế cho kiểm tổng quát; `T_tel` đổi cùng lúc tuổi, cửa sổ và nhiễu (N2) | Phase 7 | Đọc `telemetry_view` dòng 22–29: cửa sổ T, đếm Poisson, `rhohat=n_pkt*s/T` |
| `experiments/scan/twin.py` | Archive | Posterior của tải và DelayCurve trạng thái dừng, không có backlog input của $M_0/M_1$ ở D10 | — | Đọc `DelayCurve` dòng 11–26, `posterior` dòng 35–40 và `twin_view` |
| `experiments/scan/telemetry_fit.py` | Reference | Ý tưởng twin ước lượng tham số là ứng viên feasible model repair, chưa phải operator đã kiểm | Phase 8 | File tồn tại; chưa audit riêng |
| `experiments/scan/rollout_v2…v6.py`, `experiments/gocheck/*` | Archive | So luật quyết định với harm budget của RQ cũ | — | Có 5 file rollout và 8 file trong gocheck tại tag chính |
| `results/*`, `experiments/results/*` | Archive | Evidence thế giới cũ; motivation cho RQ mới | — | Scope đã ghi trong inventory; không rerun kết quả |
| wip: `experiments/n01c_crn_two_branches.py` | Reference (cách tổ chức) | Chuyển tải từ đầu warm-up; chưa branch từ cùng workload tại thời điểm quyết định, không dùng làm mẫu CRN đúng cho D12 | L1.7 | Đọc header, phép đọc workload và cảnh báo dòng 62; inventory cũng nêu giới hạn |
| wip: `experiments/n00–n02*.py`, N0–N2, test | Reference (thiết kế) / Archive (kết quả) | Factorial trên twin cũ; S/M/P không phải State/Model repair mới | L1.7 | Liệt kê script/test; `n02_source_factorial.py` dòng 26 import `scan.twin.posterior`, header ghi PSA |
| `data/aoi_measured/*` | Reference | AoI của NDT prototype Ditto, có PROVENANCE và SHA-256; **không dùng làm neo** tuổi thông tin — T00 dùng trục chế độ telemetry (DL-008) | Chỉ đối chiếu lịch sử | Đọc JSON/PROVENANCE, kiểm hash và 10 ô: [T00](../notes/theory/T00_timescale_sanity.md) |
| `data/mininet_calibration/*` | Reference | Calibration HTB token bucket là ứng viên representation độc lập | Phase 7–8 | 5 file tồn tại; chưa audit nội dung riêng |
| `notes/seed_registry.md` | Reference (cách làm) | Giữ cách làm sổ seed; cập nhật exposure mới trong repo này | L1.7 | Đọc registry: dải đã xem, “để dành” và cảnh báo seed mới không tự thành confirmation |
| `notes/ownership/O1_pipeline.md`, `notes/lessons_from_dt4n.md` | Reference (cách làm) | Mẫu “Làm gì – Vì sao – Nếu sai”; bài học quy trình | Mọi lesson | Cả hai file tồn tại |
| `notes/theory/T1_queue.md`, `notes/theory/T2_ou_measurement.md` | Reference | Nền queue và OU | Phase 1, 7 | Cả hai file tồn tại |
| `notes/theory/T3–T5`, `notes/feasibility/*`, `notes/map/*` | Archive | Lý thuyết và spike của RQ cũ | — | Giữ phạm vi lịch sử; không audit mới toàn bộ nhóm |
| `notes/01_literature/notes/opentwin_2026_v2.md`, `notes/01_literature/notes/li_remote_decision_2026.md` | Keep | Ứng viên closest prior P10/S11 theo hướng dẫn; phải kiểm đúng primary paper trước khi dùng | Phase 2 | Cả hai file tồn tại; chưa xác nhận nội dung primary |
| Repo `dt4n`: `mininet/`, `bridge/`, `ditto/`, `dashboard/`, `cloud/`, `rl/`, `cert/` | Archive | Engineering platform không cần cho diagnostic hiện tại | Chỉ khi Phase 8 cần timing | Theo hồ sơ L0.1; chưa audit mới các thư mục |
| dt4n: 4 commit local + 2 stash (bundle) | Unknown | Chưa kiểm nội dung để phân loại | Ngoài đường găng Phase 0 | Chỉ có record tồn tại/bảo toàn ở L0.1 |
| Repo `dt4n-core` | Unknown | Remote riêng, ngoài hai tag switch-or-stay; chưa kiểm mức phù hợp RQ | Ngoài đường găng Phase 0 | Metadata remote/bundle đã biết, nội dung chưa phân loại |
| Backup raw AoI (30 `aoi_*.jsonl`) | Unknown | Chưa chứng minh là bộ khoảng 427 MiB; chưa tái tính AoI | Phase 8 | Metadata trong raw manifest; không coi JSON summary là raw revalidation |

**Engine khác chỗ gọi engine.** `workload_after` nhận một arrival stream bất kỳ rồi cập nhật workload với reflection và finite-buffer admission. `des_world.py` tạo arrivals từ tải nền rồi dùng probe đọc workload đó, không đưa managed traffic sau Switch vào queue. Engine có thể tham khảo; protocol gọi engine phải rebuild cho D5 và AS3.

**Keep không có nghĩa chép ngay.** AoI hiện được trích qua immutable archive ở T00; chưa có experiment cần migrate file. Các module mới chỉ dùng code thuộc repo này và thư viện đã khai báo, không import từ workspace cũ.

### Không mang sang

| # | Giả định cũ | Nằm ở | Mâu thuẫn với contract hiện hành |
|---|---|---|---|
| 1 | Managed flow không làm đổi tải | `des_world.py`, probe chỉ đọc | D5: A giảm đúng lượng B tăng |
| 2 | Objective gain-ms với harm budget; SESOI 8,1 ms của VoIP | Brief cũ; F6 | D13–D14 và D23: objective/threshold phải đúng construct hiện tại |
| 3 | Oracle cùng thông tin hoặc oracle nhìn trước tương lai trong thiết kế cũ | F6/F7; rollout, tùy benchmark | D15: chung oracle biết current state/law, không biết $w$ |
| 4 | Twin chỉ là đường cong trạng thái dừng | `scan/twin.py` | D10: dự báo động, load-aware, có initial state hợp lệ |
| 5 | Mỗi luật tự đi quỹ đạo riêng | Rollout v2–v6 | D5, D12 và §1: một quyết định/episode, bốn ô cùng episode/horizon |
| 6 | H2, κ, phân rã info/center/width/safety thay cho estimand mới | T4–T5, F7 | D19: contrasts giá trị can thiệp State/Model |
| 7 | Observation là số gói đếm theo cửa sổ | `scan/world.py` | D8: backlog timestamped; muốn đổi schema phải sửa contract |
| 8 | Dải seed được mặc định coi là “fresh” | `seed_registry.md`, F6 | §9 seed streams và [exposure register](../notes/00_exposure_register.md) |
| 9 | Chia lỗi bằng Shapley rồi coi phần phân bổ là nguyên nhân | N2 | D19 và §0: đo giá trị can thiệp, không attribution phần trăm lỗi |
| 10 | Dùng lại seed 9101–9110 hoặc cấu hình n02 làm confirmation | wip | §9 seed streams/held-out; exposure bao gồm seed **và** regime |

Đã nối 10 mục với định nghĩa/quy tắc hiện có trong [contract](../notes/01_definitions.md). Các giả định cũ vẫn có thể hợp lệ cho RQ cũ; danh sách này ngăn dùng chúng làm mặc định cho RQ hiện tại.

### Quy trình migrate — chỉ khi có experiment cần

`git show <tag>:<path> > <đích>` (byte-exact) → file `PROVENANCE` đi kèm (repo, tag, peeled commit, path, ngày, lý do) → SHA-256 → test kiểm checksum → một dòng decision log. Không chèn header hoặc đổi byte trong file được chép; thông tin tác giả/biên tập của bản migrate ghi ở PROVENANCE riêng. Không di chuyển tag archive.

### Tự kiểm L0.5

Đối chiếu kỹ thuật đã đọc hơn 5 artifact/nhóm ở bảng trên, gồm hai đoạn code cốt lõi. Bài tác giả tự giải thích ít nhất 5 dòng còn chờ ở `notes/lessons/L0.5_legacy.md` (file 8). Với mỗi artifact, trả lời:

1. Nó phục vụ câu hỏi nào của contract?
2. Giả định không phù hợp nằm ở đâu?
3. Cần rebuild hay chỉ đổi input?
4. Nó đã được verify với model nào, và bằng chứng đâu?
5. Experiment nào cần nó ngay bây giờ?

Mở lại nguồn từ clone archive:

```bash
git -C /path/to/archive-clone show archive-switch-or-stay-2026-10-02:experiments/f04b_des_gap.py | rg -n -A10 'def workload_after'
git -C /path/to/archive-clone show archive-switch-or-stay-2026-10-02:experiments/scan/des_world.py | rg -n 'arrivals|probe|workload_after'
```

Giữ các mục Unknown ở trạng thái chưa phân loại; không mở bundle hoặc chạy lại experiment cũ để lấp checklist. Cập nhật dòng nguồn gốc khi có record tự kiểm thật của tác giả.
