"""Doan Van Tai: format verified saved A1 measurements; no experiment calls."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'results/lessons/p4_a1'
v=json.loads((OUT/'verification.json').read_text())
runs=v['runs']


def put(path,obj):
    with path.open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


table=[]
for run,r in runs.items():
    cfg=json.loads((ROOT/'experiments/P4_A1/runs'/run/'prereg.json').read_text())
    base=ROOT/cfg['output'];full=json.loads((base/'full_summary.json').read_text())
    table.append(dict(run=run,status=r['status'],planned=r['planned'],full_stage_completed=r['full_stage_completed'],
                      observed_distinct_including_benchmark=r['observed_distinct_including_benchmark'],
                      PASS=full['counts'].get('PASS',0),NOT_READY=full['counts'].get('NOT_READY',0),
                      BUG=full['counts'].get('BUG',0),eval_cpu_seconds_including_control=r['unique_evaluation_cpu_seconds_including_control']))
    cache=base/'native_cache'; files=[]
    for p in sorted(cache.rglob('*')):
        if not p.is_file():continue
        digest=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1024**2),b''):digest.update(block)
        files.append(dict(path=str(p.relative_to(cache)),bytes=p.stat().st_size,sha256=digest.hexdigest()))
    put(base/'cache_manifest.json',dict(local_only=True,regenerable_from_frozen_source=True,
                                       files=files,total_bytes=sum(f['bytes'] for f in files)))
with (OUT/'measured_runs.csv').open('x',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
sv=runs['L43_A1_SV'];sub=runs['SUB_PROBE'];rho=sv['independent_rho_rescore']
svtext='Không chọn rho hoặc tạo manifest vì full HOLD.' if not isinstance(rho,dict) else '\n'.join(
    f"- {name}: N_ready={d['N_ready']}; rho*={d['rho_star']}; median GS/Cref {d['median_GS_original_pctC']:.9f}% -> {d['median_GS_theta_pctC']:.9f}%; median deltaL00={d.get('median_deltaL00')} packet·s; narrow={d['descriptive_narrow']}."
    for name,d in rho.items())
lines=['# P4-A1 — kết quả thực thi 31/10/2026','',
       'Người phụ trách: **Doan Van Tai**. AI triển khai và soạn quyết định/dự đoán theo ủy quyền chat; không tác giả tự viết hoặc human review.','',
       '## Đã triển khai và kiểm tra','',
       'Áp patch nguồn, sửa trước freeze: manifest NOT_READY; S11; resume identity/K/ref/CF/hash; dừng bundle sau BUG; lưu CPU lỗi; provenance ủy quyền; hash toàn bộ diagnosis inputs. Frozen source/history/card/CF cũ giữ nguyên.',
       'Patch nguồn thiếu newline cuối đã chuẩn hóa, bản gốc giữ nguyên.72targeted ban đầu PASS; một lượt fixture mới FAIL(NameError) giữ log; sau sửa80targeted PASS2.90s,842full PASS88.76s. Không sửa code A1 sau freeze đầu tiên.','',
       '## Kết quả đo được','',
       '|Run|Trạng thái|Full stage/kế hoạch|Full PASS/NOT_READY/BUG|Đã quan sát cả benchmark|Evaluation CPU gồm control (s)|',
       '|---|---|---:|---:|---:|---:|']
for d in table:
    lines.append(f"|{d['run']}|{d['status']}|{d['full_stage_completed']}/{d['planned']}|{d['PASS']}/{d['NOT_READY']}/{d['BUG']}|{d['observed_distinct_including_benchmark']}|{d['eval_cpu_seconds_including_control']:.6f}|")
lines += ['',
    'L44: HOLD do SH NOT_READY8/72>10%; thực quan sát19tọa độ(11PASS/8NR),71NOT_RUN. Toàn bộ19native-ready nhưng baseline có9arithmetic/12R1events. Khôngrho*,khôngMV/SH claim-narrow,khôngforecastmedians toànscope. Summarize refusal exit1 đúng guard. Chi tiết: ../l4_4/a1/report.md và hold_case_ledger.csv.','',
    '### SV baseline trên tập READY','',svtext,'',
    'Đây là selection/mô tả trên READY subset nếu có exclusions, không full-scope DL104 hoặc confirmation. NOT_READY entries không bị xóa, xuất UNRESOLVED; chưa sàng hộp/p-hat hoặc quyết định thêm card.',
    'DeltaL00 là output mới so với patch baseline-readiness fields: kiểm bổ sung read-only trong verification.json, không tự đổi criterion sau run.','',
    '### SUB probe','',json.dumps(sub.get('predeclared_native_decision'),ensure_ascii=False),
    'XM2X000: Cref-dt ref4/coarse-ref2=0.3105391881%, ref8/coarse-ref4=0.0779178392%. Không suy convergence order hoặc coverage toàn vùng từ một điểm. Giữκ>=.05 là đề xuất cho coverage L4.7 tiếp, không SUB-effect confirmation. Chi tiết probe_metrics.csv.','',
    '## Lệnh thực tế và thứ tự','',
    '`.venv/bin/python -m pytest -q`; `python -m experiments.P4_A1.diagnose`; mỗi run `freeze --run RUN`, commit prereg, `run control/benchmark/budget --run RUN`, commit budget, `run full --run RUN`. Chỉ fullPASS mới `summarize --run RUN`.',
    '`PYTHONPATH=src:. .venv/bin/python notes/verification/p4_a1/verify_outputs.py` đối chiếu arithmetic và rescore độc lập từ saved outputs. Independent runs có thể overlap; mỗi run giữ workers/caps/budget riêng theo execution/schedule.json.','',
    '## Files','',
    '- Source: experiments/P4_A1/; configs/choices/preregs: runs/L44_A1,runs/L43_A1_SV,runs/SUB_PROBE.',
    '- Log/tests/inputs/diagnosis: results/lessons/p4_a1/{preflight,execution,inputs,diagnosis}.',
    '- Raw/control/budget/full/CSV: results/lessons/l4_4/a1/, results/lessons/l4_3/a1_sv/, results/lessons/l4_3/a1_sub_probe/.',
    '- verification.json, measured_runs.csv và cache manifests. Native caches giữ local, ngoài Git; không xóa.','',
    '## Kết luận và giới hạn','',
    'Đã kiểm implementation và chạy plant thật trong scope đăng ký; root cause OLD/CURRENT chưa xác nhận hoàn toàn. Không nới threshold hoặc đổi code sau HOLD. Refinement differences không certified total error bounds. Các median/gridcounts là discovery trên mẫu thích nghi, không prevalence mạng thật; không mới MC/CI hoặc empirical validation.',
    'F1baseline vẫn HOLD; SUB còn cần combined native+baseline/support prereg và coverage. candidate_readiness chưa tạo; L4.5PartB chưa mở.0CF/sealedoutcomes/boxcounts/carddecision,cardv2/F1/thresholds giữ nguyên. G1/P0-V10/L8/Understanding giữ; không nâng AI-work thành tác giả tự làm.']
with (OUT/'report.md').open('x') as f:f.write('\n'.join(lines)+'\n')
print(json.dumps(table,indent=2))
