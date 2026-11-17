# V7-2: not run tonight (Claude, 18/11/2026, under the author's overnight delegation)

Owner: **Doan Van Tai**. Inputs: the audit `results/letter/v7_2/REPORT.md` and the design draft `results/letter/v7_2/DESIGN.md` (class B, DESIGN_DRAFT).

## Decision
V7-2 stays at the design-draft stage. No card, no adapter and no run tonight.
- V7-1 is scored, and V7-3 (congested) holds the compute and the Codex quota.
- The author can reopen V7-2 later with this note and the design draft.

## Reasons, scored against the locked V7 criteria (`letter_smr/briefs/V7_CRITERIA.md`, 14c03bf)
1. **Answers "not practical" (×3).** Only partly.
   - The real MAWI trace is used as a Cox intensity source: Poisson packets, Exp(10) service. It is not a literal packet replay.
   - The topology is two flow subsets of one link with low mean load (≤ 0.775).
   - V7-3 answers the same criticism with a real topology, real matrices and a temporal train/test split.
2. **Evidence strength (×3).** Weak.
   - There is one 4-hour record, so 4-hour holds are DATA_BLOCKED; only the 1- and 2-hour holds fit.
   - The windows overlap.
   - The regime panel was already exposed by EV-D4b/c, so it is not unseen.
3. **New weaknesses opened (×2).** High.
   - The old trace results showed a weak sign law near τ ≈ T_int (D4b 110/158; D4c band about 54%).
   - A new run on the same trace invites that comparison without new data.
4. **Fit with the advisor's single message (×2).** Moderate: it would add a second setting rather than sharpen the main claim.

## Cost if reopened
- Codex adapter: chronological split without wrap, posterior conditional propagation, conditional reference, raw writer and checks.
- Run: 11.7 CPU-h central and 53 CPU-h contingency (design draft, Section 8), for 1/2-hour holds only.
