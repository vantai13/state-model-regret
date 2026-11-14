# Codex brief EV-D2 (phase 1) — real-trace (MAWI) rate series and a trace-driven Cox arrival class

From Claude, 14/11/2026. Implement and test locally. **No GCP, no download of the full trace, no scored run.**
cwd: worktree `~/smr-ext-d2` (branch `ext/ev-d2`). Env:
`source /home/vantai/state-model-regret/.venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- Only add files, plus a minimal additive change to `experiments/ext_validity/packet.py`. Existing tests must still pass.
- No commits. Keep the code compact.

## Goal
Drive the EV-D packet simulator with REAL traffic rate structure from a public MAWI backbone trace. The source is
http://mawi.wide.ad.jp/mawi/samplepoint-F/: daily 15-minute pcap.gz, CapLen 96 bytes, about 2 Gbps.

## 1. Extractor `experiments/ext_validity/trace_rates.c` (+ a Python wrapper `trace_rates.py`)
- Streams a pcap from stdin (`zcat file.pcap.gz | ./trace_rates ...`). Handle the classic pcap header, both microsecond and nanosecond magic, and the Ethernet linktype.
- For each packet: timestamp. Parse IPv4 (Ethernet type 0x0800; also skip one 802.1Q tag if present) and IPv6 (0x86DD) headers within caplen, to get the 5-tuple (src, dst, proto, sport, dport; ports only for TCP/UDP).
- Output, per bin of width `--bin` (default 0.01 s), counts (int32) of:
  - (a) all packets;
  - (b) packets whose flow hash is ≡ 0 mod M (flow sampling, `--mod` default 1000; a fixed 64-bit hash of the 5-tuple, seed fixed and documented);
  - (c) the same for a second disjoint residue (≡ 1 mod M), so the two sampled series are independent-ish streams for paths A and B.
- Write a small binary or `.npy`-compatible output plus a JSON sidecar: start time, bin, number of packets, parse errors, non-IP count.
- Must handle truncated packets and odd caplen without crashing; count them.
- The Python wrapper compiles with `gcc -O2` (check that gcc exists; if not, provide a pure-numpy fallback that is slower but correct), runs, and saves `series.npz` with arrays `all`, `s0`, `s1` and metadata.

## 2. Arrival class `trace_cox` in `packet.py` (additive)
- `params = dict(series='path/to/series.npz', key='s0' or 's1', bin=0.01, T_r=...)`.
- The intensity on path X is λ_X · R_X(t), with R = counts / mean(counts) (mean 1) and the series looped with period L. Each call starts at an independent uniform random phase (`rng`).
- Arrivals are a Cox process: Poisson within each bin with mean λ·R·bin, positions uniform in the bin.
- **T_r for the rate-aware twin:** `params['T_r']` if given. Otherwise the integral of the autocorrelation of R up to the first zero crossing, computed once and cached, from the series itself. This is the twin's calibration, not truth.
- The `validate()` and `rate_settings()` paths must accept the new class; keep the existing classes bit-identical.

## 3. Tests (< 90 s)
1. A synthetic pcap written in the test, with known timestamps and flows (IPv4 TCP/UDP, IPv6, VLAN, a truncated packet). Bin counts and flow-sampling assignments must match a pure-Python reference exactly.
2. `trace_cox` with a constant series reproduces a Poisson process: mean rate within 3 se, and variance ≈ mean in 1 s windows.
3. With a two-level square-wave series the empirical rate per phase matches λ·R within 3 se.
4. All existing packet tests still pass.

## 4. Smoke check on real data (small)
Download only the first ~200 MB of one MAWI file with an HTTP Range request, e.g. `curl -r 0-200000000 http://mawi.nezu.wide.ad.jp/mawi/samplepoint-F/2025/202503111400.pcap.gz`. Pipe it through `zcat` (a truncated gzip is fine; stop at EOF) and run the extractor. Report the packets parsed, the parse errors, the bin count, mean packets per bin and CoV for all/s0/s1, and the autocorrelation integral time of s0 and s1. Store outputs in `/tmp/ev_d2_smoke/`, not in the repo.

## Report back
Files, pytest summary, smoke statistics, any deviation.
