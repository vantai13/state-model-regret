"""Doan Van Tai — render the Vietnamese report from independently checked tables."""
import csv
import difflib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(newline='') as f:
        return list(csv.DictReader(f))


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---']*len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, row)) + ' |' for row in rows])


def main():
    A, C, D = read('aggregate_rolling.csv'), read('comparisons_rolling.csv'), read('diagnostics_rolling.csv')
    groups = read('case_groups.csv')
    run = json.loads((HERE / 'run.json').read_text())
    timing = json.loads((HERE / 'command_timing.json').read_text())
    audit = json.loads((HERE / 'independent_rescore.json').read_text())
    tests = json.loads((HERE / 'tests_spawn_timing.json').read_text())
    old_timing = json.loads((HERE / 'attempt01_startup_failed/command_timing.json').read_text())
    rescore_timing = json.loads((HERE / 'rescore_timing.json').read_text())
    index = {(r['group'], r['trace'], r['h_mult'], r['tau_s'], r['population'], r['method']): r for r in A}

    def metric(method, group='ALL', trace='ALL', hm='MAX_AVAILABLE', tau='0.0', pop='uniform'):
        return index[(group, trace, hm, tau, pop, method)]

    def fmt(method, **kw):
        r = metric(method, **kw)
        return f"{float(r['median_pct']):.3f} ({float(r['mean_pct']):.3f})"

    def counts(method, reference, group):
        r = next(r for r in C if r['group'] == group and r['trace'] == 'ALL' and r['h_mult'] == 'MAX_AVAILABLE'
                 and r['tau_s'] == '0.0' and r['population'] == 'uniform' and r['method'] == method
                 and r['reference'] == reference)
        return '/'.join(r[k] for k in ('better', 'worse', 'within_margin'))

    methods = ['M0', 'static', 'hybrid'] + [f'{kind}_{e}_{w}' for w in ('60', '300', 'all')
                                          for e in ('sim', 'mm1') for kind in ('static', 'hybrid')]
    main_table = table(['Policy', 'OK, n=8', 'FLIP, n=18'],
                       [[m, fmt(m, group='OK'), fmt(m, group='FLIP')] for m in methods])
    comparison_table = table(['Policy', 'OK so với gốc', 'OK so với M0', 'FLIP so với gốc', 'FLIP so với M0'],
        [[m, counts(m, m.split('_')[0], 'OK'), counts(m, 'M0', 'OK'),
          counts(m, m.split('_')[0], 'FLIP'), counts(m, 'M0', 'FLIP')] for m in methods[3:]])
    diag_rows = []
    for tag in ['original', 'sim_60', 'mm1_60', 'sim_300', 'mm1_300', 'sim_all', 'mm1_all']:
        cells = [next(r for r in D if r['group'] == g and r['trace'] == 'ALL' and r['h_mult'] == 'MAX_AVAILABLE'
                      and r['tau_s'] == '0.0' and r['population'] == 'uniform' and r['estimator'] == tag)
                 for g in ('OK', 'FLIP')]
        diag_rows.append([tag] + [f"{100*float(r['mean_sign_ok']):.2f}% / {100*float(r['mean_disagreement']):.2f}%"
                                 for r in cells])
    diag_table = table(['Estimator', 'OK, dấu đúng / bất đồng', 'FLIP, dấu đúng / bất đồng'], diag_rows)
    flag_rows = []
    flags = {(r['window'], r['status']): int(r['windows']) for r in read('window_flag_counts.csv')}
    for w in ('60', '300', 'all'):
        one, both = flags[(w, 'ONE_UNSTABLE')], flags[(w, 'BOTH_UNSTABLE_SIGN_PROXY')]
        flag_rows.append([w, flags[(w, 'STABLE')], one, both, f'{one+both}/23296'])
    flag_table = table(['W', 'Stable', 'Một action unstable', 'Hai action unstable', 'Tổng flag'], flag_rows)
    trace_rows = []
    for trace in ('ditl_20230412', 'mawi_20250311', 'mawi_20260414'):
        trace_rows.append([trace, metric('M0', trace=trace)['n_cases']] +
                          [fmt(m, trace=trace) for m in ('M0', 'hybrid', 'hybrid_sim_60', 'hybrid_sim_300', 'hybrid_sim_all')])
    trace_table = table(['Trace', 'n', 'M0', 'Hybrid gốc', 'Sim 60', 'Sim 300', 'Sim all'], trace_rows)
    h_rows = []
    for hm in ('0.3', '0.5', '1.0', '2.0', '3.0', '5.0', '10.0'):
        h_rows.append([hm, metric('M0', group='FLIP', hm=hm)['n_cases']] +
                      [fmt(m, group='FLIP', hm=hm) for m in ('M0', 'hybrid', 'hybrid_sim_60', 'hybrid_sim_300', 'hybrid_sim_all')])
    h_table = table(['h/T_int', 'n FLIP', 'M0', 'Hybrid gốc', 'Sim 60', 'Sim 300', 'Sim all'], h_rows)
    age_rows = []
    for tau in ('0.0', '60.0', '300.0'):
        for pop in ('uniform', 'alarm'):
            age_rows.append([tau, pop, metric('M0', group='FLIP', tau=tau, pop=pop)['n_cases']] +
                [fmt(m, group='FLIP', tau=tau, pop=pop) for m in ('M0', 'hybrid', 'hybrid_sim_60', 'hybrid_sim_300', 'hybrid_sim_all')])
    age_table = table(['τ (s)', 'Population', 'n FLIP', 'M0', 'Hybrid gốc', 'Sim 60', 'Sim 300', 'Sim all'], age_rows)
    headline = {g: {m: {k: float(metric(m, group=g)[k]) for k in ('mean_pct', 'median_pct')}
                    for m in methods} for g in ('ALL', 'OK', 'FLIP')}
    with (HERE / 'headline_metrics.json').open('x') as f:
        json.dump(dict(condition='largest available h per case; tau=0; uniform; ratio-of-means within case, equal cases across cases',
                       metrics=headline, groups=audit['group_counts'],
                       sim_all_hybrid_vs_original=counts('hybrid_sim_all', 'hybrid', 'ALL'),
                       sim_all_hybrid_vs_M0=counts('hybrid_sim_all', 'M0', 'ALL')), f, indent=2)
    minimum = min(int(g['group_n']) for g in groups if g['group'] != 'NOT_EVALUABLE')
    text = f'''S1-C rolling ŝ, exploratory POST HOC, 21/11/2026. Người phụ trách Doan Van Tai.

Rolling bằng simulation trên toàn lịch sử test đã qua giảm mạnh lỗi do dấu train không khớp test trên panel này. Ở h lớn nhất khả dụng mỗi case, τ=0, uniform, regret trung bình theo 26 case của M0 là {float(metric('M0')['mean_pct']):.3f}% C_ref, static gốc {float(metric('static')['mean_pct']):.3f}%, hybrid gốc {float(metric('hybrid')['mean_pct']):.3f}%, rolling sim_all static/hybrid cùng {float(metric('hybrid_sim_all')['mean_pct']):.3f}%. Đây là sửa estimator theo dữ liệu đã thấy. Chưa xác nhận trên dữ liệu mới và chưa thấy lợi ích riêng của hybrid so với rolling static tại lát này.

Đã thực hiện và kiểm chứng

Giữ đúng 6 biến thể với W∈{{60 s, 300 s, toàn lịch sử test}} × {{sim, mm1}}. Không thêm biến thể sau outcome. Giữ nguyên từng cost, C_ref, fluid gap, population uniform/alarm và support từ full/. Raw local có 26 case có decisions, gồm 8 OK và 18 FLIP, cùng 1 NOT_EVALUABLE do train T_int unresolved/censored. Con số 25 và 8/17 trong brief không khớp raw hiện có. Lần đếm sơ bộ 9/17 trong commentary và docstring trước run cũng sai, được đính chính bằng case_groups.csv và rescore độc lập. Source đã chạy được giữ nguyên để kiểm SHA.

Seed test là full_seed 311121 + trace_index×100 + 1000000, khớp simulate_case. Tái tạo qA/qB đúng {run['checked_rows']:,}/{run['rows']:,} rows, thay cho lấy mẫu mỗi 37 rows trong nháp. Cửa sổ là [max(0,e−W),e], hoặc [0,e], với e=t−τ. Sim tính time-average tổng backlog của hai shadow histories action 0/1 từ đầu test. Công thức occupation là tổng max(0,min(departure,e)−max(arrival,start)). Packet đến sau e đóng góp 0, packet còn chờ ở e được cắt tại e. Departure sau e không làm lộ thời điểm hoàn thành tương lai. Test thay phần tape/service sau e và test cắt occupation đều PASS. M/M/1 đếm background arrivals trên (start,e], dùng u và μ đã cho, với mean number λ/(μ−λ) khi stable. Không burn thêm đầu cửa sổ.

Các sửa đổi trước outcome gồm chấm dấu theo s_test cấp case, lưu riêng độ khớp dấu với từng future, và sửa fallback M/M/1 khi cả hai action unstable. Nháp dùng hiệu overload có đơn vị packet/s như một slope backlog, làm h·ŝ sai đơn vị. Bản chạy chỉ dùng dấu overload dưới dạng ±∞, hoặc 0 khi hòa, và gắn flag. Đây là heuristic khi không tồn tại stationary M/M/1 mean, mọi flag được giữ trong kết quả. Các sửa đổi khác gồm kiểm mọi backlog, lưu support trống, nhận diện từng window duy nhất, đo CPU/wall, chống ghi đè trước compute. Lần khởi chạy đầu FAIL PermissionError ở forkserver socket, trước khi tạo worker hoặc outcome. Đổi multiprocessing sang spawn như runner gốc, rồi test và chạy lại. Log lần lỗi được giữ trong attempt01_startup_failed/.

36 tests PASS trong {tests['wall_s']:.3f} s wall, gồm test mới và regression runner gốc. Command run hoàn tất với {timing['CPU_s']:.3f} CPU-s và {timing['wall_s']:.3f} s wall, 6 worker. Bộ đếm nội bộ task+parent là {run['CPU_s']:.3f} CPU-s, không gồm hết overhead khởi tạo/IPC nên dùng command timing làm tổng. Lần lỗi đầu tốn thêm {old_timing['CPU_s']:.3f} CPU-s. Rescore độc lập dùng stdlib, không import scorer, PASS trên {audit['checked_rows']:,} rows, {audit['checked_available_cells']:,} ô có dữ liệu trong {audit['total_support_cells']:,} ô support, {audit['window_n']:,} windows và {audit['protected_hashes']} hash đầu vào. Rescore tốn {rescore_timing['CPU_s']:.3f} CPU-s.

Cách đọc số liệu

Trong mỗi case×h×τ×population, regret được tính bằng 100×mean(regret)/mean(C_ref), không lấy trung bình các tỉ số từng decision. Đơn vị cost là packet·s. Mọi ô dưới đây ghi trung vị (trung bình) của các tỉ số case, đơn vị % C_ref, các case có trọng số bằng nhau. h lớn nhất khả dụng nằm trong 1, 2, 3 hoặc 10 T_int tùy case. Không coi đây là cùng physical horizon. Nhãn OK/FLIP dùng dấu s_train so với mean((cost_switch−cost_stay)/h) ở h lớn nhất, uniform, τ=0. s_test dùng outcome nên nhóm chỉ có giá trị chẩn đoán. Không loại case mới để khớp count của brief.

Ở h lớn nhất khả dụng, τ=0, uniform

{main_table}

Đếm case tốt hơn/tệ hơn/trong margin, theo đúng thứ tự a/b/c. Margin là 0,05 điểm %, so sánh cùng case và cùng policy static hoặc hybrid gốc. Bảng này dùng cùng điều kiện với bảng trên.

{comparison_table}

Độ đúng dấu và bất đồng static với hybrid, trung bình các share theo case, cùng điều kiện trên. Dấu đúng ở đây so với s_test cấp case. sign_local_ok trong CSV chấm riêng với từng future. Với sim_all, local sign accuracy trung bình trên 26 case là 97,077%, dù dấu cấp case khớp 100%.

{diag_table}

Đếm flag M/M/1 trên đơn vị case×W×e duy nhất, không đếm lặp cùng window qua các h. Mỗi W có 23.296 windows. Không dùng các windows này như independent trials.

{flag_table}

Theo trace, gộp cả hai nhóm, h lớn nhất khả dụng, τ=0, uniform. Sim trong các bảng còn lại là hybrid dùng estimator tương ứng.

{trace_table}

Theo h, chỉ nhóm FLIP, τ=0, uniform. Số case giảm khi thiếu tail support ở h dài. Hai hàng khác h có thể khác panel.

{h_table}

Theo τ và population, nhóm FLIP, giữ h lớn nhất của case theo uniform. Alarm dùng nguyên nhãn từ policy static gốc, không tính lại theo rolling.

{age_table}

Toàn bộ joint slices OK/FLIP×trace×h×τ×population cho đủ 15 policy, gồm static và hybrid của cả 6 biến thể, nằm trong aggregate_rolling.csv. Từng case nằm trong summary_rolling.csv. Counts với margin và shares tương ứng nằm trong comparisons_rolling.csv và diagnostics_rolling.csv. Các bảng trên chọn τ=0, 60, 300 s theo brief, CSV giữ cả 7 tuổi gốc.

Cơ chế và giới hạn

Ở h lớn nhất, rolling sim_all tốt hơn hybrid gốc ở {counts('hybrid_sim_all', 'hybrid', 'ALL')} case theo thứ tự tốt/tệ/trong margin và tốt hơn M0 ở {counts('hybrid_sim_all', 'M0', 'ALL')}. Trong FLIP, mean regret giảm từ 39,574% xuống 0,472%, trong khi M0 là 13,420%. Ở h=10 T_int, chỉ còn 4 FLIP thuộc DITL, mean hybrid gốc 117,256%, sim_60 27,448%, sim_300 15,840%, sim_all 2,103%. W dài hơn hữu ích trong dữ liệu này. W ngắn không luôn bám drift tốt hơn. Chẳng hạn DITL s120 c0 thuộc OK, W=60 có dấu sai 2/9 decisions tại h lớn nhất và regret 114,042%, so với 0% của gốc, W=300 và all. Mẫu hình cho thấy các trung bình ngắn có thể đổi dấu mạnh theo đoạn history, chưa tách được nhiễu Poisson khỏi biến động tải.

Mọi s_test cấp case đều âm trên 26 case. Sim_all có dấu âm tại mọi decision trong lát h lớn nhất, τ=0, uniform, và static/hybrid không bất đồng. Do đó mức cải thiện ở đây đến từ việc đổi estimator và chọn action phù hợp drift đã quan sát, chưa chứng minh thành phần fluid+h·ŝ tốt hơn rolling static. Ở alarm, τ=300 s, 3 case FLIP còn support có mean sim_all 5,871% so với M0 4,962%, nên không kết luận rolling thắng ở mọi population hoặc age. Các trường hợp M/M/1 unstable vẫn là kết quả của fallback có flag, không được diễn giải thành stationary truth.

Thứ nhất, đây là post hoc trên cùng dữ liệu full đã thấy, có nhóm dùng outcome. Thứ hai, chỉ có 3 ngày trace count, dữ liệu gói là Cox replay với service marks mô phỏng, hai shadow histories cần model/tape và không được xem là estimator đo trực tiếp trong production. Thứ ba, futures và windows chồng lấn, các case chia sẻ ngày/seed, số decision ở h lớn nhất có thể chỉ {minimum}, alarm còn ít hơn. Không có population CI hoặc bằng chứng độc lập giữa case. Cuối cùng, không điều chỉnh tuning, tải hoặc population sau khi xem kết quả. Giữ nguyên sáu biến thể là đủ cho câu hỏi chẩn đoán này.

Lệnh thực tế và vị trí lưu

Mọi command dưới đây dùng PYTHONDONTWRITEBYTECODE=1. Test và run source experiments/explore_ctmc/env.sh trước khi chạy.

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=results/letter/sweep/trace/rolling/pytest_spawn_tmp results/letter/sweep/trace/rolling/test_rolling.py tests/test_sweep_trace.py
.venv/bin/python -B results/letter/sweep/trace/rolling/analyze_rolling.py
.venv/bin/python -B results/letter/sweep/trace/rolling/summarize_rolling.py
.venv/bin/python -B results/letter/sweep/trace/rolling/render_report.py
```

Các file dưới đây đều trong results/letter/sweep/trace/rolling/.

| Loại | File |
| --- | --- |
| Source và test | analyze_rolling.py, test_rolling.py, summarize_rolling.py, render_report.py |
| Quy tắc trước run | run_started.json, dùng nguyên ../design_ready/plan.json |
| Raw rolling | rows_rolling.csv, windows_rolling.csv, case_groups.csv |
| Metric và slices | summary_rolling.csv, aggregate_rolling.csv, comparisons_rolling.csv, diagnostics_rolling.csv, window_flag_counts.csv, headline_metrics.json |
| Log và timing | tests.log, tests_spawn.log, run.log, rescore.log, tests_timing.json, tests_spawn_timing.json, command_timing.json, rescore_timing.json, run.json |
| Audit và lịch sử | audit_before.json, variant_manifest_before_analysis.json, independent_rescore.json, draft_changes.diff, analyze_rolling.original.py.txt, analyze_rolling.attempt01.py.txt, attempt01_startup_failed/ |
| Báo cáo | REPORT_ROLLING.md |

Không tạo biểu đồ, không tải dữ liệu, không commit, không SSH và không sửa file ngoài rolling/. Giữ nguyên experiments/letter/sweep_trace.py, full/ và không truy cập kết quả sweep/ctmc/. Kết quả xác nhận việc cập nhật ŝ có thể sửa sai dấu train trong panel này, đồng thời ghi nhận thất bại của cửa sổ ngắn và alarm ít support. Muốn suy ra hiệu quả ngoài panel cần một thiết kế xác nhận riêng.
'''
    with (HERE / 'REPORT_ROLLING.md').open('x') as f:
        f.write(text)
    original = (HERE / 'analyze_rolling.original.py.txt').read_text().splitlines(keepends=True)
    current = (HERE / 'analyze_rolling.py').read_text().splitlines(keepends=True)
    with (HERE / 'draft_changes.diff').open('x') as f:
        f.writelines(difflib.unified_diff(original, current, fromfile='analyze_rolling.original.py', tofile='analyze_rolling.py'))
    print('Wrote REPORT_ROLLING.md, headline_metrics.json and draft_changes.diff exclusively.')


if __name__ == '__main__':
    main()
