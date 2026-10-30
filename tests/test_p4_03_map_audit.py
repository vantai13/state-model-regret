"""Synthetic L4.3 guard tests; no engine calls or real CF inputs."""
from fractions import Fraction as F
import json
import subprocess
import sys

import pytest

from experiments.P4_03_map_audit import common as C
from experiments.P4_03_map_audit.prepare import native_cases


CASE=dict(id='FAKE_DISCOVERY',parameters=['6','7','1/5','1/2','2','0'])


def row(level=(640,4),gs='2',gm='1/10',gam='2/5',cref='100'):
    gs,gm,gam=map(F,(gs,gm,gam))
    values=dict(G_S=gs,G_M=gm,G_SM=gs+gm+gam,Gamma=gam,G_S_M1=gs+gam,G_M_S1=gm+gam)
    return dict(id=CASE['id'],parameters=CASE['parameters'],status='COMPLETED',K=level[0],ref=level[1],
                Cref=cref,**{k:str(v) for k,v in values.items()},
                normalized_error={k:'0' for k in C.METRICS},Sbar='100',GM_identity_gap='0',
                arithmetic_pass=True,validity_errors=[],CF_computed=False)


def fixture():
    rows={lv:row(lv) for lv in C.LEVELS}
    alias=dict(id='FAKE',zones=['A'],pilot_class='A',pilot_pctC={m:str(C.pct(rows[C.LEVELS[0]],m)) for m in C.METRICS})
    return alias,rows


def test_cf_guard_exact_six_coordinate_key():
    key=C.canonical(CASE['parameters'])
    with pytest.raises(RuntimeError,match='CF_COLLISION'):C.forbid_cf(CASE['parameters'],{key})
    C.forbid_cf(CASE['parameters'],set())


def test_cf_guard_survives_python_optimized_mode():
    code="from experiments.P4_03_map_audit.common import forbid_cf,canonical; p=['6','7','1/5','1/2','2','0']; forbid_cf(p,{canonical(p)})"
    p=subprocess.run([sys.executable,'-O','-c',code],capture_output=True,text=True)
    assert p.returncode and 'CF_COLLISION' in p.stderr


def test_age_normalized_CF_collision_is_refused_before_native_import():
    r=dict(id='old_age',_key=tuple(map(F,['6','7','1/10','1/2','1','1/2','6'])),
           **{'class':'A'},**{m+'_pctC':0 for m in C.METRICS})
    with pytest.raises(RuntimeError,match='CF_COLLISION'):
        native_cases([r],{C.canonical(CASE['parameters'])})


def test_compare_same_values_is_pass():
    alias,rows=fixture();result=C.compare(alias,CASE,rows)
    assert result['status']=='PASS' and not result['class_flipped'] and result['native_class_R6']=='A'


def test_algebra_guard_detects_modified_gamma():
    r=row();r['Gamma']='1'
    with pytest.raises(RuntimeError,match='S11'):C.validate_row(r,CASE,(640,4))


@pytest.mark.parametrize('field,bad', [('arithmetic_pass',False),('arithmetic_pass',1),
                                     ('validity_errors',['fake_error']),('CF_computed',True),
                                     ('parameters',['6','8','1/5','1/2','2','0'])])
def test_native_row_guards(field,bad):
    r=row();r[field]=bad
    with pytest.raises(RuntimeError):C.validate_row(r,CASE,(640,4))


def test_R1_also_checks_Cref_and_all_six_contrasts():
    alias,rows=fixture();rows[(320,4)]['Cref']='101'
    result=C.compare(alias,CASE,rows)
    assert result['status']=='HOLD' and 'R1' in result['reasons']


def test_pilot_native_tolerance_is_not_a_class_tolerance():
    alias,rows=fixture()
    alias['pilot_pctC']['G_S']='1.008'
    for r in rows.values():
        gs=F('0.970');gm=F('0.01');gam=F('0.23')
        r.update(G_S=str(gs),G_M=str(gm),G_SM=str(gs+gm+gam),Gamma=str(gam),
                 G_S_M1=str(gs+gam),G_M_S1=str(gm+gam))
    alias['pilot_pctC'].update({m:str(C.pct(rows[(640,4)],m)) for m in C.METRICS if m!='G_S'})
    result=C.compare(alias,CASE,rows)
    assert result['status']=='PASS' and result['class_flipped'] and result['native_class']=='D'
    assert abs(result['shift_pp']['G_S'])<.25


def test_refinement_near_threshold_is_unresolved():
    alias,rows=fixture()
    for lv,gs in [((640,4),'0.970'),((320,4),'0.935'),((640,2),'0.950')]:
        rows[lv]=row(lv,gs=gs,gm='0',gam='0')
    alias['pilot_pctC']={m:str(C.pct(rows[(640,4)],m)) for m in C.METRICS}
    result=C.compare(alias,CASE,rows)
    assert result['status']=='PASS' and result['unresolved_A_GS']


def test_zero_measured_d_at_threshold_has_no_exact_certificate():
    alias,rows=fixture()
    rows={lv:row(lv,gs='1') for lv in C.LEVELS}
    alias['pilot_pctC']={m:str(C.pct(rows[(640,4)],m)) for m in C.METRICS}
    assert C.compare(alias,CASE,rows)['native_class_R6']=='UNRESOLVED'


def test_missing_or_nonpositive_reference_is_HOLD():
    alias,rows=fixture();rows.pop((640,2))
    assert C.compare(alias,CASE,rows)['status']=='HOLD'
    alias,rows=fixture();rows[(640,4)]['Cref']='0'
    assert C.compare(alias,CASE,rows)['status']=='HOLD'


def test_exclusive_write_preserves_previous_result(tmp_path):
    p=tmp_path/'result.json';C.write_once(p,{'result':1})
    with pytest.raises(FileExistsError):C.write_once(p,{'result':2})
    assert json.loads(p.read_text())=={'result':1}


def test_negative_or_positive_pilot_shift_above_tolerance_is_HOLD():
    alias,rows=fixture();alias['pilot_pctC']['G_S']='2.251'
    result=C.compare(alias,CASE,rows)
    assert result['status']=='HOLD' and 'PILOT_NATIVE:G_S' in result['reasons']
