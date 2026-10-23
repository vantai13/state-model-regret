"""Doan Van Tai — controlled toy mutant: recover idle by subtracting large costs.

Run only the preregistered synthetic conservation test. No candidate data.
"""
import time
import numpy as np


def cost_subtraction(indices,increments,H,keep,keep_error=0,extended=False):
    start=time.monotonic();q=np.asarray(indices,dtype=np.int64);growth=max(0,*increments)
    domain=int(max(q))+H*growth;old=np.zeros((domain+1,2));s=float(keep)
    for t in range(1,H+1):
        n=int(max(q))+(H-t)*growth;points=np.arange(n+1);new=np.zeros((n+1,2))
        for m,a in enumerate(increments):
            end=np.maximum(0,points+a)
            assert max(end)<len(old)
            new[:,m]=end+s*old[end,m]+(1-s)*old[end,1-m]
        old=new
    linear=np.zeros(2)
    for initial in (0,1):
        probability=np.array([float(initial==0),float(initial==1)])
        for k in range(H):
            linear[initial]+=(H-k)*np.dot(probability,increments)
            probability=np.array([s*probability[0]+(1-s)*probability[1],(1-s)*probability[0]+s*probability[1]])
    result=old[q]-H*q[:,None]-linear
    return result,0.,time.monotonic()-start


if __name__=='__main__':
    import sys,pytest
    import smr.gap_screen as module
    module.backward=cost_subtraction
    raise SystemExit(pytest.main(['-q','tests/test_gap_screen.py::test_zero_capacity_loss_is_exact_zero_and_large_toy_fits_budget',*sys.argv[1:]]))
