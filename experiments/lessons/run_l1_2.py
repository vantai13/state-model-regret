"""Run and persist the declared L1.2 verification, including isolated mutants.

Author: Doan Van Tai.
From repo root: .venv/bin/python -m experiments.lessons.run_l1_2
Outputs are actual runs, not values copied into a report. No RNG/seed/network.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from fractions import Fraction
from itertools import product
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.lessons.l1_2_queue import rollout, step, two_queue_cost

ROOT = Path(__file__).resolve().parents[2]
MUTANTS = {
    "B1": ("Service trước arrivals; idle cũng theo model đó", """
def mutant_step(q, a, c):
    return max(0, q - c) + a, max(0, c - q)
plant.step = mutant_step
"""),
    "B2": ("Cộng backlog k=0 vào cost", """
original = plant.two_queue_cost
def mutant_cost(q0, bA, bB, u, cA, cB, action, dt=1):
    cost, idle = original(q0, bA, bB, u, cA, cB, action, dt)
    return cost + dt * sum(q0), idle
plant.two_queue_cost = mutant_cost
"""),
    "B3": ("Idle quên arrivals", """
def mutant_step(q, a, c):
    return max(0, q + a - c), max(0, c - q)
plant.step = mutant_step
"""),
    "B4": ("Switch thêm u vào B nhưng giữ u ở A", """
def mutant_cost(q0, bA, bB, u, cA, cB, action, dt=1):
    qA, iA = plant.rollout(q0[0], [b + u for b in bA], cA)
    qB, iB = plant.rollout(q0[1], [b + (u if action == 'Switch' else 0) for b in bB], cB)
    return dt * (sum(qA) + sum(qB)), [a + b for a, b in zip(iA, iB)]
plant.two_queue_cost = mutant_cost
"""),
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pytest_run(out, name, mutation=None):
    xml_path = out / f"{name}.xml"
    args = ["-q", "--color=no", f"--junitxml={xml_path}"]
    if name != "full_suite":
        args.append("tests/test_l1_2_queue.py")
    if mutation:
        bootstrap = ("import pytest\nfrom experiments.lessons import l1_2_queue as plant\n"
                     + mutation + "\nraise SystemExit(pytest.main(" + repr(args) + "))\n")
        command = [sys.executable, "-c", bootstrap]
    else:
        command = [sys.executable, "-m", "pytest", *args]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    elapsed = time.perf_counter() - started
    (out / f"{name}.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if not xml_path.exists():
        raise RuntimeError(f"{name}: pytest did not create JUnit; see {out / (name + '.txt')}")
    cases = list(ET.parse(xml_path).iter("testcase"))
    failures = [case.attrib["name"] for case in cases if case.find("failure") is not None]
    errors = [case.attrib["name"] for case in cases if case.find("error") is not None]
    skipped = [case.attrib["name"] for case in cases if case.find("skipped") is not None]
    return dict(returncode=proc.returncode, total=len(cases), failed=len(failures),
                passed=len(cases) - len(failures) - len(errors) - len(skipped),
                failed_tests=failures, errors=errors, skipped=skipped,
                wall_seconds=elapsed, log=f"{name}.txt", junit=f"{name}.xml")


def enumerate_grid(reference):
    rows, violations = [], []
    for qA, qB, cA, cB, u in product((0, 2, 10), (0, 2, 10), (2, 3), (2, 3), (0, 2)):
        for a0, a1, b0, b1 in product((0, 1, 4), repeat=4):
            cfg = dict(q0=(qA, qB), bA=[a0, a1], bB=[b0, b1], u=u, cA=cA, cB=cB)
            stay, idle_st = two_queue_cost(action="Stay", **cfg)
            switch, idle_sw = two_queue_cost(action="Switch", **cfg)
            rhs = sum((2 - j) * (sw - st) for j, (sw, st) in enumerate(zip(idle_sw, idle_st)))
            no_idle = not any(idle_st + idle_sw)
            ref_st = reference.rollout((qA, qB), ((a0, b0), (a1, b1)), (cA, cB), u)
            ref_sw = reference.rollout((qA, qB), ((a0, b0), (a1, b1)), (cA, cB), u, True)
            matches = (stay, idle_st) == ref_st and (switch, idle_sw) == ref_sw
            if switch - stay != rhs or (no_idle and stay != switch) or not matches:
                violations.append(cfg)
            rows.append(dict(qA0=qA, qB0=qB, cA=cA, cB=cB, u=u,
                             bA0=a0, bA1=a1, bB0=b0, bB1=b1,
                             cost_stay=stay, cost_switch=switch, delta=switch-stay,
                             idle_stay_0=idle_st[0], idle_stay_1=idle_st[1],
                             idle_switch_0=idle_sw[0], idle_switch_1=idle_sw[1],
                             weighted_idle_diff=rhs, identity_residual=switch-stay-rhs,
                             no_idle_both=no_idle, reference_match=matches))
    return rows, dict(configurations=len(rows),
                      identity_violations=sum(r["identity_residual"] != 0 for r in rows),
                      no_idle_pairs=sum(r["no_idle_both"] for r in rows),
                      no_idle_cost_violations=sum(r["no_idle_both"] and r["delta"] != 0 for r in rows),
                      reference_mismatches=sum(not r["reference_match"] for r in rows),
                      violating_configurations=violations,
                      zero_action_pairs=sum(r["u"] == 0 for r in rows))


def slot_rows(q0, arrivals, capacity, example, action, queue):
    rows, q = [], q0
    for k, a in enumerate(arrivals):
        q_next, idle = step(q, a, capacity)
        rows.append(dict(example=example, action=action, queue=queue, slot=k,
                         q_before=q, arrivals=a, capacity=capacity,
                         linear_candidate=q+a-capacity, q_after=q_next,
                         idle=idle, served=capacity-idle))
        q = q_next
    return rows


def worked_examples(golden):
    one = golden.ONE_QUEUE
    rows = slot_rows(one["q0"], one["arrivals"], one["c"], "one_queue", "n/a", "A")
    backlogs, idles = rollout(one["q0"], one["arrivals"], one["c"])
    assert (backlogs, idles) == (one["backlogs"], one["idles"])
    one_result = dict(backlogs=backlogs, idles=idles, final_backlog=backlogs[-1],
                      linear_part=one["q0"]+sum(a-one["c"] for a in one["arrivals"]),
                      total_idle=sum(idles), total_arrivals=sum(one["arrivals"]),
                      total_served=sum(r["served"] for r in rows))
    cases = []
    for name, case in golden.TWO_QUEUE_CASES.items():
        cfg = case["cfg"]
        results = [two_queue_cost(action=action, **cfg) for action in ("Stay", "Switch")]
        assert tuple(cost for cost, _ in results) == case["costs"]
        assert tuple(idle for _, idle in results) == case["idles"]
        weighted = sum((2-j)*(sw-st) for j, (sw, st) in enumerate(zip(results[1][1], results[0][1])))
        assert results[1][0] - results[0][0] == weighted
        cases.append(dict(name=name, cfg=cfg, cost_stay=results[0][0], cost_switch=results[1][0],
                          delta=results[1][0]-results[0][0], weighted_idle_diff=weighted,
                          idle_stay=results[0][1], idle_switch=results[1][1]))
        for action in ("Stay", "Switch"):
            for l, queue in enumerate(("A", "B")):
                managed = cfg["u"] if (action == "Stay") == (queue == "A") else 0
                rows.extend(slot_rows(cfg["q0"][l], [b+managed for b in cfg[f"b{queue}"]],
                                      cfg[f"c{queue}"], name, action, queue))
    return rows, one_result, cases


def mean_path_illustration():
    paths = []
    expected = [Fraction(0), Fraction(0)]
    idle_expected = [[Fraction(0), Fraction(0)] for _ in range(2)]
    for background in product((1, 5), repeat=2):
        pair = [two_queue_cost((10, 0), [1, 1], list(background), 2, 3, 3, action)
                for action in ("Stay", "Switch")]
        paths.append(dict(bB=list(background), probability="1/4", stay=pair[0][0], switch=pair[1][0]))
        for a in range(2):
            expected[a] += Fraction(pair[a][0], 4)
            for j in range(2):
                idle_expected[a][j] += Fraction(pair[a][1][j], 4)
    mean_costs = [two_queue_cost((10, 0), [1, 1], [3, 3], 2, 3, 3, action)[0]
                  for action in ("Stay", "Switch")]
    delta = expected[1] - expected[0]
    weighted = sum((2-j)*(idle_expected[1][j]-idle_expected[0][j]) for j in range(2))
    assert expected == [Fraction(45, 2), Fraction(20)] and delta == weighted == Fraction(-5, 2)
    assert mean_costs == [20, 20]
    return dict(law="illustration only: B i.i.d. {1,5}, each probability 1/2; not canonical Markov law",
                paths=paths, expected_cost_stay=str(expected[0]), expected_cost_switch=str(expected[1]),
                delta=str(delta), weighted_idle_difference=str(weighted),
                mean_costs=mean_costs, mean_action="Stay", oracle_action="Switch",
                regret=str(expected[0]-min(expected)))


def plot_examples(out, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), layout="constrained")
    for col, (name, title) in enumerate((("dl010_no_idle", "No idle: costs 37 / 37"),
                                        ("dl010_with_idle", "Idle: costs 23 / 17"))):
        for action, marker in (("Stay", "o"), ("Switch", "s")):
            selected = [r for r in rows if r["example"] == name and r["action"] == action]
            totals = [sum(r["q_after"] for r in selected if r["slot"] == k) for k in range(2)]
            idles = [sum(r["idle"] for r in selected if r["slot"] == k) for k in range(2)]
            axes[0, col].plot((1, 2), totals, marker=marker, label=action)
            axes[1, col].plot((0, 1), idles, marker=marker, label=action)
        axes[0, col].set(title=title, xlabel="Cost index k (end of slot)", ylabel="Total backlog (packets)", xticks=(1, 2))
        axes[1, col].set(xlabel="Slot j", ylabel="Unused capacity (packets / slot)", xticks=(0, 1))
        for ax in axes[:, col]:
            ax.grid(alpha=0.3)
            ax.legend()
    fig.savefig(out / "queue_comparison.png", dpi=160)
    plt.close(fig)


def report(result, rows):
    grid, tests = result["grid"], result["tests"]
    text = ["# L1.2 — kết quả chạy và đo", "", f"Lần chạy: {result['run_time_asia_saigon']}.", "",
            "Tác giả: **Doan Van Tai**. Thực hiện theo hai tài liệu L1.2 được cung cấp; experiment card lập trước khi chạy.",
            "Kết quả là verification F1/D13 trên toy grid; không là evidence mạng hoặc record tác giả tự làm.", "",
            "## Kiểm thử và vét cạn", "",
            f"- Bộ L1.2: **{tests['lesson']['passed']}/{tests['lesson']['total']} đạt**.",
            f"- Toàn repo: **{tests['full_suite']['passed']}/{tests['full_suite']['total']} đạt**.",
            f"- Lưới H=2: **{grid['configurations']:,} cấu hình**, **{grid['identity_violations']} vi phạm** đẳng thức hiệu cost.",
            f"- Không idle dưới cả hai action: **{grid['no_idle_pairs']:,} cấu hình** "
            f"({100*grid['no_idle_pairs']/grid['configurations']:.2f}%); **{grid['no_idle_cost_violations']} sai khác cost**.",
            f"- u=0: **{grid['zero_action_pairs']:,} cấu hình**; kiểm bằng nhau về cost và idle trong test zero-action.",
            f"- Đối chiếu cost và idle từng action với verify_dl010.py trên toàn lưới: **{grid['reference_mismatches']} sai khác**.",
            "- Đây là số cấu hình/path không idle, chưa phải tỉ lệ state thuộc vùng bảo toàn của lưới D ở L1.8.", "",
            "## Một queue — bài tính mẫu", "",
            "| Slot | q trước | Arrivals | q+A−c | q sau | Idle | Phục vụ |", "|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        if row["example"] == "one_queue":
            text.append("| " + " | ".join(str(row[key]) for key in
                        ("slot", "q_before", "arrivals", "linear_candidate", "q_after", "idle", "served")) + " |")
    one = result["one_queue"]
    text.extend(["", f"q_cuối = phần tuyến tính {one['linear_part']} + idle {one['total_idle']} = {one['final_backlog']}.",
                 f"Tổng đến {one['total_arrivals']} − tổng phục vụ {one['total_served']} = −1 = q_cuối 3 − q₀ 4.", "",
                 "## Hai queue — cost đo từ q₁…q_H", "",
                 "Đơn vị: packet·slot với dt=1. Δ=C(Switch)−C(Stay); c_sw=0.", "",
                 "| Ví dụ | Stay | Switch | Δ | Idle Stay | Idle Switch | Hiệu idle có trọng số |",
                 "|---|---:|---:|---:|---|---|---:|"])
    for case in result["two_queue_examples"]:
        text.append(f"| {case['name']} | {case['cost_stay']} | {case['cost_switch']} | {case['delta']} | "
                    f"{case['idle_stay']} | {case['idle_switch']} | {case['weighted_idle_diff']} |")
    text.extend(["", "Chi tiết A/B từng slot nằm trong [slot_tables.csv](slot_tables.csv).", "",
                 "![Backlog và capacity bỏ phí](queue_comparison.png)", "",
                 "## Bốn bug giả — lần chạy trong subprocess riêng", "",
                 "| Mutant | Bug | Test đỏ | Test xanh |", "|---|---|---:|---:|"])
    for name, mutant in result["mutations"].items():
        text.append(f"| {name} | {mutant['description']} | {mutant['failed']}/{mutant['total']} | {mutant['passed']} |")
    for name, mutant in result["mutations"].items():
        text.extend(["", f"**{name}** bắt bởi: " + ", ".join(f"`{test}`" for test in mutant["failed_tests"]) + "."])
    text.extend(["", "B1 vẫn qua hai đẳng thức/bảo toàn vì idle được đổi nhất quán với recurrence khác; "
                 "golden và complementarity phát hiện sai ngữ nghĩa. B2 chỉ bị ba golden cost tuyệt đối bắt: "
                 "cộng q₀ là hằng số chung nên mọi phép trừ che được lỗi.", "",
                 "## Minh họa đường trung bình (Part 1 §9.2)", "",
                 "B i.i.d. mỗi slot là 1 hoặc 5, mỗi giá trị xác suất 1/2; không phải law Markov của ví dụ chuẩn.",
                 "Liệt kê 4 path bằng Fraction: J(Stay)=45/2=22,5; J(Switch)=20; Δ=−5/2=−2,5.",
                 "Mean rollout cho 20/20, hoà chọn Stay; regret thật=5/2=2,5. Hiệu idle kỳ vọng có trọng số=−5/2.", "",
                 "## Provenance, phạm vi và cách tái chạy", "",
                 "Ba hàm nằm ở `experiments/lessons/l1_2_queue.py`; 11 test ở `tests/test_l1_2_queue.py`. "
                 "Đáp án golden trong `tests/golden_phase1.py` được ghi từ tài liệu ngày 09/10/2026, "
                 "không phải bài tính tay độc lập của Doan Van Tai. Đối chiếu hai implementation chưa đủ để gọi là independent review.",
                 "G1, V3/V10/V11 và HOLD Phase 4 giữ nguyên. Chưa kiểm mọi H, mạng thật, practical gain, novelty, "
                 "hay toàn bộ pipeline Phase 3/A01. Plant Phase 3 vẫn cần golden do tác giả tự tính.", "",
                 f"Thời gian wall-clock toàn runner: {result['elapsed_seconds']:.3f} s; "
                 "bao gồm pytest, mutation, exact enumeration và tạo hình. Không là benchmark mạng.",
                 f"Python {result['environment']['python']}; pytest {result['environment']['pytest']}. "
                 "SHA-256 source và commit nền nằm trong `results.json`.", "",
                 "```bash", ".venv/bin/python -m experiments.lessons.run_l1_2",
                 ".venv/bin/python -m pytest -q", "```", "",
                 "Có thể dùng `--output-dir /tmp/l1_2-rerun` để lưu lần chạy khác; output mặc định được ghi lại khi tái chạy.", "",
                 "| File | Nội dung |", "|---|---|",
                 "| [results.json](results.json) | Metrics, ví dụ, test/mutation counts, thời gian, provenance/hash |",
                 "| [grid_results.csv](grid_results.csv) | Toàn bộ 5.832 cấu hình, cost/idle, residual và đối chiếu |",
                 "| [slot_tables.csv](slot_tables.csv) | 46 dòng: một queue 6 slot + 5 ví dụ × 2 action × 2 queue × 2 slot |",
                 "| [lesson.txt](lesson.txt), [full_suite.txt](full_suite.txt) | stdout/stderr pytest thật; JUnit tương ứng *.xml |",
                 "| B1.txt…B4.txt, B1.xml…B4.xml | Test đỏ/xanh và lỗi của từng mutant; lỗi là có chủ đích |",
                 "| [reference_dl010.json](reference_dl010.json) | Chạy lại verify(): conservation và Markov/Jensen; phạm vi khác ví dụ i.i.d. |",
                 "| [queue_comparison.png](queue_comparison.png) | Hình từ số đo backlog/idle của hai ví dụ DL-010 |", ""])
    return "\n".join(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "notes/verification/l1_2")
    out = parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    golden = load_module("golden_phase1", ROOT / "tests/golden_phase1.py")
    reference = load_module("reference_dl010", ROOT / "notes/verification/verify_dl010.py")
    lesson = pytest_run(out, "lesson")
    full = pytest_run(out, "full_suite")
    for name, test in (("lesson", lesson), ("full_suite", full)):
        if test["returncode"] != 0 or test["errors"] or test["skipped"]:
            raise RuntimeError(f"{name} failed; see {out / test['log']}")
    assert lesson["total"] == lesson["passed"] == 11
    print(f"L1.2 tests: {lesson['passed']}/{lesson['total']} passed", flush=True)
    print(f"Repository tests: {full['passed']}/{full['total']} passed", flush=True)
    grid_rows, grid = enumerate_grid(reference)
    write_csv(out / "grid_results.csv", grid_rows)
    write_json(out / "grid_summary.json", grid)
    assert grid["configurations"] == 5832 and grid["no_idle_pairs"] == 2048
    assert not grid["violating_configurations"], grid["violating_configurations"][:1]
    print(f"Grid: {grid['configurations']} configurations, {grid['no_idle_pairs']} no-idle, "
          f"{grid['identity_violations']} identity violations, {grid['reference_mismatches']} reference mismatches", flush=True)
    ref_result = reference.verify()
    assert (ref_result["conservation_action_pairs"], ref_result["no_idle_pairs"]) == (5832, 2048)
    write_json(out / "reference_dl010.json", ref_result)
    slots, one, examples = worked_examples(golden)
    write_csv(out / "slot_tables.csv", slots)
    mutations = {}
    for name, (description, mutation) in MUTANTS.items():
        measured = pytest_run(out, name, mutation)
        assert measured["returncode"] == 1 and measured["failed"] > 0
        assert measured["total"] == 11 and not measured["errors"] and not measured["skipped"]
        mutations[name] = dict(description=description, **measured)
        print(f"{name}: {measured['failed']}/11 tests detected the bug", flush=True)
    illustration = mean_path_illustration()
    plot_examples(out, slots)
    sources = ["experiments/lessons/l1_2_queue.py", "experiments/lessons/run_l1_2.py",
               "tests/golden_phase1.py", "tests/test_l1_2_queue.py", "notes/verification/verify_dl010.py",
               "notes/lessons/L1.2_experiment_card.md"]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    import pytest
    result = dict(run_time_asia_saigon=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(),
                  environment=dict(python=platform.python_version(), pytest=pytest.__version__),
                  base_commit=commit, source_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                  golden_provenance=golden.PROVENANCE, grid=grid, tests=dict(lesson=lesson, full_suite=full),
                  one_queue=one, two_queue_examples=examples, mutations=mutations,
                  mean_path_illustration=illustration, elapsed_seconds=time.perf_counter()-started,
                  scope="finite toy-grid verification, not network evidence or author understanding; G1 and V3/V10/V11 unchanged")
    write_json(out / "results.json", result)
    (out / "report.md").write_text(report(result, slots), encoding="utf-8")
    print("\nExample                 Stay  Switch  Delta")
    for case in examples:
        print(f"{case['name']:27} {case['cost_stay']:4}  {case['cost_switch']:6}  {case['delta']:5}")
    print("Mean-path illustration: true J=22.5/20; mean rollout=20/20; regret=2.5")
    print(f"Report: {out / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
