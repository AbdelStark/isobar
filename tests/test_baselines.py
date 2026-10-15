import pytest

from isobar.baselines import race_risk


def test_published_reduced_cases():
    assert race_risk(2, 1.0, 1.0, "none") == 0.5
    assert race_risk(2, 1.0, 1.0, "private") == pytest.approx(2 / 3)
    assert race_risk(2, 1.0, 1.0, "public") == pytest.approx(2 / 3)
    assert race_risk(2, 2.0, 1.0, "none") == 0.0
    assert race_risk(2, 2.0, 1.0, "private") == pytest.approx(1 / 3)
    assert race_risk(2, 2.0, 1.0, "public") == pytest.approx(5 / 12)


@pytest.mark.parametrize("teams,mu,e", [(2, 0.5, 1.0), (5, 3.0, 0.5), (2, 10.0, 0.2)])
@pytest.mark.parametrize("information", ["private", "public"])
def test_closed_form_matches_independent_quadrature(teams, mu, e, information):
    steps = 20000
    total = 0.0
    for step in range(steps):
        u = (step + 0.5) / steps
        if information == "private":
            safety = min(1.0, mu * u / (e * (teams - 1) + 1))
            density = teams * u ** (teams - 1)
        else:
            safety = min(1.0, mu * u / e)
            density = teams * (1 - u) ** (teams - 1)
        total += (1 - safety) * density / steps
    assert race_risk(teams, mu, e, information) == pytest.approx(total, abs=1e-7)


@pytest.mark.parametrize(
    "teams,mu,e,info",
    [
        (1, 1, 1, "none"),
        (True, 1, 1, "none"),
        (2, float("nan"), 1, "none"),
        (2, 1, 0, "none"),
        (2, 1, 1, "unknown"),
    ],
)
def test_baseline_input_boundary(teams, mu, e, info):
    with pytest.raises(ValueError):
        race_risk(teams, mu, e, info)
