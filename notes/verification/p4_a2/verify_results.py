"""Doan Van Tai: read-only, independent arithmetic audit of completed A2 outputs.

No engine imports/calls, rho selection, or regional effect/regret medians.
Writes separate verification/CSV artifacts; never modifies the frozen experiment.
"""
import csv
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'results/lessons/p4_a2'
RUN = ROOT / 'results/lessons/l4_4/a2_probe'
PREREG = ROOT / 'experiments/P4_A2/runs/L44_PROBE/prereg.json'
METRICS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')
FIELDS = dict(L00='error00', L10='error10', GS_theta='GS_theta_error', deltaL10='deltaL10_error')
REPLAY = ('Cref', 'losses', 'cost_error', 'contrast_error', 'normalized_error',
          'uncertain_action_mass', 'Stay', 'Stay_error', 'baseline', *METRICS,
          'Sbar', 'Sbar_error', 'GM_identity_gap', 'P_flip',
          'zero_action_certificate', 'identical_models_test')
TOL, WIDTH = F(1, 400), F(1, 4000)


def read(p):
    return json.loads(p.read_text())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if p.exists():
        assert p.read_text() == text, f'never overwrite a changed audit: {p}'
    else:
        with p.open('x') as stream:
            stream.write(text)


def delta(fine, coarse, field, getter):
    cf, cc = F(fine['Cref']), F(coarse['Cref'])
    a, b = F(getter(fine, field)), F(getter(coarse, field))
    return max(abs(a-b)/cf, abs(a/cf-b/cc))


def native_ready(rows):
    fine, *coarse = rows
    for row in coarse:
        if abs(F(fine['Cref'])-F(row['Cref'])) / F(fine['Cref']) > TOL:
            return False
        for key in METRICS:
            if delta(fine, row, key, lambda r, k: r[k]) > TOL:
                return False
            a, b = F(fine[key])/F(fine['Cref']), F(row[key])/F(row['Cref'])
            if a*b < 0 and abs(a) > F(1, 200) and abs(b) > F(1, 200):
                return False
    for row in rows:
        c = F(row['Cref'])
        if max(map(F, row['normalized_error'].values())) > WIDTH:
            return False
        if row['zero_action_certificate']:
            if any(F(row[k]) != 0 for k in METRICS):
                return False
            continue
        if any(F(row[k])/c < -TOL for k in ('G_M', 'G_SM', 'G_S_M1', 'G_M_S1')):
            return False
        if abs(F(row['GM_identity_gap']))/c > TOL:
            return False
        if any((abs(F(row[k]))-F(row['Sbar']))/c > TOL for k in ('G_S', 'Gamma')):
            return False
    return True


def diagnose(rows, index):
    fine, krow, dtrow = rows
    getter = lambda r, k: r['baseline'][index][k]
    widths = [max(F(r['baseline'][index][e])/F(r['Cref']) for e in FIELDS.values()) for r in rows]
    dk = {k: delta(fine, krow, k, getter) for k in FIELDS}
    dd = {k: delta(fine, dtrow, k, getter) for k in FIELDS}
    flags = ''.join(k for k, bad in [('W', max(widths)>WIDTH), ('K', max(dk.values())>TOL), ('D', max(dd.values())>TOL)] if bad)
    return dict(failure=flags, width=max(widths), dK=dk, ddt=dd)


def main():
    cfg, decision = read(PREREG), read(RUN/'decision.json')
    fp, summary = digest(PREREG), read(RUN/'run_summary.json')
    targets, ladder = cfg['targets'], cfg['ladder']
    assert {p.name for p in (RUN/'native').iterdir()} == {t['id'] for t in targets}
    assert summary['status'] == 'PASS' and summary['completed_ids'] == [t['id'] for t in targets]
    assert summary['a2_prereg_sha256'] == fp == decision['prereg_sha256']
    locked = {**cfg['source_sha256'], **cfg['preserved_history_sha256']}
    for path, expected in locked.items():
        assert digest(ROOT/path) == expected, f'changed frozen file: {path}'
        assert subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) == (ROOT/path).read_bytes()
    assert not subprocess.check_output(['git','diff','a481db7','--',
        'experiments/P4_A1','src','experiments/A00_engine',
        'experiments/R3R_05_contract','experiments/R3R_14_lean_close',
        'experiments/P4_04_baseline','tests/test_p4_a1.py'],cwd=ROOT)
    levels = list(dict.fromkeys(tuple(lv) for step in ladder for lv in step))
    assert len(levels) == 7 and len(targets) == 8
    assert len(list(RUN.glob('native/*/level_*.json'))) == 56
    assert len(list(RUN.glob('controls/*/level_*.json'))) == 1
    files, point_csv, detail_csv, native_counts = [], [], [], [0,0,0]
    ready_counts, native_bad, new_rho_ids, nonmonotone, replay_rows = [0,0,0], [], [], [], 0
    cpu_by_point, first_counts = {}, {'0':0,'1':0,'2':0,'never':0}
    for target, reported in zip(targets, decision['points'], strict=True):
        cid = target['id']; folder = RUN/'native'/cid
        assert reported['id'] == cid
        rows = {lv:read(folder/f'level_{lv[0]}_{lv[1]}.json') for lv in levels}
        receipt = read(folder/'point_summary.json')
        assert receipt['status'] == 'COMPLETED' and receipt['a2_prereg_sha256'] == fp
        expected_paths = {str((folder/f'level_{k}_{r}.json').relative_to(ROOT)) for k,r in levels}
        assert set(receipt['rows_sha256']) == expected_paths
        for lv, row in rows.items():
            path = folder/f'level_{lv[0]}_{lv[1]}.json'; files.append(path)
            assert digest(path) == receipt['rows_sha256'][str(path.relative_to(ROOT))]
            assert row['id'] == cid and row['parameters'] == target['parameters']
            assert (row['K'],row['ref']) == lv and row['dt'] == str(F(1,120*lv[1]))
            assert row['status'] == 'COMPLETED' and not row['a1_bug_reasons']
            assert row['a2_prereg_sha256'] == fp and row['CF_computed'] is False
            assert [b['rho'] for b in row['baseline']] == cfg['rho']
            assert row['call_cpu_seconds'] >= 0 and F(row['Cref']) > 0
            for a,b in [('00','01'),('10','11')]:
                assert F(row['losses'][a])+F(row['cost_error'][a]) >= F(row['losses'][b])-F(row['cost_error'][b])
            for b in row['baseline']:
                for a,err,ref in [('L00','error00','01'),('L10','error10','11')]:
                    assert F(b[a])+F(b[err]) >= F(row['losses'][ref])-F(row['cost_error'][ref])
            if lv in map(tuple,ladder[0]):
                old = read(ROOT/'results/lessons/l4_4/a1/native'/cid/path.name)
                assert all(old[k] == row[k] for k in REPLAY)
                rep = read(folder/f'reproduction_{lv[0]}_{lv[1]}.json')
                assert rep['saved_numerical_fields_equal'] and rep['reparsed_significant_bits_equal']
                assert not rep['unequal_fields'] and not rep['bit_mismatch_fields']
                replay_rows += 1
        cpu_by_point[cid] = math.fsum(row['call_cpu_seconds'] for row in rows.values())
        assert cpu_by_point[cid] == receipt['cpu_seconds']
        states, diagnostic = [], dict(id=cid,target_rho=target['target_rho'][0],cpu_seconds=cpu_by_point[cid])
        new_rhos = set()
        for step_index, step in enumerate(ladder):
            trio = [rows[tuple(lv)] for lv in step]
            native = native_ready(trio); native_counts[step_index] += native
            if not native: native_bad.append([cid,step_index])
            per_rho = [diagnose(trio,i) for i in range(len(cfg['rho']))]
            failing = [rho for rho,d in zip(cfg['rho'],per_rho) if d['failure']]
            ready = native and not failing
            saved = reported['steps'][step_index]
            assert ready == saved['point_ready']
            assert native == (not saved['row_reasons'])
            assert failing == saved['failing_rho']
            for i,(rho,d) in enumerate(zip(cfg['rho'],per_rho)):
                sr = saved['per_rho_diagnostics'][i]
                assert d['failure'] == sr['failure']
                for field in FIELDS:
                    assert float(d['dK'][field]) == sr['d_K_'+field]
                    assert float(d['ddt'][field]) == sr['d_dt_'+field]
                assert float(max(d['dK']['L00'],d['ddt']['L00'])) == saved['L00_refinement'][rho]
                detail_csv.append(dict(id=cid,step=step_index,main_K=step[0][0],main_ref=step[0][1],rho=rho,
                    failure=d['failure'],width_pctCref=100*float(d['width']),
                    dK_L00_pctCref=100*float(d['dK']['L00']),ddt_L00_pctCref=100*float(d['ddt']['L00'])))
            ready_counts[step_index] += ready; states.append(ready)
            new_rhos.update(set(failing)-set(target['target_rho']))
            td = per_rho[cfg['rho'].index(target['target_rho'][0])]
            diagnostic.update({f'ready_step{step_index}':ready,
                f'failing_rho_step{step_index}':','.join(failing),
                f'target_failure_step{step_index}':td['failure'],
                f'target_L00_refinement_pctCref_step{step_index}':100*float(max(td['dK']['L00'],td['ddt']['L00'])),
                f'target_width_pctCref_step{step_index}':100*float(td['width'])})
        first = next((i for i,s in enumerate(states) if s),None)
        assert first == reported['ready_at_step']
        first_counts[str(first) if first is not None else 'never'] += 1
        if any(states[i] and not states[i+1] for i in range(2)): nonmonotone.append(cid)
        if new_rhos: new_rho_ids.append(dict(id=cid,new_failing_rho=sorted(new_rhos,key=F)))
        diagnostic['first_ready_step'] = first
        point_csv.append(diagnostic)
    control = read(RUN/'control_summary.json'); ccase = cfg['control']
    cpath = RUN/'controls'/ccase['id']/'level_1280_8.json'; cr = read(cpath); files.append(cpath)
    creceipt = read(cpath.parent/'point_summary.json')
    assert control['status'] == 'PASS' and cr['zero_action_certificate'] is True
    assert cr['status'] == 'COMPLETED' and cr['parameters'] == ccase['parameters']
    assert cr['id'] == ccase['id'] and (cr['K'],cr['ref']) == (1280,8)
    assert cr['dt'] == str(F(1,960)) and not cr['a1_bug_reasons']
    assert creceipt['status'] == 'COMPLETED' and creceipt['a2_prereg_sha256'] == fp
    assert all(F(cr[k]) == 0 for k in METRICS) and cr['CF_computed'] is False
    assert control['a2_prereg_sha256'] == fp == cr['a2_prereg_sha256']
    assert creceipt['rows_sha256'][str(cpath.relative_to(ROOT))] == digest(cpath)
    cpu = math.fsum(read(p)['call_cpu_seconds'] for p in sorted(files))
    assert cpu == summary['cpu_seconds'] and cpu <= cfg['decisions']['cpu_cap_hours']*3600
    n = 8-first_counts['never']; d = cfg['decisions']
    branch = ('LADDER_RESOLVES' if n >= d['ladder_resolves_if_at_least'] else
              d['branch_if_ladder_fails'] if n <= d['ladder_fails_if_at_most'] else
              'INCONCLUSIVE_AUTHOR_DECIDES_WITH_NEW_DL')
    assert n == decision['n_ready_within_ladder'] and branch == decision['branch']
    assert not decision['rho_selection_computed'] and not decision['regional_medians_computed']
    assert decision['CF_outcomes'] == 0 and replay_rows == decision['replay_rows_confirmed'] == 24
    for name,records in [('point_summary.csv',point_csv),('rho_step_diagnostics.csv',detail_csv)]:
        path = OUT/name
        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer,fieldnames=list(records[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(records)
        if path.exists():
            assert path.read_text() == buffer.getvalue(), f'changed audit CSV: {path}'
        else:
            with path.open('x',newline='') as stream:
                stream.write(buffer.getvalue())
    audit = dict(responsible='Doan Van Tai',status='PASS',engine_calls_in_verifier=0,
        numerical_levels=len(files),discovery_levels=len(files)-1,controls=1,
        source_locks_verified=len(cfg['source_sha256']),history_locks_verified=len(cfg['preserved_history_sha256']),
        replay_rows_equal=24,native_ready_by_step=native_counts,baseline_point_ready_by_step=ready_counts,
        first_ready_step_counts=first_counts,n_ready_within_ladder=n,branch=branch,
        cpu_seconds=cpu,cpu_hours=cpu/3600,control_cpu_seconds=cr['call_cpu_seconds'],cpu_by_point=cpu_by_point,
        native_not_ready=native_bad,new_failing_rho_points=new_rho_ids,ready_then_not_ready=nonmonotone,
        raw_arithmetic_pass_counts={str(v):sum(read(p)['arithmetic_pass'] is v for p in files) for v in (True,False)},
        raw_validity_nonempty=sum(bool(read(p)['validity_errors']) for p in files),
        bug_rows=0,reproduction_mismatches=0,rho_selection_computed=False,regional_medians_computed=False,
        CF_outcomes=0,new_coordinates=0,prereg_sha256=fp,
        artifacts_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(files)+[RUN/'decision.json',RUN/'run_summary.json']},
        verifier_sha256=digest(Path(__file__)))
    save(OUT/'verification.json',audit)
    print(json.dumps({k:v for k,v in audit.items() if k!='artifacts_sha256'},indent=2,ensure_ascii=False))


if __name__ == '__main__':
    main()
