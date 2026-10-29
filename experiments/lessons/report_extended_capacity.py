"""Doan Van Tai — combine preserved v1/v2 resource probes; never run an engine."""
import csv
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.R3R_07_confirmation.common import digest,write_once
from experiments.R3R_07_numerics.run import verify_prereg


def main():
    prereg=Path('experiments/R3R_07_numerics/prereg_extended_v2.json')
    cfg=verify_prereg(prereg);raw=Path(cfg['output'])
    recovered=not (raw/'summary.json').exists()
    summary_path=raw/('recovery_summary.json' if recovered else 'summary.json')
    summary=json.loads(summary_path.read_text())
    old=json.loads(Path(cfg['prior_attempt']['path']).read_text())
    old_by_id={r['id']:r for r in old['records']}
    rows=[]
    for rec in summary['records']:
        rid=rec['id'];resources=rec['resources'];p=raw/rid/'result.json'
        data=json.loads(p.read_text()) if p.exists() else {}
        progress=raw/rid/'progress.jsonl'
        phases=[json.loads(s) for s in progress.read_text().splitlines()] if progress.exists() else []
        last=next((p['phase'] for p in reversed(phases) if p['phase']!='worker_finished'),'not_started')
        reason=resources.get('stop_reason') or data.get('error_type') or ''
        rows.append(dict(id=rid,status=rec['status'],prior_status=old_by_id[rid]['status'],
                         prior_cpu_seconds=old_by_id[rid]['resources']['cpu_seconds'],
                         cpu_seconds=resources['cpu_seconds'],wall_seconds=resources['wall_seconds'],
                         cpu_seconds_lower=resources.get('observed_cpu_seconds_lower',resources['cpu_seconds']),
                         peak_rss_MiB=max(resources['sampled_peak_rss_bytes'] or 0,data.get('peak_rss_bytes',0))/1024**2 if resources['sampled_peak_rss_bytes'] is not None else None,
                         final_phase=last,reason=reason,error=data.get('error',''),
                         law_error_upper=data.get('law_error_upper'),
                         posterior_error_max=max(data.get('posterior_errors',[0])) if data else None))
    with (raw/'capacity_metrics.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    done=sum(r['status']=='COMPLETED' for r in rows)
    memory=[r for r in rows if r['reason'] in ('RSS_LIMIT','MemoryError') or 'allocate' in r['error'].lower()]
    numerical=[r for r in rows if r['reason'] and r['reason'] not in ('CPU_LIMIT','WALL_LIMIT','RSS_LIMIT','MemoryError')]
    if recovered:verdict='LOCAL_BASELINE_PARTIAL_AFTER_INTERRUPTION'
    elif done==len(rows):verdict='LOCAL_STATIONARY_PROBES_COMPLETE'
    elif memory:verdict='LOCAL_MEMORY_BUDGET_EXCEEDED'
    elif numerical:verdict='NUMERICAL_ERROR_REQUIRES_AUDIT'
    else:verdict='LOCAL_RUNTIME_UNRESOLVED_WITHIN_DECLARED_CAP'
    result=dict(owner='Doan Van Tai',date=datetime.now(ZoneInfo('Asia/Saigon')).isoformat(),
                status=verdict,completed=done,attempted=len(rows),source_commit=json.loads((raw/'attempt.json').read_text())['source_commit'],
                prereg_sha256=digest(prereg),cpu_seconds=sum(r['cpu_seconds'] for r in rows) if all(r['cpu_seconds'] is not None for r in rows) else None,
                cpu_seconds_lower=sum(r['cpu_seconds_lower'] for r in rows),
                wall_seconds_sum=sum(r['wall_seconds'] for r in rows) if all(r['wall_seconds'] is not None for r in rows) else None,
                peak_rss_MiB=max(r['peak_rss_MiB'] for r in rows if r['peak_rss_MiB'] is not None),
                peak_rss_complete_coverage=not recovered,raw_summary=str(summary_path),budget_enforcement_fully_verified=not recovered,
                combined_stationary_completed=3+done,combined_stationary_total=6,legacy_anchors_reused=3,
                prior_v1_results_preserved=True,CF_generated=0,confirmation_root=None,n=None,Phase4='HOLD',
                global_audit='not performed by these stationary-only measurements',
                GCP=dict(user_supplied_type='n2-standard-8',vcpus=8,memory_GB=32,status='RUNNING verified via API; author started',started_by_agent=False),
                interpretation='single-worker stationary feasibility only; no measured p95 full-regime time, no guarantee on full confirmation',rows=rows)
    write_once(raw/'capacity_verification.json',result)
    lines=['# L3R.7 — đo dài hơn để đánh giá máy local','',
           'Người phụ trách: **Doan Van Tai** · 29/10/2026 · baseline theo DL-080.',
           f"Prereg commit `{result['source_commit'][:7]}`. Giữ nguyên 3 đầu vào khoa học; giới hạn mỗi job: 1800 CPU-s, 2400 wall-s, 6 GiB RSS, 7 GiB address space; 1 worker.",'',
           f"Trạng thái: **{verdict}**. Hoàn tất **{done}/{len(rows)}** probe mới; gộp với v1 là **{3+done}/6** stationary probes.",'',
           '| Probe | Kết quả | CPU(s) | Wall(s) | Peak RSS(MiB) | Phase/lý do |',
           '|---|---|---:|---:|---:|---|']
    def fmt(v):return f'{v:.3f}' if v is not None else 'chưa biết'
    for r in rows:
        lines.append(f"|{r['id']}|{r['status']}|{fmt(r['cpu_seconds'])}|{fmt(r['wall_seconds'])}|{fmt(r['peak_rss_MiB'])}|{r['final_phase']} / {r['reason'] or '—'}|")
    lines+=['',f"Tổng CPU chính xác: **{fmt(result['cpu_seconds'])} s**; CPU lower bound đã quan sát: **{result['cpu_seconds_lower']:.3f} s**. Peak RSS lớn nhất trong các receipt đầy đủ: **{result['peak_rss_MiB']:.1f} MiB**.",
            'Ca B không có final resource/result sau phiên bị ngắt. Last CPU sample1815.55s vượt ceiling1800s; không xác nhận finalCPU, peakRSS, exit reason hoặc budget enforcement của ca này. Không suy numerical PASS từ việc process đã dừng.' if recovered else 'Các job đều có receipt cuối.','',
            '## Cách đọc kết quả','',
            '- Đây là mở rộng giới hạn tài nguyên sau khi v1 chạm CPU limit, theo ủy quyền của tác giả; không khai là có giới hạn này từ đầu.',
            '- Giữ nguyên toàn bộ error/partial của v1. Không chạy lại những ca PASS để chọn timing thuận lợi.',
            '- Chỉ tính stationary law, certificate, quantile và posterior error bounds; chưa tính joint cost, global accuracy hoặc p95 của một CF regime.',
            '- Nếu memory limit: chỉ kết luận vượt resource budget local đã khai. VM GCP 32 GB có thêm RAM nhưng phải đo, audit và khóa environment riêng.',
            '- Nếu CPU limit: GCP 8 vCPU chưa chắc nhanh hơn cho một job một thread; cần đo từng core và đánh giá thuật toán.',
            '- Nếu certificate/root finding có lỗi: tăng RAM/CPU không tự sửa correctness; cần giữ kết quả và audit.',
            '- Nếu tất cả complete: vẫn cần kiểm certificate, reuse v1 và full audit trước v1.3.1/n/root/CF.',
            '- Tác giả đã bật GCP; API xác nhận RUNNING. Phiên này không start/create/resize VM; cloud profile có prereg và môi trường riêng.','',
            '## Lệnh và artifact','',
            '```bash',
            '.venv/bin/python -m experiments.R3R_07_numerics.run --prereg experiments/R3R_07_numerics/prereg_extended_v2.json --out results/R3R_numerics/20261029_02',
            '.venv/bin/python -m experiments.lessons.report_extended_capacity',
            '```','',
            'CSV: `results/R3R_numerics/20261029_02/capacity_metrics.csv`.',
            'JSON: `capacity_verification.json`, `summary.json`, từngprobe/resource/result/progress.',
            'Log: `results/lessons/l3r_7/extended_capacity/run.log`.',
            'Không cóCF/newseed/practicalnetworkvalidation; không sửa card/measure hoặctag đãkhóa.']
    report=Path('results/lessons/l3r_7/extended_capacity/report.md')
    with report.open('x') as f:f.write('\n'.join(lines)+'\n')
    write_once(raw/'artifact_index.json',{str(p):digest(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='artifact_index.json'})
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
