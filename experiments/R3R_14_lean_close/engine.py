"""Doan Van Tai — lean L3R.7 closure: thin, write-once wrapper around the native05 evaluator.

AI (Claude) theo ủy quyền (DL-095). The physical/numerical code is the native05 code, byte-identical to
experiments/R3R_11_native_population/prereg.json source_sha256; this module only (i) injects the same
NativePosteriorFastLaw, (ii) evaluates one registered calibration spec at one (K, ref), and (iii) writes
JSON safely (native05 lost two rows to a NumPy-bool serialisation error). No CF, no random sampling.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import resource
import time

import numpy as np


def configure():
    from experiments.R3R_08_population_numerics import law_cache
    from experiments.R3R_10_interval_evaluation.evaluator import NativePosteriorFastLaw
    law_cache.FastLaw = NativePosteriorFastLaw


def snap(value, step):
    """Nearest multiple of step, ties to the even multiple (card rounding_mode)."""
    return round(F(value) / F(step)) * F(step)


def round_rates(parameters, r):
    """Round lamA, lamB and u = 2*eta to multiples of r; kappa, h, c_sw unchanged. Returns card-style strings."""
    lamA, lamB, kappa, eta, h, c = parameters
    u = snap(2 * F(eta), r)
    return [str(snap(lamA, r)), str(snap(lamB, r)), str(F(kappa)), str(u / 2), str(F(h)), str(F(c))]


def _plain(x):
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return float(x)
    if isinstance(x, (F, np.longdouble)):
        return str(x)
    return x


def write_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(_plain(obj), indent=1) + '\n')
    if path.exists():
        tmp.unlink()
        raise FileExistsError(f'write-once result already exists: {path}')
    tmp.rename(path)


def cpu_seconds():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def evaluate_level(case_id, parameters, K, ref, cache):
    """One population evaluation; returns the native05 row plus CPU/wall of this call."""
    from experiments.R3R_08_population_numerics import population
    lamA, lamB, kappa, eta, h, c = parameters
    begin_cpu, begin_wall = cpu_seconds(), time.monotonic()
    row = population.evaluate((case_id, lamA, lamB, kappa, eta, h, ref, K, c), Path(cache))
    row = _plain(row)
    row['call_cpu_seconds'] = cpu_seconds() - begin_cpu
    row['call_wall_seconds'] = time.monotonic() - begin_wall
    return row
