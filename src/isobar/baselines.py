"""Published reduced-game checks, separate from the dynamic reference kernel.

Armstrong, Bostrom and Shulman (2013), sections 2.1-2.3:
https://nickbostrom.com/papers/racing-to-the-precipice.pdf
The equations describe that game's assumptions, not real catastrophe probabilities.
"""

from __future__ import annotations

import math


def race_risk(teams: int, capability_range: float, enmity: float, information: str) -> float:
    """Closed-form outcome of the published symmetric race game, for n >= 2, e > 0."""
    if type(teams) is not int or not 2 <= teams <= 1000:
        raise ValueError("teams must be an integer from 2 to 1000.")
    for value in (capability_range, enmity):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Baseline parameters must be finite numbers.")
    if capability_range <= 0 or not 0 < enmity <= 1:
        raise ValueError("capability_range must be positive and enmity in (0, 1].")
    n, mu, e = teams, capability_range, enmity
    if information == "none":
        return max(0.0, 1.0 - mu / (e * n))
    if information == "private":
        threshold = e * (n - 1) + 1
        if mu < threshold:
            return 1 - mu * n / ((n + 1) * threshold)
        return (threshold / mu) ** n / (n + 1)
    if information == "public":
        if mu < e:
            return 1 - mu / (e * (n + 1))
        ratio = e / mu
        if ratio == 0:
            return 0.0
        if ratio == 1:
            return n / (n + 1)
        # Avoid cancellation in (mu-e)**(n+1) - mu**(n+1).
        return max(0.0, 1 + math.expm1((n + 1) * math.log1p(-ratio)) / ((n + 1) * ratio))
    raise ValueError("information must be none, private or public.")
