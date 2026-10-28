# T1 adapter correction — Doan Van Tai

Before fix, unit test at commit778c4ce failed random finite toy245: exact M0 gap0
was converted to longdouble rational probabilities and became slightly negative.
L00=9.4 instead of exact9.25; fixture and failed JUnit/log retained. This tests a
**different rounded input law** if exact rational tie information is discarded.
No physical-pilot discrepancy follows from that failure alone.

Fix only the golden adapter, not pilot: put all toy states on A and trivial B=0,
c=0. Let W be lcm of conditional probability denominators, C the lcm of cost/gap
denominators. Supply integer counts W*D and integer costs C*J,C*Delta,C*Dhat to
actual pilot pair_values. Its costs are homogeneous with factor W*C in this setup;
actions depend only sign, unaffected by positive scales. All integer accumulations
for bounded toys are exact in longdouble, checked explicitly, then divide returned
cost by W*C as Fraction. Population average uses original exact p(y).
This retains every test and the exact targets; no epsilon or widened tolerance.
The adapter does not change production engine, raw pilot or its policy. Therefore
this adapter error does not trigger a scientific pilot-v2 rerun. Near-zero physical
model-gap sign certification remains a reported limitation, not assumed solved.
