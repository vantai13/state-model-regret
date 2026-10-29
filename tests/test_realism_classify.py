"""Scientific failure modes: missing evidence, incompatible anchors, dedup design."""
import pytest
from experiments.R3R_04_realism.classify import classify


def test_missing_evidence_is_not_in_or_out():
    assert classify(None, [{'name': 'CV', 'allowed_tau_s': [1, 2]}])['label'] == 'UNSOURCED'
    x = classify([1, 3], [{'name': 'CV', 'allowed_tau_s': None}])
    assert x['label'] == 'UNSOURCED' and x['missing'] == ['CV']


def test_individual_feasibility_with_different_anchors_does_not_produce_in():
    c = [{'name': 'CV', 'allowed_tau_s': [1, 2]}, {'name': 'delay', 'allowed_tau_s': [3, 4]}]
    assert classify([1, 4], c)['label'] == 'OUT'
    c[0]['relaxed_tau_s'] = [1, 3]
    assert classify([1, 4], c)['label'] == 'EDGE'


def test_at_most_one_deviation_and_tau_not_relaxed():
    c = [{'name': n, 'allowed_tau_s': [5, 6], 'relaxed_tau_s': [1, 6]} for n in ['CV', 'delay']]
    assert classify([1, 2], c)['label'] == 'OUT'
    assert classify([1, 2], c, k=2)['label'] == 'EDGE'
    assert classify([5, 6], c)['label'] == 'IN'
    assert classify([7, 8], c, k=2)['label'] == 'OUT'


def test_invalid_and_vacuous_envelopes_rejected():
    with pytest.raises(ValueError): classify([1, 2], [])
    with pytest.raises(ValueError): classify([2, 1], [{'name': 'CV', 'allowed_tau_s': [1, 2]}])
