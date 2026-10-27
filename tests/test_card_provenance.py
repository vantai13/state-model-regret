"""Doan Van Tai — exact bytes, draft rejection and two distinct commits."""
import json

import pytest

from tests.test_engine_guard import isolated_repo, commit, git
from tests.card_git_fixture import make_card, make_lock
from experiments.A03_card.provenance import CARD, verify_receipt


def test_committed_draft_never_unlocks_A01(isolated_repo):
    repo = isolated_repo
    make_card(repo, status='DRAFT')
    commit(repo, 'fixture draft')
    make_lock(repo, git(repo, 'rev-parse', 'HEAD'))
    commit(repo, 'fixture receipt cannot bless draft')
    with pytest.raises(PermissionError, match='DRAFT'):
        verify_receipt(repo)


def test_frozen_card_needs_a_later_clean_matching_receipt(isolated_repo):
    repo = isolated_repo
    card = make_card(repo)
    commit(repo, 'fixture frozen card')
    first = git(repo, 'rev-parse', 'HEAD')
    with pytest.raises(PermissionError):
        verify_receipt(repo)
    lock = make_lock(repo, first)
    commit(repo, 'fixture receipt')
    r = verify_receipt(repo)
    assert r['prediction_card_commit'] == first
    assert r['prediction_lock_commit'] != first
    data = json.loads(lock.read_text())
    data['sha256'] = '0' * 64
    lock.write_text(json.dumps(data))
    commit(repo, 'fixture corrupted receipt')
    with pytest.raises(PermissionError):
        verify_receipt(repo)


def test_committed_card_edit_after_freeze_fails_hash_check(isolated_repo):
    repo = isolated_repo
    card = make_card(repo)
    commit(repo, 'fixture card')
    make_lock(repo, git(repo, 'rev-parse', 'HEAD'))
    commit(repo, 'fixture receipt')
    card.write_text(card.read_text() + '\nAn amendment changes the full-file hash\n')
    commit(repo, 'fixture amended card')
    with pytest.raises(PermissionError, match='differs'):
        verify_receipt(repo)


def test_registered_tag_must_exist_and_point_to_receipt(isolated_repo):
    repo = isolated_repo
    make_card(repo)
    commit(repo, 'fixture card')
    make_lock(repo, git(repo, 'rev-parse', 'HEAD'))
    commit(repo, 'fixture receipt')
    assert verify_receipt(repo)['prediction_tag'] == 'fixture-a03'
    git(repo, 'tag', '-d', 'fixture-a03')
    with pytest.raises(PermissionError, match='tag'):
        verify_receipt(repo)
