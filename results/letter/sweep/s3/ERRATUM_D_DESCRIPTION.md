# Erratum (Claude, 21/11/2026): mô tả D trong thẻ S3
Thẻ CARD_S3.md (đã khóa, không sửa) mô tả D_ŝ là "share bất đồng luật tĩnh–hybrid". Sai về lời: theo `analyze_s2.py` (định nghĩa mà thẻ dẫn và
scorer khóa dùng), D = D_fresh + D_stale của Corollary 1 — hai xác suất đuôi π0{|Δ̂|≥h|ŝ|} và P{|E[Δ̂|Y]|≥h|ŝ|}, trung bình trên τ/T_int ∈ {0,3; 1; 3};
đây là cận trên của tỉ lệ bất đồng thật (assert trong analyze_s2.py). Ngưỡng 0,28, code, lock, outcome và verdict PASS không đổi. Mô tả sai đã lọt vào
câu S3 của letter v10.5 ("departure shares") và tin nhắn cho tác giả; sửa ở v10.6 (letter_smr_v10) thành "D(h) of Corollary 1 averaged over ages".
Codex phát hiện qua ghi chú ledger S3.
