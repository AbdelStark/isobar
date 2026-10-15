# MVP acceptance record

Checked locally on 2026-10-15. Status: **headless implementation verified; final live-browser acceptance pending**. The source and browser bundle are runnable, but this record does not mark the whole MVP accepted until that remaining check is completed.

## Functional evidence

| Requirement | Implemented evidence | Remaining boundary |
|---|---|---|
| F1: versioned inputs | Strict scenario/action models; 32 input-model tests; resolved defaults, units, provenance and finite values | Source quality is not automatically verified |
| F2: replace policies/strategies | Four policy families crossed with four strategies in kernel tests; three hazard alternatives | Finite myopic grid, not an equilibrium solver |
| F3: separate observations | Hidden-state and capture isolation tests, redacted narratives/digests/lineage, actor-order and no-lookahead tests | Live UI boundary workflow pending; researcher configuration is not an actor view |
| F4: policy lifecycle | Trigger, delayed activation, exceptions, expiry, majority renewal, reviewed restart, residual misuse | Warning and shocks are exogenous synthetic inputs |
| F5/F9: evidence and explanation | Independent reports, denied access, false allegations, causal decisions, paid enforcement, appeals and restoration | One-positive-report decision rule; no learned evidence fusion |
| F6: outcome vectors | Defined denominators, null handling, terminal accounting; paired overall and per-group summaries | One population group per jurisdiction; no empirical welfare score |
| F7: paired ensembles/branches | Exact paired-delta tests, checked batch resumption, immutable parent prefix and up to 16 replayable interventions | Conditional Monte Carlo uncertainty only |
| F8: private adapter boundary | Private-only adapter metadata, unreviewed warning and public-export denial tests | Organization-specific sources/mappings stay outside this repo; owner review gates design attribution |
| F10: visual exploration | Responsive workbench, four panels, saved-frame playback, keyboard labels/focus, table alternatives, error states; build and unit tests pass | Four live-browser specs authored but final run, mobile visual inspection and accessibility verification pending |
| F11: human/model actions | Same validated structured action contract, recorded overrides and invalid-action fallback; branch API tested | Offline model-action records only; no hosted inference, RL training or untrusted plugin execution |
| F12: reproduce/export | Full-result deterministic replay, forged-checksum/provenance rejection, cancelled-run and batch resume; isolated wheel/CLI checks | Identity checks are not signatures or scientific validation |

The six fixtures cover racing, reciprocal pacing with hidden capacity, freeze residuals, false allegations, non-member leakage/shocks, and concentrated/captured enforcement. All are fictional. The separate published race-game formula check has 12 tests, including independent numerical integration; it does not establish that the dynamic model reproduces that game's equilibria.

## Executed checks

- `make check`: 136 Python tests, six frontend unit tests, Ruff, formatting, mypy and TypeScript/Vite build pass.
- `pytest --cov=isobar`: 85% statement coverage. CLI tests execute subprocesses, which this coverage invocation does not count; the CLI is additionally checked from an isolated wheel installation. Coverage is not a validity score.
- `make build`: wheel and source archive built; wheel includes kernel, type marker, HTML, favicon, CSS and JS.
- Isolated Python 3.12 wheel installation, outside the checkout: catalog, schema, validate, run, replay, resume, branch, public export, interrupted/resumed comparison, and loopback serving of bundled assets checked.
- `npm audit`, including development dependencies: no known vulnerabilities reported. `pip-audit` on the locked runtime dependencies: no known vulnerabilities reported. This is a point-in-time advisory check, not a security proof.
- HTTP tests cover loopback host/origin restrictions, path traversal, content validation, private export and nested intervention reconstruction. No external deployment exists.

One earlier desktop screenshot was inspected for layout. The initial browser test was stopped and does not count as a passed suite. Final browser execution requires owner approval because the connected browser surface blocks localhost. No automated accessibility certification, screen-reader pass or human usability study is claimed. Hosted CI status is recorded by the repository's workflow runs, not inferred from these local results.

## Measured reference performance

Apple M4 Max, macOS 26.6.2 arm64, Python 3.12.12. Sixty in-process kernel runs: six presets, seeds 0 through 9, each extended to 120 ticks. Scenario validation was outside the timed interval; result construction and digesting were inside it. Median 16.0 ms, nearest-rank p95 24.5 ms, maximum 27.6 ms. These are a local smoke benchmark, not a cross-device guarantee. Browser interaction latency has not been measured.

## Scientific acceptance is separate

The implementation aggregates a state and its developer into one actor, uses binary compliance beliefs, synthetic scalar hazards and a budgeted institution. It omits independent strategic firms, bargaining, learned agent training, empirical calibration, a multi-bin hidden-capacity posterior and a full technical verification-system emulator. These are explicit reductions, not implemented features hidden behind UI controls.

Independent methods review, design-owner review of a private mapping, the proposed five-participant usability exercise, empirical validation and any policy recommendation remain separate research work. No amount of passing software tests supplies that evidence.
