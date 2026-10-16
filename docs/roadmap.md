# Direction and completion criteria

Isobar's next milestone is a **reliable, reproducible research workbench**. Finish
the reference model and its evidence path before adding learned agents or richer
geopolitics. The useful product is a clear route from a conditional question to
inspectable assumptions, reproducible comparisons and an explanation of tradeoffs.

The [MVP contract](mvp-contract.md) defines implemented scope;
[acceptance](acceptance.md) records verification. This roadmap defines what to work
on next. A green test suite alone does not complete a research study.

## Assessment, 2026-10-16

| Area | What works | What needs attention |
|---|---|---|
| Model | One deterministic kernel, explicit observation boundaries, separate actions/policies, finite institutional resources. | Synthetic reductions need sensitivity analysis and independent methods review before substantive claims. |
| Exploration | Offline Earth view, trace inspection, decision explanations and branching use the real kernel. | New-reader usability has not been independently tested; map polish must not imply geopolitical calibration. |
| Reproduction | Matched seeds, verified replay, resume, immutable outputs and an isolated package gate. | Validation needs adversarial inputs through callers, not only preset coverage. Reports must retain enough identity to reproduce them. |
| Agent context | A short repository map and focused model/verification skills. | Current module ownership, experiment procedure and release finish criteria must stay discoverable as the project grows. |
| Scientific communication | Model card, primary-source connections and explicit limits. | A worked, reproducible sensitivity study should connect those descriptions to an auditable result. |

The quality review found and addressed reserved actor IDs colliding with view modes,
loosely typed artifact versions and malformed checkpoint metadata escaping as
tracebacks. It also added source/runtime identity to comparison reports and an
automated MIT package check. These are contract corrections; the existing simulation
equations and default fixture results are preserved. Evidence belongs in the
acceptance record, rather than being inferred from this list.

Lessons for further work: test names that cross namespaces; exercise invalid data
through the CLI/HTTP caller; inspect exported contents before describing them; and
check guidance by using it. More documentation or more tests are useful only when
they change a decision or catch a distinct failure.

## Next milestone: one reference sensitivity study

Question: **How do false-positive reports and correlated monitoring failures change
the tradeoff between reciprocal pacing and unrestricted development in S2?**
This studies the specified model; it does not estimate the merits of a real treaty.

Deliverables:

1. A checked-in protocol and small generation script using the existing `compare`
   interface. Fix S2, policies `unrestricted` and `reciprocal`, seeds 0–19, false-positive
   rates 0.01/0.10 and shared-root failure probabilities 0.0/0.3 before reading results.
   These illustrative values and 20 seeds are a demonstration design, not a power
   calculation or empirical estimates.
2. Report service, incidents, cooperation, denial, privacy exposure, appeals and
   per-group differences for every condition. Retain terminal runs, undefined
   denominators and paired sample counts. Separate within-model intervals from the
   differences across sensitivity conditions. Do not collapse outcomes into a winner.
3. Preserve resolved scenarios, seeds, exact revision, environment identity and
   per-run metrics/digests. Regenerate selected full traces and verify replay. Generate
   tables/figures from these artifacts, with one documented command from a clean setup.
4. Explain the result in a short worked example, including negative or ambiguous
   findings and what changing the reduced actor/institution assumptions could alter.

Done means a clean second execution reproduces the reported numbers and selected
trace digests, every reported comparison maps to its inputs, and the interpretation
matches the actual denominators and observation boundary. The
[workflow smoke check](research-foundations.md#workflow-smoke-check) establishes the
mechanics only; it does not complete this study.

## Finish the reference-workbench release

| Gate | Completion evidence | Responsibility |
|---|---|---|
| Software contract | All F1–F12 evidence remains valid; `make verify` passes locally and on the exact published commit; wheel installation and license are checked outside the checkout. | Maintainer/automation |
| Worked research path | The sensitivity study above can be reproduced from its protocol; published text/tables agree with retained artifacts. | Research contributor/maintainer |
| Independent methods review | A reviewer checks scheduling, information boundaries, paired comparisons and interpretation; consequential findings are resolved or disclosed. | Independent reviewer and maintainer |
| New-reader usability | Run the proposed five-participant exercise: install, run, inspect an actor view, branch, compare and explain one limitation. Record failures and resolve blockers. | Human participants and maintainer |
| Release record | A versioned source/wheel release identifies its commit, changes, validated platforms and remaining limitations; the quickstart works from that distribution. | Maintainer |

The first two gates are engineering/research-artifact work; the next two require real
independent participation and cannot be replaced by agent self-review or browser
automation. Release publication is a separate maintainer action. Do not label these
gates passed merely because the MVP exists.

Once these gates pass, keep the reference model stable and maintain it. Empirical
calibration is a separate research program, required for any empirical policy claim;
it is not silently implied by releasing a synthetic workbench.

## After the reference release

Consider agent adapters only with a defined evaluation question, recorded observation/
action boundaries and classical comparisons. Consider strategic firms, bargaining or
polycentric institutions only when a specific study needs them, with a new model-version
decision and its own acceptance evidence. Hosted deployment needs a separate trust model.
None is a prerequisite for finishing the current local reference workbench.
