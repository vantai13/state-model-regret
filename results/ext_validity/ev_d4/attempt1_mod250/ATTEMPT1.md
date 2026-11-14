# EV-D4 attempt 1 (mod 250): infeasible under the pre-train rule — no test run (14/11/2026)

Doan Van Tai — AI (Claude) theo ủy quyền.

**Design.** Committed in `83b7bec4` before train:
- Paths A/B are the s0/s1 flow samples at hash mod 250, i.e. 0.4% of flows each, about 340–430 pkt/s. This rate was chosen to match the EV-D3b sample rate.
- The trace replay uses one shared phase for both paths.
- Rule: drop a regime at every τ if T_int is censored or 30·T_int > 7200 s.

**Train-only facts** (no test output exists):
- T_int median **1445 s** (range 1135–1836 s); 0 censored.
- **120/120 cases have 30·T_int > 7200 s**, so the rule excludes everything.
- s_train ranges from −1038 to 2616.
- Running the test would need about 4·10⁷ simulated seconds per job, which is also infeasible in memory.

**Cause (train-free description of the series).** Each mod-250 sample is dominated by a few flows:
- minute means range from 0.31 to 6.8 times the overall mean;
- ACF integral 13–16 s.

So minute-long surges overload the queue for many minutes. For comparison, the link aggregate is smooth: minute means 0.84–1.27×, 113.5k pkt/s. A mod-1000 extraction was even burstier (0.16–14.9×) and was set aside before any train.

**Decision.** One redesign only, recorded before its train:
- mod 10, so each path is a disjoint 10% flow subset;
- same rule;
- if more than 50% of regimes are excluded again, EV-D4 stops and is reported as infeasible.

The train JSONs of this attempt are kept in `train/`.
