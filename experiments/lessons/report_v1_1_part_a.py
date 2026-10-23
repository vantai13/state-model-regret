"""Doan Van Tai — assemble measured Part A results and a standalone plot."""
from experiments.lessons.v1_1_a_common import *
import hashlib,platform
import numpy as np,scipy,mpmath


def run():
    out=ROOT/'results/lessons/v1_1_a6'
    if (out/'results.json').exists():raise SystemExit('Preserve existing report')
    readiness=json.loads((out/'readiness.json').read_text())
    prior=[]
    for suffix in ('','_redesign'):prior+=list(csv.DictReader((ROOT/f'results/lessons/v1_1_a1{suffix}/certificates.csv').open()))
    initial=list(csv.DictReader((ROOT/'results/lessons/v1_1_a4/screen.csv').open()))
    final=list(csv.DictReader((ROOT/'results/lessons/v1_1_a4_redesign/screen.csv').open()))
    comparison=[]
    for i in range(1,23):
        id=f'M{i:02}';a=next(r for r in initial if r['cell']==id and r['refinement']=='2');b=next(r for r in final if r['cell']==id and r['refinement']=='2')
        comparison.append(dict(cell=id,initial_low=a['p_low'],initial_high=a['p_high'],initial_class=a['classification'],
            redesign_low=b['p_low'],redesign_high=b['p_high'],redesign_class=b['classification']))
    csvwrite(out/'screen_comparison.csv',comparison)
    results=dict(author='Doan Van Tai',date='2026-10-23',status='HOLD_NARROW_REQUIRED',
        baseline_tests=165,full_tests=177,new_tests=12,
        original_stationary_certificates=20,redesign_stationary_certificates=20,v1_reference_comparisons=10,
        max_law_error=readiness['max_law_error'],max_posterior_error=readiness['max_posterior_error'],
        max_certificate_wall_s=max(float(r['wall_s']) for r in prior),max_certificate_peak_RSS_bytes=max(int(r['peak_rss_bytes']) for r in prior),
        initial_in=8,redesign_in=11,required_in=15,main_count=22,cells_kept=34,redesign_count=1,
        screen_rows=88,unresolved_mass_max=readiness['unresolved_mass_max'],max_p_interval_width=readiness['max_p_interval_width'],
        screen_total_wall_s=sum(float(r['wall_s']) for r in initial+final),max_screen_wall_s=max(float(r['wall_s']) for r in initial+final),
        max_screen_peak_RSS_bytes=max(int(r['peak_rss_bytes']) for r in initial+final),
        consistency={s:sum(r['status']==s for r in readiness['checks']) for s in ('PASS','PARTIAL','FAIL')},
        calibration=[],formal_contract_promoted=False,new_tag=False,headsup_sent=False,network_validation=False,
        scientific_result='Two candidate designs fail the declared decision-relevance screen; no hypothesis test or contrasts run')
    write(out/'results.json',results)
    attachment=Path('/home/vantai/.codex/attachments/0598b6c8-38d7-41de-ac52-0e5551539548/Pasted text.txt')
    source=['src/smr/stationary_spectral.py','src/smr/stationary_v2.py','src/smr/gap_screen.py','src/smr/native/idle_backward.cpp',
        'experiments/lessons/run_v1_1_a1.py','experiments/lessons/run_v1_1_a1_redesign.py','experiments/lessons/run_v1_1_a2.py',
        'experiments/lessons/run_v1_1_a4.py','experiments/lessons/run_v1_1_a5.py','tests/test_stationary_spectral.py','tests/test_gap_screen.py',
        'notes/verification/verify_v1_1_part_a.py','notes/verification/verify_v1_1_factorized_law.py','experiments/lessons/report_v1_1_part_a.py']
    write(out/'config.json',dict(author='Doan Van Tai',input_sha256=hashlib.sha256(attachment.read_bytes()).hexdigest(),
        source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source},
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,mpmath=mpmath.__version__,longdouble_eps=str(np.finfo(np.longdouble).eps)),
        physical_config=dict(mu_packet_per_s=10,age_s=1,dt_s=['1/120','1/240'],A_background_amplitude=6,B_OFF=2,B_ON=14,
            lambdaA_initial=['6.5','7.5','8.5'],lambdaA_redesign=['7','7.2','8.1'],kappa=['.3','1','3'],eta_core=.5,eta_spoke=.9),
        prior_law_error_target=1e-10,posterior_error_target=1e-8,tail_target_spectral=1e-36,uncertain_mass_alarm=.01,
        p_acceptance=[.1,.9],required_main_in=15,redesign_limit=1,memory_limit_bytes=4*1024**3,seconds_per_solver_or_action=1200,
        A01_updates_limit=2e11,seed=None,RNG_draws=0,margin_or_Lstar_outputs=False))
    plot(out,comparison,prior)
    lines=['# Phần A — kết quả thực chạy','', 'Người phụ trách: **Doan Van Tai** ·23/10/2026.','',
        '**HOLD / NARROW REQUIRED.** Solver được gỡ nút thắt; B4 không đạt sau đúng một redesign. Không formal freeze/tagv1.1.','',
        '| Phép kiểm | Kết quả |','|---|---|',
        '| Baseline → full suite |165 → **177/177 PASS**;12 tests mới|',
        '| Stationary original / redesign |**20/20 +20/20 PASS** ởdt1/120 và1/240|',
        '| Đối chiếu solver v1 |10/10 PASS; allowance array evaluation báo riêng|',
        f"| Max law error / posterior error |{results['max_law_error']:.6g} / {results['max_posterior_error']:.6g}|",
        f"| Prior max wall / peak RSS |{results['max_certificate_wall_s']:.3f}s / {results['max_certificate_peak_RSS_bytes']/2**20:.2f}MiB; cap1200s/4096MiB|",
        '| Candidate/D/ĐK1 |28ô+6reserve mỗi thiết kế;272 queue-support artifacts audit; không Cartesian product|',
        '| B3 |88 sign-only rows; unresolved mass0; reserve không screen|',
        f"| Max p_sw interval width |{results['max_p_interval_width']:.6g}|",
        '| B4 acceptance |**8/22 →11/22**, yêu cầu**15/22**; không ô bị xóa|',
        f"| Screen total wall / max per row / peak RSS |{results['screen_total_wall_s']:.3f}s / {results['max_screen_wall_s']:.3f}s / {results['max_screen_peak_RSS_bytes']/2**20:.2f}MiB|",
        '| Sáu consistency checks |4PASS,1PARTIAL(full source),1FAIL(grid/calibration); numeric constraintsPASS|','',
        'Conditions: μ10packet/s; age1s; A backgroundλA±6, B2/14; κ.3/1/3; ηcore.5/spoke.9. Quantile coarse defines physical observation; finer prior recomputed at same observation, Hfine=2Hcoarse. No Monte Carlo/seed/CI lấy mẫu; đây là numeric bounds của law và p_sw.','',
        'Sparse longdouble trials được giữ, gồm law bound2.293e−10 vượt1e−10. Spectral approximation dùng interval balance, boundary, normalization, independent tail và Bellman return bound. Không gọi finite capped chain exact infinite law.','',
        'Native weighted-idle DP dùng integer lattice và zero-tail proof, không clip.6 tests mới kiểm native/Fraction, golden(+2,−1.5,+1.5,−3), hai Markov queues, sorted p_sw/brute force và syntheticH1000.6 tests stationary gồm closed-form/invalid coefficient/roundoff guard/large law. Native subtraction mutant lọt test dyadic đầu; đã giữ record và thêm keep.97 trong cùng conservation test: mutantFAIL đúng kỳ vọng, full177/177PASS sau bổ sung. Gamma mutantFAIL đúng kỳ vọng. Hai log subtraction mốc2 copy trongA3 là historical reference, không nhận là rerun native.','',
        'B4 dùng đúng một redesign đã commit trước outcome mới: λA7/7.2/8.1, center7.2.11ôin không đủ15; không chốt calibration dù có individual cells đạt. NegativeN01/N02 SD vàN03/N04 conservation: sáu contrast0 là kỳ vọng giải tích, chưa chạy contrast. Không được bỏout hay thử λ lần hai trong protocol này.','',
        'V1/V8/P0-V3/P0-V11 author-attested trực tiếp, không có artifact lưu; V9/P0-V10 chưa independently verified. Full PHASE_1/Final Review source chưa mở, chỉ có digest/reading note; không giả full SHA/quote hoặc gọi check4PASS. Heads-up chỉ là nháp repo, chưa gửi. G1 và MainRQ không đổi; failed screen convention không bác hypothesis.','',
        '## p_sw ởΔt/2 — đối chiếu đầy đủ','', '| Ô | Initial | Redesign | Nhãn cuối |','|---|---:|---:|---|']
    for r in comparison:lines.append(f"|{r['cell']}|{float(r['initial_low']):.9f}–{float(r['initial_high']):.9f}|{float(r['redesign_low']):.9f}–{float(r['redesign_high']):.9f}|{r['redesign_class']}|")
    lines+=['','Intervals đầy đủ không làm tròn trongCSV;0/1 hiển thị9decimal không chứng nhận constant chính xác nếu interval vẫn chạm biên.','',
        '## Lệnh đã thực thi','', '```bash','PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a1',
        'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a2','PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a4',
        'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a1_redesign --output-dir /tmp/smr-a1-redesign-replay',
        'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a2 --redesign','PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a4 --redesign',
        'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a5',
        '.venv/bin/python -m pytest -q --junitxml=results/lessons/v1_1_a6/full_suite.xml',
        '.venv/bin/python notes/verification/verify_v1_1_part_a.py','PYTHONPATH=src:. .venv/bin/python notes/verification/verify_v1_1_factorized_law.py','```','',
        'A1/A2 runners giữ output và từ chối ghi đè; A4 có resume và kiểm candidate/source hashes cho lần redesign. Tái lập trong clone/worktree sạch hoặc chọn output mới khi CLI hỗ trợ. Baseline165 là record mốc2, không giả rerun hiện tại vẫn165test.','',
        '## Artifacts','',
        '- config.json/results.json/readiness.json: cấu hình, metric và trạng thái từng check.',
        '- full_suite.txt/xml, native_subtraction_mutant*.txt/xml, mutation_development_note.md: baseline thật và mutant trước/sau.',
        '- screen_comparison.csv + part_A_diagnostics.png: p_sw hai thiết kế và plot standalone.',
        '- dominance_mass.csv/factorized_law_audit.json: masses ĐK1 và136 legacyB comparisons (maxTV≈1.32e−14).',
        '- ../v1_1_a1*/certificates.csv +certificate JSON:20+20 priors; ../v1_1_a2*/supports.json,NPZ,labels.csv,budget.csv: D/ĐK1/budget.',
        '- ../v1_1_a4*/screen.csv/run_output.txt:88rows vàlog; ../v1_1_a5/selection.json: quyết định rejected vàcalibration rỗng.',
        '- notes/design/grid_v1_1*.json/md: full decision/candidate manifests; definitions/boundary/brief v1.1 vẫn draft vì B4fail.',
        '- source src/smr/stationary_spectral.py,stationary_v2.py,gap_screen.py,native/idle_backward.cpp; tests/test_stationary_spectral.py,test_gap_screen.py.',
        '- Không cómargin/Lstar/contrast/network experiment hoặc tagv1.1 mới. Bước tiếp theo là protocol NARROW/REFORMULATE mới, chưa chọn tham số outcome-driven tiếp.','']
    (out/'report.md').write_text('\n'.join(lines));manifest(out)
    print(json.dumps(results,ensure_ascii=False,indent=2))


def plot(out,comparison,prior):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(14,4.8));x=np.arange(1,23)
    axes[0].axhspan(.1,.9,color='green',alpha=.12,label='Accept [.1, .9]')
    axes[0].plot(x,[float(r['initial_low']) for r in comparison],'o-',label='Initial: 8/22')
    axes[0].plot(x,[float(r['redesign_low']) for r in comparison],'s-',label='One redesign: 11/22')
    axes[0].set_xticks(x);axes[0].set_xlabel('Main cell ID');axes[0].set_ylabel('Strict Switch probability at dt/2');axes[0].legend()
    axes[1].semilogy(range(1,41),[max(float(r['law_error_A']),float(r['law_error_B'])) for r in prior],'o',label='Law error bound')
    axes[1].axhline(1e-10,color='red',linestyle='--',label='Declared law target')
    axes[1].set_xlabel('Prior certificate row (20 original + 20 redesign)');axes[1].set_ylabel('TV error bound');axes[1].legend()
    fig.suptitle('Part A: solver certificates pass; grid acceptance fails (needs 15/22)');fig.tight_layout()
    fig.savefig(out/'part_A_diagnostics.png',dpi=160);plt.close(fig)

if __name__=='__main__':run()
