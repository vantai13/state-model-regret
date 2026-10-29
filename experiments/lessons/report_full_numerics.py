"""Audit exported calibration records; never sample, execute CF, or create a tag."""
import argparse
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from experiments.R3R_05_contract.freeze import verify_lock
from experiments.R3R_06_cards.verify_cards import verify
from experiments.R3R_07_confirmation.common import git,digest
from experiments.R3R_08_population_numerics.checks import check


def main():
    p=argparse.ArgumentParser();p.add_argument('--attempt',choices=['02','03'],required=True);a=p.parse_args()
    folder=Path('results/lessons/l3r_7/full_numerics');raw=Path('results/R3R_population_numerics')/('20261029_'+a.attempt)
    prereg=Path('experiments/R3R_08_population_numerics')/('prereg_'+a.attempt+'.json')
    cfg=json.loads(prereg.read_text());summary=json.loads((raw/'summary.json').read_text())
    attempt=json.loads((raw/'attempt.json').read_text());commit=attempt['source_commit']
    assert attempt['prereg_sha256']==digest(prereg)
    assert git('show',f'{commit}:{prereg}')==prereg.read_bytes()
    for name,h in cfg['source_sha256'].items():assert hashlib.sha256(git('show',f'{commit}:{name}')).hexdigest()==h,name
    export=json.loads((folder/f'export{a.attempt}_verification.json').read_text())
    assert export['status']=='PASS'
    for name,h in export['source_sha256'].items():assert digest(name)==h,name
    suites=list(ET.parse(folder/f'attempt{a.attempt}/full_suite.xml').getroot().iter('testsuite'))
    assert sum(int(s.get('tests',0)) for s in suites)==cfg['full_tests_required']
    assert not any(int(s.get(k,0)) for s in suites for k in ('failures','errors','skipped'))
    contract=verify_lock();card=verify();assert card['status']=='PASS'
    levels=json.loads((raw/'levels.json').read_text());cases={j['id']:j for j in cfg['cases']}
    rows=[];gains=[];errors=[];legacy=0;marginals=0;global_complete=0
    for receipt in summary['receipts']:
        rid,stage=receipt['id'],receipt['stage'];dest=raw/stage/rid
        result=json.loads((dest/'result.json').read_text())
        assert json.loads((dest/'receipt.json').read_text())==receipt
        resource=receipt['resources']
        assert json.loads((dest/'resource.json').read_text())==resource
        completed=receipt['status']=='COMPLETED'
        if completed:
            assert result['status']=='COMPLETED' and resource['exit_code']==0 and receipt['payload_valid']
            if stage=='marginal':
                expected=next(j for j in cfg['legacy_jobs']+cfg['marginals'] if j['id']==rid)
                assert result['kind']==expected['kind']
                if result['kind']=='legacy_anchor':assert result['comparison']['status']=='PASS';legacy+=1
                else:marginals+=1
            else:
                assert result['kind']=='global_calibration'
                assert set(result['levels'])=={f'{K}:{ref}' for K,ref in cfg['stage_levels'][stage]}
                if stage=='base':global_complete+=1
                for key,row in result['levels'].items():
                    assert row==levels[rid][key]
                    gain=dict(id=rid,stage=stage,K=row['K'],ref=row['ref'],Cref_packet_seconds=row['Cref'],arithmetic_pass=row['arithmetic_pass'])
                    for cell,value in row['losses'].items():gain['L'+cell+'_packet_seconds']=value
                    for metric in ('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1'):
                        gain[metric+'_percent_Cref']=100*float(F(row[metric])/F(row['Cref']))
                    gain['maximum_arithmetic_error_percent_Cref']=100*max(float(v) for v in row['normalized_error'].values())
                    gains.append(gain)
        else:errors.append(dict(id=rid,stage=stage,error=result.get('error'),resource_outcome=resource['outcome']))
        rows.append(dict(id=rid,stage=stage,status=receipt['status'],cpu_seconds=resource['cpu_seconds'],wall_seconds=resource['wall_seconds'],peak_rss_MiB=resource['sampled_peak_rss_bytes']/1024**2))
    coverage=[]
    for stage,K,ref in cfg['candidates']:
        checks={rid:check(b,K,ref) for rid,b in levels.items()}
        ready=sum(v['ready'] for v in checks.values())
        coverage.append(dict(K=K,ref=ref,ready=ready,registered_records=len(cases),records_with_any_levels=len(levels),unready_or_uncomputed=len(cases)-ready,
                             checks=checks,scope='fixed calibration designs, not a prevalence estimate under the CF measure'))
    assert summary['CF_generated']==0 and summary['confirmation_root'] is summary['n'] is None
    assert summary['tag_created'] is False
    selected=summary['selected_levels'];timing=None
    if selected:
        selected_checks=next(c for c in coverage if [c['K'],c['ref']]==selected)
        assert selected_checks['ready']==len(cases)
        by_id={t['id']:t for t in summary['timing']}
        groups={name:[by_id[rid]['cold_bundle_planning_seconds'] for rid,j in cases.items() if (j.get('role')=='rational_rate_timing_accuracy')==(name=='rational_rates')]
                for name in ('rational_rates','corners_audit_controls')}
        timing={name:dict(n=len(v),p95_cpu_seconds=float(np.quantile(v,.95,method='higher'))) for name,v in groups.items()}
        timing['planning_p95_cpu_seconds']=max(t['p95_cpu_seconds'] for t in timing.values())
        timing['scope']='max of declared calibration-class p95, cold-component adjusted; no guarantee of CF population p95'
    out=folder/f'report{a.attempt}';out.mkdir(exist_ok=False)
    for name,values in [('metrics',rows),('gains_calibration_only',gains)]:
        if values:
            with (out/(name+'.csv')).open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
    verification=dict(owner='Doan Van Tai',status='PASS_RECORD_INTEGRITY_NUMERICS_READY_FOR_CLOSURE' if selected else 'PASS_RECORD_INTEGRITY_NUMERICS_HOLD',
        numerical_status=summary['status'],source_commit=commit,source_files=len(cfg['source_sha256']),export_files=export['files'],full_tests=cfg['full_tests_required'],
        frozen_contract_files=len(contract['source_sha256']),frozen_card_files=card['files'],legacy_pass=legacy,marginals_pass=marginals,
        base_global_bundles_complete=global_complete,global_cases_registered=len(cases),unique_physical_designs=len({tuple(j['parameters']) for j in cases.values()}),
        completed=sum(r['status']=='COMPLETED' for r in rows),unresolved=len(errors),errors=errors,cpu_seconds=summary['cpu_seconds'],
        measured_peak_rss_MiB=max(r['peak_rss_MiB'] for r in rows),selected_levels=selected,timing=timing,CF_generated=0,n=None,confirmation_root=None,Phase4='HOLD')
    (out/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    (out/'r_coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
    (out/'report.md').write_text(f'''# L3R.7 — full numerical audit {a.attempt}

Người phụ trách: **Doan Van Tai**.

Trạng thái: **{summary['status']}**. Integrity của artifact đã kiểm, không đồng
nghĩa numerical readiness hoặc hypothesis PASS.

| Mục | Kết quả |
|---|---:|
| Full tests trên GCP | {cfg['full_tests_required']} PASS |
| Legacy replay / stationary regression PASS | {legacy} / {marginals} |
| Global bundles base hoàn tất / đăng ký | {global_complete} / {len(cases)} |
| Record chưa giải quyết | {len(errors)} |
| CPU đã đo, giây | {summary['cpu_seconds']:.6f} |
| RSS mẫu lớn nhất, MiB | {verification['measured_peak_rss_MiB']:.3f} |
| Mức số đã chọn | {selected} |
| CF / n / root | 0 / chưa chốt / chưa cấp |

Sai số R1 là diagnostic làm mịn, tách khỏi arithmetic enclosures. Coverage chỉ
trên các designs hiệu chuẩn đã khai; không suy tỷ lệ lỗi toàn population.
Không đổi metric, ngưỡng, card, plant hoặc mở R09/R10.

Lệnh chạy: `python -m experiments.R3R_08_population_numerics.cloud_pipeline
--base /home/ubuntu/state-model-regret-l3r7-full-20261029/attempt{a.attempt}
--prereg {prereg}`. Pipeline chạy pytest trước rồi registered runner.

Raw: `{raw}/`; logs/test XML: `../attempt{a.attempt}/`;
CSV tài nguyên: `metrics.csv`; metric hai phương pháp: `gains_calibration_only.csv`;
kiểm chứng/hash: `verification.json` và `../export{a.attempt}_verification.json`;
R1/coverage: `r_coverage.json`; cấu hình: `{prereg}`.
Không tạo biểu đồ. Phase4 vẫn HOLD.
''')
    print(json.dumps(verification,indent=2))


if __name__=='__main__':main()
