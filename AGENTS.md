# Working in Isobar

Isobar is an MIT-licensed, local simulation workbench for conditional AI-governance questions.
Read [the MVP contract](docs/mvp-contract.md) for scope and interfaces and
[the acceptance record](docs/acceptance.md) for verified behavior and remaining boundaries.
Synthetic fixture success is implementation evidence, never empirical policy validation.

## Navigate by task

- Priorities, milestone planning or release completion: read
  [the roadmap](docs/roadmap.md) and its evidence-based finish criteria.
- Model, policy, strategy, observation or metric changes: use
  [isobar-model-change](.agents/skills/isobar-model-change/SKILL.md) before editing.
- Runtime, UI, packaging, test or CI changes: use
  [isobar-verify](.agents/skills/isobar-verify/SKILL.md) to select and close verification.
- Experiments, sensitivity analysis or interpretation: use
  [isobar-experiment](.agents/skills/isobar-experiment/SKILL.md); keep the protocol
  separate from results and software acceptance separate from scientific validity.
- User workflows: [user guide](docs/user-guide.md). Equations, scheduling, units and
  metric denominators: [model card](docs/model-card.md). Artifact and HTTP trust
  boundaries: [SECURITY.md](SECURITY.md).

## Code map

`models.py` validates input → `scenarios.py` supplies fixtures → `engine.py` owns
all state transitions and projections. `strategies.py` consumes actor observations.
`artifacts.py` verifies and persists runs; `experiments.py` pairs policy comparisons.
`cli.py` and `server.py` expose that same kernel. All Python modules are in `src/isobar/`.
`decisions.py` reconstructs pre-action diagnostics through that same kernel.
`web/src/main.ts` owns workbench state; `world.ts` renders Earth exploration;
`core.ts` and `world-core.ts` hold pure display helpers; `ui.ts` owns DOM primitives.
`style.css` owns the visual system. Python tests mirror modules; `web/tests/` uses
the real local server. Reuse these boundaries instead of duplicating model logic in UI.

## Work and finish

Use Python 3.12 through `uv`, Node 24, and locked dependencies. `make setup` prepares
the checkout; `make serve` starts it. Validation commands live in `Makefile`.
Keep `AGENTS.md` a short map; add task knowledge to its existing linked source.

Preserve unrelated work and stage exact paths. Keep confidential mappings in an
authorized external location, never fixtures or CI artifacts. Routine local work
can proceed autonomously; public sharing, hosted deployment, collaborator changes
and external model calls require explicit authorization unless already supplied.

Complete means the requested behavior works through its callers, relevant checks
pass, and changed contracts/docs match. Record commands and their outcomes, unresolved
limits, and any active process handle when handing off. Recheck current files and
processes on resumption; a prior acceptance note is not evidence for a new revision.
