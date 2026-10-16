# Working on Isobar

Use Python 3.12 through `uv` and Node 24. Install with `make setup`, then `make check`.
Install Chromium once with `make browser-setup`; `make verify` runs the full local
acceptance gate, including the real-browser and isolated-wheel checks. Dependencies
and browser installation need network access; the running application does not.

The kernel owns physical state and transitions. Policies change obligations, not physics. Strategies receive only actor views. Keep action, observation and institutional decisions separate, and test changed information boundaries.

Every model change needs a model-card update, regression tests, an explicit model version decision and a reproducible synthetic example. Do not describe fixture success as calibrated policy effectiveness. Preserve negative results and explain load-bearing assumptions.

Isobar is released under the [MIT license](LICENSE). Contributions are welcome through issues and pull requests. Include a reproducer and the verification you ran; discuss substantial model changes in an issue before implementation.

Keep external private designs, credentials and sensitive scenarios out of issues, pull requests and CI artifacts. Maintainer authorization is required for license changes, repository access changes, external model calls and hosted deployment. Agents should stage exact paths and preserve unrelated work.

For a focused UI change use `make check-browser`. It starts a fresh server on 4318;
stop your own development server first, or inspect the listener if the port is busy.
Open `web/playwright-report/index.html` for results and inspect failure traces and
screenshots in `web/test-results/`. `make check-package` builds and installs outside
the checkout, using locked runtime dependencies, and checks the CLI and bundled UI.
CI runs `make verify` and retains synthetic browser evidence for 14 days.

README screenshots come from the real `world` fixture, seed 42. With `make serve`
running, run `cd web && node scripts/capture-readme.mjs` to regenerate the two images
in `docs/assets/`. Review the images and keep their captions aligned with the run.

Agents start at [AGENTS.md](AGENTS.md). The two repository skills cover model changes
and verification, with detailed equations and contracts kept in the existing docs.
This follows the [native repository guidance and skill pattern](https://developers.openai.com/blog/skills-agents-sdk).
The harness uses [Playwright accessibility scans](https://playwright.dev/docs/accessibility-testing)
alongside keyboard, failure-recovery and real-kernel tests. Automated scans do not
replace screen-reader testing or a human usability study.
