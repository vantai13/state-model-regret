# Codex brief W2-LIT — targeted reading of 3 prior sources (download, read, note, log)

From Claude (orchestrator) for Doan Van Tai, 14/11/2026. The author delegated source selection and downloads.
Use your `paper-research` skill and the MCP servers `paper_search`, `scholar_search`, `paper_pilot`.
cwd: `/home/vantai/state-model-regret` (branch `ext/validity`).
- Edit ONLY: `notes/literature/W2_prior_check.md` (new) and `notes/literature/search_log.md` (append rows under the existing heading "W2-LIT").
- Do not commit.

## Rules (repo protocol `notes/literature/search_protocol.md`; read it first)
- **No invented references.** Every ID comes from a tool result in this session.
- **No Sci-Hub, LibGen or mirrors.** If there is no open-access copy, record "no OA" and stop for that source.
- **PDFs go to `~/papers/state-model-regret/current/`**, never into the repo. Names: `<FirstAuthor><Year>_<short>_<version>.pdf`.
- **Reading level is AI-T** (targeted) with the exact sections and pages you read. Never claim the author read anything.
- **Every content claim carries §/page/equation.** Separate "Fact (what the paper says)" from "Inference (mapping to this repo)". Mark inferences "AI đề xuất".
- **No novelty statements.** Write "chưa xác nhận từ các nguồn đã đọc", never "chưa ai làm".
- Before downloading, check whether the PDF is already in `~/papers/state-model-regret/current/` or `/mnt/c/Users/VAN TAI/Downloads/`.

## Sources and the question each must answer
Our wave-1 findings are summarised in `results/ext_validity/WAVE1_REPORT.md` and `notes/theory/T12_plugin_stationarity.md`; read them first.

1. **Bumpensanti & Wang**, "A Re-Solving Heuristic with Uniformly Bounded Loss for Network Revenue Management", Management Science 66(7):2993–3009, 2020, DOI 10.1287/mnsc.2019.3365. OA: arXiv 1802.06192 (check the version).
   - **Q1:** what exactly do they prove about re-solving frequency of a deterministic (mean-value) LP? What are the assumptions (inventory, horizon, irrevocable decisions, observed state)?
   - Does anything correspond to our closed-loop result: harm at long decision periods, a sign reversal when Δ ≲ T_int, and a first-order law with the 1/Δ transient term?
   - Read: abstract, introduction and contributions, model, main theorem statements, and any discussion of why frequent re-solving does not help.
2. **Soleymani, Baras, Johansson**, "Stochastic Control with Stale Information – Part I: Fully Observable Systems", CDC 2019, pp. 4178–4182, DOI 10.1109/CDC40024.2019.9029447. OA: arXiv 1810.10983.
   - **Q1/Q3:** with an optimal controller (true model), does performance degrade monotonically with staleness?
   - How is "value"/cost of staleness defined? Does anything relate to an approximate (biased) controller, decision period, or event triggering?
   - Read: abstract, problem setup, main results, conclusions.
3. **Mendelson & Kuang**, "Load Balancing Using Sparse Communication", arXiv 2206.02410 (v2).
   - First check with Crossref/dblp/Semantic Scholar whether a published version exists; record it.
   - **Q3:** how does the load balancer process approximate/stale state (plug-in vs model-based estimate)? Which performance result depends on that? Any herding/harm result?
   - Read: abstract, introduction, model, main theorems, discussion.

**Optional, one step only.** One forward-citation screen of Bumpensanti & Wang (`get_paper_citations` or `get_citing_papers`), up to 20 results. Look for papers on re-solving or re-optimisation frequency with delayed/stale state, or fluid-approximation control in queues.
- Log the screen.
- At most ONE further source may be *proposed* in the log. Do not download or read it.

## Output
- **`notes/literature/W2_prior_check.md`**, in Vietnamese and concise. Per source:
  - metadata;
  - versions checked;
  - PDF path;
  - reading level with exact §/pages;
  - a Fact table (claim | §/page/Eq);
  - Inference (AI đề xuất): overlap with our findings in terms of estimand / mechanism / regime; what is different; and which wording our paper must avoid because of this source;
  - Unclear items.
- End with a 5-line summary for Q1/Q2/Q3: what is known, and what remains unconfirmed.
- **Append to `search_log.md`** one row per real operation: lookup, download, read, forward.
- **Final message:** the files written, reading levels, and any access failures.
