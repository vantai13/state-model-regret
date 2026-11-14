"""Doan Van Tai — classic Ethernet pcap stdin -> series.npz (+ JSON).

Usage: zcat prefix.pcap.gz | python -m experiments.ext_validity.trace_rates \
           --out /tmp/ev_d2_smoke/series.npz [--bin .01 --mod 1000]
gcc -O2 is used if available; --python forces the slower Python/numpy fallback.
No compiler artifacts are written into the repository. Both parsers use the
directional FNV-1a tuple encoding documented in trace_rates.c. Sampling residues
are disjoint flow partitions, not a claim of statistical independence.
Bins are [start+k*bin,start+(k+1)*bin), anchored at the first packet (integer ns).
The last bin may be incomplete; there is no padding to the advertised duration.
"""
import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

import numpy as np


def flow_hash(frame):
    """None for non-IP; ValueError for a missing/malformed tuple.

    Only tuple headers must be captured; payload truncation is normal. Noninitial
    fragments cannot supply a 5-tuple and are counted as parse errors.
    """
    def need(pos, count, end=None):
        if pos+count > len(frame) or (end is not None and pos+count > end):
            raise ValueError('truncated tuple')

    def u16(pos):
        need(pos, 2)
        return int.from_bytes(frame[pos:pos+2], 'big')

    need(0, 14)
    eth, o = u16(12), 14
    if eth == 0x8100:
        need(0, 18)
        eth, o = u16(16), 18
    if eth == 0x0800:
        need(o, 20)
        ihl, end = (frame[o] & 15)*4, o+u16(o+2)
        if frame[o] >> 4 != 4 or ihl < 20 or end < o+ihl or u16(o+6) & 0x1fff:
            raise ValueError('invalid/fragmented IPv4 tuple')
        need(o, ihl)
        ver, proto, addresses, pos = 4, frame[o+9], frame[o+12:o+20], o+ihl
    elif eth == 0x86dd:
        need(o, 40)
        if frame[o] >> 4 != 6:
            raise ValueError('invalid IPv6 version')
        ver, proto, addresses, pos = 6, frame[o+6], frame[o+8:o+40], o+40
        end = pos+u16(o+4)
        while proto in (0, 43, 60, 44, 51):
            need(pos, 2, end)
            if proto == 44:
                need(pos, 8, end)
                if u16(pos+2) & 0xfff8:
                    raise ValueError('noninitial IPv6 fragment')
                step = 8
            else:
                step = (frame[pos+1]+2)*4 if proto == 51 else (frame[pos+1]+1)*8
            need(pos, step, end)
            proto, pos = frame[pos], pos+step
    else:
        return None
    ports = b'\0'*4
    if proto in (6, 17):
        need(pos, 4, end)
        ports = frame[pos:pos+4]
    h = 14695981039346656037
    for byte in bytes([ver])+addresses+bytes([proto])+ports:
        h = ((h ^ byte)*1099511628211) & ((1 << 64)-1)
    return h


def options(bin_width, mod):
    if not np.isfinite(bin_width) or not 1e-9 <= bin_width <= 1e9:
        raise ValueError('bin must be >=1 ns and <=1e9 s')
    if not isinstance(mod, int) or not 2 <= mod < 2**64:
        raise ValueError('mod must be an integer in [2,2**64)')
    # Match C llround (positive values), not Python ties-to-even.
    return int(np.floor(bin_width*1e9+.5))


def extract_python(stream, bin_width=.01, mod=1000):
    """Streaming fallback; only the count matrix and one packet are retained."""
    ns_bin = options(bin_width, mod)
    h = stream.read(24)
    magics = {b'\xd4\xc3\xb2\xa1': ('<', 1000), b'\xa1\xb2\xc3\xd4': ('>', 1000),
              b'\x4d\x3c\xb2\xa1': ('<', 1), b'\xa1\xb2\x3c\x4d': ('>', 1)}
    if len(h) != 24 or h[:4] not in magics:
        raise ValueError('incomplete/not classic pcap header')
    endian, scale = magics[h[:4]]
    major, minor, _, _, _, link = struct.unpack(endian+'HHIIII', h[4:])
    if (major, minor) != (2, 4) or link & 0xffff != 1:
        raise ValueError('requires classic pcap 2.4 Ethernet')
    counts, used, start = np.zeros((1024, 3), dtype='<i4'), 0, None
    meta = dict(packets=0, parse_errors=0, non_ip=0, truncated_records=0,
                truncated_record_headers=0, snaplen_truncated=0)
    while rh := stream.read(16):
        if len(rh) != 16:
            meta['parse_errors'] += 1
            meta['truncated_record_headers'] += 1
            break
        sec, frac, cap, wire = struct.unpack(endian+'IIII', rh)
        if cap > 16*1024*1024 or frac >= 1_000_000_000//scale:
            raise ValueError('invalid caplen/timestamp')
        ns = sec*1_000_000_000+frac*scale
        if start is None:
            start = ns
        idx = (ns-start)//ns_bin
        if not 0 <= idx < 100_000_000:
            raise ValueError('timestamp before origin or series exceeds 100M bins')
        if idx >= len(counts):
            grown = np.zeros((max(2*len(counts), idx+1), 3), dtype='<i4')
            grown[:len(counts)] = counts
            counts = grown
        used = max(used, idx+1)
        if counts[idx, 0] == np.iinfo(np.int32).max:
            raise ValueError('int32 bin count overflow')
        counts[idx, 0] += 1
        meta['packets'] += 1
        meta['snaplen_truncated'] += int(cap < wire)
        frame = stream.read(cap)
        if len(frame) != cap:
            meta['parse_errors'] += 1
            meta['truncated_records'] += 1
            break
        try:
            if cap > wire:
                raise ValueError('caplen > wire length')
            hashed = flow_hash(frame)
        except ValueError:
            meta['parse_errors'] += 1
            continue
        if hashed is None:
            meta['non_ip'] += 1
        elif hashed % mod < 2:
            counts[idx, 1+hashed % mod] += 1
    meta.update(start_ns=start or 0, start_time=(start or 0)/1e9,
                bin=ns_bin/1e9, bins=used, mod=mod, hash='FNV-1a-64',
                hash_seed='14695981039346656037', format='<i4 [bins,3]: all,s0,s1')
    return counts[:used], meta


def extract(stream, out, bin_width=.01, mod=1000, python=False):
    options(bin_width, mod)
    gcc = shutil.which('gcc')
    if python or gcc is None:
        if not python:
            print('gcc unavailable; using Python/numpy fallback', file=sys.stderr)
        counts, meta = extract_python(stream, bin_width, mod)
        backend = 'python'
    else:
        with tempfile.TemporaryDirectory(prefix='trace_rates_') as tmp:
            exe, raw = Path(tmp)/'trace_rates', Path(tmp)/'rates.bin'
            subprocess.run([gcc, '-O2', '-std=c99', str(Path(__file__).with_suffix('.c')),
                            '-lm', '-o', str(exe)], check=True)
            subprocess.run([str(exe), '--bin', str(bin_width), '--mod', str(mod),
                            '--out', str(raw)], stdin=stream, check=True)
            counts = np.fromfile(raw, dtype='<i4').reshape(-1, 3)
            meta = json.loads(Path(str(raw)+'.json').read_text())
        backend = 'gcc'
    meta['backend'] = backend
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('wb') as f:
        np.savez_compressed(f, all=counts[:, 0], s0=counts[:, 1], s1=counts[:, 2],
                            metadata=json.dumps(meta, sort_keys=True))
    out.with_suffix('.json').write_text(json.dumps(meta, indent=2, allow_nan=False)+'\n')
    return meta


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bin', type=float, default=.01)
    p.add_argument('--mod', type=int, default=1000)
    p.add_argument('--out', default='series.npz')
    p.add_argument('--python', action='store_true')
    a = p.parse_args(argv)
    print(json.dumps(extract(sys.stdin.buffer, a.out, a.bin, a.mod, a.python)))


if __name__ == '__main__':
    main()
