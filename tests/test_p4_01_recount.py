"""Doan Van Tai — AI-authored fixture answers, not an author hand-work attestation."""
import csv
import io
from fractions import Fraction as F

import pytest

from experiments.P4_01_recount import recount_map as R


def fake_csv():
    # Choose four losses with Cref=100, so absolute contrasts equal pctC.
    # Manual algebra (AI): GS=L00-L10, GM=L00-L01, GSM=L00-100,
    # Gamma=L10+L01-L00-100. C also has GM>=1 to test C priority.
    losses = [('A',103,100.5,102.8), ('B',103,102.8,100.5),
              ('AB',105,103,103), ('J',101.5,101,101),
              ('C',103,104,100), ('D',100.75,100.5,100.5)]
    out=io.StringIO()
    cols=['id','lambdaA','lambdaB','kappa','eta','h','Cbar',*R.NUM]
    w=csv.DictWriter(out,fieldnames=cols)
    w.writeheader()
    for i,(label,l00,l10,l01) in enumerate(losses):
        w.writerow(dict(id=label,lambdaA=6,lambdaB=8,kappa='.1',eta='.5',h=i+1,Cbar=100,
                        **dict(zip(R.NUM,(l00-l10,l00-l01,l00-100,l10+l01-l00-100,l01-100,l10-100)))))
    lines=out.getvalue().splitlines()
    return '\n'.join(lines+[lines[1].replace('A,','A_copy,',1)])+'\n'


def test_six_classes_and_exact_duplicate_from_csv():
    rows=R.read_rows(fake_csv(),'synthetic')
    table,dropped=R.dedup(rows)
    assert [R.cls(r) for r in table]==['A','B','AB','J','C','D']
    assert len(rows)==7 and len(table)==6 and len(dropped)==1
    assert dropped[0]['kept_id']=='A' and dropped[0]['dropped_id']=='A_copy'


@pytest.mark.parametrize('gs,gm,gsm,gamma,label',[
    (-1,3,2,0,'C'),(-.999,1,1,.999,'B'),(1,.999,2,.001,'A'),
    (1,1,2,0,'AB'),(.25,.25,1,.5,'J'),(.25,.25,.999,.499,'D'),
    (.8,.1,1,.1,'D'),(.25,.25,1,.249999,'D'),
])
def test_inclusive_thresholds_and_joint_condition(gs,gm,gsm,gamma,label):
    assert R.cls(dict(zip(R.NUM,(gs,gm,gsm,gamma,0,0))))==label


@pytest.mark.parametrize('field',['G_S_pctC','Cbar','ref'])
def test_conflicting_duplicate_stops(field):
    rows=R.read_rows(fake_csv(),'synthetic')
    rows[-1][field]=rows[-1].get(field,1)+.1
    # ref absent in the fixture: add it to first copy to test numerical level conflict.
    if field=='ref': rows[0]['ref']=1
    with pytest.raises(ValueError,match='conflicting duplicate'):
        R.dedup(rows)


def test_wall_time_is_not_a_deterministic_outcome():
    rows=R.read_rows(fake_csv(),'synthetic')
    rows[0]['wall_s']=1
    rows[-1]['wall_s']=999
    assert len(R.dedup(rows)[0])==6


def test_exact_key_does_not_merge_nearby_coordinates():
    rows=R.read_rows(fake_csv().replace('A_copy,6,','A_copy,6.00000000001,'),'synthetic')
    assert len(R.dedup(rows)[0])==7


def test_default_plant_and_c_sw_filter():
    rows=R.read_rows(fake_csv(),'synthetic')
    assert all(r['age']==1 and r['amp']==6 and r['c_sw']==0 for r in rows)
    blob=fake_csv().replace('id,','c_sw,id,',1)
    lines=blob.splitlines()
    blob='\n'.join([lines[0]]+['1,'+line for line in lines[1:]])
    assert R.read_rows(blob,'synthetic')==[]


@pytest.mark.parametrize('bad',['nan','inf','-inf'])
def test_nonfinite_outcomes_rejected(bad):
    with pytest.raises(ValueError,match='non-finite'):
        R.read_rows(fake_csv().replace(',100,',f',{bad},',1),'synthetic')


def test_linear_quantile_known_interpolation():
    assert R.q_linear([0,10,20,30],.9)==pytest.approx(27)
    assert R.q_linear([4],.9)==4


def test_mv_filter_uses_scaled_age_and_amplitude_namespace():
    r={'_key':tuple(map(F,('7.5','8','.1','.5','8','.5','6')))}
    assert R.in_mv_plus(r)
    assert R.namespace_key(r)==('v1.3_fixed_plant','15/2|8|1|1/5|16|0')
    r['_key']=(*r['_key'][:-1],F(4))
    assert not R.in_mv_plus(r)
    assert R.namespace_key(r)[0]=='explore_amplitude_4'


def test_existing_output_refused_before_build(tmp_path,monkeypatch):
    def forbidden(): raise AssertionError('read data before output guard')
    monkeypatch.setattr(R,'build',forbidden)
    with pytest.raises(FileExistsError,match='before reading data'):
        R.main(['--out',str(tmp_path)])
