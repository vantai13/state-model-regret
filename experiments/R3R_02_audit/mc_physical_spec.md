# Physical specification for independent L3R.3 Monte Carlo

Responsible: Doan Van Tai. Audit-only clarification before reading pilot engine.
Source docs: notes/design/grid_v1.md line14 (locked R2), notes/01_definitions_v1.md D1/D7,
current notes/01_definitions_v1_2.md D5-D16; T07. No engine source consulted for this spec.

- Two independent queues, capacity mu=10 packet/s, no finite buffer. Background side i
  has rate lambda_i-6 in mode0 and lambda_i+6 in mode1. Managed traffic u is on A before
  decision, and remains A for Stay; Switch moves all u to B at t0 for entire h.
- tau=1 second, dt=1/(120*ref), integer tau/dt and h/dt. State is qA,mA,qB,mB at START
  of slot0. The mode in that state supplies arrivals during that slot. Update backlog
  q'=max(0,q+(lambda+6*(2*m-1)+managed-mu)*dt), then transition mode for next slot.
  Each side independently keeps current mode with probability (1+exp(-2*dt/kappa))/2.
  Thus kappa is CTMC mean dwell in seconds; R2 is exact mode skeleton, not exact
  integrated arrivals inside a continuous-time slot. Do not simulate CTMC jumps within slots.
- D13 realized cost: dt*sum_{k=1..H}(qA[k]+qB[k]) after each backlog update. No q0 term,
  no terminal surcharge. Switching cost c_sw>=0 is added ONCE in packet*s to Switch.
- Stationary episode law before decision is under Stay (A carries u). y=(qA,qB) records
  backlog at t0-tau, no modes. Run exactly tau/dt pre-Stay slots to x at t0.
  This is the pilot-law audit target only, not adoption of v1.3 stationary periodic contract.
- Episodes must be IID for ordinary s/sqrt(N) SE. Use independent stationary burn-in per
  episode, or an independently computed finite-chain invariant distribution with disclosed
  truncation/convergence error; never call engine stationary/posterior/cost functions.
- Draw ONE future mode sequence per side per episode, shared by both actions and all
  policies (CRN). S0 actions depend y only, S1 actions x only; get actions from a provided
  black-box interface, never show implementation to MC author. M0 cost is mean rollout
  conditional on initial mode (expected rates per slot), cost then average over belief;
  the MC only evaluates given actions, it does not define model repair.
- Three checks: C1 simulate JStay/JSwitch from fixed x; C2 given exact y_side (incl0 and
  3-4 positive lattice points), simulate current state after age and future, compare expected
  side action cost gap; C3 population 4 costs, 6 contrasts and Cbar from oracle-policy loss.
- For C2 conditional initial mode must come from true stationary joint backlog/mode given y,
  not unconditional 1/2. Engine need not supply mode weights to MC.
- C3 both estimator comparison (fixed policies from bin representative, mean stationary
  distribution still continuous/lattice) and estimand comparison (policies at exact y).
  IMPORTANT: representative-point quadrature is NOT integration over bin policies; even
  estimator comparison can have quadrature bias. Do not claim z-only valid without a
  same-law discrete-node design or an explicit numerical allowance. Record this distinction.
- Strict true/predicted gap<0 Switch; exact ties Stay. No future leakage.
- Need pilot N0 to estimate SD, production N chosen BEFORE final runs for SE<=.001*Cbar
  on contrasts, N~ceil((sd/(.001*Cbar))**2), prereg max/retry. z limit3, one 4N retry
  with independent seed for alarm. Numeric allowance must be measured separately; no
  broadened tolerance after outcomes. Failure or insufficient SE -> flag, not manufactured PASS.
- No CF/R09/R10, only declared discovery regimes. MC code should be reusable and save
  per-episode aggregates/moments; no import of smr or experiments engine modules.
- Seed range reserved for audit only: 318300000..318399999 (verification, not confirmation).

Current task implementation paths: experiments/R3R_02_audit/independent_mc.py (and optional
independent native source/tests). Do not touch T07, prereg, report, or other agents' files.
