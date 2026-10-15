# Working on Isobar

Use Python 3.12 through `uv` and Node 24. Install with `make setup`, then `make check`. Browser tests are in `web/`; backend tests require no network or credentials.

The kernel owns physical state and transitions. Policies change obligations, not physics. Strategies receive only actor views. Keep action, observation and institutional decisions separate, and test changed information boundaries.

Every model change needs a model-card update, regression tests, an explicit model version decision and a reproducible synthetic example. Do not describe fixture success as calibrated policy effectiveness. Preserve negative results and explain load-bearing assumptions.

Use exact paths when staging. Keep external private designs out of the repository. Public sharing, a license change, collaborators, remote model calls and hosted deployment require separate owner approval. This private repository has no open-source license grant.

Build the wheel after the browser bundle, then verify CLI and local serving from an isolated wheel installation. Do not rely only on an editable install.
