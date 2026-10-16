# When shared monitoring failures reverse the service comparison

In this fixed S2 experiment, reciprocal policy increases mean aggregate service
relative to unrestricted development when shared-root failure is zero. At a 30%
shared-root failure probability, the mean difference turns negative at both tested
false-positive rates. Aurora loses service in every condition, even where aggregate
service rises. These are conditional findings about the synthetic reference model,
not evidence for or against a real agreement.

Read the [prospective protocol](protocol.md), [generated tables](reference/tables.md)
and [artifact manifest](reference/manifest.json). The protocol fixes four conditions,
two policies, seeds 0–19 and the 24-tick S2 horizon before results are examined.
All 160 runs completed; none terminated early. Every run was regenerated and
replay-verified; eight seed-0 full bundles are retained beside the reports.

## What the outcomes say

At false-positive rate 0.01, reciprocal minus unrestricted service is **+10.3125**
normalized units with no shared failures, versus **−6.79225** with shared failure
probability 0.3. Their separate conditional 95% Monte Carlo intervals are
[5.15681, 15.4682] and [−11.9033, −1.68119]. At false-positive rate 0.10 the respective
means are +8.88025 and −3.43825; the latter interval includes zero
[−8.05721, 1.18071]. These are policy contrasts within four conditions, not an
interval or significance test for the difference between conditions.

The aggregate conceals opposing group effects. At low false positives and no shared
failure, Aurora's mean service difference is −7.0125 while Boreal's is +17.325.
Across all four conditions Aurora's mean difference is negative and Boreal's positive.
The [group tables](reference/tables.md#aurora-aurora) also report service per synthetic
population weight, denial, privacy and incidents. An aggregate gain cannot establish
that both actors benefit.

Reciprocal-policy cooperation averages 0.890278 and 0.906944 with no shared failures,
versus 0.766667 and 0.801389 with 30% shared failure (low/high false positives,
respectively). Increasing false positives does **not** produce a uniform worsening
across outcomes: mean cooperation rises at each shared-failure level, while mean
service falls at one level and rises at the other. The model uses the configured
false-positive likelihood both to generate reports and to interpret them in belief
updates. This experiment does not isolate that pathway from enforcement, appeals or
budget effects. A mechanism attribution would need a separate controlled study.

Control-incident counts are identical in every paired run: seeds 4 and 17 each
record one incident under both policies, and the other seeds record none. Thus the
paired mean and interval are [0, 0] despite different readiness gaps. This finite
sample does not establish equal underlying hazards. The misuse difference is −0.05
with interval [−0.148, 0.048] in every condition; it does not resolve an incident
advantage. The normal intervals are left untruncated even when a count interval
extends below zero, making the approximation's limitations visible.

The reciprocal privacy ratio is 0.1 per audit record in every condition with n=20.
That is the configured exposure fraction; constancy does not establish equal total
exposure. Unrestricted runs have no audit records, so their ratio and every paired
privacy difference are undefined. Cooperation and appeal comparisons likewise have
no valid unrestricted denominator. Reciprocal appeal success is about 0.082, 0.054,
0.538 and 0.297 in condition order; the first uses 18 valid runs, the others 20.
Appeal resolution is 1 among runs with filed appeals. Ratios are averaged over valid
runs, not pooled; neither an absent appeal nor an absent rule is scored as failure.

## Reproduce and inspect

From the repository root with `uv` available, this one command installs the locked
Python environment as needed and generates the complete study into a fresh directory:

```sh
uv run --locked python scripts/sensitivity_study.py runs/s2-monitoring-a
```

The generator refuses existing output paths and an uncommitted kernel/lock change.
It validates resolved inputs, full policy/seed coverage, statuses, global/group means
and valid denominators, then checks every full replay against the report. An incomplete
directory without `manifest.json` is a failed run; use a new directory after fixing it.
Assertion checks are mandatory, so running Python with `-O` is refused.

To apply the pass/fail criterion in a second fresh process:

```sh
uv run --locked python scripts/sensitivity_study.py runs/s2-monitoring-b
diff -r runs/s2-monitoring-a runs/s2-monitoring-b
```

Pass requires both commands to succeed and `diff` to exit zero with no output.
For the retained reference, compare the payloads with:

```sh
diff -r -x manifest.json docs/studies/s2-monitoring/reference runs/s2-monitoring-a
uv run --locked isobar replay runs/s2-monitoring-a/f01-r00-reciprocal-seed0.json --view public
```

`manifest.json` records checkout revision, source/runtime identity, generator,
protocol and lock hashes, plus SHA-256 of every output. Its checkout revision can
change after committing documentation or study files even when payloads remain
identical. Inspect those identity fields when comparing different revisions. The
reference was generated against unchanged kernel/lock files at
`2785b5242d2de10466e2a64806159df3871a7520`, with the uncommitted study additions identified
by their hashes. Runtime: Python 3.12.12, Pydantic 2.14.1, Darwin; cross-platform
bit identity is not promised. The saved comparison reports contain all run summaries;
the eight files named `*-seed0.json` are complete replay bundles containing truth.

## Verification and next boundary

On 2026-10-16, two separate executions produced all 14 files byte for byte, including
the manifest. Each execution verified all 160 full runs. `make check` passed 173
Python tests, eight frontend tests, formatting, lint and type checks. Output-overwrite
refusal and rejection of missing runs, altered digests and invalid sample counts were
also exercised. No model equations, fixtures, dependencies, HTTP or UI behavior changed.

The next useful rung is independent methods review of this evidence, followed by a
separately specified mechanism/structural sensitivity study if the reviewer judges
the question useful. Aggregating each jurisdiction with its developer, the bounded
action grid, the binary belief model and one-positive-report finding rule could all
change these tradeoffs. Four conditions and 20 seeds do not establish robustness
beyond this grid. Broader scenario discovery, empirical calibration, human usability
and release publication are not completed by reproducing these numbers.
