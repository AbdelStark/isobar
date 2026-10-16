# Earth explorer iteration

User objective: make Isobar a visual, planet-scale simulator with nation states and
visible dynamics of power, factors, strategies and game theory.

Acceptance for this iteration:

- An offline Earth globe and world map with real country outlines, selectable modeled
  nations, rotation/zoom controls, legends and an accessible nation list.
- A new eight-country scenario, using real geographic labels and explicitly synthetic
  parameters. Existing six fictional scenarios and saved v1 outputs remain compatible.
- Timeline-linked capability shares, readiness, service, institutional activity and
  coalition membership; values derive from the selected observation boundary.
- A nation inspector with trajectories, relationships and actual work allocations.
- A decision inspector using the kernel's pre-decision observations and shared utility
  calculation to expose incentives, expected costs and bounded-choice probabilities.
  Public views cannot obtain private decision information.
- Geographic selection connects to observation switching and human interventions;
  existing paired-policy comparison, export/replay and failure recovery still work.
- Desktop/mobile visual review, meaningful numerical/privacy regressions, real-browser
  workflows and accessibility scans, isolated package check and exact-commit CI.

The geography is presentation data, not a causal input. Values are illustrative,
not national statistics, forecasts, measured national power or actual government
preferences. Avoid inventing alliances or game equilibria to decorate the map.

Scope reaches scenarios/catalog, strategy scoring, engine instrumentation, HTTP,
frontend map/inspector, fixtures, packaging, documentation and acceptance evidence.
Keep the existing simulation equations, schema and deterministic outputs unchanged.

Completed locally on 2026-10-16. Evidence and limitations are recorded in
[acceptance.md](acceptance.md); operation and map provenance in
[earth-explorer.md](earth-explorer.md). The full browser suite includes stale-response
rejection and public/private decision boundaries. No model equations or schema
versions changed. Hosted verification is checked at the published commit.
