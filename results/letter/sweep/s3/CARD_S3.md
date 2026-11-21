# Thẻ S3 — xác nhận vùng lợi ích của hybrid trên CTMC mới (Claude điều phối, 21/11/2026)

Người phụ trách: Doan Van Tai. AI soạn theo ủy quyền thử nghiệm của tác giả (21/11: "tùy bạn thiết kế … linh hoạt"); không phải tác giả tự dự đoán.
Trạng thái: viết TRƯỚC mọi outcome S3. Khóa bằng lock.json (hash thẻ, code, config, seeds) trước truth run; một lần chạy, không retry/resume.

## Đã thấy (exposure)
- Toàn bộ S1-A (1000 regime Sobol, commit c34c9ed32) và S2 (results/letter/sweep/ctmc/s2/): d*=0,28 chọn trên 499 ID lẻ, 501 ID chẵn đã xem
  (vùng 99/501, tĩnh 2,43% → hybrid 0,32% C_ref, Δ 2,11 [1,28; 2,94]). h=T_int chọn sau khám phá. S0, X-CTMC, W1b đã thấy.
- Định lượng "tệ hơn đáng kể" của cổng S2 được viết sau khi xem S2: với mean ba tuổi không bin nào ≤ −0,05 điểm; theo từng tuổi 3 bin có mean ≤ −0,05
  nhưng mọi CI95% cắt 0. Cổng S2 coi là GO theo mọi cách định lượng này; ghi rõ đây là định lượng post hoc.

## Thiết kế
- Mô hình, miền, sampler, sàng tài nguyên, estimator ŝ (MMPP/M/1 fallback, bản ghi 300 T_int), lưới h × τ × luật: y nguyên S1-A
  (`experiments/letter/sweep_ctmc.py`), chỉ đổi **Sobol scramble seed và record seeds** sang giá trị mới, khác S1-A/pilot, ghi vào lock trước khi chạy.
- N: lấy **600 regime đủ điều kiện đầu tiên** theo thứ tự Sobol mới (sàng tài nguyên như S1-A, quyết định trước outcome). Regime INVALID estimator
  vẫn nằm trong mẫu số và báo riêng.
- Δ = regret(luật tĩnh ŝ) − regret(hybrid ŝ), phía fresh, cùng C_ref, điểm % C_ref; dương là hybrid có lợi. Tính đúng như `analyze_s2.py`.
- Vùng R = {D_ŝ ≥ 0,28}, D_ŝ đúng định nghĩa H-C trong `analyze_s2.py` (trung bình đều trên τ/T_int ∈ {0,3; 1; 3} của D_fresh,ŝ + D_stale,ŝ,τ;
  share bất đồng luật tĩnh–hybrid, không cần truth). Không đổi d*, h hay estimator sau S3.

## Phép thử (primary, h = T_int, fresh, ŝ)
- **T1 phủ:** |R| / N ≥ 10%.
- **T2 lợi trong R:** mean Δ trong R ≥ 0,1 điểm VÀ cận dưới CI95% (Student t trên regime) > 0.
- **T3 không hại ngoài R:** cận dưới CI95% của mean Δ ngoài R ≥ −0,05 điểm.
- **S3 PASS** iff T1, T2, T3 cùng PASS. |R| < 5 hoặc ngoài R < 5 regime ⇒ phép thử tương ứng NOT_EVALUABLE ⇒ S3 không PASS.
- Báo kèm (không phải test): đếm regime Δ ≤ −0,05 và ≤ −0,1 (trong/ngoài R), số INVALID/fallback, lợi tuyệt đối packet·s,
  hai ứng viên phụ h = 0,7 T (d* 0,32) và 1,5 T (d* 0,21), bảng mọi h, phía stale.

## Dự báo của AI (không phải test, ghi để có thể sai)
Phủ 15–25%; Δ trong R 1,2–2,5 điểm; mean Δ ngoài R 0,02–0,15; S3 PASS với xác suất chủ quan khoảng 0,8.

## Luật đưa vào paper (chốt trước khi chạy; mọi sửa paper vẫn đưa tác giả xem trước)
- PASS: thêm một câu vào IV-B4 (Regret of the Corrected Twin), dạng: trên N regime CTMC mới, ở X% regime mà bản hiệu chỉnh rời luật tĩnh
  ở ít nhất 28% quyết định (đo được không cần truth), regret fresh tại h = T_int giảm từ a% xuống b% C_ref; ngoài vùng không tệ hơn quá 0,05 điểm.
  Số đi qua ledger.
- T1 hoặc T2 FAIL (không xác nhận vùng): paper không claim vùng; giữ nguyên văn hiện tại.
- T3 FAIL (hybrid hại ngoài R trên regime mới): mâu thuẫn câu "keeps regret low" ⇒ phải báo trong IV-B4 một câu, kèm số.

## Quy trình
Codex: code/test/lock (không chạy truth). Claude: GCP (n2-highcpu-32, revert n2-custom-12-49152, TERMINATED), rsync + checksum, commit raw trước khi chấm.
Chấm bằng scorer đã khóa; Codex chấm lại độc lập bằng script không import scorer.
