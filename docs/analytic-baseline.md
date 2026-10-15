# Reduced analytic check

The separate `isobar.baselines.race_risk` function implements the closed-form race-game outcomes in sections 2.1-2.3 of [Armstrong, Bostrom and Shulman, FHI Technical Report 2013-1](https://nickbostrom.com/papers/racing-to-the-precipice.pdf). The primary report and equations were read on 2026-10-15.

The game assumes independent uniform capabilities, a shared enmity parameter, and safety of the winning team determining the outcome. Tests check hand-computed cases and independently integrate the private/public-information outcome distributions. The dynamic Isobar kernel is a different model; reproducing these formulas does not validate its dynamics or establish empirical risk.

For two teams, unit capability range and unit enmity, the three analytic outputs are 0.5, 2/3 and 2/3 for no, private and public capability information. These are synthetic game quantities, not estimates about actual AI development.

```sh
uv run pytest tests/test_baselines.py -q
```

The deterrence payoff check in `isobar.engine.deterrence_payoff` is a separate one-period algebraic fixture, not a published empirical law. Neither fixture implies that the dynamic ABM reaches a Nash equilibrium.
