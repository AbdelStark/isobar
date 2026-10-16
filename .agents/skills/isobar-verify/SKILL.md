---
name: isobar-verify
description: Verify Isobar code changes or MVP readiness using the real kernel, browser workflows and isolated wheel installation; diagnose failed gates and record scoped evidence.
---

# Verify a change

Run commands from the repository root. Read the diff and affected callers first;
choose evidence for the behavior changed, not just the files edited.

- Python or frontend logic: run the relevant existing regression, then `make check`.
- Workbench or HTTP behavior: run `make check-browser`. First-time browser setup is
  `make browser-setup`. The suite owns port 4318 and deliberately refuses to reuse a
  server; inspect an occupied port before stopping anything. It exercises built assets
  against the real kernel, not Vite or a mocked successful API.
- Packaging, installation or release readiness: run `make check-package`. It builds a
  fresh source archive/wheel, installs locked runtime dependencies in a temporary venv,
  then checks the CLI lifecycle, bundled assets and HTTP export-to-CLI replay outside
  the checkout. An editable installation alone cannot pass this requirement.
- Full MVP acceptance: `make verify` runs all three gates. Documentation-only edits
  need link/claim checks; rerun code only when they change a command or behavioral claim.

For a failing browser check, read the error and `web/test-results/` trace before
changing code. Assertions must wait for observable UI state; arbitrary sleeps and
retries can hide a race. Inspect desktop and 390px renders after layout changes.
Use keyboard navigation, open relevant disclosures, and check recovery paths as well
as the happy path. Accessibility scans cover detectable issues, not certification.

Keep generated screenshots, scans and traces in ignored output directories. The CI
uploads synthetic browser evidence for 14 days. Never introduce private scenarios into
that suite. Use `web/playwright-report/` for local review; record links to exact-SHA CI
runs when publishing an authorized change.

Acceptance updates go in `docs/acceptance.md`: requirement → concrete test/runtime
evidence → remaining boundary. Inspect tests to ensure they establish the requirement.
Keep independent scientific review and human usability research separate from software
acceptance. When a gate cannot run, report the failed command and observed blocker;
leave that requirement unverified.
