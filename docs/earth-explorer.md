# Earth explorer

The default `world` scenario puts eight modeled jurisdictions on a real Earth map:
the United States, China, India, Russia, Brazil, France, Japan and South Africa.
Their values, strategies, membership, preferences and population weights are invented.
They are a teaching fixture, not estimates of those countries. Countries outside the
scenario are geographic context only. Borders, distance and area have no causal role
in the kernel; this iteration does not add trade, military conflict or migration.

## Explore a strategic decision

1. Select **Simulate world**. The 36-tick replay starts in the public record.
2. Drag the globe, use its rotation/zoom buttons, or choose **World map**. Select a
   country or its keyboard-accessible nation button. The list includes every modeled
   actor even when its geography is behind the globe or absent from the map.
3. Play or scrub the timeline. **Capability balance** is a state's share of displayed
   capability among the eight modeled states. It is not measured national power.
   The map can also show cumulative service or capability minus safety. The latter
   precedes the hazard threshold and is not a probability of catastrophe.
4. Select **See this nation's observations**. Its own allocation, strategy and beliefs
   become visible. Rival states remain filtered. Coalition links mean shared synthetic
   rule membership; perceived-deviation links show the selected state's private
   beliefs. Neither is a map of actual alliances or intentions.
5. Select **Inspect this decision**. The full-width panel reconstructs the actor's
   **pre-action** observation and actual action at that tick. The trajectory and state
   dossier instead show **post-action** frames. The trajectory spans the saved replay,
   including ticks beyond the cursor; it is explicitly a researcher replay view.
6. Compare the six candidate allocations, their utility components and, for bounded
   actors, their selection probabilities. Compliant and reciprocal actors follow
   rules instead of maximizing this grid. Myopic actors maximize one-period utility.
   These are subjective model incentives, not a solved strategic equilibrium.
7. Select **Change its decision** to open an intervention for that nation and tick.
   The decision inspector then explains the recorded override. Its payoff table
   remains a comparison against the configured strategy's candidate grid.

All map layers, shares, links, trajectories and events use the selected projected
run. Public inspection of private decision incentives is rejected by the server.
Post-run truth is an explicit observation choice. The complete starting scenario is
available in labeled researcher setup; this local tool does not enforce secrecy
between different users of the same machine.

**Edit conditions** opens the existing authoring controls. Changing a draft clears
its replay and interventions. All six fictional scenarios remain available; their
actors appear in the list without invented geographic positions. The policy comparison
below the replay uses paired seeds and the draft, without human interventions.

## Geography provenance and regeneration

The bundled geometry is Natural Earth's public-domain 1:110m Admin 0 Countries data.
[Terms of use](https://www.naturalearthdata.com/about/terms-of-use/) explain its public
domain status and cartographic conventions. Boundary depiction is context, not a
political claim. No live tiles, geocoding service or runtime network access is used.

- Source: [Natural Earth country GeoJSON at pinned revision](https://github.com/nvkelso/natural-earth-vector/blob/9380cca83db5f9aef52d5e762765100745f84b27/geojson/ne_110m_admin_0_countries.geojson).
- Revision: `9380cca83db5f9aef52d5e762765100745f84b27`.
- Original file SHA256: `6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f`.
- Generator: `web/scripts/update-map.mjs`. It verifies the source checksum, retains
  country ID/name/label center, rounds geometry to three decimal places, and normalizes
  polygon winding for D3. It checks 177 unique features before writing the bundle.
- Generated source: `web/src/data/countries.json`. Lowercase Natural Earth `ADM0_A3`
  IDs locate actors; other IDs have no location. Names and parameters remain authored
  by the scenario. The package includes the bundled geometry in its static assets.
- Projection: [D3 geographic projections](https://d3js.org/d3-geo/projection), using
  orthographic and equirectangular views. Geography changes presentation only.

To regenerate, run `node scripts/update-map.mjs` from `web/` after `npm ci`. This
maintenance command downloads the pinned source; ordinary builds use the committed
JSON and do not fetch geography.
