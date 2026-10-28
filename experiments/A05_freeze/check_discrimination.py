"""Doan Van Tai — synthetic 100k reverse-triangle and lesson examples only."""
import json
from pathlib import Path
import numpy as np

from experiments.A05_freeze.scoring import compare


def main():
    seed=13603
    rng=np.random.default_rng(seed)
    p0,p1,y=rng.normal(size=(3,100000,3))
    D=np.mean(abs(p0-p1),axis=1)
    d=np.mean(abs(p0-y)-abs(p1-y),axis=1)
    excess=abs(d)-D
    # Floating summation can differ by a few ulps; report both raw and tolerance counts.
    tolerance=16*np.finfo(float).eps*np.maximum(1,D)
    a=compare([(0,0),(0,0),('1.3','1.3')],[0,'1.2',0],[0,'.4','1.1'],margin='.25')
    b=compare([(0,0),(0,0),('1.3','1.3')],[0,'.1','.2'],[0,'.15','.1'],margin='.25')
    result=dict(responsible='Doan Van Tai',seed=seed,synthetic_only=True,
                trials=100000,entries_per_trial=3,raw_positive_roundoff_count=int(sum(excess>0)),
                violations_above_float_allowance=int(sum(excess>tolerance)),
                maximum_raw_excess=float(max(excess)),
                lesson_example_support={k:str(v) for k,v in a.items()},
                lesson_example_do_not_open={k:str(v) for k,v in b.items()},
                heldout_metadata_or_outcomes_read=False)
    out=Path(__file__).resolve().parents[2]/'results/lessons/l3_6/preflight/discrimination_toys.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert result['violations_above_float_allowance']==0
    assert a['verdict']=='SUPPORT' and b['verdict']=='DO_NOT_OPEN'


if __name__=='__main__':main()
