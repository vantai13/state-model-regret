"""Checks for counting/grouping mistakes, using synthetic rows only."""
from fractions import Fraction as F

import pytest

from experiments.P4_02_reading import read_map as M
from experiments.P4_01_recount import recount_map as R


def row(rid='x',gs=0,gm=0,age='1',k='.1',h='4',amp='6',a='6',b='6.5'):
    key=tuple(map(F,(a,b,k,'.75',h,age,amp)))
    return dict(id=rid,_key=key,age=float(age),G_S_pctC=gs,G_M_pctC=gm,
                G_SM_pctC=0,Gamma_pctC=0,G_S_M1_pctC=0,G_M_S1_pctC=0,**{'class':'D'})


def test_boundary_union_counts_a_row_once_and_keeps_signed_bound():
    near=row(gs=-1.1,gm=1.05)
    got=M.boundary_rows([near,row('far',gs=1.151)])
    assert len(got)==1 and got[0]['nearest_contrast']=='G_M_pctC'
    negative=M.boundary_rows([row(gs=-1.1)])
    assert negative[0]['boundary_pctC']==-1


def test_age_pairing_scales_both_times_but_retains_amplitude():
    base=row('base',k='.2',h='8')
    scaled=row('scaled',age='.5',k='.1',h='4',gs=.2)
    other_plant=row('other',age='.5',k='.1',h='4',amp='4')
    pairs=M.same_scaled_age_pairs([base,scaled,other_plant])
    assert len(pairs)==1 and pairs[0]['base_id']=='base'
    assert pairs[0]['max_contrast_abs_difference_pp']==.2


def test_delta_slice_includes_boundaries_and_excludes_other_plants():
    selected=M.delta_slice([row('lo',k='.05',h='4'),row('hi',k='.15',h='8'),
                            row('amp',amp='4'),row('kout',k='.151'),row('hout',h='8.001')])
    assert [r['id'] for r in selected]==['lo','hi']


def test_plurality_is_not_majority_and_rate_delta_has_normalized_counterpart():
    rows=[row(str(i),a='6.25',b='7') for i in range(18)]
    values={'AB':(2,2,4,0),'C':(-2,0,0,2),'B':(0,2,2,0)}
    for i,r in enumerate(rows):
        r['class']='AB' if i<8 else 'C' if i<15 else 'B'
        # R.counts recomputes labels from contrasts; keep the fixture coherent.
        r.update(zip(R.NUM[:4],values[r['class']]))
    cell=M.cross_table(rows)[0]
    assert cell['plurality_labels']=='AB' and cell['plurality_count']==8
    assert cell['has_strict_majority'] is False
    assert cell['delta']=='3/4' and cell['delta_over_mu']=='3/40' and cell['headroom_ratio']=='4/5'


def test_source_hash_failure_precedes_csv_parsing(tmp_path,monkeypatch):
    table=tmp_path/M.TABLE; table.parent.mkdir(parents=True)
    table.write_text('invalid csv')
    (tmp_path/M.MANIFEST).write_text('{"outputs_sha256":{"recounted_regimes.csv":"wrong"}}')
    monkeypatch.setattr(R,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='hash mismatch'):
        M.load_table()


def test_existing_output_stops_before_integrity_or_data_read(tmp_path,monkeypatch):
    from experiments.P4_02_reading import run
    def forbidden(): raise AssertionError('input read for an existing output')
    monkeypatch.setattr(run,'verify',forbidden)
    with pytest.raises(FileExistsError,match='before reading data'):
        run.main(['--out',str(tmp_path)])
