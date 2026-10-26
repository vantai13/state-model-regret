# L2.5 Part2 — kết quả triển khai và kiểm chứng

Người phụ trách: **Doan Van Tai** · **26/10/2026**.
**Technical execution đã hoàn tất; tác giả Understanding/L-self/Gate chưa xác nhận.**

## Đã thực hiện

| Yêu cầu | Artifact / trạng thái |
|---|---|
| M00 A+model, đúng phiên bản | [Note M00](../../../../notes/literature/papers/M00.md); AI-T trên submission28trang; journal identity TPDS2000 đã kiểm DOI |
| Tính toy bốn server | [server_summary.csv](server_summary.csv), [phân phối332records](server_distribution.csv); exact, không service, không replication |
| Tính V1 từng bước + hi={2,5} | [Bài Part2](../../../../notes/literature/information_harm.md), [32 outcome costs](cost_events.csv), [8policy rows](policies.csv) |
| Phân biệt hai cơ chế / sửa lesson | [Bài Part2](../../../../notes/literature/information_harm.md); herding cần repeated decisions, không bắt buộc nhiều controller |
| P01 screen/skip và mức đọc đúng | [P01](../../../../notes/literature/papers/P01.md); Def2/§2.5/Fig2 AI-T; không đọc proofs, không thêm hàng Excel bắt buộc |
| K-S1…8 và ba câu khác biệt | [Prior boundary](../../../../notes/literature/prior_boundary.md#trục-state--l25-part2-26102026); giữ nguyên bảng PC/forecasts cũ, draft chờ A4/L2.9 |
| A4 R04 / provenance | [source_access.json](source_access.json): note cũ AI-T24/10, chỉ kiểm provenance; primary mapping còn mở |
| Log / thư viện | [search log](../../../../notes/literature/search_log.md), [Excel8rows](../../../../papers/paper_comparison.xlsx); M00 mới,7record cũ giữ nguyên |

## Số đo thực chạy

44checks PASS với Fraction exact; không Monte Carlo/seed hay confidence interval.
So trực tiếp helper L2.2 và frozen JSON L2.3 sau khi enumerate độc lập.

| Case | L00 | L10 | L01 | L11 | GS | GM | GSM | Γ | GSgivenM1 | GMgivenS1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1, hi={1,6} | 1,25 | 1,5 | 1,25 | 1,25 | −0,25 | 0 | 0 | 0,25 | 0 | 0,25 |
| hi={2,5} | 1,25 | 1,25 | 1,25 | 1,25 | 0 | 0 | 0 | 0 | 0 | 0 |

Đơn vị packet·s: capacity3packet/slot, U2, dt1s, một slot; không plant v1.2.
M1 exact true expectation; M0 rollout conditional mean. Bài tập có true hi tie,
Stay thắng tie. Bias hi/Stay giảm1→1/2 nhưng vẫn tồn tại; GS hết âm vì action
được chọn không mất true cost, không phải M0 trở thành đúng.

V1 R00/R10/R01/R11=(0,.25,0,0); bài tập đều0. Đây là negative state gain với
approximate policy, không là thêm thông tin làm hại Bayes-optimal controller.

Toy server, q0=(0,3,3,3),8jobs, service0: expected terminal q là stale shortest
(8,3,3,3), random(2,5,5,5), stale d2(4,13/3,13/3,13/3), fresh shortest(5,4,4,4).
D2 lấy pair không lặp/random tie; fresh tie index. Không so max E[q] với E[max q]
như một đại lượng: random có Emax=409001/65536, d2=3177203/559872; không suy delay.

## Commands và output

```bash
set -o pipefail
.venv/bin/python -B experiments/lessons/l2_5_information_mechanisms.py | tee results/lessons/l2_5/part2/run.log
.venv/bin/python -B tools/paper_library/build_notes.py | tee results/lessons/l2_5/part2/workbook_build.log
.venv/bin/python -B experiments/lessons/audit_l2_5_part2.py | tee results/lessons/l2_5/part2/audit.log
sha256sum -c results/lessons/part_a/SHA256SUMS
git diff --check
```

- [Code exact](../../../../experiments/lessons/l2_5_information_mechanisms.py),
  [config](config.json), [JSON](toy_results.json), [summary CSV](summary.csv),
  [run.log](run.log). Không overwrite output Part1/L2.2/L2.3/L2.4.
- [Auditor độc lập](../../../../experiments/lessons/audit_l2_5_part2.py),
  [verification](verification.json), [audit.log](audit.log).
- [Source metadata](source_metadata.json), [access/hashes](source_access.json),
  [reading card](reading_card.md); không có PDF trong Git.
- [Workbook build](workbook_build.log), [kiểm workbook](../../../../papers/data/verification.json).
  Backup trước đổi ngoài Git: `~/papers/state-model-regret/archive/2026-10-26_before_l2_5_part2/`.

Auditor dùng CSV để dựng cost/decisions/contrasts lại và dùng multinomial formula
độc lập DP cho phân phối server; kiểm7record Excel cũ,55file protected và link.
52checksum PartA giữ cùng file set; chỉ cập nhật hash tài liệu index/ledger đã
đổi, không sửa số liệu/proof/code PartA. Kết quả audit chi tiết nằm trong JSON/log.
Không rerun toàn bộ202tests vì production plant không đổi; không lấy số lịch sử
đó làm test count của lượt này.

Audit cuối **PASS**:32cost rows,8policy rows,332terminal records;7record Excel cũ
giữ nguyên,55protected files không đổi,221local Markdown links tồn tại và52/52
checksum khớp. `git diff --check` PASS. Log checksum ở `checksums.log`.

Lần đầu auditor dừng ở link `verification.json` vì đang kiểm chính output chưa
tạo của nó; đã sửa thứ tự kiểm output này, rồi chạy lại. Không phải lỗi số toy.
Kiểm staged còn phát hiện CRLF trong CSV; đã đổi generator sang LF và chạy lại
exact/audit/staged checks trước push. Các giá trị số không đổi.

Access limitations: web arXiv abs cache miss, fallback tải PDF v1 thành công;
pdfinfo có xref warning nhưng text và render PDF3/4 đọc được. M00 font cũ làm
MCP text tách chữ; dùng layout text/web và nhìn hình. Một lệnh `python` không có
trong PATH đã được sửa sang `python3`/`.venv/bin/python`; không ảnh hưởng output.
Không chạy Crossref sai P01 từ mentor, không bịa query/log đó thành của phiên này.

## Kết luận và điều còn mở

Đã xác nhận đúng số toy, convention d2 và phân biệt regret/benchmark của P01 từ
primary source; đã sửa các khẳng định mạnh quá trong lesson. Γ>0 của V1 tự theo
identity khi GS<0 và GSgivenM1=0, không là bằng chứng cơ chế độc lập.

**Chưa xác nhận:** novelty; GS/Gamma trên lưới; generality ngoài toy; full VoR M00;
proofs P01; primary mapping R04/A4; bài tự kiểm/đọc của tác giả và formal Gate.
G1, contract, forecasts/labels, thresholds và HOLD Phase4 giữ nguyên. Có thể học
L2.6 theo lesson; không tự chạy Phase3 hoặc freeze prereg A05 trong tác vụ này.
