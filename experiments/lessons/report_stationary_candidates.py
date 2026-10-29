"""Doan Van Tai — audit saved deterministic numerical candidates, no engine calls."""
import csv
from datetime import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from experiments.R3R_07_confirmation.common import digest,git,write_once
from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_05_contract.freeze import verify_lock
from experiments.R3R_06_cards.verify_cards import verify


def candidate(number):
    folder=Path(f'results/R3R_numerics/20261029_candidate_{number:02}')
    name='prereg.json' if number==1 else f'prereg_{"balanced" if number>=5 else "sparse"}_candidate_{number:02}.json'
    prereg=Path('experiments/R3R_07_fast_stationary')/name
    cfg=verify_prereg(prereg)
    attempt=json.loads((folder/'attempt.json').read_text())
    assert attempt['prereg_sha256']==digest(prereg)
    assert git('show',attempt['source_commit']+':'+str(prereg))==prereg.read_bytes()
    summary=json.loads((folder/'summary.json').read_text())
    resources=summary['resources'];result=summary['result'] or {}
    completed=result.get('status')=='COMPLETED' and resources['exit_code']==0
    job=cfg['stationary_jobs'][0]
    if completed:
        assert result['id']==job['id'] and result['kind']=='stationary_only'
        assert result['joint_costs_or_contrasts_computed'] is False
        assert float(result['law_error_upper'])<=1e-10
        assert max(result['posterior_errors'])<=1e-8
        assert result['certificate']['digits']==80
        assert result['stable_terms']==result['increments'][1]
        assert result['certificate']['physical_buffer'] is False
        if number>=5:
            environment=json.loads((folder/job['id']/'environment.json').read_text())
            assert environment['matches_preregistered_versions'] is True
            assert environment['python']==cfg['execution_platform']['python']
            assert environment['packages']==cfg['execution_platform']['packages']
    for p,h in cfg['source_sha256'].items():
        assert __import__('hashlib').sha256(git('show',attempt['source_commit']+':'+p)).hexdigest()==h,p
    row=dict(candidate=number,id=job['id'],backend=cfg.get('execution_platform',{}).get('backend','local WSL'),status='COMPLETED' if completed else 'UNRESOLVED',
             cpu_seconds=resources['cpu_seconds'],wall_seconds=resources['wall_seconds'],
             peak_rss_MiB=max(resources['sampled_peak_rss_bytes'],result.get('peak_rss_bytes',0))/1024**2,
             stop_reason=resources.get('stop_reason') or result.get('error_type') or '',
             law_error_upper=result.get('law_error_upper'),posterior_error_max=max(result.get('posterior_errors',[0])) if completed else None,
             quantiles=json.dumps(result.get('quantiles')),source_commit=attempt['source_commit'],
             prereg=str(prereg),raw=str(folder),certificate_method=result.get('certificate',{}).get('method'))
    assert summary['CF_generated']==0 and summary['Phase4']=='HOLD'
    return row,result


def main():
    out=Path('results/lessons/l3r_7/extended_capacity')
    rows=[];results={}
    for number in (1,2,3,4,5,6,7):
        folder=Path(f'results/R3R_numerics/20261029_candidate_{number:02}')
        if not folder.exists():continue
        row,data=candidate(number);rows.append(row);results[number]=data
    assert {1,2}<=set(results),'first two attempts required'
    old=json.loads(Path('results/R3R_numerics/20261029_02/CAL_RATE_100_A/result.json').read_text())
    baseline=json.loads(Path('results/R3R_numerics/20261029_02/CAL_RATE_100_A/resource.json').read_text())
    parity=[]
    for number in (1,3,5):
        if number not in results:continue
        new=results[number]
        ok=new.get('status')=='COMPLETED' and new['quantiles']==old['quantiles']
        if ok:
            assert new['unit']==old['unit'] and new['increments']==old['increments']
            assert float(new['law_error_upper'])<=1e-10 and max(new['posterior_errors'])<=1e-8
        parity.append(dict(candidate=number,quantiles_match=ok,
                           posterior_error_bounds_match=new.get('posterior_errors')==old['posterior_errors'],
                           posterior_point_estimates_compared=False,
                           note='worker saves error bounds only, not point posterior values'))
        assert ok,parity[-1]
    if 4 in results:
        assert results[2].get('status')=='COMPLETED' and any(p['candidate']==3 and p['quantiles_match'] for p in parity)
        first=json.loads(Path('results/R3R_numerics/20261029_candidate_04/CAL_RATE_1000_B/progress.jsonl').read_text().splitlines()[0])
        prior=json.loads(Path('results/R3R_numerics/20261029_candidate_03/CAL_RATE_100_A/progress.jsonl').read_text().splitlines()[-1])
        assert first['utc']>prior['utc']
    contract=verify_lock();card=verify();assert card['status']=='PASS'
    xml=out/'balanced_full_suite.xml'
    suites=list(ET.parse(xml).getroot().iter('testsuite'))
    assert sum(int(s.get('tests',0)) for s in suites)==633
    assert all(int(s.get(k,0))==0 for s in suites for k in ('failures','errors','skipped'))
    with (out/'candidate_metrics.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    complete=sum(r['status']=='COMPLETED' for r in rows)
    result=dict(owner='Doan Van Tai',date=datetime.now(ZoneInfo('Asia/Saigon')).isoformat(),
                status='VERIFIED_SAVED_NUMERICAL_CANDIDATES_NOT_ADOPTED',attempted=len(rows),completed=complete,
                candidate_rows=rows,medium_reference_parity=parity,
                medium_baseline_wall_seconds=baseline['wall_seconds'],
                medium_candidate01_wall_ratio=baseline['wall_seconds']/rows[0]['wall_seconds'],
                full_tests=633,frozen_contract_inputs=len(contract['source_sha256']),frozen_card_files=card['files'],
                source_and_prereg_checks='current files and execution commit verified',
                CF_generated=0,n=None,confirmation_root=None,Phase4='HOLD',
                numerical_adoption=False,global_accuracy_audit_completed=False,
                timing_scope='one attempt per point/version; concurrent baseline possible, CPU and wall reported separately; no p95 full-regime timing',
                GCP_used=any(r['candidate']>=6 for r in rows),GCP_started_by_agent=False,
                balanced_profile_attempts=sum(r['candidate']>=5 for r in rows),
                balanced_profile_completed=sum(r['candidate']>=5 and r['status']=='COMPLETED' for r in rows),
                not_run_by_prior_stop_rule=[3,4],
                medium_candidate05_wall_ratio=baseline['wall_seconds']/next(r['wall_seconds'] for r in rows if r['candidate']==5) if 5 in results else None)
    if result['GCP_used']:
        cloud=json.loads((out/'gcp/preflight.json').read_text())
        assert cloud['status']=='PASS' and cloud['tests']==633
        suites=list(ET.parse(out/'gcp/full_suite.xml').getroot().iter('testsuite'))
        assert sum(int(s.get('tests',0)) for s in suites)==633
        assert all(int(s.get(k,0))==0 for s in suites for k in ('failures','errors','skipped'))
        result['cloud_full_tests']=633
    write_once(out/'candidate_verification.json',result)
    lines=['# L3R.7 — kết quả thử cải tiến bộ tính stationary','',
           'Người phụ trách: **Doan Van Tai**. Các candidate ở experiments, chưa đưa vào src hoặc confirmation.','',
           'Giữ nguyên infinite queue, tham số plant, rounding, 80 chữ số và ngưỡng sai số law 1e-10/posterior 1e-8. Candidate02–04 dùng cách đánh giá certificate mới; không gọi đó là certificate code gốc.','',
           '| Candidate | Probe / máy | Kết quả | CPU(s) | Wall(s) | Peak RSS(MiB) | Law error upper |',
           '|---|---|---|---:|---:|---:|---:|']
    for r in rows:
        error=f"{float(r['law_error_upper']):.3g}" if r['law_error_upper'] else '—'
        lines.append(f"|{r['candidate']}|{r['id']} / {r['backend']}|{r['status']} {r['stop_reason']}|{r['cpu_seconds']:.3f}|{r['wall_seconds']:.3f}|{r['peak_rss_MiB']:.1f}|{error}|")
    lines+=['',f"Baseline medium: **{baseline['wall_seconds']:.3f}s**; candidate01 **{rows[0]['wall_seconds']:.3f}s**, tỉ số wall **{result['medium_candidate01_wall_ratio']:.2f}×** trong các attempt đã đo, không phải p95.",
            'Candidate02 trước đó không chứng nhận được normalizer khác zero; giữ nguyên ERROR và không chạy03/04. Balanced05/06/07 là phiên bản đăng ký sau lỗi này, không thay nhãn hoặc ghi đè raw cũ.',
            'Quantiles medium đối chiếu chính xác; posterior chỉ lưu và kiểm error bounds, chưa đối chiếu trực tiếp point posterior values.','',
            f"Candidate05 medium wall ratio: **{result['medium_candidate05_wall_ratio']:.2f}×** so baseline cùng máy, một attempt mỗi phiên bản; không phải p95." if 5 in results else '',
            '**633/633 tests PASS** local trước balanced profiles; cloud chạy riêng633tests trước hai probe lớn nếu thực thi. Gồm exact rational balance, dense reference, closed-form TV/tail, interval wrapping và corruption rejection. Các kiểm này không thay full cost/accuracy audit.','',
            'Bản gốc v2 chạy riêng, giữ cả CPU_LIMIT. Nếu một baseline chạm giới hạn thì thời gian hoàn tất thật chưa biết; không coi số ceiling là thời gian giải xong.','',
            '## Phạm vi đã xác nhận','',
            '- Đây là kiểm khả năng tính stationary marginal trên local/GCP như từng dòng. Không tính joint cost/gain/contrast của regime mới hoặc chấm hypothesis card.',
            '- Không tạo n/root/CF, không tag v1.3.1, không thay môi trường của baseline đang chạy.',
            '- Candidate hoàn tất vẫn cần adoption/coverage/full physical cost audit, cost-moment tails, S1 route/array conversion, D22 và dry-run B.',
            '- Bound rất nhỏ ở bảng chỉ áp dụng stationary law; không phải bound sai số toàn bộ physical costs/gains hoặc bằng chứng hypothesis đúng.',
            '- Chưa có timing p95 main/coarse-K/coarse-dt bundle, nên chưa thể ước lượng thời gian toàn confirmation hoặc chọn n.',
            '- Tác giả đã bật GCP; agent không start/resize VM. Môi trường và source được khóa riêng. Không so tốc độ khác máy như thể là speedup do thuật toán.','',
            '## Artifact và lệnh','',
            '`candidate_metrics.csv`, `candidate_verification.json` ở cùng thư mục báo cáo này. Raw các attempt01,02,05,06,07 nếu đã thực thi;03/04 không chạy do02FAIL.','',
            '```bash',
            '.venv/bin/python -m experiments.R3R_07_fast_stationary.run --prereg experiments/R3R_07_fast_stationary/prereg.json --out results/R3R_numerics/20261029_candidate_01',
            '# Với i=02,03,04 đã thực thi, mỗi lệnh một thư mục mới:',
            '.venv/bin/python -m experiments.R3R_07_fast_stationary.sparse_run --prereg experiments/R3R_07_fast_stationary/prereg_sparse_candidate_02.json --out results/R3R_numerics/20261029_candidate_02',
            '.venv/bin/python -m experiments.R3R_07_fast_stationary.balanced_run --prereg experiments/R3R_07_fast_stationary/prereg_balanced_candidate_05.json --out results/R3R_numerics/20261029_candidate_05',
            '# GCP controller chạy các balanced_run06/07 sau preflight633tests:',
            '/home/ubuntu/state-model-regret-r3r7-20261029/venv/bin/python -m experiments.R3R_07_fast_stationary.cloud_pipeline --out /home/ubuntu/state-model-regret-r3r7-20261029',
            '.venv/bin/python -m experiments.lessons.report_stationary_candidates',
            '```','']
    with (out/'candidate_report.md').open('x') as f:f.write('\n'.join(lines))
    for r in rows:
        raw=Path(r['raw']);index=raw/'artifact_index.json'
        if index.exists():
            for p,h in json.loads(index.read_text()).items():assert digest(p)==h,p
        else:write_once(index,{str(p):digest(p) for p in sorted(raw.rglob('*')) if p.is_file() and p.name!='artifact_index.json'})
    print(json.dumps({k:v for k,v in result.items() if k not in ('candidate_rows',)},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
