---
name: isobar-experiment
description: Design and reproduce Isobar policy comparisons, sensitivity analyses and counterfactual experiments, with scoped interpretation of synthetic results.
---

# Run an interpretable experiment

Use repository-root paths. Read `docs/research-foundations.md` for interpretation
and `docs/model-card.md` for the mechanism, scheduling and outcome denominators.
Use `docs/roadmap.md` when choosing the next study; user-specified questions take
precedence. For model semantics changes, also use
`.agents/skills/isobar-model-change/SKILL.md`.

1. Write the question, comparison, primary outcomes, seed set and sensitivity cases
   before examining results. Identify the assumption whose removal could change the
   conclusion. Describe national fixtures as synthetic, including their preferences.
2. Validate each resolved `Scenario`. Keep all conditions identical except the stated
   intervention. `compare` varies policy family; changing a strategy, information or
   institution parameter requires a separately labeled scenario condition.
3. Run the same distinct seeds in every condition using `experiments.compare` or the
   CLI. Choose a fresh output directory; checkpoints and final reports need different
   paths. Run outputs are immutable; only an explicitly selected checkpoint is updated.
   Retain cancelled status and every terminal run. Resume only verified checkpoints
   from the matching source/runtime, otherwise start a separately labeled experiment.
4. Check report contents before interpretation: resolved config, environment identity,
   expected policy/seed pairs, completed/terminal status, per-group outcomes and paired
   sample counts. `runs` contains metrics/digests, not full replay bundles. Regenerate
   a selected run with its stored config, policy and seed; compare its metrics/digests.
   For branching or decision inspection, retain the full bundle and `input_actions`;
   realized `actions` alone lose invalid-input fallback provenance.
5. Report the outcome vector and per-group tradeoffs, including null denominators and
   ambiguous findings. Normal intervals quantify conditional Monte Carlo variability;
   sensitivity to parameters or model structure is a separate result. A treatment
   changing event realization does not mean keyed random draws stopped being paired.
6. Deliver the protocol, exact revision, reproduction command, report and interpretation
   together. Exported research artifacts contain hidden state; check classification and
   permission before sharing. Finish when a second execution reproduces the selected
   evidence, not when a preferred policy wins.

The executable smoke protocol in `docs/research-foundations.md#workflow-smoke-check`
tests this path without making a scientific result out of a small sample. A substantial
study should keep its generation code beside its protocol and generated report.
