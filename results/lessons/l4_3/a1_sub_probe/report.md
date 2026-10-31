# SUB_PROBE — năm điểm coverage đã chạy đủ

Người phụ trách: **Doan Van Tai**. AI soạn và thực thi theo ủy quyền, không dự đoán độc lập của tác giả.
Prereg bf767f2, budget6686b28 trước full. Main(640,8), coarseK(320,8), coarsedt(640,4),5điểm cố định.

ControlPASS; benchmark1PASS/1NOT_READY; budget0.3480063CPUh/2. FullPASS về hoàn tất protocol (capNOT_READY=100%):4PASS/1NOT_READY,0BUG. Native readiness4/5; maxbundle164.404769CPU-s<=600. Unique evalCPU gồmcontrol425.712089s.

Áp nguyên văn luật trước run: đề xuất giữκ>=1/20 để kiểmcoverageL4.7 tiếp. Không chứng nhận toàn vùng, không SUB-effect/card confirmation; chưa combinedSUBrun/candidate_readiness.

XM2X000 Cref-dt0.3105391881% ởref4 giảm về0.0779178392% ởref8. Cả5probe cóCref-dt<.25%, nhưng P43_0595 vẫn NOT_READY do các kiểm khác, nêu dưới. Không suy bậc hội tụ chung từ một điểm.

Native readiness reasons P43_0595:

[
  "R1_K:cref=0.00008,max=0.00381,flips=[]",
  "R1_dt:cref=0.00056,max=0.00605,flips=[]",
  "arithmetic_width:(640, 8)",
  "arithmetic_width:(320, 8)",
  "arithmetic_width:(640, 4)"
]

Files: probe_metrics.csv đủ5điểm; predeclared_decision.json; native/15rows; controls/1row; full_summary.json; summary/case_ledger.csv và summary/summary.json. Logs: results/lessons/p4_a1/execution/SUB_PROBE/. Config và rule: experiments/P4_A1/runs/SUB_PROBE/.
Khôngsửa frozenA1,khôngrho/card/newCF/sealedoutcomes/boxcounts; G1/P0V10/L8/Understanding giữ.
