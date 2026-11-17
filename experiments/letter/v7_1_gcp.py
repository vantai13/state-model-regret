"""Doan Van Tai — V7-1 GCP extraction, followed by local scoring.

AI-assisted implementation of V7_1_gcp_brief.md. The pilot extractor and
statistics are imported unchanged. Only extraction uses process workers.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
from multiprocessing import get_context
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

import numpy as np
import scipy

from experiments.letter import v7_1_rule as R

OUT = R.OUT / "full"
BRIEF = R.ROOT / "notes/ops/codex/V7_1_gcp_brief.md"
MAX_WORKERS = 16


def verify_workers(workers):
    if not 1 <= workers <= MAX_WORKERS:
        raise ValueError("V7-1 permits 1..16 workers")


def verify_source(manifest):
    changed = [name for name, digest in manifest["sha256"].items()
               if R.sha(R.ROOT / name) != digest]
    network = R.E.T.data_root() / manifest["network"]["relative_path"]
    if R.sha(network) != manifest["network"]["sha256"]:
        changed.append("SMR_SNDLIB/geant.txt")
    if changed:
        raise RuntimeError(f"input SHA256 mismatch: {changed}")
    if not R.ctmc.l72_unlocked():
        raise RuntimeError("L7.2 amplitude lock is not valid")
    return dict(status="PASS", files=len(manifest["sha256"])+1, changed=[])


def prepare(out=OUT):
    if out.exists():
        raise FileExistsError("full output already exists; do not resume or rerun")
    for path in (BRIEF, R.OUT / "CARD_V7_1.md"):
        saved = subprocess.check_output(["git", "show", "HEAD:"+str(path.relative_to(R.ROOT))], cwd=R.ROOT)
        if saved != path.read_bytes():
            raise RuntimeError(f"{path.name} differs from HEAD")
    pilot_manifest = json.loads((R.OUT / "input_manifest.json").read_text())
    for name, digest in pilot_manifest["sha256"].items():
        if R.sha(R.ROOT / name) != digest:
            raise RuntimeError(f"pilot input changed: {name}")
    pilot_verification = json.loads((R.OUT / "verification.json").read_text())
    for name, digest in pilot_verification["artifacts_sha256"].items():
        if R.sha(R.ROOT / name) != digest:
            raise RuntimeError(f"pilot artifact changed: {name}")
    lock = json.loads(R.ctmc.LOCKS_L72.read_text())
    for name, digest in lock["files"].items():
        if R.sha(R.ROOT / name) != digest:
            raise RuntimeError(f"L7.2 lock mismatch: {name}")
    paths = R.input_paths() + [Path(__file__), BRIEF, R.ctmc.LOCKS_L72,
                               R.ROOT / "experiments/ext_validity/packet.py",
                               R.ROOT / "experiments/explore_ctmc/env.sh",
                               R.ROOT / "tests/test_letter_v7_1_gcp.py",
                               R.ROOT / "experiments/letter/v7_1_gcp_pipeline.sh",
                               R.OUT / "pilot.json", R.OUT / "input_manifest.json",
                               R.OUT / "verification.json"]
    paths += [R.ROOT / name for name in lock["files"]]
    paths += sorted((R.OUT / "extracted").glob("*"))
    for directory in ("letter", "ext_validity", "explore_ctmc"):
        paths.append(R.ROOT / "experiments" / directory / "__init__.py")
    network = R.E.T.data_root() / "sndlib-networks-native/geant.txt"
    manifest = dict(owner="Doan Van Tai", git_head=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=R.ROOT, text=True).strip(),
        sha256={str(p.relative_to(R.ROOT)): R.sha(p) for p in sorted(set(paths))},
        network=dict(relative_path="sndlib-networks-native/geant.txt", sha256=R.sha(network)),
        scope="before full extraction; reuse the two verified pilot artifacts only",
        max_workers=MAX_WORKERS)
    verify_source(manifest)
    (out / "extracted").mkdir(parents=True)
    shutil.copy2(R.OUT / "pilot.json", out / "pilot.json")
    for path in sorted((R.OUT / "extracted").glob("*")):
        shutil.copy2(path, out / "extracted" / path.name)
    shutil.copy2(R.OUT / "REPORT_V7_1.md", out / "pilot_report_snapshot.md")
    shutil.copy2(R.OUT / "summary.json", out / "pilot_summary_snapshot.json")
    R.write_json(out / "source_manifest.json", manifest)
    print(json.dumps(dict(stage="prepare", status="PASS", files=len(manifest["sha256"])+1)), flush=True)


def worker(task):
    kind, prefix, argument, out = task
    if kind == "CTMC":
        record, arrays = R.extract_ctmc(json.loads(Path(argument).read_text()))
    else:
        spec, training, sub, chunk = argument
        record, arrays = R.extract_geant_chunk(spec, training, sub, chunk)
    R.save_extraction(out, prefix, record, arrays)
    return dict(prefix=prefix, cpu_s=record["cpu_s"], wall_s=record["wall_s"],
                worker_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def extract(out=OUT, workers=MAX_WORKERS):
    verify_workers(workers)
    manifest = json.loads((out / "source_manifest.json").read_text())
    verify_source(manifest)
    if (out / "input_manifest.json").exists():
        raise FileExistsError("extraction already started; no resume or rerun")
    start, wall = time.process_time(), time.perf_counter()
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    R.write_json(out / "input_manifest.json", manifest)
    paths = sorted((R.ROOT / "results/letter/w1b/raw").glob("*.json"))
    if len(paths) != 93:
        raise ValueError("expected 93 CTMC regimes")
    tasks = [("CTMC", "CTMC_"+p.stem, str(p), out) for p in sorted(
        paths, key=lambda p: -R.ctmc_work(json.loads(p.read_text())))]
    specs, training = R.geant_inputs()
    for sub in ("e4", "e4b"):
        for spec in specs:
            for chunk in range(10):
                prefix = f"GEANT_{sub}_{spec['id']}_{chunk:02d}"
                tasks.append(("GEANT", prefix, (spec, training[spec["id"]], sub, chunk), out))
    reused, pending = [], []
    for task in tasks:
        if R.read_extraction(out, task[1]) is None:
            pending.append(task)
        else:
            reused.append(task[1])
    if len(tasks) != 433 or len(reused) != 2:
        raise ValueError("expected 433 extractions, exactly two from the verified pilot")
    timings = []
    # Precompile the unchanged native predictor once, before process workers.
    R.E.T.native()
    pool = ProcessPoolExecutor(max_workers=workers, mp_context=get_context("spawn"))
    try:
        futures = [pool.submit(worker, task) for task in pending]
        for future in as_completed(futures):
            timing = future.result()
            timings.append(timing)
            print(json.dumps(dict(event="extracted", completed=len(timings), total=len(pending), **timing)), flush=True)
    except BaseException:
        pool.terminate_workers()
        raise
    else:
        pool.shutdown(wait=True)
    scales = [R.read_extraction(out, "CTMC_"+p.stem)["scale"] for p in paths]
    for sub in ("e4", "e4b"):
        for spec in specs:
            # Every chunk is already present: geant_scale only reads arrays.
            scales.append(R.geant_scale(out, spec, training[spec["id"]], sub))
    rows = R.load_cells(scales)
    R.write_csv(out / "regime_scales.csv", scales)
    R.write_csv(out / "cells.csv", rows)
    records = [json.loads(p.read_text()) for p in sorted((out / "extracted").glob("*.json"))]
    checks = dict(ctmc_relative_checks=[dict(regime=e["scale"]["regime"], **c)
                  for e in records if "scale" in e for c in e["checks"]],
                  geant_chunks=[e for e in records if "scale" not in e],
                  ctmc_regimes=sum("scale" in e for e in records),
                  geant_chunk_count=sum("scale" not in e for e in records))
    if (checks["ctmc_regimes"], checks["geant_chunk_count"]) != (93, 340):
        raise ValueError("extraction population mismatch")
    R.write_json(out / "extraction_checks.json", checks)
    source_check = verify_source(manifest)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    compute = dict(workers=workers, compute_location="gcp", reused_pilot_artifacts=reused,
                   new_extractions=len(timings), total_extractions=len(records),
                   new_worker_cpu_s=sum(t["cpu_s"] for t in timings),
                   extraction_cpu_s_including_reused_pilot=sum(e["cpu_s"] for e in records),
                   extraction_wall_sum_s_including_reused_pilot=sum(e["wall_s"] for e in records),
                   gcp_main_cpu_s=time.process_time()-start,
                   gcp_child_cpu_s=children.ru_utime+children.ru_stime-child_before.ru_utime-child_before.ru_stime,
                   gcp_elapsed_wall_s=time.perf_counter()-wall,
                   worker_max_peak_rss_kib=max(t["worker_peak_rss_kib"] for t in timings),
                   parent_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   memory_scope="maximum single-worker RSS, not simultaneous total VM memory",
                   environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                       variables={k:os.environ.get(k) for k in ("NPY_DISABLE_CPU_FEATURES", "OPENBLAS_CORETYPE",
                                                              "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}))
    R.write_json(out / "extraction_complete.json", dict(owner="Doan Van Tai", status="EXTRACTED_NOT_SCORED",
                 cells=dict(Counter(r["dataset"] for r in rows)), scales=len(scales),
                 input_hash_verification=source_check, compute=compute))
    artifact_paths = sorted(p for p in out.rglob("*") if p.is_file() and p.suffix != ".log")
    R.write_json(out / "raw_manifest.json", dict(owner="Doan Van Tai", sha256={
        str(p.relative_to(out)): R.sha(p) for p in artifact_paths}))
    print(json.dumps(dict(stage="extract", status="EXTRACTED_NOT_SCORED", compute=compute)), flush=True)


def verify_raw(out):
    manifest = json.loads((out / "raw_manifest.json").read_text())
    changed = [name for name, digest in manifest["sha256"].items() if R.sha(out / name) != digest]
    if changed:
        raise RuntimeError(f"raw artifact SHA256 mismatch: {changed}")
    return dict(status="PASS", files=len(manifest["sha256"]), changed=[])


def verify_raw_commit(out, raw_commit):
    if not raw_commit:
        raise ValueError("score requires the pushed extraction commit")
    for ref in ("HEAD", "@{upstream}"):
        subprocess.run(["git", "merge-base", "--is-ancestor", raw_commit, ref], cwd=R.ROOT, check=True)
    for name in ("cells.csv", "regime_scales.csv", "raw_manifest.json"):
        path = out / name
        saved = subprocess.check_output(["git", "show", raw_commit+":"+str(path.relative_to(R.ROOT))], cwd=R.ROOT)
        if saved != path.read_bytes():
            raise RuntimeError(f"{name} differs from pushed extraction commit")


def score(out=OUT, raw_commit=None):
    verify_raw_commit(out, raw_commit)
    raw_check = verify_raw(out)
    source = json.loads((out / "source_manifest.json").read_text())
    verify_source(source)
    if (out / "summary.json").exists():
        raise FileExistsError("score already exists; no automatic rerun")
    start, wall = time.process_time(), time.perf_counter()
    with (out / "cells.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["Y"] = int(row["Y"])
        for key in ("tau_s", "h_s", "regret_fresh_pct", "regret_stale_pct", "C_ref",
                    "M_hat", "Q90", "s_hat", "T_int_s", "h_star_s", "h_star_Tint", *R.PREDICTORS):
            row[key] = float(row[key])
    if Counter(r["dataset"] for r in rows) != {"CTMC":3255, "GEANT":612}:
        raise ValueError("incomplete cell table")
    with (out / "regime_scales.csv").open() as handle:
        scales = list(csv.DictReader(handle))
    for scale in scales:
        for key in ("M_hat", "Q90", "s_hat", "T_int_s", "h_star_s", "h_star_Tint", "max_relative_error"):
            scale[key] = float(scale[key])
    extraction = json.loads((out / "extraction_complete.json").read_text())
    compute = dict(extraction["compute"], raw_commit_before_scoring=raw_commit)
    summary = R.summarize(out, rows, scales, compute)
    subgroups = []
    for dataset, factor in (("CTMC", "family"), ("GEANT", "seed")):
        for value in sorted({r[factor] for r in rows if r["dataset"] == dataset}):
            group = [r for r in rows if r["dataset"] == dataset and r[factor] == value]
            subgroups.append(dict(dataset=dataset, factor=factor, value=value, cells=len(group),
                Y1=sum(r["Y"] for r in group), **{f"auc_{p}":R.auc([r["Y"] for r in group],
                                              [r[p] for r in group]) for p in R.PREDICTORS}))
    R.write_csv(out / "subgroups.csv", subgroups)
    R.binned_figure(out, rows)
    summary["input_hash_verification"] = verify_source(source)
    summary["raw_hash_verification"] = raw_check
    summary["artifact_directory"] = str(out.relative_to(R.ROOT))
    summary["deviations"] = [
        "M0 fluid gaps are absent from E4/E4b raw; the unchanged pilot code reconstructs the original predictor inputs.",
        "A new wrapper separates parallel GCP extraction from local scoring; original source files and card remain unchanged.",
        "The two verified pilot extractions are reused, as planned in the pilot handoff; 431 extractions are new."]
    compute.update(local_score_cpu_s=time.process_time()-start, local_score_wall_s=time.perf_counter()-wall,
                   local_score_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    R.write_json(out / "summary.json", summary)
    R.report(out, summary, scales)
    report = out / "REPORT_V7_1.md"
    text = report.read_text().replace(
        "Không commit, không SSH, không sửa card/file cũ/paper, không chạm V7-2/V7-3. Các test/log thực thi được ghi riêng trong thư mục này.",
        "Thực hiện brief GCP tại HEAD: extraction detached, tối đa 16 workers; tải về và đối chiếu SHA256 hai phía; commit và push bảng trước scoring local. Không thay trạng thái/cấu hình VM, card, code pilot hoặc paper; không chạm V7-2/V7-3. Log/checksum/receipt ở thư mục này.")
    report.write_text(text)
    print(json.dumps(dict(stage="score", verdict=summary["verdict"], compute=compute)), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "extract", "score"), required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--raw-commit")
    args = parser.parse_args()
    if args.stage == "prepare":
        prepare(args.out)
    elif args.stage == "extract":
        extract(args.out, args.workers)
    else:
        score(args.out, args.raw_commit)


if __name__ == "__main__":
    main()
