# P1-PRIOR: comparison matrix for the paper's three main claims (steps 2–4, Claude) — DRAFT

Doan Van Tai. **AI (Claude) theo ủy quyền**, 15/11/2026, in parallel with Codex's step 1 (`P1_prior_candidates.md`, pending).
- Reading levels are AI only: **AI-T** means targeted full-text reading with §/page; **AI-A** means abstract only.
- No novelty conclusion. Overlap is judged by estimand, mechanism and regime, not by shared keywords.

**Claims under check** (paper wording):
- **K2:** a predictable $hs\Delta F$ law for a mean-value twin's value of fresh state, for one held decision.
- **K3:** plug-in pipelines have no $h$-linear term.
- **K5:** fresh telemetry harms the mean-value twin in most regimes, without herding.

## Read so far

| Work | Year, venue | Read | Estimand | Mechanism | Regime | Overlap with our claims |
|---|---|---|---|---|---|---|
| Hyytiä, Jacko, Righter, "Routing with too much information?" | 2022, Queueing Systems 100 (special issue, 3 pp.) | AI-T, whole note §1–3, pp. 1–3 | Structure of optimal routing when job sizes are known; LWL vs MWL counterexamples | Job-size information makes the optimal policy irregular; heuristics near-optimal in heavy traffic | Two FCFS servers, two-point job sizes, discrete time | **Low.** Despite the title, it is about job-size information and policy structure, not freshness or staleness of state. Not a prior for K2/K3/K5 |
| Goren, Vargaftik, Moses, "Distributed Dispatching in the Parallel Server Model" | 2022, IEEE/ACM ToN (arXiv 2008.00793v2 read) | AI-T, Abstract and §1, pp. 1–3 | Job dispatching performance with multiple dispatchers; value of queue-length information | **Herding / incast:** shared, more accurate information makes many dispatchers send to the same short queues. The proposed Tidal Water Filling accounts for other dispatchers, and its performance improves with information | Many dispatchers, parallel servers, repeated decisions | **Same phenomenon label, different mechanism.** It is the direct prior for "more accurate information can degrade performance". Our K5 must be framed as a single held decision without herding, with harm tied to the twin class and the horizon |
| PSP: packet-level load balancing for stale-state networks | 2026, IEEE LCN (arXiv 2608.08425v1 read) | AI-A plus Abstract/§I glance | Tail latency in multipath Clos networks | Stale state causes herding and oscillation in packet-level schemes; probabilistic state-proportional dispatching suppresses it | Data-center multipath, many packets per state update | **Low–medium.** Same family as Goren and Mitzenmacher (herding from stale state across many decisions) |
| Atar, Lipshutz, "Heavy Traffic Limits for Join-the-Shortest-Estimated-Queue Policy Using Delayed Information" | 2021, Math. Oper. Res. 46(1):268–300 (Crossref; online 15 Jun 2020), 10.1287/moor.2020.1056 | AI-T: Abstract, §1 pp. 1–3, and the related-work paragraph (author-downloaded Articles-in-Advance PDF) | Heavy-traffic diffusion limit of JSQ on estimated current queue lengths | Applying a current-state policy to delayed queue lengths (the "naive" plug-in estimator) can give large oscillations through delayed negative feedback, as in Mitzenmacher and Pender et al. (§1, p. 1 and related work). Estimating the current queues from delayed state and past routing fixes the input; simulations show the estimators significantly beat the naive one | **One** dispatcher, **repeated** per-arrival routing (feedback loop), parallel queues, heavy traffic | **Medium.** It is a prior for "plug-in on delayed state can perform poorly, and age-aware estimation helps" in repeated routing. Our K3 is a different statement: for **one held decision** under stationarity, the plug-in has no $h$-linear term. Our K5 (fresh state harms the age-aware mean-value twin) compares fresh versus stale for a fixed twin, which is not their comparison. Cite it, and state the difference: repeated feedback/oscillation versus one held decision |
| Beraldi, Canali, Lancellotti, Proietti Mattia, "On the impact of stale information on distributed online load balancing protocols for edge computing" | 2022, Computer Networks 210:108935, 10.1016/j.comnet.2022.108935 | AI-T: Abstract and Conclusions (author-downloaded VoR) | Load-balancing effectiveness (drop rate, response) of randomized resource sharing | Stale information when the schedule lag is comparable to the service time **reduces** balancing effectiveness; a model of the state correlation between decision and actuation times | Edge nodes, random probing, repeated decisions | **Low–medium.** It shows staleness **hurts**, i.e. fresh is better, with a correlation model. It is useful context for the usual direction of the effect, but it is not a prior for fresh information harming a twin |
| Hyytiä, Righter, "Dynamic Routing Problems with Delayed Information" | 2021, VALUETOOLS, LNICST pp. 171–184 (Crossref), 10.1007/978-3-030-92511-6_11 | AI-T: Abstract, §1, §6 Conclusions pp. 12–13 (author's accepted manuscript, esa.hi.is) | Mean response time of dispatching with delayed state or delayed acknowledgments | Naive JSQ on delayed state (JSQ0) can be **worse than round robin** (a state-blind rule) because its state estimate is biased. Delay-aware policies built on state distributions work well; with small delays plain JSQ is near-optimal | One dispatcher, repeated routing, parallel exponential servers | **Medium.** It is a prior for "a state-blind rule can beat a naive state-based rule under delayed information" (related to our K4 stationary rule) and for plug-in versus delay-aware processing. Differences: repeated dispatching, mean response time, no held horizon, no twin model class |

## Downloads
Atar & Lipshutz and Beraldi et al. were downloaded by the author on 15/11/2026 and copied to `~/papers/state-model-regret/current/` (sha256 6a66aadc…, d3fe6c8f…).


## Selection for Table I (step 2 result, Claude, 15/11/2026)

**Selection.** From Codex's 40 candidates (`P1_prior_candidates.md`) and the five seeds, 11 works were kept for **Table I**: Mitzenmacher 2000, Goren 2023, Atar–Lipshutz 2021, Hyytiä–Righter 2021, Beraldi 2022, Li 2026 (S11), Shisher–Sun 2022, Moeller 2026, Othman 2026, Amad 2026 (DT²), and Min 2026 (WM26).
- The LaTeX table is `state-model-regret-papers/paper_smr/tables/tab_related.tex`.
- Table entries are AI-judged positioning: AI-T for the read works, AI-A for Othman 2026. **They await author review.**
- Columns:
  - **Age:** state staleness or age is studied;
  - **Proc.:** plug-in versus age-aware processing is part of the analysis;
  - **Model:** model fidelity or class is studied;
  - **Horizon:** dependence on the decision horizon is analyzed;
  - **Hurt:** more accurate, fresher or better-modeled inputs can degrade decisions.
- **Horizon column.** Only this work is marked. Among the sources read, none analyzes how the value of fresher state depends on a held decision horizon. This is "chưa xác nhận từ các nguồn đã đọc", not a novelty claim.

**Not in the table** (cite in text or drop):
- Kuri–Kumar 1995 (old optimal control with delay);
- Dahlin 2000 and Fischer–Vöcking 2009 (older herding / stale-routing family);
- Tahir 2023 IEEE TC (delayed-feedback POMDP), which could be added as one text citation;
- the Lévy-queue transient approximation (2017), kept as possible support for the transient term;
- VoI/AoI control papers (CDC 2019/2021, TCCN 2025, WiOpt 2023, COML 2023, TCOMM 2024) as background;
- PSP (LCN 2026), same family as Goren.

**Implications for the claims.** These are the wording rules for the paper.
- **K5** (fresh harms the mean-value twin): the phenomenon label "more accurate information degrades performance" exists (Goren 2023, Mitzenmacher 2000, Hyytiä–Righter 2021, Atar–Lipshutz 2021 for naive use of delayed state). Claim only the one-held-decision setting without herding, the twin-class dependence, and the predictive $hs\Delta F$ law.
- **K3** (plug-in has no $h$-linear term): related work shows naive plug-in on delayed state can perform poorly in **repeated** routing through feedback and oscillation (Atar–Lipshutz, Hyytiä–Righter). Our statement concerns one held decision under stationarity, so state the difference explicitly.
- **K4** (stationary rule): Hyytiä–Righter report that a state-blind rule (round robin) can beat naive JSQ under delay. Cite this as related context.
- **K2:** no source among those read derives the value of fresh state as $hs\Delta F+B$ for a held decision. **Not confirmed** beyond the sources read; the 2×20 rule was not reached (Codex step 1 stopped at the 40-candidate cap).
