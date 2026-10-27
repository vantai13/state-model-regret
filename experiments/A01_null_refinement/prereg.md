# A01 — Null control, ô kiểm âm và chọn dt cuối — PREREG FROZEN

Người phụ trách: **Doan Van Tai** · 27/10/2026 · contract-v1.2.
AI triển khai theo hai lesson L3.4 được cung cấp; không nhận đây là tác giả tự viết
hoặc dự đoán kín sách. Câu hỏi: (1) implementation cho đúng các đáp án kiểm đã biết?
(2) mức dt nào đạt D1 trong ngân sách đã khóa?

## Khóa và thứ tự

A03 card commit `b05ed70bd4e93544bccefc975cdc452ad40d1380`, SHA256
`14021a83c6d45a3fbeba6b7cbe27e9c8c0e572734557af1598cf79b819f34639`,
receipt `bcd1941a5a00718d68886866ba667b9fa2d6ea97`, tag `a03-card-v1`.
Engine nền trước sửa direct-positive sum: commit `f72306f17ce216cb2c879efe2f207dcaa1898228`.
Engine A01/config và toàn bộ source hashes được ghi trong **receipt commit kế tiếp**;
prereg có commit riêng trước receipt và mọi lần chạy grid của A01. Manifest run
ghi cả hai commit/hash, code/config, phiên bản thư viện/compiler. Không tự ghi hash
commit chứa chính nó; không sửa card, không amend/rebase/force.

Nguồn: `results/lessons/l3_4/lesson_part1.txt`, `lesson_part2.txt`; lịch sử L3.2
300 tests/11 mutant, L3.3 324 tests/11 mutant. Trước run kiểm lại engine/direct sums,
selector trên synthetic fixtures và full suite. Bug controls được sửa rồi commit
trước retry; lưu nguyên failed run và lý do. Không sửa prereg/dung sai theo outcome.

## Part 0 — chỉ xuất p_sw

M01/M09/M22 × ref1/2/4. `reproduce_psw` dựng D bằng adapter hiện hành, native gap
và certificate, giữ arithmetic/bounds convention float64-first của screen lịch sử.
API chỉ trả p_low/p_high; CSV chỉ cell/ref/p_low/p_high/match. Đòi **bit-for-bit**
hai đầu khoảng với `grid_v1_2.json`; mismatch STOP trước cost/PartA. Không log gap,
mean gap, J hoặc M0. Kernel shared nên đây không là chứng minh độc lập native DP.
Phần cost engine longdouble có cận khác screen; không đòi bitwise trùng khoảng
khác precision. PartA/B mới expose ledger của calibration, và kiểm physics đã có
Fraction references/golden/native tests L3.2.

## Part A — ref1 và ref2, mọi bắt buộc PASS mới chạy B

| Control | Dựng | Bắt buộc / phạm vi | Bug bắt được |
|---|---|---|---|
| C1 | M01/M09/M22 đặt u=0, **dựng lại D pre-Stay**; y vật lý giữ nguyên | Δ,Δhat≡0; mọi L bằng nhau; 6G==0; xác minh law A thay đổi | action bookkeeping/pre-load |
| C2 | S0 nhận x, belief point; M0/M1 quyết định theo state | GS=GS_M1=Γ=0, GM=GM_S1; bảo toàn GM_S1 gốc | thông tin State |
| C2prime | D22 biết backlog giấu mode | V quan sát, không yêu cầu0 | nhầm backlog với full state |
| C3 | cả hai model quyết theo Δhat, **chấm true Δ** | GM=GM_S1=Γ=0; GS gốc giữ nguyên | model switch/input |
| C4 | toy rational độc lập enumerate p·min(Jst,Jsw), so cut oracle; kiểm tie action riêng | L11=independent Lstar, switch mass đúng; exact tie Stay | aggregation/oracle/tie |
| C5 | N01,N02 SD; N03,N04,P01 conservation | **sáu G ==0 chính xác**, không clamp/tolerance | certificate/gap signs |
| C6 | W01,S01,P02 WD | **GS_M1==0 chính xác**; GM,GS chỉ quan sát | WD hiểu sai là all-zero |

Direct EΔ+ và EΔ− đều dùng strict cuts; GS_M1=min(EΔ+,EΔ−), không lấy hiệu
hai L để đòi structural zero. Đây là biểu diễn tương đương D19/T01, không đổi
estimand. C2/C3 control paths chọn policy từng pipeline rồi chấm true costs;
factorial differences group theo policies bằng nhau, không chèn số0 theo nhãn cell.
**C3 pipeline11 sau thay model không là D15 true oracle**; chỉ yêu cầu identities
control, không yêu cầu regret gốc pipeline11 bằng0. C4 độc lập đường ghép, không
độc lập physical kernel; oracle cost không phát hiện tie action nên kiểm riêng.

Các đính chính lesson: W01/P02 có p_sw<1; S01 p_sw=1, không phải cả3<1.
Hai số khác0 giống bit pattern vẫn có thể trừ ra0; điều cần giữ là bảo đảm
zero theo cấu trúc, không mệnh đề mọi phép trừ nonzero đều không thể exact0.
E9 random arrivals một slot nằm ngoài D7 current-mode-known, không đổi D7.
Không có dự đoán GM của WD do tác giả viết; bài khuyến nghị không bắt buộc.

## Part B — D1 và năm làm rõ thủ tục (DL-050)

Chỉ M01/M09/M22 × **m=1,2,4,8,16**, toàn bộ mức, không dừng cặp PASS đầu.
Giữ h=8s, rates, μ10 packet/s, age1s, kappa, u, **y coarse vật lý**. Mỗi mức
dt=1/(120m)s, H=960m; dựng lại D/prior; Cref=Lstar của đúng mức đó.
Không re-anchor lambdaA, không tính lại quantile y. Không Monte Carlo/seed/CI.
Budget inherited ≤2e11 updates, ≤4GiB mỗi cell/mức; không mở thêm mức sau run.

(a) Pair reference=min(Cref_coarse,Cref_fine). D1 max trên6 contrasts ≤.0025·C,
không sign flip có max magnitude>.005·C. **Chứng nhận bảo thủ** dùng lower bound C
và |Gfine−Gcoarse|+e_coarse+e_fine; nominal cũng báo riêng. Đây là áp numeric
enclosures trước khi kết luận, không tăng dung sai. Missing bounds/precision →HOLD.

(b) Chọn cặp thô nhất mà **mọi cặp kề từ nó đến ref16 đều PASS**; báo endpoint
mịn hơn của cặp đó. Không gọi finite-level stability là continuum convergence.

(c) dt chung là mức mịn nhất trong ba picks; một ô HOLD thì toàn A01 HOLD.

(d) Dao động a00 không tự tạo ngoại lệ: nếu làm suffix không có cặp hợp lệ thì
HOLD, kèm EΔhat/EΔ/actions và fingerprint; không đổi D1 hoặc calibration cells.

(e) Cặp mịn nhất không đạt trong ngân sách →HOLD. Không nới dung sai, không thêm
ref32. Muốn thay đổi phải có quyết định nghiên cứu mới riêng trước thêm outcomes.

Costs tính native **longdouble từ đầu**, ghi mantissa/compiler. Mỗi mức đòi
e_num cho tất cả contrast ≤.0025·Cref_lower; unresolved mass oracle/M0/D22 mỗi
loại ≤.01 và a00 certified. Longdouble vẫn không đạt →HOLD, không epsilon tie.
Pair kiểm precision ở cả hai mức. Cận conditional trên input/kernel bounds,
không CI và không chứng minh formal đầy đủ các cận vật lý.

Ghi 6G,Lstar,EΔ,EΔhat,a00/a01, e_num, unresolved, wall time ở CSV/JSON;
rho/Richardson mọi triplet/pair chỉ diagnostics. 0/0 ghi undefined, n/0 infinite.
Fingerprint khi a00 flip: nếu chỉ L00 nhảy J thì GS/GM/GSM +J, Γ−J, còn
GS_M1/GM_S1 không đổi; giữa mức có D/physics drift nên không áp như equality
zero-drift. Không tự gán một jump là bug hay discontinuity nếu thiếu kiểm.

## Exposure / hành động sau chạy

C2/C3 và baseline PartA expose một phần/toàn ledger M01/M09/M22 ref1/2;
PartB expose contrast/gap expectations của ba ô ở **mọi mức1–16**. Ghi chính
xác những mức đã chạy kể cả retry. Chúng vẫn được chấm ở A04 theo card A03 tại
dt cuối, nhưng ngoài card chỉ là discovery. Không outcome/D held-out mới,
không A04 hoặc chấm P2/P3/P5/P6 trong A01, không chọn H1/null.

Control fail →STOP, sửa implementation/control, giữ failed artifacts rồi retry;
không chạy B trước controls PASS. B fail →DL HOLD; PASS →DL dt cuối và A04 cần
kiểm cặp 2·dt_final/dt_final riêng mỗi cell. V9 hiện **chưa gửi, A04 chờ**;
A01 PASS không tự đóng V9/L8/P0-V10/T05 author-writing hoặc Phase4.
