# Codex brief EV-TE — code, tests, data, training and timing pilot (NO truth run)

From Claude (orchestrator) for Doan Van Tai, 15/11/2026.
- The author approved the design: "oke" to `results/ext_validity/ev_te/DESIGN.md`.
- cwd: `/home/vantai/state-model-regret` (branch `ext/validity`).
- Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`. Use `python3` if `python` is missing.
- **Do not commit. Do not ssh. Do not run the truth (seed B) computation.** Network is allowed only for the SNDlib download.

## Read first
1. `results/ext_validity/ev_te/DESIGN.md`. This brief makes it precise; if the two disagree, this brief wins. Do not edit DESIGN.md.
2. `experiments/ext_validity/packet.py`: `tint` (reuse it for $T_{int}$), `fluid_cost`, `batch_stats`, the write-once pattern and `--timing-only`.
3. `experiments/ext_validity/ev_d4c_panel.py` and `ev_d4c_pipeline.sh`: CLI and pipeline style, write-once writers, lock checking.

## Edit ONLY these new files
- `experiments/ext_validity/ev_te.py`: Arm S plus the shared network and fluid code.
- `experiments/ext_validity/ev_te_trace.py`: Arm R.
- `experiments/ext_validity/ev_te_pipeline.sh`: the GCP truth pipeline. Write it, but do not run it.
- `tests/test_ev_te.py`.
- Outputs go under `results/ext_validity/ev_te/` (except `DESIGN.md`).

Do not change any existing file. If you need to, stop and report.

## Data (outside Git)
- Directory `~/papers/data/sndlib/`. `sndlib-networks-native/abilene.txt` and `geant.txt` are already there (from `https://sndlib.put.poznan.pl/download/sndlib-networks-native.zip`; the old host `sndlib.zib.de` redirects to it).
- Claude has already downloaded `https://sndlib.put.poznan.pl/download/directed-abilene-zhang-5min-over-6months-ALL-native.tgz` (49,203,514 bytes) into the same directory. It is extracted to `abilene_tm/directed-abilene-zhang-5min-over-6months-ALL-native/` (48,096 files `demandMatrix-abilene-zhang-5min-YYYYMMDD-HHMM.txt`).
- Your sandbox cannot write outside the repo, so **`fetch` only verifies and records; it does not download**. It writes `results/ext_validity/ev_te/data_manifest.json`, containing:
  - the URLs;
  - the size and sha256 of the zip, the tgz, `abilene.txt` and `geant.txt`;
  - the TM file count;
  - one sha256 over the sorted list of (name, sha256) pairs of the TM files.
- Code reads the data root from `SMR_SNDLIB` (default `~/papers/data/sndlib`).

## Model (Arm S)
**Units.** Rates in Mb/s, backlog in Mb, time in units of the fast mode time constant $T_b=1$, cost in Mb·(time unit).

**Topology.**
- Parse the SNDlib native NODES, LINKS and DEMANDS. Each undirected link becomes two directed links with the same capacity.
- Abilene: capacity = `pre_installed_capacity`.
- GÉANT: all pre-installed capacities are 0, so use a uniform capacity of 10000 for every link. Record this in `design.json` as a limitation.

**Routing.**
- Stay path of each OD: minimum hop count. Break ties by the lexicographically smallest node-id sequence.
- Switch path: Yen $k=2$ second-shortest loopless path, with the same tie rule.
- All non-managed ODs always use their Stay path.

**Load scaling.** Mean OD demand is $d_{od}=\alpha\cdot$ (SNDlib demand value). Choose $\alpha$ so that $\max_e \sum_{od\ni e} d_{od}/C_e=\rho$ under all-Stay routing, with $\rho\in\{0.80,0.90\}$. The argmax link is the **bottleneck $e^*$**.

**Managed sets.**
- Candidates are ODs whose Stay path contains $e^*$ and whose Switch path avoids $e^*$. Rank them by $d_{od}$ (ties by OD id).
- OD1, OD2 and OD3 are the top three; the fourth set is {OD1, OD2}. Raise an error if a topology has fewer than three candidates.
- For a set of $m$ aggregates, the actions are all $2^m$ Stay/Switch combinations. Action 0 is all-Stay (the incumbent). The switching cost is $c=0$.

**Traffic.**
- Each OD rate is $d_{od}(1+\beta m_{od}(t))$, where $m_{od}\in\{-1,+1\}$ is a symmetric two-state Markov chain with rate $\kappa_{od}$ in each direction. The stationary marginal is 1/2 each.
- $\kappa=1$ (fast). If `slow=1`, ODs at odd rank in descending $d_{od}$ order (rank 0 is the largest) get $\kappa=0.1$.
- $\beta\in\{0.3,0.6\}$.

**Discretization.**
- Time step $dt=\min(0.05,\,T_{int}/40)$, fixed per regime from training.
- Modes change only at step boundaries, with flip probability $(1-e^{-2\kappa dt})/2$. This is the exact sampled chain.
- The load is constant within a step.
- The backlog step and the cost integral are exact for a constant load: $Q'=\max(0,Q+(\lambda-C)dt)$; the cost increment is $(Q+Q')dt/2$ if no clipping occurs, else $Q^2/(2(C-\lambda))$.
- Cost = $\sum_e\int Q_e\,dt$, using the offered-load approximation (each link sees the sum of the rates routed over it, with no shaping).

**Lossless reductions.**
- A link is *active* if its maximum possible load (all ODs high, under any action) exceeds $C_e$. Only active links can queue.
- Simulate only active links and the ODs that cross them.
- A test must show equal costs with and without the reduction.

**Regimes.**
- 2 topologies × 4 managed sets × 2 values of $\rho$ × 2 values of $\beta$ × 2 slow settings = 64.
- Regime id: `{A|G}{set1..4}_r{80|90}_b{3|6}_s{0|1}`, e.g. `A1_r80_b3_s0`.

## State, observations, twins
**State and instances.**
- The state is $X=$ (modes of the relevant ODs, backlogs of the active links). Decision instances come from a run under all-Stay routing:
  - burn-in $50\,T_{int}$;
  - decision times $t_0$ spaced $3\,T_{int}$;
  - fresh observation $X=X(t_0)$;
  - stale observation $Y_\tau=X(t_0-\tau)$ (full state, age $\tau$).
- Grids:
  - $\tau/T_{int}\in\{0.1,0.3,1,3\}$, rounded to whole steps, minimum 1 step;
  - $h/T_{int}\in\{1,2,4,7,15,30\}$, rounded to whole steps.

**Twin cost $\hat C_a(h,x)$ (mean-value fluid twin).**
- It is deterministic. The future rate of each OD is its conditional mean $d_{od}(1+\beta\bar m_{od}e^{-2\kappa_{od}t})$, where $\bar m$ is the current mode, or a fractional conditional mean for the CE twin.
- Integrate the same exact fluid step on the same $dt$ grid, with the load evaluated at the step start.

**Posterior.** $X_k\sim X\mid Y_\tau$, $k=1..K$: simulate forward from $Y_\tau$ for $\tau$ under all-Stay routing. This is exact, because $Y_\tau$ is the full Markov state.

**Pipelines,** each an argmin over actions at each $h$. Ties go to the lowest action index.

| Pipeline | Rule |
|---|---|
| `M0_new` (= `P_new` = `CE_new`) | $\hat C_a(h,X)$ |
| `M0_old` | $\frac1K\sum_k\hat C_a(h,X_k)$ |
| `P_old` | $\hat C_a(h,Y_\tau)$ (stale state used as if current) |
| `CE_old` | $\hat C_a(h,\bar X)$, where $\bar X$ = (mean of the $X_k$ backlogs, exact conditional mean modes $m(t_0-\tau)e^{-2\kappa\tau}$) |
| `M1_new` | argmin of $\hat V_a(h,X)$ from $R_{dec}$ independent rollouts from $X$ |
| `M1_old` | argmin of $\frac1K\sum_k V_a^{(1)}(h,X_k)$, with one rollout per posterior sample, CRN across actions |

**Evaluation.**
- $R_{eval}$ rollouts from $X$, with common random numbers: the same mode paths for every action, independent of the decision rollouts.
- Record $V_a(h)$ at every $h$ checkpoint for every action.
- The pipeline cost of an instance is $V_{a_{pipe}}(h)$.
- Defaults $K=128$, $R_{dec}=128$, $R_{eval}=256$. The pilot may change them.

## Predictor (multi-action Proposition 1; training seed only)
- **$r_a$:**
  - for every action, a long run with CRN on training seed A = 1, of length $T=\max(20000,\,2000\,T_{int})$;
  - $r_a$ is the time-average cost rate after burn-in, with batch-means se;
  - $T_{int}$ comes from `packet.tint` on the total backlog of the all-Stay run, sampled every $dt$;
  - a regime is excluded (`design_excluded.json`, reason recorded) if $T_{int}$ is censored, or if $P(\text{total backlog}>0)<0.01$ under all-Stay.
- **$F$:**
  - from $N_{train}=2000$ training instances (seed A), the action shares $F_{pipe}(a;h,\tau)$ for `M0_new`, `M0_old`, `P_old`, `CE_old`;
  - no rollouts and no costs are needed for this.
- **Predictions** (`predictions.csv`, one row per regime × τ × twin ∈ {M0, P, CE}):
  - slope$(h)=\sum_a r_a[F_{old}(a;h)-F_{new}(a;h)]$ for every $h$;
  - $\Delta_{pred}=\sum_a r_a[h_{30}\Delta F_a(h_{30})-h_7\Delta F_a(h_7)]$;
  - level$_{pred}=h_{30}\,$slope$(h_{30})$, in Mb·time (unnormalized; scoring divides by the measured $C_{ref}$);
  - also $r_a$, $s$-type summaries and $T_{int}$.
  - A test checks that for $|A|=2$ the slope equals $h\,s\,\Delta F$.

## Commands (`python -m experiments.ext_validity.ev_te <cmd>`; every writer raises `FileExistsError`)
1. **`fetch`**: the data and `data_manifest.json`.
2. **`design`**: writes `design.json` and `regimes.json` (64 specs). The design records, per topology:
   - $e^*$, $\alpha$, candidates and paths;
   - for every regime, the active links.
3. **`train --workers N`**: writes `train/{regime}.json` ($r_a$ ± se, $T_{int}$, $dt$, $P(Q>0)$, $F$ tables) and `design_excluded.json`.
4. **`predict`**: writes `predictions.csv`.
5. **`run --workers N [--regimes ...] [--timing-only]`**: the truth computation, test seed B = 1000001, $N=500$ instances per regime.
   - Writes `raw/{regime}.npz`: per-instance $V$ per pipeline, $h$ and $\tau$, plus $V_{\text{Stay}}$, so that a rescore can recompute everything. Writes `raw/{regime}.json`: meta, timing and seeds.
   - Before computing, it must call `verify-lock` and abort on any mismatch.
   - `--timing-only` uses a separate pilot seed 777, writes only `timing.json` (CPU-s per instance per regime, peak memory), and **writes no costs**.
6. **`verify-lock`**: compares the sha256 of `ev_te.py`, `ev_te_trace.py`, `regimes.json`, `predictions.csv`, the `train/*` files and the data files with `lock.json`. Claude writes `lock.json` later; if it is missing, exit non-zero.
7. **`score`**:
   - per cell (regime × τ), for each $h$: $L$ of each pipeline, $C_{ref}=L(\text{M1\_new})$, $E_{stay}$;
   - $G_S$ for M0, P and CE; $G_M=L(\text{M0\_old})-L(\text{M1\_old})$; $\Gamma=L(\text{M0\_new})+L(\text{M1\_old})-L(\text{M0\_old})-L(\text{M1\_new})$;
   - $z=100G/C_{ref}$;
   - se = sd of the per-instance paired differences / $\sqrt N$;
   - increment $\Delta_{meas}=100[G_S(h_{30})-G_S(h_7)]/C_{ref}(h_{30})$, with a paired se;
   - H1–H4 exactly as in DESIGN §7. The predicted pp values are the predictor values × $100/C_{ref}(h)$, using the measured $C_{ref}$;
   - writes `score.json` (verdicts, counts, eligible denominators) and `score_cells.csv`.

## Arm R (`ev_te_trace.py`, descriptive)
**Parsing.**
- Parse the 5-min Abilene TMs: timestamps from file names, 132 OD values. Report the count of missing or malformed files.
- Test split: the first 2 calendar months train, the rest test.
- $\alpha$, $e^*$ and the managed sets OD1 and {OD1, OD2} follow the Arm S rules, applied to the **train-period mean** TM.
- $\rho\in\{0.80,0.90\}$.

**Fluid replay.**
- Rates are piecewise constant per 5-min bin. Use the same exact step (one step = one bin, time unit = minutes) and the same active-link reduction (computed from the maximum observed train-plus-test load).

**Twins.** Only `P` and a regression nowcast `N`, because there is no true model.
- The mean-value twin relaxes each OD rate from its observed value to its train mean with time constant $T_r=-\Delta t/\ln\rho_1$. Here $\rho_1$ is the lag-1 autocorrelation of that OD on the train period, clipped to [5 min, 24 h].
- Fresh = the backlogs and rates of the bin ending at $t_0$. Stale = the same at $t_0-\tau$.
- `N`: per-OD OLS on train, predicting the rate at $t_0$ from (1, rate at $t_0-\tau$, rate one bin earlier), and per-link OLS predicting the backlog at $t_0$ from (1, stale backlog, stale link load). Clip predictions at 0.

**Evaluation.**
- Decision times: every test bin whose window has no missing data.
- Grids: $\tau\in\{1,2\}$ bins; $h\in\{1,2,3,6,12\}$ bins.
- The realized replay cost of each action gives $G_S$ (% of $E_{stay}$).
- se: day-block batch means.
- $T_{int}$ of the total all-Stay backlog via `packet.tint`, in minutes, on train.

**Commands.** `train`, then `run` (write-once; descriptive, so no lock is needed, but do not run it before Claude says so), then `summary`. Outputs go to `results/ext_validity/ev_te/arm_r/`.

## Tests (`tests/test_ev_te.py`, all must pass)
1. The exact fluid step equals `packet.fluid_cost` for a constant load, and the clip case is right.
2. Two-state chain: stationary marginal 1/2; the conditional mean decays as $e^{-2\kappa t}$ (statistical, fixed seed, loose tolerance).
3. The posterior sampler equals forward simulation (distribution check on a small case).
4. CRN: identical mode paths across actions.
5. The active-link reduction is lossless on a small topology.
6. The predictor reduces to $h\,s\,\Delta F$ for 2 actions.
7. Write-once writers; `run` aborts without a valid lock; `--timing-only` writes no costs.
8. Parsing of the SNDlib native network and one TM file.
9. Seeds are reproducible (same seed gives bitwise-equal output).

## What to run now
1. `fetch`, `design`, `train` (local, `--workers 8`), `predict`.
2. Arm R `train` only.
3. `run --timing-only` on 4 regimes: one Abilene and one GÉANT, each with `slow=0` and `slow=1`.
4. Do **not** run truth, Arm R `run`, or `score`.

## Final message
- The test results.
- `design.json` highlights: $e^*$ and the managed ODs per topology.
- Excluded regimes with reasons.
- The $T_{int}$ range.
- Signs of the $s$-type quantities (the count of regimes where $r_{\text{Switch}}<r_{\text{Stay}}$).
- Timing per instance, and the total CPU-s projected for $N=500$ at the default $K/R$.
- A proposal of $N/K/R$ that fits **≤ 8×10⁵ CPU-s** on 32 vCPU. GÉANT may get a smaller $N$; never cut below $N=200$.
- Arm R: the train $T_{int}$ in minutes, the missing-file count, and the managed ODs.
- Anything in this brief that turned out impossible or ambiguous.
