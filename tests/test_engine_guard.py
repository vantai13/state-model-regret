"""Doan Van Tai — exercise guards only; no grid D/J/gaps are evaluated."""
import json
import subprocess

import pytest

from experiments.A00_engine.guard import CARD, FREEZE, GRID_PATH, guard
from tests.card_git_fixture import make_card, make_lock


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def commit(repo, name):
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Doan Van Tai', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', name)
    from experiments.A03_card.provenance import LOCK
    if (repo / LOCK).exists():
        if subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', 'refs/tags/fixture-a03'],
                          capture_output=True).returncode:
            git(repo, '-c', 'user.name=Doan Van Tai', '-c', 'user.email=fixture@example.invalid',
                'tag', '-a', 'fixture-a03', '-m', 'Synthetic receipt tag')


@pytest.fixture
def isolated_repo(tmp_path):
    git(tmp_path, 'init', '-q', '-b', 'main')
    (tmp_path / 'README').write_text('Synthetic guard fixture; not a research prediction\n')
    commit(tmp_path, 'fixture baseline')
    return tmp_path


def test_all_58_grid_ids_denied_without_flags():
    grid = json.loads(GRID_PATH.read_text())
    ids = [c['id'] for k in ('main', 'heldout', 'controls', 'probes') for c in grid[k]]
    assert len(ids) == 58
    for cid in ids:
        with pytest.raises(PermissionError):
            guard(cid)
    assert guard('TOY')['scope'] == 'toy'


def test_card_must_be_clean_and_in_HEAD(isolated_repo):
    repo = isolated_repo
    with pytest.raises(PermissionError):
        guard('M01', allow_grid=True, purpose='A01', repo=repo)
    path = make_card(repo)
    with pytest.raises(PermissionError):
        guard('M01', allow_grid=True, purpose='A01', repo=repo)
    commit(repo, 'fixture card')
    card_commit = git(repo, 'rev-parse', 'HEAD')
    make_lock(repo, card_commit)
    commit(repo, 'fixture receipt')
    receipt = guard('M01', allow_grid=True, purpose='A01', repo=repo)
    assert receipt['prediction_card_commit'] == card_commit
    path.write_text('dirty fixture\n')
    with pytest.raises(PermissionError):
        guard('M01', allow_grid=True, purpose='A01', repo=repo)


def test_heldout_needs_freeze_not_only_boolean_flag(isolated_repo):
    repo = isolated_repo
    card = make_card(repo)
    commit(repo, 'fixture card')
    make_lock(repo, git(repo, 'rev-parse', 'HEAD'))
    commit(repo, 'fixture receipt')
    for flags in ({}, {'allow_grid': True, 'purpose': 'A01', 'allow_heldout': True},
                  {'allow_grid': True, 'purpose': 'A05-T', 'allow_heldout': True}):
        with pytest.raises(PermissionError):
            guard('R01', repo=repo, **flags)
    (repo / FREEZE).parent.mkdir(parents=True, exist_ok=True)
    (repo / FREEZE).write_text('Fixture A05-F\n')
    commit(repo, 'fixture freeze')
    r = guard('R01', allow_grid=True, allow_heldout=True, purpose='A05-T', repo=repo)
    assert r['freeze_commit'] == git(repo, 'rev-parse', 'HEAD')
    card.write_text('Changed card after freeze\n')
    commit(repo, 'fixture changed card')
    with pytest.raises(PermissionError):
        guard('R01', allow_grid=True, allow_heldout=True, purpose='A05-T', repo=repo)


def test_evaluate_guard_runs_before_loading_cell_or_D(monkeypatch):
    from experiments.A00_engine import evaluate
    def forbidden(*args, **kwargs):
        raise AssertionError('load/D/cost must not be reached')
    monkeypatch.setattr(evaluate, 'load_cell', forbidden)
    for cid in ('M01', 'N01', 'P01', 'P02', 'R01'):
        with pytest.raises(PermissionError):
            evaluate.evaluate_cell(cid, 1)


def test_A01_cannot_use_other_main_cell(isolated_repo):
    with pytest.raises(PermissionError):
        guard('M31', allow_grid=True, purpose='A01', repo=isolated_repo)
