"""Doan Van Tai — finite references for L1.7, independent of RNG/sampler code.

Exact law uses L1.3 future enumeration and L1.2 plant. Shifted coupling enumerates
six independent keep/flip bits under p=s=1/2 using parity, without mode_path.
"""
from fractions import Fraction as F
from itertools import product
from math import sqrt

from experiments.lessons.l1_2_queue import two_queue_cost
from experiments.lessons.l1_3_expected_cost import futures
from experiments.lessons.l1_4_factorial import choose

ACTIONS = ("Stay", "Switch")


def direct_cost(x, th, b, action):
    return two_queue_cost(x[:2], [th["bA"]]*th["H"], b, th["u"], th["cA"], th["cB"], action)[0]


def moments(rows):
    """Rows (P, CStay, CSwitch); exact covariance decomposition, population moments."""
    assert sum(p for p,_,_ in rows) == 1
    st = sum(p*a for p,a,_ in rows)
    sw = sum(p*b for p,_,b in rows)
    vst = sum(p*(a-st)**2 for p,a,_ in rows)
    vsw = sum(p*(b-sw)**2 for p,_,b in rows)
    cov = sum(p*(a-st)*(b-sw) for p,a,b in rows)
    var = sum(p*((b-a)-(sw-st))**2 for p,a,b in rows)
    assert var == vst+vsw-2*cov
    return dict(mean_stay=st, mean_switch=sw, delta=sw-st, var_stay=vst, var_switch=vsw,
                covariance=cov, paired_variance=var, independent_variance=vst+vsw,
                correlation=float(cov)/sqrt(float(vst*vsw)) if vst*vsw else None,
                independent_over_paired=float((vst+vsw)/var) if var else None)


def exact_pairs(x, th):
    rows, paths = [], []
    for b,p in futures(x, th):
        a,z = (direct_cost(x,th,b,action) for action in ACTIONS)
        rows.append((p,a,z))
        paths.append(dict(background=str(b),probability=p,stay=a,switch=z,delta=z-a))
    return moments(rows), paths


def shifted_pairs(x, th):
    if th["p_onon"] != F(1,2) or th["p_offoff"] != F(1,2):
        raise ValueError("shifted-bit reference is for p=s=1/2 only")
    def arrivals(flips):
        state = int(x[2] == "on")
        b = [th["rate_on"] if state else th["rate_off"]]
        for flip in flips:
            state ^= flip
            b.append(th["rate_on"] if state else th["rate_off"])
        return b
    rows, paths = [], []
    by_first = {0:[],1:[]}
    for bits in product((0,1), repeat=th["H"]):
        st,sw = arrivals(bits[:-1]),arrivals(bits[1:])
        a,z = direct_cost(x,th,st,"Stay"),direct_cost(x,th,sw,"Switch")
        p = F(1,2**th["H"])
        rows.append((p,a,z))
        by_first[bits[0]].append((2*p,a,z))
        paths.append(dict(bits=str(bits),background_stay=str(st),background_switch=str(sw),
                          probability=p,stay=a,switch=z,delta=z-a))
    result = moments(rows)
    result["conditional_first_keep"] = moments(by_first[0])
    result["conditional_first_flip"] = moments(by_first[1])
    return result,paths


def leak_reference(x, th):
    paths = [(b,p,{a:direct_cost(x,th,b,a) for a in ACTIONS}) for b,p in futures(x,th)]
    J = {a:sum(p*c[a] for _,p,c in paths) for a in ACTIONS}
    star = choose(J["Switch"]-J["Stay"])
    leak = sum(p*min(c.values()) for _,p,c in paths)
    honest = sum(p*q*c[choose(cp["Switch"]-cp["Stay"])]
                 for _,p,c in paths for _,q,cp in paths)
    wins = sum(p*q for _,p,c in paths for _,q,cp in paths
               if c[choose(cp["Switch"]-cp["Stay"])] < c[star])
    return dict(J=J,oracle_action=star,oracle=J[star],leak=leak,honest=honest,honest_win_probability=wins), [
        dict(background=str(b),probability=p,stay=c["Stay"],switch=c["Switch"],
             clairvoyant_action=choose(c["Switch"]-c["Stay"])) for b,p,c in paths]
