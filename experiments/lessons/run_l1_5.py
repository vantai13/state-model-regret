"""Doan Van Tai — reproduce L1.5 F5, I_delta, checker independence and limits.

Run: .venv/bin/python -m experiments.lessons.run_l1_5
Only exact lesson verification; no H0 fitting or held-out evaluation is performed.
"""
import argparse
import hashlib
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

from experiments.lessons import l1_5_identity as identity
from experiments.lessons.l1_3_expected_cost import CANON, expected_cost
from experiments.lessons.l1_4_factorial import additive_cells, cell_costs, choose, contrasts
from experiments.lessons.run_l1_2 import load_module, write_csv
from experiments.lessons.run_l1_3 import write_json

ROOT = Path(__file__).resolve().parents[2]
CORE = "tests/test_l1_5_identity.py"
EXTRA = "tests/test_l1_5_diagnostic_limits.py"
CELLS = ("00", "10", "01", "11")
MUTANTS = {
    "P1": ("F5 bỏ số hạng hoà", """
identity.regret_identity = lambda delta, predicted: abs(delta) if delta*predicted < 0 else 0
"""),
    "P2": ("F5 dùng <=, đếm hoà như sai dấu", """
def bad_f5(delta, predicted):
    wrong = abs(delta) if delta*predicted <= 0 else 0
    return wrong + (max(0, -delta) if predicted == 0 else 0)
identity.regret_identity = bad_f5
"""),
    "P3": ("I_delta đổi dấu số hạng d10", """
identity.i_delta = lambda d00, d10, d01, d11: d11+d10-d01+d00
"""),
    "P4": ("belief_average bỏ trọng số", """
identity.belief_average = lambda belief, values: sum(values[x] for x in belief)/F(len(belief))
"""),
    "P5": ("Cell01 dùng M0 thay cho delta thật", """
def bad_per_state(belief, delta, m0):
    d01 = identity.belief_average(belief, m0)
    d00 = identity.belief_average(belief, m0)
    return {x: identity.i_delta(d00, m0[x], d01, delta[x]) for x in belief}
identity.i_delta_per_state = bad_per_state
"""),
}


def run_tests(out, name, targets, mutation=None):
    junit = out / f"{name}.xml"
    args = ["-q", "--color=no", f"--junitxml={junit}", *targets]
    if mutation:
        patch = out / f"{mutation}_patch.py"
        before_import = ""
        if mutation == "cross_choose":
            before_import = ("from experiments.lessons import l1_4_factorial\n"
                             "l1_4_factorial.choose = lambda gap: 'Switch' if gap <= 0 else 'Stay'\n")
            patch_code = ""
        else:
            patch_code = MUTANTS[mutation][1]
        patch.write_text("# Doan Van Tai — isolated mutant; normal source is unchanged.\n"
                         "import sys\nfrom fractions import Fraction as F\nimport pytest\n"
                         f"sys.path.insert(0, {str(ROOT)!r})\n"
                         f"sys.path.insert(0, {str(ROOT / 'tests')!r})\n"
                         + before_import + "from experiments.lessons import l1_5_identity as identity\n"
                         + patch_code + "\nraise SystemExit(pytest.main(sys.argv[1:]))\n", encoding="utf-8")
        command = [sys.executable, str(patch), *args]
    else:
        command = [sys.executable, "-m", "pytest", *args]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (out / f"{name}.txt").write_text(proc.stdout+proc.stderr, encoding="utf-8")
    if not junit.is_file():
        raise RuntimeError(f"Missing JUnit, see {out / (name+'.txt')}")
    cases = list(ET.parse(junit).iter("testcase"))
    failed = [c.attrib["name"] for c in cases if c.find("failure") is not None]
    errors = [c.attrib["name"] for c in cases if c.find("error") is not None]
    skipped = [c.attrib["name"] for c in cases if c.find("skipped") is not None]
    return dict(command=command, returncode=proc.returncode, total=len(cases),
                passed=len(cases)-len(failed)-len(errors)-len(skipped), failed=len(failed),
                failed_tests=failed, errors=errors, skipped=skipped,
                log=f"{name}.txt", junit=f"{name}.xml", wall_seconds=time.perf_counter()-started)


def make_coupled_checker(out):
    """Reconstruct only the shared-helper checker from the lesson's cautionary example."""
    source = (ROOT / CORE).read_text(encoding="utf-8")
    independent = "assert sum(wi * interaction[s] for wi, s in zip(weights, states)) == 0"
    assert source.count(independent) == 1
    reconstructed = source.replace(independent, "assert belief_average(b, interaction) == 0")
    path = out / "coupled_checker" / "test_l1_5_identity.py"
    path.parent.mkdir(exist_ok=True)
    path.write_text("# Doan Van Tai — deliberately weakened checker for mutation replay.\n"
                    f"import sys\nsys.path.insert(0, {str(ROOT / 'tests')!r})\n"+reconstructed,
                    encoding="utf-8")
    return str(path)


def measure_canonical(out, golden):
    states = (golden.X_A, golden.X_B, golden.X_C, golden.X_D)
    belief = golden.CANONICAL_BELIEF
    costs = {x: tuple(expected_cost(x, a, CANON) for a in ("Stay", "Switch")) for x in states}
    delta = {x: costs[x][1]-costs[x][0] for x in states}
    m0 = golden.DELTA_HAT_10
    d00, d01 = identity.belief_average(belief, m0), identity.belief_average(belief, delta)
    interaction = identity.i_delta_per_state(belief, delta, m0)
    assert (d00, d01) == (F(1, 4), F(-1, 4))
    assert interaction == golden.CANONICAL_I_DELTA
    mean_error = sum(belief[x]*(m0[x]-delta[x]) for x in states)
    state_rows, pair_rows = [], []
    for label, x in zip(("x_a", "x_b", "x_c", "x_d"), states):
        stay, switch = costs[x]
        gaps = {"00": d00, "10": m0[x], "01": d01, "11": delta[x]}
        true_costs = cell_costs(stay, switch, gaps)
        gamma = contrasts(*(true_costs[c] for c in CELLS))["Gamma"]
        assert true_costs == golden.FACTORIAL_ROWS[x]
        assert interaction[x] == mean_error-(m0[x]-delta[x])
        state_rows.append(dict(state=label, qA=x[0], qB=x[1], mode=x[2], probability=belief[x],
                               delta=delta[x], margin=abs(delta[x]), m0_gap=m0[x], model_gap_error=m0[x]-delta[x],
                               d00=d00, d10=m0[x], d01=d01, d11=delta[x], I_delta=interaction[x], gamma=gamma))
        for cell in CELLS:
            dh = gaps[cell]
            direct = identity.direct_regret(stay, switch, dh)
            f5 = identity.regret_identity(delta[x], dh)
            assert direct == f5 == golden.IDENTITY_REGRETS[x][cell]
            pair_rows.append(dict(state=label, probability=belief[x], cell=cell,
                                  j_stay=stay, j_switch=switch, delta=delta[x], margin=abs(delta[x]),
                                  delta_hat=dh, action=choose(dh),
                                  wrong_sign_loss=abs(delta[x]) if dh*delta[x] < 0 else 0,
                                  tie_loss=max(0, -delta[x]) if dh == 0 else 0,
                                  direct_regret=direct, f5_regret=f5, residual=direct-f5))
    summaries = []
    for cell in CELLS:
        rows = [r for r in pair_rows if r["cell"] == cell]
        consistency = sum(r["probability"] for r in rows
                          if r["action"] == ("Switch" if r["delta"] < 0 else "Stay"))
        regret = sum(r["probability"]*r["direct_regret"] for r in rows)
        summaries.append(dict(cell=cell, decision_consistency=consistency, expected_regret=regret))
    assert [r["expected_regret"] for r in summaries] == [F(9, 8), F(0), F(7, 8), F(0)]
    assert [r["decision_consistency"] for r in summaries] == [F(1, 2), F(1), F(1, 2), F(1)]
    mean = sum(belief[x]*interaction[x] for x in states)
    mean_abs = sum(belief[x]*abs(interaction[x]) for x in states)
    assert (mean, mean_abs) == (F(0), F(1, 4))
    distribution, cumulative = [], F(0)
    for value in sorted(set(interaction.values())):
        mass = sum(belief[x] for x in states if interaction[x] == value)
        cumulative += mass
        distribution.append(dict(I_delta=value, probability=mass, cumulative_probability=cumulative))
    write_csv(out / "canonical_states.csv", state_rows)
    write_csv(out / "canonical_regrets.csv", pair_rows)
    write_csv(out / "consistency_regret.csv", summaries)
    write_csv(out / "i_delta_distribution.csv", distribution)
    return dict(states=state_rows, pairs=pair_rows, cell_summaries=summaries,
                mean_i_delta=mean, mean_abs_i_delta=mean_abs, mean_model_gap_error=mean_error,
                i_delta_distribution=distribution), states, belief, delta, m0


def measure_f5(out):
    values = [F(k, 2) for k in range(-4, 5)]
    rows = []
    for delta, predicted in product(values, repeat=2):
        direct = identity.direct_regret(F(10), F(10)+delta, predicted)
        f5 = identity.regret_identity(delta, predicted)
        strict = abs(predicted-delta) < abs(delta)
        assert direct == f5 and (not strict or direct == 0)
        rows.append(dict(delta=delta, delta_hat=predicted, direct_regret=direct, f5_regret=f5,
                         residual=direct-f5, true_tie=delta == 0, predicted_tie=predicted == 0,
                         strict_error_below_margin=strict))
    write_csv(out / "f5_grid.csv", rows)
    bounds = []
    for delta, bound in product(values, (F(0), F(1, 2), F(1), F(2))):
        for e_stay, e_switch in product((-bound, F(0), bound), repeat=2):
            predicted = delta+e_switch-e_stay
            regret = identity.direct_regret(F(10), F(10)+delta, predicted)
            assert regret <= 2*bound
            bounds.append(dict(delta=delta, bound_b=bound, error_stay=e_stay, error_switch=e_switch,
                               delta_hat=predicted, regret=regret, upper_bound=2*bound))
    write_csv(out / "cost_error_bounds.csv", bounds)
    return dict(pairs=len(rows), violations=sum(r["residual"] != 0 for r in rows),
                predicted_tie_pairs=sum(r["predicted_tie"] for r in rows),
                true_tie_pairs=sum(r["true_tie"] for r in rows),
                strict_margin_cases=sum(r["strict_error_below_margin"] for r in rows),
                cost_bound_cases=len(bounds), cost_bound_violations=0)


def measure_belief_grid(out):
    states = ("s1", "s2", "s3")
    beliefs = ((F(1, 3),)*3, (F(1, 2), F(1, 3), F(1, 6)), (F(7, 10), F(1, 10), F(1, 5)))
    levels = [F(k, 2) for k in (-3, 0, 1, 4)]
    rows = []
    for index, weights in enumerate(beliefs):
        belief = dict(zip(states, weights))
        assert sum(weights) == 1
        for delta in product(levels, repeat=3):
            for m0 in product(levels, repeat=3):
                interaction = identity.i_delta_per_state(belief, dict(zip(states, delta)), dict(zip(states, m0)))
                independent_mean = sum(weights[i]*interaction[s] for i, s in enumerate(states))
                assert independent_mean == 0
                rows.append(dict(belief_id=index+1, **{f"p{i+1}": p for i, p in enumerate(weights)},
                                 **{f"delta{i+1}": d for i, d in enumerate(delta)},
                                 **{f"m0_{i+1}": d for i, d in enumerate(m0)},
                                 **{f"I{i+1}": interaction[s] for i, s in enumerate(states)},
                                 independent_mean=independent_mean))
    write_csv(out / "belief_grid.csv", rows)
    assert len(rows) == 12288
    return dict(configurations=len(rows), beliefs=len(beliefs), configurations_per_belief=4096,
                mean_zero_violations=sum(r["independent_mean"] != 0 for r in rows))


def measure_diagnostic_limits(out, states, belief, delta, m0):
    interactions = identity.i_delta_per_state(belief, delta, m0)
    detectable = dict(zip(states, (F(3, 8), F(1, 8), F(3, 8), F(1, 8))))
    blind = dict(zip(states, (F(1, 4), F(1, 4), F(3, 8), F(1, 8))))
    cases, state_rows = [], []
    for name, distribution in (("matched", belief), ("detectable_mismatch", detectable), ("undetected_mismatch", blind)):
        mean = sum(distribution[x]*interactions[x] for x in states)
        cases.append(dict(scenario=name, same_belief_as_D=distribution == belief, mean_I_delta=mean,
                          zero_mean_guard_pass=mean == 0))
        for i, x in enumerate(states):
            state_rows.append(dict(scenario=name, state="x_"+"abcd"[i], belief=belief[x],
                                   evaluation_D=distribution[x], I_delta=interactions[x]))
    assert [r["mean_I_delta"] for r in cases] == [F(0), F(1, 8), F(0)]
    d00 = sum(detectable[x]*m0[x] for x in states)
    d01 = sum(belief[x]*delta[x] for x in states)
    split_mean = sum(belief[x]*identity.i_delta(d00, m0[x], d01, delta[x]) for x in states)
    assert split_mean == F(7, 8)
    cases.append(dict(scenario="different_beliefs_cells_00_01", same_belief_as_D=False,
                      mean_I_delta=split_mean, zero_mean_guard_pass=False))
    groups = []
    for mode in ("on", "off"):
        subset = [x for x in states if x[2] == mode]
        mass = sum(belief[x] for x in subset)
        mean = sum(belief[x]*interactions[x] for x in subset)/mass
        groups.append(dict(mode=mode, probability=mass, mean_I_delta=mean, guard_applicable=False))
    assert [r["mean_I_delta"] for r in groups] == [F(1, 4), F(-1, 4)]
    abstract_gaps = dict(zip(CELLS, (F(4), F(3), F(2), F(5))))
    table = cell_costs(F(10), F(15), abstract_gaps)
    assert identity.i_delta(*(abstract_gaps[c] for c in CELLS)) == 4
    assert contrasts(*(table[c] for c in CELLS))["Gamma"] == 0
    e0_rows = []
    for e0 in (-1, 0, 1):
        gaps = {c: gap+e0 for c, gap in additive_cells(F(-2), F(3), F(1, 2)).items()}
        value = identity.i_delta(*(gaps[c] for c in CELLS))
        assert value == 0
        e0_rows.append(dict(e0=e0, **{f"d{c}": gaps[c] for c in CELLS}, I_delta=value))
    write_csv(out / "belief_diagnostics.csv", cases)
    write_csv(out / "belief_diagnostic_states.csv", state_rows)
    write_csv(out / "hidden_mode_groups.csv", groups)
    write_csv(out / "additive_common_error.csv", e0_rows)
    return dict(cases=cases, hidden_groups=groups, different_cell_beliefs_mean=split_mean,
                prediction_without_decision_interaction=dict(I_delta=F(4), gamma=F(0)),
                additive_e0_cases=len(e0_rows), H0_fitted=False, held_out_evaluated=False)


def plot_results(out, canonical):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout="constrained")
    rows = canonical["states"]
    labels = [r["state"] for r in rows]
    for ax, field, title in ((axes[0], "I_delta", "Prediction interaction"), (axes[1], "gamma", "Decision interaction")):
        bars = ax.bar(labels, [float(r[field]) for r in rows])
        ax.bar_label(bars, fmt="%g", padding=3)
        ax.axhline(0, color="black", linewidth=0.7)
        ax.set(title=title, ylabel="packet-slot")
        ax.margins(y=0.2)
    summary = canonical["cell_summaries"]
    bars = axes[2].bar([r["cell"] for r in summary], [float(r["expected_regret"]) for r in summary])
    axes[2].bar_label(bars, fmt="%g", padding=3)
    axes[2].set(title="Expected regret by cell", xlabel="Cell (state,model)", ylabel="packet-slot", ylim=(0,1.4))
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
    fig.savefig(out / "identity_diagnostics.png", dpi=160)
    plt.close(fig)


def render_report(result):
    canonical = result["canonical"]
    lines = ["# L1.5 — F5, I_Δ và giới hạn của phép kiểm belief", "",
             f"Tác giả: **Doan Van Tai** · Ngày thực hiện: **21/10/2026** · Lần chạy: {result['run_time_asia_saigon']}.", "",
             "Triển khai 5 hàm, giữ plant/cost/D của L1.3–L1.4, hoà Stay. F5 không gọi choose; regret trực tiếp "
             "gọi choose L1.4 rồi mới dùng J để chấm. Các dự đoán M0 và belief cho sẵn, chưa implement pipeline L1.6.", "",
             "## Bảng chuẩn", "",
             "H=2,dt=1,c=3,u=2,b_A=1,B on/off=5/0,p=s=1/2,c_sw=0; y=(2,0),tau=1. "
             "Bốn state có cùng observation và xác suất 1/4. Cost/regret/gap/I/gamma có đơn vị **packet·slot**.", "",
             "| State | Δ | M0 gap | e_M | I_Δ | gamma |", "|---|---:|---:|---:|---:|---:|"]
    for r in canonical["states"]:
        lines.append("| "+r["state"]+" | "+" | ".join(f"{float(r[k]):g}" for k in ("delta","m0_gap","model_gap_error","I_delta","gamma"))+" |")
    lines += ["", "d00=1/4,d01=−1/4; E_b[e_M]=1/2. I(x)=E_b[e_M]−e_M(x) khớp ở cả bốn state.",
              "**E_D[I_Δ|y]=0**, nhưng **E_D|I_Δ|=1/4=0,25**. Mean bằng 0 không có nghĩa mọi I bằng 0. "
              "Phân phối exact: I=−1/2 có xác suất 1/4, I=0 có 1/2, I=1/2 có 1/4.", "",
              "| Ô | Decision consistency | Expected regret |", "|---|---:|---:|"]
    for r in canonical["cell_summaries"]:
        lines.append(f"| {r['cell']} | {100*float(r['decision_consistency']):g}% | {float(r['expected_regret']):g} |")
    lines += ["", "Cả **16 cặp episode–ô** khớp golden và hai đường tính regret. "
              "Ô 00 và ô 01 cùng consistency 50% nhưng regret 9/8 và 7/8, vì margin của các lựa chọn sai khác nhau.", "",
              "![I_delta, gamma, regret](identity_diagnostics.png)", "",
              "## Lưới kiểm và bounds nền", "",
              f"- F5: **{result['f5_grid']['pairs']} cặp** Δ,Δ_hat từ −2 tới 2 bước 1/2; 0 sai khác direct/F5. "
              "Có 9 cặp predicted tie và 9 cặp true tie, giao nhau tại (0,0).",
              "- Golden tie Δ=−11/4,+11/4,0 cho regret=11/4,0,0. Không bỏ số hạng hoà.",
              f"- **{result['belief_grid']['configurations']:,} cấu hình** (3 belief × 4096 bộ số): mean I theo chính belief bằng 0; "
              "checker dùng sum trực tiếp, 0 vi phạm. Tự lấy mean theo belief đang dùng là kiểm đại số, chưa kiểm b=P_D(x|y).",
              f"- Bound sai số gap nhỏ hơn margin: {result['f5_grid']['strict_margin_cases']} cặp thỏa tiền đề đều regret=0. "
              "Bound cost error≤b cho regret≤2b: **324 cấu hình, 0 vi phạm** (có lặp khi b=0). Đây là E0 đã biết.", "",
              "## Sức phát hiện và giới hạn của guard mean-zero", "",
              "| Kịch bản | Mean I theo D | Guard mean-zero |", "|---|---:|---|"]
    for r in result["diagnostic_limits"]["cases"]:
        lines.append(f"| {r['scenario']} | {r['mean_I_delta']} | {'thoả' if r['zero_mean_guard_pass'] else 'bị vi phạm'} |")
    lines += ["", "Hai kịch bản mismatch là phép reweight chẩn đoán có chủ đích, không thay D chuẩn của plant. "
              "D=(3/8,1/8,3/8,1/8) làm mean=1/8. D=(1/4,1/4,3/8,1/8) cũng khác b nhưng mean=0 vì cùng "
              "kỳ vọng sai số model. Vì vậy D≠b **không luôn** kéo mean≠0; phép kiểm có sức phát hiện ở trường hợp "
              "đã thử nhưng chưa đủ chứng nhận posterior. Dùng belief khác giữa cell00 và cell01 làm mean=7/8 ở ví dụ thử.",
              "Guard bị vi phạm ở ví dụ cố ý sai nghĩa là test kiểm sức phát hiện phải **PASS**. "
              "Tài liệu có câu lẫn trạng thái PASS của test với trạng thái guard; note đặc tả đã làm rõ.",
              "Nhóm mode thật on/off có mean=1/4 và −1/4; guard theo y không áp cho các nhóm đó. "
              "Sai khác mean cũng có thể do bug/aggregation sai giả định, không chỉ do belief.", "",
              "I không bắt buộc đi cùng gamma: x_c có I=0,gamma=3/2; gaps=(4,3,2,5),J=(10,15) cho I=4,gamma=0. "
              "Thêm common error e0=−1,0,1 vào mô hình cộng đều cho I=0, kể cả khi cell11 chưa là oracle.", "",
              "## Mutation và tính độc lập của người chấm", ""]
    for label, key in (("L1.5 theo tài liệu", "lesson"), ("Bốn lesson theo tài liệu", "lessons"),
                       ("Kiểm giới hạn bổ sung", "limits"), ("Toàn repo", "full_suite")):
        t = result["tests"][key]
        lines.append(f"- {label}: **{t['passed']}/{t['total']} PASS**.")
    lines += ["", "43=11+9+12+11 là số test trong tài liệu; toàn repo còn 11 smoke/timescale, "
              "3 kiểm thêm L1.3, 2 kiểm thêm L1.4 và 2 kiểm thêm L1.5, nên có 61. "
              "Checker cũ được dựng lại trong file riêng, chỉ đổi assert mean-zero từ sum độc lập sang belief_average; "
              "không tuyên bố repo từng dùng phiên bản cũ đó. Mutant chạy ở subprocess riêng; FAIL sau đây có chủ đích.", "",
              "| Bug | Mô tả | Test đỏ checker dùng chung /11 | Test đỏ checker độc lập /11 |", "|---|---|---:|---:|"]
    for name, m in result["mutations"].items():
        lines.append(f"| {name} | {m['description']} | {m['coupled']['failed']} | {m['independent']['failed']} |")
    for name, m in result["mutations"].items():
        lines += ["", f"**{name}, checker cuối bắt bởi:** "+", ".join(f"`{t}`" for t in m["independent"]["failed_tests"])+"."]
    lines += ["", "P4 làm cả implementation và checker cũ cùng lấy trung bình thường: test any-belief xanh sai. "
              "Checker độc lập có trọng số bắt được P4; trong bộ cũ P4 chỉ bị test mismatch bắt tình cờ.",
              "Cross-module: sửa choose L1.4 thành tie Switch trước khi import L1.5 làm đúng 2 test điểm hoà/lưới F5 đỏ. "
              "Điều này xác nhận F5 không dùng chung logic choose bị hỏng với direct regret.", "",
              "## Spec, H0 và file", "",
              "[Note đặc tả](../../lessons/L1.5_identity_diagnostic_spec.md) ghi F5/F6, điều kiện mean-zero, "
              "rà shared computation của test L1.2–L1.4, đoạn H0 ≤10 dòng và việc mang sang L1.8. "
              "H0 chỉ kiểm được khi family/features, split theo workload/parameter, ngân sách fit và metric/biên lỗi được "
              "khoá, fit trên calibration rồi dự báo held-out. True gaps/errors của test chỉ evaluator dùng để chấm targets.",
              "**Chưa fit H0/H1, chưa chấm held-out và chưa kiểm RQ2.** I khác 0 không chứng minh queue mechanism. "
              "Báo E|I| và phân phối; δ cho P(|I|>δ), convention quantile, C_ref và epsilon_E chính thức còn chờ L1.8. "
              "Không chọn δ hoặc báo tỷ lệ đáng kể sau khi xem kết quả.", "",
              "```bash", ".venv/bin/python -m experiments.lessons.run_l1_5",
              ".venv/bin/python -m experiments.lessons.run_l1_5 --output-dir /tmp/l1_5-rerun", "```", "",
              "| File | Nội dung |", "|---|---|",
              "| [config.json](config.json), [results.json](results.json) | Cấu hình, exact metrics, source/doc hashes, commands và scope |",
              "| [canonical_states.csv](canonical_states.csv), [canonical_regrets.csv](canonical_regrets.csv) | I/error/gamma 4 state và regret theo 16 cặp |",
              "| [consistency_regret.csv](consistency_regret.csv), [i_delta_distribution.csv](i_delta_distribution.csv) | Consistency, regret và CDF exact |",
              "| [f5_grid.csv](f5_grid.csv), [belief_grid.csv](belief_grid.csv), [cost_error_bounds.csv](cost_error_bounds.csv) | 81, 12.288 và 324 cấu hình |",
              "| [belief_diagnostics.csv](belief_diagnostics.csv), [belief_diagnostic_states.csv](belief_diagnostic_states.csv), [hidden_mode_groups.csv](hidden_mode_groups.csv) | Phát hiện mismatch, blind spot, nhóm mode |",
              "| [additive_common_error.csv](additive_common_error.csv) | Common error e0 và I dưới cộng tính |",
              "| lesson.txt, lessons.txt, limits.txt, full_suite.txt và *.xml | Log/JUnit baseline thật |",
              "| P*_coupled.txt, P*_independent.txt và *.xml; P*_patch.py | Replay checker cũ, checker cuối và năm bug cụ thể |",
              "| coupled_checker/test_l1_5_identity.py | Bản test dùng chung helper, chỉ phục vụ replay |",
              "| cross_choose.txt/xml, cross_choose_patch.py | Lỗi choose L1.4 bị test L1.5 phát hiện |",
              "| [identity_diagnostics.png](identity_diagnostics.png) | Biểu đồ từ số đo |", "",
              "Source: `experiments/lessons/l1_5_identity.py`, runner `experiments/lessons/run_l1_5.py`; "
              "tests `tests/test_l1_5_identity.py`, `tests/test_l1_5_diagnostic_limits.py`; golden `tests/golden_phase1.py`. "
              "Golden ghi từ tài liệu ngày 21/10/2026; chưa là bài giấy của tác giả. "
              "Không sửa snapshot contract-v0; note chỉ chuẩn bị contract-v1.",
              "Exact int/Fraction, không RNG/seed/Monte Carlo hoặc CI lấy mẫu. Verification E0/E1 không xác nhận "
              "hypothesis, posterior S0, novelty hay network validity. Giữ G1,V3/V10/V11 và HOLD Phase 4.",
              f"Python {result['environment']['python']}, pytest {result['environment']['pytest']}; "
              f"wall time runner {result['elapsed_seconds']:.3f} s (không là benchmark mạng).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "notes/verification/l1_5")
    out = parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    run_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat()
    config = dict(author="Doan Van Tai", canonical=CANON, cell_order=CELLS, observation=(2,0), tau=1,
                  prior_on=F(1,2), belief=[F(1,4)]*4, m0_gaps=[F(2),F(-1,2),F(2),F(-5,2)],
                  dt=1,c_sw=0,tie_action="Stay", metric="regret / gap / I_delta; packet-slot", seed=None,
                  f5_grid=[F(k,2) for k in range(-4,5)],
                  belief_grid_weights=[[F(1,3)]*3,[F(1,2),F(1,3),F(1,6)],[F(7,10),F(1,10),F(1,5)]],
                  belief_grid_levels=[F(k,2) for k in (-3,0,1,4)], cost_error_bounds=[F(0),F(1,2),F(1),F(2)],
                  method="exact finite enumeration; independent checker for belief moments",
                  significance_delta=None, quantile_convention=None, H0_fitted=False, held_out_evaluated=False)
    write_json(out / "config.json", config)
    coupled_file = make_coupled_checker(out)
    tests = {}
    targets_by_name = (("lesson",[CORE]),
                       ("lessons",["tests/test_l1_2_queue.py","tests/test_l1_3_expected_cost.py","tests/test_l1_4_factorial.py",CORE]),
                       ("limits",[EXTRA]),("full_suite",["tests/"]))
    for name, targets in targets_by_name:
        t = run_tests(out,name,targets)
        tests[name] = t
        if t["returncode"] or t["errors"] or t["skipped"]:
            write_json(out/"failed_run.json",dict(stage=name,result=t))
            raise RuntimeError(f"Baseline failed: see {out/t['log']}")
        print(f"{name}: {t['passed']}/{t['total']} PASS",flush=True)
    assert tests["lesson"]["total"] == 11 and tests["lessons"]["total"] == 43
    assert tests["limits"]["total"] == 2
    golden = load_module("golden_phase1",ROOT/"tests/golden_phase1.py")
    canonical,states,belief,delta,m0 = measure_canonical(out,golden)
    f5_grid = measure_f5(out)
    belief_grid = measure_belief_grid(out)
    limits = measure_diagnostic_limits(out,states,belief,delta,m0)
    print("Exact: 16 canonical pairs; 81 F5 pairs; 12288 belief configurations; 0 violations",flush=True)
    mutations = {}
    for name,(description,_) in MUTANTS.items():
        measured = {}
        for stage,targets in (("coupled",[coupled_file]),("independent",[CORE])):
            t = run_tests(out,f"{name}_{stage}",targets,name)
            assert t["returncode"] == 1 and t["failed"] > 0 and t["total"] == 11
            assert not t["errors"] and not t["skipped"]
            measured[stage] = t
        mutations[name] = dict(description=description,**measured)
        print(f"{name}: coupled checker {measured['coupled']['failed']}/11 FAIL; independent {measured['independent']['failed']}/11 FAIL",flush=True)
    checker_name = "test_mean_zero_holds_for_any_belief_and_any_numbers"
    assert checker_name not in mutations["P4"]["coupled"]["failed_tests"]
    assert checker_name in mutations["P4"]["independent"]["failed_tests"]
    cross = run_tests(out,"cross_choose",[CORE],"cross_choose")
    assert cross["returncode"] == 1 and cross["failed"] == 2 and not cross["errors"]
    plot_results(out,canonical)
    sources = ["experiments/lessons/l1_2_queue.py","experiments/lessons/l1_3_expected_cost.py","experiments/lessons/l1_4_factorial.py",
               "experiments/lessons/l1_5_identity.py","experiments/lessons/run_l1_2.py","experiments/lessons/run_l1_3.py",
               "experiments/lessons/run_l1_5.py",CORE,EXTRA,"tests/golden_phase1.py","pyproject.toml",
               "notes/lessons/L1.5_experiment_card.md","notes/lessons/L1.5_identity_diagnostic_spec.md"]
    documents = [Path("/home/vantai/.codex/attachments/f6b36ef8-5e94-4ce4-b055-5bbdbaf8dd81/Pasted text.txt"),
                 Path("/home/vantai/.codex/attachments/fac04c56-a37a-479f-9e5e-43b1f669a8e9/Pasted text.txt")]
    import pytest
    commit = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
    result = dict(author="Doan Van Tai",run_time_asia_saigon=run_time,configuration=config,
                  environment=dict(python=platform.python_version(),pytest=pytest.__version__),base_commit=commit,
                  source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                  supplied_documents=[dict(part=i+1,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                      for i,p in enumerate(documents) if p.is_file()],
                  golden_provenance=golden.L1_5_PROVENANCE,tests=tests,canonical=canonical,f5_grid=f5_grid,
                  belief_grid=belief_grid,diagnostic_limits=limits,mutations=mutations,cross_module_mutation=cross,
                  elapsed_seconds=time.perf_counter()-started,
                  scope="exact finite verification; given belief/M0; no posterior certification, H0 fit or held-out claims; G1/V3/V10/V11 unchanged")
    write_json(out/"results.json",result)
    (out/"report.md").write_text(render_report(result),encoding="utf-8")
    print("Canonical I_delta:",[r["I_delta"] for r in canonical["states"]])
    print("Mean I_delta:",canonical["mean_i_delta"],"; mean absolute:",canonical["mean_abs_i_delta"])
    print("Diagnostics:",[(r["scenario"],r["mean_I_delta"]) for r in limits["cases"]])
    print(f"Report: {out/'report.md'}")


if __name__ == "__main__":
    main()
