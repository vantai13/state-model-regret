"""Doan Van Tai — CARD_W2 §A arrival-count estimator, with bounded RAM.

Modes have exact exponential holding times; each Poisson bin uses the exact
integrated intensity, including switches inside the bin.  Counts live in a
temporary memmap.  Chunk FFTs include cross-chunk pairs and implement the
global-mean, (n-k)-normalized autocovariance, without decimating telemetry.
"""
import hashlib
import math
from pathlib import Path
import tempfile

import numpy as np
from scipy.fft import irfft, next_fast_len, rfft

from experiments.letter import mmpp

BIN_WIDTH = .01
CHUNK_BINS = 262144


def simulate_counts(load, alpha, kappa, W, rng, destination, delta=BIN_WIDTH,
                    chunk_bins=CHUNK_BINS):
    """Fill complete bins; simulate and record the final partial bin separately."""
    if not (0 <= alpha <= load and kappa > 0 and W >= delta > 0):
        raise ValueError('invalid telemetry parameters')
    n = int(math.floor(W / delta))
    if len(destination) != n:
        raise ValueError('count buffer length mismatch')
    mode = int(rng.integers(0, 2))
    remaining = float(rng.exponential(kappa))
    digest = hashlib.sha256()
    switches = 0

    def integrate(edges):
        nonlocal mode, remaining, switches
        duration = float(edges[-1])
        ends, t = [0.], remaining
        initial = mode
        while t < duration:
            ends.append(t)
            t += float(rng.exponential(kappa))
        event_count = len(ends) - 1
        ends.append(duration)
        segments = np.asarray(ends)
        rates = load + alpha * (2 * ((initial + np.arange(len(segments)-1)) % 2) - 1)
        prefix = np.r_[0., np.cumsum(np.diff(segments) * rates)]
        indices = np.minimum(np.searchsorted(segments, edges, side='right')-1, len(rates)-1)
        cumulative = prefix[indices] + rates[indices] * (edges-segments[indices])
        intensity = np.maximum(0., np.diff(cumulative))
        mode = (initial + event_count) % 2
        remaining = t - duration
        switches += event_count
        return intensity

    for start in range(0, n, chunk_bins):
        size = min(chunk_bins, n-start)
        intensity = integrate(np.arange(size+1, dtype=float)*delta)
        counts = rng.poisson(intensity)
        if counts.max(initial=0) > np.iinfo(np.int32).max:
            raise OverflowError('bin count does not fit int32')
        destination[start:start+size] = counts
        digest.update(np.asarray(counts, dtype='<i4').tobytes())
    partial = max(0., W-n*delta)
    partial_count = int(rng.poisson(integrate(np.array([0., partial]))[0])) if partial > 0 else 0
    return dict(W=float(W), W_complete_bins=n*delta, delta=delta, n_bins=n,
                partial_bin_duration=partial, partial_bin_count=partial_count,
                partial_bin_used_in_estimate=False, mode_switches=switches,
                count_sha256_le_i4=digest.hexdigest(),
                count_storage='temporary int32 memmap; seed + count digest retained')


def autocovariances(counts, delta, max_lag, chunk_bins=CHUNK_BINS):
    """Exact pair coverage, FFT arithmetic; chunk boundaries are not discarded."""
    n = len(counts)
    lag = min(int(max_lag), n-1)
    if lag < 1:
        raise ValueError('at least two bins are required')
    mean_count = float(np.sum(counts, dtype=np.float64) / n)
    sums = np.zeros(lag+1)
    for start in range(0, n, chunk_bins):
        core_size = min(chunk_bins, n-start)
        right = min(n, start+core_size+lag)
        block = (np.asarray(counts[start:right], dtype=float)-mean_count)/delta
        core = block[:core_size]
        # Requested lags can exceed the last block's physical length. Pad
        # through lag+core_size so those queries cannot wrap into negative
        # lags of a short final chunk.
        fft_size = next_fast_len(max(lag+len(core), len(block)+len(core)-1))
        products = irfft(np.conj(rfft(core, fft_size))*rfft(block, fft_size), fft_size)
        sums += products[:lag+1]
    return sums / (n-np.arange(lag+1))


def estimate_path(load, managed_shift, alpha, kappa, T_int, rng, *,
                  W=None, kappa_guess=None, delta=BIN_WIDTH, chunk_bins=CHUNK_BINS):
    """Literal card estimator. No finite-bin bias correction or parameter clipping.

    The design kappa is the default *computational lag cap guess* only.  It
    never replaces kappa_hat.  Invalid estimates remain INVALID, with no M/M/1
    fallback.  W override exists solely for the synthetic unit control.
    """
    load, managed_shift, alpha, kappa, T_int = map(float, (load, managed_shift, alpha, kappa, T_int))
    W = 100*T_int if W is None else float(W)
    guess = kappa if kappa_guess is None else float(kappa_guess)
    if not math.isfinite(guess) or guess <= 0:
        raise ValueError('positive finite kappa_guess required')
    with tempfile.TemporaryDirectory(prefix='letter_w2_counts_') as tmp:
        n = int(math.floor(W/delta))
        counts = np.memmap(Path(tmp)/'counts.i4', mode='w+', dtype='<i4', shape=(n,))
        record = simulate_counts(load, alpha, kappa, W, rng, counts, delta, chunk_bins)
        count_mean = float(np.sum(counts, dtype=float)/n)
        # Compute variance directly, so the alpha floor is governed by the
        # card's variance rather than FFT roundoff at lag zero.
        sum_sq = 0.
        for start in range(0, n, chunk_bins):
            centered = np.asarray(counts[start:start+chunk_bins], dtype=float)-count_mean
            sum_sq += float(centered @ centered)
        lam = count_mean/delta
        variance = sum_sq/n/delta**2
        alpha_sq_raw = variance-lam/delta
        alpha_sq = max(0., alpha_sq_raw)
        cov = autocovariances(counts, delta, max(1, math.ceil(50*guess/delta)), chunk_bins)
        nonpositive = np.flatnonzero(cov[1:] <= 0)
        stop = int(nonpositive[0]+1) if len(nonpositive) else None
        used = stop-1 if stop is not None else len(cov)-1
        khat = float(2*np.sum(cov[1:used+1])*delta/alpha_sq) if alpha_sq > 0 else None
        del counts
    errors = []
    if khat is None or khat <= 0 or not math.isfinite(khat):
        errors.append('undefined or nonpositive kappa_hat')
    ahat = math.sqrt(alpha_sq)
    if not (ahat <= min(lam, lam+managed_shift) and max(lam, lam+managed_shift) < 10):
        errors.append('estimated action loads/amplitude outside stable nonnegative MMPP domain')
    record.update(lambda_hat=lam, alpha_hat=ahat, alpha_squared_raw=alpha_sq_raw,
                  rate_variance=variance, variance_ddof=0, kappa_hat=khat,
                  stay_load_hat=lam, switch_load_hat=lam+managed_shift,
                  kappa_guess=guess, kappa_guess_source='design kappa (lag cap only)' if kappa_guess is None else 'caller',
                  max_lag_bins=len(cov)-1, first_nonpositive_lag=stop,
                  positive_lags_summed=used, lag_cap_reached=stop is None,
                  autocovariances=cov[:used+2].tolist(),
                  autocovariance_normalization='global mean, denominator n-k',
                  status='INVALID' if errors else 'VALID', errors=errors)
    return record


def estimate_levels(prepared, regime_index):
    la, lb, u, kappa, _ = prepared['parameters']
    seed = 20261116 + int(regime_index)
    rng = np.random.default_rng(seed)
    telemetry = {}
    means, records, errors = {}, {}, []
    for side, load, shift in (('A', la+u, -u), ('B', lb, u)):
        est = estimate_path(load, shift, prepared['a'], kappa, prepared['T_int'], rng)
        telemetry[side] = est
        for action in ('stay', 'switch'):
            name = side+'_'+action
            try:
                if est['status'] != 'VALID':
                    raise ValueError('; '.join(est['errors']))
                result = mmpp.stationary_mean(est[action+'_load_hat'], est['kappa_hat'], est['alpha_hat'])
                means[name] = result.r
                records[name] = dict(status='VALID', load=est[action+'_load_hat'], **result.record())
            except (ValueError, ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
                records[name] = dict(status='INVALID', error=str(exc))
                errors.append(dict(chain=name, error=str(exc)))
    value = means['A_switch']+means['B_switch']-means['A_stay']-means['B_stay'] if not errors else None
    true_s = float(prepared['s'])
    return dict(seed=seed, status='INVALID' if errors else 'VALID', fallback=None,
                s_hat_mmpp=value, true_s=true_s,
                sign_correct=None if value is None else bool(np.sign(value)==np.sign(true_s)),
                relative_error=None if value is None or true_s == 0 else abs(value-true_s)/abs(true_s),
                telemetry=telemetry, chains=records, errors=errors)
