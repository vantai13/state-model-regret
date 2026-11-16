# E4 CARD: fluid twin vs hybrid correction on GÉANT (written before truth; Claude, 16/11/2026)

- **Approval:** the author approved `results/letter/E4_DESIGN.md` and delegated adjustments ("bạn có thể tự điều chỉnh phù hợp rồi bạn tự quyết định và chạy luôn"). Roles: Claude (card, decisions), Codex (code `experiments/letter/e4_geant.py`, `e4_rhat.py`; 21 tests PASS; GÉANT M0_new regression bitwise-identical to locked EV-TE).
- **Seen before this card:**
  - EV-TE training outputs (seed 1) and the EV-TE truth (seed 1000001), including GÉANT outcomes;
  - E4 training checks (seed 1, N = 100): r̂ (ii) best action agrees with (i) in 14/17 regimes, (iii) in 9/17; M0 fresh ties average 46%, stale 3%;
  - an E4 pilot on seed 7000001 (2 regimes × 1 chunk; costs seen);
  - Claude's own training-only test of masked or tail-weighted Gaussian variants (14/17 and 15/17; not in the code).
- **Not seen:** anything on test seed **3000001**.

## Tests (machine card `CARD_E4.json`, schema letter-e4-card-v1)
Unit for E4-1, E4-2 and E4-4: regime × τ × h with h ∈ {7, 15, 30}·T_int (`horizon_rule: each`). 17 regimes × 3 ages × 3 horizons = 153 rows. Regret uses both sides (fresh and stale must pass). Rows share instances, so they are not independent trials.

| ID | Pipeline | Pass if |
|---|---|---|
| E4-1 | Hybrid (i) | \|G_S\| ≤ 0.25% C_ref in ≥ 90% of rows |
| E4-2 | Hybrid (i) | regret ≤ 0.5% C_ref (both sides) in ≥ 90% of rows |
| E4-3 | r̂ (ii) vs (i) on training | best-action agreement ≥ 90% of regimes. **Already known before truth: 14/17 = 82%, NOT met.** Reported as a pre-truth finding with its cause analysis (Gaussian closed form overestimates backlog in near-empty, slow-mode regimes; see INSIGHTS I21). |
| E4-4 | Hybrid (ii) | regret ≤ 0.5% C_ref (both sides) in ≥ 80% of rows |
| E4-5 | descriptive | share of the M0 → hybrid (i) regret reduction captured by M0-tie-r̂ (i) |
| E4-6 | descriptive | M0 regret and G_S vs h/T_int; tie shares; reversed-ordering cost; noise levels |

## Onset-aware hybrid (rule fixed now, before W2's P15/P16 are known)
- If W2's held-out **P15 and P16 both hold** for ŝ = true s, then `onset_theta` = W2's selected θ for true s. Otherwise `onset_theta` = null and the onset pipeline is not run.
- The value is copied mechanically from `results/letter/w2/summary.json` into `CARD_E4.json` before the lock.

## Forecasts (Claude; not tests)
- **E4-1:** likely met. In the CTMC, the hybrid's G_S was ≈ 0 beyond about 4·T_int.
- **E4-2:** likely met.
- **E4-3:** not met (known).
- **E4-4:** borderline. The three regimes where (ii) orders actions wrongly give 27/153 = 18% of rows, which probably fail, so the pass share is about 82% against an 80% threshold.
- **E4-5:** tie-breaking toward r̂ (i) captures most of the M0 → hybrid gain, because about 46% of fresh decisions are zero-zero ties.

## Protocol
1. Write `CARD_E4.json` (onset θ per the rule above).
2. Lock `results/letter/e4/lock.json` with sha256 of the code, card, training checks and EV-TE inputs; commit and push.
3. One truth run on GCP: `run --workers 32 --chunks all --card results/letter/e4/CARD_E4.json` (plus `--onset-theta` if set).
4. Commit the raw outputs before `score`. Score with the locked code, then an independent rescore (Codex, no import of e4_geant).
5. Result analysis (`result-analysis`): causes and improvements before concluding.

## Addendum before truth (Claude, 16/11/2026, author delegation)
- **W2 outcome for the onset rule:** P16 held; P15 was mechanically "not held" (true_s old side 127/256). The cause is a wording error in Claude's W2 card: the stale side was compared to *fresh* M0. On the same side the held-out share is 99–100% (post-hoc, INSIGHTS I23).
- **Deviation from the rule above:** `onset_theta` = 0.5 (W2's selection for true s) is set in `CARD_E4.json`, but the onset pipeline is **descriptive only**. It is not used by E4-1…E4-4, and it is reported separately as a deviation. Without this addendum the rule would have set it to null.
- **Lock:** `results/letter/e4/lock.json`, 27 files (code, EV-TE inputs, training checks, machine card). Nothing on seed 3000001 has been computed.
