# P4-A1 — execution in progress, 31/10/2026

Người phụ trách: **Doan Van Tai**. AI thực hiện theo ủy quyền chat, không author self-writing/Understanding.

Code ec5fd62; diagnosis1a8d83a; delegated choices195672a. Preregs L44d1c2879,SV7c7c956,SUBbf767f2 trước mọi plant A1.842tests PASS88.76s,80targeted PASS2.90s. Không sửa code A1 sau freeze.

- L44: controlPASS; benchmark3PASS/1NOT_READY,0BUG; budget2.9291639CPUh/8 committed3cef246. Full HOLD:16/90 stage cases,8PASS/8NOT_READY; capSH8/72>10%,0BUG. Observedincludingbenchmark19cases(11PASS/8NR). No rho freeze; summarize refusal exit1 expected. Log results/lessons/p4_a1/execution/L44_A1/full.log.
- SV: controlPASS; benchmark4PASS; budget5.5399958CPUh/8 committed4bf82f8. Full497keys(449plus+48minus) đang chạy; log results/lessons/p4_a1/execution/L43_A1_SV/full.log.
- SUB: controlPASS; budget0.348CPUh committed6686b28; full5/5 complete,4PASS/1NOT_READY,0BUG. Native4/5ready,maxbundle164.404769CPU-s -> rulePROPOSE_KEEP_KAPPA_GE_1_20_FOR_FURTHER_COVERAGE. Summary and predeclared_decision saved.
- L44/ SV /SUB chạy độc lập theo schedule5efc715; maxworkers2/2/1, budgetCPU riêng. Mỗi run vẫn commit budget trước full.

Terminal active: SVfull88982 only. L44 and SUB sessions finished. Không khởi động lại schedule nếu đang chạy. Khi kết thúc PASS mới chạy `python -m experiments.P4_A1.summarize --run RUN`; HOLD không chọnrho/manifest. SUB cần commitbudget trước full.

Sau cảba: `PYTHONPATH=src:. .venv/bin/python notes/verification/p4_a1/verify_outputs.py` đọc artifact/rescore độc lập, không engine/boxcounts. Viết report/completion mới, không sửa completion/history cũ; kiểmhash/runreceipt, ghiexposure/forecastverdict/forking, cập nhật README/AGENTS,commit,pushoriginmain vàkiểmremoteSHA.

Cần báo rõ: NOT_READYcap>0 đổi selection sang READYsubset soDL104; rootcausecrossroute chưa xácnhận; kiểmdeltaL00 bổsung chỉdiagnostic (patchkhôngđưa fieldnày vào baseline_readiness). KhôngCF/R09R10outcomes/boxp-hat/carddecision/Gate4; G1/P0V10/L8/Understandinggiữ.
