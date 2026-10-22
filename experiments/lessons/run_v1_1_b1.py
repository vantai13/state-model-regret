"""Doan Van Tai — integrate/verify B1 only; no v1.1 grid or p_switch."""
import argparse
import contextlib
import csv
import json
import math
import platform
import subprocess
import sys
import time
import types
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

from smr.dominance import cell_label, cell_masses, classify_state, empty_after_every_slot
from experiments.lessons.run_l1_8_a import Tee, clean, sha, tests, write_json
from tests import test_dominance_v1_1 as reference

ROOT=Path(__file__).resolve().parents[2]
INPUT_FOLDERS=('3211803d-71c7-4fc6-92f2-a8cfa6a7d0fb',
               '37dcc956-8a6f-4d29-957f-a1e48edc5de0',
               '49acaac5-1e7e-4303-af33-78ae0a1480a1',
               '66cc89a7-531e-4387-b4b5-d22fa0bff405')
FROZEN=('notes/01_definitions_v1.md','notes/design/grid_v1.md','notes/design/grid_v1.json',
        'src/smr/design.py','src/smr/exact.py','src/smr/thresholds.py',
        'notes/phases/PHASE_1_closeout.md','notes/lessons/L1.8D_decision_cards.md')


def csv_write(out,name,rows):
    with (out/name).open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(clean(rows))


def csv_read(path):
    with path.open() as handle: return list(csv.DictReader(handle))


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def classification(out):
    """Read the EXISTING v1 CSV. No episode_law or action-value calls."""
    manifest=json.loads((ROOT/'notes/design/grid_v1.json').read_text())
    saved=csv_read(ROOT/'results/lessons/l1_8_cde/episode_states.csv')
    groups=defaultdict(list)
    for row in saved:
        groups[row['cell']].append((F(row['qA_packet']),'det',F(row['qB_packet']),
                                    int(row['mode']),float(row['probability'])))
    dt=F(manifest['profile']['dt_candidate_s'])
    rows=[]
    for cell in manifest['cells']:
        H=F(cell['horizon'])/dt; assert H.denominator==1
        plant=dict(ratesA={'det':5*dt},ratesB={0:2*dt,1:14*dt},
                   cA=10*dt,cB=10*dt,u=2*F(cell['eta'])*dt,H=int(H))
        masses=cell_masses(groups[cell['id']],plant)
        assert abs(masses['total']-1)<3e-14
        rows.append(dict(cell=cell['id'],role=cell['role'],**masses,label=cell_label(masses,tol=1e-12)))
    sd={r['cell'] for r in rows if r['label']=='SD-cell'}
    assert sd=={f'M{i:02}' for i in range(1,13)}|{'S01'}
    assert set(manifest['calibration_cells'])<=sd
    counts=dict(Counter(r['label'] for r in rows))
    assert counts=={'SD-cell':13,'conservation-cell':2,'candidate':13}
    csv_write(out,'v1_classification.csv',rows)
    reserve=[]
    for i,c in enumerate(manifest['reserve_coordinates_only'],1):
        z,eta=F(c['z']),F(c['eta']); yA=2*z; u=2*eta
        qa=max(F(0),yA+(5+u-10))  # age=1, deterministic A pre-Stay
        H=z/(1-eta)/dt; assert H.denominator==1
        sd2=empty_after_every_slot(qa,'det',{'det':5*dt},u*dt,10*dt,int(H))
        reserve.append(dict(coordinate_id=i,role=c['role'],z=z,kappa=c['kappa'],eta=eta,
                            qA_t0=qa,SD2=sd2,D_generated=False,action_values_computed=False))
    csv_write(out,'v1_reserve_parameters.csv',reserve)
    assert sum(r['SD2'] for r in reserve if r['role']=='held_out')==6
    assert sum(r['role']=='held_out' for r in reserve)==12
    return dict(v1_cells=len(rows),positive_support_states=len(saved),labels=counts,
                SD_cells=sorted(sd),calibration_SD_cells=manifest['calibration_cells'],
                held_out_SD2=6,held_out_coordinates=12,reserve_D_generated=False,
                v1_action_values_computed=False)


def exhaustive(out):
    metrics={name:dict(condition=name,states=0,pathwise_violations=0,M0_sign_violations=0)
             for name in ('SD1','SD2','WD1','WD2')}
    n_states=path_pairs=switch_wins=conservation=0
    groups=Counter()
    conservation_violations=necessary_violations=0
    for plant,state in reference._small_plants():
        n_states+=1
        groups[plant.get('verification_group','supplied_grid')]+=1
        flags=classify_state(*state,plant)
        diffs=[]
        for a,b in product(reference._paths(state[1],plant['H']),reference._paths(state[3],plant['H'])):
            d=reference._cost(state,a,b,plant,'Switch')-reference._cost(state,a,b,plant,'Stay')
            diffs.append(d); path_pairs+=1
            if d<0:
                switch_wins+=1
                qa,_=reference._rollout(state[0],a,plant['ratesA'],plant['u'],plant['cA'])
                _,ib=reference._rollout(state[2],b,plant['ratesB'],0,plant['cB'])
                necessary_violations+=not(any(q>0 for q in qa) and any(i>0 for i in ib))
        gap=reference._m0_cost(state,plant,'Switch')-reference._m0_cost(state,plant,'Stay')
        for name,row in metrics.items():
            if flags[name]:
                row['states']+=1
                row['pathwise_violations']+=any(d<0 if name.startswith('SD') else d>0 for d in diffs)
                row['M0_sign_violations']+=gap<0 if name.startswith('SD') else gap>0
        if flags['label']=='conservation':
            conservation+=1; conservation_violations+=any(d!=0 for d in diffs)
    assert dict(groups)=={'supplied_grid':9216,'integration_low_arrival':3456}
    assert n_states==12672 and path_pairs==116352
    assert not necessary_violations and not conservation_violations
    assert all(r['states']>0 and r['pathwise_violations']==r['M0_sign_violations']==0 for r in metrics.values())
    csv_write(out,'exhaustive_conditions.csv',list(metrics.values()))
    plant=dict(H=3,cA=3,cB=3,u=1,keepA=F(1,2),keepB=F(1,2),
               ratesA=dict(off=5,on=5),ratesB=dict(off=1,on=5))
    state=(10,'on',0,'on')
    J={act:sum(reference._prob(a,plant['keepA'])*reference._prob(b,plant['keepB'])*
               reference._cost(state,a,b,plant,act)
               for a,b in product(reference._paths('on',3),repeat=2)) for act in ('Stay','Switch')}
    M={act:reference._m0_cost(state,plant,act) for act in ('Stay','Switch')}
    assert J=={'Stay':F(109,2),'Switch':F(54)} and M=={'Stay':54,'Switch':54}
    csv_write(out,'wd_tie_example.csv',[dict(action=a,truth_J=J[a],M0_J=M[a],
                                           cost_unit='packet times teaching time unit') for a in ('Stay','Switch')])
    return dict(states=n_states,state_groups=dict(groups),path_pairs=path_pairs,conditions=list(metrics.values()),
                strictly_switch_winning_paths=switch_wins,necessary_condition_violations=necessary_violations,
                conservation_states=conservation,conservation_violations=conservation_violations,
                WD_tie_truth_J=J,WD_tie_M0_J=M,WD_tie_M0_regret=F(1,2))


def mutations(out):
    source=(ROOT/'src/smr/dominance.py').read_text()
    test_source=(ROOT/'tests/test_dominance_v1_1.py').read_text()
    specs=[('idle_less_equal','if q0 + first < capacity:','if q0 + first <= capacity:',
            'test_closed_forms_match_explicit_rollouts'),
           ('empty_uses_minimum','max(rates.values()) + extra <= capacity',
            'min(rates.values()) + extra <= capacity','test_closed_forms_match_explicit_rollouts'),
           ('SD2_omits_managed','SD2=empty_after_every_slot(qA, mA, rA, u, cA, H)',
            'SD2=empty_after_every_slot(qA, mA, rA, 0, cA, H)','test_four_conditions_hold_pathwise_and_for_m0')]
    rows=[]
    for name,old,new,target in specs:
        assert source.count(old)==1
        module=types.ModuleType('b1_mutant_'+name)
        exec(compile(source.replace(old,new,1),f'<{name}>','exec'),module.__dict__)
        env={'__name__':'b1_mutant_reference'}
        exec(compile(test_source,'<reference tests>','exec'),env)
        for function in ('can_idle_within','empty_after_every_slot','classify_state','cell_masses','cell_label'):
            env[function]=getattr(module,function)
        start=time.perf_counter()
        try:
            env[target]()
        except AssertionError:
            status='KILLED'
        else:
            status='SURVIVED'
        rows.append(dict(mutant=name,status=status,test=target,wall_s=time.perf_counter()-start,
                         edits_to_production_files=0))
    assert all(r['status']=='KILLED' for r in rows)
    csv_write(out,'mutation_checks.csv',rows)
    return rows


def check_old_artifacts():
    counts={}
    for lesson in ('l1_8_a','l1_8_b','l1_8_cde'):
        folder=ROOT/'results/lessons'/lesson
        manifest=json.loads((folder/'artifact_manifest.json').read_text())
        for entry in manifest['files']:
            p=folder/entry['file']
            assert p.stat().st_size==entry['size_bytes'] and sha(p)==entry['sha256'],p
        counts[lesson]=len(manifest['files'])
    return counts


def render(r):
    e=r['exhaustive']; c=r['classification']; t=r['tests']
    return '\n'.join([
      '# B1 v1.1 — kết quả tích hợp/kiểm chứng','',
      'Người thực hiện: **Doan Van Tai** · **23/10/2026**, Asia/Saigon. Ngày nguồn patch22/10 và attribution được giữ nguyên; không nhận đây là bài kín sách/V11 hoặc independent review.','',
      f"- Baseline trước áp patch: **{r['baseline']['passed']}/{r['baseline']['total']} PASS**.",
      f"- Dominance tests: **{t['lesson']['passed']}/{t['lesson']['total']} PASS**; toàn repo **{t['full_suite']['passed']}/{t['full_suite']['total']} PASS**.",
      f"- Vét cạn **{e['states']:,} state-parameter configurations**, **{e['path_pairs']:,} cặp path**. Bốn điều kiện SD1/SD2/WD1/WD2:0 vi phạm path-wise và0 vi phạm dấu M0.",
      '- Gồm9.216 ca nguồn +3.456 ca bổ sung low-arrival/H1. Ca nguồn không kích hoạt SD2/WD2; coverage assertion đã phát hiện lỗi này ở lần đầu, dù154 tests PASS. Log/config/JUnit và coverage counts được giữ trong first_run/. Không nới tiêu chí coverage để PASS.',
      f"- **{e['strictly_switch_winning_paths']:,} path Switch thắng**:0 vi phạm điều kiện cần; conservation **{e['conservation_states']:,} states**,0 vi phạm.",
      f"- Phân loại v1 từ **{c['positive_support_states']:,} rows D đã lưu**, không tính J: **13 SD-cell,2 conservation-cell,13 candidate**. SD=M01–M12,S01; calibration M01/M02/M10 đều SD.",
      '- Reserve v1:6/12 tọa độ held-out thỏa SD2 từ tham số A;4 extrapolation còn lại không SD2. Không sinh D reserve, không tính action values.',
      '- WD/tie toy: truth J(Stay)=54.5,J(Switch)=54; M0=54/54 → chọn Stay, regret0.5 packet·time-unit. WD không phải zero control.',
      '- Ba mutant có chủ đích: **3/3 KILLED** bằng assertion của reference tests; chạy trong memory, không tạo mutant patch/file hoặc sửa source thật.',
      '- Guards mới bắt NaN/Inf, empty/zero support; state probability10⁻⁴⁰ không bị bỏ bởi tolerance. No RNG, no seed mới.','',
      '## Đã sửa gì','',
      'Áp patch sau git apply --check. Giữ provenance nguồn, thêm người tích hợp/ngày thực. Code mới dominance.py; tám điều kiện/proofs và DL-026…028; status hiện tại HOLD A01/A04 trên grid v1. Gia cố phân loại ô bằng support certificates thay vì chỉ so mass≈1.','',
      'Sửa các claim quá mạnh: p_sw trong khoảng không đủ chứng minh State gain dương (ties); ngoài khoảng nhưng chưa0/1 là oracle-lệch. Fraction(float_P) không tự là exact law R2. Solver stationary A sau này cần tail/error control, không chỉ finite residual. PHASE_1 full chưa có nên xung đột V11 là reported/source comparison pending, không tự xác minh trích dẫn.','',
      '## Phạm vi đã thực hiện và còn chờ','',
      '**B1 hoàn thành phần tích hợp/verification; bản điều kiện vẫn DRAFT để tác giả review.** Chưa chọn số lưới v1.1, chưa có grid_v1_1.md/json, chưa p_switch/ĐK2, chưa calibration/reserve mới hoặc A01; không tag contract-v1.1. Bảy lựa chọn §11, dt screen và cách xác nhận dấu R2 phải chốt/commit trước B3. Không gửi heads-up/email, không tạo human feedback, không thay bài tự làm.','',
      'v1 và snapshot A/B/CDE giữ byte; không di chuyển tag contract-v1 hoặc v0. Support/regime v1 được dùng lại là exposed verification. Random200paths/ô của mock review là exposure do attachment báo, không có seed/log để tái lập; không tính nó là kiểm PASS trong phiên này. G1 giữ nguyên, P0-V3/V10/V11 còn OPEN.','',
      '## Commands và files','',
      '```bash',
      'git apply --check .git/l1_8_b1_source.patch',
      'git apply .git/l1_8_b1_source.patch',
      'PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_b1',
      '```','',
      'Runner gọi pytest thật (command,returncode,Junit trong results.json). Baseline được chạy trước áp patch; lesson/full tests sau áp patch và sửa integration. CSV ghi scalar/Fraction, no Monte Carlo CI. Đơn vị test toy là packet×teaching time unit; không quy thành physicalms của R2.','',
      '| File | Nội dung |','|---|---|',
      '| config.json,results.json | SHA2564inputs, source hashes, tag/base, actual commands/metrics |',
      '| baseline.json/.txt/.xml,lesson.txt/.xml,full_suite.txt/.xml | Trước/sau và JUnit thực |',
      '| exhaustive_conditions.csv | Đếm state từng điều kiện, vi phạm path/M0 |',
      '| v1_classification.csv | 28 old cells, mass/support certificates/label |',
      '| v1_reserve_parameters.csv | 16 old coordinates, chỉ kiểm SD2 tham số; no D |',
      '| wd_tie_example.csv | J và M0 hai action của teaching counterexample |',
      '| mutation_checks.csv | Ba lỗi được cài trong memory và test bắt lỗi |',
      '| artifact_checks.json,artifact_manifest.json | Read-back CSV/JUnit/hashes và frozen snapshots |',
      '| first_run/ | Lần runner FAIL coverage: log/config/JUnit và phân tích nguyên nhân, giữ nguyên byte |',
      '| run_output.txt,report.md | Log và báo cáo hiển thị kết quả |','',
      'Source src/smr/dominance.py; tests/test_dominance_v1_1.py; conditions notes/design/design_conditions_v1_1.md; decisions/exposure ở notes/02_decision_log.md và notes/00_exposure_register.md. Không tạo biểu đồ: đây là theorem/control verification và bản điều kiện B1, chưa có kết quả grid v1.1 để vẽ.',''])


def execute(out):
    assert (out/'baseline.json').exists(),'Capture baseline BEFORE applying source patch'
    baseline=json.loads((out/'baseline.json').read_text())
    assert baseline['total']==baseline['passed']==146
    base=git('rev-parse','HEAD')
    assert not (ROOT/'notes/design/grid_v1_1.json').exists()
    assert not (ROOT/'notes/design/grid_v1_1.md').exists()
    frozen={p:git('rev-parse',f'contract-v1:{p}') for p in FROZEN}
    for p in FROZEN:
        assert subprocess.check_output(['git','show',f'contract-v1:{p}'],cwd=ROOT)==(ROOT/p).read_bytes(),p
    source=('src/smr/dominance.py','tests/test_dominance_v1_1.py',
            'notes/design/design_conditions_v1_1.md','experiments/lessons/run_v1_1_b1.py')
    inputs=[Path('/home/vantai/.codex/attachments')/folder/'Pasted text.txt' for folder in INPUT_FOLDERS]
    config=dict(author='Doan Van Tai',execution_time=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                source_document_date='2026-10-22',integration_date='2026-10-23',python=platform.python_version(),
                git_base_commit=base,contract_v1_target=git('rev-parse','contract-v1^{}'),
                immutable_v1_blobs=frozen,source_patch_original_commit='e1763b16bff6a4ecd56aa0534fca2592318e0e5c',
                input_hashes=[dict(path=str(p),sha256=sha(p)) for p in inputs],
                source_hashes={p:sha(ROOT/p) for p in source},
                command=[sys.executable,'-m','experiments.lessons.run_v1_1_b1','--output-dir',str(out)],
                baseline_command=baseline['command'],scope='B1 only; no v1.1 grid or p_switch',
                random_draws=0,new_seeds=[],source_attribution='Retained in imported patch files',
                independent_human_validation=False)
    write_json(out/'config.json',config)
    lesson=tests(out,'lesson',['tests/test_dominance_v1_1.py'])
    full=tests(out,'full_suite',[])
    classification_result=classification(out)
    exhaustive_result=exhaustive(out)
    mutation_result=mutations(out)
    assert all(sha(ROOT/p)==digest for p,digest in config['source_hashes'].items())
    result=dict(author='Doan Van Tai',status='B1_TECHNICAL_PASS_DESIGN_CHOICES_PENDING',
                baseline=baseline,tests=dict(lesson=lesson,full_suite=full),config=config,
                classification=classification_result,exhaustive=exhaustive_result,mutations=mutation_result,
                new_v1_1_grid_computed=False,p_switch_computed=False,new_v1_1_tag_created=False,
                new_rng_draws=0,gate='G1; HOLD A01/A04 on grid_v1; P0-V3/V10/V11 OPEN')
    write_json(out/'results.json',result)
    old_manifests=check_old_artifacts()
    for t in (baseline,lesson,full):
        cases=list(ET.parse(out/t['junit']).iter('testcase'))
        assert len(cases)==t['passed']==t['total']
        assert all(c.find('failure') is None and c.find('error') is None and c.find('skipped') is None for c in cases)
    assert len(csv_read(out/'v1_classification.csv'))==28
    assert all(int(r['pathwise_violations'])==int(r['M0_sign_violations'])==0
               for r in csv_read(out/'exhaustive_conditions.csv'))
    write_json(out/'artifact_checks.json',dict(author='Doan Van Tai',status='PASS',
               old_manifest_files_verified=old_manifests,immutable_v1_blobs=frozen,
               source_hashes_match=True,baseline_lesson_full_JUnit_verified=True,
               v1_1_grid_absent=True,random_draws=0))
    report=render(result); (out/'report.md').write_text(report); print(report,end='',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_v1_1_b1')
    out=parser.parse_args().output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    if (out/'config.json').exists(): raise SystemExit('Use fresh output directory to preserve existing evidence')
    with (out/'run_output.txt').open('w') as handle:
        with contextlib.redirect_stdout(Tee(sys.stdout,handle)),contextlib.redirect_stderr(Tee(sys.stderr,handle)):
            try:
                execute(out)
            except Exception:
                import traceback
                traceback.print_exc()
                raise
    write_json(out/'artifact_manifest.json',dict(author='Doan Van Tai',files=[
        dict(file=str(p.relative_to(out)),size_bytes=p.stat().st_size,sha256=sha(p))
        for p in sorted(out.rglob('*')) if p.is_file() and p != out/'artifact_manifest.json']))


if __name__=='__main__': main()
