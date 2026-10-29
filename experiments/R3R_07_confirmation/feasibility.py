"""Design arithmetic only; never instantiate a stationary law or engine."""
from fractions import Fraction as F
from functools import reduce
from math import gcd,lcm


def lattice_size(lam,managed,ref=1):
    lam,managed=F(lam),F(managed)
    increments=[(lam+managed-16)/ (120*ref),(lam+managed-4)/(120*ref)]
    denominator=lcm(*(x.denominator for x in increments))
    scaled=[int(x*denominator) for x in increments]
    unit=F(reduce(gcd,map(abs,scaled)),denominator)
    steps=[int(x/unit) for x in increments]
    return dict(unit=str(unit),steps=steps,polynomial_degree=max(steps)-min(steps))


def report(inventory):
    pilot=[r['coordinates'] for r in inventory['records'] if r['source'] in ('stage1','stage2','stage3')]
    maximum=max(lattice_size(r['lambdaA'],r['u'])['polynomial_degree'] for r in pilot)
    return dict(scope='parameter-only arithmetic; no runtime/RAM claim; no engine instantiation',
                max_pilot_A_pre_degree=maximum,
                illustrative_rates=dict(lambdaA='7123/1000',u='617/500'),
                illustrative_ref1=lattice_size('7123/1000','617/500',1),
                illustrative_ref2=lattice_size('7123/1000','617/500',2),
                engine_runs=0,
                requirement='v1.3.1 must cover interior 1/1000 lattice feasibility as well as kappa=3,h=16; '
                            'changing frozen measure/rounding requires card v2 + DL before frame')
