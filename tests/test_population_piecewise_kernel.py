"""Exact finite-path references for compressed Bellman and stale expectations."""
from functools import lru_cache
from fractions import Fraction as F
import numpy as np
import pytest
from experiments.R3R_08_population_numerics import piecewise as P


def exact(H,inc,p):
    @lru_cache(None)
    def f(t,q,m):
        if not t:return F(0)
        next=max(0,q+inc[m]);idle=max(0,-q-inc[m])
        return t*idle+p*f(t-1,next,m)+(1-p)*f(t-1,next,1-m)
    return lambda q,m:f(H,q,m)


@pytest.mark.parametrize('inc,p,H',[((-2,1),F(3,4),12),((-7,5),F(9,10),25),((-3,-1),F(1,2),9),((1,2),F(3,4),10)])
@pytest.mark.parametrize('budget',['1e-8','0.2'])
def test_uniform_kernel_encloses_exact_path_costs(inc,p,H,budget):
    table=P.idle(H,inc,p,error_budget_raw=np.longdouble(budget));truth=exact(H,inc,p)
    qs=np.arange(0,H*max(0,-min(inc))+10,dtype=np.int64)
    for m in (0,1):
        computed=P.evaluate(table,qs,m)
        reference=np.array([P.number(truth(int(q),m)) for q in qs],dtype=np.longdouble)
        assert np.max(abs(reference-computed))<=table['error']
        assert computed[-1]==0


@pytest.mark.parametrize('p',[F(1,2),F(3,4),F(9,10)])
def test_mean_path_hinges_match_independent_forward_reflection(p):
    H=30;inc=(-5,3);table=P.mean_idle(H,inc,p)
    for q0 in range(50):
        for m in (0,1):
            q=F(q0);total=F(0)
            for k in range(H):
                net=F(sum(inc),2)+(2*m-1)*F(inc[1]-inc[0],2)*(2*p-1)**k
                total+=(H-k)*max(F(0),-q-net);q=max(F(0),q+net)
            got=P.evaluate(table,np.array([q0]),m)[0]
            assert abs(got-P.number(total))<=table['error']


def test_backward_age_matches_independent_forward_path_distribution():
    inc=(-3,2);p=F(3,4);table=P.idle(15,inc,p,error_budget_raw=np.longdouble('.005'))
    aged=P.age(table,9,inc,p,error_budget_raw=np.longdouble('.005'))
    for q0 in (0,1,7,22,50):
        for m0 in (0,1):
            distribution={(q0,m0):F(1)}
            for _ in range(9):
                new={}
                for (q,m),w in distribution.items():
                    end=max(0,q+inc[m])
                    for mode in (0,1):new[end,mode]=new.get((end,mode),F(0))+w*(p if mode==m else 1-p)
                distribution=new
            truth=sum(w*exact(15,inc,p)(q,m) for (q,m),w in distribution.items())
            value=P.evaluate(aged,np.array([q0]),m0)[0]
            assert abs(value-P.number(truth))<=aged['error']


def test_compression_budget_refuses_instead_of_truncating():
    with pytest.raises(ArithmeticError,match='knot budget'):
        P.idle(40,(-7,3),F(9,10),max_knots=2)
