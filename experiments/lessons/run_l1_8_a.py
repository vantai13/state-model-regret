"""Doan Van Tai — deterministic verification of L1.8 Part A only.

Run .venv/bin/python -m experiments.lessons.run_l1_8_a.
No RNG, new seeds, contrast-grid selection or contract-v1 freeze.
"""
import argparse
import csv
import contextlib
import traceback
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict
from datetime import datetime
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.lessons.l0_6_timescale import effective_age_s
from experiments.lessons.l1_8_reference import boundary_comparison, fluid_interval
from experiments.lessons.l1_8_slots import (
    ANCHOR_A, ANCHOR_B, CANDIDATE_DT, T_mode_from_lambda, anchor_card,
    p_stay, persistence_R1, persistence_R2, to_slots,
)
from experiments.lessons.run_l1_2 import write_csv

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path('/home/vantai/.codex/attachments/9febf793-2885-436f-9482-934cd26287f2/Pasted text.txt')
CORE='tests/test_l1_8_slots.py'
EXTRA='tests/test_l1_8_boundaries.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value):
    if isinstance(value,F): return str(value)
    if isinstance(value,float) and not math.isfinite(value): return str(value)
    if isinstance(value,dict): return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [clean(v) for v in value]
    return value


def write_json(path,value):
    path.write_text(json.dumps(clean(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def tests(out,name,targets):
    command=[sys.executable,'-m','pytest','-q','--color=no',f'--junitxml={out/name}.xml',*targets]
    proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/f'{name}.txt').write_text(proc.stdout+proc.stderr)
    cases=list(ET.parse(out/f'{name}.xml').iter('testcase'))
    failed=[c.attrib['name'] for c in cases if c.find('failure') is not None]
    errors=[c.attrib['name'] for c in cases if c.find('error') is not None]
    skips=[c.attrib['name'] for c in cases if c.find('skipped') is not None]
    measured=dict(command=command,returncode=proc.returncode,total=len(cases),failed=failed,errors=errors,
                  skipped=skips,passed=len(cases)-len(failed)-len(errors)-len(skips),log=f'{name}.txt',junit=f'{name}.xml')
    if proc.returncode or failed or errors or skips:
        write_json(out/'failed_run.json',measured)
        raise RuntimeError(f'Tests failed: {name}.txt')
    print(f"{name}: {measured['passed']}/{measured['total']} PASS",flush=True)
    return measured


def persistence_table(out):
    rows=[]
    target=math.exp(-4.08)
    for dt in (F(3,250),F(3,500),F(3,1000)):
        n,error=to_slots(F(51,250),dt)
        assert error==0
        for law,fn in (('R1',persistence_R1),('R2',persistence_R2)):
            lam=fn(dt,F(1,10))
            p=p_stay(lam)
            ph=p_stay(fn(dt/2,F(1,10)))
            semigroup_error=ph**2+(1-ph)**2-p
            corr=lam**n
            row=dict(law=law,dt_s=dt,T_mode_s=F(1,10),age_s=F(51,250),age_slots=n,
                     lambda_slot=lam,p_stay=p,p_leave=1-p,sampled_run_mean_s=float(dt)/(1-p),
                     correlation=corr,target_correlation=target,correlation_error=corr-target,
                     semigroup_error=semigroup_error,stationary_on=.5*p+.5*(1-p))
            if law=='R2':
                assert math.isclose(corr,target,rel_tol=1e-12,abs_tol=1e-14)
                assert abs(semigroup_error)<1e-14
                assert math.isclose(T_mode_from_lambda(lam,dt),.1,rel_tol=1e-12)
            else:
                assert abs(semigroup_error)>1e-6
                assert math.isclose(row['sampled_run_mean_s'],.1,rel_tol=1e-12)
            rows.append(row)
    write_csv(out/'persistence_comparison.csv',rows)
    stale=[]
    for dt in (.01,.005):
        stale.append(dict(dt_s=dt,p_leave_fixed=.1,T_R1_s=dt/.1,T_R2_s=T_mode_from_lambda(.8,dt)))
    write_csv(out/'fixed_probability_mistake.csv',stale)
    variant=dict(lambda_coarse=.25,T_mode_slot_units=T_mode_from_lambda(.25,1),
                 lambda_half=persistence_R2(.5,T_mode_from_lambda(.25,1)),p_stay_half=.75)
    return dict(rows=rows,fixed_probability=stale,variant=variant)


def fluid_tables(out):
    summary,paths=[],[]
    for name,q0,rate in (('drain',F(2),F(1)),('rise',F(0),F(5))):
        for dt in (F(1),F(1,2),F(1,4),F(1,8)):
            rows=boundary_comparison(q0,[rate]*int(1/dt),F(3),dt)
            paths.extend(dict(example=name,dt_s=dt,**r) for r in rows)
            area=sum(r['fluid_area'] for r in rows)
            cost=sum(r['d13'] for r in rows)
            correction=sum(r['crossing_correction'] for r in rows)
            assert area==1 and correction==0
            summary.append(dict(example=name,dt_s=dt,fluid_cost=area,d13_cost=cost,error=cost-area,
                                boundary_term=dt*(rows[-1]['q_end']-q0)/2,crossing_correction=correction))
    grid=[]
    for q,r,s,dt in product((0,1,2,5),(0,1,3,5),(1,3),(F(1),F(1,2),F(1,4))):
        row=boundary_comparison(F(q),[F(r)],F(s),dt)[0]
        assert row['crossing_correction']>=0
        assert row['error']==row['boundary_term']+row['crossing_correction']
        grid.append(dict(dt_s=dt,**row))
    assert len(grid)==96
    write_csv(out/'fluid_convergence.csv',summary)
    write_csv(out/'fluid_paths.csv',paths)
    write_csv(out/'boundary_grid.csv',grid)
    crossing=boundary_comparison(F(1),[F(0)],F(2),F(1))[0]
    assert (crossing['fluid_area'],crossing['error'],crossing['boundary_term'],crossing['crossing_correction'])==(F(1,4),F(-1,4),F(-1,2),F(1,4))
    canonical=[]
    for a,rA,rB in (('Stay',F(3),F(0)),('Switch',F(1),F(2))):
        ra=boundary_comparison(F(2),[rA]*2,F(3),F(1))
        rb=boundary_comparison(F(0),[rB]*2,F(3),F(1))
        canonical.append(dict(action=a,d13=sum(r['d13'] for r in ra+rb),fluid=sum(r['fluid_area'] for r in ra+rb)))
    assert [(r['d13'],r['fluid']) for r in canonical]==[(4,4),(0,1)]
    write_csv(out/'canonical_all_off.csv',canonical)
    cumulative=[]
    for h in (10,20):
        _,area=fluid_interval(F(10),F(1),F(3),F(h))
        assert area==25
        cumulative.append(dict(h_s=h,cumulative_packet_s=area,time_average_packet=area/h))
    write_csv(out/'cumulative_vs_average.csv',cumulative)
    return dict(convergence=summary,grid_cases=len(grid),boundary_violations=0,crossing_example=crossing,
                canonical=canonical,cumulative=cumulative)


def rounding_tables(out):
    grid=[]
    for dt,n,offset in product((F(3,250),F(3,500),F(3,1000)),range(1,101),(F(-49,100),F(0),F(49,100))):
        seconds=(n+offset)*dt
        got,error=to_slots(seconds,dt)
        assert got==n and error==got*dt-seconds and abs(error)<=dt/2
        grid.append(dict(dt_s=dt,seconds_requested=seconds,slots=got,seconds_represented=got*dt,error_s=error,error_over_dt=error/dt))
    write_csv(out/'round_trip_grid.csv',grid)
    cards=[]
    for anchor in (ANCHOR_A,ANCHOR_B):
        for divisor in (1,2,4):
            cards.append(anchor_card(anchor,CANDIDATE_DT[anchor.name]/divisor))
    write_csv(out/'anchor_refinements.csv',cards)
    # Only candidate conversion coordinates, not contrast/dt acceptance tests.
    a=anchor_card(ANCHOR_A,CANDIDATE_DT['a'])
    b=anchor_card(ANCHOR_B,CANDIDATE_DT['b'])
    write_csv(out/'anchor_cards.csv',[a,b])
    snmp_age=effective_age_s(F(30),F(0),F(30))
    snmp=dict(period_s=30,window_s=30,latency_s=0,effective_age_s=snmp_age,
              T_drain_pre_B_s=F(3,5),drain_over_age=F(3,5)/snmp_age,
              observation='counter-difference rate, not backlog; does not satisfy D8 backlog schema')
    leftover=fluid_interval(F(100),F(750),F(2500,3),F(3,5))[0]
    assert leftover==50
    extra100=dict(link_bps=10**8,t_pkt_s=F(3,25000),capacity_packet_slot=10,dt_candidate_s=F(3,2500),
                  T_mode_s=F(1,20),p_leave_R1=1-p_stay(persistence_R1(F(3,2500),F(1,20))),
                  p_leave_R2=1-p_stay(persistence_R2(F(3,2500),F(1,20))))
    return dict(cards=[a,b],refinements=cards,round_trip_cases=len(grid),round_trip_violations=0,
                snmp=snmp,B_constant_mean_load_remaining_at_h_packet=leftover,self_check_100M=extra100)


def plot(out,fluid,persistence):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for name in ('drain','rise'):
        rows=[r for r in fluid['convergence'] if r['example']==name]
        axes[0].plot([float(r['dt_s']) for r in rows],[float(r['d13_cost']) for r in rows],'o-',label=name)
    axes[0].axhline(1,color='black',linestyle='--',label='Exact fluid area')
    axes[0].set(xlabel='dt (s)',ylabel='Cost (packet s)',title='E1: endpoint occupancy versus fluid area')
    for name in ('R1','R2'):
        rows=[r for r in persistence['rows'] if r['law']==name]
        axes[1].plot([1000*float(r['dt_s']) for r in rows],[r['correlation'] for r in rows],'o-',label=name)
    axes[1].set(xlabel='dt (ms)',ylabel='Mode correlation at 204 ms',title='R2 preserves physical-time correlation')
    for ax in axes:
        ax.grid(alpha=.25)
        ax.legend()
    fig.savefig(out/'slot_and_persistence.png',dpi=160)
    plt.close(fig)


def render(result):
    cards=result['conversions']['cards']
    lines=['# L1.8 Part A — từ giây tới slot','',
           f"Người thực hiện: **Doan Van Tai** · {result['run_time_asia_saigon']}.",'',
           'Chỉ triển khai PartA: conversion module,R2 candidate,thẻ hai neo và deterministic verification. '
           'Không đổi contract-v0; chưa khóa Δt cuối hoặc contract-v1,không chạy PartsB–E/Phase3 A01.','',
           '## Hai thẻ đổi đơn vị','',
           '| Neo | t_packet | Δt ứng viên | c / nền trước | Tuổi slots → giây | Sai số tuổi | H | Tdrain pre B | Tdrain post B |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in cards:
        post='chưa khai báo' if c['T_drain_post_B_switch_s'] is None else str(float(c['T_drain_post_B_switch_s']))+'s'
        lines.append(f"| {c['anchor']} | {1e3*float(c['t_pkt_s']):g}ms | {1e3*float(c['dt_candidate_s']):g}ms | "
                     f"{c['capacity_packet_slot']} / {c['background_pre_packet_slot']} packet/slot | "
                     f"{c['age_slots']} → {float(c['age_represented_s']):g}s | {100*float(c['age_error_relative']):g}% | "
                     f"{c['H']} | {float(c['T_drain_pre_B_s']):g}s | {post} |")
    lines += ['', 'a:1Gb/s,b:10Mb/s,1500byte,qB0=100,rho_pre=.8. Tuổi+act5ms/.2s,h6ms/.6s '
              'là minh hoạ,không là end-to-end measurement. T_mode của a chưa khai báo. '
              'b:T_mode=.1s chưa có nguồn,rho_post=.9 là scenario giả định. '
              'Không có full ON/OFF on/off rates hoặc D tại các neo; aggregate rho chưa xác định law. '
              'q0=100 dùng cho hai diagnostic pre/post,không phải một episode đã tiến qua prehistory.','',
              f"b: ratio pre/age từ3 xuống **{float(cards[1]['z_pre_represented']):.6f}**,zone①→② sau rounding. "
              f"h/Tpost=**{float(cards[1]['h_over_post_drain']):g}**. Constant-load fluid rho_post=.9 cho "
              '**50 packet** còn lại sau .6s; đây không là E[q] của ON/OFF queue. '
              'Không dùng ratio hoặc zone làm chứng minh gain dương.','',
              '## R1 và R2','',
              'R2 được dùng trong draft:lambda=exp(-2dt/T),p_stay=(1+lambda)/2,giữ correlation '
              'qua tuổi vật lý. R1 giữ mean sampled run duration nhưng không semigroup. '
              'Quyết định research cuối cùng ở thẻ PartD/E.','',
              '| Luật | Δt(ms) | Age slots | P leave | Corr tại204ms | Mean sampled run(ms) | Semigroup residual |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for r in result['persistence']['rows']:
        lines.append(f"| {r['law']} | {1e3*float(r['dt_s']):g} | {r['age_slots']} | {float(r['p_leave']):.9f} | "
                     f"{float(r['correlation']):.9f} | {1000*r['sampled_run_mean_s']:.6f} | {float(r['semigroup_error']):.3g} |")
    lines += ['', 'R2 correlation exact formula exp(−4.08),stationary ON1/2; mean sampled run≈112.48ms '
              'ở dt12ms so holding100ms vì bỏ các lần lật rồi quay lại. '
              'R1 correlation thay đổi theo dt; đó là negative control cố ý,không là test failure. '
              'Giữ leave=.1 khi đổi dt10→5ms làm T_R1 100→50ms,T_R2≈89.628→44.814ms.','',
              'lambda0 (canonical p=s1/2) không có finite positive CTMC holding time. '
              'lambda1 có embedding suy biến Q0/holding vô hạn; inverse helper từ chối vì ngoài finite-positive scope, '
              'không gọi nó là không nhúng được tuyệt đối. CTMC skeleton không làm arrivals tích phân trong slot chính xác.','',
              '## E1: diện tích backlog và điểm cuối','',
              '| Example | Δt | D13 | Fluid area | Error |', '|---|---:|---:|---:|---:|']
    for r in result['fluid']['convergence']:
        lines.append(f"| {r['example']} | {r['dt_s']} | {r['d13_cost']} | {r['fluid_cost']} | {r['error']} |")
    lines += ['', 'Đơn vị packet·s,interval1s. Queue drain q0=2,rate1,service3;rise q0=0,rate5,service3. '
              'Constant rate trong slot cho đúng endpoint backlog với plantL1.2. D13 sai diện tích,hội tụ về1 ở hai hướng.','',
              '**Làm rõ công thức crossing:** nếu không chạm0 bên trong slot,error=dt(QH−Q0)/2 chính xác. '
              'Nếu q0=1,net−2,dt1,fluidarea1/4,D13=0,error−1/4,boundaryterm−1/2. '
              '**Correction=+1/4**,không phải số hạng âm bổ sung so với telescoping. '
              'Tổng error của slot drain vẫn âm. [boundary_grid.csv](boundary_grid.csv) kiểm96 intervals,0 vi phạm.','',
              'Canonical xd,all-off,H2,dt1:Stay D13/fluid4/4,Switch0/1;gap−4 so−3. '
              'Đây là branch diagnostic,không thay expected J hay objective của các lesson cũ. '
              'Cumulative q=(10−2t)+ cho area25 ở h10 và20;time-average2.5 và1.25. '
              'Không suy GS cumulative về0 khi tăng h từ ví dụ time-average.','',
              '## E3 và verification','',
              '900 round-trip cases có0 vi phạm |error|≤dt/2; nearest/ties-to-even được ghi rõ. '
              'Default reject duration tròn thành0slot; explicit allow_zero chỉ dành cho duration thật0 (D8 age0). '
              'anchor_refinements.csv ghi12/6/3ms và.12/.06/.03ms,cùng physical durations; '
              'ratio thay đổi chỉ qua rounding,không gọi đây là PartB contrast acceptance.','']
    for name,s in result['tests'].items():
        lines.append(f"- {name}: **{s['passed']}/{s['total']} PASS**,log`{s['log']}`,JUnit`{s['junit']}`.")
    lines += ['', 'Preflight13/13 PASS trước runner; sau đó thêm1 test rescale candidate coordinates. '
              'Bốn core từ bài,10 test bổ sung; suite trước97 nên tổng111. '
              'Bất biến contrast chuẩn hoá sau rescale vẫn chờ Phase3/PartB,Cref chưa chọn.','',
              'SNMP P=W30s,L0:tau_eff30s,Tpre/age=.02. Đây là rate từ counter,không đáp ứng '
              'backlog observation D8; đổi đơn vị không sửa schema. Self-check100Mb/s,c10,T50ms lưu '
              'dt1.2ms và hai leave probabilities trong results; đây là worked reference,không là bài kín sách.','',
              '## Giới hạn và nguồn','',
              'Con số GS.930→.534 (~43%),Gamma+.078 chỉ do tài liệu trích PHASE_1. '
              'Không có full configuration/protocol ở repo nên chưa tái lập trong PartA; '
              'không báo chúng là số chạy mới và không gán phần43% choE1 hayE2. '
              'Weak mode correlation không tự chứng minh mode-visibility gain chiếm ưu thế.','',
              '[Ward Whitt,CTMC notes §2–3](https://www.columbia.edu/~ww2040/3106F11/CTMCchapter121906.pdf) '
              'hỗ trợ CTMC có holding mũ và Chapman–Kolmogorov semigroup. R2 đối xứng được dẫn '
              'từ ODE trong spec và kiểm bằng số. Đây không xác nhận traffic mạng thật tuân law đó. '
              'Nguồn Willinger1997 mà bài nhớ lại: DOI10.1109/90.554723;publisher chặn truy cập '
              '(IEEE cần JavaScript,ACM403),chưa kiểm nội dung primary và không dùng nó xác nhận AA2 workload.','',
              'Mô hình gốc đề xuất là reflected fluid queue điều biến CTMC. Δt/2 chỉ kiểm sai số '
              'với mô hình đó,chưa validate packet network; còn E2 mode changes nội slot chưa được '
              'mô phỏng trong PartA. Code không sửaD13 thành fluid area. '
              'Chưa chốt Δt,H,lướiD,Cref,epsilon,confirmation hoặccontractv1. '
              'G1,V3/V10/V11,HOLDPhase4 giữ nguyên; bài tự làm và legacy debt chưa được ghi Đạt.','',
              '## File và tái chạy','',
              '```bash','.venv/bin/python -m experiments.lessons.run_l1_8_a',
              '.venv/bin/python -m experiments.lessons.run_l1_8_a --output-dir /tmp/l1_8_a-rerun','```','',
              '| Artifact | Nội dung |','|---|---|',
              '| [config.json](config.json),[results.json](results.json) | Inputs,source/input hashes,exact và float metrics,actual commands |',
              '| [anchor_cards.csv](anchor_cards.csv),[anchor_refinements.csv](anchor_refinements.csv) | Hai thẻ và rounding theo dt |',
              '| [persistence_comparison.csv](persistence_comparison.csv),[fixed_probability_mistake.csv](fixed_probability_mistake.csv) | R1/R2,correlation,run duration,semigroup |',
              '| [fluid_convergence.csv](fluid_convergence.csv),[fluid_paths.csv](fluid_paths.csv),[boundary_grid.csv](boundary_grid.csv) | E1 và crossing correction |',
              '| [canonical_all_off.csv](canonical_all_off.csv),[cumulative_vs_average.csv](cumulative_vs_average.csv),[round_trip_grid.csv](round_trip_grid.csv) | Branch gap,cumulative,900round trips |',
              '| [slot_and_persistence.png](slot_and_persistence.png) | Hình từ các số đã tính |',
              '| lesson.txt,boundaries.txt,full_suite.txt,*.xml,run_output.txt | Logs và JUnit thật |',
              '| [artifact_checks.json](artifact_checks.json),[artifact_manifest.json](artifact_manifest.json) | Đọc lại CSV,hashes,manifest |','',
              'Source:experiments/lessons/l1_8_slots.py,l1_8_reference.py,run_l1_8_a.py; '
              'tests/test_l1_8_slots.py,test_l1_8_boundaries.py. '
              'Card/spec tại notes/lessons/L1.8A_experiment_card.md vàL1.8A_slot_model_spec.md. '
              f"Python{result['python']};wall time{result['elapsed_seconds']:.3f}s. Không RNG/seed,không CI lấy mẫu.",'']
    return '\n'.join(lines)


def audit(out,result):
    counts={}
    for filename,expected in (('round_trip_grid.csv',900),('boundary_grid.csv',96),('anchor_cards.csv',2),('persistence_comparison.csv',6)):
        with (out/filename).open() as f: rows=list(csv.DictReader(f))
        assert len(rows)==expected
        if filename=='round_trip_grid.csv':
            for r in rows:
                dt,seconds=F(r['dt_s']),F(r['seconds_requested'])
                assert int(r['slots'])*dt-seconds==F(r['error_s']) and abs(F(r['error_s']))<=dt/2
        elif filename=='boundary_grid.csv':
            for r in rows:
                assert F(r['error'])==F(r['boundary_term'])+F(r['crossing_correction'])
                assert F(r['crossing_correction'])>=0
        counts[filename]=len(rows)
    for path,digest in result['config']['source_hashes'].items():
        assert sha(ROOT/path)==digest,path
    return dict(status='PASS',CSV_rows_checked=counts,source_hashes_checked=len(result['config']['source_hashes']),new_rng_draws=0)


def execute(out):
    start=time.perf_counter()
    source=[ROOT/'experiments/lessons/l1_8_slots.py',ROOT/'experiments/lessons/l1_8_reference.py',Path(__file__),
            ROOT/CORE,ROOT/EXTRA,ROOT/'experiments/lessons/l1_2_queue.py',ROOT/'experiments/lessons/l0_6_timescale.py',
            ROOT/'notes/01_definitions.md',ROOT/'notes/theory/T00_timescale_sanity.md',
            ROOT/'notes/lessons/L1.8A_experiment_card.md',ROOT/'notes/lessons/L1.8A_slot_model_spec.md']
    config=dict(author='Doan Van Tai',scope='L1.8 Part A only',anchors=[asdict(ANCHOR_A),asdict(ANCHOR_B)],
                dt_candidates_s=CANDIDATE_DT,persistence_law_candidate='R2 symmetric finite-positive CTMC',
                rounding='nearest/ties-to-even; positive durations must not round to zero',
                float_check_tolerances=dict(relative=1e-12,absolute=1e-14),
                seed=None,random_sampling=False,dt_final_locked=False,contract_v1_locked=False,
                PartB_acceptance_run=False,Phase3_contrast_scale_invariance_checked=False,
                input=dict(path=str(INPUT),sha256=sha(INPUT)),source_hashes={str(p.relative_to(ROOT)):sha(p) for p in source},
                base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    write_json(out/'config.json',config)
    ts={}
    for name,targets in [('lesson',[CORE]),('boundaries',[EXTRA]),('full_suite',['tests/'])]:
        ts[name]=tests(out,name,targets)
    assert ts['lesson']['total']==4 and ts['boundaries']['total']==10
    persistence=persistence_table(out)
    fluid=fluid_tables(out)
    conversions=rounding_tables(out)
    result=dict(author='Doan Van Tai',run_time_asia_saigon=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                command=[sys.executable,'-m','experiments.lessons.run_l1_8_a','--output-dir',str(out)],
                config=config,tests=ts,persistence=persistence,fluid=fluid,conversions=conversions,python=platform.python_version(),
                elapsed_seconds=time.perf_counter()-start)
    plot(out,fluid,persistence)
    result['artifact_checks']=audit(out,result)
    write_json(out/'artifact_checks.json',result['artifact_checks'])
    write_json(out/'results.json',result)
    (out/'report.md').write_text(render(result))
    for c in conversions['cards']:
        print(f"Anchor {c['anchor']}: dt={1000*float(c['dt_candidate_s']):g}ms,c={c['capacity_packet_slot']},H={c['H']},"
              f"age_slots={c['age_slots']},age_error={100*float(c['age_error_relative']):g}%,z={float(c['z_pre_represented']):.9f}")
    for r in persistence['rows']:
        print(f"{r['law']} dt={1000*float(r['dt_s']):g}ms:corr={float(r['correlation']):.9f},leave={float(r['p_leave']):.9f},run_ms={1000*r['sampled_run_mean_s']:.6f}")
    print('96 boundary cases + 900 round-trip cases: PASS; crossing correction=+1/4; no RNG/seeds')
    print(f'Output: {out}')


class Tee:
    def __init__(self,*handles): self.handles=handles
    def write(self,value):
        for h in self.handles: h.write(value)
        return len(value)
    def flush(self):
        for h in self.handles: h.flush()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_a')
    out=parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run_output.txt').open('w') as log:
        with contextlib.redirect_stdout(Tee(sys.stdout,log)),contextlib.redirect_stderr(Tee(sys.stderr,log)):
            try:
                execute(out)
            except Exception:
                traceback.print_exc()
                raise SystemExit(1)
    entries=[dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
             if p.is_file() and p.name!='artifact_manifest.json']
    write_json(out/'artifact_manifest.json',dict(author='Doan Van Tai',files=entries))


if __name__=='__main__': main()
