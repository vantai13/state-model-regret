# Spectral stationary certificate — derivation

Doan Van Tai,23/10/2026. Increments(-d,+b),d>b>0, coprime, symmetric keep s in(0,1).
For q>b, row balance with π(q,m)=v_m r^q gives
s r^(d+b)−(2s−1)r^d−r^b+s=0, v0=1, v1=(1−s r^d)r^b/(1−s).
The solver proposes b decaying roots and coefficients. Boundary conditions are
Σ c_j v1_j r_j^(−i)=0 for i=1…b−1, π(0,on)=Σc_jv1_j,
π(0,off)=sπ(0,on)/(1−s). Normalize via geometric sums. These formulas
are proposals; no completeness/positivity theorem about numerical roots is
required for the certificate below.

Treat decimal approximations of all coefficients as exact inputs to an
outward-rounded mpmath interval computation. Real parts define an absolutely
summable signed approximation ν. Check full balance at q=0…b directly. For
q>b bound the L1 residual with each mode's geometric sum, using |r|<1 verified
by intervals. Bound |Σν−1|=e0 and absolute tail eν by geometric sums. True
stationary tail eπ is bounded independently by the Lyapunov method T02.

Collapse both tails onto K, preserving mode. The difference between each
collapsed law's balance residual and its infinite balance residual has TV
at most its absolute tail. For the finite capped transition matrix use the
Poisson argument from T02, also valid for signed differences of zero total
mass. A conservative infinite-law TV bound is
(1+2T)(eπ+eν+e0)+2T*r, where r bounds TV of the full balance residual.
No finite-buffer approximation is called exact. A signed proposal is useful
only through this bound to the nonnegative true law; CDF/point probabilities
and conditioning are enclosed explicitly.

An explicit Bellman supersolution replaces the large hitting-time LU solve:
B=(d+b)/(2(1−s)), C=d/(s−δs), drift=(d−b)/2−δs B>0.
h(q,m)=(q+B*1[m=on]+C)/drift except h(0,off)=0.
For interior off/on, h−Ph≥1; at off boundary q<d the numerator is at least
d−(1−s+δs)B, and capping only reduces next q. Thus
T≤(K+B+C)/drift. All quantities are interval-evaluated. Tail target1e−36
is stricter than the previous target and is feasible without allocating K rows.

CDF intervals plus law error certify quantiles; conditional mode error is
bounded by2e/(P(q)−e), with interval evaluation and final float-conversion error.
Arrays used for comparisons have a separate evaluation-roundoff allowance;
B2 posterior uses the interval spectral expression, not array interpolation.

The source's “≤4 incoming edges” is false at reflected q0: it aggregates d+1
source backlogs. Sparse implementation counts boundary fan-in and normalization
roundoff. A small algebraic residual alone does not certify an infinite law.
