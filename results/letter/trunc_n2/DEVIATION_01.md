# DEVIATION_01: same-platform truncation comparison

Owner: **Doan Van Tai**. Recorded on 17 November 2026 before any full-population
2N run/output. The completed local timing pilot at 2N is prior exposure named
in the card; its scientific differences have not been read or scored.

The VM's existing 1N code-path pilot does **not** reproduce the saved local
W1b output within the fixed relative tolerance of 1e-12. The handoff records a
maximum absolute cost difference of at most 2.3e-12 packet·s and a maximum
relative difference of 1.8 on near-zero values. The failed check and its raw
output are preserved in `platform_pilot_n1/`. This is floating-point platform
noise, not a passing reproduction check. Its tolerance is not loosened.

As explicitly authorized in `notes/ops/codex/LETTER_HANDOFF_R13_brief.md`, the
primary truncation comparison is therefore **2N on the VM against 1N on the
same VM**, for all 27 regimes and all saved ages/horizons. A fresh, single
full-population 1N run precedes the single full-population 2N run. They use
12 workers, a 4 h cap each, and distinct write-once output roots
`raw_n1_vm/` and `raw_n2/` (each contains `raw/` and timing receipts).

All card thresholds and field classes remain unchanged: percentage-of-C_ref
fields at 1e-6 pp, relative fields at 1e-9 with no denominator floor, and
identical discrete fields. The original card remains byte-identical. The
same-platform comparison is written to `compare.json`/`compare.md`; the full
VM-1N versus saved-local-W1b comparison is reported separately under
`platform_noise/`, with absolute differences alongside relative differences.
Near-zero failures will be reported as failures, without reclassification.

Code, tests, manifest and this deviation are committed/pushed before launch.
The VM pipeline verifies the manifest, runs without automatic scoring or
power-off, and logs start/exit. Raw outputs and logs are retrieved with
matching checksums, then committed/pushed **before** comparison. After
retrieval and scoring the VM is powered off and its stopped state checked.
The VM stays at its existing default 12-vCPU/48-GB shape, as the handoff
requests, superseding the card's earlier 32-vCPU compute projection only.
