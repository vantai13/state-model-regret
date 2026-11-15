**MISMATCH về dấu Γ**: H1–H4 và toàn bộ cờ eligible/pass đều khớp với Claude.

| Test | Độc lập = Claude | Verdict |
|---|---:|---|
| H1 | 195/196 | PASS |
| H2 | 192/192 | PASS |
| H3 | 183/192 | PASS |
| H4 | 191/196 | PASS |

Sai khác lớn nhất: **7.937.820,306464952** ở `Gamma` (đơn vị cost gốc), do hai quy ước ngược dấu. CARD §3 chưa định nghĩa Γ, nên chưa thể kết luận scorer sai. Ngoài Γ, sai khác lớn nhất **2,980232238769531×10⁻⁷ pp**, trong tolerance đối chiếu.

Đã chạy `python experiments/ext_validity/ev_te_rescore.py`: 7 self-checks PASS; kiểm đủ 1.464 dòng CSV; 122/122 raw blobs khớp commit `effcf40e`. Không commit, SSH hay sửa file có trước nhiệm vụ.

Ba file đã tạo:

- [Script](/home/vantai/state-model-regret/experiments/ext_validity/ev_te_rescore.py)
- [Số liệu và đối chiếu JSON](/home/vantai/state-model-regret/results/ext_validity/ev_te/rescore_independent.json)
- [Báo cáo chi tiết](/home/vantai/state-model-regret/results/ext_validity/ev_te/rescore_independent.md)

Không tạo log riêng; kết quả thực thi hiển thị trong phiên.