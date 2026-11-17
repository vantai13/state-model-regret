# Addendum to LETTER_RESUME_R13_brief.md (Claude, 17/11/2026 night)

- **Part 1 is DONE:** commit 285ccdbce, synced and pushed (9b04999a). Do not redo it.
- **Claude's independent check, read from the committed raw:** in 2N-VM vs 1N-VM, max abs change is
  - G_S: 2.355e-9 pp;
  - regrets: 1.389e-9 pp;
  - shares: 4.79e-8;

  exactly 10 non-numeric changes, all `margin_best.old` (near-tied margin argmin, a diagnostic not used in the letter).
- **Truncation clause** (card inclusion rule, using the class-(a) max of 7.7e-9 pp from the committed compare):
  - doubling the truncation level in the 27 α = 7.5 regimes changes every reported percentage by less than 1e-8 pp of C_ref;
  - decision shares change by less than 1e-7.

  Keep it to one clause. Do not claim that all quantities are invariant, and do not mention the margin diagnostic in the paper. Add ledger row `C5_R13` with these maxima, recomputed from the committed compare/raw.
- **letter_smr checkpoint commit:** see `git log -1` in letter_smr. Continue Part 2 from there.
