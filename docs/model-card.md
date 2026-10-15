# Reference model card

Model identity: `isobar-reference-v1`. RNG: `sha256-keyed-u53-v1`.

This is synthetic research software, not a calibrated description of any country,
verification system or AI development process. Tests establish software behavior.
They do not establish political plausibility, policy desirability, real catastrophe
probabilities or the effectiveness of an institution. No external methods review or
human study is claimed.

## Purpose, entities and scales

The question is conditional: how can imperfect monitoring, strategic work allocation
and institutional remedies affect reciprocal pacing? Six fictional fixtures expose
racing, hidden capacity, temporary freeze residuals, false allegations, non-members
and shocks, and coercive concentration. Four policy families cross four strategies;
the fixtures do not force a preferred institution to win.

Each of 2 to 8 actors aggregates a jurisdiction and its developer. A separate
institution has a budget, temporary mandate, appeal process and latent capture state.
Each jurisdiction has one affected population group. Multiple strategic firms,
coercive military operations, calibrated national utility, bargaining and market
prices are not implemented. Non-member actors receive diffusion and face hazards
but are outside the coalition's training rule and enforcement authority.

Time is a synthetic tick, not a calendar month. Capacity is normalized compute per
tick; capability and readiness are dimensionless indices; service, population and
institutional budget use separate normalized units. No conversion to FLOPs,
accelerators, people, money or a calendar lead is defined.

## Input contract and provenance

`Scenario.model_json_schema()` is the machine-readable contract. Extra fields,
wrong types, nonfinite values, inconsistent identities and unsupported units fail
before simulation. All top-level fields in the implementation contract are required.
Nested synthetic defaults are resolved into the saved scenario, not left implicit.
Positive denominators and capacities are bounded to `[1e-6, 1e6]` to exclude numerical
singularities. Other nonnegative magnitudes are bounded to `[0, 1e6]`; fractions are
`[0, 1]`. Integer limits appear in the schema. Unknown is never silently zero.

Each scenario supplies a nonempty assumptions list with `parameter`, `evidence_type`,
`rationale` and `source`. A blanket synthetic provenance entry is appropriate for
these fixtures. Marking a field measured is an author assertion, not a source check
performed by the kernel. The reference fixtures are entirely synthetic.

An optional `adapter` contains `id`, `source_snapshot`, `review_status` and `notes`.
It requires private classification. An unreviewed mapping produces an explicit
warning. The package contains no organization-specific mapping or private source.
Mapping a design does not test the actual design; design-owner review and justified
parameters remain separate research obligations. Public export refuses private
classification regardless of whether the current view is public.

### Actor parameters

| Fields | Meaning |
|---|---|
| `id`, `name` | Stable synthetic identity and display label; IDs must be unique |
| `strategy`, `member` | One of four classical strategies; coalition rule coverage |
| `declared_capacity`, `hidden_capacity` | Nonoverlapping physical capacity pools; enforcement reaches only declared capacity |
| `capability`, `safety` | Initial capability and safety-readiness indices; initial values are public in this model |
| `population`, `demand` | Synthetic population weight and benign service requested per tick |
| `capability_weight`, `service_weight`, `safety_weight` | Explicit one-period utility coefficients, not estimates of government preferences |
| `sanction_weight`, `concealment_cost` | Expected restriction cost and concealment disutility in the strategy's utility model; no monetary wealth account |
| `temperature` | Bounded-response inverse temperature, 0 to 100; zero gives uniform choice over the listed grid entries |
| `belief_prior`, `belief_learning` | Initial probability of rival deviation; disable Bayesian updates and forgetting for a no-learning control |
| `reciprocity_threshold`, `forgiveness` | Retaliation threshold and per-tick shrinkage of posterior back toward the initial prior |

### Policy, verification and institutional parameters

| Fields | Meaning |
|---|---|
| `policy.family` | `unrestricted`, `voluntary`, `reciprocal`, `freeze` |
| `cap_fraction` | Training cap as a fraction of initial declared capacity, zero under freeze |
| `activation_tick`, `activation_delay` | Tick of an exogenous public warning and delay to legal effect; not a truth-state hazard trigger |
| `duration`, `renewals_allowed` | Mandate duration and whether a recorded prior-tick member majority may renew it |
| `exception_per_tick`, `exception_total` | Per-actor absolute training allowance and cumulative cap; allowances are consumed once, never added to physical capacity |
| `restart_clear_ticks`, `restart_gap` | Consecutive declared-work review threshold required before an explicit member restart vote can take effect |
| `verification.coverage`, `audit_rate` | Conditional probability a work sample is reachable, then audited; concealment multiplies reachability by `1 - 0.5 * conceal` |
| `sensitivity`, `false_positive_rate` | Flag probabilities conditional on an actual breach or compliance |
| `delay`, `record_loss` | Delivery delay and probability of losing a generated report; even delay zero delivers next tick |
| `monitors`, `shared_root_failure` | Number of monitors and per-tick common-root failure probability shared across every actor and monitor |
| `privacy_exposure`, `audit_cost` | Exposed-record fraction and budget cost per performed audit |
| `strength` | Modeled claim-strength label only; no real cryptography, hardware attestations or signatures are generated |
| `institution.response_delay` | Delay from decision to enforcement attempt, at least one effective tick |
| `appeal_delay`, `appeal_independence`, `review_accuracy` | Review deadline, probability review is independent, and accuracy of a new independent review sample |
| `sanction_capacity`, `sanction_duration`, `enforcement_success` | Restricted share of declared capacity, duration, and success probability of an attempt |
| `budget`, `enforcement_cost`, `review_cost` | Available normalized resources and actual costs charged for attempts/reviews |
| `authority_concentration`, `capture_rate`, `capture_cost` | Initial authority concentration; probability and budget cost of a persistent capture shock |
| `disclosure` | Probability a decision is publicly inspectable; undisclosed decisions are visible to their subject |

### Dynamics parameters

| Fields | Meaning |
|---|---|
| `progress_rate`, `safety_rate`, `safety_decay`, `reference_capacity` | Coefficients and scale of the progress equations below |
| `readiness_threshold` | Assumed offset between capability and readiness indices |
| `hazard`, `control_base`, `control_growth` | Control-incident structural family and rate coefficients |
| `misuse_base` | Independent deployed-capability misuse rate coefficient |
| `service_value`, `diffusion` | Benefit per fulfilled service unit and external capability transfer per tick |
| `efficiency_shock_tick`, `efficiency_multiplier`, `diffusion_shock` | Tick and magnitude of an exogenous, persistent work-efficiency and diffusion change |
| `terminal_on_control` | Stop after the tick containing a control incident; all actors finish that simultaneous tick |
| `false_allegation_tick`, `false_allegation_actor` | Optional paired fields injecting an independent positive report; it is false only if the subject actually complied in that period |

## Scheduling and submodels

1. Deliver due reports and appeal findings. Apply paid enforcement attempts and
   restore expired or overturned restrictions. Separate cases remain separate.
2. Apply mandate expiry, recorded majority renewal, reviewed restart, activation,
   exogenous efficiency/diffusion shock and capture shock.
3. Freeze all actor observations. Choose all actions before applying any of them.
4. Apply work, progress, service and hazards. Sample monitors and queue reports.
5. File requested appeals against delivered decisions, update beliefs and record
   the period. Check a terminal condition after the simultaneous period completes.

Sorted immutable actor IDs resolve ties. Reordering input actors leaves the full
canonical result unchanged. Due items are ordered by stable causal event ID. New
evidence and enforcement never take effect within the generating tick. The mandate
controls new work; case adjudication and temporary remedies for work during the
mandate continue after its expiry.

An `Action` allocates fractions to `train`, `safety`, `service`, `idle`, summing to
one within numerical tolerance. `conceal` affects reporting and monitor reachability;
it does not create capacity. `inspect` permits or denies audit access. `appeal`,
`renew` and `request_restart` are explicit institutional choices. Invalid, missing,
late/refused or malformed supplied actions use the labeled all-idle fallback;
unknown actor/tick addresses reject the run rather than silently ignoring a record.

Active restrictions remove the **maximum** applicable restricted fraction of
declared capacity, not the sum: separate cases cannot remove the same capacity twice.
Hidden capacity stays accessible. Law alone removes no physical work. A feasible
violation is executed and recorded as a breach. Voluntary rules generate reports
but no compulsory restrictions. Concealment disutility affects strategy choice;
there is no additional physical concealment-work submodel in this version.

For actual training work `T`, safety work `S`, efficiency `e`, reference `K` and
external diffusion `d`, the transitions are:

```
c_next = c + progress_rate * log(1 + e * T / K) + d
s_next = max(0, s + safety_rate * log(1 + S / K) - safety_decay)
gap = max(0, c_next - s_next - readiness_threshold)
service = min(service_work, demand)
```

Declared capability and readiness estimates use declared available work only,
with concealed training removed. They are reports, not measurements of latent
capability. Safety work, existing capability, service and external diffusion survive
a freeze. Capability is a scalar proxy, not general intelligence or alignment.

Control hazard is one of `base * exp(min(50, growth * gap))`,
`base * (1 + 20 * I(gap > 1))`, or `base`. Incident probability is
`1 - exp(-hazard)`. The exponential cap is numerical protection, not empirical
evidence. Misuse hazard is `misuse_base * c * (service / demand) / (1 + s)`.
Incidents are distinct synthetic counts, not calibrated risk forecasts. Terminated
runs retain their partial benefits and harms and must remain in ensemble denominators.

## Strategies, beliefs and evidence

Compliant actors allocate no more than the legal training allowance, with the rest
split between safety and service. Reciprocal actors do the same until their largest
rival deviation posterior exceeds the threshold, then use a fixed retaliatory
allocation. Myopic actors maximize one-period utility over the finite grid in
`strategies.py`; bounded actors use a stable softmax on the same grid. There is no
multi-step optimizer or equilibrium claim.

The reduced belief model is a binary categorical distribution over rival
compliance/deviation, updated with the configured flag likelihoods. It does not
infer a hidden-capacity bin or actual rival strategy. A zero-likelihood observation
retains the prior and emits a misspecification event. No-learning disables both
updates and forgetting. All strategy inputs are their own state, accumulated
beliefs, public rule and declared model assumptions; no rival truth, environment
seed, future shock or same-tick action is passed to `choose`.

An allegation and a case finding are distinct events. The reference decision rule
is deliberately simple and explicit: one delivered positive report substantiates
a case. Negative, missing and denied-access reports are retained, and denied access
alone never proves a violation. Conflicting reports are not silently discarded,
but there is no learned evidence fusion in this model. The rule's weakness is a
testable institutional assumption, not an endorsement.

An appeal samples a new review using `review_accuracy`, and only independent review
can overturn a finding. Capture suppresses effective independence without removing
the nominal right to file. Unfunded appeals time out. Each finding, enforcement,
appeal and restoration retains causal event IDs. Multiple cases may restrict the
same actor; overturning one does not remove the others. Public explanations remove
links to events unavailable in that view.

## Metrics and observation boundaries

| Metric | Denominator or interpretation |
|---|---|
| `control_incidents`, `misuse_incidents` | Cumulative synthetic actor incidents through completed ticks |
| `service_total` | Sum of `service_value * fulfilled_service` |
| `denial_fraction` | Unfulfilled benign demand / requested benign demand; includes forgone service from allocation choices, not just coercion |
| `privacy_fraction` | Sum of configured exposed-record fractions / audit records created |
| `appeal_success_fraction` | Overturned appeals / resolved appeals; timed-out and pending appeals are excluded here but included in resolution denominator |
| `appeal_resolution_fraction` | Resolved appeals / filed appeals |
| `breaches` | Actual violating actor-periods, not allegations |
| `cooperation_fraction` | Compliant member-periods / active-rule member-periods |
| `power_concentration` | Sum of squared true compute shares, separate from institutional authority |
| `authority_concentration` | Configured authority concentration, raised to at least 0.95 after modeled capture |
| `auditability_fraction` | Publicly inspectable decisions / all decisions |
| `readiness_gap` | Maximum true current capability/readiness gap across actors |
| `distribution` | Service, service per population weight, denial, privacy and incident counts for each synthetic group |

An empty denominator is `null`, not zero. There is no total welfare or freedom score
and no implicit exchange rate between restrictions and incidents.

Truth is explicitly labeled post-run research inspection. Public/actor projections
filter the scenario, action logs, events, frames, metrics and branch lineage. Another
actor's hidden capacity, strategy, utility, actions and beliefs are absent. Public
capability/readiness are declared-work estimates. The selected actor may see its
own state and private notices. Latent metrics, capture state, dynamic authority
concentration and covert budget changes are withheld. A projected result is not a
replay artifact; only the local full result can support verified replay.

Free-form scenario narrative, assumption records and adapter metadata are also
researcher-only: they may describe hidden inputs. Actor display labels are declared
public. A nontruth projection gets an identity hash computed only after redaction;
it does not expose the truth-config hash or parent run identity. Researcher setup
may separately show complete assumptions, but that is not part of an actor view.

## Randomness, reproduction and acceptance

Every draw hashes `(rng_version, seed, tick, actor, process, index)` with SHA-256 and
maps the top 53 bits to `[0, 1)`. Audit, common-root, strategy, control, misuse,
enforcement, disclosure and review processes use separate keys. Adding a monitor
does not shift an unrelated incident's random variate. A common root affects all
monitors in the tick; repeated monitors do not assume unconditional independence.
Case decisions, enforcement and review use the stable subject/period/monitor key,
not a global case count. Additional reports therefore do not move an existing
case's random stream. They may legitimately change budgets, evidence and behavior.

Canonical JSON hashes identify config, trace and metrics. They prove identity,
not correctness or external attestation. `input_actions` preserves requested
overrides, including invalid payloads and fallback notices; nonfinite invalid
numbers are represented as invalid strings for JSON-safe replay. Realized `actions`
also support offline execution but do not recreate original invalid-input notices.
Branches preserve the parent's prefix and recorded lineage. Cancellation records
the completed prefix; resumption replays and verifies it before continuation.
Lineage is limited to 16 nested interventions; branch creation rejects a seventeenth
so every accepted branch remains within the artifact replay depth limit.

The locked reference environment is the reproduction boundary. Cross-platform
floating-point and math-library bit identity is not promised. The test suite covers
input failure, all scenario/policy/strategy fixtures, accounting, deterministic
order, observations, delays, false flags, appeals/restoration, budget limits, freeze
residuals, capture, shared failures, paired exogenous randomness and extreme valid
inputs. The exact deterrence identity is checked analytically. Reproducing an
external published simulator, empirical calibration, independent methods review
and a human usability study remain separate research work, not accomplished by
these checks.
