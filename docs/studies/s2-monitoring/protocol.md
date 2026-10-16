# S2 monitoring sensitivity: protocol

Specified on 2026-10-16 before running the study. This is a local, prospective
protocol, not an independently timestamped preregistration. Results and interpretation
belong in separate files; changing this design requires a separately labeled study.

## Question and fixed design

How do false-positive reports and correlated monitoring failures change the tradeoff
between reciprocal pacing and unrestricted development in the synthetic S2 fixture?

Use `get_scenario("s2")`, model `isobar-reference-v1`, its full 24-tick horizon and
all resolved defaults. Aurora remains reciprocal; Boreal remains bounded with hidden
capacity 3. Change only `verification.false_positive_rate` and
`verification.shared_root_failure` between conditions:

| Condition | False-positive rate | Shared-root failure probability |
|---|---:|---:|
| f01-r00 | 0.01 | 0.0 |
| f01-r30 | 0.01 | 0.3 |
| f10-r00 | 0.10 | 0.0 |
| f10-r30 | 0.10 | 0.3 |

In every condition, call `experiments.compare` with policies in the order
`["unrestricted", "reciprocal"]` and seeds `list(range(20))`: 40 runs per condition,
160 total. Policy changes do not change actor strategies. No overrides, tuned seeds,
extra horizons, fitted parameters or post-hoc exclusions. These levels and 20 seeds
are an illustrative design, not empirical estimates or a power calculation.

The comparator is unrestricted development, with each paired difference defined as
**reciprocal minus unrestricted** at the same seed. Keyed draws are paired; event
realization and subsequent behavior may differ. Keep every terminal run. A cancelled
comparison fails this protocol and must not be reported as complete.

## Outcomes and interpretation fixed in advance

Report service, control and misuse incidents, cooperation, denial, privacy, appeal
success and appeal resolution. Preserve all other scalar metrics and every group's
service, service per population, denial, privacy and incidents in the generated tables.
Show each policy's mean, its 95% normal-approximation Monte Carlo interval and valid
sample count, together with the paired difference and its own valid-pair count.

An undefined denominator stays `null`; it is excluded only from that metric's sample
count. In particular, unrestricted development may have no active-rule periods,
audits or appeals: the corresponding paired contrast is undefined, not zero. Denial
includes allocation choices, not just sanctions. Privacy is exposure **per audit
record**, not total records exposed. Appeal success excludes pending/timed-out appeals;
appeal resolution uses all filed appeals. Group population weights are synthetic.
These are means of per-run ratios, not pooled ratios over all runs.

Compare the four condition-specific policy differences side by side; do not pool
conditions or treat variation between them as Monte Carlo uncertainty. Normal
intervals at 20 seeds can have poor coverage, especially for rare incident counts.
No hypothesis tests, multiplicity claims, policy ranking or scalar welfare score.
Keep null, negative and ambiguous findings. A zero observed count is not proof of
zero underlying hazard.

The main interpretive threat is attributing a policy difference solely to report
accuracy: changing false-positive likelihoods also changes actors' Bayesian evidence
updates; shared failures change audits, budgets and the evidence stream. This design
measures their combined within-model consequences, not a mediation decomposition.
Two parameter levels do not establish monotonicity or robustness outside this grid.

## Evidence and pass/fail check

The raw materials are the resolved S2 scenario, kernel transitions and metric
denominators in `src/isobar/engine.py`, paired summaries in
`src/isobar/experiments.py`, and complete simulated traces. Reuse those interfaces;
do not implement a second simulator or introduce a statistics dependency.

The generator must retain four complete comparison reports, including resolved
scenarios, all seeds, per-run metrics/digests and source/runtime identity. Record the
Git checkout revision, SHA-256 of the generator, this protocol and the dependency lock.
Require the kernel and dependency lock to match that commit; separately hash the
study additions even when they have not yet been committed.
Replay-verify **all 160** regenerated full runs against the saved summaries. Retain
the seed-0 full bundle for both policies in all four conditions, chosen in advance
without regard to its outcomes. Generate tables only from saved reports.

Pass: two fresh executions reproduce every generated file byte for byte on the same
source/runtime; all 160 policy/seed records match their regenerated status, metrics
and trace digests; every full bundle passes `verify_bundle`; all tables show valid
sample counts and all groups. Any missing/duplicate run, invalid status, mismatched
configuration, failed replay, changed artifact or overwritten output fails.
Artifacts are post-run truth. The supplied fixtures are public-classification and
synthetic; publication remains a separate action.

This follows the replication and experiment-description concerns in
[Grimm et al. (2020), ODD](https://www.jasss.org/23/2/7.html). Broader uncertainty
exploration and scenario discovery, as illustrated by the
[EMA Workbench](https://emaworkbench.readthedocs.io/en/latest/indepth_tutorial/open-exploration.html),
are a possible later rung, not a capability or scientific result established here.
Independent methods review, human usability and empirical policy validity remain open.
