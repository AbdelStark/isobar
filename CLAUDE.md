# Working in Isobar

Follow [AGENTS.md](AGENTS.md) for shared repository rules, task routing and verification.

## Design Context

### Users

Design first for researchers exploring conditional AI-governance questions: set
assumptions, run scenarios, inspect what actors knew, branch decisions and compare
policies reproducibly. Support sustained analysis in a trusted local workbench.
Give newcomers a clear first experiment and explanations beside unfamiliar controls;
keep the full research workflow available as their understanding grows.

### Brand Personality

**Calm, rigorous, curious.** Build confidence through inspectable evidence and invite
experimentation through clear actions. Use precise, plain language, explain uncertainty
where it affects interpretation, and let findings retain their ambiguity.

### Aesthetic Direction

Preserve the light paper-and-olive editorial identity: warm surfaces, dark ink,
serif headings, readable sans-serif controls, fine rules and restrained rust accents.
The dark teal Earth view provides a focused visualization surface within that system.
Use typography, spacing and alignment to organize dense information; keep controls
familiar and ornament subordinate to the experiment.

The existing interface is the visual reference. Reuse the tokens and responsive
patterns in [web/src/style.css](web/src/style.css), the primitives in
[web/src/ui.ts](web/src/ui.ts), and the wave mark in
[web/public/favicon.svg](web/public/favicon.svg). Keep these files authoritative for
implementation values. No additional references, color constraints or accessibility
needs were specified in the design setup.

### Design Principles

1. **Make the experiment legible.** Keep the route from question to conditions, run,
   inspection, intervention and comparison explicit. Reveal advanced configuration
   and diagnostic detail when relevant, with a useful first action in empty states.
2. **Keep evidence beside its interpretation.** Identify the observation boundary,
   tick, units and missing values at the point of use. Distinguish researcher setup,
   actor knowledge and post-run truth; label synthetic national parameters clearly.
3. **Make tradeoffs inspectable.** Preserve separate outcomes, uncertainty and affected
   groups. Pair visual summaries with exact values and tables. A polished map must
   communicate the model's scope as clearly as its results.
4. **Support careful, recoverable work.** Explain what an action changes, show loading
   and failure states, preserve successful results on request failure, and make draft
   changes and replay invalidation visible. Confidence comes from predictable behavior.
5. **Preserve access across interaction modes.** Keep keyboard operation, visible focus,
   labeled native controls, reduced motion and complete mobile workflows. Reinforce
   color with labels, values or line styles, and provide list/table alternatives to
   spatial views. Keep interface assets available locally during use.
