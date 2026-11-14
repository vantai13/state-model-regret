# EV-B replication: alarm-triggered sign reversal at q75 and q95 (fresh panel), locked before truth (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`).

**What EV-B showed.** On 30 regimes with an alarm at q90 on the Stay path A, the zero-fit law held 30/30 and its sign held 10/10. Harm present at random decision times was gone in 18/18 harm regimes, and fresh state helped in the pos/band strata. That reversal was read out descriptively.

**Question.** Is the reversal an artefact of choosing q90?

**Design.** One new panel (seed 20261152; neg/band/pos 10 each), 0 overlap with every earlier list including EV-B. Alarm levels q75 and q95. Code is `alarm.py` unchanged; the wrapper is `alarm_rep.py`.

**Predictions** (zero-fit, `q75/predictions.csv`, `q95/predictions.csv`), at each level and h = 10 T_int:

| ID | Threshold |
|---|---|
| R1 | \|G_S − pred\| ≤ max(0.1 pp, 5% \|pred\|) on ≥ 90% of 30 rows |
| R2 | sign agreement on ≥ 90% of rows with \|pred\| ≥ 0.25 pp |
| R3 (reversal) | of the rows where the random-time G_S ≤ −0.25 pp (truth, unconditioned), ≤ 20% still have G_S_alarm ≤ −0.25 pp; needs ≥ 5 rows |

R3 is the substantive claim. Its threshold comes from EV-B (0/18), with slack.
