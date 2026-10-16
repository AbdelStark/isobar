# MVP implementation contract

Status: implemented; software acceptance is tracked in [the acceptance record](acceptance.md).
Synthetic, uncalibrated research software, distributed under the MIT license; no embedded private
company documents or organization-specific mechanisms. A local-only adapter can map
a private design using generic parameters without publishing that mapping.

## Scope and acceptance

The complete MVP covers versioned validated inputs (F1), four interchangeable policies and four classical strategies (F2), true/actor/public view separation (F3), activation/expiry/renewal/restart and exceptions (F4), evidence/disputes/appeals with causal IDs (F5/F9), disaggregated outcome vectors (F6), paired ensembles and counterfactual branches (F7), generic verification configuration and private export denial (F8), a working local visual explorer with guided human action (F10/F11), and deterministic artifacts, offline action replay, cancellation and resumption (F12).

Scenarios: S1 racing; S2 reciprocal pacing with hidden capacity; S3 emergency freeze and residual misuse; S4 false allegations and appeals; S5 non-member leakage and efficiency/diffusion shock; S6 centralized enforcement, coercion and capture. S1–S6 use fictional actors and explicit synthetic assumptions. The additional `world` fixture uses eight real geographic labels with invented national parameters; it changes no dynamics. No preferred mechanism must win.

Classical strategies: compliant, reciprocal, myopic and bounded. Policies: unrestricted, voluntary, reciprocal, freeze. Hazards: exponential, threshold and flat. Distinguish physical feasibility from legal compliance. Maintain declared/hidden work separately, no same-tick lookahead, independent keyed random streams. Local model-driven actions use recorded structured actions through the same validation as human actions. No hosted inference calls are needed or authorized.

Scientific limits: software tests prove implementation behavior only. External review, a human study, empirical calibration and government forecasts are not supplied by this MVP. Document these as remaining research obligations, never completed tests.

## Python domain interface (stable integration boundary)

`from isobar.models import Scenario, Action`

Pydantic v2 models, strict finite numeric validation, extra keys forbidden. `Scenario.model_validate(dict)` and `model_dump(mode="json")`. Required top-level fields: `schema_version: 1`, `id`, `name`, `description`, `question`, `classification: public|private`, `seed: int`, `horizon: int (1..240)`, `units`, `assumptions`, `actors`, `policy`, `verification`, `institution`, `dynamics`. Built-in presets supply all fields, including explicit units/provenance. Nested fields are defined by the generated Scenario schema and documented in the model card.

Policy config includes `family` with the four values above. Each actor has `id`, `name`, `strategy`, `member`, `declared_capacity`, `hidden_capacity`, `capability`, `safety`, `population`; other necessary values explicit with synthetic defaults. IDs unique; 2..8 actors. Missing units and unknown units fail. All parameters documented in model card. No eval/import from scenario data.

Action: normalized fractions `train`, `safety`, `service`, `idle` (sum 1, nonnegative), `conceal` (0..1), and boolean `appeal`, `inspect`, `renew`, `request_restart` choices. All physical actions run through one validated contract. A supplied invalid action results in a labeled no-action fallback and an event; malformed scenario fails before running.

`from isobar.scenarios import catalog, get_scenario`

- `catalog() -> list[dict]`: list of complete serializable Scenario dictionaries (seven presets).
- `get_scenario(id: str) -> Scenario`: fresh preset instance, unknown ID raises ValueError.

`from isobar.engine import simulate, project, branch, deterrence_payoff`

- `simulate(scenario: Scenario, *, actions: dict | None = None, stop_at: int | None = None, on_decision: Callable | None = None) -> dict`: JSON-safe result; `actions` keys `"<tick>:<actor_id>"`, values Action dict or invalid payload. Tick decisions start at 0. `stop_at` is number of ticks to execute, enabling replay-based checked resumption. No hidden mutable global state. Optional `on_decision(tick, actor_id, observation, action)` receives copies of the pre-action observation and chosen action; it changes no serialized fields.
- `project(result: dict, view: str = "public") -> dict`: `view` is `public`, `truth`, or actor ID. Return filtered run; truth is explicitly labeled post-run. No rival hidden capacity/actions/beliefs/truth-only metrics in actor/public views. Filtering must include scenario/config/events/metrics, not just frames. Never mutate input.
- `branch(result: dict, tick: int, actor_id: str, action: dict) -> dict`: identical history before tick, override action at tick, simulate onward; branch metadata `parent_id`, `tick`, `actor_id`, `action`. Validate actor/tick and immutable parent. Reuse keyed exogenous draws.
- `deterrence_payoff(gain, concealment_cost, probability, credibility, discount, delay, sanction) -> float`: `G-K-p*q*discount**delay*sanction` with finite/range checks.

Result structure:

```
{
  "schema_version": 1, "model_version": "isobar-reference-v1",
  "id": "deterministic-content-id", "status": "completed|cancelled|terminal",
  "scenario": { ... }, "seed": 42, "policy": "reciprocal",
  "completed_ticks": 24, "terminal_cause": null,
  "frames": [{"tick": 0, "actors": [{"id": "aurora", "name": "Aurora", ...}],
              "institution": {...}, "metrics": {...}}],
  "events": [{"id": "e-...", "tick": 1, "kind": "...", "actor_id": null,
              "summary": "...", "causes": [], "visibility": "public|truth|actor:<id>",
              "data": {...}}],
  "metrics": {"control_incidents": 0, "misuse_incidents": 1, ...},
  "actions": {"0:aurora": {...}}, "warnings": [], "branch": null,
  "digests": {"scenario": "...", "trace": "...", "metrics": "..."}
}
```

Metrics must include `control_incidents`, `misuse_incidents`, `service_total`, `denial_fraction`, `privacy_fraction`, `appeal_success_fraction` (null denominator), `breaches`, `cooperation_fraction`, `power_concentration`, `auditability_fraction`, `readiness_gap`, and per-group `distribution`. Label quantities/units and conditional interpretations. Frames include cumulative metrics and actor capability/safety/service for truth; actor views filter unavailable fields. Public view uses only declared/observed outcomes, never hidden aggregate truth.

## Experiment and HTTP interface

`artifacts.py`: canonical SHA256, atomically persist verified bundles; version/config/trace checks; local-only code/environment identity; `--public` export refuses private classification. Recorded actions reproduce runs offline. Checkpoint stores validated result prefix and config/action/digest identity; resume replays prefix deterministically and verifies before continuation. No pretend serialization of an unvalidated arbitrary Python object.

`experiments.py`: compare policies across matched seeds; paired deltas and uncertainty (Monte Carlo only), not calibrated probability. Include all runs including terminal runs. Structural alternatives reported separately. Validate seed uniqueness, minimum counts and finite metrics. Batch manifests preserve completed items for resume; cancellation status explicit.

HTTP binds `127.0.0.1:4318` only; reject nonlocal Host, foreign Origin, oversized JSON, filesystem traversal. Serve only bundled UI assets, never repository files. No accounts, cloud deployment, remote dependencies, analytics or arbitrary plugin uploads.

- `GET /api/catalog` -> `{scenarios: [...], policies: [four strings], strategies: [four strings], model_version: "isobar-reference-v1"}`
- `GET /api/schema` -> Scenario JSON schema
- `POST /api/run` body `{scenario: Scenario dict, actions?: dict, interventions?: [...], stop_at?: int, view?: "truth|public|<actor>"}` -> projected result. Default view public.
- `POST /api/project` body `{result: full run, view: string}` -> verified filtered result (frontend can instead rerun same scenario with selected view).
- `POST /api/branch` body `{scenario: dict, actions?: dict, interventions?: [...], tick: int, actor_id: string, action: dict, view?: string}` -> branch from the reconstructed parent. API reconstructs truth locally, never trusts client results.
- `POST /api/decision` body `{scenario: dict, actions?: dict, interventions?: [...], tick: int, actor_id: string, view: "truth|<same actor>"}` -> reconstructed pre-action incentives, actual selected action, six candidate payoffs and bounded-choice probabilities. Public and other-actor views return 403. Tick must identify a completed decision. See `decisions.inspect_decision` and `strategies.explain`; no client result is trusted.
- `POST /api/compare` body `{scenario: dict, policies: [...], seeds: [int,...], view: "truth"}` -> `{model_version, paired: true, baseline, seeds, summaries: [{policy,n,metrics:{key:{mean,sd,ci_low,ci_high,n}},distribution:[...]}], differences:[{policy, baseline, metrics:{...},distribution:[...]}], note}`. Explicit truth mode is required. Each distribution row preserves actor identity, population and per-group metric summaries. Maximum 20 seeds, 4 policies, 120 horizon for HTTP.
- `POST /api/export` body `{scenario: dict, actions?: dict, interventions?: [...], public: bool}` -> checked bundle JSON; public export denies private scenarios. Every research export contains post-run truth, even when the browser displays a filtered view.
- Error: HTTP 400/403/413/422 `{error: "actionable message", details?: [...]}`. POST requires JSON. Avoid leaking internal file paths in errors.

An intervention is exactly `{tick, actor_id, action}`. Up to 16 are replayed in order, preserving nested parent lineage across view changes and exports. A partial `stop_at` run cannot also specify interventions. Browser seeds are uint32; the single-run Python/CLI scenario contract additionally accepts integers through `2^63 - 1`.

Browser explorer loads catalog and defaults to `world`, public view. An offline Earth globe/map, capability-share list, trajectory inspector and pre-action decision panel use the selected projection. Geographic IDs are presentation metadata; unmatched fictional actors remain selectable in the list. See the [Earth guide](earth-explorer.md). Explicit button/select enables post-run truth view. Scenario/policy/strategy/seed/horizon and coverage/error/delay controls, advanced JSON editor with validation. Four visible sections: actors, evidence/decisions, outcomes, assumptions. Timeline playback scrubs saved frames; manual action branch at a chosen tick. Ensemble comparison explains paired samples; display a real table alternative to charts. JSON download only via server export. Clear loading/error/empty states and keyboard controls. Mobile works without dropping features. All data rendered as text, not unsanitized HTML.

## Release evidence

Tests for each functional requirement, seven scenario smokes, four policies crossed with four strategies, alternative hazards, deterministic replay, actor-order invariance, zero/perfect detection, false allegations, appeal/restoration, privacy filtering, freeze residuals, shared-root correlation, malformed inputs, CLI command examples, wheel import/CLI, HTTP security, and browser workflows. Browser screenshots and accessibility checks must use the actual running application. Record what was not established, especially scientific validity and independent human usability.
