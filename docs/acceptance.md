# MVP acceptance record

Checked locally on 2026-10-16. Status: **software MVP, Earth iteration and validation hardening accepted locally** against
[F1–F12 in the implementation contract](mvp-contract.md). All three gates in
`make verify` pass: kernel/frontend checks, real-server browser workflows, and an
isolated wheel installation. Scientific acceptance is a separate obligation below.

## Requirement evidence

Test paths below are relative to the repository root. Tests were inspected for the
assertions they make, not counted as proof merely because they pass.

| Requirement | Current evidence | Boundary |
|---|---|---|
| F1: versioned inputs | `tests/test_models.py`: catalog round-trip/freshness, finite types/ranges, units, IDs, cross-field constraints, unknown-field rejection. Browser JSON authoring validates, resolves defaults and renders hostile strings as text. | Provenance labels do not verify source quality. |
| F2: replace policies/strategies | `test_policy_strategy_cross_product`: all 16 combinations; `test_alternative_hazards_and_terminal_accounting`: three hazards. | Finite myopic grid, not an equilibrium solver. |
| F3: separate observations | Projection, hidden-state, capture, narrative/digest and no-lookahead regressions in `tests/test_engine.py`; browser switches public → truth → actor → public, including a branch. | Researcher setup and truth exports intentionally contain hidden state; this is not multiplayer access control. |
| F4: policy lifecycle | Engine tests exercise delayed activation, exceptions, expiry, majority renewal, reviewed restart, late reports and residual misuse. | Warning and shocks are exogenous synthetic inputs. |
| F5/F9: evidence/explanation | Perfect/zero detection, shared-root failure, denied inspection, false allegations, causal appeals/restoration, budget exhaustion, capture and monitor-count independence tests. The browser renders the evidence timeline and causal records. | One-positive-report decision rule; no learned evidence fusion. |
| F6: outcome vectors | Terminal accounting, null-denominator and per-group paired-delta regressions; browser comparison renders intervals, tables and group outcomes. Definitions live in the model card. | One population group per jurisdiction; no empirical welfare score. |
| F7: paired ensembles/branches | `tests/test_experiments.py` checks exact matched-seed deltas, group deltas, cache rejection and resumed/fresh equality. Branch tests preserve parent history and replay 16 nested interventions; browser branches, changes views and exports. | Conditional Monte Carlo uncertainty only. |
| F8: private adapter | Model tests reject public adapter mappings; engine warns on unreviewed mappings; artifact, HTTP and browser tests reject private public-classification exports. | Organization-specific sources stay outside the repo; owner review gates design attribution. |
| F10: visual exploration | Fifteen Chromium tests in `web/tests/` cover seven presets, globe/map rotation, zoom, geographic and keyboard selection, layer changes, tick-linked shares, private beliefs, decision payoffs, intervention explanation, stale-response rejection, branching, comparison, downloads and recovery. Desktop and 390px renders inspected; axe scans pass in initial, public replay, truth/comparison and authoring states at both widths. | Chromium acceptance; no screen-reader certification or human usability study. |
| F11: human/model actions | Invalid-action fallback, override-address and offline-replay tests; browser rejects nonconserving allocations then submits a valid human action through the kernel. | Offline structured model actions only; no hosted inference, RL training or uploaded code. |
| F12: reproduce/export | Full-result replay rejects forged checksums, identities and lineage; cancelled runs and batches resume. `scripts/check_package.py` verifies installed CLI lifecycle, bundled assets and HTTP export → CLI replay. Concurrent save regression proves exactly one writer succeeds without overwriting another result. | Checksums are not signatures. Resume requires matching source/runtime identity. |

The six fictional fixtures cover racing, hidden capacity, freeze residuals, false
allegations, non-member leakage/shocks, and concentrated/captured enforcement. The
additional world fixture places eight synthetic actors on bundled Natural Earth
geometry. `tests/test_decisions.py` checks copied diagnostic observations, actual
chosen actions, utility decomposition, bounded probabilities, private-rival invariance
and nested overrides. HTTP tests reject private incentives from public/rival views. The
12 analytic-baseline tests include independent numerical integration of a separate
published race-game formula; they do not validate the dynamic model's equilibria.

## Executed gates

- `make verify`: 173 Python tests, eight frontend unit tests, fifteen real-server browser
  tests, Ruff, formatting, mypy, and TypeScript checking of app, tests and configs.
- The package gate builds a fresh source archive/wheel and installs the wheel with
  hashed, locked runtime dependencies in a temporary Python 3.12 environment outside
  the checkout. It checks catalog, schema, validation, cancellation/resume, replay,
  branch, export, interrupted/resumed comparisons, overwrite rejection, static
  assets/third-party notices and world HTTP run/decision/export/replay. It asserts
  imports resolve inside that environment.
- Browser tests use production assets and a fresh loopback server, with no successful
  API mocks. Fault injection tests startup and request recovery. All preset requests
  stay local. Reports, accessibility scans and screenshots are generated under
  `web/playwright-report/` and `web/test-results/`; failure traces are retained.
- Regenerating bundled geography from its pinned, checksum-verified source produces
  byte-identical JSON. Its 177 geographic features do not enter model dynamics.
- HTTP tests cover host/origin restrictions, traversal, content type, body size,
  malformed/nonfinite JSON, classification and intervention reconstruction.
- `npm audit` (including development dependencies) and `pip-audit --disable-pip
  --no-deps` against the complete locked runtime export reported no known
  vulnerabilities on 2026-10-16. These are advisory checks, not security proofs.
- All three repository skills pass the skill-creator frontmatter validator. The model
  and verification workflows were exercised by the gates above; the documented
  [experiment smoke check](research-foundations.md#workflow-smoke-check) saved and
  regenerated 16 policy/seed runs across two conditions, checked environment identity,
  and replay-verified full traces. `AGENTS.md` routes to the maintained sources and
  [roadmap](roadmap.md). This is workflow validation, not a measured productivity claim.
- CI uses pinned action commits, read-only repository permissions, a timeout, and the
  same `make verify` gate. Synthetic browser evidence is retained for 14 days. See
  [workflow runs](https://github.com/AbdelStark/isobar/actions/workflows/check.yml)
  for hosted status at a particular commit; local success does not imply hosted success.

The 2026-10-16 changes add Earth exploration, a synthetic fixture, observational
decision instrumentation, keyboard focus and artifact write safety. Existing model
dynamics and serialized run fields remain unchanged. All six original full preset
results matched a saved pre-refactor capture exactly on the development runtime.
Model `isobar-reference-v1`, scenario schema 1 and
artifact schema 1 remain unchanged. Source-identity checks still reject resuming
checkpoints created by different code; complete artifacts remain replay-verified.

## Public-workbench quality review

The subsequent 2026-10-16 review reproduced three boundary defects before fixing them:
actor IDs `public`/`truth` collided with observation modes, boolean/float artifact
versions were accepted as integer 1, and malformed checkpoint environments raised
an uncaught `AttributeError`. Model/artifact/batch regressions now reject these inputs;
HTTP returns 422 for reserved actor IDs, and CLI resume exits 2 with an actionable
error while preserving the input and leaving the output absent. The new regressions
failed against the previous implementation, then passed with the validation fixes.

Comparison reports now include runtime/source identity. The README describes their
`runs` entries as metrics/digest summaries, rather than full replay bundles. The
isolated-package gate also checks the wheel's MIT expression, license-file metadata
and license contents. No new runtime dependency or agent-provider integration was added.

All seven complete default fixture outputs matched canonical pre-change hashes on
the same development runtime. Model `isobar-reference-v1`, scenario schema 1 and
artifact schema 1 remain unchanged: equations, scheduling and valid run serialization
are preserved; comparison `environment` metadata is additive. Validation is tighter:
custom scenarios using reserved actor IDs must rename those actors and their references.
Source identity changed, so existing checkpoints require their original code to resume;
do not rewrite checkpoint identities to bypass that check.

The roadmap records the next sensitivity study and separates software verification
from independent methods review, new-reader usability and release publication. The
smoke experiment is not the proposed study and does not satisfy those external gates.

A browser quality pass reproduced and fixed unreadable HTTP 200 responses replacing
a valid replay and renamed actors retaining stale observation labels. The real-server
regressions check replay preservation, retry and both observation selectors. The
outcome table and comparison selector now expose the kernel's existing authority
concentration metric alongside compute concentration; public projections still withhold
both. The pass also removes unused browser action state and the completed Earth plan,
documents generated assets, and makes CI read the Node range from `web/package.json`.
Locked dependency versions and Python model behavior are unchanged.

## Workbench polish

The 2026-10-16 interface pass preserves the paper-and-olive identity and model copy.
It aligns paired controls and numeric table columns, enlarges disclosures and mobile
inputs, distinguishes post-run truth beside the map, and repairs tablet sidebar
spacing. Comparison charts reflow when their container changes width, retaining
readable labels and all policy points. The masthead now uses the bundled wave mark.

`make check` passed with 173 Python tests, eight frontend tests, lint, formatting and
type checks. `make check-browser` passed all fifteen real-server Chromium tests,
including axe scans, numeric/missing-value alignment, chart resizing, observation
boundaries, recovery, branching and export. Setup, replay, decision and comparison
captures covered 1440, 768, 390 and 320px; desktop, tablet and mobile renders were
inspected. No page overflow was detected, and a long actor name also remained
contained at 390px. Local confirmation captures are
under `web/test-results/polish/`. The Impeccable mechanical scan reported no findings,
and `web/scripts/capture-readme.mjs` refreshed the two reviewed README images.
Packaging, other browser engines and physical touch devices were not rechecked in
this interface-only pass. This is software/UI evidence, not human usability or
scientific validation.

## Measured reference performance

2026-10-16, Apple M4 Max, macOS arm64, Python 3.12.12. Sixty in-process runs: six
presets, seeds 0–9, horizon 120. Scenario validation was outside the timed interval;
simulation, result construction and digesting were inside. Median 17.1 ms,
nearest-rank p95 31.7 ms, maximum 34.2 ms. These are local smoke measurements under
concurrent test load, not cross-device latency guarantees. Browser interaction
latency has not been benchmarked. These timings predate the eight-actor world fixture
and do not measure decision-inspection reexecution.

## Scientific acceptance is separate

The [S2 monitoring sensitivity study](studies/s2-monitoring/README.md) completes the
roadmap's worked research path locally on 2026-10-16. Its prospective protocol fixes
four monitoring conditions, two policies and seeds 0–19. Two fresh executions of
`uv run --locked python scripts/sensitivity_study.py <fresh-directory>` each regenerated
and replay-verified all 160 runs; `diff -r` found all 14 output files byte-identical.
Four saved comparisons retain every seed, resolved scenario, per-run metrics/digests
and runtime/source identity; eight prespecified seed-0 full bundles support inspection.
The manifest identifies the kernel revision and hashes the generator/protocol/lock
and every output. Tables are generated from saved reports, including missing
denominators, valid-pair counts and all group outcomes.

`make check` passed (173 Python tests, eight frontend tests, lint, formatting and type
checks). Study self-checks verify input identity, run coverage, statuses, replay,
means and denominators; deliberate missing-run, digest and sample-count corruption
was rejected. Existing output was refused without changing its contents. Browser
and isolated-package gates were not rerun for this script/documentation addition.
Kernel, fixtures, model/schema versions and dependencies are unchanged. This is a
reproducible synthetic result, not independent methods review or scientific validation.

The implementation aggregates a state and its developer into one actor, uses binary
compliance beliefs, synthetic scalar hazards and a budgeted institution. It omits
independent strategic firms, bargaining, learned agent training, empirical calibration,
a multi-bin hidden-capacity posterior and a full technical verification-system emulator.
These are explicit reductions, not implemented features hidden behind UI controls.

Independent methods review, review of any private mapping, the proposed five-participant
usability exercise, empirical validation and policy recommendations remain separate
research work. The application is local-only; no hosted deployment is claimed.
