"""Doan Van Tai — explicit versioned evaluator injection before any computation.

The law and profile caches retain their original parameter/source/SHA checks.
Only the posterior precision fallback changes. All original validity, physical
cost, infinite-law certificate and numerical thresholds remain authoritative.
"""
from experiments.R3R_08_population_numerics import law_cache
from experiments.R3R_08_population_numerics.worker import main
from experiments.R3R_10_interval_evaluation.evaluator import NativePosteriorFastLaw


def configure_engine():
    law_cache.FastLaw = NativePosteriorFastLaw


if __name__ == '__main__':
    configure_engine()
    raise SystemExit(main())
