"""Doan Van Tai — N1/N2 verification, parameter feasibility and stationary bounds.

No episodes, oracle frequencies, margins or contrasts of a v1.1 candidate grid.
"""
import argparse,contextlib,csv,json,math,platform,subprocess,sys,time
from datetime import datetime
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
from smr.design import stationary_parameters
from smr.idle_gap import gap_from_idle
from smr.single_observation import statistics
from smr.stationary import (r2_keep,stationary_two_mode,tail_plan,quantile_interval,
                            conditional_mode_interval,StationaryBudgetError)
from experiments.lessons.v1_1_numerics import conservation_cases,subtract_truth,subtract_mean
from experiments.lessons.run_l1_8_a import Tee,clean,sha,tests,write_json
from experiments.lessons.l1_3_expected_cost import CANON,expected_cost
from experiments.lessons.l1_6_belief import m0_cost
from tests.golden_phase1 import CANONICAL_BELIEF

ROOT=Path(__file__).resolve().parents[2]


def csvout(out,name,rows):
    with (out/name).open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(clean(rows))


def qB_estimate(alpha,dt,kappa):
    s=float(r2_keep(dt,kappa)[0]);r,A=stationary_parameters(s)
    C=A*(1+r+r*r)/(1-r)
    q=max(0,math.ceil(math.log((1-alpha)/C)/math.log(r)-1))
    while 1-C*r**(q+1)<alpha:q+=1
    while q>0 and 1-C*r**q>=alpha:q-=1
    return 4*dt*q


def queue_lattice(rates,managed,dt):
    changes=[(r+managed-10)*dt for r in rates]
    denominator=math.lcm(*(v.denominator for v in changes))
    unit=F(math.gcd(*(int(v*denominator) for v in changes)),denominator)
    return unit,tuple(int(v/unit) for v in changes)


def run(out):
    baseline=json.loads((out/'baseline.json').read_text());assert baseline['passed']==baseline['total']==154
    source=['src/smr/idle_gap.py','src/smr/single_observation.py','src/smr/stationary.py',
            'tests/test_v1_1_numerics.py','tests/test_stationary_certificate.py',
            'experiments/lessons/v1_1_numerics.py','experiments/lessons/run_v1_1_m2.py',
            'notes/design/decisions_v1_1_m2.md','notes/01_definitions_v1_1_draft.md',
            'notes/theory/T01_single_observation.md','notes/theory/T02_stationary_certificate.md',
            'notes/phases/PHASE_1_closeout.md']
    inputs=[Path('/home/vantai/.codex/attachments')/f/'Pasted text.txt' for f in (
        'c5d3cb8c-bcc4-4ff7-9677-822418639b67','540be37b-1f39-4f32-9e64-112ca66c2820')]
    config=dict(author='Doan Van Tai',time=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
        python=platform.python_version(),numpy=np.__version__,preregistration_commit='27eeed4',
        inputs=[dict(path=str(p),sha256=sha(p)) for p in inputs],
        source_hashes={p:sha(ROOT/p) for p in source},command=[sys.executable,'-m','experiments.lessons.run_v1_1_m2'],
        choices=dict(N2='one observation/cell',epsilon_num_relative=1e-9,uncertain_mass_alarm=.01,
          tail_target=1e-20,infinite_law_target=1e-10,cap_limit=50000,dt_screen='1/120',half_step='1/240',
          lambdaA=['6.5','7.5','8.5'],amplitudeA='6',lambdaB='8',eta_core='.5',eta_spoke='.9'),
        rng_draws=0,seed=None,scope='verification toys and parameter map, no grid outcomes',
        headsup_sent=False,handwritten_artifact_created=False)
    write_json(out/'config.json',config)
    lesson=tests(out,'lesson',['tests/test_v1_1_numerics.py','tests/test_stationary_certificate.py'])
    full=tests(out,'full_suite',[])
    ties=[]
    for model,count,mutant in (('M1',300,subtract_truth),('M0',468,subtract_mean)):
        for i,(state,p) in enumerate(conservation_cases(count)):
            before=mutant(state,p);after=gap_from_idle(state,p,model)
            assert after==0
            ties.append(dict(model=model,case=i,H=p['H'],dt=p['dt'],subtraction_gap=before,
                             idle_gap=after,wrong_switch_before=before<0,wrong_switch_after=after<0))
    csvout(out,'structural_ties.csv',ties)
    N1={m:dict(cases=sum(r['model']==m for r in ties),
        subtraction_wrong=sum(r['model']==m and r['wrong_switch_before'] for r in ties),idle_wrong=0) for m in ('M1','M0')}
    assert all(r['subtraction_wrong']>0 for r in N1.values())
    canonical=statistics([(p,expected_cost(x,'Stay',CANON),expected_cost(x,'Switch',CANON),
                           m0_cost(x,'Stay',CANON),m0_cost(x,'Switch',CANON)) for x,p in CANONICAL_BELIEF.items()])
    n=0
    for a,b,c,d in product(range(-2,3),repeat=4):
        for p in (F(1,4),F(1,2),F(3,4)):
            statistics([(p,5,5+a,5,5+c),(1-p,5,5+b,5,5+d)]);n+=1
    assert n==1875
    write_json(out/'N2_lemma.json',dict(canonical=canonical,exact_two_state_cases=n,violations=0,
                                     artifact_kind='technical reference, not closed-book author evidence'))
    refs=[];arrays={}
    for i,(increments,s,e) in enumerate([((-2,1),F(1,2),F(0)),((-2,1),F(3,4),F(0)),
                                        ((-2,1),F(9,10),F(0)),((-5,3),F(3,4),F(0)),
                                        ((-2,1),*r2_keep(F(1,120),F(3,10)))],1):
        start=time.perf_counter();mass,cert=stationary_two_mode(increments,s,e,cap_limit=12000)
        arrays[f'case_{i}']=mass
        refs.append(dict(case=i,off_increment=increments[0],on_increment=increments[1],keep=s,
                         wall_s=time.perf_counter()-start,**cert))
    np.savez_compressed(out/'stationary_reference_masses.npz',**arrays)
    csvout(out,'stationary_certificates.csv',refs)
    dt=F(1,120);feasible=[];scaling=[]
    for k in (F(3,10),F(1),F(3)):
        q50,q90=qB_estimate(.5,dt,k),qB_estimate(.9,dt,k)
        scaling.append(dict(kappa=k,q50_packet=q50,q90_packet=q90,q90_over_kappa=q90/k,
                            kind='closed-form float estimate; finite-slot scaling not exact'))
    for lam,k,eta in [(a,k,F(1,2)) for a,k in product((F(13,2),F(15,2),F(17,2)),(F(3,10),F(1),F(3)))]+[(F(15,2),F(1),F(9,10))]:
        u=2*eta;rates=(lam-6,lam+6);unit,increments=queue_lattice(rates,u,dt)
        s,e=r2_keep(dt,k);plan=tail_plan(increments,s,e)
        row=dict(lambdaA=lam,psi=(lam-8)/10,kappa=k,eta=eta,u=u,A_OFF=rates[0],A_ON=rates[1],
                 rhoA_stay=(lam+u)/10,rhoB_switch=(8+u)/10,stable_A=lam+u<10,
                 ON_plus_u_exceeds_capacity=rates[1]+u>10,OFF_nonnegative=rates[0]>=0,
                 queue_unit_packet=unit,off_index=increments[0],on_index=increments[1],
                 required_cap=plan['cutoff'],tail_bound=plan['tail_bound'],status='HOLD_CAP',
                 qA90_low_packet=None,qA90_high_packet=None,law_error_bound=None,
                 posterior_error_bound=None,qB90_estimate_packet=qB_estimate(.9,dt,k),
                 full_DP_runtime_measured=False)
        assert row['stable_A'] and row['ON_plus_u_exceeds_capacity'] and row['OFF_nonnegative']
        if plan['cutoff']<=50000:
            try:
                mass,cert=stationary_two_mode(increments,s,e,cap_limit=50000)
                err=float(cert['infinite_law_error_upper']);lo,hi=quantile_interval(mass,.9,err)
                row.update(qA90_low_packet=lo*unit,qA90_high_packet=None if hi is None else hi*unit,
                           law_error_bound=cert['infinite_law_error_upper'],status='CERTIFIED_STATIONARY_PROTOTYPE')
                if hi is None or lo!=hi:row['status']='HOLD_QUANTILE'
                else:
                    _,bound=conditional_mode_interval(mass,lo,err);row['posterior_error_bound']=bound
                    if bound>1e-8:row['status']='HOLD_POSTERIOR'
            except (ArithmeticError,StationaryBudgetError) as exc:
                row['status']='HOLD_CERTIFICATE';print('stationary certificate HOLD:',str(exc),flush=True)
        feasible.append(row)
        print(f"parameter map lambdaA={lam} kappa={k} eta={eta}: {row['status']} cap={plan['cutoff']}",flush=True)
    csvout(out,'feasibility_parameters.csv',feasible);csvout(out,'quantile_scaling.csv',scaling)
    region=[]
    for rho,eta in ((F(4,5),F(1,2)),(F(4,5),F(9,10)),(F(3,5),F(1,2)),(F(1,2),F(9,10)),(F(1,5),F(9,10))):
        u=eta*(1-rho)*10
        region.append(dict(rhoB=rho,eta=eta,generic_psi_lower=(10-u)/20-rho,
                           generic_psi_upper=(10-u)/10-rho,rhoB_post=rho+eta*(1-rho),
                           fixed_amplitude_A_psi_lower=F(3,5)-rho))
    csvout(out,'feasible_regions.csv',region)
    assert region[-1]['rhoB_post']==F(23,25) # .92 counterexample to universal .95
    proc=subprocess.run([sys.executable,'notes/verification/verify_l1_8_cde_artifacts.py','--read-only'],
                        cwd=ROOT,capture_output=True,text=True)
    (out/'legacy_CDE_audit.txt').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
    write_json(out/'legacy_CDE_audit.json',json.loads(proc.stdout))
    plot(out,N1,region,scaling)
    assert len([l for l in (ROOT/'notes/01_definitions_v1_1_draft.md').read_text().splitlines() if l.startswith('| D')])==25
    assert all(sha(ROOT/p)==d for p,d in config['source_hashes'].items())
    result=dict(author='Doan Van Tai',status='TECHNICAL_PREPARATION_PASS_GATE_AND_GRID_HOLD',config=config,
                baseline=baseline,tests=dict(lesson=lesson,full_suite=full),N1=N1,N2=canonical,
                N2_exact_cases=n,stationary_reference_cases=len(refs),feasibility_parameter_sets=len(feasible),
                feasibility_status_counts={key:sum(r['status']==key for r in feasible) for key in sorted({r['status'] for r in feasible})},
                candidate_grid_created=False,p_switch_computed=False,A01_A04_run=False,tag_v1_1_created=False,
                human_artifacts_verified=False,headsup_sent=False,new_rng_draws=0)
    write_json(out/'results.json',result)
    text=render(result);(out/'report.md').write_text(text);print(text,end='',flush=True)


def plot(out,N1,region,scaling):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    x=np.arange(2);axes[0].bar(x-.15,[N1[m]['subtraction_wrong'] for m in ('M1','M0')],.3,label='cost subtraction')
    axes[0].bar(x+.15,[0,0],.3,label='idle identity');axes[0].set_xticks(x,['Truth (300)','M0 (468)'])
    axes[0].set_ylabel('Wrong Switch on certified ties');axes[0].legend()
    rho=np.linspace(0,1,200)
    for eta in (.5,.9):
        upper=(1-eta)*(1-rho);lower=(1-eta*(1-rho))/2-rho
        axes[1].fill_between(rho,lower,upper,alpha=.2,label=f'generic eta={eta}')
    axes[1].axhline(0,color='black',linewidth=.7);axes[1].set_xlabel('rho B');axes[1].set_ylabel('psi feasible interval');axes[1].legend()
    axes[2].plot([float(r['kappa']) for r in scaling],[float(r['q90_over_kappa']) for r in scaling],'o-')
    axes[2].set_xlabel('kappa');axes[2].set_ylabel('q90 / kappa (packets)');axes[2].set_title('Finite-slot scaling estimate')
    fig.tight_layout();fig.savefig(out/'N1_N3_N4_diagnostics.png',dpi=160);plt.close(fig)


def render(r):
    n=r['N1'];t=r['tests'];s=r['N2']
    return '\n'.join(['# Mốc2 — N1–N6: kết quả thực chạy','',
      'Người phụ trách: **Doan Van Tai**,23/10/2026. Technical reference; không fake bài kín sách/read-back hoặc buổi người thật. Heads-up chỉ lưu nháp theo yêu cầu, chưa gửi.','',
      f"- Baseline **{r['baseline']['passed']}/{r['baseline']['total']} PASS**; new tests **{t['lesson']['passed']}/{t['lesson']['total']} PASS**; full **{t['full_suite']['passed']}/{t['full_suite']['total']} PASS**.",
      f"- Truth300 structural ties: subtraction chọn nhầm Switch **{n['M1']['subtraction_wrong']}**, idle identity **0**.",
      f"- M0468 structural ties: subtraction chọn nhầm Switch **{n['M0']['subtraction_wrong']}**, idle identity **0**. Counts là deterministic fixtures của phiên này, không giả tái lập105/114/183/6549 của reviewer.",
      f"- N2 canonical: L00={s['L00']},L01={s['L01']},GM={s['G_M']},GSgivenM1={s['G_S_given_M1']}; bias={s['model_bias']},positive={s['E_positive']},negative={s['E_negative']}. **1875** exact two-state checks,0 violations.",
      '- Stationary solver: **5 reference cases**, gồm −2/+1 đối chiếu Decimal70digits, generic−5/+3, R2 probability interval; tail và law/residual certificates lưu riêng. Finite cap không giả là physical buffer.',
      f"- N3 parameter map: **{r['feasibility_parameter_sets']} sets**; statuses **{r['feasibility_status_counts']}**. Chỉ thông số/stationary/quantile/budget, không J hoặc oracle frequency.",
      '- Sửa lỗi review: eta.9,rhoB.2 cho postload.92<.95. q90/kappa chỉ gần invariant finite-slot, không equality tuyệt đối.',
      '- Legacy CDE audit read-only PASS; active closeout HOLD, old source hash đối chiếu commit snapshot thay vì sửa historical inputs. Tagv1 không dời.','',
      '## Trạng thái và giới hạn','',
      '**Mốc2 đã commit27eeed4 trước parameter map.** Đã chọn11 mục theo ủy quyền, proof/reference N2, idle-gap+certificates/precision API, stationary certificate và feasibility/claim updates. Không coi numeric band là thay mathematical oracle; unresolved sign phải escalation/HOLD.','',
      'Các sets vượt cap50.000 hoặc posterior/quantile không certified được giữ HOLD; chưa dựng/chốt grid manifest v1.1 hoặc chạy p_sw, A01/A04. Chưa tagv1.1 do grid/validity gates chưa đạt; P0-V3/P0-V11/V1/V8 vẫn thiếu record. Không có email gửi, RNG/seed mới hoặc network experiment. Phase2a mới bắt đầu primary reading, chưa novelty conclusion; full PHASE_1 chưa có để kiểm hash đầy đủ.','',
      '## Lệnh và artifacts','', '```bash',
      'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_m2',
      '.venv/bin/python notes/verification/verify_l1_8_cde_artifacts.py --read-only','```','',
      'config.json/results.json: commands,inputs/source hashes,choices và metrics. baseline/lesson/full_suite txt+xml: pytest thật. structural_ties.csv: before/after768ca; N2_lemma.json: canonical/reference; stationary_certificates.csv+stationary_reference_masses.npz: bounded reference laws; feasibility_parameters.csv/feasible_regions.csv/quantile_scaling.csv: thông số vàHOLD; N1_N3_N4_diagnostics.png:plot; run_output.txt:log; artifact_manifest.json:outputSHA256. No Monte Carlo CI; quantile estimates ngoài certified law được dán nhãn estimate.','',
      'Source: src/smr/idle_gap.py,single_observation.py,stationary.py; tests mới trong tests/test_v1_1_numerics.py vàtest_stationary_certificate.py. Contract draft25terms; active closeout HOLD; proof tham khảo T01/T02; heads-up nháp notes/meetings/2026-10-23_headsup.md. Không dùng technical report thay artifact người thật.',''])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/v1_1_m2')
    out=parser.parse_args().output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/'config.json').exists():raise SystemExit('Select fresh output directory; preserve evidence')
    with (out/'run_output.txt').open('w') as h:
        with contextlib.redirect_stdout(Tee(sys.stdout,h)),contextlib.redirect_stderr(Tee(sys.stderr,h)):
            try:run(out)
            except Exception:
                import traceback;traceback.print_exc();raise
    write_json(out/'artifact_manifest.json',dict(author='Doan Van Tai',files=[
        dict(file=str(p.relative_to(out)),size_bytes=p.stat().st_size,sha256=sha(p))
        for p in sorted(out.rglob('*')) if p.is_file() and p!=out/'artifact_manifest.json']))


if __name__=='__main__':main()
