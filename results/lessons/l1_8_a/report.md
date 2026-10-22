# L1.8 Part A — từ giây tới slot

Người thực hiện: **Doan Van Tai** · 2026-10-22T19:04:49.040696+07:00.

Chỉ triển khai PartA: conversion module,R2 candidate,thẻ hai neo và deterministic verification. Không đổi contract-v0; chưa khóa Δt cuối hoặc contract-v1,không chạy PartsB–E/Phase3 A01.

## Hai thẻ đổi đơn vị

| Neo | t_packet | Δt ứng viên | c / nền trước | Tuổi slots → giây | Sai số tuổi | H | Tdrain pre B | Tdrain post B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| a | 0.012ms | 0.12ms | 10 / 8 packet/slot | 42 → 0.00504s | 0.8% | 50 | 0.006s | chưa khai báo |
| b | 1.2ms | 12ms | 10 / 8 packet/slot | 17 → 0.204s | 2% | 50 | 0.6s | 1.2s |

a:1Gb/s,b:10Mb/s,1500byte,qB0=100,rho_pre=.8. Tuổi+act5ms/.2s,h6ms/.6s là minh hoạ,không là end-to-end measurement. T_mode của a chưa khai báo. b:T_mode=.1s chưa có nguồn,rho_post=.9 là scenario giả định. Không có full ON/OFF on/off rates hoặc D tại các neo; aggregate rho chưa xác định law. q0=100 dùng cho hai diagnostic pre/post,không phải một episode đã tiến qua prehistory.

b: ratio pre/age từ3 xuống **2.941176**,zone①→② sau rounding. h/Tpost=**0.5**. Constant-load fluid rho_post=.9 cho **50 packet** còn lại sau .6s; đây không là E[q] của ON/OFF queue. Không dùng ratio hoặc zone làm chứng minh gain dương.

## R1 và R2

R2 được dùng trong draft:lambda=exp(-2dt/T),p_stay=(1+lambda)/2,giữ correlation qua tuổi vật lý. R1 giữ mean sampled run duration nhưng không semigroup. Quyết định research cuối cùng ở thẻ PartD/E.

| Luật | Δt(ms) | Age slots | P leave | Corr tại204ms | Mean sampled run(ms) | Semigroup residual |
|---|---:|---:|---:|---:|---:|---:|
| R1 | 12 | 17 | 0.120000000 | 0.009415233 | 100.000000 | 0.0072 |
| R2 | 12 | 17 | 0.106686069 | 0.016907466 | 112.479540 | 0 |
| R1 | 6 | 34 | 0.060000000 | 0.012954208 | 100.000000 | 0.0018 |
| R2 | 6 | 34 | 0.056539782 | 0.016907466 | 106.119971 | 2.22e-16 |
| R1 | 3 | 68 | 0.030000000 | 0.014883122 | 100.000000 | 0.00045 |
| R2 | 3 | 68 | 0.029117733 | 0.016907466 | 103.029998 | 0 |

R2 correlation exact formula exp(−4.08),stationary ON1/2; mean sampled run≈112.48ms ở dt12ms so holding100ms vì bỏ các lần lật rồi quay lại. R1 correlation thay đổi theo dt; đó là negative control cố ý,không là test failure. Giữ leave=.1 khi đổi dt10→5ms làm T_R1 100→50ms,T_R2≈89.628→44.814ms.

lambda0 (canonical p=s1/2) không có finite positive CTMC holding time. lambda1 có embedding suy biến Q0/holding vô hạn; inverse helper từ chối vì ngoài finite-positive scope, không gọi nó là không nhúng được tuyệt đối. CTMC skeleton không làm arrivals tích phân trong slot chính xác.

## E1: diện tích backlog và điểm cuối

| Example | Δt | D13 | Fluid area | Error |
|---|---:|---:|---:|---:|
| drain | 1 | 0 | 1 | -1 |
| drain | 1/2 | 1/2 | 1 | -1/2 |
| drain | 1/4 | 3/4 | 1 | -1/4 |
| drain | 1/8 | 7/8 | 1 | -1/8 |
| rise | 1 | 2 | 1 | 1 |
| rise | 1/2 | 3/2 | 1 | 1/2 |
| rise | 1/4 | 5/4 | 1 | 1/4 |
| rise | 1/8 | 9/8 | 1 | 1/8 |

Đơn vị packet·s,interval1s. Queue drain q0=2,rate1,service3;rise q0=0,rate5,service3. Constant rate trong slot cho đúng endpoint backlog với plantL1.2. D13 sai diện tích,hội tụ về1 ở hai hướng.

**Làm rõ công thức crossing:** nếu không chạm0 bên trong slot,error=dt(QH−Q0)/2 chính xác. Nếu q0=1,net−2,dt1,fluidarea1/4,D13=0,error−1/4,boundaryterm−1/2. **Correction=+1/4**,không phải số hạng âm bổ sung so với telescoping. Tổng error của slot drain vẫn âm. [boundary_grid.csv](boundary_grid.csv) kiểm96 intervals,0 vi phạm.

Canonical xd,all-off,H2,dt1:Stay D13/fluid4/4,Switch0/1;gap−4 so−3. Đây là branch diagnostic,không thay expected J hay objective của các lesson cũ. Cumulative q=(10−2t)+ cho area25 ở h10 và20;time-average2.5 và1.25. Không suy GS cumulative về0 khi tăng h từ ví dụ time-average.

## E3 và verification

900 round-trip cases có0 vi phạm |error|≤dt/2; nearest/ties-to-even được ghi rõ. Default reject duration tròn thành0slot; explicit allow_zero chỉ dành cho duration thật0 (D8 age0). anchor_refinements.csv ghi12/6/3ms và.12/.06/.03ms,cùng physical durations; ratio thay đổi chỉ qua rounding,không gọi đây là PartB contrast acceptance.

- lesson: **4/4 PASS**,log`lesson.txt`,JUnit`lesson.xml`.
- boundaries: **10/10 PASS**,log`boundaries.txt`,JUnit`boundaries.xml`.
- full_suite: **111/111 PASS**,log`full_suite.txt`,JUnit`full_suite.xml`.

Preflight13/13 PASS trước runner; sau đó thêm1 test rescale candidate coordinates. Bốn core từ bài,10 test bổ sung; suite trước97 nên tổng111. Bất biến contrast chuẩn hoá sau rescale vẫn chờ Phase3/PartB,Cref chưa chọn.

SNMP P=W30s,L0:tau_eff30s,Tpre/age=.02. Đây là rate từ counter,không đáp ứng backlog observation D8; đổi đơn vị không sửa schema. Self-check100Mb/s,c10,T50ms lưu dt1.2ms và hai leave probabilities trong results; đây là worked reference,không là bài kín sách.

## Giới hạn và nguồn

Con số GS.930→.534 (~43%),Gamma+.078 chỉ do tài liệu trích PHASE_1. Không có full configuration/protocol ở repo nên chưa tái lập trong PartA; không báo chúng là số chạy mới và không gán phần43% choE1 hayE2. Weak mode correlation không tự chứng minh mode-visibility gain chiếm ưu thế.

[Ward Whitt,CTMC notes §2–3](https://www.columbia.edu/~ww2040/3106F11/CTMCchapter121906.pdf) hỗ trợ CTMC có holding mũ và Chapman–Kolmogorov semigroup. R2 đối xứng được dẫn từ ODE trong spec và kiểm bằng số. Đây không xác nhận traffic mạng thật tuân law đó. Nguồn Willinger1997 mà bài nhớ lại: DOI10.1109/90.554723;publisher chặn truy cập (IEEE cần JavaScript,ACM403),chưa kiểm nội dung primary và không dùng nó xác nhận AA2 workload.

Mô hình gốc đề xuất là reflected fluid queue điều biến CTMC. Δt/2 chỉ kiểm sai số với mô hình đó,chưa validate packet network; còn E2 mode changes nội slot chưa được mô phỏng trong PartA. Code không sửaD13 thành fluid area. Chưa chốt Δt,H,lướiD,Cref,epsilon,confirmation hoặccontractv1. G1,V3/V10/V11,HOLDPhase4 giữ nguyên; bài tự làm và legacy debt chưa được ghi Đạt.

## File và tái chạy

```bash
.venv/bin/python -m experiments.lessons.run_l1_8_a
.venv/bin/python -m experiments.lessons.run_l1_8_a --output-dir /tmp/l1_8_a-rerun
```

| Artifact | Nội dung |
|---|---|
| [config.json](config.json),[results.json](results.json) | Inputs,source/input hashes,exact và float metrics,actual commands |
| [anchor_cards.csv](anchor_cards.csv),[anchor_refinements.csv](anchor_refinements.csv) | Hai thẻ và rounding theo dt |
| [persistence_comparison.csv](persistence_comparison.csv),[fixed_probability_mistake.csv](fixed_probability_mistake.csv) | R1/R2,correlation,run duration,semigroup |
| [fluid_convergence.csv](fluid_convergence.csv),[fluid_paths.csv](fluid_paths.csv),[boundary_grid.csv](boundary_grid.csv) | E1 và crossing correction |
| [canonical_all_off.csv](canonical_all_off.csv),[cumulative_vs_average.csv](cumulative_vs_average.csv),[round_trip_grid.csv](round_trip_grid.csv) | Branch gap,cumulative,900round trips |
| [slot_and_persistence.png](slot_and_persistence.png) | Hình từ các số đã tính |
| lesson.txt,boundaries.txt,full_suite.txt,*.xml,run_output.txt | Logs và JUnit thật |
| [artifact_checks.json](artifact_checks.json),[artifact_manifest.json](artifact_manifest.json) | Đọc lại CSV,hashes,manifest |

Source:experiments/lessons/l1_8_slots.py,l1_8_reference.py,run_l1_8_a.py; tests/test_l1_8_slots.py,test_l1_8_boundaries.py. Card/spec tại notes/lessons/L1.8A_experiment_card.md vàL1.8A_slot_model_spec.md. Python3.14.5;wall time7.738s. Không RNG/seed,không CI lấy mẫu.
