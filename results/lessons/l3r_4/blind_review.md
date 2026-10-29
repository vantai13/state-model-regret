# L3R.4 — Fresh blinded automated realism review

Người phụ trách: **Doan Van Tai** · 29/10/2026.

**Label consistency: PASS trong phạm vi năm input được phép. Realism thực nghiệm: HOLD, chưa được xác nhận.** Đây là review tự động mới, bị giới hạn input; không phải human feedback, xác nhận GVHD hay tác giả tự đọc/read-back. Tên người phụ trách không phải attestation rằng người đó đã trực tiếp thực hiện review này.

## Phạm vi đã đọc

Chỉ đọc đúng năm input:

- `notes/realism/envelope_v1.json`
- `notes/realism/rules_v1.md`
- `notes/realism/worksheet_v1.md`
- `results/lessons/l3r_4/screen/labels.csv`
- `results/lessons/l3r_4/screen/receipt.json`

Không đọc gains, pilot outcomes, reports khác, phase summaries, source code, Git diff/log, design CSV, implied features CSV hoặc primary papers; không dùng network hay tìm literature mới. Có references/thresholds trong chính input được phép, nhưng không mở references hoặc suy vùng effect từ chúng. Không sửa frozen inputs. Chỉ tạo report này.

Review kiểm được consistency, số đếm, dedup và hash của input hiện có; chưa kiểm công thức/implementation, membership ID so với design gốc, primary evidence hay chronology của commits. Hai trường `outcomes_opened=false` và `CF_opened=false` là khai báo trong receipt, không phải audit truy cập độc lập. `feature_rows=432` phù hợp số học 216×2 nhưng artifact features không được đọc. Không sử dụng thông tin báo lỗi/đã sửa code do người khác chuyển tiếp làm bằng chứng source correctness.

## Số đếm và integrity

| Context | f | ID | Tọa độ | IN | EDGE | OUT | UNSOURCED |
|---|---:|---:|---:|---:|---:|---:|---:|
| a | 1.5 | 216 | 210 | 0 | 0 | 0 | 216 |
| a | 2 | 216 | 210 | 0 | 0 | 0 | 216 |
| a | 3 | 216 | 210 | 0 | 0 | 0 | 216 |
| b | 1.5 | 216 | 210 | 0 | 0 | 0 | 216 |
| b | 2 | 216 | 210 | 0 | 0 | 0 | 216 |
| b | 3 | 216 | 210 | 0 | 0 | 0 | 216 |

Tổng cộng **1.296 dòng, 216 ID, 210 tọa độ** tám thành phần. Chuẩn hóa từng thành phần bằng `fractions.Fraction` vẫn cho 210 tọa độ; không có duplicate ẩn do cách biểu diễn phân số.

- Khóa `(id, context, f)`: 1.296 khóa, 0 khóa trùng; đủ sáu tổ hợp context/f cho mỗi ID hiện diện; 0 tổ hợp thiếu/thừa.
- Khóa `(coordinate, context, f)`: 1.260 khóa; 36 dòng dư do sáu cặp ID chung tọa độ, lặp qua hai contexts và ba f. Đây là duplicate tọa độ đã khai báo, không phải 36 thiết kế độc lập mới.
- 0 ID có nhiều tọa độ; 0 xung đột label/missing/flags giữa ID chung tọa độ trong cùng context/f.
- 1.296/1.296 dòng có đúng mười mục missing: `tau_eff_s` cộng chín ràng buộc bắt buộc; 0 mismatch hoặc tên lặp trong danh sách missing.
- Buffer flag: 1.296 UNSOURCED; actuation flag: 1.296 UNSOURCED; mode-oracle flag: 1.296 `True`. Ba cờ tách biệt, không thấy điểm realism tổng hợp trong CSV.
- Các dimensions và sáu bảng counts trong receipt khớp CSV; `expected_ids=216`, `expected_distinct=210` của envelope khớp nội bộ. Chưa đối chiếu membership với design gốc.

Sáu duplicate theo thứ tự khóa `(λA,λB,κ,u,h,c_sw,ref,K)` khai trong rules:

| Tọa độ | Hai ID |
|---|---|
| `15/2|8|3/10|1|8|0|1|40` | X1037, X2066 |
| `15/2|8|3/10|3/2|8|0|1|40` | X1039, X2069 |
| `7|8|3/10|1|8|0|1|40` | X1025, X2030 |
| `7|8|3/10|3/2|8|0|1|40` | X1027, X2033 |
| `8|8|3/10|1|8|0|1|40` | X1049, X2102 |
| `8|8|3/10|3/2|8|0|1|40` | X1051, X2105 |

## Evidence gaps và common-τ

Envelope có hai `tau_eff_s=null`, 18/18 miền `allowed_tau_s=null` (chín/context), hai `buffer_time_s=null`, hai `actuation_s=null`. Mỗi context có đủ tên chín constraints, nhưng chưa có numerical envelope cho constraint nào. Rules 2–3 buộc UNSOURCED trước nhãn khác; mọi label hiện tại tuân thủ policy đó. Null không chứng minh OUT hoặc IN.

Worksheet ghi các khác biệt định nghĩa có ý nghĩa: rate/poll khác backlog AoI; loop period khác thời gian giữ quyết định; egress threshold khác offered input; burst theo ngưỡng khác mode duration; IDC/interarrival CV khác CV_rate trên cửa sổ vật lý cố định; dynamic shared-buffer occupancy khác budget per-port đổi ra thời gian. Review xác nhận caveats có mặt trong tài liệu, chưa xác minh primary claims/locators trong papers. Nguồn LAN lịch sử không tự xác nhận edge hiện đại; scope fluid/two-mode/a/c=.6/ideal backlog/infinite buffer/instant action vẫn là giới hạn thực chất.

Luật common-τ được viết phù hợp mục đích chống chọn scale riêng: một τ đồng thời cho T, h, delay và CV trên cửa sổ vật lý cố định; EDGE cũng không được nới miền tuổi có nguồn. Anchor minh họa 10ms/100ms bị loại khỏi chứng nhận IN; không thấy CSV nâng anchor thành evidence. Tuy nhiên, mọi miền đều null nên không có giao miền số để kiểm. PASS hiện tại không xác nhận implementation của common-τ khi có miền hữu hạn, cũng không kiểm được nhánh IN/EDGE/OUT.

## Factor sensitivity và điểm cần rõ trước phiên bản có nguồn

`k=1`, `f_primary=2`, sensitivity `f=[1.5,2,3]` thống nhất giữa envelope và CSV. Cả ba f cho cùng nhãn vì missing-first policy. Đây chưa phải bằng chứng realism robust với dung sai và chưa kiểm ranh EDGE/OUT. Không có cơ sở từ review này để đổi f, k hoặc các engineering thresholds.

Trước phiên bản có đủ nguồn cần khai rõ: (i) `offered_mean_and_peak_load` là constraint ghép, vậy nới cả mean và peak có được tính một đại lượng theo k=1 hay không; (ii) phép nới có nghĩa của observation schema/variability shape nếu có. Rules đã cấm tự bỏ qua định tính nhưng v1 chưa cung cấp phép nới cụ thể. Đây là khoảng trống ở nhánh phân loại tương lai, không gây nhãn sai trong bảng toàn UNSOURCED hiện tại. Chuyển mỗi constraint thành miền τ, xử lý miền rời/biên và duy trì cửa sổ CV vật lý cũng cần kiểm khi có input số; source nằm ngoài review này.

## Rủi ro motivated realism và giới hạn kết luận

Các biện pháp có mặt trong v1: contexts a/b định trước; common-τ; không lấy số khác định nghĩa làm dải; không suy OUT từ thiếu nguồn; khai trước f/k; nguồn sau labels phải tạo phiên bản mới; buffer/actuation/oracle tách khỏi label. Về thiết kế, các biện pháp này hạn chế chọn scale/envelope để hợp thức hóa vùng đã thấy; review không chứng minh quy trình thực tế không chịu ảnh hưởng bởi pilot.

Rủi ro còn lại: chọn nguồn/dải thuận lợi sau labels hoặc outcomes; dùng anchor minh họa như tuổi thực; xem cùng nhãn trên ba f như robustness thực nghiệm; dùng tỷ lệ 216/210 như tần suất ngoài đời; dùng UNSOURCED để che known tension của model. Cần tiếp tục giữ tension/definition mismatch trong worksheet và provenance/version của nguồn mới, kể cả sau khi có số đo. Reviewer không đọc outcomes nên không đánh giá được liên hệ giữa lựa chọn realism và vùng effect; không quyết định MV/SH riêng hoặc suy effect sign/magnitude.

Kết luận được hỗ trợ là **v1 chưa đủ nguồn để chứng nhận realism ở cả hai contexts; HOLD phù hợp policy đã khai**. Review này không chứng minh thiết kế thực tế/phi thực tế, buffer triển khai an toàn, model đủ fidelity hoặc scope repair đã được adopt.

## Hashes, kiểm chứng và artifacts

SHA-256 của ba frozen inputs đọc được và `labels.csv` đều khớp receipt: **4/4 PASS**. Không kiểm hashes của source/note/design còn lại. Fingerprint receipt dưới đây không chứng minh receipt tồn tại trước outcomes.

| Input | SHA-256 |
|---|---|
| envelope_v1.json | `11f6983cf76d2ddf20936dbead575343e6909ba65a81415bbf2081a83622268e` |
| rules_v1.md | `0e983e15cb6cca5582581a2babc153670fab93c61852def7fb02ce22244bef7a` |
| worksheet_v1.md | `bf6afeba79bf8880372be96ef4e6ba0c5ad0a71c0c13caa50d1f8691eba82e00` |
| labels.csv | `ca3471bf6b06baccd4178c59322e576386b9e21f5830dd5749f48e9867161ae6` |
| receipt.json | `09ec6034859e010ba8a63692b606a2338432d73ee720003721a6dc1bcf96a965` |

Lệnh đã chạy: `cat notes/realism/envelope_v1.json`, `cat notes/realism/rules_v1.md`, `cat notes/realism/worksheet_v1.md`, `cat results/lessons/l3r_4/screen/receipt.json` đều exit 0. Lần đọc CSV qua `python - <<'PY'` **FAIL exit 127** vì không có executable `python`; đã chuyển `python3`. Hai lệnh `python3 - <<'PY'` đọc schema/sample rồi audit toàn CSV/JSON/hashes đều exit 0. Lần tạo report bằng heredoc bị lỗi delimiter/SyntaxError; đã chuyển `apply_patch`, không sửa frozen inputs. Không chạy experiment/simulation hoặc source tests vì ngoài phạm vi.

Core audit dưới đây đã chạy **PASS, exit 0**; chỉ đọc năm inputs được phép. Kiểm tra file report tồn tại và khác rỗng cũng PASS.

```bash
python3 - <<'PY'
from pathlib import Path
from collections import Counter
from fractions import Fraction
import csv, hashlib, json
p = Path('results/lessons/l3r_4/screen')
e = json.loads(Path('notes/realism/envelope_v1.json').read_text())
t = json.loads((p/'receipt.json').read_text())
with (p/'labels.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))
ids = {r['id'] for r in rows}
coords = {r['coordinate'] for r in rows}
canon = {tuple(Fraction(x) for x in c.split('|')) for c in coords}
keys = Counter((r['id'], r['context'], r['f']) for r in rows)
groups = {(c['id'], str(f)) for c in e['contexts'] for f in e['f_sensitivity']}
expected = {(i,c,f) for i in ids for c,f in groups}
missing = {'tau_eff_s', *e['required']}
assert len(rows) == t['label_rows'] == 1296
assert len(ids) == t['ids'] == e['expected_ids'] == 216
assert len(coords) == len(canon) == t['distinct'] == e['expected_distinct'] == 210
assert set(keys) == expected and set(keys.values()) == {1}
assert all(len(c.split('|')) == 8 for c in coords)
assert all(set(r['missing'].split(';')) == missing and len(r['missing'].split(';')) == len(missing) for r in rows)
assert Counter(r['label'] for r in rows) == {'UNSOURCED':1296}
assert Counter(r['buffer_flag'] for r in rows) == {'UNSOURCED':1296}
assert Counter(r['actuation_flag'] for r in rows) == {'UNSOURCED':1296}
assert Counter(r['mode_oracle_flag'] for r in rows) == {'True':1296}
for c,f in sorted(groups):
    rs = [r for r in rows if (r['context'],r['f']) == (c,f)]
    assert len(rs) == 216 and len({r['coordinate'] for r in rs}) == 210
    assert dict(Counter(r['label'] for r in rs)) == t['counts'][c+':f='+f]
for s in ['notes/realism/envelope_v1.json','notes/realism/rules_v1.md','notes/realism/worksheet_v1.md']:
    assert hashlib.sha256(Path(s).read_bytes()).hexdigest() == t['freeze_hashes'][s]
assert hashlib.sha256((p/'labels.csv').read_bytes()).hexdigest() == t['outputs'][str(p/'labels.csv')]
print('PASS: 1296 labels; 216 IDs; 210 coordinates; six context/f groups; 4 hashes')
PY
```

Output duy nhất: `results/lessons/l3r_4/blind_review.md`. Không tạo log file, CSV/JSON metrics hoặc chart mới. Không đổi labels/envelope/rules; không nâng lượt review này thành human feedback, L-self hoặc author read-back.
