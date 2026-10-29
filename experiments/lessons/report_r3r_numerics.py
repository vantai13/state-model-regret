"""Doan Van Tai — report preserved calibration, never execute or select regimes."""
import csv
from datetime import datetime
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_confirmation.common import digest,write_once


def main():
    prereg=Path('experiments/R3R_07_numerics/prereg.json');cfg=verify_prereg(prereg)
    raw=Path(cfg['output']);summary=json.loads((raw/'summary.json').read_text())
    jobs={j['id']:j for j in cfg['legacy_jobs']+cfg['stationary_jobs']}
    metrics=[]
    for rec in summary['records']:
        rid=rec['id'];job=jobs[rid];res=rec.get('resources',{})
        progress=raw/rid/'progress.jsonl'
        phases=[json.loads(line) for line in progress.read_text().splitlines()] if progress.exists() else []
        last_stage=next((p for p in reversed(phases) if p['phase']!='worker_finished'),{})
        result=raw/rid/'result.json';data=json.loads(result.read_text()) if result.exists() else {}
        degree=None
        if job['kind']=='stationary_only':
            total=F(job['lambda'])+F(job['managed']);a,b=total-16,total-4
            den=__import__('math').lcm(a.denominator,b.denominator)
            g=__import__('math').gcd(abs(int(a*den)),abs(int(b*den)))
            degree=int((b-a)*den/g)
        phase=last_stage.get('phase','not_started')
        reason=res.get('stop_reason') or data.get('error_type') or (f"SIGNAL_{-res['exit_code']}" if res.get('exit_code',0)<0 else '')
        metrics.append(dict(id=rid,kind=job['kind'],status=rec['status'],degree=degree,
                            wall_seconds=res.get('wall_seconds'),cpu_seconds=res.get('cpu_seconds'),
                            sampled_peak_rss_MiB=res.get('sampled_peak_rss_bytes',0)/1024**2,
                            reported_peak_rss_MiB=data.get('peak_rss_bytes',0)/1024**2 if data else None,
                            final_phase=phase,stop_reason=reason,exit_code=res.get('exit_code'),
                            legacy_matches=rec.get('legacy_comparison',{}).get('status'),
                            law_error_upper=data.get('law_error_upper')))
    with (raw/'metrics.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(metrics[0]),lineterminator='\n');writer.writeheader();writer.writerows(metrics)
    legacy=[r for r in metrics if r['kind']=='legacy_anchor'];stationary=[r for r in metrics if r['kind']=='stationary_only']
    audit=dict(owner='Doan Van Tai',observed_at=datetime.now(ZoneInfo('Asia/Saigon')).isoformat(),
               status=summary['status'],prereg_commit=json.loads((raw/'attempt.json').read_text())['source_commit'],
               prereg_sha256=digest(prereg),legacy_replays=len(legacy),legacy_exact_pass=sum(r['legacy_matches']=='PASS' for r in legacy),
               stationary_attempts=len(stationary),stationary_completed=sum(r['status']=='COMPLETED' for r in stationary),
               stationary_unresolved=sum(r['status']!='COMPLETED' for r in stationary),
               cpu_seconds=summary['stage0_cpu_seconds'],wall_seconds_sum=sum(r['wall_seconds'] or 0 for r in metrics),
               conditional_global_jobs_not_run=summary['conditional_global_jobs'],
               K_star=None,ref_star=None,n=None,confirmation_root=None,CF_generated=0,Phase4='HOLD',
               findings='operational feasibility evidence for the registered implementation and ceilings; not a hypothesis verdict or impossibility proof',
               rows=metrics)
    write_once(raw/'verification.json',audit)
    lines=['# L3R.7 — kết quả calibration numerics đã chạy','',
           'Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · DL-078–079.',
           f"Prereg commit `{audit['prereg_commit'][:7]}` trước run; trạng thái **{summary['status']}**.",'',
           'Đây là kết quả chạy thật trên engine/law hiện tại. Không cấp n/root/CF và không tạo tagv1.3.1.','',
           '| Job | Kết quả | Degree | Wall(s) | CPU(s) | RSS mẫu(MiB) | Phase cuối / lý do |',
           '|---|---|---:|---:|---:|---:|---|']
    for r in metrics:
        lines.append(f"| {r['id']} | {r['status']} | {r['degree'] or '—'} | {r['wall_seconds']:.3f} | {r['cpu_seconds']:.3f} | {r['sampled_peak_rss_MiB']:.1f} | {r['final_phase']} / {r['stop_reason'] or '—'} |")
    lines += ['',f"Legacy anchors khớp **{audit['legacy_exact_pass']}/{len(legacy)}**, gồm numeric pair columns theo bit pattern.",
              f"Stationary marginals hoàn tất **{audit['stationary_completed']}/{len(stationary)}**; UNRESOLVED **{audit['stationary_unresolved']}**.",
              f"Tổng worker CPU **{audit['cpu_seconds']:.3f}s**; tổng elapsed nối tiếp **{audit['wall_seconds_sum']:.3f}s**.",'',
              '## Điều đã và chưa xác nhận','',
              '- Nếu anchors PASS: xác nhận tái lập engine ở ba regime đã thấy, chưa là global accuracy.',
              '- Probe stationary chỉ tính marginal/certificate/quantile/posterior; không tính J/gap/regret/contrast ở joint regime mới.',
              '- Timeout/resource/error là UNRESOLVED trong ceiling đã preregistered; không gọi là hypothesis FALSIFY hoặc chứng minh mọi thuật toán đều không chạy được.',
              '- Hệ mpmath giải dày và bước numpy_roots cần được kiểm/đổi thuật toán khi tăng degree; không ngầm hạ rate grid hoặc dùng fluid law.',
              '- Không chuyển timing của vài marginal thành p95 đầy đủ, không suy r của measure từ những ca này.',
              f"- **{summary['conditional_global_jobs']} global calibration jobs không chạy** theo stop rule; chưa có coverage R1/R6/fullκ3h16costs.",
              '- Route/tail/cost-moment certificate, global accuracy, D22 và dry-runB vẫn chưa đóng; n/root/CF giữ null.','',
              'Kiểm sau run: cut_value trong experiments/V13_step1/regime.py bị thiếu trong explicit45-file manifest; post_run_dependency_check.json xác nhận file khớp runcommit. Đây là evidence bổ sung sau run,không phải preregistered coverage. Fullaudit cần complete dependency closure.','',
              '## Lệnh và file','',
              '```bash',
              '.venv/bin/python -m pytest tests/test_r3r_numerics_budget.py -q',
              '.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_7/numerics_logs/full_suite_final.xml',
              '.venv/bin/python -m experiments.R3R_07_numerics.run --prereg experiments/R3R_07_numerics/prereg.json --out results/R3R_numerics/20261029_01',
              '.venv/bin/python -m experiments.lessons.report_r3r_numerics',
              '```','',
              'Tests trước calibration: **595full/8targeted PASS**. Test suite595 chạy sau khi thêm guard direct-worker không được mở global schedule. Giữ snapshot594 trước đó.','',
              '- Prereg/code: `experiments/R3R_07_numerics/` (run.py,worker.py,budget.py,prereg.json/md).',
              '- CSV: `results/R3R_numerics/20261029_01/metrics.csv`.',
              '- JSON: `results/R3R_numerics/20261029_01/summary.json`, `verification.json`, từng job/result/resource/receipt.',
              '- Logs/phase: từng job/stdout.log, progress.jsonl và `results/lessons/l3r_7/numerics_logs/calibration.log`.',
              '- Không tạo chart/PDF, final numerics tag/receipt hoặc CF list.','',
              '## Bước tiếp theo theo evidence','',
              'Giữ card/contract v1.3 và stop rule. Cần engineering/audit thuật toán stationary ở resolution đã khóa, rồi full numerical audit trước khi khóav1.3.1. Không tự đổi measure/rounding để làm kết quả chạy được. Nới ceiling hoặc method mới cần version/DL và giữ kết quả lần này. Phase4 HOLD/G1 giữ nguyên.']
    report=Path('results/lessons/l3r_7/numerics_report.md')
    with report.open('x') as f:f.write('\n'.join(lines)+'\n')
    hashes={str(p):digest(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='artifact_index.json'}
    write_once(raw/'artifact_index.json',hashes)
    print(json.dumps({k:v for k,v in audit.items() if k!='rows'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
