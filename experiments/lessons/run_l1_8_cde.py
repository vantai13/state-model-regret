"""Doan Van Tai — C/D/E design diagnostics, exposed-reference checks, no grid J."""
import argparse
import contextlib
import csv
import json
import math
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from smr.design import (design_cells, diagnostic, episode_law, reserved_coordinates,
                        stationary_mass, stationary_total)
from smr.exact import value_backward
from smr.thresholds import to_ms_per_packet, verdict
from experiments.lessons.l1_2_queue import two_queue_cost
from experiments.lessons.l1_3_expected_cost import CANON, expected_cost
from experiments.lessons.l1_6_belief import m0_cost, predict
from experiments.lessons.l1_8_forward_reference import propagate_B
from experiments.lessons.run_l1_8_a import Tee, clean, sha, tests, write_json
from tests.golden_phase1 import CANONICAL_BELIEF, EXPECTED_COSTS
from tests.test_l1_8_contract import idle_grid_check

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'notes/design/grid_v1.json'
INPUTS=[Path('/home/vantai/.codex/attachments')/folder/'Pasted text.txt' for folder in (
    'd3491ab2-086d-4b6a-8631-155cd269eb5b', '29b93c8c-40d1-447d-a519-4077188002ef',
    'e188727e-4b63-47f7-9fc8-e51216673a56')]


def csv_out(out,name,rows):
    with (out/name).open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(clean(rows))


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def consistency(manifest):
    contract=(ROOT/'notes/01_definitions_v1.md').read_text()
    brief=(ROOT/'notes/00_research_brief_v1.md').read_text()
    old=(ROOT/'notes/01_definitions.md').read_text()
    review=(ROOT/'notes/verification/final_review_reading_note.md').read_text()
    closeout=(ROOT/'notes/phases/PHASE_1_closeout.md').read_text()
    ids=re.findall(r'^\| (D\d+) \|',contract,re.M)
    assert ids==[f'D{i}' for i in range(1,26)] and len(set(ids))==25
    rq='For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?'
    assert all(rq in document for document in (contract,brief,old,review))
    used=set(re.findall(r'\bD\d+\b',brief))
    assert used <= set(ids)
    pending=['A01','A05','P0-V3','P0-V10','P0-V11','HUMAN','FEEDBACK','MODEL5','FEASIBLE8','PRIOR2A','SOURCE']
    assert all(f'| {key} |' in closeout for key in pending)
    t=manifest['thresholds']
    assert 0<t['refinement_fraction']<=t['epsilon_E']/2<t['epsilon_E']<t['epsilon_R']
    assert manifest['cells']==clean(design_cells())
    assert manifest['reserve_coordinates_only']==clean(reserved_coordinates())
    assert manifest['calibration_cells']==['M01','M02','M10']
    assert manifest['profile']['R2'] and not manifest['rng']['roots_allocated']
    assert 'Lstar per cell at same dt'==t['C_ref']
    assert t['I_delta_threshold']=='epsilon_E*C_ref'
    # v0 is intentionally byte-preserved in its original file.
    frozen=subprocess.check_output(['git','show','contract-v0:notes/01_definitions.md'],cwd=ROOT)
    assert frozen==(ROOT/'notes/01_definitions.md').read_bytes()
    return dict(author='Doan Van Tai',overall='CONDITIONAL_PASS',checks=[
        dict(id=1,status='PASS',check='25 unique operational definition IDs, no duplicate row'),
        dict(id=2,status='PASS',check='Main RQ exact in v0/v1/brief/review digest; brief D references defined',references=sorted(used)),
        dict(id=3,status='PASS',check='every declared deferred/pending topic has location',topics=pending),
        dict(id=4,status='PARTIAL',check='Final Review full-source consistency',
             reason='Repository reading note checked; full source sections2/11/12 unavailable, full comparison not performed'),
        dict(id=5,status='PASS',check='25-term budget; v0 bytes match immutable contract-v0'),
        dict(id=6,status='PASS',check='threshold/refinement/Cref/I/prior/grid/roles/RNG cross-card constraints')],
        external_human_review='PENDING',full_PHASE_1_template_comparison='NOT_AVAILABLE')


def reference_checks(out):
    golden=[]
    for x,expected in EXPECTED_COSTS.items():
        qa,qb,mode=x
        for action in ('Stay','Switch'):
            A=value_backward(2 if action=='Stay' else 0,2,3,{'a':1},{'a':{'a':F(1)}},[qa],F(1))
            P={m:{n:F(1,2) for n in ('on','off')} for m in ('on','off')}
            B=value_backward(2 if action=='Switch' else 0,2,3,{'on':5,'off':0},P,[qb],F(1))
            value=A[qa,'a']+B[qb,mode]
            assert value==expected[action=='Switch']==expected_cost(x,action,CANON)
            golden.append(dict(state=str(x),action=action,J=value,golden=expected[action=='Switch'],residual=0))
    csv_out(out,'golden_costs.csv',golden)
    rows=[]
    m,H,keep=16,32,(1+.25**(1/16))/2
    P={i:{j:keep if i==j else 1-keep for j in (0,1)} for i in (0,1)}
    start=time.perf_counter()
    for managed in (0,2):
        backward=value_backward(managed,H,3,{0:0,1:5},P,range(33),F(1,m*m))
        for q,mode in product(range(33),(0,1)):
            initial=np.zeros((33,2)); initial[q,mode]=1
            _,forward=propagate_B(initial,H,keep,managed,m)
            value=float(backward[q,mode]); error=abs(value-forward)
            assert error<5e-13
            rows.append(dict(m=m,H=H,qB_packet=F(q,m),mode=mode,managed_index_amount=managed,
                             backward=value,forward=forward,abs_error=error))
    elapsed=time.perf_counter()-start
    csv_out(out,'backward_forward_B16.csv',rows)
    joint=[]
    P={m:{n:F(1,2) for n in (0,1)} for m in (0,1)}
    for ma,mb,switch in product((0,1),(0,1),(False,True)):
        A=value_backward(0 if switch else 2,2,3,{0:0,1:4},P,[2],F(1))
        B=value_backward(2 if switch else 0,2,3,{0:0,1:5},P,[1],F(1))
        together=sum(F(1,2)*two_queue_cost((2,1),[4*ma,4*n],[5*mb,5*n],2,3,3,
                                         'Switch' if switch else 'Stay')[0] for n in (0,1))
        separated=A[2,ma]+B[1,mb]
        assert separated==together
        joint.append(dict(modeA=ma,modeB=mb,switch=switch,correlation='common next mode',
                          joint=together,separate=separated,residual=0))
    csv_out(out,'queue_additivity.csv',joint)
    # Already exposed teaching episode, not the new profile/grid.
    belief=CANONICAL_BELIEF
    d00=predict(belief,'Switch','M0',CANON)-predict(belief,'Stay','M0',CANON)
    d01=predict(belief,'Switch','M1',CANON)-predict(belief,'Stay','M1',CANON)
    I=[]; Cref=F(25,4); delta=F(1,200)*Cref
    for x,p in belief.items():
        d11=expected_cost(x,'Switch',CANON)-expected_cost(x,'Stay',CANON)
        d10=m0_cost(x,'Switch',CANON)-m0_cost(x,'Stay',CANON)
        interaction=d11-d10-d01+d00
        I.append(dict(state=str(x),p=p,I_delta=interaction,delta=delta,exceeds=abs(interaction)>delta))
    csv_out(out,'canonical_I_delta.csv',I)
    interaction=dict(mean=float(sum(r['p']*r['I_delta'] for r in I)),
                     expected_abs=float(sum(r['p']*abs(r['I_delta']) for r in I)),
                     probability_exceeding_delta=float(sum(r['p']*r['exceeds'] for r in I)),delta=str(delta))
    return dict(golden_values=len(golden),golden_violations=0,backward_forward_values=len(rows),
                backward_forward_max_error=max(r['abs_error'] for r in rows),
                reference_check_wall_s=elapsed,correlated_queue_checks=len(joint),
                canonical_interaction=interaction)


def run(out):
    manifest=json.loads(MANIFEST.read_text())
    # Require a committed design before full-grid diagnostics. No grid values J anywhere here.
    assert subprocess.check_output(['git','show','HEAD:notes/design/grid_v1.json'],cwd=ROOT)==MANIFEST.read_bytes()
    source=[ROOT/p for p in ('src/smr/design.py','src/smr/exact.py','src/smr/thresholds.py',
        'tests/test_l1_8_contract.py','experiments/lessons/run_l1_8_cde.py',
        'notes/design/grid_v1.json','notes/design/grid_v1.md','notes/01_definitions_v1.md',
        'notes/00_research_brief_v1.md','notes/lessons/L1.8D_decision_cards.md',
        'notes/lessons/L1.8E_question_card.md','notes/lessons/L1.8E_changes_v0_v1.md',
        'notes/phases/PHASE_1_closeout.md')]
    config=dict(author='Doan Van Tai',time=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                python=platform.python_version(),numpy=np.__version__,git_design_commit=git('rev-parse','HEAD'),
                command=[sys.executable,'-m','experiments.lessons.run_l1_8_cde','--output-dir',str(out)],
                source_hashes={str(p.relative_to(ROOT)):sha(p) for p in source},
                attachments=[dict(path=str(p),sha256=sha(p)) for p in INPUTS],
                manifest_sha256=sha(MANIFEST),random_draws=0,seed=None,
                scope='CDE diagnostics only; J checks on already exposed teaching configurations',
                new_grid_contrasts_computed=False,reserve_generated=False)
    write_json(out/'config.json',config)
    checks=consistency(manifest); write_json(out/'consistency_checks.json',checks)
    lesson=tests(out,'lesson',['tests/test_l1_8_contract.py'])
    full=tests(out,'full_suite',[])
    idle=idle_grid_check(); csv_out(out,'idle_grid_5832.csv',idle)
    assert len(idle)==5832 and not any(r['action_mismatches'] for r in idle)
    references=reference_checks(out)
    rows=[]; scaled=[]; episodes=[]; start=time.perf_counter()
    for cell in design_cells():
        row=diagnostic(cell); other=diagnostic(cell,time_scale=F(3),rate_scale=F(7))
        assert abs(row['total_mass']-1)<3e-14 and abs(row['stationary_total']-1)<3e-14
        assert row['s_bt']==other['s_bt']
        rows.append(row)
        qa,quantum,mass,dt,keep=episode_law(cell)
        for q,mode in zip(*np.nonzero(mass)):
            episodes.append(dict(cell=cell['id'],qA_packet=qa,qB_packet=F(int(q))*quantum,
                                 mode=int(mode),probability=float(mass[q,mode])))
        scaled.append(dict(cell=cell['id'],time_scale=3,rate_scale=7,
                           s_bt_original=row['s_bt'],s_bt_scaled=other['s_bt'],residual=0))
    wall=time.perf_counter()-start
    for row in rows:
        if row['role']=='negative_control': assert abs(row['s_bt']-1)<3e-14
    csv_out(out,'design_diagnostics.csv',rows); csv_out(out,'scale_checks.csv',scaled)
    csv_out(out,'episode_states.csv',episodes)
    stationary=[]
    keeps=[.5,.625,.9,.99]+[(1+math.exp(-2/120/k))/2 for k in (.3,1,3)]
    for s in keeps:
        for q,mode in product(range(30),(0,1)):
            incoming=sum(stationary_mass(previous,old,s)*(s if old==mode else 1-s)
                         for previous in range(q+3) for old in (0,1)
                         if max(0,previous+(1 if old else -2))==q)
            value=stationary_mass(q,mode,s)
            stationary.append(dict(keep=s,q=q,mode=mode,stationary=value,incoming=incoming,
                                   balance_error=abs(value-incoming),infinite_total=stationary_total(s)))
    csv_out(out,'stationary_balance.csv',stationary)
    threshold_examples=[dict(gain=g,C_ref=8,verdict=verdict(g,8),
                             converted_ms_packet=to_ms_per_packet(g,100)) for g in (.1,-.03,.05,.04,-.04,.08,-.08)]
    csv_out(out,'threshold_examples.csv',threshold_examples)
    alarms=[r['cell'] for r in rows if r['upper_scalar_updates']>manifest['budget']['max_updates_per_cell_level'] or
            r['estimated_peak_bytes']>manifest['budget']['max_estimated_workspace_bytes']]
    result=dict(author='Doan Van Tai',status='TECHNICAL_PASS_WITH_PENDING_GATES',config=config,
                tests=dict(lesson=lesson,full_suite=full),references=references,
                idle_pairs=len(idle),idle_mismatches=0,episode_state_rows=len(episodes),main_cells=24,negative_controls=2,stress_cells=2,
                reserve_coordinates=16,reserve_generated=False,new_grid_contrasts_computed=False,
                diagnostic_wall_s=wall,max_D_mass_error=max(abs(r['total_mass']-1) for r in rows),
                stationary_balance_max_error=max(r['balance_error'] for r in stationary),
                main_s_bt_min=min(r['s_bt'] for r in rows if r['role']=='main'),
                main_s_bt_max=max(r['s_bt'] for r in rows if r['role']=='main'),
                negative_s_bt=[r['s_bt'] for r in rows if r['role']=='negative_control'],
                max_upper_updates=max(r['upper_scalar_updates'] for r in rows),
                max_estimated_peak_bytes=max(r['estimated_peak_bytes'] for r in rows),
                budget_alarm_cells=alarms,budget_measured_full_J=False,final_dt='PENDING_A01',
                numerical_grid_convergence='NOT_RUN_BEFORE_TAG',consistency=checks,random_draws=0)
    write_json(out/'results.json',result)
    plot(out,rows)
    text=report(result,rows); (out/'report.md').write_text(text); print(text,flush=True)
    return result


def plot(out,rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    x=np.arange(len(rows))
    axes[0].bar(x,[r['s_bt'] for r in rows]); axes[0].set_ylabel('Conservation mass s_bt')
    axes[1].bar(x,[r['upper_scalar_updates'] for r in rows]); axes[1].set_yscale('log')
    axes[1].axhline(2e9,color='red',linestyle='--',label='planning budget')
    axes[1].set_ylabel('Conservative scalar-update estimate'); axes[1].legend()
    for ax in axes:
        ax.set_xticks(x,[r['cell'] for r in rows],rotation=90,fontsize=7)
        ax.set_xlabel('Declared discovery/control/stress cell')
    fig.tight_layout(); fig.savefig(out/'design_diagnostics.png',dpi=160); plt.close(fig)


def report(r,rows):
    refs=r['references']; tests_=r['tests']
    lines=['# L1.8 C–E — kết quả thực chạy','',
      'Người thực hiện: **Doan Van Tai**. G1; technical freeze có điều kiện, không human/independent sign-off.','',
      f"- Lesson **{tests_['lesson']['passed']}/{tests_['lesson']['total']} PASS**; full suite **{tests_['full_suite']['passed']}/{tests_['full_suite']['total']} PASS**.",
      f"- Idle: {r['idle_pairs']} cặp action, {r['idle_mismatches']} mismatch; goldens {refs['golden_values']} giá trị, 0 vi phạm.",
      f"- Backward/forward B16: {refs['backward_forward_values']} giá trị, max error {refs['backward_forward_max_error']:.12g}; correlated additivity {refs['correlated_queue_checks']} cases PASS.",
      f"- 24 main+2negative+2stress; main s_bt min/max={r['main_s_bt_min']:.12g}/{r['main_s_bt_max']:.12g}; controls={r['negative_s_bt']}.",
      f"- D mass error max={r['max_D_mass_error']:.12g}; infinite-stationary balance error max={r['stationary_balance_max_error']:.12g}; scaling 28/28 PASS.",
      f"- Diagnostic thực chạy {r['diagnostic_wall_s']:.6g}s (28 ô và28 scale copies); không phải runtime tính J.",
      f"- Upper bound max **{r['max_upper_updates']:,} scalar updates**, peak workspace estimate **{r['max_estimated_peak_bytes']:,} bytes**; planning-budget alarms: {', '.join(r['budget_alarm_cells']) or 'không có'}.",
      '- Budget là ước lượng bảo thủ, chưa benchmark full J. Các ô alarm giữ nguyên; A01 cần tối ưu/benchmark, không tuyên bố toàn lưới đã tính được.',
      f"- Canonical I: E[I]={refs['canonical_interaction']['mean']}, EabsI={refs['canonical_interaction']['expected_abs']}, P(absI>δ)={refs['canonical_interaction']['probability_exceeding_delta']}, δ={refs['canonical_interaction']['delta']} (teaching units).",
      '- Ngưỡng đã chọn: Cref=Lstar cùng ô/cùng dt, εR1%, εE.5%, discretization budget.25%; các threshold examples là function checks, không measured network gains.',
      '- Consistency:5 PASS và1 PARTIAL (full Final Review thiếu); source reading note đã đối chiếu. V0 byte-exact với contract-v0.',
      '- Final dt/main-grid refinement A01 **CHƯA CHẠY**. Không tính J/gaps/margins/contrasts trên new grid; reserve16 chỉ tọa độ, chưa sinh; RNG/seed mới0.','',
      '## Tái lập','', '```bash',
      'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_l1_8_cde',
      '.venv/bin/python -m pytest -q tests/test_l1_8_contract.py',
      '.venv/bin/python -m pytest -q',
      '.venv/bin/python notes/verification/verify_l1_8_cde_artifacts.py', '```','',
      'Runner lưu commands thực tế, phiên bản, input/source SHA256 và design commit ở config.json. Không ghi đè run cũ: dùng --output-dir khác khi tái lập. JUnit/log đầy đủ: lesson.txt/.xml, full_suite.txt/.xml.','',
      '## Số liệu và output','',
      '| File | Nội dung |','|---|---|',
      '| design_diagnostics.csv | Toàn bộ28 ô, s_bt, mass, ratios, conservative budget |',
      '| episode_states.csv | Finite D sau prehistory; cho auditor dựng lại law/screen độc lập |',
      '| idle_grid_5832.csv, stationary_balance.csv, scale_checks.csv | Kiểm độc lập rollout, stationary incoming balance và scale |',
      '| golden_costs.csv, backward_forward_B16.csv, queue_additivity.csv | J checks trên worked examples đã exposed, không main grid |',
      '| canonical_I_delta.csv, threshold_examples.csv | Diagnostic I và test quy đổi/ngưỡng |',
      '| results.json, config.json, consistency_checks.json | Metrics, inputs, status và checks |',
      '| run_output.txt, lesson.txt/.xml, full_suite.txt/.xml | Log thực và JUnit |',
      '| design_diagnostics.png | Conservation mass và budget; không gain map |',
      '| artifact_manifest.json | SHA256 outputs, không self-hash |','',
      'Contract/brief/cards/closeout nằm trong notes; code chính src/smr/{design,exact,thresholds}.py. Các phần tự học/human feedback/primary literature/network validity chưa xác nhận, HOLD Phase4 trước V10. A01/A04 sau tag là bước nghiên cứu riêng, không thực hiện âm thầm trong L1.8.','',
      '## Bảng thiết kế thực đo','',
      '| Cell | Role | states D | s_bt | H | update upper bound |',
      '|---|---|---:|---:|---:|---:|']
    for row in rows:
        lines.append(f"| {row['cell']} | {row['role']} | {row['states']} | {row['s_bt']:.9g} | {row['H']} | {row['upper_scalar_updates']} |")
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_cde')
    out=parser.parse_args().output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    if (out/'config.json').exists(): raise SystemExit('Output exists; select a fresh --output-dir to preserve evidence')
    with (out/'run_output.txt').open('w') as handle:
        with contextlib.redirect_stdout(Tee(sys.stdout,handle)),contextlib.redirect_stderr(Tee(sys.stderr,handle)):
            run(out)
    write_json(out/'artifact_manifest.json',dict(author='Doan Van Tai',files=[
        dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
        if p.is_file() and p.name!='artifact_manifest.json']))


if __name__=='__main__': main()
