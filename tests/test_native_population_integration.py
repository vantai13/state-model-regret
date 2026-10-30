from fractions import Fraction as F

from experiments.R3R_08_population_numerics import law_cache, population
from experiments.R3R_11_native_population.worker import configure_engine


def test_native_evaluator_full_population_keeps_the_reference_estimator(tmp_path, monkeypatch):
    spec = ['NATIVE_REFERENCE_TOY', '7', '8', '1/10', '1/2', '1/40', 1, 16, '0']
    reference = population.evaluate(spec, tmp_path/'reference')
    # Restore the process-global injection after this isolated integration check.
    monkeypatch.setattr(law_cache, 'FastLaw', law_cache.FastLaw)
    configure_engine()
    actual = population.evaluate(spec, tmp_path/'native')
    assert actual['S1_route'] == reference['S1_route']
    assert actual['validity_errors'] == reference['validity_errors']
    for key in population.CONTRASTS:
        bound = F(actual['contrast_error'][key]) + F(reference['contrast_error'][key])
        assert abs(F(actual[key])-F(reference[key])) <= bound
    assert abs(F(actual['Cref'])-F(reference['Cref'])) <= F(actual['cost_error']['11'])+F(reference['cost_error']['11'])
