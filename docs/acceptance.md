# MVP acceptance record

Checked locally on 2026-10-16. Status: **software MVP accepted locally** against
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
| F10: visual exploration | Eight Chromium tests in `web/tests/workbench.spec.ts` cover six presets, four panels, keyboard replay, view filtering, branching, comparison, downloads, JSON authoring, private export and network recovery. Desktop and 390px renders inspected; axe scans pass in initial, public replay, truth/comparison and authoring states at both widths. | Chromium acceptance; no screen-reader certification or human usability study. |
| F11: human/model actions | Invalid-action fallback, override-address and offline-replay tests; browser rejects nonconserving allocations then submits a valid human action through the kernel. | Offline structured model actions only; no hosted inference, RL training or uploaded code. |
| F12: reproduce/export | Full-result replay rejects forged checksums, identities and lineage; cancelled runs and batches resume. `scripts/check_package.py` verifies installed CLI lifecycle, bundled assets and HTTP export → CLI replay. Concurrent save regression proves exactly one writer succeeds without overwriting another result. | Checksums are not signatures. Resume requires matching source/runtime identity. |

The six fictional fixtures cover racing, hidden capacity, freeze residuals, false
allegations, non-member leakage/shocks, and concentrated/captured enforcement. The
12 analytic-baseline tests include independent numerical integration of a separate
published race-game formula; they do not validate the dynamic model's equilibria.

## Executed gates

- `make verify`: 143 Python tests, six frontend unit tests, eight real-server browser
  tests, Ruff, formatting, mypy, and TypeScript checking of app, tests and configs.
- The package gate builds a fresh source archive/wheel and installs the wheel with
  hashed, locked runtime dependencies in a temporary Python 3.12 environment outside
  the checkout. It checks catalog, schema, validation, cancellation/resume, replay,
  branch, export, interrupted/resumed comparisons, overwrite rejection, static
  assets and HTTP export/replay. It asserts imports resolve inside that environment.
- Browser tests use production assets and a fresh loopback server, with no successful
  API mocks. Fault injection tests startup and request recovery. All preset requests
  stay local. Reports, accessibility scans and screenshots are generated under
  `web/playwright-report/` and `web/test-results/`; failure traces are retained.
- HTTP tests cover host/origin restrictions, traversal, content type, body size,
  malformed/nonfinite JSON, classification and intervention reconstruction.
- `npm audit` (including development dependencies) and `pip-audit --disable-pip
  --no-deps` against the complete locked runtime export reported no known
  vulnerabilities on 2026-10-16. These are advisory checks, not security proofs.
- Both repository skills pass the skill-creator frontmatter validator. Their commands
  were exercised by the gates above; `AGENTS.md` links to the existing model/contract
  sources instead of copying them. This is workflow validation, not a measured claim
  about agent productivity.
- CI uses pinned action commits, read-only repository permissions, a timeout, and the
  same `make verify` gate. Synthetic browser evidence is retained for 14 days. See
  [workflow runs](https://github.com/AbdelStark/isobar/actions/workflows/check.yml)
  for hosted status at a particular commit; local success does not imply hosted success.

The 2026-10-16 fixes change keyboard focus and artifact write safety, not model
dynamics or serialized run fields. Model `isobar-reference-v1`, scenario schema 1 and
artifact schema 1 remain unchanged. Source-identity checks still reject resuming
checkpoints created by different code; complete artifacts remain replay-verified.

## Measured reference performance

2026-10-16, Apple M4 Max, macOS arm64, Python 3.12.12. Sixty in-process runs: six
presets, seeds 0–9, horizon 120. Scenario validation was outside the timed interval;
simulation, result construction and digesting were inside. Median 17.1 ms,
nearest-rank p95 31.7 ms, maximum 34.2 ms. These are local smoke measurements under
concurrent test load, not cross-device latency guarantees. Browser interaction
latency has not been benchmarked.

## Scientific acceptance is separate

The implementation aggregates a state and its developer into one actor, uses binary
compliance beliefs, synthetic scalar hazards and a budgeted institution. It omits
independent strategic firms, bargaining, learned agent training, empirical calibration,
a multi-bin hidden-capacity posterior and a full technical verification-system emulator.
These are explicit reductions, not implemented features hidden behind UI controls.

Independent methods review, review of any private mapping, the proposed five-participant
usability exercise, empirical validation and policy recommendations remain separate
research work. The application is local-only; no hosted deployment is claimed.
