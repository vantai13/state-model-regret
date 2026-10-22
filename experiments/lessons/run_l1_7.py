"""Doan Van Tai — reproduce the supplied L1.7 teaching demo, not Phase4/E01.

.venv/bin/python -m experiments.lessons.run_l1_7 [--output-dir /tmp/l1_7-rerun]
Preserves raw episode results, exact references, actual pytest/JUnit and mutants.
"""
import argparse
import contextlib
import csv
import hashlib
import importlib.metadata
import inspect
import json
import platform
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from fractions import Fraction as F
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from experiments.lessons.l1_3_expected_cost import CANON, expected_cost, oracle
from experiments.lessons.l1_4_factorial import contrasts
from experiments.lessons.l1_6_belief import factorial_end_to_end
from experiments.lessons.l1_3_expected_cost import generate_episodes
from experiments.lessons.l1_7_reference import direct_cost, exact_pairs, leak_reference, moments, shifted_pairs
from experiments.lessons.l1_7_streams import (
    DEMO_ROOT, PATH, ROLE, background_B, future_rng, identity2_residual, mk_action,
    naive_two_actions, path_costs, predictor_rng, primitive_two_actions,
)
from experiments.lessons.run_l1_2 import write_csv
from experiments.lessons.run_l1_3 import write_json

ROOT = Path(__file__).resolve().parents[2]
CORE = "tests/test_l1_7_streams.py"
EXTRA = "tests/test_l1_7_limits.py"
N = 2000
XB = (2,2,"off")
XS = [(2,2,"on"),XB,(2,0,"on"),(2,0,"off")]
TH6,TH3 = dict(CANON,H=6),dict(CANON,H=3)
INPUTS = [Path('/home/vantai/.codex/attachments/fe413710-3b2e-4f37-81bd-68a3811155b2/Pasted text.txt'),
          Path('/home/vantai/.codex/attachments/4c9b7506-2453-4d44-9e80-6cb02d12b625/Pasted text.txt')]
MUTANTS = {
    "R1": ("Action Switch mã hoá thành1 lọt vào khóa future", '''
original = lesson.primitive_two_actions
def bad(root, episode, x, th, extra_draws):
    st, _ = original(root,episode,x,th,extra_draws)
    sw = lesson.background_B(x,th,lesson.stream(root,"future",episode,lesson.PATH["B"],1).random(th["H"]-1))
    return st,sw
lesson.primitive_two_actions = bad
'''),
    "R2": ("Switch rút extra_draws từ future thay vì branch", '''
def bad(root, episode, x, th, extra_draws):
    st = lesson.background_B(x,th,lesson.future_rng(root,episode,"B").random(th["H"]-1))
    rng = lesson.future_rng(root,episode,"B")
    rng.random(extra_draws)
    return st,lesson.background_B(x,th,rng.random(th["H"]-1))
lesson.primitive_two_actions = bad
'''),
    "R3": ("Đảo u<P(keep) thành u>=P(keep)", '''
source = inspect.getsource(lesson.mode_path)
old = 'last if u < keep else'
assert source.count(old)==1
exec(source.replace(old,'last if u >= keep else'),lesson.__dict__)
'''),
    "R4": ("predictor_rng trả stream future B", '''
lesson.predictor_rng = lambda root,episode: lesson.future_rng(root,episode,"B")
'''),
    "R5": ("Bỏ episode khỏi khóa của mọi role", '''
original = lesson.stream
lesson.stream = lambda root,role,*index: original(root,role,*index[1:])
'''),
    "R6": ("Background luôn bắt đầu từ off", '''
original = lesson.background_B
lesson.background_B = lambda x,th,uniforms: original((x[0],x[1],"off"),th,uniforms)
'''),
    "R7": ("Bỏ chia K; equivalent mutant đối với action", '''
source = inspect.getsource(lesson.mk_action)
old = 'return choose(F(total, K))'
assert source.count(old)==1
exec(source.replace(old,'return choose(total)'),lesson.__dict__)
'''),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_tests(out,name,targets,mutation=None):
    args = ['-q','--color=no',f'--junitxml={out/name}.xml',*targets]
    if mutation:
        patch = out/f'{mutation}_patch.py'
        patch.write_text('# Doan Van Tai — isolated intentional mutant.\n'
                         'import sys, inspect\nimport pytest\n'
                         f'sys.path.insert(0,{str(ROOT)!r})\n'
                         'from experiments.lessons import l1_7_streams as lesson\n'
                         +MUTANTS[mutation][1]+'\nraise SystemExit(pytest.main(sys.argv[1:]))\n')
        command = [sys.executable,str(patch),*args]
    else:
        command = [sys.executable,'-m','pytest',*args]
    start = time.perf_counter()
    proc = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/f'{name}.txt').write_text(proc.stdout+proc.stderr)
    junit = out/f'{name}.xml'
    if not junit.is_file():
        raise RuntimeError(f'Missing JUnit: {name}')
    cases = list(ET.parse(junit).iter('testcase'))
    failed = [c.attrib['name'] for c in cases if c.find('failure') is not None]
    errors = [c.attrib['name'] for c in cases if c.find('error') is not None]
    skipped = [c.attrib['name'] for c in cases if c.find('skipped') is not None]
    return dict(command=command,returncode=proc.returncode,total=len(cases),failed=len(failed),
                passed=len(cases)-len(failed)-len(errors)-len(skipped),failed_tests=failed,
                failed_functions=sorted({n.split('[')[0] for n in failed}),errors=errors,skipped=skipped,
                wall_seconds=time.perf_counter()-start,log=f'{name}.txt',junit=junit.name)


def stats(values,exact):
    v = np.asarray(values,dtype=float)
    mean,var = float(v.mean()),float(v.var(ddof=1))
    se = (var/len(v))**.5
    return dict(n=len(v),mean=mean,sample_variance=var,SE=se,exact=exact,
                error=mean-float(exact),error_over_SE=(mean-float(exact))/se if se else None,
                within_3SE=abs(mean-float(exact)) <= 3*se)


def exact_measurements(out):
    refs,paths = [],[]
    for h,x in [(2,XS[0]),(2,XB),*( (6,x) for x in (XB,XS[0],(6,6,'on'),(10,10,'on')) )]:
        ref,rows = exact_pairs(x,dict(CANON,H=h))
        refs.append(dict(H=h,state=str(x),**ref))
        paths.extend(dict(H=h,state=str(x),**r) for r in rows)
    write_csv(out/'exact_moments.csv',refs)
    write_csv(out/'exact_paths.csv',paths)
    assert refs[0]['paired_variance']==0 and refs[0]['independent_variance']==F(25,2)
    assert refs[1]['paired_variance']==F(9,4) and refs[1]['independent_variance']==F(29,4)
    assert refs[2]['delta']==F(145,16)
    shifted,shift_paths = shifted_pairs(XB,TH6)
    for field in ('mean_stay','mean_switch','var_stay','var_switch'):
        assert shifted[field]==refs[2][field]
    assert shifted['paired_variance']>refs[2]['independent_variance']
    write_csv(out/'shifted_exact_paths.csv',shift_paths)
    leak,leak_paths = leak_reference(XB,TH3)
    assert [leak[k] for k in ('oracle','leak','honest')]==[F(31,4),F(13,2),F(65,8)]
    write_csv(out/'leak_exact_paths.csv',leak_paths)
    # Pairing across the canonical episode distribution, not across future samples.
    D = generate_episodes((2,0),1,CANON,F(1,2))
    _,ells,_ = factorial_end_to_end([(-1,(2,0))],CANON,F(1,2),D)
    rows = [dict(state=str(x),probability=p,L00=ells[x]['00'],L10=ells[x]['10'],
                 G_S=ells[x]['00']-ells[x]['10']) for x,p in D.items()]
    gs = moments([(p,ells[x]['10'],ells[x]['00']) for x,p in D.items()])
    assert gs['paired_variance']==F(99,64) and gs['independent_variance']==F(1359,64)
    write_csv(out/'episode_pairing.csv',rows)
    wrong = dict(CANON,p_onon=F(3,4),p_offoff=F(3,4))
    true_delta=expected_cost(XB,'Switch',CANON)-expected_cost(XB,'Stay',CANON)
    biased_delta=expected_cost(XB,'Switch',wrong)-expected_cost(XB,'Stay',wrong)
    assert (true_delta,biased_delta)==(F(-3,2),F(-9,4))
    return dict(moments=refs,shifted=shifted,leak=leak,episode_pairing=gs,
                wrong_law=dict(true_delta=true_delta,wrong_delta=biased_delta,bias=biased_delta-true_delta))


def measure_crn(out,exact):
    rows,series = [],{'primitive':[],'naive':[]}
    counts = {name:dict(future_mismatch=0,residual_nonzero=0) for name in series}
    for i in range(N):
        seed = np.random.SeedSequence(DEMO_ROOT,spawn_key=(ROLE['future'],i,PATH['B']))
        prim = primitive_two_actions(DEMO_ROOT,i,XB,TH6,1)
        naive = naive_two_actions(seed,XB,TH6,1)
        assert naive[0]==prim[0]
        assert naive_two_actions(seed,XB,TH6,0)==(prim[0],prim[0])
        for name,pair in (('primitive',prim),('naive',naive)):
            costs = path_costs(XB,TH6,*pair)
            st,sw = costs['Stay'][0],costs['Switch'][0]
            residual=identity2_residual(costs)
            mismatch=pair[0]!=pair[1]
            series[name].append(sw-st)
            counts[name]['future_mismatch']+=mismatch
            counts[name]['residual_nonzero']+=residual!=0
            rows.append(dict(method=name,episode=i,background_stay=str(pair[0]),background_switch=str(pair[1]),
                             cost_stay=st,cost_switch=sw,delta=sw-st,idle_stay=str(costs['Stay'][1]),
                             idle_switch=str(costs['Switch'][1]),identity_residual=residual,future_mismatch=mismatch))
    summaries=[]
    for name in series:
        ev = exact['moments'][2]['paired_variance'] if name=='primitive' else exact['shifted']['paired_variance']
        summary=dict(method=name,**stats(series[name],F(145,16)),exact_variance=ev,**counts[name])
        assert summary['within_3SE']
        summaries.append(summary)
        print(f"CRN {name}: delta={summary['mean']:.6f},SE={summary['SE']:.6f},var={summary['sample_variance']:.6f},"
              f"exact_var={float(ev):.6f}; mismatch={counts[name]['future_mismatch']}/{N},residual_nonzero={counts[name]['residual_nonzero']}/{N}",flush=True)
    assert counts['primitive']==dict(future_mismatch=0,residual_nonzero=0)
    assert counts['naive']['future_mismatch']/N>.9 and counts['naive']['residual_nonzero']/N>.9
    assert summaries[1]['sample_variance']>2*summaries[0]['sample_variance']
    write_csv(out/'crn_episodes.csv',rows)
    write_csv(out/'crn_summary.csv',summaries)
    return summaries


def measured_leak(x,th,n):
    star=oracle(x,th)[0]
    rows=[]
    for i in range(n):
        w=background_B(x,th,future_rng(DEMO_ROOT,i,'B').random(th['H']-1))
        costs=path_costs(x,th,w,w)
        actions=dict(oracle=star,leak=mk_action(x,th,future_rng(DEMO_ROOT,i,'B'),1),
                     honest=mk_action(x,th,predictor_rng(DEMO_ROOT,i),1))
        values={name:costs[a][0] for name,a in actions.items()}
        rows.append(dict(state=str(x),H=th['H'],episode=i,background=str(w),
                         **{name+'_action':a for name,a in actions.items()},**values))
    return rows


def measure_leak(out,exact):
    rows=measured_leak(XB,TH3,N)
    write_csv(out/'leak_episodes.csv',rows)
    summaries=[dict(method=name,**stats([r[name] for r in rows],exact['leak'][name]))
               for name in ('oracle','leak','honest')]
    for s in summaries:
        assert s['within_3SE']
        print(f"Leak {s['method']}: cost={s['mean']:.6f},SE={s['SE']:.6f},exact={float(s['exact']):.6f}",flush=True)
    gap=stats([r['oracle']-r['leak'] for r in rows],F(5,4))
    excess=stats([r['honest']-r['oracle'] for r in rows],F(3,8))
    assert all(r['leak']<=r['oracle'] for r in rows) and gap['mean']>3*gap['SE']
    assert excess['mean']>=-3*excess['SE']
    honest_wins=sum(r['honest']<r['oracle'] for r in rows)
    blind=[]
    for x in XS:
        cases=measured_leak(x,CANON,300)
        assert all(r['leak']==r['oracle'] for r in cases)
        ref,_=leak_reference(x,CANON)
        assert ref['leak']==ref['oracle']
        blind.extend(cases)
    write_csv(out/'canonical_blind_spot.csv',blind)
    write_csv(out/'leak_summary.csv',summaries)
    return dict(summary=summaries,paired_oracle_minus_leak=gap,paired_honest_minus_oracle=excess,
                honest_wins=honest_wins,honest_win_rate=honest_wins/N,
                leak_never_loses=True,canonical_blind_cases=len(blind))


def measure_sampler(out):
    th=dict(CANON,H=4,p_onon=F(3,4),p_offoff=F(1,2))
    raw,summaries=[],[]
    for x in ((2,2,'on'),(2,0,'off')):
        series={a:[] for a in ('Stay','Switch')}
        for i in range(N):
            pair=primitive_two_actions(DEMO_ROOT,i,x,th,0)
            costs=path_costs(x,th,*pair)
            raw.append(dict(state=str(x),episode=i,background=str(pair[0]),stay=costs['Stay'][0],switch=costs['Switch'][0]))
            for a in series:
                series[a].append(costs[a][0])
        for a in series:
            row=dict(state=str(x),action=a,**stats(series[a],expected_cost(x,a,th)))
            assert row['within_3SE']
            summaries.append(row)
    write_csv(out/'sampler_episodes.csv',raw)
    write_csv(out/'sampler_checks.csv',summaries)
    return summaries


def diagnostic_limits(out):
    a,b=[0,5,0,0],[0,0,5,5]
    costs=path_costs(XB,dict(CANON,H=4),a,b)
    residual=identity2_residual(costs)
    assert a!=b and residual==0
    tape=[.31,.72,.05,.88,.46,.63]
    st,sw=background_B(XB,TH6,tape[:5]),background_B(XB,TH6,tape[1:])
    naive=path_costs(XB,TH6,st,sw)
    assert (naive['Stay'][0],naive['Switch'][0])==(19,41)
    result=dict(residual_false_negative=dict(state=XB,H=4,background_stay=a,background_switch=b,
                costs=costs,residual=residual,reason='weighted background-arrival differences cancel'),
                tape=dict(uniforms=tape,source='invented deterministic tape supplied by lesson, not RNG output',
                          background_stay=st,background_switch=sw,naive_costs=naive,
                          naive_residual=identity2_residual(naive)),
                predictor_keys='(2,episode), sequential samples; no implemented per-k streams',
                role_alias_limit='(1,i) differs from (1,i,B); role-code alias alone need not leak future')
    write_json(out/'diagnostics.json',result)
    return result


def plot_results(out,result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    refs=result['exact']
    values=[refs['moments'][2]['paired_variance'],refs['shifted']['paired_variance'],refs['moments'][2]['independent_variance']]
    bars=axes[0].bar(['CRN','Shifted same seed','Independent'],[float(v) for v in values])
    axes[0].bar_label(bars,fmt='%.2f',padding=3)
    axes[0].set(ylabel='Variance (packet-slot)^2',title='H=6: exact variance',ylim=(0,410))
    summaries=result['leak']['summary']
    axes[1].bar([s['method'] for s in summaries],[s['mean'] for s in summaries],
                yerr=[3*s['SE'] for s in summaries],capsize=4,label='MC mean +/- 3SE')
    axes[1].scatter(range(3),[float(s['exact']) for s in summaries],color='red',marker='x',label='Exact expectation')
    axes[1].set(ylabel='Cost (packet-slot)',title='H=3: intentional leak positive control')
    axes[1].legend()
    for ax in axes:
        ax.grid(axis='y',alpha=.25)
        ax.set_axisbelow(True)
    fig.savefig(out/'crn_and_leak.png',dpi=160)
    plt.close(fig)


def report(result):
    e=result['exact']
    lines=['# L1.7 — CRN, stream, exposure và future leak','',
           f"Người thực hiện: **Doan Van Tai** · {result['run_time_asia_saigon']}.",'',
           'Đây là lần chạy demo theo hai tài liệu được cung cấp, không là Phase4/E01 hoặc confirmation. '
           'Plant và oracle exact giữ nguyên. dt=1,cA=cB=3,u=2,bA=1,B on/off5/0,p=s=1/2,c_sw=0; '
           'mode slot0 biết trước, tie→Stay. Cost/Δ/SE tính bằng packet·slot; phương sai bằng (packet·slot)².','',
           f"Root demo **{DEMO_ROOT}** được tiếp nhận từ tài liệu, không sinh mới. N={N},episodes0–1999. "
           'NumPy2.5.3 được pin riêng; PCG64/SeedSequence. Không sinh/mở root discovery,calibration,confirmation.','',
           '## CRN so với cùng seed nhưng dịch một lần rút','',
           'x=(2,2,off),H6,extra1; hai cách có đúng cùng nhánh Stay. Primitive sinh B trước, '
           'extra draws từ branch; naive Switch dịch stream future. Độc lập chỉ tính exact, không chạy MC.','',
           '| Cách | MC mean Δ ± SE | Sample variance | Exact variance | Future khác /N | Residual khác0 /N |',
           '|---|---:|---:|---:|---:|---:|']
    for s in result['crn']:
        lines.append(f"| {s['method']} | {s['mean']:.6f} ± {s['SE']:.6f} | {s['sample_variance']:.6f} | "
                     f"{float(s['exact_variance']):.6f} | {s['future_mismatch']}/{N} | {s['residual_nonzero']}/{N} |")
    lines += [f"| Independent (exact only) | — | — | {float(e['moments'][2]['independent_variance']):.6f} | — | — |",'',
              'Δ exact=145/16=9.0625. Hai marginal mean/variance naive khớp exact với CRN, nên unbiasedness '
              'ở cấu hình này được xác nhận bằng enumeration; mẫu MC trong ±3SE chỉ là consistency check. '
              'Cách ngây thơ ở đây tệ hơn independent, không suy thành quy luật mọi cấu hình.','',
              f"Naive exact covariance={e['shifted']['covariance']},correlation={e['shifted']['correlation']:.6f}; "
              f"conditional first keep/flip correlations={e['shifted']['conditional_first_keep']['correlation']:.6f}/"
              f"{e['shifted']['conditional_first_flip']['correlation']:.6f}.",'',
              '| State | H | Paired var | Independent var | Independent/paired | Correlation |',
              '|---|---:|---:|---:|---:|---:|']
    for s in e['moments']:
        ratio='∞' if s['independent_over_paired'] is None else f"{s['independent_over_paired']:.3f}"
        lines.append(f"| {s['state']} | {s['H']} | {float(s['paired_variance']):.6f} | {float(s['independent_variance']):.6f} | {ratio} | {s['correlation']:.6f} |")
    lines += ['',f"Ghép canonical episodes cho GS: paired variance={e['episode_pairing']['paired_variance']}, "
              f"independent={e['episode_pairing']['independent_variance']}. "
              'Sai law p=s3/4 ở XB,H2 cho Δ−9/4 thay vì−3/2: CRN không sửa bias.','',
              '## Positive control cho rò tương lai','',
              'x=(2,2,off),H3,K1; oracle chọn bằng J exact. Honest lấy samples predictor độc lập với '
              'future evaluator; leak cố ý lấy đúng future để kiểm máy dò.','',
              '| Policy | MC cost ± SE | Exact cost |', '|---|---:|---:|']
    for s in result['leak']['summary']:
        lines.append(f"| {s['method']} | {s['mean']:.6f} ± {s['SE']:.6f} | {s['exact']} |")
    lk=result['leak']
    lines += ['',f"Honest thắng oracle trên **{lk['honest_wins']}/{N}={100*lk['honest_win_rate']:.2f}%** episode "
              '(exact25%). Đây là cost trên một realized future, ngay cả khi oracle J tính exact; '
              'không cần oracle estimation noise để có hiện tượng này. Leak không thua oracle ở bất kỳ episode đã kiểm. '
              f"Paired oracle−leak={lk['paired_oracle_minus_leak']['mean']:.6f} ± "
              f"{lk['paired_oracle_minus_leak']['SE']:.6f} SE. "
              f"Canonical H2: **{lk['canonical_blind_cases']}/{lk['canonical_blind_cases']}** leak cost bằng oracle; "
              'có rò nhưng ví dụ chuẩn không thấy. Dấu hiệu này là positive control trong toy, không là test chứng nhận mọi leakage.','',
              '## Sampler bất đối xứng và giới hạn detector','',
              'H4,p3/4,s1/2,N2000 mỗi state. Runner lưu/in J để audit; do đó các outcome verification này cũng được ghi exposed.','',
              '| State | Action | Mean ± SE | Exact J | Error/SE |', '|---|---|---:|---:|---:|']
    for s in result['sampler']:
        lines.append(f"| {s['state']} | {s['action']} | {s['mean']:.6f} ± {s['SE']:.6f} | {s['exact']} | {s['error_over_SE']:.3f} |")
    lines += ['', 'Residual0 là điều kiện cần của cùng background, không đủ. Phản ví dụ H4: '
              'Stay background[0,5,0,0],Switch[0,0,5,5],hai mảng khác nhau nhưng residual0 vì weighted arrivals triệt tiêu. '
              'Demo kiểm cả equality arrays và idle identity. Tape tự đặt cho costs19/41,residual15; đây không phải RNG sample.','',
              '## Test và mutation','']
    for name,s in result['tests'].items():
        lines.append(f"- {name}: **{s['passed']}/{s['total']} PASS**,log `{s['log']}`,JUnit `{s['junit']}`.")
    lines += ['', '72 là13 L1.7 +59 lesson trước; repo có thêm21 kiểm trước và4 kiểm L1.7 mới →97. '
              'Preflight17 đã PASS trước runner. Lần gọi preflight đầu bị shell từ chối vì thư mục output chưa tồn tại; '
              'chưa chạy pytest lúc đó. Đã tạo thư mục và giữ log lần chạy thật; không có lỗi baseline pytest.','',
              '| Mutant | Nội dung | Cases đỏ /13 | Functions đỏ |', '|---|---|---:|---:|']
    for name,s in result['mutations'].items():
        lines.append(f"| {name} | {s['description']} | {s['failed']} | {len(s['failed_functions'])} |")
    for name,s in result['mutations'].items():
        lines += ['',name+': '+(', '.join('`'+n+'`' for n in s['failed_tests']) or 'Không bị bắt: equivalent đối với dấu/action hiện tại.')]
    lines += ['', 'R1–R6 là intentional failures của mutant; R7 bỏ chiaK không đổi dấu nên phải qua. '
              'Tách số test functions khỏi parametrized cases; không ép số đỏ bằng tài liệu. '
              'Các patch chỉ áp trong subprocess, source baseline không bị sửa/copy. '
              'Role alias đơn thuần cũng chưa chắc tạo leak vì khóa(1,i) khác(1,i,B).','',
              '![CRN và leak](crn_and_leak.png)','',
              '## Artifact và tái lập','',
              'Source: `experiments/lessons/l1_7_streams.py`,`l1_7_reference.py`,`run_l1_7.py`; '
              'tests: `tests/test_l1_7_streams.py`,`test_l1_7_limits.py`; pin `experiments/lessons/requirements-l1_7.txt`.','',
              '```bash','.venv/bin/python -m experiments.lessons.run_l1_7',
              '.venv/bin/python -m experiments.lessons.run_l1_7 --output-dir /tmp/l1_7-rerun','```','',
              '| File | Nội dung |','|---|---|',
              '| [config.json](config.json),[results.json](results.json) | Parameters,seeds,environment,commands,input/source hashes,metrics |',
              '| [crn_episodes.csv](crn_episodes.csv),[crn_summary.csv](crn_summary.csv) | 4000 rows CRN/naive,chi tiết cost,idle,residual |',
              '| [exact_moments.csv](exact_moments.csv),[exact_paths.csv](exact_paths.csv),[shifted_exact_paths.csv](shifted_exact_paths.csv) | Exact moments và 64 shifted sequences |',
              '| [leak_episodes.csv](leak_episodes.csv),[leak_summary.csv](leak_summary.csv),[leak_exact_paths.csv](leak_exact_paths.csv) | Actions/evaluator futures/costs và exact leak reference |',
              '| [canonical_blind_spot.csv](canonical_blind_spot.csv),[episode_pairing.csv](episode_pairing.csv) | H2 blind spot và GS episode pairing |',
              '| [sampler_episodes.csv](sampler_episodes.csv),[sampler_checks.csv](sampler_checks.csv) | Asymmetric-chain samples và checks |',
              '| [diagnostics.json](diagnostics.json),[artifact_checks.json](artifact_checks.json),[artifact_manifest.json](artifact_manifest.json) | Tape,counterexample,cross-file verification,SHA256 |',
              '| run_output.txt,preflight.txt,lesson.txt,lessons.txt,limits.txt,full_suite.txt,*.xml | Actual baseline commands/log/JUnit |',
              '| R1…R7.txt,*.xml,R*_patch.py | Intentional mutations và test phát hiện |',
              '| [crn_and_leak.png](crn_and_leak.png) | Chart từ số liệu,không có network throughput/delay measurements |','',
              'Sổ seed/exposure/card đã ghi trước chạy. Hai trục stage×role chỉ là draft cho demo; '
              'chưa khóa contract-v1/thẻ8 L1.8. Predictor dùng(2,i) với sequential prefix samples, '
              'chưa có(2,i,k). Interface Python là quy ước, chưa là access-control sandbox. '
              'Không claim mọi sample đều independent hoặc chứng minh PRNG bằng tests.','',
              'Mock reviewer là bản tham khảo có tài liệu; không gán là bài kín sách của tác giả hoặc independent review. '
              'L0.5,Phụ lụcD,V3/V10/V11 còn mở. Không thay contract-v0,không fit H0/H1,không có held-out/network validation. '
              'G1 và HOLD Phase4 giữ nguyên.','',
              f"Python {result['environment']['python']};NumPy {result['environment']['numpy']};"
              f"pytest {result['environment']['pytest']};wall time {result['elapsed_seconds']:.3f}s (không là network benchmark).",'']
    return '\n'.join(lines)


def audit_outputs(out,result):
    checks={}
    with (out/'crn_episodes.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==2*N
    for s in result['crn']:
        part=[r for r in rows if r['method']==s['method']]
        measured=stats([int(r['delta']) for r in part],F(145,16))
        for key in ('mean','sample_variance','SE'):
            assert measured[key]==s[key]
        assert sum(int(r['identity_residual'])!=0 for r in part)==s['residual_nonzero']
    checks['crn_rows_recomputed']=len(rows)
    with (out/'leak_episodes.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==N
    for s in result['leak']['summary']:
        assert stats([int(r[s['method']]) for r in rows],s['exact'])['mean']==s['mean']
    checks['leak_rows_recomputed']=len(rows)
    for path,expected in result['config']['source_hashes'].items():
        assert sha(ROOT/path)==expected
    checks['source_hashes_verified']=len(result['config']['source_hashes'])
    checks['all_baseline_JUnit_clean']=all(s['failed']==0 and not s['errors'] and s['returncode']==0 for s in result['tests'].values())
    assert checks['all_baseline_JUnit_clean']
    checks['status']='PASS'
    write_json(out/'artifact_checks.json',checks)
    return checks


def execute(out):
    start=time.perf_counter()
    if np.__version__!='2.5.3':
        raise RuntimeError('Install experiments/lessons/requirements-l1_7.txt; do not silently change demo RNG version')
    source_paths=[*sorted(ROOT.glob('experiments/lessons/l1_[2-7]*.py')),
                  Path(__file__),ROOT/CORE,ROOT/EXTRA,ROOT/'experiments/lessons/requirements-l1_7.txt',
                  ROOT/'notes/lessons/L1.7_experiment_card.md',ROOT/'notes/seed_registry.md',ROOT/'notes/00_exposure_register.md']
    config=dict(author='Doan Van Tai',method='supplied teaching-root demo with exact finite references',canonical=CANON,
                root=DEMO_ROOT,root_provenance='provided attachment Part2; adopted 2026-10-22; not newly generated',
                roles=ROLE,paths=PATH,episode_range=[0,N-1],N=N,H_crn=6,H_leak=3,K_leak=1,extra_draws=[0,1,7],
                sampler=dict(H=4,p_onon=F(3,4),p_offoff=F(1,2),states=[(2,2,'on'),(2,0,'off')]),
                dt=1,c_sw=0,tie='Stay',thresholds=dict(max_error_SE=3,primitive_variance_relative_tolerance=.15,
                minimum_mismatch_rate=.9,minimum_variance_ratio=2),
                source_hashes={str(p.relative_to(ROOT)):sha(p) for p in source_paths},
                input_hashes=[dict(path=str(p),sha256=sha(p)) for p in INPUTS],
                git_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                git_note='working tree contains uncommitted lesson work; source hashes identify actual version',
                confirmation_opened=False,phase4_E01_run=False,independent_MC_run=False)
    write_json(out/'config.json',config)
    environment=dict(python=platform.python_version(),numpy=np.__version__,pytest=importlib.metadata.version('pytest'),
                     matplotlib=importlib.metadata.version('matplotlib'),bit_generator=type(future_rng(DEMO_ROOT,0,'B').bit_generator).__name__,
                     platform=platform.platform())
    tests={}
    targets=[('lesson',[CORE]),('lessons',['tests/test_l1_2_queue.py','tests/test_l1_3_expected_cost.py',
                'tests/test_l1_4_factorial.py','tests/test_l1_5_identity.py','tests/test_l1_6_belief.py',CORE]),
             ('limits',[EXTRA]),('full_suite',['tests/'])]
    for name,files in targets:
        tests[name]=run_tests(out,name,files)
        write_json(out/'test_progress.json',tests)
        if tests[name]['returncode'] or tests[name]['errors'] or tests[name]['skipped']:
            raise RuntimeError(f'Baseline failed: {name}.txt')
        print(f"{name}: {tests[name]['passed']}/{tests[name]['total']} PASS",flush=True)
    assert tests['lesson']['total']==13 and tests['lessons']['total']==72 and tests['limits']['total']==4
    exact=exact_measurements(out)
    crn=measure_crn(out,exact)
    leak=measure_leak(out,exact)
    sampler=measure_sampler(out)
    diag=diagnostic_limits(out)
    mutations={}
    for name in MUTANTS:
        s=run_tests(out,name,[CORE],name)
        mutations[name]=dict(description=MUTANTS[name][0],**s)
        write_json(out/'mutation_progress.json',mutations)
        assert not s['errors'] and not s['skipped'] and s['total']==13
        assert (s['failed']>0 and s['returncode']==1) if name!='R7' else (s['failed']==0 and s['returncode']==0)
        print(f"{name}: {s['failed']}/13 failed cases; {len(s['failed_functions'])} functions",flush=True)
    result=dict(author='Doan Van Tai',run_time_asia_saigon=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                command=[sys.executable,'-m','experiments.lessons.run_l1_7','--output-dir',str(out)],
                environment=environment,config=config,tests=tests,exact=exact,crn=crn,leak=leak,sampler=sampler,
                diagnostics=diag,mutations=mutations,elapsed_seconds=time.perf_counter()-start,
                scope=dict(G_level='G1',V3_V10_V11='open',phase4='HOLD',held_out=False,
                           closed_book_mock_done=False,legacy_L05_done=False))
    plot_results(out,result)
    result['artifact_checks']=audit_outputs(out,result)
    write_json(out/'results.json',result)
    (out/'report.md').write_text(report(result),encoding='utf-8')
    print(f"Artifact audit: PASS; honest episode wins={leak['honest_wins']}/{N}; output={out}",flush=True)


class Tee:
    def __init__(self,*handles): self.handles=handles
    def write(self,value):
        for h in self.handles: h.write(value)
        return len(value)
    def flush(self):
        for h in self.handles: h.flush()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_7')
    out=parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run_output.txt').open('w') as log:
        with contextlib.redirect_stdout(Tee(sys.stdout,log)),contextlib.redirect_stderr(Tee(sys.stderr,log)):
            try:
                execute(out)
            except Exception:
                traceback.print_exc()
                raise SystemExit(1)
    entries=[dict(file=str(p.relative_to(out)),size_bytes=p.stat().st_size,sha256=sha(p))
             for p in sorted(out.iterdir()) if p.is_file() and p.name!='artifact_manifest.json']
    write_json(out/'artifact_manifest.json',dict(author='Doan Van Tai',files=entries))


if __name__=='__main__':
    main()
