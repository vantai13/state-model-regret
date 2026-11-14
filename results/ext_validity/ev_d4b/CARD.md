# EV-D4b — telemetry-age dose response on a 4 h continuous real trace, low-load regimes: card locked before the test seed (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`). The author asked for it to run on the cloud overnight; the author's PC may be off.

## Why a new card

EV-D4 stopped before any test (`results/ext_validity/ev_d4/REPORT_EV_D4.md`):
- On the 4 h continuous DITL trace, the backlog integral time T_int at loads 0.85–0.95 is 9–24 min. So h = 30 T_int does not fit the series.
- A train-only diagnostic showed that a 15-min looped replay shortens T_int 6–10×. The wave 2–3 "30 T_int" was therefore not a long horizon for continuous traffic.

EV-D4b asks the EV-D4 questions only where the 4 h trace can answer them: low load.

## Questions

On real, continuous, non-looped rate structure, with telemetry age τ ∈ {1, 10, 30, 60, 120, 300} s:
1. Does the train-only leading-term law predict the sign of the effect of fresh telemetry on nowcast twins (D2)? Does it predict the magnitude (D3)?
2. Does the effect follow the law across τ (dose response, D5)?
3. T12 as corrected after the audit: is the plug-in effect free of an h-linear term (D6)? D1 is the old practical reading, kept for continuity.
4. Does the hybrid remove harm (D4)?

## Panel

- **Series:** `results/ext_validity/ev_d4/series_ditl4h_mod10.npz`. MAWI samplepoint-F DITL 2023-04-12, 16 consecutive 15-min files (10:00–14:00), 10 ms bins, 8 gap bins filled.
  - Paths A/B are two disjoint 10% flow subsets (hash mod 10 = 0 and 1), with mean 103/152 counts per bin.
  - Minute-mean ratio 0.63–1.87 / 0.72–1.72. ACF integral 46/24 s. Correlation between the two subsets at 1 min: −0.15.
- **Replay:** Cox arrivals with **one shared real-time phase for both paths** (audit B3). A run is about 1.9·10⁶–5.3·10⁶ s, so it loops over the full 4 h about 130–370 times. Each horizon h ≤ 89 min spans at most 37% of the series.
- **Regimes:** 20 (Sobol seed 20261231; strata neg 8, band 4, pos 8).
  - Cap: max(λA, λB) + u ≤ 7.75 (load ≤ 0.775). The cap was chosen from EV-D4 attempt-2 train T_int only.
  - Case seeds 14000–14019. Each regime is run at all 6 τ, giving 120 cases.
- **Horizons:** h ∈ {10, 30} × T_int (train). n_inst = 10⁴, spacing 3 T_int, 40 batches. Test seed = train seed + 10⁶.
- **Feasibility rule** (from EV-D4, applied by `select` after train): T_int ≤ 240 s and not censored at every τ. Result: **20/20 kept**.

## Seen before the lock (train only; no D, no test output)

T_int median 111 s (63–177). s_train ranges from −13.9 to 10.0. Plug-in |F_old − F_new| ≤ 0.0015 at every τ.

| τ (s) | 1 | 10 | 30 | 60 | 120 | 300 |
|---|---|---|---|---|---|---|
| nowcast slope β₁ (A, median) | 0.994 | 0.942 | 0.808 | 0.599 | 0.229 | −0.113 |
| F_old − F_new, fluid nowcast, h30 (median) | +0.025 | +0.040 | +0.050 | +0.053 | +0.054 | +0.200 |
| prediction < 0, h30 rows | 17/40 | 12/40 | 12/40 | 15/40 | 17/40 | 22/40 |
| \|pred\| ≥ 0.25 pp, h30 (approx., using train E_stay) | 21/40 | 20/40 | 28/40 | 27/40 | 25/40 | 38/40 |

## Predictions and thresholds

Predictions are in `predictions.csv` (480 rows: 120 cases × h{10, 30} × 2 nowcast twins), computed from the train JSON only. The leading term is h·ŝ·(F_old − F_new).

| ID | Rows | Threshold |
|---|---|---|
| D1 plug-in, practical | h = 30 T, fluid + ratefluid (240) | G_S ≥ −max(0.25 pp, 2 se) on ≥ 90% |
| D2 nowcast sign | h = 30 T, nowcast twins with \|pred\| ≥ 0.25 pp | sign agreement ≥ 85% (NOT_EVALUABLE if < 5 rows) |
| D3 nowcast size | h = 30 T, nowcast twins (240) | \|G_S − pred\| ≤ max(0.15, 0.3·\|pred\|) + 2 se on ≥ 80% |
| D4 hybrid | h ∈ {10, 30}, ratefluid_nowcast_hybrid_train (240) | G_S ≥ −max(0.1, 2 se) on ≥ 90% |
| D5 dose response | per τ, median over h30 nowcast rows: predicted vs observed | Spearman over the 6 τ ≥ 0.8 |
| D6 T12 (no h-linear term) | plug-in twins, each case with both h | \|G%(30) − G%(10)·E10/E30\| ≤ max(0.25 pp, 2(se30 + se10·E10/E30)) on ≥ 90% |

Rules:
- If fewer than 90% of the 240 (case, h) outputs exist, the result is INCONCLUSIVE.
- One run.
- Code: `experiments/ext_validity/ev_d4b_panel.py`. Its score reuses `ev_d4_panel.score`. Simulator: `packet.py` with `path_keys`.

## Run (GCP VM only)

`experiments/ext_validity/ev_d4b_pipeline.sh` runs the following steps:
1. The test seed, resumable with fixed seeds per (case, h). On a crash it retries with fewer workers.
2. `raw_manifest.json`, the sha256 of every raw test file, written **before** scoring.
3. `score.json`, using the locked code.
4. VM power-off.

Raw files, the manifest and the score are committed from the author's PC afterwards: raw and manifest first, then the score.

**Expectation** (stated here, not a threshold): on earlier traces, D2 passed and D3/D4 failed. Here the slower, non-looped variation is new. D6 is the first direct test of corrected T12.
