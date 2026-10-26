"""L2.6 Part B: exact teaching examples, not a P13/grid replication.

Responsible: Doan Van Tai. Fraction arithmetic; all finite cost tables and
fluid examples are declared separately from the locked routing experiment.
"""
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/lessons/l2_6/part_b"
ACT=("St","Sw")


def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x


def csv_out(name,rows):
    with (OUT/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader();w.writerows(encode(rows))


def area(q,r,h):
    """Continuous fluid integral, r>0; no division by h here."""
    duration=min(h,q/r)
    return q*duration-r*duration*duration/2


def endpoint(q,r,h,dt):
    """D13-style right-endpoint rectangle sum, independent recurrence."""
    steps=h/dt
    assert steps.denominator==1
    cost=F(0)
    for _ in range(int(steps)):
        q=max(F(0),q-r*dt)
        cost+=dt*q
        if not q:break
    return cost,q


def choice(st,sw):return "Sw" if sw<st else "St"


def continuous_bias_loss(a,b):
    """Integrate actual policy loss on [-a,a]; affine on cut intervals."""
    cuts=sorted({-a,F(0),a,*([-b] if -a < -b < a else [])})
    loss=F(0)
    for lo,hi in zip(cuts,cuts[1:]):
        d=(lo+hi)/2
        truth=choice(F(5),5+d)
        model=choice(F(5),5+d+b)
        loss+=(hi-lo)*(abs(d) if truth!=model else 0)/(2*a)
    return loss


def finite_table(gaps,bias):
    mass=F(1,len(gaps));mean_gap=sum(gaps,F(0))*mass
    a01=choice(F(5),5+mean_gap)
    a00=choice(F(5),5+mean_gap+bias)
    true=lambda d,a:F(5)+(d if a=="Sw" else 0)
    a10=[choice(F(5),5+d+bias) for d in gaps]
    a11=[choice(F(5),5+d) for d in gaps]
    L={"00":sum((true(d,a00) for d in gaps),F(0))*mass,
       "01":sum((true(d,a01) for d in gaps),F(0))*mass,
       "10":sum((true(d,a) for d,a in zip(gaps,a10)),F(0))*mass,
       "11":sum((true(d,a) for d,a in zip(gaps,a11)),F(0))*mass}
    return dict(**{f"L{k}":v for k,v in L.items()},
                GS=L["00"]-L["10"],GM=L["00"]-L["01"],
                GMgS1=L["10"]-L["11"],Gam=L["10"]+L["01"]-L["00"]-L["11"],
                a00=a00,a01=a01)


def main():
    OUT.mkdir(parents=True,exist_ok=True);checks=[]
    def check(name,test):
        if not test:raise AssertionError(name)
        checks.append(name)

    fluid=[];discrete=[]
    for q,h in product((F(10),F(20)),map(F,(2,5,10,100))):
        r=F(2);value=area(q,r,h);end=max(F(0),q-r*h)
        t=min(h,q/r)
        trapezoid=t*(q+max(F(0),q-r*t))/2
        check(f"fluid independent trapezoid q={q},h={h}",value==trapezoid)
        tail=end*end/(2*r)
        check(f"remaining area q={q},h={h}",value+tail==q*q/(2*r))
        fluid.append(dict(q0=q,r=r,h=h,drain=q/r,integral=value,average=value/h,
                          qH=end,post_h_continuous_area=tail,lifetime_area=q*q/(2*r)))
        for dt in (F(1),F(1,10),F(1,100)):
            c,final=endpoint(q,r,h,dt)
            check(f"endpoint quadrature q={q},h={h},dt={dt}",value-c==dt*(q-end)/2 and final==end)
            discrete.append(dict(q0=q,r=r,h=h,dt=dt,endpoint_sum=c,continuous_integral=value,
                                 error=value-c,qH=final,last_endpoint_charge=dt*final))
    check("fluid exercise20 = four times25",area(F(20),F(2),F(100))==100==4*area(F(10),F(2),F(100)))
    check("zero initial backlog control",area(F(0),F(2),F(10))==0)
    # Definition u_k in P13 §2.1 versus the M/M/1 example printed in §5.1.
    # N~Poisson(1): E[N],E[N²],E[N³]=1,2,5; S|N=n~Gamma(n,1).
    raw1,raw2,raw3=F(1),F(2)+1,F(5)+3*2+2
    central3=raw3-3*raw1*raw2+2*raw1**3
    check("P13 unit compound Poisson exponential third central moment",central3==6 and raw2-raw1**2==2)
    # T00 helper is read-only and only used for this synthetic link/capacity.
    from l0_6_timescale import drain_time_s
    check("T00 drain reference =5s",abs(drain_time_s(10,120000,.8)-5)<1e-12)

    gaps=[]
    for drift,h in product((F(-1,2),F(0),F(1,2)),(F(2),F(8))):
        values=(drift*h+3,drift*h-3)
        ep=sum((max(d,F(0)) for d in values),F(0))/2
        em=sum((max(-d,F(0)) for d in values),F(0))/2
        l01=min(F(10),10+sum(values)/2)
        l11=sum((min(F(10),10+d) for d in values),F(0))/2
        check(f"gap horizon identity drift={drift},h={h}",l01-l11==min(ep,em))
        gaps.append(dict(drift=drift,h=h,gap1=values[0],gap2=values[1],Epositive=ep,
                         Enegative=em,L01=l01,L11=l11,GSgM1=l01-l11))
    check("lesson gap7,1 Epositive corrected to4",next(r for r in gaps if r["drift"]==F(1,2) and r["h"]==8)["Epositive"]==4)

    smooth=[]
    for horizon in map(F,(2,10,100)):
        # Normalized toy objective, not the P13 capacity cost.
        cost=lambda x:(x-5)**2+2*x/horizon
        actual=5-1/horizon;steady=F(5)
        loss=cost(steady)-cost(actual)
        check(f"continuous optimizer shift/loss T={horizon}",loss==1/horizon**2)
        smooth.append(dict(T=horizon,mu_steady=steady,mu_optimal=actual,
                           average_loss=loss,cumulative_loss=horizon*loss))
    biases=(F(-1),F(0),F(1,4),F(2,5),F(1,2),F(3,5),F(1),F(3,2),F(2),F(4),F(6))
    binary=[];uniform=[];finite=[]
    for b in biases:
        predicted=F(-1,2)+b;act=choice(F(5),5+predicted)
        loss=F(1,2) if act=="St" else F(0)
        check(f"S0 step/bias bound b={b}",loss<=abs(b))
        binary.append(dict(bias=b,true_mean_gap=F(-1,2),predicted_gap=predicted,
                           action=act,loss=loss))
        for a in (F(2),F(4)):
            loss1=continuous_bias_loss(a,b)
            formula=min(abs(b),a)**2/(4*a)
            check(f"uniform exact policy integral a={a},b={b}",loss1==formula)
            uniform.append(dict(halfwidth=a,bias=b,density_at_zero=1/(2*a),
                                loss=loss1,local_quadratic=b*b/(4*a),quadratic_range=abs(b)<=a))
        for name,support in [("balanced_five",tuple(map(F,(-2,-1,0,1,2)))),
                             ("mean_minus_half",(F(-3,2),F(1,2)))]:
            row=finite_table(support,b)
            check(f"finite exact identities {name},b={b}",row["Gam"]==row["GMgS1"]-row["GM"] and row["GM"]>=0 and row["GMgS1"]>=0)
            finite.append(dict(case=name,bias=b,**row))
    find=lambda name,b:next(r for r in finite if r["case"]==name and r["bias"]==b)
    check("finite support loss plateau at small bias",find("balanced_five",F(1,4))["GMgS1"]==0)
    check("Gamma positive without queues",find("balanced_five",F(1))["Gam"]==F(1,5))
    check("Gamma negative without queues",find("mean_minus_half",F(3,5))["Gam"]==F(-1,2))
    check("uniform exercise narrower support =1/8",continuous_bias_loss(F(2),F(1))==F(1,8))

    moments=[]
    for distribution,support in [("q=10",(F(10),)),("q=20",(F(20),)),("q=0_or20",(F(0),F(20)))]:
        mean=sum(support)/len(support);second=sum(x*x for x in support)/len(support)
        variance=sum((x-mean)**2 for x in support)/len(support)
        check(distribution+": second moment",second==mean*mean+variance)
        for eta in (F(1,2),F(3,4)):
            r=F(2);u=r*eta
            direct=second/2*(1/(r-u)-1/r)
            factor=second/(2*r)*eta/(1-eta)
            check(f"moment heuristic algebra {distribution},eta={eta}",direct==factor)
            finite_h=sum((area(x,r-u,F(8))-area(x,r,F(8)) for x in support),F(0))/len(support)
            moments.append(dict(distribution=distribution,mean=mean,variance=variance,second_moment=second,
                                eta=eta,u=u,r_pre=r,r_post=r-u,B_only_limit=direct,
                                B_only_h8=finite_h,mean_B_after_Switch=8+u,capacity=F(10)))

    config=dict(responsible="Doan Van Tai",seed=None,arithmetic="fractions.Fraction",
                status="exposed teaching verification; no grid outcomes or P13 simulation replication",
                fluid=dict(q0=[10,20],r=2,h=[2,5,10,100],dt=["1","1/10","1/100"],unit="packet*s; average in packets"),
                decision_examples=dict(common_Stay_cost=5,biases=encode(biases),finite_supports={"balanced_five":[-2,-1,0,1,2],"mean_minus_half":["-3/2","1/2"]},
                                       uniform_halfwidths=[2,4],unit="abstract cost units, not grid packet*s outcomes"),
                tie="Stay",moment=dict(r_pre=2,eta=["1/2","3/4"],h_for_comparison=8,
                                      scope="B-only constant-drift fluid, long-h limit, not GS or full routing gap"))
    result=dict(status="PASS",check_count=len(checks),checks=checks,
                fluid10_h10=F(25),fluid10_h100=F(25),fluid20_h100=F(100),
                uniform_a4_b1=F(1,16),uniform_a2_b1=F(1,8),
                Gamma_no_queue_positive=find("balanced_five",F(1))["Gam"],
                Gamma_no_queue_negative=find("mean_minus_half",F(3,5))["Gam"],
                unit_compound_Poisson_Exp1=dict(mean=raw1,raw2=raw2,raw3=raw3,third_central=central3),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    for name,data in [("config.json",config),("toy_results.json",result)]:
        (OUT/name).write_text(json.dumps(encode(data),ensure_ascii=False,indent=2)+"\n")
    for name,data in [("fluid.csv",fluid),("endpoint_sum.csv",discrete),("gap_horizon.csv",gaps),
                      ("continuous_optimizer.csv",smooth),("binary_step.csv",binary),
                      ("uniform_bias.csv",uniform),("finite_support_2x2.csv",finite),("moment_heuristic.csv",moments)]:csv_out(name,data)
    print(json.dumps(encode({k:v for k,v in result.items() if k!="checks"}),ensure_ascii=False))


if __name__=="__main__":main()
