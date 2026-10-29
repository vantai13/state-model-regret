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
    summary=json.loads((raw/'summary.json').read_text())
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
                         peak_rss_MiB=max(resources['sampled_peak_rss_bytes'],data.get('peak_rss_bytes',0))/1024**2,
                         final_phase=last,reason=reason,error=data.get('error',''),
                         law_error_upper=data.get('law_error_upper'),
                         posterior_error_max=max(data.get('posterior_errors',[0])) if data else None))
    with (raw/'capacity_metrics.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    done=sum(r['status']=='COMPLETED' for r in rows)
    memory=[r for r in rows if r['reason'] in ('RSS_LIMIT','MemoryError') or 'allocate' in r['error'].lower()]
    numerical=[r for r in rows if r['reason'] and r['reason'] not in ('CPU_LIMIT','WALL_LIMIT','RSS_LIMIT','MemoryError')]
    if done==len(rows):verdict='LOCAL_STATIONARY_PROBES_COMPLETE'
    elif memory:verdict='LOCAL_MEMORY_BUDGET_EXCEEDED'
    elif numerical:verdict='NUMERICAL_ERROR_REQUIRES_AUDIT'
    else:verdict='LOCAL_RUNTIME_UNRESOLVED_WITHIN_DECLARED_CAP'
    result=dict(owner='Doan Van Tai',date=datetime.now(ZoneInfo('Asia/Saigon')).isoformat(),
                status=verdict,completed=done,attempted=len(rows),source_commit=json.loads((raw/'attempt.json').read_text())['source_commit'],
                prereg_sha256=digest(prereg),cpu_seconds=sum(r['cpu_seconds'] for r in rows),
                wall_seconds_sum=sum(r['wall_seconds'] for r in rows),peak_rss_MiB=max(r['peak_rss_MiB'] for r in rows),
                combined_stationary_completed=3+done,combined_stationary_total=6,legacy_anchors_reused=3,
                prior_v1_results_preserved=True,CF_generated=0,confirmation_root=None,n=None,Phase4='HOLD',
                global_audit='not performed by these stationary-only measurements',
                GCP=dict(user_supplied_type='n2-standard-8',vcpus=8,memory_GB=32,status='reported STOPPED',started=False),
                interpretation='single-worker stationary feasibility only; no measured p95 full-regime time, no guarantee on full confirmation',rows=rows)
    write_once(raw/'capacity_verification.json',result)
    lines=['# L3R.7 — đo dài hơn để đánh giá máy local','',
           'Người phụ trách: **Doan Van Tai** · 29/10/2026 · DL-080–081.',
           f"Prereg commit `{result['source_commit'][:7]}`,giữ nguyên3đầu vào khoa học; ceiling1800CPU-s/2400wall-s/6GiBRSS/7GiBAS,1worker.",'',
           f"Trạng thái: **{verdict}**. Hoàn tất **{done}/{len(rows)}** probe mới; gộp với v1 là **{3+done}/6** stationary probes.",'',
           '| Probe | Kết quả | CPU(s) | Wall(s) | Peak RSS(MiB) | Phase/lý do |',
           '|---|---|---:|---:|---:|---|']
    for r in rows:
        lines.append(f"|{r['id']}|{r['status']}|{r['cpu_seconds']:.3f}|{r['wall_seconds']:.3f}|{r['peak_rss_MiB']:.1f}|{r['final_phase']} / {r['reason'] or '—'}|")
    lines+=['',f"TổngCPU **{result['cpu_seconds']:.3f}s**;sumwall **{result['wall_seconds_sum']:.3f}s**;peakRSS **{result['peak_rss_MiB']:.1f}MiB**.",'',
            '## Cách đọc kết quả','',
            '- Đây làresourceextension sauv1CPU-limit theoủyquyền tácgiả,không phải kếtquả được khai từđầu.',
            '- Giữ nguyên tấtcảv1error/partial. Không chạy lại những caPASS đểlấy timing đẹp.',
            '- Chỉstationary law/certificate/quantile/posterior; chưa jointcost,globalaccuracy hoặc p95 của mộtCFregime.',
            '- Nếu memorylimit: chỉ kết luận vượt resourcebudget local đãkhai; máyGCP32GB cóthêmRAM nhưng phải đo,audit vàkhóaenvironment riêng.',
            '- Nếu CPUlimit: GCP8vCPU không tự bảođảm nhanhhơn mộtjob1thread; cần đánhgiáper-core/thuậttoán.',
            '- Nếu numericalcertificate/rootfindingerror: tăngRAM/CPU không tựsửa correctness; giữ kếtquả vàaudit.',
            '- Nếu tấtcảcomplete: chỉđóng feasibilitygate saukhi kiểmcertificates vàreusev1; cònfullaudit trướcv1.3.1/n/root/CF.',
            '- VMGCP đangđược tácgiảbáoSTOPPED; phiênnày khôngstart/create/resizeVM.','',
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
