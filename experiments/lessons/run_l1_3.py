"""Doan Van Tai — reproduce L1.3 exact metrics and isolated mutation experiments.

Run from repo root: .venv/bin/python -m experiments.lessons.run_l1_3
No RNG, sampling, external data, or change to the L1.2 plant.
"""
import argparse
import hashlib
import json
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
from experiments.lessons.l1_3_expected_cost import (
    CANON, expected_cost, futures, generate_episodes, mode_paths, oracle, p_idle,
)
from experiments.lessons.run_l1_2 import load_module, slot_rows, write_csv

ROOT = Path(__file__).resolve().parents[2]
CORE = "tests/test_l1_3_expected_cost.py"
ASYM_TEST = "test_asymmetric_chain_weights_branches_by_probability"
ACTIONS = ("Stay", "Switch")
MUTANTS = {
    "M1": ("Hoà chọn Switch", """
def bad_oracle(x, th):
    delta = lesson.expected_cost(x, 'Switch', th) - lesson.expected_cost(x, 'Stay', th)
    return ('Switch' if delta <= 0 else 'Stay'), delta
lesson.oracle = bad_oracle
"""),
    "M2": ("Mode slot 0 bị phân nhánh thay vì cố định theo x", """
def bad_futures(x, th):
    for seq, pr in lesson.mode_paths(x[2], th['H'], th['p_onon'], th['p_offoff']):
        yield [lesson._rate(m, th) for m in seq[1:]], pr
lesson.futures = bad_futures
"""),
    "M3": ("D12 bỏ chạy plant, giữ backlog y làm state hiện tại", """
def bad_episodes(y, tau, th, prior_on):
    out = {}
    for initial, p0 in (('on', prior_on), ('off', 1-prior_on)):
        if p0 == 0:
            continue
        for seq, pr in lesson.mode_paths(initial, tau, th['p_onon'], th['p_offoff']):
            x = (*y, seq[-1])
            out[x] = out.get(x, 0) + p0*pr
    return out
lesson.generate_episodes = bad_episodes
"""),
    "M4": ("Không nhân xác suất path cũ: dùng pm thay pr×pm", """
def bad_mode_paths(m0, n, p_onon, p_offoff):
    paths = [((m0,), F(1))]
    for _ in range(n):
        nxt = []
        for seq, pr in paths:
            last = seq[-1]
            keep = p_onon if last == 'on' else p_offoff
            other = 'off' if last == 'on' else 'on'
            for mode, pm in ((last, keep), (other, 1-keep)):
                if pm > 0:
                    nxt.append((seq+(mode,), pm))
        paths = nxt
    return paths
lesson.mode_paths = bad_mode_paths
"""),
    "M5": ("Expected cost lấy trung bình thường, bỏ trọng số xác suất", """
def bad_expected_cost(x, action, th):
    costs = [lesson.two_queue_cost(x[:2], [th['bA']]*th['H'], bB,
             th['u'], th['cA'], th['cB'], action)[0] for bB, pr in lesson.futures(x, th)]
    return F(sum(costs), len(costs))
lesson.expected_cost = bad_expected_cost
"""),
}


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2,
                               default=lambda value: str(value) if isinstance(value, F) else value) + "\n",
                    encoding="utf-8")


def run_tests(out, name, targets, mutation_name=None, initial=False):
    junit = out / f"{name}.xml"
    args = ["-q", "--color=no", f"--junitxml={junit}", *targets]
    if initial:
        args += ["-k", f"not {ASYM_TEST}"]
    if mutation_name:
        patch_file = out / f"{mutation_name}_patch.py"
        patch_file.write_text(
            "# Doan Van Tai — isolated mutant, never imported by normal tests.\n"
            "from fractions import Fraction as F\nimport sys\nimport pytest\n"
            f"sys.path.insert(0, {str(ROOT)!r})\n"
            "from experiments.lessons import l1_3_expected_cost as lesson\n"
            + MUTANTS[mutation_name][1] + "\nraise SystemExit(pytest.main(sys.argv[1:]))\n", encoding="utf-8")
        command = [sys.executable, str(patch_file), *args]
    else:
        command = [sys.executable, "-m", "pytest", *args]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (out / f"{name}.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if not junit.is_file():
        raise RuntimeError(f"Missing JUnit: see {name}.txt")
    cases = list(ET.parse(junit).iter("testcase"))
    failed = [c.attrib["name"] for c in cases if c.find("failure") is not None]
    errors = [c.attrib["name"] for c in cases if c.find("error") is not None]
    skipped = [c.attrib["name"] for c in cases if c.find("skipped") is not None]
    return dict(command=command, returncode=proc.returncode, total=len(cases),
                passed=len(cases)-len(failed)-len(errors)-len(skipped), failed=len(failed),
                failed_tests=failed, errors=errors, skipped=skipped,
                wall_seconds=time.perf_counter()-started, log=f"{name}.txt", junit=f"{name}.xml")


def measure_states(out, golden):
    episodes = generate_episodes((2, 0), 1, CANON, F(1, 2))
    assert episodes == {x: F(1, 4) for x in golden.EXPECTED_COSTS}
    summary, branch_rows, slots = [], [], []
    named_states = (("x_a", golden.X_A), ("x_b", golden.X_B), ("x_c", golden.X_C), ("x_d", golden.X_D))
    for label, x in named_states:
        probability = episodes[x]
        stay, switch = (expected_cost(x, a, CANON) for a in ACTIONS)
        action, delta = oracle(x, CANON)
        p_st, p_sw = (p_idle(x, a, CANON) for a in ACTIONS)
        assert (stay, switch) == golden.EXPECTED_COSTS[x]
        assert (p_st, p_sw) == golden.IDLE_PROBABILITIES[x]
        expected_idle_difference, clairvoyant = F(0), F(0)
        for bB, pr in futures(x, CANON):
            tail = "on" if bB[-1] == CANON["rate_on"] else "off"
            st, i_st = two_queue_cost(x[:2], [1, 1], bB, 2, 3, 3, "Stay")
            sw, i_sw = two_queue_cost(x[:2], [1, 1], bB, 2, 3, 3, "Switch")
            assert (st, sw, i_st, i_sw) == golden.FUTURE_BRANCHES[(x, tail)]
            weighted = sum((2-j)*(s-t) for j, (s, t) in enumerate(zip(i_sw, i_st)))
            assert sw-st == weighted
            expected_idle_difference += pr*weighted
            clairvoyant += pr*min(st, sw)
            branch_rows.append(dict(state=label, qA=x[0], qB=x[1], mode0=x[2], mode1=tail,
                                    conditional_probability=str(pr), cost_stay=st, cost_switch=sw,
                                    idle_stay_0=i_st[0], idle_stay_1=i_st[1],
                                    idle_switch_0=i_sw[0], idle_switch_1=i_sw[1],
                                    delta=sw-st, weighted_idle_diff=weighted, min_path_cost=min(st, sw)))
            for chosen in ACTIONS:
                for index, queue in enumerate(("A", "B")):
                    managed = CANON["u"] if (chosen == "Stay") == (queue == "A") else 0
                    background = [1, 1] if queue == "A" else bB
                    slots.extend(slot_rows(x[index], [b+managed for b in background], 3,
                                           f"{label}_{tail}", chosen, queue))
        assert delta == expected_idle_difference
        assert clairvoyant == min(stay, switch)
        summary.append(dict(state=label, qA=x[0], qB=x[1], mode0=x[2], probability=probability,
                            j_stay=stay, j_switch=switch, delta=delta, oracle=action,
                            p_idle_stay=p_st, p_idle_switch=p_sw, conservation=p_st == p_sw == 0,
                            oracle_cost=min(stay, switch), clairvoyant_cost=clairvoyant,
                            regret_stay=stay-min(stay, switch), regret_switch=switch-min(stay, switch)))
    l_star = sum(r["probability"]*r["oracle_cost"] for r in summary)
    l_stay = sum(r["probability"]*r["j_stay"] for r in summary)
    l_switch = sum(r["probability"]*r["j_switch"] for r in summary)
    baselines = [dict(policy="Oracle", cost=l_star, regret=F(0)),
                 dict(policy="Always Stay", cost=l_stay, regret=l_stay-l_star),
                 dict(policy="Always Switch", cost=l_switch, regret=l_switch-l_star)]
    assert (l_star, l_stay, l_switch) == (F(25, 4), F(59, 8), F(57, 8))
    assert (l_stay-l_star, l_switch-l_star) == (F(9, 8), F(7, 8))
    assert all(r["delta"] != 0 and not r["conservation"] for r in summary)
    write_csv(out / "state_costs.csv", summary)
    write_csv(out / "future_branches.csv", branch_rows)
    write_csv(out / "slot_tables.csv", slots)
    write_csv(out / "baselines.csv", baselines)
    return summary, baselines


def trace_episodes(y, tau, th, prior_on, scenario):
    rows, aggregate = [], {}
    for initial, p0 in (("on", prior_on), ("off", 1-prior_on)):
        for seq, pr in mode_paths(initial, tau, th["p_onon"], th["p_offoff"]):
            qA, _ = rollout(y[0], [th["bA"]+th["u"]]*tau, th["cA"])
            qB, _ = rollout(y[1], [th["rate_on"] if m == "on" else th["rate_off"] for m in seq[:-1]], th["cB"])
            x = (qA[-1] if qA else y[0], qB[-1] if qB else y[1], seq[-1])
            aggregate[x] = aggregate.get(x, F(0)) + p0*pr
            rows.append(dict(scenario=scenario, observation_A=y[0], observation_B=y[1], tau=tau,
                             modes=" -> ".join(seq), path_probability=str(p0*pr),
                             qA0=x[0], qB0=x[1], mode0=x[2]))
    assert aggregate == generate_episodes(y, tau, th, prior_on)
    return rows


def extra_cases(out, golden):
    asymmetric = dict(CANON, p_onon=F(3, 4), p_offoff=F(1, 4))
    asym_costs = tuple(expected_cost(golden.X_B, a, asymmetric) for a in ACTIONS)
    assert asym_costs == golden.ASYMMETRIC_EXPECTED_COSTS
    asym_paths = [dict(bB=bB, probability=pr,
                       costs=[two_queue_cost(golden.X_B[:2], [1, 1], bB, 2, 3, 3, a)[0] for a in ACTIONS])
                  for bB, pr in futures(golden.X_B, asymmetric)]
    h3 = dict(CANON, H=3)
    h3_costs = tuple(expected_cost(golden.X_D, a, h3) for a in ACTIONS)
    assert h3_costs == golden.H3_EXPECTED_COSTS
    h3_paths = []
    for bB, pr in futures(golden.X_D, h3):
        tail = tuple("on" if b else "off" for b in bB[1:])
        costs = tuple(two_queue_cost(golden.X_D[:2], [1]*3, bB, 2, 3, 3, a)[0] for a in ACTIONS)
        assert costs == golden.H3_BRANCH_COSTS[tail]
        h3_paths.append(dict(bB=bB, probability=pr, costs=costs))
    tau0 = generate_episodes((2, 0), 0, CANON, F(3, 4))
    assert tau0 == {golden.X_C: F(3, 4), golden.X_D: F(1, 4)}
    tau2 = generate_episodes((2, 0), 2, asymmetric, F(3, 4))
    assert tau2 == golden.TAU2_EPISODES
    traces = trace_episodes((2, 0), 1, CANON, F(1, 2), "canonical")
    traces += trace_episodes((2, 0), 0, CANON, F(3, 4), "tau0_prior3_4")
    traces += trace_episodes((2, 0), 2, asymmetric, F(3, 4), "tau2_prior3_4")
    write_csv(out / "episode_paths.csv", traces)
    as_records = lambda eps: [dict(state=x, probability=pr) for x, pr in eps.items()]
    return dict(asymmetric=dict(parameters=asymmetric, state=golden.X_B, costs=asym_costs, branches=asym_paths),
                h3=dict(parameters=h3, state=golden.X_D, costs=h3_costs, branches=h3_paths),
                tau0=as_records(tau0), tau2=as_records(tau2))


def audit_old_example(out):
    rows = []
    for bB in product((0, 2), repeat=2):
        costs = [two_queue_cost((2, 0), [1, 1], list(bB), 2, 3, 3, a)[0] for a in ACTIONS]
        rows.append(dict(bB0=bB[0], bB1=bB[1], probability="1/4", stay=costs[0], switch=costs[1]))
    stay = sum(F(r["stay"], 4) for r in rows)
    switch = sum(F(r["switch"], 4) for r in rows)
    unchanged_A, _ = rollout(0, [3, 3], 3)
    assert (stay, switch) == (F(4), F(5, 4)) and unchanged_A == [0, 0]
    write_csv(out / "old_example_paths.csv", rows)
    return dict(source="L1.3 Part 1 section 13 quotation; not a full audit of original Master Plan",
                c_sw0=dict(stay=stay, switch=switch, delta=switch-stay),
                c_sw3=dict(stay=stay, switch=switch+3, delta=switch+3-stay),
                A_from_observation_zero=unchanged_A,
                D12_reachable_A2_from_A0=False,
                label="bookkeeping example, not a plant-generated episode under the quoted assumptions")


def plot_results(out, states, baselines):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    indexes = list(range(len(states)))
    for offset, field, label in ((-0.18, "j_stay", "Stay"), (0.18, "j_switch", "Switch")):
        bars = axes[0].bar([i+offset for i in indexes], [float(r[field]) for r in states], width=0.36, label=label)
        axes[0].bar_label(bars, fmt="%g", padding=3)
    axes[0].set(xticks=indexes, xticklabels=[r["state"] for r in states], ylabel="Expected cost (packet-slot)",
                title="Canonical states: J(a | x), H=2")
    axes[0].legend()
    bars = axes[1].bar(["Oracle", "Always Stay", "Always Switch"], [float(r["regret"]) for r in baselines],
                       color=("#2ca02c", "#1f77b4", "#ff7f0e"))
    axes[1].bar_label(bars, fmt="%g", padding=3)
    axes[1].set(ylabel="Expected regret (packet-slot)", title="Baselines on D: four states, each P=1/4", ylim=(0, 1.3))
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
    fig.savefig(out / "expected_costs.png", dpi=160)
    plt.close(fig)


def render_report(result):
    tests = result["tests"]
    lines = ["# L1.3 — expected cost, oracle và regret", "",
             f"Tác giả: **Doan Van Tai** · Ngày thực hiện: **21/10/2026** · Lần chạy: {result['run_time_asia_saigon']}.", "",
             "Đã triển khai sáu hàm theo hai phần L1.3, dùng lại plant L1.2. Experiment card lập trước khi chạy; "
             "không đổi recurrence, metric hoặc điều kiện thí nghiệm.", "",
             "## Cấu hình và kết quả state", "",
             "c_A=c_B=3, u=2, nền A=1, nền B on/off=5/0; p=s=1/2. H=2, dt=1, c_sw=0. "
             "y=(2,0) đầu slot −1, tau=1; mode lúc −1 có prior 1/2 độc lập với y. Trước t0 dùng Stay. "
             "Mode slot 0 thuộc state; chỉ slot 1 là tương lai. Hoà chọn Stay.", "",
             "| State | (q_A,q_B,mode) | P_D | J Stay | J Switch | Δ | Oracle | P idle Stay | P idle Switch |",
             "|---|---|---:|---:|---:|---:|---|---:|---:|"]
    for r in result["states"]:
        lines.append(f"| {r['state']} | ({r['qA']},{r['qB']},{r['mode0']}) | {r['probability']} | "
                     f"{float(r['j_stay']):g} | {float(r['j_switch']):g} | {float(r['delta']):+g} | "
                     f"{r['oracle']} | {r['p_idle_stay']} | {r['p_idle_switch']} |")
    lines += ["", "Mọi state có Δ khác 0 và có idle với xác suất dương dưới ít nhất một action; "
              "**0/4 state thuộc vùng bảo toàn**. Có idle là điều kiện cần, tự nó chưa đủ kết luận không suy biến.", "",
              "## Baselines và oracle", "", "Cost, Δ và regret có đơn vị **packet·slot**.", "",
              "| Luật | Expected cost L | Expected regret | Giá trị chính xác (L; R) |",
              "|---|---:|---:|---|"]
    for r in result["baselines"]:
        lines.append(f"| {r['policy']} | {float(r['cost']):g} | {float(r['regret']):g} | {r['cost']}; {r['regret']} |")
    lines += ["", "Oracle không thấu thị được dùng làm benchmark. Phép kiểm chẩn đoán E[min C] bằng min J "
              "ở cả bốn state, nên oracle thấu thị cũng có L=25/4 ở riêng ví dụ này; không suy ra kết quả cho law/H khác.",
              "Tính bằng Fraction trên toàn cây: **không sai số lấy mẫu, không RNG/seed, không CI thống kê**. "
              "Bất định tương lai vẫn hiện diện trong law và đã được tích phân; chưa kiểm model uncertainty hoặc mạng thật.", "",
              "![Expected cost và regret](expected_costs.png)", "",
              "## Bảng nhánh — kiểm nối L1.2", "",
              "[future_branches.csv](future_branches.csv) chứa 8 nhánh (2/state), "
              "[slot_tables.csv](slot_tables.csv) chứa 64 dòng A/B theo action và slot. "
              "Tất cả cost và idle khớp bảng cung cấp; hiệu cost từng nhánh và kỳ vọng khớp tổng idle có trọng số, 0 vi phạm.", "",
              "## Kiểm thử và mutation", "",
              f"- L1.3 theo tài liệu: **{tests['lesson']['passed']}/{tests['lesson']['total']} PASS**.",
              f"- L1.2 + L1.3 theo tài liệu: **{tests['lessons']['passed']}/{tests['lessons']['total']} PASS**.",
              f"- Ba test biên/nhiều bước bổ sung: **{tests['boundaries']['passed']}/{tests['boundaries']['total']} PASS**.",
              f"- Toàn repository: **{tests['full_suite']['passed']}/{tests['full_suite']['total']} PASS**.",
              "- Con số 19 trong Part 1 ứng với 11+8 test trước test bất đối xứng; Part 2 dùng 11+9=20. "
              "Toàn repo còn có 11 test smoke/timescale và 3 test bổ sung, nên là 34.", "",
              "Mutant chạy trong subprocess riêng, không sửa source baseline. FAIL dưới đây là lỗi được cài có chủ đích.", "",
              "| Mutant | Bug | Test đỏ, bộ đầu (8) | Test đỏ, bộ cuối (9) |", "|---|---|---:|---:|"]
    for name, mutation in result["mutations"].items():
        lines.append(f"| {name} | {mutation['description']} | {mutation['initial']['failed']}/8 | {mutation['final']['failed']}/9 |")
    for name, mutation in result["mutations"].items():
        lines += ["", f"**{name}, test cuối bắt được:** " + ", ".join(f"`{t}`" for t in mutation["final"]["failed_tests"]) + "."]
    lines += ["", "M5 lọt toàn bộ 8 test ban đầu: nhánh 1/2–1/2 che lỗi bỏ trọng số. "
              "Test bất đối xứng bắt được M5 với x_b,p=3/4,s=1/4: J(Stay)=11/2=5,5, J(Switch)=19/4=4,75. "
              "M4 chỉ lộ khi có nhiều bước chuyển; zero-action kiểm riêng luật hoà của M1.", "",
              "## Các trường hợp bổ sung", "",
              "- H=3,x_d: các tail on/on,on/off,off/on,off/off có xác suất 1/4; "
              "cost Stay=12/8/8/6, Switch=12/7/4/0; J=17/2 và 23/4.",
              "- tau=0, prior_on=3/4: giữ nguyên backlog y, mode on/off có xác suất 3/4 và 1/4.",
              "- tau=2,p=3/4,s=1/4,prior_on=3/4: 8 path gộp thành 6 state, tổng xác suất 1. "
              "[episode_paths.csv](episode_paths.csv) lưu cả trace chuẩn, tau=0 và tau=2.", "",
              "Preflight trước khi hoàn thiện có **22 PASS, 1 FAIL**: bảng dự đoán bổ sung H=3 "
              "ghi nhầm Stay tail on/off là 7. Tính lại A=[2,2,2] (tổng 6), B=[0,2,0] (tổng 2) "
              "cho cost đúng 8, J Stay=17/2. Đã sửa dẫn giải/golden, giữ nguyên plant và đáp án tài liệu. "
              "Log lần lỗi lưu tại `notes/verification/l1_3/preflight.txt` và `preflight.xml` trong repo; "
              "experiment card giữ dự đoán ban đầu kèm đính chính.", "",
              "## Kiểm toán EV-22", "",
              "Chỉ dùng cấu hình được trích trong L1.3 Part 1 §13, chưa đối chiếu bản Master Plan gốc đầy đủ: "
              "B i.i.d. {0,2}, q=(2,0), H=2, c=3,u=2,b_A=1. Liệt kê 4 path cho J Stay=4, Switch=5/4 "
              "khi c_sw=0, Δ=−11/4. Cộng c_sw=3 như ví dụ cũ cho Switch=17/4=4,25, Δ=1/4; "
              "giá trị này chỉ để audit lịch sử, không đưa vào cấu hình thí nghiệm hiện hành.",
              "Dưới Stay, A nhận đúng capacity nên q_A giữ nguyên: quan sát 0 không thể sinh state thật 2. "
              "EV-22 được ghi nhãn **ví dụ sổ sách, không phải episode sinh từ plant** dưới các giả định đã trích. "
              "Giữ bảng lịch sử và các phép tính đại số của nó; ví dụ chuẩn L1.3 dùng cho phần episode/J phía sau.", "",
              "## File, tái lập và giới hạn", "",
              "Source: `experiments/lessons/l1_3_expected_cost.py`; runner: `experiments/lessons/run_l1_3.py`; "
              "tests: `tests/test_l1_3_expected_cost.py`, `tests/test_l1_3_boundaries.py`; "
              "golden: `tests/golden_phase1.py`; experiment card: `notes/lessons/L1.3_experiment_card.md`.", "",
              "```bash", ".venv/bin/python -m experiments.lessons.run_l1_3",
              ".venv/bin/python -m pytest -q",
              "# Tái chạy sang thư mục khác để giữ artifact hiện tại:",
              ".venv/bin/python -m experiments.lessons.run_l1_3 --output-dir /tmp/l1_3-rerun", "```", "",
              "| File | Nội dung |", "|---|---|",
              "| [config.json](config.json) | Cấu hình chính, biến thể, seed=null, metric và điều kiện |",
              "| [results.json](results.json) | Kết quả chính xác, môi trường, command đã chạy, hash source/tài liệu nguồn |",
              "| [state_costs.csv](state_costs.csv), [baselines.csv](baselines.csv) | J, Δ, oracle, P_idle, L và regret |",
              "| [future_branches.csv](future_branches.csv), [slot_tables.csv](slot_tables.csv) | Cost/idle của từng nhánh, từng queue/slot |",
              "| [episode_paths.csv](episode_paths.csv), [old_example_paths.csv](old_example_paths.csv) | Pre-t0 traces và bốn path audit EV-22 |",
              "| lesson.txt, lessons.txt, boundaries.txt, full_suite.txt và *.xml | stdout/stderr và JUnit thật của baseline |",
              "| M1_initial.txt…M5_initial.txt, M1_final.txt…M5_final.txt và *.xml | Kết quả mutation trước/sau test bất đối xứng |",
              "| M1_patch.py…M5_patch.py | Code bug tách biệt để kiểm lại; không import trong test thông thường |",
              "| [expected_costs.png](expected_costs.png) | Biểu đồ từ số liệu thực thi |", "",
              "Golden ngày 21/10/2026 ghi từ tài liệu; chưa là xác nhận tác giả đã tự tính bài giấy. "
              "Các trường hợp bổ sung có dẫn giải exact riêng. Giữ G1, V3/V10/V11 và HOLD Phase 4. "
              "Không suy implementation hoàn thành thành hypothesis đúng, không tính G_S/G_M/Gamma trước L1.4.",
              "Liệt kê cây tăng theo 2^(H−1); H=4 tối đa 8 nhánh, H=50 tối đa 562.949.953.421.312 nhánh/state "
              "cho chuỗi đầy đủ hai nhánh. Chưa chạy H=50, chưa implement lan truyền phân phối Phase 3. "
              "p=s=1/2 là chuỗi dạy học; kết quả chưa đại diện nguồn traffic vật lý.", "",
              f"Python {result['environment']['python']}; pytest {result['environment']['pytest']}. "
              f"Wall time runner: {result['elapsed_seconds']:.3f} s (gồm test, mutation, exact enumeration, vẽ hình; không là benchmark mạng).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "notes/verification/l1_3")
    out = parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    run_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat()
    config = dict(author="Doan Van Tai", canonical=CANON, observation=(2, 0), tau=1, prior_on=F(1, 2),
                  prior_independent_of_observation=True, pre_t0_action="Stay", dt=1, c_sw=0,
                  tie_action="Stay", metric="end-of-slot cumulative occupancy; packet-slot",
                  seed=None, method="exact integers/Fractions; enumerate all positive-probability paths",
                  asymmetric=dict(p_onon=F(3, 4), p_offoff=F(1, 4)),
                  supplementary=dict(H=3, tau_values=[0, 2], prior_on=F(3, 4)))
    write_json(out / "config.json", config)
    golden = load_module("golden_phase1", ROOT / "tests/golden_phase1.py")
    tests = {}
    for name, targets in (("lesson", [CORE]), ("lessons", ["tests/test_l1_2_queue.py", CORE]),
                          ("boundaries", ["tests/test_l1_3_boundaries.py"]), ("full_suite", ["tests/"])):
        measured = run_tests(out, name, targets)
        tests[name] = measured
        if measured["returncode"] != 0 or measured["skipped"] or measured["errors"]:
            write_json(out / "failed_run.json", dict(stage=name, result=measured))
            raise RuntimeError(f"Baseline failed: see {out / measured['log']}")
        print(f"{name}: {measured['passed']}/{measured['total']} PASS", flush=True)
    assert tests["lesson"]["total"] == 9 and tests["lessons"]["total"] == 20
    assert tests["boundaries"]["total"] == 3
    states, baselines = measure_states(out, golden)
    extras = extra_cases(out, golden)
    old = audit_old_example(out)
    mutations = {}
    for name, (description, _) in MUTANTS.items():
        stages = {}
        for stage in ("initial", "final"):
            measured = run_tests(out, f"{name}_{stage}", [CORE], name, initial=stage == "initial")
            assert not measured["errors"] and not measured["skipped"]
            assert measured["total"] == (8 if stage == "initial" else 9)
            expected_survival = name == "M5" and stage == "initial"
            assert measured["returncode"] == (0 if expected_survival else 1)
            assert (measured["failed"] == 0) == expected_survival
            stages[stage] = measured
        mutations[name] = dict(description=description, **stages)
        print(f"{name}: initial {stages['initial']['failed']}/8 FAIL, final {stages['final']['failed']}/9 FAIL", flush=True)
    plot_results(out, states, baselines)
    sources = ["experiments/lessons/l1_2_queue.py", "experiments/lessons/l1_3_expected_cost.py",
               "experiments/lessons/run_l1_2.py", "experiments/lessons/run_l1_3.py", "tests/golden_phase1.py",
               "tests/test_l1_2_queue.py", CORE, "tests/test_l1_3_boundaries.py", "pyproject.toml",
               "notes/lessons/L1.3_experiment_card.md"]
    attachments = [Path("/home/vantai/.codex/attachments/996bc096-c05b-43ad-903b-aa202b898ff0/Pasted text.txt"),
                   Path("/home/vantai/.codex/attachments/2dec9193-6cc4-474a-a89a-4ecff7476d57/Pasted text.txt")]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    import pytest
    result = dict(author="Doan Van Tai", run_time_asia_saigon=run_time, configuration=config,
                  environment=dict(python=platform.python_version(), pytest=pytest.__version__), base_commit=commit,
                  source_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                  supplied_documents=[dict(part=i+1, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                      for i, p in enumerate(attachments) if p.is_file()],
                  golden_provenance=golden.L1_3_PROVENANCE, tests=tests, states=states, baselines=baselines,
                  extras=extras, old_example_audit=old, mutations=mutations,
                  elapsed_seconds=time.perf_counter()-started,
                  scope="declared finite toy cases; G1/V3/V10/V11 unchanged; no network evidence or author understanding certification")
    write_json(out / "results.json", result)
    (out / "report.md").write_text(render_report(result), encoding="utf-8")
    for r in states:
        print(f"{r['state']}: P={r['probability']}, J(Stay)={r['j_stay']}, J(Switch)={r['j_switch']}, delta={r['delta']}, oracle={r['oracle']}")
    for r in baselines:
        print(f"{r['policy']}: L={r['cost']} ({float(r['cost']):g}), R={r['regret']} ({float(r['regret']):g})")
    print(f"Report: {out / 'report.md'}")


if __name__ == "__main__":
    main()
