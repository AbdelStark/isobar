# Research foundations and interpretation

Isobar is a small agent-based model for conditional AI-governance experiments.
Its scientific value depends on whether a mechanism is specified, implemented and
examined clearly enough to support a particular question. The sources below locate
those questions; they do not certify Isobar or its parameter choices.

## What is reproduced, and what is motivated by theory

### A reduced AI race game: mathematical reproduction

[Armstrong, Bostrom and Shulman (2013), *Racing to the Precipice*](https://nickbostrom.com/papers/racing-to-the-precipice.pdf),
sections 2.1–2.3, analyze a stylized race under different information conditions.
`race_risk` implements those closed-form outcomes separately from the dynamic model.
The check covers no, private and public capability information, hand-computed cases,
and independent numerical integration for private/public information.

Evidence: [implementation](../src/isobar/baselines.py),
[tests](../tests/test_baselines.py), [derivation scope](analytic-baseline.md).
The dynamic kernel has different states, actions and institutions. A correct reduced
formula is not validation of that kernel's equilibria or of real-world AI risk.

### Cooperation and reciprocity: a behavioral question

[Axelrod and Hamilton (1981), *The Evolution of Cooperation*](https://public.websites.umich.edu/~axe/research/Axelrod%20and%20Hamilton%20EC%201981.pdf)
study reciprocity in repeated interaction. That literature makes the conditions for
sustained cooperation a useful question here. Isobar implements a specific alternative:
restraint while the largest rival-deviation belief remains below a threshold, followed
by a fixed retaliatory allocation. Reports update beliefs; forgiveness shrinks them
back toward a prior.

Evidence: [strategy rules](../src/isobar/strategies.py) and
[belief specification](model-card.md#strategies-beliefs-and-evidence).
This is not literal tit-for-tat, an evolutionary tournament, or a demonstration of
an equilibrium. Compare belief learning on/off, evidence delay and false positives
before attributing a run's cooperation to reciprocity alone.

### Logit choice: a response rule without an equilibrium solver

[McKelvey and Palfrey (1995), *Quantal Response Equilibria for Normal Form Games*](https://authors.library.caltech.edu/records/4fh4n-4c340)
connect probabilistic utility-sensitive choice to a joint equilibrium condition.
Isobar's bounded strategy uses the logit response form on a six-action grid:

$$P_i(a\mid o_i)=\frac{\exp(\lambda_i U_i(a;o_i))}{\sum_{b\in A_i(o_i)}\exp(\lambda_i U_i(b;o_i))}.$$

The implementation subtracts the largest scaled score before exponentiation for
numerical stability. `temperature` is the inverse-temperature coefficient; at zero,
each grid entry is equally likely. The rule-constrained entry can coincide with
another entry, so equal probabilities over entries need not imply equal probabilities
over distinct allocations. The myopic strategy chooses the grid maximum.

Evidence: [shared scoring and selection](../src/isobar/strategies.py),
[decision regressions](../tests/test_decisions.py).
There is no fixed-point solver, estimation against experimental choices, learned
value function or multi-period planning. The utility chart explains the implemented
one-period calculation, including the actual recorded override when one was supplied.

### Institutions and collective action: mechanisms to separate

[Ostrom (2009), *Beyond Markets and States: Polycentric Governance of Complex Economic Systems*](https://www.nobelprize.org/uploads/2018/06/ostrom_lecture.pdf)
discusses monitoring, sanctions, conflict resolution and institutional diversity.
These questions motivate examining rule compliance alongside the costs and
accountability of enforcement. They do not imply that an AI-development race is a
calibrated common-pool-resource model.

Isobar distinguishes an allegation from a finding, an enforcement attempt from an
actual restriction, and a nominal appeal from an independent review. Its institution
has finite resources and can be captured. These choices expose how an enforcement
mechanism might fail even when its formal rule remains unchanged.

Evidence: [scheduling and submodels](model-card.md#scheduling-and-submodels),
[engine regressions](../tests/test_engine.py).
The reference model has one institution. Polycentric authority, endogenous bargaining,
graduated sanctions and legitimacy formation are not implemented. Institutional
parameters are illustrative, not estimates fitted to Ostrom's empirical cases.

## Model description and experimental discipline

[Grimm et al. (2020), the second update of the ODD protocol](https://www.jasss.org/23/2/7.html)
argue for explicit model purpose, entities, scheduling, design concepts, initialization,
inputs and submodels, with rationale and evaluation sufficient for replication.
Isobar's [model card](model-card.md) documents those practical concerns. It is not
presented as an independently reviewed ODD submission or a complete account of social
behavior. The code and tests are linked so readers can check the reductions directly.

For a useful experiment:

1. State the outcome and mechanism you intend to test before selecting a favorable seed.
2. Define the intervention and comparison. Distinguish changing a policy, an actor's
   strategy, its information, or one recorded action.
3. Pair seeds across alternatives and report every completed run, including terminal
   runs. Preserve negative and ambiguous results.
4. Vary the assumptions doing the explanatory work: hazard family, preferences,
   hidden capacity, monitor dependence, false positives and institutional resources.
5. Report per-group outcomes and missing denominators. Separate Monte Carlo intervals
   from uncertainty about parameters, model structure and external validity.
6. Release the exact commit, resolved scenarios, seed list, action overrides and
   artifacts when their classification and underlying permissions allow it.

Counterfactual branches identify consequences **inside the specified simulation**.
They do not identify causal effects in observational human data. Private views are
observation filters for research, not access control between remote participants.
The [acceptance record](acceptance.md) separates software evidence from open scientific
and usability obligations.

## Workflow smoke check

For a complete worked example, see the [S2 monitoring sensitivity study](studies/s2-monitoring/README.md):
a prospective protocol, four fixed conditions, all 160 runs replay-verified and
generated per-policy/per-group tables. The small example below remains a mechanics check.

From a prepared checkout, this small two-condition experiment checks report saving,
runtime provenance, paired coverage and regeneration of individual traces. Its four
seeds establish workflow behavior, not a substantive result or adequate statistical
precision. It writes only to a temporary directory and removes the artifacts on exit.
Use a persistent, fresh directory and retain the protocol for an actual study.

```sh
uv run python - <<'PY'
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from isobar.artifacts import atomic_json, environment, package_run, read_json, verify_bundle
from isobar.engine import simulate
from isobar.experiments import compare
from isobar.models import Scenario
from isobar.scenarios import get_scenario

policies, seeds = ["unrestricted", "reciprocal"], [0, 1, 2, 3]
with TemporaryDirectory(prefix="isobar-study-") as directory:
    for false_positive_rate in (0.01, 0.10):
        raw = get_scenario("s2").model_dump(mode="json")
        raw["verification"]["false_positive_rate"] = false_positive_rate
        scenario = Scenario.model_validate(raw)
        report = compare(scenario, policies, seeds)
        path = Path(directory) / f"fpr-{false_positive_rate}.json"
        atomic_json(path, report, overwrite=False)
        saved = read_json(path)
        assert saved["environment"] == environment()
        assert {(r["policy"], r["seed"]) for r in saved["runs"]} == {
            (policy, seed) for policy in policies for seed in seeds
        }
        for row in saved["runs"]:
            config = deepcopy(saved["config"]["scenario"])
            config["policy"]["family"], config["seed"] = row["policy"], row["seed"]
            run = simulate(Scenario.model_validate(config))
            assert run["status"] == row["status"] in {"completed", "terminal"}
            assert run["metrics"] == row["metrics"] and run["digests"] == row["digests"]
            verify_bundle(package_run(run))
        assert compare(scenario, policies, seeds) == saved
        print(f"Verified {len(saved['runs'])} paired runs at false_positive_rate={false_positive_rate}")
PY
```
