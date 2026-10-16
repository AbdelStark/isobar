---
name: isobar-model-change
description: Change Isobar scenarios, dynamics, policies, strategies, observations or outcome metrics while preserving scientific provenance and deterministic replay.
---

# Change the model

Read `docs/model-card.md` for the affected equation, parameter or scheduling rule,
and `docs/mvp-contract.md` for its integration contract. Use paths from the repo root.

1. Trace the change through input validation, scenario defaults, transition order,
   observation filtering, artifact replay, ensembles and UI labels. State the changed
   invariant and the evidence that would distinguish the old behavior from the new.
   Actor IDs share the observation selector namespace: `public` and `truth` are reserved.
2. Reproduce the behavior in a small synthetic scenario. Use the existing strict
   `Scenario` and `Action` models, keyed randomness and fixture helpers. Keep physical
   feasibility separate from obligations; an allegation is not a proven breach.
3. Implement in the owning module. Strategies receive only actor observations, all
   actors decide from the same pre-tick state, and added events must not shift unrelated
   random draws. Projection filtering covers metadata, narratives, lineage and digests
   as well as frames. Exercise an adversarial hidden-state change when touching it.
4. Add a regression for the changed invariant and test the nearest boundary case.
   For metrics, check denominators, terminal runs, group distribution and paired deltas.
   For interventions, verify immutable history and nested offline replay.
5. Update the model card and decide model/schema version compatibility explicitly.
   Dynamics changes need a model-version decision; input/artifact changes need a schema
   compatibility decision. Never edit an old artifact to make replay pass. Document
   implementation fixes that preserve model semantics as such.
   For an intended behavior-preserving change, compare complete canonical fixture
   outputs before and after on the same runtime. Source edits still invalidate old
   checkpoints for resumption; deterministic replay and resume are different checks.
6. Follow `.agents/skills/isobar-verify/SKILL.md`. Finish with the synthetic evidence,
   assumptions affected, version decision and limits of the claim. A preferred policy
   winning the fixture is not a correctness criterion.
