# Codex brief P1-PRIOR (step 1 of 4): candidate search for the prior check of the paper's three main claims

From Claude for Doan Van Tai, 15/11/2026. The author approved this batch.
- **Codex does step 1 (search, dedup, screen, log).** Claude does steps 2–4: second screening, targeted reading, and the comparison matrix.
- cwd: `/home/vantai/state-model-regret` (branch `ext/validity`).
- **Edit ONLY:** `notes/literature/P1_prior_candidates.md` (new) and `notes/literature/search_log.md` (append a section `## P1-PRIOR`). Do not commit. Do not download PDFs in this step.
- Use the `paper-research` skill and the MCP servers `paper_search` and `scholar_search`. Read `notes/literature/search_protocol.md` first. Its rules are binding: real counts only, lookup versus keyword versus backward versus forward, no pirate libraries.

## The three claims to check (paper wording, simplified)
1. **K2.** For a model-based (mean-value / fluid / certainty-equivalent) twin that makes one decision held over a horizon h, the value of fresh state is $h\,s\,\Delta F + B + O(e^{-\gamma h})$. Its sign and size can be predicted from the twin and stationary quantities, without fitting the true model.
2. **K3.** A plug-in pipeline, i.e. the same decision rule applied to stale and fresh observations under stationarity, has no term growing linearly in h.
3. **K5.** Fresh telemetry makes the mean-value twin's decision worse in most regimes, with only a narrow helpful band, even when the fresh telemetry carries only backlog. This happens without herding and without many agents.

## Seeds (in the library; resolve IDs with lookup first)
- S11: "From Freshness to Effectiveness: Goal-Oriented Sampling for Remote Decision Making", IEEE Trans. Inf. Theory 72(4), 2026 (arXiv 2504.19507).
- M00: M. Mitzenmacher, "How Useful Is Old Information?", IEEE TPDS 11(1), 2000.
- SS22: M. K. C. Shisher and Y. Sun, "How Does Data Freshness Affect Real-time Supervised Learning?", MobiHoc 2022, DOI 10.1145/3492866.3549711.
- R51: "DT²: Decision-Targeted Digital Twins", ICML 2026, PMLR 306.
- WM26: "When Low Prediction Error Misleads Planning: Diagnosing Representation, Dynamics ...", arXiv 2610.05550.

## Operations
1. **Backward chaining** (`get_paper_references`) and **forward chaining** (`get_paper_citations`; OpenAlex `get_citing_papers` on 429) for each seed.
   - Forward: up to 50 most recent citing works per seed.
   - Backward: the full reference list, screened by title.
2. **Keyword queries** (Semantic Scholar / OpenAlex; dblp for networking venues), 20 results each:
   - "value of information routing";
   - "model mismatch regret network control";
   - "stale state routing decision";
   - "stale information load balancing queue";
   - "network digital twin synchronization decision quality";
   - "telemetry freshness network control decision";
   - "certainty equivalence stale state queueing";
   - "age of information non-monotone decision".
   - You may add up to 4 refined queries, and log why.
3. **Stopping rule.** Stop the keyword part when 2 consecutive valid queries × 20 results give no new kept candidate (the repo's 2×20 rule). Report whether the rule was reached.

## Screening (title, then abstract)
- **KEEP** if the work studies a decision or control that uses stale, delayed or aged state information, or a simplified or mean-field/fluid model, and evaluates **decision cost or regret**. It must not stop at estimation error only. The field is networking, queueing, routing or load balancing, digital twins, networked control, or age of information.
- **Also KEEP** works that compare the value of better information with the value of a better model, and works on the long-horizon or average-cost effect of information.
- **DROP:** pure estimation or prediction accuracy without decisions; unrelated fields (finance, biology, transport unless it is network-like routing); surveys that do not address the question (note them). Also drop vehicle routing (VRP) as opposed to network routing.
- **Recency preference:** 2017 onward, but keep an older work if it is a direct prior for K2, K3 or K5, and state why.
- At most **40 kept candidates** in total. Rank them by closeness to K2, K3 and K5.

## Output: `notes/literature/P1_prior_candidates.md`
- A table: `# | title | year | venue | DOI/arXiv | peer-reviewed? | OA PDF (Unpaywall/arXiv/HAL) | found by (seed/backward/forward/keyword q#) | closest claim (K2/K3/K5) | one-line abstract-level reason | reading level = abstract-only/metadata`.
- Below the table:
  - counts per operation (results seen, kept, duplicates);
  - errors and rate limits;
  - whether the 2×20 stop was reached.
- **No conclusions about novelty.** Write "chưa xác nhận" language only.

## Final message
- Number of candidates.
- The top 15 by closeness, each with one line.
- Which ones have no OA (the author may download them).
- Tool failures.
