# Using the local workbench

## One question, then one change

Start with S4 to inspect a false allegation and its remedy, or S2 to inspect reciprocal restraint under imperfect information. Read the assumption card before running. A tick is a synthetic period, not a week or month.

The saved frame is the state **after** that tick's action. Tick 0 is the first decision. Replay playback only moves through saved frames; it does not resimulate or make decisions for you. Public and actor views are filtered by the kernel. Researcher setup deliberately shows full starting assumptions in a separate, labeled area. This is a local research application, not a multiplayer secrecy boundary.

To intervene, choose an actor, a completed decision tick and allocations that sum to one. The checkbox permits an inspection if one is sampled; it does not request an audit. Run the branch, inspect its provenance, then compare the earlier history. Up to 16 interventions can be chained. Editing the scenario clears the old replay, interventions and comparison to prevent stale results being attributed to new inputs.

The comparison uses the draft scenario, without human interventions. It varies policy family across consecutive matched seeds. Inspect both the overall outcome vector and the affected-group table. The latter includes service per synthetic population weight, denied service, exposure and incidents. Null means the denominator is absent or the observation is unavailable, never zero. With very few seeds, normal-approximation intervals can be poor even within the assumed model.

## Author a scenario

Expand Advanced scenario authoring, edit the JSON, then validate and apply. The kernel rejects unknown fields, unsupported units, invalid ranges and inconsistent actor identities. Defaults are resolved into the saved input. Use the assumption records to explain provenance; a `measured` label is your assertion, not something the simulator verifies.

The browser supports seeds from 0 through 4294967295. Comparisons need 2 to 20 distinct seeds and at most 120 ticks in the browser. The CLI supports up to 1000 comparison seeds and 240 ticks; individual CLI runs support seeds through `2^63 - 1`. Use the schema for exact field limits:

```sh
uv run isobar schema --output runs/scenario-schema.json
uv run isobar validate s2
uv run isobar validate /path/to/scenario.json
```

A design adapter must be private and carry a source snapshot, review status and limitations. The unreviewed warning must not be removed without actual review. Software guards do not make a private mapping appropriate for sharing.

## Replay and intervene offline

```sh
uv run isobar run s2 -o runs/original.json
uv run isobar replay runs/original.json --view aurora
uv run isobar branch runs/original.json --tick 3 --actor aurora \
  --action '{"train":0.0,"safety":0.5,"service":0.5,"idle":0.0}' \
  -o runs/branch.json
uv run isobar replay runs/branch.json --view truth
uv run isobar export runs/branch.json --public -o runs/export.json
```

`run --actions actions.json` accepts recorded structured actions from a human or local model. The map uses keys such as `"3:aurora"`; values use the same `Action` schema as classical strategies. Missing overrides use the configured classical strategy. A supplied null, refused, late or invalid action is recorded with a labeled idle fallback. Unknown actor/tick addresses reject the run. No provider is contacted and no supplied code is executed.

Replay verifies the complete canonical result, not just a user-editable checksum. A filtered projection cannot be used as a replay bundle. Cross-platform bit-identical floating-point behavior is not promised. Resume requires the same package, Python, Pydantic and source-code identity.

## Cancel and resume

```sh
uv run isobar run s2 --stop-at 4 -o runs/partial.json
uv run isobar resume runs/partial.json -o runs/resumed.json
uv run isobar compare s2 --seeds 1 2 3 4 --stop-after 2 \
  --checkpoint runs/batch.json -o runs/partial-batch.json
uv run isobar compare s2 --seeds 1 2 3 4 \
  --checkpoint runs/batch.json -o runs/final-comparison.json
```

The batch checkpoint is atomically updated after each completed run. Repeating the command verifies cached runs before continuing. The checkpoint and output must be different files; outputs are never intentionally replaced. Partial batches have no completed-comparison label. Terminal incident runs remain in completed ensembles, including their truncated benefits and harms.

## Build and test

`make setup` installs frontend dependencies and builds static assets before installing the Python package: the package includes those assets, even in editable mode. `make check` runs Python lint, formatting, types, tests, frontend unit tests and the production build. `make build` creates a source archive and wheel with bundled static assets. A wheel installation needs Python and its runtime dependencies, not Node. `make serve` uses the built workbench, not Vite's development server.

Four real-server browser tests are authored in `web/tests/workbench.spec.ts`; final execution is pending. They cover replay/view boundaries, branching/comparison/export, invalid JSON and text safety, private export denial, narrow viewport and keyboard access. They are not a substitute for screen-reader testing or a human study.

Do not expose the server publicly. There are no accounts, permissions for remote users or production-server guarantees. See [SECURITY.md](../SECURITY.md).
