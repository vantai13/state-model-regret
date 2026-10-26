"""L2.7 Part B exact examples and coordinate-only K membership.

Responsible: Doan Van Tai. No plant simulation, held-out outcomes or K selection.
"""
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/lessons/l2_7/part_b"
EPS, REL, BUDGET = F(1,200), F(1,100), F(1,400)


def pack(obj):
    if isinstance(obj,F): return str(obj)
    if isinstance(obj,dict): return {k:pack(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)): return [pack(v) for v in obj]
    return obj


def save_json(name,obj):
    (OUT/name).write_text(json.dumps(pack(obj),ensure_ascii=False,indent=2)+"\n")


def save_csv(name,rows):
    with (OUT/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader();w.writerows(pack(rows))


def decision(gaps, predicted, weights=(F(1,2),F(1,2))):
    gaps,predicted=tuple(map(F,gaps)),tuple(map(F,predicted))
    weights=tuple(map(F,weights)); assert sum(weights)==1 and min(weights)>=0
    avg=lambda values:sum((p*v for p,v in zip(weights,values)),F(0))
    g,h=avg(gaps),avg(predicted)
    gm=F(h<0)*g-min(F(0),g)
    known=avg([F(b<0)*a-min(F(0),a) for a,b in zip(gaps,predicted)])
    cref=10+avg([min(F(0),a) for a in gaps])
    return dict(g=g,h=h,GM=gm,GMgivenS1=known,Gamma=known-gm,
                S0_error=abs(h-g),S1_error=avg([abs(b-a) for a,b in zip(gaps,predicted)]),
                Cref=cref,GM_relative=gm/cref,GMgivenS1_relative=known/cref)


def numeric_label(g,e,cref_lo=F(1),cref_hi=F(1)):
    g,e,cref_lo,cref_hi=map(F,(g,e,cref_lo,cref_hi))
    assert e>=0 and cref_lo<=cref_hi
    if cref_lo<=0: return "RELATIVE_UNDEFINED_OR_UNCERTIFIED"
    if e>BUDGET*cref_lo: return "NUMERICAL_BUDGET_HOLD"
    lo,hi=g-e,g+e
    if max(abs(lo),abs(hi))<=EPS*cref_lo: return "EQUIVALENT_CERTIFIED"
    minimum=F(0) if lo<=0<=hi else min(abs(lo),abs(hi))
    if minimum>EPS*cref_hi: return "OUTSIDE_EQUIVALENCE_CERTIFIED"
    return "NUMERICAL_INCONCLUSIVE"


def ci_label(lo,hi):
    lo,hi=F(lo),F(hi); assert lo<=hi
    return "EQUIVALENT_TOST_CRITERION" if -EPS<lo and hi<EPS else "CI_INCONCLUSIVE"


def main():
    OUT.mkdir(parents=True,exist_ok=True);checks=[]
    def check(name,condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    frozen=ROOT/"results/lessons/l2_3/p11_toy.json"
    v1=json.loads(frozen.read_text())["v1"]
    cref=F(v1["L"]["11"]);gm=F(v1["L"]["00"])-F(v1["L"]["01"])
    known=F(v1["L"]["10"])-F(v1["L"]["11"])
    check("V1 S0 equivalence and S1 non-equivalence",gm==0 and known/cref==F(1,5))
    examples={
        "small_margin_exercise":decision([F(-1,100),1],[F(1,100),1]),
        "rare_large_error":decision([-1,1],[1,1],[F(1,1000),F(999,1000)]),
        "cancelling_gap_errors":decision([F(-1,2),F(1,2)],[F(1,2),F(-1,2)]),
        "Gamma_nonzero_both_equivalent":decision([F(-1,1000),F(1,1000)],[F(1,1000),F(1,1000)]),
    }
    small=examples["small_margin_exercise"]
    check("S1 action mismatch can be regret equivalent",small["GMgivenS1"]==F(1,200)
          and small["GMgivenS1_relative"]==F(1,1999)<EPS)
    rare=examples["rare_large_error"]
    check("S1 expected bound does not require pointwise small errors",
          rare["GMgivenS1"]<=rare["S1_error"]<=EPS*rare["Cref"]<2)
    cancel=examples["cancelling_gap_errors"]
    check("S1 cannot replace expected absolute error by absolute mean error",
          cancel["S0_error"]==0 and cancel["GMgivenS1"]==F(1,2))
    n=examples["Gamma_nonzero_both_equivalent"]
    check("nonzero Gamma need not cross equivalence boundary",n["Gamma"]!=0
          and max(n["GM_relative"],n["GMgivenS1_relative"])<=EPS)
    check("tie predicted gap zero selects Stay",decision([F(-1,4)]*2,[0,0])["GM"]==F(1,4))
    check("true gap zero has zero loss despite different actions",decision([0,0],[-1,-1])["GM"]==0)
    common_bias=dict(true_costs=[10,9],model_costs=[12,11],true_gap=-1,model_gap=-1,regret=0)
    check("same action does not require correct predicted costs",
          common_bias["model_gap"]==common_bias["true_gap"] and common_bias["true_costs"]!=common_bias["model_costs"])
    sweep=[]
    for i,values in enumerate(product([F(-1,2),F(-1,4),F(0),F(1,4),F(1,2)],repeat=4)):
        a,b,c,d=values;r=decision([a,b],[c,d])
        assert 0<=r["GM"]<=r["S0_error"]
        assert 0<=r["GMgivenS1"]<=r["S1_error"]
        sweep.append(dict(case=i,true_gap1=a,true_gap2=b,model_gap1=c,model_gap2=d,**r))
    check("625 two-state problems verify both bounds including ties",len(sweep)==625)
    numeric=[]
    cases=[("lesson_pass",".001",".001","1","1","EQUIVALENT_CERTIFIED"),
           ("lesson_straddle",".003",".0025","1","1","NUMERICAL_INCONCLUSIVE"),
           ("closed_boundary",".005","0","1","1","EQUIVALENT_CERTIFIED"),
           ("zero_reference","0","0","0","0","RELATIVE_UNDEFINED_OR_UNCERTIFIED"),
           ("uncertain_reference",".0048","0",".9","1.1","NUMERICAL_INCONCLUSIVE"),
           ("budget_exceeded","0",".003","1","1","NUMERICAL_BUDGET_HOLD"),
           ("gray_exact",".009","0","1","1","OUTSIDE_EQUIVALENCE_CERTIFIED")]
    for name,g,e,cl,ch,expected in cases:
        status=numeric_label(g,e,cl,ch);check("numeric:"+name,status==expected)
        numeric.append(dict(case=name,G=g,error=e,Cref_lower=cl,Cref_upper=ch,
                            interval_lower=F(g)-F(e),interval_upper=F(g)+F(e),status=status))
    ci=[]
    for name,lo,hi,expected in [("pass",".0005",".0035",True),
                                ("straddle","-.004",".008",False),
                                ("touch_boundary","-.001",".005",False),
                                ("positive_relevance",".010",".014",False)]:
        status=ci_label(lo,hi);check("CI:"+name,(status=="EQUIVALENT_TOST_CRITERION")==expected)
        ci.append(dict(case=name,CI90_lower=lo,CI90_upper=hi,status=status,
                       lower_bound_at_least_epsilonR=F(lo)>=REL))
    check("mean across K can mask failure",(F(0)+F(9,1000))/2<=EPS<F(9,1000))
    # A restricted VE example, not the routing plant or an A05 null.
    trueP=[[1,0],[0,1]];altP=[[0,1],[1,0]];gamma=F(1,2)
    bellman=lambda p,v,discount:[1+discount*sum((F(q)*F(x) for q,x in zip(row,v)),F(0)) for row in p]
    ve=dict(trueP=trueP,alternativeP=altP,reward=[1,1],gamma=gamma,
            restricted_v=[0,0],extra_v=[0,1],
            restricted_true=bellman(trueP,[0,0],gamma),restricted_alt=bellman(altP,[0,0],gamma),
            expanded_true=bellman(trueP,[0,1],gamma),expanded_alt=bellman(altP,[0,1],gamma))
    check("restricted VE permits different transition kernels",trueP!=altP and ve["restricted_true"]==ve["restricted_alt"])
    check("enlarging test functions can distinguish models",ve["expanded_true"]!=ve["expanded_alt"])
    check("gamma0 cannot identify transition kernel",bellman(trueP,[0,1],F(0))==bellman(altP,[0,1],F(0)))
    gridpath=ROOT/"notes/design/grid_v1_2.json";grid=json.loads(gridpath.read_text())
    keys=["id","role","kappa","alphaA","alphaB","eta","h","label_1","label_2"]
    coordinates=[{k:r.get(k) for k in keys} for group in ["main","heldout","controls","probes"] for r in grid[group]]
    coordinate_match=lambda r:r["alphaA"]==r["alphaB"]=="9/10" and F(r["h"])==8
    rules={"listed_M19_M22":lambda r:r["id"] in {"M19","M20","M21","M22"},
           "coordinate_kappa3":lambda r:coordinate_match(r) and F(r["kappa"])==3,
           "coordinate_kappa_ge2":lambda r:coordinate_match(r) and F(r["kappa"])>=2}
    memberships=[];summary={}
    for rule,predicate in rules.items():
        matched=[]
        for r in coordinates:
            eligible=r["role"] in {"main","heldout"} and r["label_1"]==r["label_2"]=="candidate"
            included=eligible and predicate(r)
            memberships.append(dict(rule=rule,**r,eligible=eligible,included=included))
            if included:matched.append(r)
        summary[rule]={role:[r["id"] for r in matched if r["role"]==role] for role in ["main","heldout"]}
    check("K list and kappa3 have no held-out member",summary["listed_M19_M22"]["heldout"]==summary["coordinate_kappa3"]["heldout"]==[])
    check("coordinate kappa>=2 matches main4 and held-out2",summary["coordinate_kappa_ge2"]==dict(main=["M19","M20","M21","M22"],heldout=["R03","R04"]))
    check("metadata projection excludes private held-out outcome features",all(set(r)==set(keys) for r in coordinates)
          and not any(k in keys for k in ["lambdaA","p_1","p_2","psi","delta","J","margin"]))
    save_csv("gap_bound_sweep.csv",sweep)
    save_csv("numeric_intervals.csv",numeric);save_csv("CI_examples.csv",ci)
    save_csv("K_membership.csv",memberships);save_json("grid_coordinates.json",coordinates)
    save_json("config.json",dict(responsible="Doan Van Tai",arithmetic="fractions.Fraction",seed=None,
          epsilon_E=EPS,epsilon_R=REL,numerical_budget=BUDGET,info_levels=["S0","S1"],
          sweep_values=["-1/2","-1/4","0","1/4","1/2"],sweep_weights=["1/2","1/2"],
          selected_K_rule=None,heldout_metadata_only=True,MC_samples=0,
          scope="teaching examples/proposed interval reporting; no contract change, grid experiment, null choice or preregistration"))
    save_json("toy_results.json",dict(status="PASS",check_count=len(checks),checks=checks,
          V1=dict(Cref=cref,GM=gm,GMgivenS1=known,GM_relative=gm/cref,GMgivenS1_relative=known/cref),
          examples=examples,common_bias=common_bias,VE_example=ve,K_rule_membership=summary,
          inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [frozen,gridpath]},
          source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    print(f"PASS {len(checks)} checks;625 exact two-state cases; K membership uses coordinates only")
    print(f"V1: S0 model gain/Cref={gm/cref}, S1={known/cref}; small-margin exercise={small['GMgivenS1_relative']}")
    print("K candidates:",json.dumps(summary));print("selected_K_rule=None; MC_samples=0; P02 PartA still BLOCKED")


if __name__=="__main__":main()
