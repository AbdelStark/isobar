# Isobar

A local simulation laboratory for AI governance. Compare development policies under imperfect verification, inspect disputes and enforcement, and examine tradeoffs in safety, freedom and concentrated power.

All scenarios are synthetic. Simulation outcomes are conditional on the model, not predictions about countries, evidence that a treaty works, or calibrated estimates of catastrophic risk.

The Python kernel owns all dynamics. An interactive Earth globe shows changing capability shares, national trajectories, coalition links and private beliefs. A decision inspector explains each action using the kernel’s own utility calculations. The workbench includes an eight-country sandbox, six fictional scenarios, four policy families, four classical strategies, human counterfactuals and paired experiments. Kernel, browser and isolated-install acceptance checks pass. See the [acceptance record](docs/acceptance.md) for the exact boundary.

## Run locally

Use Python 3.12, Node 24 and `uv`. Dependencies are locked. Setup needs package-registry access; the running application makes no external requests.

```sh
make setup
make serve
```

Open `http://127.0.0.1:4318`. No accounts, analytics, external fonts or hosted model calls. The server is for trusted local use only, not public deployment.

Start with **Simulate world**, select a nation and play the timeline. Switch map layers, inspect a national strategy, or change its decision. The eight real country names carry entirely synthetic parameters. Read the assumption card before interpreting the results. Switch between public observations, an actor's observations and explicitly labeled post-run truth. Scrub the timeline, follow a disputed report through its decision and appeal, or replace one actor action. Compare all four policies across matched seeds, including outcomes for each affected group.

Research exports contain hidden state, regardless of the current view. Public-classification export rejects private inputs; it does not grant permission to publish a synthetic run. Keep confidential mappings outside this repository.

## Headless experiments

```sh
uv run isobar run s4 -o runs/false-allegation.json
uv run isobar replay runs/false-allegation.json --view public
uv run isobar compare s2 --seeds 1 2 3 4 -o runs/comparison.json
make browser-setup
make verify
```

Output files are not overwritten. Replay checks the entire result by deterministic re-execution, including nested branch provenance. Comparisons report paired differences, explicit sample sizes and Monte Carlo intervals; those intervals exclude structural uncertainty. There is no global policy score.

- [Earth explorer](docs/earth-explorer.md): nation states, map layers, strategic decisions and geographic provenance.
- [User guide](docs/user-guide.md): authoring, interventions, replay, cancellation and resumption.
- [Model card](docs/model-card.md): equations, every parameter, scheduling and metric denominators.
- [Implementation contract](docs/mvp-contract.md): Python and local HTTP interfaces.
- [Analytic check](docs/analytic-baseline.md): a separate published race-game calculation, not validation of the ABM.
- [Acceptance record](docs/acceptance.md) and [local trust boundary](SECURITY.md).
- [Contributing](CONTRIBUTING.md) and [agent entrypoint](AGENTS.md): local skills, verification gates and CI evidence.

AI-assisted implementation and documentation. Actors aggregate a jurisdiction and its developer; hazards, preferences and institutional behavior are uncalibrated. No independent methods review, human usability study, learned-policy training or hosted deployment is claimed. Private repository, no open-source license grant.
