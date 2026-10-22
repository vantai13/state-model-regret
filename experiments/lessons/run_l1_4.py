"""Doan Van Tai — run L1.4 bookkeeping, exact grids, patterns, isolated mutants.

Run: .venv/bin/python -m experiments.lessons.run_l1_4
Artifacts are derived from actual runs. The canonical predicted gaps are given
inputs from the lesson, not predictions derived from an implemented S/M pipeline.
"""
import argparse
import hashlib
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.lessons import l1_4_factorial as factorial
from experiments.lessons.l1_3_expected_cost import CANON, expected_cost, generate_episodes
from experiments.lessons.run_l1_2 import load_module, write_csv
from experiments.lessons.run_l1_3 import write_json

ROOT = Path(__file__).resolve().parents[2]
CORE = "tests/test_l1_4_factorial.py"
EXTRA = "tests/test_l1_4_patterns.py"
ASYMMETRIC = "test_asymmetric_errors_distinguish_state_from_model"
CELLS = ("00", "10", "01", "11")
MUTANTS = {
    "N1": ("Đảo dấu Gamma", """
original = factorial.contrasts
def bad_contrasts(*args):
    result = original(*args)
    result['Gamma'] = -result['Gamma']
    return result
factorial.contrasts = bad_contrasts
"""),
    "N2": ("G_S|M1 copy nhầm công thức G_M", """
original = factorial.contrasts
def bad_contrasts(L00, L10, L01, L11):
    result = original(L00, L10, L01, L11)
    result['G_S|M1'] = L00-L01
    return result
factorial.contrasts = bad_contrasts
"""),
    "N3": ("Hoà chọn Switch", """
factorial.choose = lambda gap: 'Switch' if gap <= 0 else 'Stay'
"""),
    "N4": ("Additive cells đổi nhãn state repair và model repair", """
def bad_additive(delta, e_S, e_M):
    return {'00': delta+e_S+e_M, '10': delta+e_S, '01': delta+e_M, '11': delta}
factorial.additive_cells = bad_additive
"""),
    "N5": ("Tại điểm hoà, dùng J thật để chọn action", """
def bad_cell_costs(J_stay, J_switch, gaps):
    costs = {'Stay': J_stay, 'Switch': J_switch}
    return {cell: min(J_stay, J_switch) if gap == 0 else costs[factorial.choose(gap)]
            for cell, gap in gaps.items()}
factorial.cell_costs = bad_cell_costs
"""),
}


def C(table):
    return factorial.contrasts(*(table[cell] for cell in CELLS))


def run_tests(out, name, targets, mutant=None, initial=False):
    junit = out / f"{name}.xml"
    args = ["-q", "--color=no", f"--junitxml={junit}", *targets]
    if initial:
        args += ["-k", f"not {ASYMMETRIC}"]
    if mutant:
        patch = out / f"{mutant}_patch.py"
        patch.write_text("# Doan Van Tai — isolated mutation only.\nimport sys\nimport pytest\n"
                         f"sys.path.insert(0, {str(ROOT)!r})\n"
                         "from experiments.lessons import l1_4_factorial as factorial\n"
                         + MUTANTS[mutant][1] + "\nraise SystemExit(pytest.main(sys.argv[1:]))\n", encoding="utf-8")
        command = [sys.executable, str(patch), *args]
    else:
        command = [sys.executable, "-m", "pytest", *args]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (out / f"{name}.txt").write_text(proc.stdout+proc.stderr, encoding="utf-8")
    if not junit.is_file():
        raise RuntimeError(f"JUnit missing: {out / (name+'.txt')}")
    cases = list(ET.parse(junit).iter("testcase"))
    failed = [c.attrib["name"] for c in cases if c.find("failure") is not None]
    errors = [c.attrib["name"] for c in cases if c.find("error") is not None]
    skipped = [c.attrib["name"] for c in cases if c.find("skipped") is not None]
    return dict(command=command, returncode=proc.returncode, total=len(cases),
                passed=len(cases)-len(failed)-len(errors)-len(skipped), failed=len(failed),
                failed_tests=failed, errors=errors, skipped=skipped,
                log=f"{name}.txt", junit=f"{name}.xml", wall_seconds=time.perf_counter()-started)


def properties(table, margin):
    contrasts = C(table)
    return dict(a=all(contrasts[k] >= 0 for k in ("G_SM", "G_S|M1", "G_M|S1")),
                b=F(contrasts["Gamma"])/margin in {-1, 0, 1, 2},
                e=contrasts["Gamma"] == contrasts["G_S|M1"]-contrasts["G_S"]
                  == contrasts["G_M|S1"]-contrasts["G_M"])


def measure_grid(out, name, levels):
    rows, coefficients, pattern_counts = [], Counter(), Counter()
    violations = dict(a=0, b=0, e=0, additive_identity=0)
    for delta, eS, eM in product((-3, -1, 1, 3), levels, levels):
        gaps = factorial.additive_cells(delta, eS, eM)
        table = factorial.cell_costs(F(10), F(10+delta), gaps)
        cs = C(table)
        best = min(10, 10+delta)
        indicators = tuple(int(table[cell] > best) for cell in CELLS[:3])
        coefficient = cs["Gamma"]/abs(delta)
        checks = properties(table, abs(delta))
        for prop, ok in checks.items():
            violations[prop] += not ok
        i_delta = gaps["11"]-gaps["10"]-gaps["01"]+gaps["00"]
        violations["additive_identity"] += i_delta != 0
        coefficients[str(coefficient)] += 1
        pattern_counts[str(indicators)] += 1
        rows.append(dict(delta=delta, e_S=eS, e_M=eM,
                         **{f"gap_{cell}": gaps[cell] for cell in CELLS},
                         **{f"ell_{cell}": table[cell] for cell in CELLS},
                         **cs, i00=indicators[0], i10=indicators[1], i01=indicators[2],
                         gamma_coefficient=coefficient, I_delta=i_delta,
                         **{f"property_{prop}": ok for prop, ok in checks.items()}))
    write_csv(out / f"{name}.csv", rows)
    assert not any(violations.values()), violations
    assert set(coefficients) == {"-1", "0", "1"}
    assert "(0, 1, 1)" not in pattern_counts
    return dict(configurations=len(rows), violations=violations,
                coefficient_counts=dict(coefficients), pattern_counts=dict(pattern_counts),
                coefficient_two_cases=0, has_probability_distribution=False)


def measure_patterns(out):
    rows = []
    for delta in (-2, 2):
        best = min(20, 20+delta)
        for indicators in product((0, 1), repeat=3):
            bits = dict(zip(CELLS, (*indicators, 0)))
            gaps = {cell: -delta if wrong else delta for cell, wrong in bits.items()}
            table = factorial.cell_costs(F(20), F(20+delta), gaps)
            cs = C(table)
            coeff = factorial.gamma_coefficient(*indicators)
            assert cs["Gamma"] == coeff*abs(delta)
            assert table == {cell: best+wrong*abs(delta) for cell, wrong in bits.items()}
            assert all(properties(table, abs(delta)).values())
            rows.append(dict(delta=delta, i00=indicators[0], i10=indicators[1], i01=indicators[2],
                             coefficient=coeff, **cs, **{f"ell_{cell}": table[cell] for cell in CELLS},
                             I_delta=gaps["11"]-gaps["10"]-gaps["01"]+gaps["00"]))
    write_csv(out / "all_patterns.csv", rows)
    assert {r["coefficient"] for r in rows} == {-1, 0, 1, 2}
    return dict(cases=len(rows), distinct_patterns=8, coefficients=[-1, 0, 1, 2],
                coefficient_two_cases=sum(r["coefficient"] == 2 for r in rows))


def measure_canonical(out, golden):
    distribution = generate_episodes((2, 0), 1, CANON, F(1, 2))
    episode_rows, cell_rows, pattern_mass = [], [], {}
    for label, state in (("x_a", golden.X_A), ("x_b", golden.X_B),
                         ("x_c", golden.X_C), ("x_d", golden.X_D)):
        stay, switch = (expected_cost(state, action, CANON) for action in ("Stay", "Switch"))
        probability, delta = distribution[state], switch-stay
        gaps = {"00": F(1, 4), "10": golden.DELTA_HAT_10[state], "01": F(-1, 4), "11": delta}
        table = factorial.cell_costs(stay, switch, gaps)
        best = min(stay, switch)
        indicators = tuple(int(table[cell] > best) for cell in CELLS[:3])
        cs = C(table)
        assert table == golden.FACTORIAL_ROWS[state]
        assert all(properties(table, abs(delta)).values())
        assert cs["Gamma"] == factorial.gamma_coefficient(*indicators)*abs(delta)
        pattern = ",".join(str(i) for i in indicators)
        pattern_mass[pattern] = pattern_mass.get(pattern, F(0)) + probability
        episode_rows.append(dict(state=label, qA=state[0], qB=state[1], mode=state[2], probability=probability,
                                 j_stay=stay, j_switch=switch, delta=delta, oracle_cost=best,
                                 **{f"ell_{cell}": table[cell] for cell in CELLS},
                                 **{f"r_{cell}": table[cell]-best for cell in CELLS},
                                 i00=indicators[0], i10=indicators[1], i01=indicators[2], pattern=pattern,
                                 gamma_coefficient=cs["Gamma"]/abs(delta), **cs))
        for cell in CELLS:
            cell_rows.append(dict(state=label, probability=probability, cell=cell,
                                  delta_hat=gaps[cell], action=factorial.choose(gaps[cell]),
                                  true_cost=table[cell], regret=table[cell]-best, wrong=int(table[cell] > best)))
    assert sum(r["probability"] for r in episode_rows) == 1
    means = {cell: sum(r["probability"]*r[f"ell_{cell}"] for r in episode_rows) for cell in CELLS}
    cs = C(means)
    assert means == golden.FACTORIAL_MEANS and cs == golden.FACTORIAL_CONTRASTS
    for name, value in cs.items():
        assert value == sum(r["probability"]*r[name] for r in episode_rows)
    l_star = sum(r["probability"]*r["oracle_cost"] for r in episode_rows)
    regrets = {cell: means[cell]-l_star for cell in CELLS}
    assert C(regrets) == cs
    mode_rows = []
    for mode in ("on", "off"):
        subset = [r for r in episode_rows if r["mode"] == mode]
        mass = sum(r["probability"] for r in subset)
        mode_means = {cell: sum(r["probability"]*r[f"ell_{cell}"] for r in subset)/mass for cell in CELLS}
        mode_rows.append(dict(mode=mode, probability=mass, **C(mode_means),
                              evaluator_only=True))
    write_csv(out / "canonical_episodes.csv", episode_rows)
    write_csv(out / "canonical_cells.csv", cell_rows)
    write_csv(out / "canonical_by_mode.csv", mode_rows)
    write_csv(out / "pattern_distribution.csv", [dict(pattern=p, probability=mass) for p, mass in pattern_mass.items()])
    write_csv(out / "canonical_means.csv", [dict(cell=c, expected_cost=means[c], expected_regret=regrets[c]) for c in CELLS])
    return dict(episodes=episode_rows, means=means, regrets=regrets, contrasts=cs, oracle_cost=l_star,
                pattern_probability=pattern_mass, by_mode=mode_rows,
                model_repair_harm_probability=sum(r["probability"] for r in episode_rows if r["G_M"] < 0),
                gamma_range=[min(r["Gamma"] for r in episode_rows), max(r["Gamma"] for r in episode_rows)],
                identity_violations=0, contrast_linearity_violations=0)


def measure_toys(out):
    sweep = []
    expected_gamma = (0, 0, -2, -2, 2, 2, 2, 2, 2)
    for k in range(9):
        e = F(k, 2)
        gaps = factorial.additive_cells(-2, e, e)
        table = factorial.cell_costs(F(20), F(18), gaps)
        cs = C(table)
        assert cs["Gamma"] == expected_gamma[k]
        sweep.append(dict(e=e, **{f"ell_{cell}": table[cell] for cell in CELLS}, **cs))
    tie_gaps = factorial.additive_cells(-2, F(3, 2), F(1, 2))
    tie_stay = factorial.cell_costs(20, 18, tie_gaps)
    # A diagnostic alternative only; the actual decision function stays unchanged.
    tie_switch = {cell: 18 if gap <= 0 else 20 for cell, gap in tie_gaps.items()}
    assert (C(tie_stay)["Gamma"], C(tie_switch)["Gamma"]) == (-2, 0)
    positive = factorial.table_from_additive(F(20), F(18), 3, 3)
    negative = factorial.table_from_additive(F(20), F(18), F(3, 2), F(3, 2))
    mixtures = []
    for p in (F(1, 2), F(7, 10)):
        mean = {cell: p*positive[cell]+(1-p)*negative[cell] for cell in CELLS}
        cs = C(mean)
        assert cs["Gamma"] == 4*p-2
        assert all(cs[k] == p*C(positive)[k]+(1-p)*C(negative)[k] for k in cs)
        mixtures.append(dict(p_positive=p, p_negative=1-p, mean_abs_gamma=F(2), **cs))
    repairs = []
    for scale in (F(1), F(0), F(1, 2)):
        for kind, eM, eS in ((1, F(1), F(3, 2)), (2, F(3), F(-5, 2))):
            gap = -2+eM+scale*eS
            action = factorial.choose(gap)
            cost = 18 if action == "Switch" else 20
            repairs.append(dict(state_error_scale=scale, type=kind, probability=F(1, 2),
                                delta_hat=gap, action=action, true_cost=cost, regret=cost-18))
    repair_means = {str(s): sum(r["probability"]*r["regret"] for r in repairs if r["state_error_scale"] == s)
                    for s in (F(1), F(0), F(1, 2))}
    assert repair_means == {"1": F(1), "0": F(1), "1/2": F(0)}
    asymmetric = C(factorial.table_from_additive(20, 18, 3, F(1, 2)))
    mirror = C(factorial.table_from_additive(20, 18, F(1, 2), 3))
    assert (asymmetric["G_S"], asymmetric["G_M"]) == (2, 0)
    assert (mirror["G_S"], mirror["G_M"]) == (0, 2)
    write_csv(out / "error_sweep.csv", sweep)
    write_csv(out / "mixtures.csv", mixtures)
    write_csv(out / "partial_repairs.csv", repairs)
    write_csv(out / "tie_diagnostic.csv", [dict(tie_action=a, **C(t)) for a, t in (("Stay", tie_stay), ("Switch", tie_switch))])
    return dict(error_sweep=sweep, mixtures=mixtures, partial_regrets=repair_means,
                full_state_gain=F(0), half_state_gain=F(1), R00=F(1),
                tie_gamma_stay=-2, tie_gamma_switch=0, asymmetric=asymmetric, mirrored=mirror)


def plot_results(out, canonical, toys):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
    sweep = toys["error_sweep"]
    axes[0, 0].step([float(r["e"]) for r in sweep], [float(r["Gamma"]) for r in sweep], where="post")
    axes[0, 0].scatter((1, 2), (-2, 2), zorder=3)
    axes[0, 0].set(title="Additive toy: fixed J=20/18, ties Stay", xlabel="e_S = e_M", ylabel="Gamma (cost units)", yticks=(-2, 0, 2))
    rows = canonical["episodes"]
    bars = axes[0, 1].bar([r["state"] for r in rows], [float(r["Gamma"]) for r in rows],
                         color=["#ff7f0e" if r["Gamma"] > 0 else "#1f77b4" for r in rows])
    axes[0, 1].bar_label(bars, fmt="%g", padding=3)
    axes[0, 1].axhline(float(canonical["contrasts"]["Gamma"]), color="black", linestyle="--", label="Mean Gamma=-0.25")
    axes[0, 1].set(title="Canonical episodes: gamma", ylabel="packet-slot", ylim=(-3.8, 2.8))
    axes[0, 1].legend()
    indexes = list(range(4))
    for offset, key, label in ((-0.18, "G_S", "State repair"), (0.18, "G_M", "Model repair")):
        axes[1, 0].bar([i+offset for i in indexes], [float(r[key]) for r in rows], width=0.36, label=label)
    axes[1, 0].set(xticks=indexes, xticklabels=[r["state"] for r in rows], title="Canonical episode gains", ylabel="packet-slot")
    axes[1, 0].legend()
    patterns = canonical["pattern_probability"]
    bars = axes[1, 1].bar(list(patterns), [float(p) for p in patterns.values()], color=("#ff7f0e", "#1f77b4"))
    axes[1, 1].bar_label(bars, fmt="%g", padding=3)
    axes[1, 1].set(title="Pattern probability under canonical D", xlabel="(i00,i10,i01)", ylabel="Probability", ylim=(0, 0.65))
    for ax in axes.flat:
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
    fig.savefig(out / "factorial_results.png", dpi=160)
    plt.close(fig)


def render_report(result):
    canonical, tests = result["canonical"], result["tests"]
    lines = ["# L1.4 — sổ sách 2×2: kết quả chạy và đo", "",
             f"Tác giả: **Doan Van Tai** · Ngày thực hiện: **21/10/2026** · Lần chạy: {result['run_time_asia_saigon']}.", "",
             "Đã triển khai sáu hàm sổ sách D19, dùng J từ L1.3. Chỉ gap dự đoán được dùng để chọn action; "
             "J thật dùng sau quyết định để chấm điểm. Golden và experiment card được ghi trước khi chạy.", "",
             "## Cấu hình và bảng chuẩn", "",
             "H=2,dt=1,c_A=c_B=3,u=2,b_A=1,B on/off=5/0,p=s=1/2,c_sw=0. "
             "D sinh từ y=(2,0),tau=1,prior_on=1/2 độc lập observation, trước t0 dùng Stay; mỗi state có xác suất 1/4. "
             "Gap00=1/4, gap01=−1/4; gap10 theo x_a…x_d là 2,−1/2,2,−5/2; gap11=Δ thật. "
             "Đây là các dự đoán cho sẵn; nguồn gốc belief/model chờ L1.6. Đơn vị cost, gain, gamma: **packet·slot**.", "",
             "| Episode | ℓ00 | ℓ10 | ℓ01 | ℓ11 | g_S | g_M | γ | Pattern |", "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in canonical["episodes"]:
        values = [r[f"ell_{c}"] for c in CELLS]+[r["G_S"], r["G_M"], r["Gamma"]]
        lines.append("| "+r["state"]+" | "+" | ".join(f"{float(v):g}" for v in values)+f" | ({r['pattern']}) |")
    lines += ["", "| Ô | Expected cost L | Expected regret R |", "|---|---:|---:|"]
    for cell in CELLS:
        lines.append(f"| {cell} | {float(canonical['means'][cell]):g} | {float(canonical['regrets'][cell]):g} |")
    lines += ["", "| G_S | G_M | G_SM | Γ | G_S given M1 | G_M given S1 |", "|---:|---:|---:|---:|---:|---:|",
              "| "+" | ".join(f"{float(v):g}" for v in canonical["contrasts"].values())+" |", "",
              "Cell11 và cell10 đạt cost oracle L_*=25/4=6,25. Model repair có G_M=1/4 trung bình "
              "nhưng g_M âm ở x_a,x_c, chiếm **1/2 tổng xác suất D**. Gamma trung bình=−1/4, "
              "trong khi gamma episode từ −3 tới +2. Hai pattern (0,0,1) và (1,0,0) có xác suất 1/2 mỗi loại; "
              "toàn bộ gamma dương trong ví dụ này đến từ bù sai số, không phải pattern (1,1,1).", "",
              "Nhóm mode on: G_M=−7/4, Gamma=7/4; mode off: G_M=9/4, Gamma=−9/4. "
              "Các nhóm theo mode thật chỉ là chẩn đoán evaluator, chưa là nhóm triển khai có thể quan sát trước action.", "",
              "![Sweep, episode gains và pattern](factorial_results.png)", "",
              "## Lưới và bất biến", "",
              f"- Lưới nửa đơn vị: **{result['grids']['coarse']['configurations']:,} cấu hình**, 0 vi phạm (a),(b),(e).",
              f"- Lưới bước 1/6: **{result['grids']['fine']['configurations']:,} cấu hình**, 0 vi phạm (a),(b),(e).",
              "- Cả hai lưới cộng tính chỉ cho hệ số gamma/margin thuộc {−1,0,1}; không có hệ số 2. "
              "Đây là số đếm thiết kế, không phải tần suất ước lượng cho phân phối D.",
              "- Kiểm đủ 8 pattern cho Δ=−2 và +2: **16 trường hợp**, chạm đủ {−1,0,1,2}; "
              "hai trường hợp hệ số 2 cho gamma=4. Margin bằng 0 cho mọi contrast bằng 0.",
              "- Tuyến tính và đồng nhất thức theo cả cost lẫn regret đúng chính xác ở bảng chuẩn, 0 vi phạm.", "",
              "**Giới hạn cộng tính (E0).** Với gap11=Δ và I_delta=0: gap00=gap10+gap01−Δ. "
              "Nếu Δ<0, hai ô 10/01 sai nghĩa là gap10,gap01≥0, kéo gap00>0 nên ô 00 cũng sai. "
              "Nếu Δ>0, hai ô đó sai nghĩa là gap10,gap01<0, kéo gap00<0 nên ô 00 cũng sai. "
              "Vậy pattern (0,1,1) không thể xuất hiện và gamma≤|Δ|. Khi Δ≠0 và cell11 là oracle chính xác, "
              "gamma=2|Δ| bác bỏ cộng tính ở episode đó; chưa xác định nguyên nhân là queue hay predictor/estimator phi tuyến.", "",
              "Ở Phase 3, test (b) phải chạy trên dự đoán thực M0/M1, cùng golden bất đối xứng và test tại điểm hoà. "
              "Lưới cộng tính không bao phủ hết các pattern.", "",
              "## Part A: các phép kiểm sổ sách", "",
              "- Quét e=0,1/2,…,4: Gamma=0,0,−2,−2,2,2,2,2,2. Cost 20/18 giữ nguyên.",
              "- Chỉ tại điểm hoà e_S=3/2,e_M=1/2: tie Stay cho Gamma=−2, tie Switch cho 0. "
              "D16 thực thi vẫn là tie Stay; phương án kia chỉ để chẩn đoán.",
              "- Mixture p=7/10 cho Gamma=4/5; p=1/2 cho 0 dù mọi episode có |gamma|=2.",
              "- EV-26: R không sửa=1, sửa hết state=1, sửa một nửa=0. Full gain=0, half gain=1=R00; "
              "gain oracle repair không là cận trên chung.",
              "- Bất đối xứng e_S=3,e_M=1/2 cho G_S=2,G_M=0; đảo hai lỗi cho G_S=0,G_M=2.", "",
              "## Tests và năm bug giả", ""]
    for label, name in (("L1.4 theo tài liệu", "lesson"), ("Ba lesson theo tài liệu", "lessons"),
                        ("Kiểm pattern/margin bổ sung", "patterns"), ("Toàn repo", "full_suite")):
        t = tests[name]
        lines.append(f"- {label}: **{t['passed']}/{t['total']} PASS**.")
    lines += ["", "32 test trong tài liệu là 11+9+12; repo có thêm 11 smoke/timescale, "
              "3 kiểm bổ sung L1.3 và 2 kiểm bổ sung L1.4, nên tổng là 48. "
              "Các FAIL mutant sau đây có chủ đích; mỗi mutant chạy ở subprocess riêng, không thay source baseline.", "",
              "| Bug | Mô tả | Test đỏ ban đầu /11 | Test đỏ cuối /12 |", "|---|---|---:|---:|"]
    for name, m in result["mutations"].items():
        description = m["description"].replace("|", "\\|")
        lines.append(f"| {name} | {description} | {m['initial']['failed']} | {m['final']['failed']} |")
    for name, m in result["mutations"].items():
        lines += ["", f"**{name}**, test cuối bắt: "+", ".join(f"`{t}`" for t in m["final"]["failed_tests"])+"."]
    lines += ["", "N4 đổi nhãn S/M lọt toàn bộ 11 test ban đầu, kể cả ba tính chất, "
              "rồi bị golden bất đối xứng bắt. Mutation này tác động `additive_cells`; bảng chuẩn cho gaps trực tiếp "
              "không đi qua hàm đó. Các bất biến đối xứng tự chúng chưa kiểm được ngữ nghĩa nhãn.",
              "N1 đảo dấu vẫn qua test (b) trên lưới cộng tính, nhưng bị test bổ sung đủ pattern bắt "
              "khi hệ số 2 biến thành −2. N5 bị bắt tại điểm hoà vì dùng cost thật để chọn vi phạm quyền thông tin.", "",
              "Lần runner đầu dừng sau 48/48 test PASS vì phép chia cost nguyên tạo nhãn hệ số float "
              "(-1.0,0.0,1.0), khác nhãn Fraction được kiểm. Đã sửa bằng Fraction trước phép chia; "
              "không đổi công thức, golden hay cấu hình. Record lỗi tại `notes/verification/l1_4/development_issue.json` trong repo.", "",
              "## File và tái chạy", "",
              "Source: `experiments/lessons/l1_4_factorial.py`; runner: `experiments/lessons/run_l1_4.py`; "
              "tests: `tests/test_l1_4_factorial.py`, `tests/test_l1_4_patterns.py`; golden: `tests/golden_phase1.py`; "
              "card: `notes/lessons/L1.4_experiment_card.md`.", "",
              "```bash", ".venv/bin/python -m experiments.lessons.run_l1_4",
              ".venv/bin/python -m experiments.lessons.run_l1_4 --output-dir /tmp/l1_4-rerun", "```", "",
              "| Artifact | Nội dung |", "|---|---|",
              "| [config.json](config.json), [results.json](results.json) | Cấu hình, metric/seed, kết quả exact, commands, source/document hashes |",
              "| [canonical_cells.csv](canonical_cells.csv) | 16 dòng: gap, action, cost và regret của từng ô |",
              "| [canonical_episodes.csv](canonical_episodes.csv), [canonical_means.csv](canonical_means.csv) | Bốn episode, L/R trung bình và sáu contrast |",
              "| [pattern_distribution.csv](pattern_distribution.csv), [canonical_by_mode.csv](canonical_by_mode.csv) | Pattern có trọng số D, chẩn đoán theo mode thật |",
              "| [coarse_grid.csv](coarse_grid.csv), [fine_grid.csv](fine_grid.csv), [all_patterns.csv](all_patterns.csv) | Toàn lưới và 16 trường hợp pattern |",
              "| [error_sweep.csv](error_sweep.csv), [mixtures.csv](mixtures.csv), [partial_repairs.csv](partial_repairs.csv), [tie_diagnostic.csv](tie_diagnostic.csv) | Part A |",
              "| lesson.txt, lessons.txt, patterns.txt, full_suite.txt và *.xml | stdout/stderr và JUnit thật |",
              "| N1_initial.txt…N5_initial.txt, N1_final.txt…N5_final.txt, *.xml, N1_patch.py…N5_patch.py | Bug cụ thể và kết quả trước/sau golden bất đối xứng |",
              "| N1_all_patterns.txt/xml | Kiểm riêng khả năng bắt đảo dấu khi chạm hệ số 2 |",
              "| [factorial_results.png](factorial_results.png) | Hình dựng từ số liệu đã chạy |", "",
              "Đây là verification E0/E1 trên cấu hình khai báo, chưa là evidence mạng hoặc xác nhận hypothesis/novelty. "
              "Golden ghi từ đáp án tài liệu ngày 21/10/2026, chưa thay bài tác giả tự tính. "
              "Chưa suy ra S0/M0/M1 end-to-end hoặc kiểm null L1.5. Giữ G1,V3/V10/V11 và HOLD Phase 4.",
              "Không có RNG/seed, Monte Carlo hoặc CI lấy mẫu; số học int/Fraction chính xác. "
              "Bất định tương lai trong J được tích phân theo law L1.3, không phải đã loại bỏ mọi model uncertainty.",
              f"Python {result['environment']['python']}, pytest {result['environment']['pytest']}; "
              f"wall time runner {result['elapsed_seconds']:.3f} s (không phải benchmark mạng).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "notes/verification/l1_4")
    out = parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    run_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat()
    golden = load_module("golden_phase1", ROOT / "tests/golden_phase1.py")
    config = dict(author="Doan Van Tai", canonical=CANON, cell_order=CELLS,
                  observation=(2, 0), tau=1, prior_on=F(1, 2), prior_independent_of_observation=True,
                  dt=1, c_sw=0, tie_action="Stay", metric="cumulative end-of-slot occupancy; packet-slot",
                  given_gaps=dict(cell00=F(1, 4), cell01=F(-1, 4), cell10=[golden.DELTA_HAT_10[x] for x in golden.FACTORIAL_ROWS], cell11="true Delta"),
                  delta_grid=[-3, -1, 1, 3], coarse_error_levels=[F(k, 2) for k in range(-8, 9)],
                  fine_error_levels=[F(k, 6) for k in range(-24, 25)],
                  seed=None, method="exact enumeration; int/Fraction; no Monte Carlo")
    write_json(out / "config.json", config)
    tests = {}
    for name, targets in (("lesson", [CORE]),
                          ("lessons", ["tests/test_l1_2_queue.py", "tests/test_l1_3_expected_cost.py", CORE]),
                          ("patterns", [EXTRA]), ("full_suite", ["tests/"])):
        measured = run_tests(out, name, targets)
        tests[name] = measured
        if measured["returncode"] or measured["errors"] or measured["skipped"]:
            write_json(out / "failed_run.json", dict(stage=name, result=measured))
            raise RuntimeError(f"Baseline failed: see {out / measured['log']}")
        print(f"{name}: {measured['passed']}/{measured['total']} PASS", flush=True)
    assert tests["lesson"]["total"] == 12 and tests["lessons"]["total"] == 32
    assert tests["patterns"]["total"] == 2
    canonical = measure_canonical(out, golden)
    grids = dict(coarse=measure_grid(out, "coarse_grid", config["coarse_error_levels"]),
                 fine=measure_grid(out, "fine_grid", config["fine_error_levels"]))
    assert grids["coarse"]["configurations"] == 1156 and grids["fine"]["configurations"] == 9604
    patterns = measure_patterns(out)
    toys = measure_toys(out)
    print("Exact grids: 1156 + 9604 configurations; 0 property violations; 16 all-pattern cases", flush=True)
    mutations = {}
    for name, (description, _) in MUTANTS.items():
        stages = {}
        for stage in ("initial", "final"):
            measured = run_tests(out, f"{name}_{stage}", [CORE], name, initial=stage == "initial")
            assert measured["total"] == (11 if stage == "initial" else 12)
            assert not measured["errors"] and not measured["skipped"]
            survival = name == "N4" and stage == "initial"
            assert measured["returncode"] == (0 if survival else 1)
            assert (measured["failed"] == 0) == survival
            stages[stage] = measured
        mutations[name] = dict(description=description, **stages)
        print(f"{name}: {stages['initial']['failed']}/11 initially FAIL; {stages['final']['failed']}/12 finally FAIL", flush=True)
    n1_patterns = run_tests(out, "N1_all_patterns", [f"{EXTRA}::test_property_b_all_patterns_include_coefficient_two"], "N1")
    assert n1_patterns["returncode"] == 1 and n1_patterns["failed"] == 1 and not n1_patterns["errors"]
    assert "test_property_b_gamma_takes_four_values" not in mutations["N1"]["final"]["failed_tests"]
    plot_results(out, canonical, toys)
    sources = ["experiments/lessons/l1_2_queue.py", "experiments/lessons/l1_3_expected_cost.py",
               "experiments/lessons/l1_4_factorial.py", "experiments/lessons/run_l1_2.py",
               "experiments/lessons/run_l1_3.py", "experiments/lessons/run_l1_4.py", CORE, EXTRA,
               "tests/golden_phase1.py", "pyproject.toml", "notes/lessons/L1.4_experiment_card.md"]
    attachments = [Path("/home/vantai/.codex/attachments/f5021979-10cb-43a8-b1e3-0075de21b28f/Pasted text.txt"),
                   Path("/home/vantai/.codex/attachments/264d284b-dd16-4080-8489-33176ca354bf/Pasted text.txt")]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    import pytest
    result = dict(author="Doan Van Tai", run_time_asia_saigon=run_time, configuration=config,
                  environment=dict(python=platform.python_version(), pytest=pytest.__version__), base_commit=commit,
                  source_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                  supplied_documents=[dict(part=i+1, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                      for i, p in enumerate(attachments) if p.is_file()],
                  golden_provenance=golden.L1_4_PROVENANCE, tests=tests, canonical=canonical,
                  grids=grids, all_patterns=patterns, toys=toys, mutations=mutations,
                  extra_mutation_test=n1_patterns, elapsed_seconds=time.perf_counter()-started,
                  scope="finite E0/E1 verification; given predicted gaps; G1/V3/V10/V11 unchanged; no network validation")
    write_json(out / "results.json", result)
    (out / "report.md").write_text(render_report(result), encoding="utf-8")
    print("Canonical L (00,10,01,11):", canonical["means"])
    print("Canonical contrasts:", canonical["contrasts"])
    print("Pattern mass:", canonical["pattern_probability"])
    print(f"Report: {out / 'report.md'}")


if __name__ == "__main__":
    main()
