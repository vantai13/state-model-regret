"""Doan Van Tai — exact L1.6 A-D verification; outputs outside source directories.

Run: .venv/bin/python -m experiments.lessons.run_l1_6
No RNG/seed, repository copies, warm-up simulation, H0 fitting or held-out evaluation.
"""
import argparse
import hashlib
import inspect
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.lessons.l1_2_queue import rollout, two_queue_cost
from experiments.lessons.l1_3_expected_cost import CANON, expected_cost, futures, generate_episodes
from experiments.lessons.l1_4_factorial import choose, contrasts
from experiments.lessons.l1_5_identity import i_delta, regret_identity
from experiments.lessons.l1_6_belief import belief, cost_with_current_backlog, factorial_end_to_end, m0_cost, predict
from experiments.lessons.l1_6_reference import history_reference
from experiments.lessons.run_l1_2 import load_module, write_csv
from experiments.lessons.run_l1_3 import write_json

ROOT = Path(__file__).resolve().parents[2]
CORE = "tests/test_l1_6_belief.py"
EXTRA = "tests/test_l1_6_reference.py"
CELLS = ("00","10","01","11")
CANONICAL_TESTS = {"test_belief_canonical_one_observation", "test_m0_golden_canonical",
                   "test_predict_averages_predictions_not_states", "test_end_to_end_canonical_matches_L14",
                   "test_tau0_cell_splits_G_S"}
MUTANTS = {
    "Q1": ("Bỏ chuẩn hoá belief", """
source = inspect.getsource(lesson.belief)
old = 'return {state: p/evidence for state, p in masses.items()}'
assert source.count(old) == 1
exec(source.replace(old, 'return masses'), lesson.__dict__)
"""),
    "Q2": ("Bỏ likelihood, giữ cả chuỗi không khớp observation", """
source = inspect.getsource(lesson.belief)
old = 'if next_time in observations and observations[next_time] != (qA, qB):'
assert source.count(old) == 1
exec(source.replace(old, 'if False:'), lesson.__dict__)
"""),
    "Q3": ("M0 dùng stationary mean từ slot1 thay conditional mean", """
def bad_m0(x, action, th):
    pi = (1-th['p_offoff'])/(2-th['p_onon']-th['p_offoff'])
    mean = pi*th['rate_on']+(1-pi)*th['rate_off']
    bB = [th['rate_on'] if x[2] == 'on' else th['rate_off']] + [mean]*(th['H']-1)
    return lesson.two_queue_cost(x[:2], [th['bA']]*th['H'], bB, th['u'],th['cA'],th['cB'],action)[0]
lesson.m0_cost = bad_m0
"""),
    "Q4": ("M1 dùng uniform belief khác belief của M0", """
original = lesson.predict
def bad_predict(b, action, model, th):
    if model == 'M1':
        b = {x: F(1,len(b)) for x in b}
    return original(b, action, model, th)
lesson.predict = bad_predict
"""),
    "Q5": ("S0 ép prior=1/2", """
original = lesson.belief
lesson.belief = lambda history, th, prior_on: original(history,th,F(1,2))
"""),
    "Q6": ("M0 bỏ qua rate_off khác0", """
original = lesson.m0_cost
lesson.m0_cost = lambda x, action, th: original(x,action,dict(th,rate_off=0))
"""),
}


def C(table):
    return contrasts(*(table[c] for c in CELLS))


def run_tests(out, name, targets, mutation=None):
    junit = out/f"{name}.xml"
    args = ["-q","--color=no",f"--junitxml={junit}",*targets]
    if mutation:
        patch = out/f"{mutation}_patch.py"
        patch.write_text("# Doan Van Tai — isolated mutation, no repository copy.\n"
                         "import sys\nimport inspect\nfrom fractions import Fraction as F\nimport pytest\n"
                         f"sys.path.insert(0,{str(ROOT)!r})\n"
                         "from experiments.lessons import l1_6_belief as lesson\n"
                         +MUTANTS[mutation][1]+"\nraise SystemExit(pytest.main(sys.argv[1:]))\n",encoding="utf-8")
        command = [sys.executable,str(patch),*args]
    else:
        command = [sys.executable,"-m","pytest",*args]
    started = time.perf_counter()
    proc = subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    (out/f"{name}.txt").write_text(proc.stdout+proc.stderr,encoding="utf-8")
    if not junit.is_file():
        raise RuntimeError(f"Missing JUnit: {name}.txt")
    cases = list(ET.parse(junit).iter("testcase"))
    failures = [c.attrib["name"] for c in cases if c.find("failure") is not None]
    errors = [c.attrib["name"] for c in cases if c.find("error") is not None]
    skipped = [c.attrib["name"] for c in cases if c.find("skipped") is not None]
    return dict(command=command,total=len(cases),passed=len(cases)-len(failures)-len(errors)-len(skipped),
                failed=len(failures),failed_tests=failures,
                failed_test_functions=sorted({n.split("[")[0] for n in failures}),errors=errors,skipped=skipped,
                returncode=proc.returncode,log=f"{name}.txt",junit=f"{name}.xml",
                wall_seconds=time.perf_counter()-started,
                canonical_failed_tests=[n for n in failures if n in CANONICAL_TESTS])


def mean_background(x,th):
    paths = list(futures(x,th))
    return [sum(p*b[k] for b,p in paths) for k in range(th["H"])]


def jensen_row(x,action,th):
    bB = mean_background(x,th)
    mean_cost, mean_idle = two_queue_cost(x[:2],[th["bA"]]*th["H"],bB,th["u"],th["cA"],th["cB"],action)
    exact_idle = [F(0)]*th["H"]
    for background,p in futures(x,th):
        _,idle = two_queue_cost(x[:2],[th["bA"]]*th["H"],background,th["u"],th["cA"],th["cB"],action)
        for k,value in enumerate(idle):
            exact_idle[k] += p*value
    j = expected_cost(x,action,th)
    m0 = m0_cost(x,action,th)
    weighted = sum((th["H"]-k)*(exact_idle[k]-mean_idle[k]) for k in range(th["H"]))
    assert m0 == mean_cost and j-m0 == weighted and m0 <= j
    return dict(qA=x[0],qB=x[1],mode=x[2],action=action,M0=m0,M1=j,jensen_gap=j-m0,
                weighted_idle_difference=weighted,
                **{f"mean_background_{k}":v for k,v in enumerate(bB)},
                **{f"expected_idle_{k}":v for k,v in enumerate(exact_idle)},
                **{f"mean_path_idle_{k}":v for k,v in enumerate(mean_idle)})


def measure_canonical(out,golden):
    history,prior = [(-1,(2,0))],F(1,2)
    D,evidence,_ = history_reference(history,CANON,prior)
    assert D == generate_episodes((2,0),1,CANON,prior) == golden.CANONICAL_BELIEF
    L,rows,b = factorial_end_to_end(history,CANON,prior,D)
    assert b == D and L == golden.FACTORIAL_MEANS and C(L) == golden.FACTORIAL_CONTRASTS
    predictions = {model:{a:predict(b,a,model,CANON) for a in ("Stay","Switch")} for model in ("M0","M1")}
    state_rows,cell_rows,jensen = [],[],[]
    for name,x in (("x_a",golden.X_A),("x_b",golden.X_B),("x_c",golden.X_C),("x_d",golden.X_D)):
        js = {a:expected_cost(x,a,CANON) for a in ("Stay","Switch")}
        ms = {a:m0_cost(x,a,CANON) for a in ("Stay","Switch")}
        assert tuple(ms.values()) == golden.M0_COSTS[x]
        delta = js["Switch"]-js["Stay"]
        assert abs((ms["Switch"]-ms["Stay"])-delta) < abs(delta)
        gaps = {"00":predictions["M0"]["Switch"]-predictions["M0"]["Stay"],
                "10":ms["Switch"]-ms["Stay"],
                "01":predictions["M1"]["Switch"]-predictions["M1"]["Stay"],"11":delta}
        I = i_delta(*(gaps[c] for c in CELLS))
        assert rows[x] == golden.FACTORIAL_ROWS[x] and I == golden.CANONICAL_I_DELTA[x]
        state_rows.append(dict(state=name,probability=D[x],qA=x[0],qB=x[1],mode=x[2],
                               M0_stay=ms["Stay"],M0_switch=ms["Switch"],M1_stay=js["Stay"],M1_switch=js["Switch"],
                               delta=delta,model_gap_error=gaps["10"]-delta,I_delta=I,**C(rows[x])))
        for c in CELLS:
            regret = rows[x][c]-min(js.values())
            assert regret == regret_identity(delta,gaps[c])
            cell_rows.append(dict(state=name,probability=D[x],cell=c,delta_hat=gaps[c],action=choose(gaps[c]),
                                  true_cost=rows[x][c],regret=regret))
        for a in ("Stay","Switch"):
            jensen.append(dict(state=name,**jensen_row(x,a,CANON)))
    l_star = sum(D[x]*min(expected_cost(x,a,CANON) for a in ("Stay","Switch")) for x in D)
    current = {m:cost_with_current_backlog(D,CANON,m) for m in ("M0","M1")}
    assert current == {"M0":F(7),"M1":F(7)}
    freshness,mode_value = L["00"]-current["M0"],current["M0"]-L["10"]
    assert (freshness,mode_value) == (F(3,8),F(3,4))
    write_csv(out/"canonical_states.csv",state_rows)
    write_csv(out/"canonical_cells.csv",cell_rows)
    write_csv(out/"canonical_jensen.csv",jensen)
    write_csv(out/"canonical_means.csv",[dict(cell=c,cost=L[c],regret=L[c]-l_star) for c in CELLS])
    return dict(states=state_rows,cells=cell_rows,means=L,regrets={c:L[c]-l_star for c in CELLS},
                contrasts=C(L),belief=[dict(state=x,probability=p) for x,p in b.items()],evidence=evidence,
                predictions=predictions,oracle_cost=l_star,EVPPI=L["01"]-l_star,
                current_backlog_costs=current,freshness_gain=freshness,mode_visibility_gain=mode_value)


def grid():
    for ron,(p,s),yA,yB,u in product((3,4,5,6),((F(1,2),F(1,2)),(F(3,4),F(3,4)),(F(3,4),F(1,2))),
                                     (0,2,4),(0,1,2,3),(1,2)):
        yield dict(CANON,rate_on=ron,p_onon=p,p_offoff=s,u=u),(yA,yB)


def measure_grids(out):
    matched,wrong,actions = [],[],[]
    f5_pairs,zero_margin = 0,0
    for prior in (F(1,4),F(1,2),F(3,4)):
        for index,(th,y) in enumerate(grid()):
            history = [(-1,y)]
            D = generate_episodes(y,1,th,prior)
            reference,_,_ = history_reference(history,th,prior)
            L,rows,b = factorial_end_to_end(history,th,prior,D)
            assert b == D == reference
            truth = {a:sum(p*expected_cost(x,a,th) for x,p in D.items()) for a in ("Stay","Switch")}
            assert L["01"] == min(truth.values()) and C(L)["G_M"] >= 0
            d00 = predict(b,"Switch","M0",th)-predict(b,"Stay","M0",th)
            d01 = predict(b,"Switch","M1",th)-predict(b,"Stay","M1",th)
            mean_I = F(0)
            for x,p in D.items():
                delta = expected_cost(x,"Switch",th)-expected_cost(x,"Stay",th)
                d10 = m0_cost(x,"Switch",th)-m0_cost(x,"Stay",th)
                mean_I += p*i_delta(d00,d10,d01,delta)
                cs = C(rows[x])
                assert cs["Gamma"] == cs["G_S|M1"]-cs["G_S"] == cs["G_M|S1"]-cs["G_M"]
                if delta:
                    assert cs["Gamma"]/abs(delta) in {-1,0,1,2}
                else:
                    assert all(v == 0 for v in cs.values())
                    zero_margin += 1
                assert all(cs[k] >= 0 for k in ("G_SM","G_S|M1","G_M|S1"))
                for c,dh in zip(CELLS,(d00,d10,d01,delta)):
                    assert rows[x][c]-min(expected_cost(x,a,th) for a in ("Stay","Switch")) == regret_identity(delta,dh)
                    f5_pairs += 1
                for a in ("Stay","Switch"):
                    actions.append(dict(grid_id=index,prior_D=prior,rate_on=th["rate_on"],p=th["p_onon"],s=th["p_offoff"],
                                        yA=y[0],yB=y[1],u=th["u"],state_probability=p,**jensen_row(x,a,th)))
            assert mean_I == 0
            base = dict(grid_id=index,prior_D=prior,rate_on=th["rate_on"],p=th["p_onon"],s=th["p_offoff"],yA=y[0],yB=y[1],u=th["u"])
            matched.append(dict(**base,**{f"L{c}":L[c] for c in CELLS},**C(L),mean_I_delta=mean_I,
                                posterior_matches_D=b == D,bayes_cost=min(truth.values())))
            if prior != F(1,2):
                bad,_,bad_b = factorial_end_to_end(history,th,F(1,2),D)
                wrong.append(dict(**base,prior_S0=F(1,2),**{f"L{c}":bad[c] for c in CELLS},**C(bad),
                                  matched_G_M=C(L)["G_M"],belief_matches_D=bad_b == D))
    write_csv(out/"matched_prior_grid.csv",matched)
    write_csv(out/"wrong_prior_grid.csv",wrong)
    write_csv(out/"jensen_grid.csv",actions)
    negatives = [r for r in wrong if r["G_M"] < 0]
    write_csv(out/"wrong_prior_negative_cases.csv",negatives)
    assert len(matched) == 864 and len(wrong) == 576 and len(negatives) == 5
    example = next(r for r in wrong if r["rate_on"] == 4 and r["p"] == r["s"] == F(1,2)
                   and (r["yA"],r["yB"],r["u"],r["prior_D"]) == (4,3,1,F(3,4)))
    assert example["G_M"] == F(-3,16)
    return dict(matched_cases=len(matched),wrong_prior_cases=len(wrong),matched_negative_G_M=0,
                wrong_prior_negative_G_M=len(negatives),jensen_state_action_cases=len(actions),
                jensen_violations=0,posterior_mismatches=0,mean_I_violations=0,
                F5_pairs_checked=f5_pairs,zero_margin_state_cases=zero_margin,wrong_prior_example=example)


def measure_histories_variants(out,golden):
    p34 = dict(CANON,p_onon=F(3,4),p_offoff=F(3,4))
    p55 = dict(CANON,p_onon=F(11,20),p_offoff=F(11,20))
    off = dict(CANON,rate_on=4,rate_off=1,p_onon=F(3,4),p_offoff=F(1,2),H=3)
    cases = [("canonical",CANON,[(-1,(2,0))],F(1,2)),
             ("p55",p55,[(-1,(2,0))],F(1,2)),("p75_controlled",p34,[(-1,(2,0))],F(1,2)),
             ("p75_empty_conditioned_prior",p34,[(-1,(2,0))],F(1,4)),
             ("two_observations_up",p34,[(-2,(2,0)),(-1,(2,2))],F(1,2))]
    variants,posterior_rows,path_rows = [],[],[]
    extra = [("older_tau2",CANON,[(-2,(2,0))],F(1,2)),
             ("two_up_prior_quarter",p34,[(-2,(2,0)),(-1,(2,2))],F(1,4)),
             ("two_empty",p34,[(-2,(2,0)),(-1,(2,0))],F(1,2)),
             ("tau3_nonzero_off",off,[(-3,(2,0)),(-2,(2,1)),(-1,(2,0))],F(1,4))]
    for name,th,hist,prior in cases+extra:
        D,evidence,paths = history_reference(hist,th,prior)
        b = belief(hist,th,prior)
        assert D == b and sum(b.values()) == 1
        for x,p in b.items():
            posterior_rows.append(dict(scenario=name,prior=prior,evidence=evidence,qA=x[0],qB=x[1],mode=x[2],probability=p))
        path_rows.extend(dict(scenario=name,**r) for r in paths)
        if name in {c[0] for c in cases}:
            L,_,_ = factorial_end_to_end(hist,th,prior,D)
            fresh = cost_with_current_backlog(D,th,"M0")
            fresh_m1 = cost_with_current_backlog(D,th,"M1")
            assert fresh_m1 <= fresh
            variants.append(dict(scenario=name,p=th["p_onon"],s=th["p_offoff"],persistence=th["p_onon"]+th["p_offoff"]-1,
                                 prior=prior,evidence=evidence,**{f"L{c}":L[c] for c in CELLS},**C(L),
                                 current_backlog_cost_M0=fresh,current_backlog_cost_M1=fresh_m1,
                                 freshness_gain=L["00"]-fresh,mode_visibility_gain=fresh-L["10"]))
    expected = [(F(9,8),F(1,4)),(F(979,800),F(13,40)),(F(31,32),F(0)),(F(45,64),F(0)),(F(21,32),F(0))]
    assert [(r["G_S"],r["G_M"]) for r in variants] == expected
    for history in ([(-2,(2,0)),(-1,(2,1))],):
        D,evidence,paths = history_reference(history,p34,F(1,2))
        assert not D and evidence == 0
        try:
            belief(history,p34,F(1,2))
        except ValueError:
            pass
        else:
            raise AssertionError("impossible history must be rejected")
        path_rows.extend(dict(scenario="impossible_history",**r) for r in paths)
    write_csv(out/"posterior_states.csv",posterior_rows)
    write_csv(out/"history_paths.csv",path_rows)
    write_csv(out/"persistence_variants.csv",variants)
    b1 = []
    D = golden.CANONICAL_BELIEF
    for x in D:
        actions = {m:choose(predict({x:F(1)},"Switch",m,CANON)-predict({x:F(1)},"Stay",m,CANON)) for m in ("M0","M1")}
        costs = {m:sum(p*expected_cost(state,actions[m],CANON) for state,p in D.items()) for m in ("M0","M1")}
        b1.append(dict(selected_qA=x[0],selected_qB=x[1],selected_mode=x[2],tie_rule="choose this tied joint-MAP state",
                       action_M0=actions["M0"],action_M1=actions["M1"],G_S=costs["M0"]-F(25,4),G_M=costs["M0"]-costs["M1"]))
    assert all(r["G_M"] == 0 for r in b1)
    write_csv(out/"B1_sensitivity.csv",b1)
    shortcut = tuple(two_queue_cost((F(2),F(1)),[1,1],[F(5,2)]*2,2,3,3,a)[0] for a in ("Stay","Switch"))
    assert shortcut == (F(9,2),F(13,2))
    toys = []
    for q0,horizon in ((0,2),(20,3)):
        path_costs = []
        mean_backlogs,_ = rollout(q0,[F(3)]*horizon,3)
        for arrivals in product((2,4),repeat=horizon):
            backlogs,idle = rollout(q0,arrivals,3)
            path_costs.append(sum(backlogs))
            toys.append(dict(example=f"one_queue_q{q0}_H{horizon}",arrivals=str(arrivals),probability=F(1,2**horizon),
                             backlog_path=str(backlogs),cost=sum(backlogs),idle_total=sum(idle),mean_path_cost=sum(mean_backlogs)))
        assert sum(path_costs)/F(len(path_costs)) == (F(5,4) if q0 == 0 else F(60))
        assert sum(mean_backlogs) == (F(0) if q0 == 0 else F(60))
    write_csv(out/"jensen_toy_paths.csv",toys)
    true = {a:sum(F(1,4)*two_queue_cost((0,0),[1,1],list(b),2,3,3,a)[0]
                  for b in product((0,2),repeat=2)) for a in ("Stay","Switch")}
    assert true == {"Stay":0,"Switch":F(5,4)}
    return dict(variants=variants,B1=b1,mean_state_shortcut=shortcut,
                negative_gap_error_iid_example=dict(true_costs=true,mean_path_costs=[0,0],e_M=F(-5,4)),
                impossible_history_rejected=True,reference_posterior_cases=len(cases+extra),
                source_note="separate iid illustrations; not a change to canonical known-slot0 Markov model")


def plot_results(out,canonical,extras):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(1,3,figsize=(14,4.2),layout="constrained")
    for offset,field,label in ((-0.18,"M0_stay","M0 Stay"),(0.18,"M1_stay","M1 Stay")):
        bars = axes[0].bar([i+offset for i in range(4)],[float(r[field]) for r in canonical["states"]],width=.36,label=label)
        axes[0].bar_label(bars,fmt="%g",padding=3)
    axes[0].set(xticks=range(4),xticklabels=[r["state"] for r in canonical["states"]],title="Conditional rollout vs exact cost",ylabel="packet-slot")
    axes[0].legend()
    axes[1].bar(("Fresh backlog","See mode"),(float(canonical["freshness_gain"]),float(canonical["mode_visibility_gain"])))
    axes[1].set(title="Ordered GS split: old -> fresh -> state",ylabel="packet-slot",ylim=(0,.9))
    for i,value in enumerate((canonical["freshness_gain"],canonical["mode_visibility_gain"])):
        axes[1].text(i,float(value)+.025,f"{float(value):g}",ha="center")
    rows = extras["variants"][:3]
    axes[2].bar([str(float(r["persistence"])) for r in rows],[float(r["G_M"]) for r in rows])
    axes[2].set(title="Three toy persistence settings",xlabel="lambda (controlled initialization)",ylabel="G_M (packet-slot)",ylim=(0,.4))
    for ax in axes:
        ax.grid(axis="y",alpha=.25)
        ax.set_axisbelow(True)
    fig.savefig(out/"belief_pipeline.png",dpi=160)
    plt.close(fig)


def render_report(result):
    canonical,grid_result = result["canonical"],result["grid"]
    lines = ["# L1.6 A–D — belief, M0 và 2×2 end-to-end", "",
             f"Tác giả: **Doan Van Tai** · Ngày: **22/10/2026** · Lần chạy: {result['run_time_asia_saigon']}.", "",
             "Đã triển khai B2 với likelihood 0/1, M0 có conditional means, shared-belief predict, factorial end-to-end "
             "và ô backlog hiện tại. Plant, exact J, choose, contrasts và F5 được dùng lại từ L1.2–L1.5.", "",
             "## Cấu hình và dự đoán", "",
             "H=2,dt=1,c=3,u=2,b_A=1,B on/off=5/0,p=s=1/2,c_sw=0. History=[(-1,(2,0))],prior_D=prior_S0=1/2. "
             "Đo backlog đầu slot không nhiễu, không thấy mode. Trước t0 dùng Stay; S0 posterior b=1/4 mỗi state, "
             "đã so trực tiếp với evaluator/golden. Không cấp D hoặc state thật cho hai quyết định S0. Đơn vị cost/gain/regret: **packet·slot**.", "",
             "| State | M0 Stay | M1 Stay | M0 Switch | M1 Switch | e_M | I_Δ |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in canonical["states"]:
        lines.append("| "+row["state"]+" | "+" | ".join(f"{float(row[k]):g}" for k in ("M0_stay","M1_stay","M0_switch","M1_switch","model_gap_error","I_delta"))+" |")
    lines += ["", "S0M0 predicts Stay=6,75,Switch=7 → gap=+0,25 → Stay. "
              "S0M1 predicts Stay=7,375,Switch=7,125 → gap=−0,25 → Switch. "
              "S1M0 và S1M1 chọn theo state và cùng đạt oracle ở ví dụ chuẩn. Dự đoán giờ được tính từ history/model, không nhập gap cho sẵn.", "",
              "| Ô | L | R |", "|---|---:|---:|"]
    for cell in CELLS:
        lines.append(f"| {cell} | {float(canonical['means'][cell]):g} | {float(canonical['regrets'][cell]):g} |")
    lines += ["", "| G_S | G_M | G_SM | Γ | G_S given M1 | G_M given S1 |", "|---:|---:|---:|---:|---:|---:|",
              "| "+" | ".join(f"{float(v):g}" for v in canonical["contrasts"].values())+" |", "",
              "Tái lập đúng L1.4–L1.5. G_S given M1=7/8 có dạng EVPPI về state hiện tại dưới posterior đúng; "
              "không phải biết trước future và không là contribution mới. Chưa đọc/đối chiếu P11 gốc; note ghi câu hỏi cho Phase2a.", "",
              "## Jensen, posterior và lưới", "",
              f"- **{grid_result['matched_cases']}** cấu hình matched prior: b=D/reference, cell01=Bayes, G_M≥0, mean I theo history=0; 0 vi phạm.",
              f"- **{grid_result['jensen_state_action_cases']}** cặp state/action: M0≤M1 và Jensen gap bằng chênh lệch idle có trọng số; 0 vi phạm.",
              f"- F5 và (a),(b),(e) kiểm trên dự đoán thực: **{grid_result['F5_pairs_checked']}** cặp episode/cell; "
              f"{grid_result['zero_margin_state_cases']} trường hợp state margin=0 được xử lý riêng, không chia margin0.",
              f"- **{grid_result['wrong_prior_cases']}** trường hợp S0 prior1/2 sai: đúng **{grid_result['wrong_prior_negative_G_M']}** ô G_M<0. "
              "Lưu cả toàn bộ lưới, không chỉ các ô âm. Ví dụ rate_on4,u1,y=(4,3),p=s=1/2,prior_D3/4 cho G_M=−3/16.",
              "- Reference evaluator dùng Cartesian mode product và direct transition products, không gọi S0 hoặc mode_paths; "
              "vẫn dùng chung plant đã kiểm. Các history có loại trừ, prior thay đổi, τ3/nonzero-off có posterior/evidence/path records riêng.",
              "- Với hai observation (2,0)→(2,2),p=s=3/4: evidence=1/2 ở prior1/2 và1/4 ở prior1/4, "
              "cùng posterior 9/16,3/16,3/16,1/16. Joint P(qB4,on)=9/16 khác tích marginals15/32. "
              "History (2,0)→(2,1) có evidence0 và bị từ chối đúng dự kiến.", "",
              "M0≤M1 cần infinite buffer, mean đúng và cost backlog tuyến tính. Sai số gap có thể âm: "
              "iid toy q=(0,0),B={0,2} cho e_M=−5/4. Đây là toy khác, không đổi ngữ nghĩa known-slot0 của ví dụ chuẩn. "
              "EV-20 q0=20,H3 cho true/mean cost60; q0=0,H2,arrivals2/4 cho true cost5/4,mean cost0.", "",
              "## Freshness, B1 và variants", "",
              "Ô backlog hiện tại giấu mode có cost **7** ở cả M0/M1. Theo thứ tự tau1→tau0→S1: "
              "**freshness=3/8=0,375**, **mode visibility=3/4=0,75**, tổng9/8. Hai phần ba GS đến từ thấy mode; "
              "không gán phần này cho refresh backlog thực tế. Ô tau0 là diagnostic condition D, chưa tính delay/cost telemetry.", "",
              "| Scenario | G_S | G_M | Gamma |", "|---|---:|---:|---:|"]
    for row in result["extras"]["variants"]:
        lines.append(f"| {row['scenario']} | {row['G_S']} | {row['G_M']} | {row['Gamma']} |")
    lines += ["", "GS không được suy đơn điệu từ các hàng conditional có D/history khác nhau. "
              "Prior1/4 chỉ mô tả biến thể điều kiện B rỗng trong luật cụ thể; chưa chạy warm-up/stationary simulation.",
              "B1 sensitivity thử đủ bốn lựa chọn joint-MAP tied: mode on cho GS9/8,mode off7/8,GM0; "
              "ghi rõ lựa chọn, không đổi baseline B2. State-mean shortcut cho Stay4,5/Switch6,5, khác B2 M0 6,75/7; "
              "shortcut chỉ minh hoạ lỗi, không dùng trong pipeline.", "",
              "![M0, freshness và persistence](belief_pipeline.png)", "",
              "## Kiểm thử và mutation", ""]
    for label,key in (("L1.6 theo tài liệu","lesson"),("Năm lesson theo tài liệu","lessons"),("Reference/schema bổ sung","reference"),("Toàn repo","full_suite")):
        t = result["tests"][key]
        lines.append(f"- {label}: **{t['passed']}/{t['total']} PASS**.")
    lines += ["", "59=43+16 là số test trong tài liệu. Repo có 18 test ngoài bộ lesson trước đó và 3 kiểm mới nên tổng 80. "
              "Preflight19 đã chạy khi ghi experiment card; đây là verification theo kỳ vọng tài liệu, không là preregistration held-out.", "",
              "| Mutant | Bug cụ thể | Test đỏ /16 | Test function đỏ | Trong 5 test chuẩn |", "|---|---|---:|---:|---:|"]
    for name,m in result["mutations"].items():
        lines.append(f"| {name} | {m['description']} | {m['failed']} | {len(m['failed_test_functions'])} | {len(m['canonical_failed_tests'])} |")
    for name,m in result["mutations"].items():
        lines += ["", f"**{name}** bắt bởi: "+", ".join(f"`{t}`" for t in m["failed_tests"])+"."]
    lines += ["", "Số test đỏ là kết quả của các mutant được lưu cụ thể; tham số pytest được tính thành các test riêng. "
              "Theo test function, số đỏ là 2/3/3/2/1, khớp bảng tài liệu; theo pytest collected cases là 2/3/3/4/2 "
              "vì parametrization prior. Cả năm mutant đều qua các test ví dụ chuẩn; "
              "chúng lộ ở histories/priors/persistence hoặc tính chất trên lưới.",
              f"Q6 bổ sung (M0 bỏ rate_off) lọt {result['sixth_mutation']['core']['passed']}/16 test gốc, "
              f"bị {result['sixth_mutation']['extra']['failed']}/3 test bổ sung bắt. Các FAIL mutant là có chủ đích; "
              "không sửa source baseline hoặc sao chép repository.", "",
              "## File, giới hạn và tái chạy", "",
              "Source: `experiments/lessons/l1_6_belief.py`; reference `l1_6_reference.py`; runner `run_l1_6.py`; "
              "tests `tests/test_l1_6_belief.py`, `tests/test_l1_6_reference.py`; golden `tests/golden_phase1.py`. "
              "Card/spec tại `notes/lessons/L1.6_experiment_card.md` và `L1.6_belief_model_spec.md`.", "",
              "```bash", ".venv/bin/python -m experiments.lessons.run_l1_6",
              ".venv/bin/python -m experiments.lessons.run_l1_6 --output-dir /tmp/l1_6-rerun", "```", "",
              "| Artifact | Nội dung |", "|---|---|",
              "| [config.json](config.json), [results.json](results.json) | Configuration, exact metrics, commands, hashes, scope |",
              "| [canonical_states.csv](canonical_states.csv), [canonical_cells.csv](canonical_cells.csv), [canonical_means.csv](canonical_means.csv) | M0/M1/gaps/I/contrasts và 16 quyết định được sinh end-to-end |",
              "| [canonical_jensen.csv](canonical_jensen.csv), [jensen_grid.csv](jensen_grid.csv) | Jensen gap và idle identity cho state/action |",
              "| [matched_prior_grid.csv](matched_prior_grid.csv), [wrong_prior_grid.csv](wrong_prior_grid.csv), [wrong_prior_negative_cases.csv](wrong_prior_negative_cases.csv) | Toàn bộ 864 matched,576 wrong,5 negative cases |",
              "| [posterior_states.csv](posterior_states.csv), [history_paths.csv](history_paths.csv) | Evidence, normalized posterior và path filtering |",
              "| [persistence_variants.csv](persistence_variants.csv), [B1_sensitivity.csv](B1_sensitivity.csv), [jensen_toy_paths.csv](jensen_toy_paths.csv) | Sensitivities và toy Jensen |",
              "| lesson.txt,lessons.txt,reference.txt,full_suite.txt và *.xml | Baseline stdout/stderr và JUnit |",
              "| Q1.txt…Q5.txt, Q6_core.txt,Q6_extra.txt,*.xml,Q*_patch.py | Mutants cụ thể, log và test bị bắt |",
              "| [belief_pipeline.png](belief_pipeline.png) | Biểu đồ từ số liệu |", "",
              "Exact int/Fraction, không RNG/seed/Monte Carlo hoặc CI lấy mẫu. Đây là finite verification E0/E1 "
              "và toy discovery, chưa là evidence mạng, practical gain hoặc novelty. Không fit H0/H1, chưa chấm held-out, "
              "chưa đọc P11 gốc. Đã có artifact kỹ thuật cho DL-010(i),(ii); chưa thay bài giấy/understanding của tác giả. "
              "Chưa khóa schema/prior/D/B1/M_K tại L1.8, chưa kiểm timescale vật lý hoặc H/τ lớn. "
              "Giữ G1,V3/V10/V11 và HOLD Phase 4.",
              f"Python {result['environment']['python']}, pytest {result['environment']['pytest']}; "
              f"runner wall time {result['elapsed_seconds']:.3f} s, không là benchmark mạng.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=ROOT/"results/lessons/l1_6")
    out = parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    started = time.perf_counter()
    timestamp = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat()
    config = dict(author="Doan Van Tai",canonical=CANON,history=[(-1,(2,0))],prior_D=F(1,2),prior_S0=F(1,2),
                  dt=1,c_sw=0,tie_action="Stay",cell_order=CELLS,rate_on_grid=[3,4,5,6],
                  transition_grid=[(F(1,2),F(1,2)),(F(3,4),F(3,4)),(F(3,4),F(1,2))],
                  observed_qA=[0,2,4],observed_qB=[0,1,2,3],managed_u=[1,2],priors=[F(1,4),F(1,2),F(3,4)],
                  seed=None,method="exact finite enumeration; B2 vs evaluator reference",warmup_simulated=False,
                  physical_timescale_locked=False,H0_fitted=False,held_out_evaluated=False)
    write_json(out/"config.json",config)
    tests = {}
    for name,targets in (("lesson",[CORE]),("lessons",["tests/test_l1_2_queue.py","tests/test_l1_3_expected_cost.py",
                                    "tests/test_l1_4_factorial.py","tests/test_l1_5_identity.py",CORE]),
                         ("reference",[EXTRA]),("full_suite",["tests/"])):
        measured = run_tests(out,name,targets)
        tests[name] = measured
        if measured["returncode"] or measured["errors"] or measured["skipped"]:
            write_json(out/"failed_run.json",dict(stage=name,result=measured))
            raise RuntimeError(f"Baseline failed: {out/measured['log']}")
        print(f"{name}: {measured['passed']}/{measured['total']} PASS",flush=True)
    assert tests["lesson"]["total"] == 16 and tests["lessons"]["total"] == 59
    golden = load_module("golden_phase1",ROOT/"tests/golden_phase1.py")
    canonical = measure_canonical(out,golden)
    grids = measure_grids(out)
    extras = measure_histories_variants(out,golden)
    print(f"Grid: {grids['matched_cases']} matched; {grids['wrong_prior_cases']} wrong prior; "
          f"{grids['wrong_prior_negative_G_M']} negative G_M; {grids['jensen_state_action_cases']} Jensen cases",flush=True)
    mutations = {}
    for name in ("Q1","Q2","Q3","Q4","Q5"):
        measured = run_tests(out,name,[CORE],name)
        assert measured["returncode"] == 1 and measured["failed"] > 0 and measured["total"] == 16
        assert not measured["errors"] and not measured["skipped"] and not measured["canonical_failed_tests"]
        mutations[name] = dict(description=MUTANTS[name][0],**measured)
        print(f"{name}: {measured['failed']}/16 tests detected bug; canonical detectors=0",flush=True)
    sixth = dict(core=run_tests(out,"Q6_core",[CORE],"Q6"),extra=run_tests(out,"Q6_extra",[EXTRA],"Q6"))
    assert sixth["core"]["returncode"] == 0 and sixth["core"]["passed"] == 16
    assert sixth["extra"]["returncode"] == 1 and sixth["extra"]["failed"] > 0 and not sixth["extra"]["errors"]
    plot_results(out,canonical,extras)
    sources = ["experiments/lessons/l1_2_queue.py","experiments/lessons/l1_3_expected_cost.py","experiments/lessons/l1_4_factorial.py",
               "experiments/lessons/l1_5_identity.py","experiments/lessons/l1_6_belief.py","experiments/lessons/l1_6_reference.py",
               "experiments/lessons/run_l1_2.py","experiments/lessons/run_l1_3.py","experiments/lessons/run_l1_6.py",
               CORE,EXTRA,"tests/golden_phase1.py","pyproject.toml","notes/lessons/L1.6_experiment_card.md","notes/lessons/L1.6_belief_model_spec.md"]
    documents = ["0499111e-93b0-44da-b638-87a412a8788c","62169f1f-a0cd-44da-8d3f-54f256490abd",
                 "b05f9e20-d2b5-478f-be32-d13449c4ff19","b9b58eca-8105-43bd-a9e7-02b57e32c43b"]
    document_hashes = []
    for part,identifier in zip("ABCD",documents):
        path = Path("/home/vantai/.codex/attachments")/identifier/"Pasted text.txt"
        if path.is_file():
            document_hashes.append(dict(part=part,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    import pytest
    commit = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
    result = dict(author="Doan Van Tai",run_time_asia_saigon=timestamp,configuration=config,
                  environment=dict(python=platform.python_version(),pytest=pytest.__version__),base_commit=commit,
                  source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},supplied_documents=document_hashes,
                  golden_provenance=golden.L1_6_PROVENANCE,tests=tests,canonical=canonical,grid=grids,extras=extras,
                  mutations=mutations,sixth_mutation=sixth,elapsed_seconds=time.perf_counter()-started,
                  scope="finite toy E0/E1; posterior verified only under declared initialization/history; no physical timescale, network or novelty validation")
    write_json(out/"results.json",result)
    (out/"report.md").write_text(render_report(result),encoding="utf-8")
    print("Canonical predicted costs:",canonical["predictions"])
    print("Canonical contrasts:",canonical["contrasts"])
    print("Freshness / mode visibility:",canonical["freshness_gain"],canonical["mode_visibility_gain"])
    print(f"Report: {out/'report.md'}")


if __name__ == "__main__":
    main()
