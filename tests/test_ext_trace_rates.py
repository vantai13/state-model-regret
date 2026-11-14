"""Doan Van Tai — synthetic packet references; no downloaded fixtures/study."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess

import numpy as np
import pytest

from experiments.ext_validity import packet as P, trace_cox as C, trace_rates as R


@pytest.fixture(scope='module')
def extractor(tmp_path_factory):
    gcc = shutil.which('gcc')
    if gcc is None:
        pytest.skip('gcc unavailable; Python fallback is tested separately')
    exe = tmp_path_factory.mktemp('trace_c')/'trace_rates'
    subprocess.run([gcc, '-O2', '-std=c99', '-Wall', '-Wextra', '-Werror',
                    str(Path(R.__file__).with_suffix('.c')), '-lm', '-o', str(exe)], check=True)
    return exe


def fixture_pcap(endian='<', nano=False):
    """Known tuples, header truncation, odd caplen, payload snaplen, gaps/ties."""
    records, tuples = [], []
    eth = b'\x01'*12
    for i in range(24):
        v6, proto, vlan = i % 4 == 0, (6, 17, 1)[i % 3], i % 5 == 0
        if v6 and proto == 1:
            proto = 58
        src, dst = (bytes([i])*16, bytes([i+1])*16) if v6 else (bytes([10, 0, 0, i]), bytes([10, 0, 1, i]))
        ports = struct.pack('!HH', 1000+i, 443) if proto in (6, 17) else b'\0'*4
        transport = ports+b'\0'*16
        if v6:
            # Include a hop-by-hop extension before the final tuple protocol.
            ip = struct.pack('!IHBB', 6 << 28, 8+len(transport), 0, 64)+src+dst
            ip += bytes([proto, 0])+b'\0'*6
        else:
            ip = struct.pack('!BBHHHBBH', 0x45, 0, 20+len(transport), i, 0, 64, proto, 0)+src+dst
        frame = eth+(b'\x81\x00\0\x01' if vlan else b'')+struct.pack('!H', 0x86dd if v6 else 0x0800)+ip+transport+b'X'
        # Repeated tuple appears again, independent of timestamp or extra payload.
        for t in (i*10_000_000, i*10_000_000+1_000_000):
            records.append((t, frame, len(frame)+50))
            tuples.append(bytes([6 if v6 else 4])+src+dst+bytes([proto])+ports)
    records += [(250_000_000, eth+b'\x08\x06'+b'\0'*7, 21),
                (260_000_000, eth+b'\x08\x00'+b'\x45\0', 16),
                (300_000_000, b'\0'*5, 5)]
    tuples += [None, 'error', 'error']
    magic = (0xa1b23c4d if nano else 0xa1b2c3d4)
    data = struct.pack(endian+'IHHIIII', magic, 2, 4, 0, 0, 96, 1)
    start = 1_700_000_000*10**9+123_000_000
    expected = np.zeros((31, 3), dtype='<i4')
    residues = set()
    for (delta, frame, wire), key in zip(records, tuples):
        stamp = start+delta
        sec, ns = divmod(stamp, 10**9)
        data += struct.pack(endian+'IIII', sec, ns if nano else ns//1000, len(frame), wire)+frame
        idx = delta//10_000_000
        expected[idx, 0] += 1
        if isinstance(key, bytes):
            # Independent reference hashes known tuples, not production parsing.
            value = 0xcbf29ce484222325
            for byte in key:
                value ^= byte
                value = value*0x100000001b3 % 2**64
            residue = value % 3
            residues.add(residue)
            if residue < 2:
                expected[idx, residue+1] += 1
    assert residues == {0, 1, 2}
    return data, expected, start


@pytest.mark.parametrize('endian,nano', [('<', False), ('>', False), ('<', True), ('>', True)])
def test_synthetic_exact_reference(extractor, tmp_path, endian, nano):
    data, expected, start = fixture_pcap(endian, nano)
    out = tmp_path/'counts.bin'
    subprocess.run([str(extractor), '--bin', '.01', '--mod', '3', '--out', str(out)], input=data, check=True)
    c = np.fromfile(out, dtype='<i4').reshape(-1, 3)
    py, metadata = R.extract_python(io.BytesIO(data), .01, 3)
    np.testing.assert_array_equal(c, expected)
    np.testing.assert_array_equal(py, expected)
    assert json.loads(Path(str(out)+'.json').read_text()) == metadata
    assert metadata['start_ns'] == start and metadata['packets'] == 51
    assert metadata['parse_errors'] == 2 and metadata['non_ip'] == 1
    assert metadata['snaplen_truncated'] == 48 and metadata['truncated_records'] == 0
    assert np.all(c[:, 1:].sum(axis=1) <= c[:, 0])
    # All packets of a known flow select the same residue across bins.
    assert np.all(c[:24, 1:] % 2 == 0)


@pytest.mark.parametrize('tail', [b'', b'broken', 'partial_body'])
def test_eof_and_truncated_record(extractor, tmp_path, tail):
    data, _, _ = fixture_pcap()
    if tail == 'partial_body':
        tail = struct.pack('<IIII', 1_700_000_000, 433000, 90, 90)+b'\0'*7
    data += tail
    raw = tmp_path/'raw'
    subprocess.run([str(extractor), '--out', str(raw)], input=data, check=True)
    expected, meta = R.extract_python(io.BytesIO(data))
    np.testing.assert_array_equal(np.fromfile(raw, dtype='<i4').reshape(-1, 3), expected)
    assert json.loads(Path(str(raw)+'.json').read_text()) == meta
    assert meta['truncated_records'] == (tail != b'' and len(tail) > 16)
    assert meta['truncated_record_headers'] == (tail == b'broken')


def test_bad_inputs_and_tuple_edges(extractor, tmp_path):
    data, _, _ = fixture_pcap()
    for blob in (b'', b'badmagic'+data[8:], data[:20]+struct.pack('<I', 101)+data[24:]):
        with pytest.raises(ValueError):
            R.extract_python(io.BytesIO(blob))
        proc = subprocess.run([str(extractor), '--out', str(tmp_path/'raw')], input=blob, capture_output=True)
        assert proc.returncode != 0
    # Noninitial IPv4/IPv6 fragments and short VLAN/transport headers.
    eth = b'\0'*12
    ipv4 = bytes.fromhex('4500002800000001400600000a0000010a000002')
    ipv6 = struct.pack('!IHBB', 6 << 28, 8, 44, 64)+b'\0'*32+bytes.fromhex('0600000800000000')
    for frame in (b'\0', eth+b'\x81\x00', eth+b'\x08\x00'+ipv4,
                  eth+b'\x86\xdd'+ipv6, eth+b'\x86\xdd'+ipv6[:40]):
        with pytest.raises(ValueError):
            R.flow_hash(frame)
    for bin_width, mod in ((0, 1000), (np.nan, 3), (.01, 1), (.01, -1)):
        with pytest.raises(ValueError):
            R.extract_python(io.BytesIO(data), bin_width, mod)


def test_wrapper_and_no_gcc_fallback(tmp_path, monkeypatch, extractor):
    data, expected, _ = fixture_pcap()
    pcap = tmp_path/'fixture.pcap'
    pcap.write_bytes(data)
    for fallback in (False, True):
        out = tmp_path/f'{fallback}.npz'
        with monkeypatch.context() as m:
            if fallback:
                m.setattr(R.shutil, 'which', lambda _: None)
            with pcap.open('rb') as stream:
                meta = R.extract(stream, out, mod=3)
        assert meta['backend'] == ('python' if fallback else 'gcc')
        assert json.loads(out.with_suffix('.json').read_text()) == meta
        with np.load(out, allow_pickle=False) as arrays:
            for j, key in enumerate(('all', 's0', 's1')):
                assert arrays[key].dtype == np.dtype('<i4')
                np.testing.assert_array_equal(arrays[key], expected[:, j])
            assert json.loads(arrays['metadata'].item()) == meta


def params(tmp_path, counts, **kwargs):
    path = tmp_path/'series.npz'
    np.savez(path, s0=counts, s1=np.asarray(counts)[::-1])
    return dict(series=str(path), key='s0', bin=.05, **kwargs)


def test_constant_poisson(tmp_path):
    p = params(tmp_path, np.full(40, 7))
    lam, T = 5., 30000.
    at = P.arrivals('trace_cox', lam, p, T, np.random.default_rng(218))
    counts = np.histogram(at, bins=np.arange(int(T)+1))[0]
    se = np.sqrt(lam/T)
    print('constant: rate, target, se, 1s variance:', len(at)/T, lam, se, counts.var(ddof=1))
    assert abs(len(at)/T-lam) <= 3*se
    assert abs(counts.var(ddof=1)-lam) <= 3*np.sqrt((lam+2*lam**2)/T)
    assert np.all(np.diff(at) >= 0) and np.all((0 <= at) & (at < T))
    assert P.rate_settings(dict(cls='trace_cox', params=p)) == (.025, .025)


def test_square_wave_by_phase(tmp_path):
    p = params(tmp_path, [1, 1, 3, 3])
    lam, T, seed = 8., 10000., 731
    phase = np.random.default_rng(seed).uniform(0, .2)
    at = P.arrivals('trace_cox', lam, p, T, np.random.default_rng(seed))
    # Total duration is an integer number of periods: each phase has T/4 exposure.
    ix = np.floor(((at+phase) % .2)/.05).astype(int)
    counts = np.bincount(ix, minlength=4)
    target = np.array([.5, .5, 1.5, 1.5])*lam*T/4
    z = (counts-target)/np.sqrt(target)
    print('square wave: observed, expected, z:', counts, target, z)
    assert np.all(abs(z) <= 3)
    assert np.array_equal(at, P.arrivals('trace_cox', lam, p, T, np.random.default_rng(seed)))


def test_partial_bins_loop_and_independent_phase(tmp_path):
    p = params(tmp_path, [0, 0, 4, 0])
    rng = np.random.default_rng(12)
    seen_phases = []
    for T in (.001, .049, .07, .2, .43):
        # A cloned generator predicts each fresh uniform phase (no fixed phase).
        probe = np.random.default_rng()
        probe.bit_generator.state = rng.bit_generator.state
        phase = probe.uniform(0, .2)
        seen_phases.append(phase)
        at = P.arrivals('trace_cox', 10000, p, T, rng)
        assert np.all((at >= 0) & (at < T))
        assert np.all(np.floor(((at+phase) % .2)/.05).astype(int) == 2)
    assert len(set(seen_phases)) == 5
    assert P.arrivals('trace_cox', 0., p, .3, rng).size == 0
    assert P.arrivals('trace_cox', 7., p, 0., rng).size == 0


def test_calibration_reference_cache_validate(tmp_path, monkeypatch):
    values, dt = np.array([1., 1., 1., 1., 5., 5., 5., 5.]), .05
    p = params(tmp_path, values)
    z = values-values.mean()
    cov = np.array([z[:len(z)-k]@z[k:]/(len(z)-k) for k in range(len(z))])
    r = cov/cov[0]
    k = np.flatnonzero(r <= 0)[0]
    reference = dt*sum((r[i]+r[i+1])/2 for i in range(k-1))
    reference += dt*r[k-1]**2/(2*(r[k-1]-r[k]))
    assert C.autocorrelation_time(values, dt) == pytest.approx(reference)
    C._calibration.cache_clear()
    original, calls = C.autocorrelation_time, []

    def count(*args):
        calls.append(1)
        return original(*args)

    monkeypatch.setattr(C, 'autocorrelation_time', count)
    case = dict(id='trace_fixture', cls='trace_cox', lamA=7., lamB=6.5, u=1., params=p)
    P.validate(case)
    assert P.rate_settings(case) == pytest.approx((reference, reference))
    assert len(calls) == 1
    assert P.rate_settings(dict(case, params=dict(p, T_r=.7, rate_window=1.))) == (.7, 1.)
    assert len(calls) == 1
    # Overwrite the file: cache must not serve the previous normalization/T_r.
    np.savez(p['series'], s0=np.ones(12), s1=np.ones(12))
    assert P.rate_settings(case) == (.025, .025)
    assert len(calls) == 2
    for patch in (dict(bin=0), dict(key='missing'), dict(T_r=0), dict(T_r=np.inf), dict(rate_window=0)):
        with pytest.raises(ValueError):
            P.validate(dict(case, params=dict(p, **patch)))
    for values in ([0, 0], [-1, 2], [np.nan, 1], [], [[1, 2]]):
        p = params(tmp_path, values)
        with pytest.raises(ValueError):
            P.arrivals('trace_cox', 7., p, 1., np.random.default_rng(0))
    for lam, T in ((-1, 1), (1, -1), (np.inf, 1), (1, np.nan)):
        with pytest.raises(ValueError):
            P.arrivals('trace_cox', lam, p, T, np.random.default_rng(0))


def test_legacy_arrivals_bit_identical():
    # Golden bytes captured from HEAD packet.py before this additive change,
    # with the project's requested numeric environment and seed 12345.
    goldens = {
        'mmpp2': '49b633b61d9063b3058647172994513a01a4a313485b6aac1a36045238fe9382',
        'onoff_exp': '4349af2677671b32284ae61633f8ff61d98938fd074b606d082eb95324a347bd',
        'onoff_pareto': '660c9b7f34d788209cc205f81b96368596704797aed77663c63f06092afaa249'}
    for cls, digest in goldens.items():
        p = dict(kappa=.5) if cls == 'mmpp2' else dict(K=4, f=.3, T_c=1.5, b=2., alpha=1.5, cap=8.)
        at = P.arrivals(cls, 7., p, 200., np.random.default_rng(12345))
        assert hashlib.sha256(at.tobytes()).hexdigest() == digest
