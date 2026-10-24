# SOB14 — partial EVPI

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI-only; chưa L-self.

Strong, Mark; Oakley, Jeremy E.; Brennan, Alan. *Estimating Multiparameter Partial
Expected Value of Perfect Information from a Probabilistic Sensitivity Analysis
Sample*. Medical Decision Making 34(3), 311–326 (issue 2014; online 18/11/2013).
[DOI 10.1177/0272989X13505910](https://doi.org/10.1177/0272989X13505910).
Peer-reviewed journal article; Crossref và White Rose được đối chiếu.
[Bản PDF](https://eprints.whiterose.ac.uk/id/eprint/78428/1/Estimating_Multiparameter.pdf).

Mức: **AI đọc full text (Method/Partial EVPI, Eqs1–4, published pp312–313;
PDF pages4–5), T**. Không đọc/đánh giá toàn bộ regression experiments.
Local `~/papers/l2_part_a/SOB14.pdf`, 18 PDF pages; checksum tại
`results/lessons/part_a/source_access.json`.

## Fact

Method Eq1 tối ưu expected net benefit trước khi biết input quan tâm; Eqs2–3
cho tối ưu sau khi biết Xi và trung bình qua Xi. Eq4 là hiệu hai giá trị.
Kỳ vọng bên trong dùng X−i conditional on Xi, giữ dependence giữa inputs.

## Claim

Abstract đề xuất cách ước lượng partial EVPI bằng regression từ PSA sample;
đây là claim của paper, không phải thuật toán được đánh giá trong repo.

## Evidence

Định nghĩa ở Method Eqs1–4 được đọc trực tiếp. Không tái lập case study hoặc
numerical comparison của paper và không dùng chúng để chứng nhận queue model.

## Inference của dự án

Ánh xạ d→a, Xi→x, X−i→w, NB→−C và joint law→D(x\|y)P(w\|x).
Tower property và đúng argmin cho GSgivenM1=EVPPI(x\|y); proof và G1–G4 ở
[T03 v2](../../theory/T03_primary_reading_start.md). Oracle không biết future.

## Giới hạn / ảnh hưởng tới claim

AI đề xuất PC1 DROP như contribution, giữ framing. Identity theo functional
không xóa khác biệt unknown parameter/hidden physical state. Chưa có record tác
giả tự đọc, đọc lại sau một ngày, hoặc kiểm kín sách. Kết quả 21.952 toy là kiểm
code của dự án, không phải kết quả paper.
