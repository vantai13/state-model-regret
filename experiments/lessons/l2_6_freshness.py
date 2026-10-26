"""L2.6 Part A teaching calculations; no grid evaluation or held-out access.

Responsible: Doan Van Tai. Exact binary-cost arithmetic; floating-point CTMC
formulas are independently checked against repeated transitions/quadrature.
"""
from fractions import Fraction as F
from itertools import product
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"results/lessons/l2_6/part_a"


def encode(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x


def write_csv(name,rows):
    with (OUT/name).open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(encode(rows))


def simpson(f,b,n=2000):
    step=b/n
    return step/3*(f(0)+f(b)+sum((4 if i%2 else 2)*f(i*step) for i in range(1,n)))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    checks=[]

    def check(name,condition):
        if not condition: raise AssertionError(name)
        checks.append(name)

    # Periodic delivery with exogenous fixed delay, no losses/reordering/queueing.
    ages=[]
    for period,delay in product((F(2),F(4),F(8)),(F(0),F(1),F(2))):
        continuous=delay+period/2
        # Integrate each affine tooth using its endpoints, not point samples.
        area=F(0)
        for i in range(8):
            start,end=delay+i*period/8,delay+(i+1)*period/8
            area+=(start+end)*period/16
        check(f"periodic area T={period},d={delay}",area/period==continuous)
        discrete=sum(delay+i for i in range(int(period)))/period
        check(f"slotted age T={period},d={delay}",discrete==delay+(period-1)/2)
        ages.append(dict(period_seconds=period,delay_seconds=delay,continuous_mean_age=continuous,
                         slot_start_mean_age=discrete,age_before_delivery=delay+period))

    mode_rows=[]
    max_semigroup_error=max_quadrature_error=0.0
    for k in (.3,1.,3.):
        a=k/2;dt=1/120
        keep=(1+math.exp(-2*dt/k))/2  # Same expression as src/smr/design.py:103.
        same,different=1.,0.
        sampled={}
        for n in range(1,961):
            same,different=same*keep+different*(1-keep),same*(1-keep)+different*keep
            if n in (120,960): sampled[n/120]=same
        for t in (1.,8.):
            exact=.5+.5*math.exp(-2*t/k)
            err=abs(sampled[t]-exact)
            max_semigroup_error=max(max_semigroup_error,err)
            check(f"CTMC semigroup k={k},t={t}",err<1e-12)
            check(f"return includes even switches k={k},t={t}",exact>math.exp(-t/k))
        # Stationary symmetric telegraph INPUT, not a queue posterior/backlog.
        norm=2*a*(1-a*(-math.expm1(-1/a)))
        var=36*norm
        integral=2*36*simpson(lambda s:(1-s)*math.exp(-s/a),1)
        error=abs(var-integral)
        max_quadrature_error=max(max_quadrature_error,error)
        check(f"integrated covariance k={k}",error<1e-8)
        mode_rows.append(dict(kappa=k,Tmode_seconds=k,correlation_seconds=a,
                              same_after_1s=.5+.5*math.exp(-2/k),same_after_8s=.5+.5*math.exp(-16/k),
                              no_switch_during_1s=math.exp(-1/k),variance_over_delta_squared=norm,
                              variance_packets_squared=var,sd_packets=math.sqrt(var),
                              quadrature_abs_error=error))
    check("input variance increases for these three examples",all(mode_rows[i]["sd_packets"]<mode_rows[i+1]["sd_packets"] for i in range(2)))

    # Binary decisions with exact tie -> Stay. Common nonnegative stay cost=3.
    identity=[]
    for g1,g2,p in product((F(-3,2),F(-1,2),F(0),F(1,2),F(3,2)),
                           (F(-3,2),F(-1,2),F(0),F(1,2),F(3,2)),
                           (F(0),F(1,4),F(1,2),F(3,4),F(1))):
        ep=p*max(g1,0)+(1-p)*max(g2,0)
        em=p*max(-g1,0)+(1-p)*max(-g2,0)
        prior_gap=p*g1+(1-p)*g2
        before=F(3)+(prior_gap if prior_gap<0 else 0)
        informed=p*(3+min(g1,0))+(1-p)*(3+min(g2,0))
        value=before-informed
        check(f"binary identity {g1},{g2},p={p}",value==min(ep,em) and value>=0)
        check(f"strict sign criterion {g1},{g2},p={p}",(value>0)==(ep>0 and em>0))
        identity.append(dict(gap1=g1,gap2=g2,p1=p,Epositive=ep,Enegative=em,
                             L01=before,L11=informed,value=value))

    # A new abstract gap table, not a modification of the queue toy or contract.
    exercise=[]
    for name,switch_lo in [("V1_true_gaps",F(0)),("flip_lo_gap",F(3))]:
        st=(F(3),F(3,2));sw=(F(5,2),switch_lo)
        gap=tuple(sw[i]-st[i] for i in range(2))
        ep=sum((max(v,F(0)) for v in gap),F(0))/2
        em=sum((max(-v,F(0)) for v in gap),F(0))/2
        a01="Sw" if sum(sw)<sum(st) else "St"
        l01=sum(sw if a01=="Sw" else st)/2
        l11=sum(min(st[i],sw[i]) for i in range(2))/2
        check(name+": direct value",l01-l11==min(ep,em))
        exercise.append(dict(case=name,gap_hi=gap[0],gap_lo=gap[1],a01=a01,
                             Epositive=ep,Enegative=em,L01=l01,L11=l11,GSgivenM1=l01-l11))
    check("modified gap exercise = 1/4",exercise[1]["GSgivenM1"]==F(1,4))
    tie_case=next(r for r in identity if (r["gap1"],r["gap2"],r["p1"])==(F(-1,2),F(0),F(1,2)))
    check("p_sw half but no strict positive gap",tie_case["value"]==0 and tie_case["Epositive"]==0 and tie_case["Enegative"]==F(1,4))

    frozen=json.loads((ROOT/"results/lessons/l2_5/part2/toy_results.json").read_text())["cases"]["V1"]
    check("V1 true-law gain frozen",F(frozen["con"]["GSgM1"])==exercise[0]["GSgivenM1"]==0)
    check("V1 fixed-M0 gain frozen",F(frozen["con"]["GS"])==F(-1,4))
    entropy_before=-sum(.5*math.log2(.5) for _ in range(2))
    check("binary entropy disclosure",entropy_before==1)
    # Illustrative timestamps only; no assertion of finite-time R2 independence.
    four_values=dict(illustrative_age_before_seconds=1,illustrative_age_after_seconds=0,
                     prior="independent old sample and current equiprobable mode, teaching setup",
                     entropy_reduction_bits=1,GSgivenM1="0",GS="-1/4")

    truth=[1,1,2,2,2,1];last_correct=0;ao_ii=[]
    for t,x in enumerate(truth):
        if x==1:last_correct=t
        penalty=(t-last_correct)*(x!=1)
        ao_ii.append(dict(t_slot=t,truth=x,estimate=1,AoI_slots=t,AoII_linear_indicator=penalty))
    check("old but correct AoII=0",ao_ii[-1]["AoI_slots"]==5 and ao_ii[-1]["AoII_linear_indicator"]==0)
    check("AoII sequence",[r["AoII_linear_indicator"] for r in ao_ii]==[0,0,1,2,3,0])

    config=dict(responsible="Doan Van Tai",seed=None,status="exposed teaching verification; not grid outcomes",
                age_seconds=1,kappa=[.3,1,3],mode_times_seconds=[1,8],mode_step_seconds="1/120",
                variance=dict(delta_packets_per_second=6,tau_seconds=1,stationary_symmetric=True,
                              method="unconditional integrated telegraph input, no reflection or conditioning on y",
                              quadrature="composite Simpson n=2000",abs_tolerance=1e-8),
                arithmetic="fractions.Fraction for costs/AoI; float for exponentials",
                mode_abs_tolerance=1e-12,entropy_unit="bit",decision_cost_unit="packet*s",tie="Stay")
    result=dict(status="PASS",check_count=len(checks),checks=checks,four_values=four_values,
                mode_rows=mode_rows,exercise=exercise,identity_cases=len(identity),
                max_semigroup_abs_error=max_semigroup_error,max_quadrature_abs_error=max_quadrature_error,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    for name,data in [("config.json",config),("toy_results.json",result)]:
        (OUT/name).write_text(json.dumps(encode(data),ensure_ascii=False,indent=2)+"\n")
    for name,data in [("periodic_age.csv",ages),("mode_and_input_variance.csv",mode_rows),
                      ("binary_identity.csv",identity),("gap_exercise.csv",exercise),("aoi_aoii_example.csv",ao_ii)]:
        write_csv(name,data)
    print(json.dumps(encode({k:v for k,v in result.items() if k!="checks"}),ensure_ascii=False))


if __name__=="__main__":main()
