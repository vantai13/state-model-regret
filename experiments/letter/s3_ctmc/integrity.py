"""Doan Van Tai — engine-free, portable S3 file integrity and exclusive I/O."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODE = ROOT / "experiments/letter/s3_ctmc"
OUT = ROOT / "results/letter/sweep/s3"
CARD = OUT / "CARD_S3.md"
LOCK = OUT / "lock.json"
NAMESPACE = "s3-ctmc-confirmation-v1"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def csv_write(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError("empty CSV without schema")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify_lock(lock_path=LOCK, expected_sha=None, root=ROOT):
    """No sampler, estimator, evaluator or truth input is imported here."""
    lock_path, root = Path(lock_path), Path(root).resolve()
    digest = sha(lock_path)
    if expected_sha is not None and digest != expected_sha:
        raise ValueError("S3 lock SHA256 differs from the launch pin")
    lock = read(lock_path)
    if lock.get("namespace") != NAMESPACE or lock.get("state") != "LOCKED_BEFORE_TRUTH":
        raise ValueError("S3 lock is not locked")
    files = lock["files"]
    if not files:
        raise ValueError("empty S3 lock")
    for name, expected in files.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError("lock path escapes repository")
        if sha(path) != expected:
            raise ValueError("S3 locked input changed: " + name)
    # Adding an unlocked Python file can change import resolution, too.
    code_path = root / "experiments/letter/s3_ctmc"
    actual_code = {str(p.relative_to(root)) for p in code_path.rglob("*")
                   if p.is_file() and p.suffix in (".py", ".sh", ".md")}
    if not actual_code <= set(files):
        raise ValueError("unlocked S3 code files")
    return dict(status="PASS", lock_sha256=digest, files=len(files))
