"""Doan Van Tai — run the exposed L1.8B calibration toy at eight resolutions."""
import argparse
import contextlib
import csv
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime
from fractions import Fraction as F
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from experiments.lessons.l1_3_expected_cost import expected_cost, generate_episodes
from experiments.lessons.l1_6_belief import factorial_end_to_end, m0_cost
from experiments.lessons.l1_8_refinement import CELLS, CONTRASTS, pair_check, solve_level, triplet_diagnostic
from experiments.lessons.l1_8_forward_reference import check_level
from experiments.lessons.run_l1_2 import write_csv
from experiments.lessons.run_l1_8_a import Tee, sha, tests, write_json

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path('/home/vantai/.codex/attachments/8975fb43-6d66-4c1a-9c5c-739a5778e312/Pasted text.txt')
LEVELS=(1,2,4,8,16,32,64,128)
MONITORED=CONTRASTS+('Lstar','freshness','mode_visibility','freshness_M1','mode_visibility_M1',
                     'hybrid_freshness','hybrid_mode')
SOURCE_TABLE={
    1:(6.391,.930,0.,0.,4),2:(6.131,.534,.078,0.,6),4:(6.008,.435,.026,0.,14),
    8:(5.964,.375,.014,0.,30),16:(5.946,.339,.015,0.,62),32:(5.939,.321,.016,0.,126),
    64:(5.935,.312,.017,0.,254),128:(5.933,.307,.017,0.,510),
}


def finite_reference(out,solutions):
    refs=[]
    for m in (1,2,4):
        s=solutions[m]
        p=s['params']
        th={k:p[k] for k in ('cA','cB','u','bA','rate_on','rate_off','H')}
        th.update(p_onon=F(float(p['p_onon'])),p_offoff=F(float(p['p_offoff'])))
        D=generate_episodes((2,0),m,th,F(1,2))
        L,_,b=factorial_end_to_end([(-m,(2,0))],th,F(1,2),D)
        assert b==D
        error=0.
        for x,mass in D.items():
            q,mode=int(x[1]*m),int(x[2]=='on')
            assert abs(s['D'][q,mode]-float(mass))<1e-12
            for ai,a in enumerate(('Stay','Switch')):
                J=expected_cost(x,a,th)*p['dt']
                M=m0_cost(x,a,th)*p['dt']
                dj=abs(float(J)-float(s['J'][q,mode,ai]))
                dm=abs(float(M)-float(s['M'][q,mode,ai]))
                error=max(error,dj,dm)
                refs.append(dict(m=m,qA=str(x[0]),qB=str(x[1]),mode=x[2],probability=str(mass),
                                 action=a,J_reference=str(J),J_DP=float(s['J'][q,mode,ai]),
                                 M0_reference=str(M),M0_DP=float(s['M'][q,mode,ai]),J_error=dj,M0_error=dm))
        for c in CELLS:
            assert abs(float(L[c]*p['dt'])-s['summary']['L'+c])<1e-12
        assert error<1e-12
    write_csv(out/'finite_path_reference.csv',refs)
    return dict(levels=[1,2,4],state_action_pairs=len(refs),max_cost_error=max(max(r['J_error'],r['M0_error']) for r in refs))


def record_level(out,s,states,near,precision):
    m=s['summary']['m']
    fine=solve_level(m,dtype=np.longdouble)
    support=s['D']>0
    action_mismatch=0
    for c in CELLS:
        differing=(s['actions'][c]!=fine['actions'][c])&support
        count=int(np.sum(differing))
        action_mismatch+=count
        near.append(dict(m=m,cell=c,**s['near_ties'][c],numerical_alert=s['summary']['numerical_alert']))
        precision.append(dict(m=m,cell=c,action_mismatch=count,mismatch_mass=float(np.sum(s['D'][differing])),
                              max_gap_error=float(np.max(np.abs(s['deltas'][c]-fine['deltas'][c]))),
                              max_J_error=float(np.max(np.abs(s['J']-fine['J']))),
                              max_M0_error=float(np.max(np.abs(s['M']-fine['M']))),
                              longdouble_epsilon=float(np.finfo(np.longdouble).eps)))
    assert action_mismatch==0
    for model in ('M0','M1'):
        c='current_'+model
        qmass=np.sum(s['D'],axis=1)
        differing=(s['current_actions'][model]!=fine['current_actions'][model])&(qmass>0)
        count=int(np.sum(differing))
        assert count==0
        near.append(dict(m=m,cell=c,**s['near_ties'][c],numerical_alert=s['summary']['numerical_alert']))
        precision.append(dict(m=m,cell=c,action_mismatch=count,mismatch_mass=float(np.sum(qmass[differing])),
            max_gap_error=float(np.max(np.abs(s['current_deltas'][model]-fine['current_deltas'][model]))),
            max_J_error=float(np.max(np.abs(s['J']-fine['J']))),max_M0_error=float(np.max(np.abs(s['M']-fine['M']))),
            longdouble_epsilon=float(np.finfo(np.longdouble).eps)))
    assert sum(d['alerted_states'] for d in s['near_ties'].values())==0
    assert np.max(s['M']-s['J'])<1e-10
    for q,mode in zip(*np.where(support)):
        row=dict(m=m,qA=2.,qB=q/m,qB_units=int(q),mode='on' if mode else 'off',probability=float(s['D'][q,mode]),
                 J_stay=float(s['J'][q,mode,0]),J_switch=float(s['J'][q,mode,1]),
                 M0_stay=float(s['M'][q,mode,0]),M0_switch=float(s['M'][q,mode,1]),
                 current_action_M0='Switch' if s['current_actions']['M0'][q] else 'Stay',
                 current_action_M1='Switch' if s['current_actions']['M1'][q] else 'Stay')
        for c in CELLS:
            delta=float(s['deltas'][c][q,mode])
            action=int(s['actions'][c][q,mode])
            row['gap'+c]=delta
            row['action'+c]='Switch' if action else 'Stay'
            row['ell'+c]=float(s['J'][q,mode,action])
            true=float(s['deltas']['11'][q,mode])
            identity=abs(true) if true*delta<0 else (max(0,-true) if delta==0 else 0)
            regret=row['ell'+c]-min(row['J_stay'],row['J_switch'])
            assert abs(identity-regret)<1e-10
        row['I_delta']=row['gap11']-row['gap10']-row['gap01']+row['gap00']
        states.append(row)


def compare_source(out,summaries):
    rows=[]
    for s in summaries:
        given=SOURCE_TABLE[s['m']]
        for metric,value in zip(('Lstar','G_S','Gamma','G_M','support_states'),given):
            actual=s[metric]
            match=(actual==value) if metric=='support_states' else abs(actual-value)<=.0005
            rows.append(dict(m=s['m'],metric=metric,source_display=value,computed=actual,
                             abs_difference=abs(actual-value),within_source_rounding=match))
    write_csv(out/'source_comparison.csv',rows)
    discrepancies=[r for r in rows if not r['within_source_rounding']]
    write_json(out/'source_discrepancies.json',discrepancies)
    given_split={1:(.273,.656),2:(.364,.170),4:(.348,.087),16:(.288,.051),64:(.274,.038)}
    split_rows=[]
    for s in summaries:
        if s['m'] not in given_split: continue
        for label,given,fixed,hybrid in zip(('freshness','mode'),given_split[s['m']],
                (s['freshness'],s['mode_visibility']),(s['hybrid_freshness'],s['hybrid_mode'])):
            split_rows.append(dict(m=s['m'],component=label,source_display=given,fixed_M0=fixed,
                hybrid_midpoint_M1_endpoint_M0=hybrid,fixed_M0_matches_source=abs(fixed-given)<=.0005,
                hybrid_matches_source=abs(hybrid-given)<=.0005))
    write_csv(out/'source_split_comparison.csv',split_rows)
    return discrepancies


def convergence_tables(out,summaries):
    cref=summaries[-1]['Lstar']
    pairs,half,triplets,monitored=[] ,[],[],[]
    for a,b in zip(summaries,summaries[1:]):
        pairs.extend(pair_check(a,b,cref,.01))
        half.extend(pair_check(a,b,cref,.005))
        for metric in MONITORED:
            monitored.append(dict(coarse_m=a['m'],fine_m=b['m'],metric=metric,
                                  coarse=a[metric],fine=b[metric],change_over_Cref=abs(a[metric]-b[metric])/cref))
    for a,b,c in zip(summaries,summaries[1:],summaries[2:]):
        triplets.extend(triplet_diagnostic(a,b,c,metric) for metric in MONITORED)
    write_csv(out/'pair_checks.csv',pairs)
    write_csv(out/'half_tolerance_checks.csv',half)
    write_csv(out/'monitored_changes.csv',monitored)
    write_csv(out/'triplet_diagnostics.csv',triplets)
    def first_pass(rows):
        for a,b in zip(summaries,summaries[1:]):
            selected=[r for r in rows if r['coarse_m']==a['m']]
            if all(r['passed'] for r in selected):
                return a['m'],b['m']
        return None,None
    original=first_pass(pairs)
    half_choice=first_pass(half)
    limits={k:2*summaries[-1][k]-summaries[-2][k] for k in MONITORED}
    # This is a proxy comparison, not a measured true continuum error.
    errors=[dict(m=s['m'],metric=k,value=s[k],Richardson_estimate=limits[k],
                 estimated_error_over_Cref=abs(s[k]-limits[k])/cref) for s in summaries for k in MONITORED]
    write_csv(out/'richardson_proxies.csv',errors)
    choices=[]
    for name,reported,pair in (('original_report_coarse',original[0],original),
                               ('proposed_report_fine',original[1],original),
                               ('proposed_half_tol_report_coarse',half_choice[0],half_choice)):
        choices.append(dict(rule=name,pair_coarse_m=pair[0],pair_fine_m=pair[1],reported_m=reported,
                            third_level_available=(pair[1]*2 in LEVELS) if pair[1] else False,
                            max_contrast_proxy_error_over_Cref=None if reported is None else max(
                                r['estimated_error_over_Cref'] for r in errors if r['m']==reported and r['metric'] in CONTRASTS),
                            order_certified=False))
    write_csv(out/'rule_comparison.csv',choices)
    return dict(C_ref=cref,C_ref_status='temporary fixed Lstar at m128, not contract-v1 reference cost',
                tolerance_fraction=.01,tolerance_abs=.01*cref,choices=choices,
                Richardson_estimates=limits,asymptotic_band_locked=False)


def plots(out,summaries,conv):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(15,4.2),layout='constrained')
    ms=[s['m'] for s in summaries]
    axes[0].plot(ms,[s['G_S'] for s in summaries],'o-',label='G_S')
    axes[0].plot(ms,[s['Gamma'] for s in summaries],'s-',label='Gamma')
    axes[0].axhline(conv['Richardson_estimates']['G_S'],linestyle='--',color='grey',label='G_S Richardson proxy')
    axes[0].set(ylabel='packet x time unit',title='Threshold contrasts')
    axes[1].plot(ms,[s['Lstar'] for s in summaries],'o-')
    axes[1].set(ylabel='packet x time unit',title='Oracle expected cost')
    axes[2].plot(ms,[100*s['mode_share'] for s in summaries],'o-',label='Mode share in G_S')
    axes[2].set(ylabel='Percent',title='Ordered M0 state-information split')
    for ax in axes:
        ax.set_xscale('log',base=2)
        ax.set(xticks=ms,xticklabels=[str(m) for m in ms],xlabel='Refinement m (dt=1/m)')
        ax.grid(alpha=.25)
    axes[0].legend(fontsize=8)
    fig.savefig(out/'refinement_and_mode_share.png',dpi=160)
    plt.close(fig)


def report(r):
    conv=r['convergence']
    lines=['# L1.8 Part B — kiểm làm mịn trên calibration toy','',
           f"Người thực hiện: **Doan Van Tai** · {r['run_time_asia_saigon']}.",'',
           'Giữ thế giới: capacity3/3,rateA1,managed2,Bon/off5/0 packet mỗi đơn vị thời gian; '
           'horizon2,observation(2,0) tại−1,stationary initial mode1/2 độc lập observation. '
           'Coarse p=s5/8,lambda1/4. R2,dt1/m,H2m,tau m;backlog không co giãn. '
           'Cost/gain: packet×đơn vị thời gian chuẩn của toy,không là calibration link thực.','',
           'Finite-law expectation bằng DP gộp state;backlog units1/m packet giữ nguyên grid integer. '
           'Không Monte Carlo/RNG/seed. Floating probabilities từ m4 trở đi,không claim arithmetic exact.','',
           '## Kết quả từng level','',
           '| m | H | States D | Lstar | GS | GM | GSM | Gamma | Freshness M0 | Mode M0 | Mode share |',
           '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for s in r['levels']:
        lines.append(f"| {s['m']} | {s['H']} | {s['support_states']} | "+
                     ' | '.join(f"{s[k]:.9f}" for k in ('Lstar','G_S','G_M','G_SM','Gamma','freshness','mode_visibility'))+
                     f" | {100*s['mode_share']:.3f}% |")
    lines += ['', 'Đủ sáu contrasts,regrets vàM1-specific split tronglevel_metrics.csv. '
              'S0M0 vàS0M1 đều chọnSwitch ở mọi level→GM0. R110,meanI≈0,mass≈1,belief=D; '
              'zero-action controls cho contrasts0 tại mọi level. All states kiểm Jensen/F5 với rounding tolerance1e-10.','',
              '**Khác biệt nguồn:** Gamma tại m4=0.0254590834198094 làm tròn thành 0.025, nguồn ghi 0.026. '
              'Lstar tại m32=5.938468844428325 làm tròn thành 5.938, nguồn ghi 5.939. '
              'DP khớp finite-path reference m1/2/4 và forward scoring độc lập mọi level. '
              'Lưu 40 comparisons cùng mọi discrepancy, không nới tolerance để che khác biệt.','',
              '## Tolerance demo,rule vàRichardson','',
              f"Cref tạm=Lstar(m128)=**{conv['C_ref']:.12f}**,tolerance1%=**{conv['tolerance_abs']:.12f}**. "
              'Functional choice vàlevels đã ghi trongcard trước run;đáp án nguồn đã exposed. '
              'Cref dùng chung toàn bảng,chưa là reference cost/SESOI chính thức củaPartD.','',
              '| Rule | Pair kiểm | Report m | Có level thứ ba? | Max contrast error proxy / Cref |',
              '|---|---|---:|---|---:|']
    for s in conv['choices']:
        lines.append(f"| {s['rule']} | {s['pair_coarse_m']}→{s['pair_fine_m']} | {s['reported_m']} | "
                     f"{s['third_level_available']} | {100*s['max_contrast_proxy_error_over_Cref']:.6f}% |")
    lines += ['', 'PASS của pair chỉ nói change≤tol và không signflip lớn;chưa chứng nhận continuum error. '
              'Cả3 rule được so cùng denominator. Có ít nhất3 levels để reportorder;chưa khóa hard band '
              'quanhrho1/2 nên không tự ghiorder certified hoặcGO cho physical anchors.','',
              '| m→2m→4m | rho GS | rho Gamma | Richardson GS từ2m/4m |', '|---|---:|---:|---:|']
    levels=r['levels']
    for a,b,c in zip(levels,levels[1:],levels[2:]):
        gs=triplet_diagnostic(a,b,c,'G_S')
        gamma=triplet_diagnostic(a,b,c,'Gamma')
        lines.append(f"| {a['m']}→{b['m']}→{c['m']} | {gs['rho_conv']:.6f} | {gamma['rho_conv']:.6f} | {gs['richardson_from_last']:.9f} |")
    lines += ['', f"Richardson từm64/128:GS≈**{conv['Richardson_estimates']['G_S']:.9f}**," 
              f"Gamma≈**{conv['Richardson_estimates']['Gamma']:.9f}**," 
              f"Lstar≈**{conv['Richardson_estimates']['Lstar']:.9f}**. "
              'Đây là conditional first-order estimates,không phải true fluid solution hoặcerror bound. '
              'Từm1/2,Richardson GS=0.137939453,sai xa estimate cuối;kết quả sớm chưa ởasymptotic regime. '
              'FlatGM0 ghi undefined/constant cho rho,không chia0 hoặcgánorder1.','',
              f"Với M0 giữ cố định, mode share từ {100*levels[0]['mode_share']:.3f}% xuống "
              f"**{100*levels[-1]['mode_share']:.3f}%** ở m128. "
              'Không đồng nhất ratio ngoại suy của hai components với limit đã chứng minh. '
              'Current-backlog cell conditionD làdiagnostic,không feasible telemetry/net gain. '
              'Câu hai phần baGS củaL1.6 chỉ thuộc chuỗi dạy họclambda0,không áp dụng mạng.','',
              '**Vấn đề phương pháp ở bảng B6:** Các giá trị freshness/mode của nguồn tái lập khi '
              'freshness=L00−L_current_M1 và mode=L_current_M1−L10. Điểm giữa dùng M1, '
              'điểm cuối S1M0 nên đã đổi model; tổng vẫn bằng GS nhưng không là hai bước state-only '
              'dưới cùng M0. Code giữ primary split M0 đã khai báo, lưu M1 split riêng và đường hybrid '
              'chỉ để audit nguồn. Không tự coi đây là định nghĩa của script gốc vì script đó chưa được cung cấp. '
              'Bảng source_split_comparison.csv cho thấy toàn bộ 10 giá trị làm tròn của nguồn khớp đường hybrid.','',
              f"Hybrid mode share ở m128={100*levels[-1]['hybrid_mode_share']:.3f}%; Richardson các components hybrid "
              'cho khoảng11% như nguồn, nhưng không gán nó cho fixed-model State repair. '
              'Hai components fixed-M0 chưa có rho gần1/2 tại triplet cuối; order của chúng còn inconclusive '
              'trong tám levels đã khai báo. Không mở thêm levels chỉ để đạt.','',
              '## Kiểm chứng và độ chính xác','']
    for name,t in r['tests'].items():
        lines.append(f"- {name}: **{t['passed']}/{t['total']} PASS**,log`{t['log']}`,JUnit`{t['junit']}`.")
    lines += ['', f"Finite-path reference m1/2/4:{r['reference']['state_action_pairs']} state-action pairs; "
              f"maxerror={r['reference']['max_cost_error']:.3g}. m1 Lstar409/64,GS119/128 exact binary; "
              'm2 Lstar6.1312255859375,GS.5338134765625,Gamma.0780029296875.','',
              f"Forward reference tái sinh D và score bốn ô cùng hai current-backlog policies ở mọi level: "
              f"max aggregate cost difference={r['forward_reference']['max_cost_error']:.3g}. "
              'Forward và backward dùng hai hướng tính riêng, vẫn là computational cross-check, chưa scientific independent review.','',
              f"Float64/longdouble:maxJdifference={r['numeric']['max_J_difference']:.3g},"
              f"maxM0difference={r['numeric']['max_M0_difference']:.3g}; "
              f"action mismatches={r['numeric']['action_mismatches']},alerted nonzero gaps={r['numeric']['alerted_nonzero_states']}. "
              'Alert64*eps*H*maxcost chỉ để kiểm tra,không đổi tie rule. '
              'Không suy same actions hai precision thành proof mọifloating error đã hết.','',
              f"Solver float64 tổng wall time{sum(s['wall_seconds'] for s in levels):.6f}s trên máy hiện tại; "
              'đó là đo thực cho optimized toy DP,không dùng phút/m128 của nguồn làm số đo repo. '
              'Runtime/memory proxy của toy không dự báo budget lưới thật PartC.','',
              '## Kết luận và phần chưa làm','',
              'Đã tái lập xu hướngGS giảm,Gamma khôngmonotonic,GM0 trên calibrationcell này. '
              'Một pair PASS chưa đủ kết luận sai số của coarse level dưới tolerance;Richardson early windows '
              'có thể sai đáng kể. Không chứng minh GS luôn giảm với dt trong mọi regime. '
              'Không ổn định trong budget cũng chưa chứng minh không có limit.','',
              'Bốn đề xuất §11 ghi thànhworking protocol,không sửa frozencontractv0. '
              'Cref/threshold,asymptoticcriterion,calibrationgrid chính thức vàdt mỗi neo còn chờPartsC–E. '
              'Chưa chạyPhase3 A01 tổngquát,packetDES/Phase7 hoặcnetworkmeasurement; '
              'chưa fitH0/H1 hoặcheldout. G1,V3/V10/V11,HOLDPhase4 giữ nguyên.','',
              '## File và tái chạy','',
              '```bash','.venv/bin/python -m experiments.lessons.run_l1_8_b',
              '.venv/bin/python -m experiments.lessons.run_l1_8_b --output-dir /tmp/l1_8_b-rerun','```','',
              '| Artifact | Nội dung |','|---|---|',
              '| [config.json](config.json),[results.json](results.json) | Cấu hình,threshold rule,commands,source/input hashes,metrics |',
              '| [level_metrics.csv](level_metrics.csv),[state_cells.csv](state_cells.csv) | Đủ levels,costs/gaps/actions/probabilities/current cells |',
              '| [pair_checks.csv](pair_checks.csv),[half_tolerance_checks.csv](half_tolerance_checks.csv),[rule_comparison.csv](rule_comparison.csv) | Rules dưới1%/.5% |',
              '| [monitored_changes.csv](monitored_changes.csv),[triplet_diagnostics.csv](triplet_diagnostics.csv),[richardson_proxies.csv](richardson_proxies.csv) | Smooth/threshold/split diagnostics,mọi windows |',
              '| [finite_path_reference.csv](finite_path_reference.csv),[zero_action_controls.csv](zero_action_controls.csv) | Reference/control checks |',
              '| [forward_reference.csv](forward_reference.csv),[source_split_comparison.csv](source_split_comparison.csv) | Forward scoring độc lập và audit hybrid split |',
              '| [near_ties.csv](near_ties.csv),[precision_comparison.csv](precision_comparison.csv) | Numeric alarms,precision stability |',
              '| [source_comparison.csv](source_comparison.csv),[source_discrepancies.json](source_discrepancies.json) | Audit bảng nguồn |',
              '| [refinement_and_mode_share.png](refinement_and_mode_share.png) | Plot từ số liệu |',
              '| run_output.txt,lesson.txt,full_suite.txt,preflight.txt,*.xml | Actual logs vàJUnit |',
              '| [artifact_checks.json](artifact_checks.json),[artifact_manifest.json](artifact_manifest.json) | CSV/hash checks |','',
              f"Python{r['environment']['python']},NumPy{r['environment']['numpy']},longdouble eps{r['environment']['longdouble_epsilon']}; "
              f"runner walltime{r['elapsed_seconds']:.3f}s. Khôngseed/RNG/MC hoặcCI lấy mẫu.",
              '', '![Refinement](refinement_and_mode_share.png)','']
    return '\n'.join(lines)


def artifact_checks(out,summaries,conv):
    with (out/'state_cells.csv').open() as handle: rows=list(csv.DictReader(handle))
    for s in summaries:
        selected=[r for r in rows if int(r['m'])==s['m']]
        assert len(selected)==s['support_states']
        assert abs(math.fsum(float(r['probability']) for r in selected)-1)<1e-10
        for c in CELLS:
            value=math.fsum(float(r['probability'])*float(r['ell'+c]) for r in selected)
            assert abs(value-s['L'+c])<1e-10
    return dict(status='PASS',state_rows_checked=len(rows),levels_checked=len(summaries),
                mass_and_four_L_recomputed=True,denominator=conv['C_ref'],random_draws=0)


def execute(out):
    start=time.perf_counter()
    source=[ROOT/'experiments/lessons/l1_8_refinement.py',ROOT/'experiments/lessons/l1_8_forward_reference.py',Path(__file__),ROOT/'tests/test_l1_8_refinement.py',
            ROOT/'experiments/lessons/l1_2_queue.py',ROOT/'experiments/lessons/l1_3_expected_cost.py',
            ROOT/'experiments/lessons/l1_4_factorial.py',ROOT/'experiments/lessons/l1_6_belief.py',
            ROOT/'experiments/lessons/run_l1_2.py',ROOT/'experiments/lessons/run_l1_8_a.py',
            ROOT/'notes/lessons/L1.8B_experiment_card.md',ROOT/'notes/lessons/L1.8B_refinement_protocol.md',
            ROOT/'notes/01_definitions.md']
    config=dict(author='Doan Van Tai',levels=LEVELS,y=[2,0],coarse_lambda=.25,coarse_p_stay=.625,
                rates_per_time_unit=dict(cA=3,cB=3,bA=1,u=2,B_on=5,B_off=0),horizon=2,age=1,
                initializer='stationary mode independent of fixed observation at -1; prehistory Stay',
                tie='Stay at exact zero; no epsilon decisions',tolerance_fraction=.01,
                Cref_definition='Lstar at m128, fixed denominator; temporary demo only',
                invariant_rounding_tolerance=1e-10,source_display_rounding_tolerance=.0005,
                asymptotic_ratio_band=None,probability_pruning=False,random_sampling=False,seed=None,
                physical_anchor_dt_locked=False,contract_v1_locked=False,
                input=dict(path=str(INPUT),sha256=sha(INPUT)),
                source_hashes={str(p.relative_to(ROOT)):sha(p) for p in source})
    write_json(out/'config.json',config)
    test_results={}
    for name,targets in [('lesson',['tests/test_l1_8_refinement.py']),('full_suite',['tests/'])]:
        test_results[name]=tests(out,name,targets)
    solutions={}
    summaries,states,near,precision,zero=[],[],[],[],[]
    for m in LEVELS:
        s=solve_level(m)
        solutions[m]=s
        summaries.append(s['summary'])
        record_level(out,s,states,near,precision)
        z=solve_level(m,managed_rate=0)['summary']
        assert all(z[k]==0 for k in CONTRASTS)
        zero.append({k:z[k] for k in ('m','support_states','Lstar',*CONTRASTS,'freshness','mode_visibility')})
        print(f"m={m}: states={s['summary']['support_states']},Lstar={s['summary']['Lstar']:.9f},"
              f"GS={s['summary']['G_S']:.9f},Gamma={s['summary']['Gamma']:.9f},GM={s['summary']['G_M']:.9f}",flush=True)
    write_csv(out/'level_metrics.csv',summaries)
    write_csv(out/'state_cells.csv',states)
    write_csv(out/'near_ties.csv',near)
    write_csv(out/'precision_comparison.csv',precision)
    write_csv(out/'zero_action_controls.csv',zero)
    reference=finite_reference(out,solutions)
    forward=[check_level(solutions[m]) for m in LEVELS]
    assert max(r['max_aggregate_cost_error'] for r in forward)<1e-10
    assert max(r['D_max_abs_error'] for r in forward)<1e-12
    write_csv(out/'forward_reference.csv',forward)
    discrepancies=compare_source(out,summaries)
    conv=convergence_tables(out,summaries)
    numeric=dict(action_mismatches=sum(r['action_mismatch'] for r in precision),
                 alerted_nonzero_states=sum(r['alerted_states'] for r in near),
                 max_J_difference=max(r['max_J_error'] for r in precision),
                 max_M0_difference=max(r['max_M0_error'] for r in precision))
    result=dict(author='Doan Van Tai',run_time_asia_saigon=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                command=[sys.executable,'-m','experiments.lessons.run_l1_8_b','--output-dir',str(out)],config=config,
                tests=test_results,levels=summaries,convergence=conv,reference=reference,numeric=numeric,
                forward_reference=dict(levels=list(LEVELS),max_cost_error=max(r['max_aggregate_cost_error'] for r in forward)),
                source_discrepancies=discrepancies,elapsed_seconds=time.perf_counter()-start,
                environment=dict(python=platform.python_version(),numpy=np.__version__,longdouble_epsilon=float(np.finfo(np.longdouble).eps)))
    plots(out,summaries,conv)
    result['artifact_checks']=artifact_checks(out,summaries,conv)
    for path,digest in config['source_hashes'].items(): assert sha(ROOT/path)==digest
    write_json(out/'artifact_checks.json',result['artifact_checks'])
    write_json(out/'results.json',result)
    (out/'report.md').write_text(report(result))
    print(f"Cref={conv['C_ref']:.12f};Richardson GS={conv['Richardson_estimates']['G_S']:.12f},Gamma={conv['Richardson_estimates']['Gamma']:.12f}",flush=True)
    print('Rule choices:',conv['choices'],flush=True)
    print('Source discrepancies:',discrepancies,flush=True)
    print('Artifact audit: PASS; output:',out,flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_b')
    out=parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run_output.txt').open('w') as log:
        with contextlib.redirect_stdout(Tee(sys.stdout,log)),contextlib.redirect_stderr(Tee(sys.stderr,log)):
            try: execute(out)
            except Exception:
                traceback.print_exc()
                raise SystemExit(1)
    files=[dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
           if p.is_file() and p.name!='artifact_manifest.json']
    write_json(out/'artifact_manifest.json',dict(author='Doan Van Tai',files=files))


if __name__=='__main__': main()
