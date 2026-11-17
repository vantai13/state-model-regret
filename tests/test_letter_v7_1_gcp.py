"""Doan Van Tai — guards for the GCP/scoring stage boundary."""
import json

import pytest

from experiments.letter import v7_1_gcp as G


@pytest.mark.parametrize("workers", [0, -1, 17, 32])
def test_worker_limit(workers):
    with pytest.raises(ValueError, match="1..16"):
        G.verify_workers(workers)


def test_score_requires_pushed_commit_before_inputs(tmp_path):
    with pytest.raises(ValueError, match="pushed extraction commit"):
        G.score(tmp_path)
    assert not list(tmp_path.iterdir())


def test_raw_manifest_detects_changed_table(tmp_path):
    table = tmp_path / "cells.csv"
    table.write_text("old table\n")
    (tmp_path / "raw_manifest.json").write_text(json.dumps({"sha256":{"cells.csv":G.R.sha(table)}}))
    assert G.verify_raw(tmp_path)["status"] == "PASS"
    table.write_text("changed table\n")
    with pytest.raises(RuntimeError, match="raw artifact SHA256 mismatch"):
        G.verify_raw(tmp_path)


def test_prepare_refuses_existing_output_without_touching_it(tmp_path):
    with pytest.raises(FileExistsError, match="do not resume or rerun"):
        G.prepare(tmp_path)
    assert not list(tmp_path.iterdir())
