# Bản chính thức S11/R01/R34, hỗ trợ tự đọc và T03 (26/10/2026)

Người phụ trách: **Doan Van Tai**. Bạn tải 3 file theo đề nghị. Kết quả kiểm và phần hỗ trợ
cho ba việc của bạn (tự đọc, tự dẫn T03, tự chấm nhãn). Mức đọc thay bạn ghi AI-T.

## Kiểm 3 file

| Đề nghị | Nhận được | Kết luận |
|---|---|---|
| S11 IEEE TIT 72(4) 2026 | Đúng, 40 trang | §III/Eq10, §VII-D/Theorem 9/Cor 2/Appendix O **khớp** arXiv v3 |
| R01 Annals OR 2010 | eCommons "6-2010" = bìa + **TR 2006** (trùng 100%) | Số mục journal **chưa kiểm** — cần bản Springer |
| R34 IEEE TAC 1995 | **CDC 1992**, 2 trang scan | Đọc được ý chính (JSEQ tối ưu k=1, không k≥2); cần bản TAC |

## Hỗ trợ cho phần bạn tự làm

- [Gói tự đọc](../../../../notes/literature/author_reading_pack.md): trang cần mở + câu tự trả lời cho WM26, R02, R04, P11, P02, S11, P12.
- [Ví dụ tính tay T03](../../../../notes/theory/T03_worked_example.md): G_S\|M1 = EVPPI = 1/9, G_M\|S1 = E[VSS] = 2/9, Γ = 1/9; không hòa; kiểm identity trên 30.000 tổ hợp tham số.
- Rà nhãn tạm với bằng chứng mới: **không đổi** ([prior_boundary](../../../../notes/literature/prior_boundary.md), mục cuối).

## Commands

```bash
.venv/bin/python -I -B experiments/lessons/t03_worked_example.py
.venv/bin/python -I -B experiments/lessons/l2_9_journal_check_records.py
.venv/bin/python -B tools/paper_library/build_notes.py
.venv/bin/python -I -B experiments/lessons/audit_l2_9_journal_check.py
.venv/bin/python -m pytest -q
```

Kết quả thực: `audit_l2_9_journal_check.py` **PASS** ([verification.json](verification.json)):
3 file đúng hash/số trang; S11 journal khớp số mục; R01 file = TR 2006; R34 file = CDC 1992;
ví dụ T03 tính lại đúng, không hòa; catalog chỉ đổi S11/R01/R34; 23/23 mức tác giả, 7 ô nhãn
tác giả và 7 ô L-self vẫn trống. Excel PASS (23 nguồn).

## Còn cần bạn

1. Tải **R01 bản Springer** ([doi:10.1007/s10479-009-0603-7](https://doi.org/10.1007/s10479-009-0603-7)) và **R34 bản IEEE TAC 1995** ([doi:10.1109/9.402238](https://doi.org/10.1109/9.402238)).
2. Tự đọc theo gói, tự dẫn T03, tự chấm cột `⟨tác giả chấm⟩` — rồi nhắn lời của bạn để ghi record.
