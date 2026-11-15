**MATCH — không có mismatch (`[]`).**

Đã tính độc lập từ raw inputs, không đọc/import hai module bị cấm, không sửa file hiện hữu, không commit/SSH.

- Manifest: **960/960 file khớp SHA-256**, không thiếu/thừa.
- Mỗi arm: **320/320 outputs**, status `OK`, không INCONCLUSIVE.
- **769 hàng**, **12.842 trường** đối chiếu khớp; số thực dùng tolerance relative `1e-12`.

| Verdict | Kết quả đo |
|---|---|
| H1 **FAIL** | Increment share 71,2329%, n=73 |
| H2 **PASS** | Share 54,2169%, n=83; median ratio 0,196338 |
| L/H band **WORKS** | 100% / 99,0476% |
| H3 **LOOPING** | Theo reading table |
| D6-C **FAIL** | 279/320 = 87,1875% |
| D6-L **PASS** | 314/320 = 98,125% |
| D6-H **PASS** | 312/320 = 97,5% |

Các chỗ cần chọn cách đọc: D6 dùng công thức explicit trong brief và mọi cặp plug-in, không áp filter nowcast; thống kê gộp theo hàng, noise filter chỉ báo cáo phụ. Ratio khi mẫu số 0 được coi undefined; trường hợp này không xuất hiện. Quy tắc ưu tiên INCONCLUSIVE/NOT_EVALUABLE không ảnh hưởng dữ liệu hiện tại. H3 đọc nguyên bảng, chưa phải bằng chứng nhân quả độc lập.

Đã chạy `python results/ext_validity/ev_d4c/rescore_independent.py` sau khi source hai environment: **exit 0**. Kiểm tra artifact/imports và `git diff --exit-code`: **PASS**.

File tạo mới: [script](/home/vantai/state-model-regret/results/ext_validity/ev_d4c/rescore_independent.py), [JSON đầy đủ](/home/vantai/state-model-regret/results/ext_validity/ev_d4c/rescore_independent.json). Không tạo log hoặc biểu đồ riêng.