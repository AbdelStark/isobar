import './style.css';
import { actionFromInputs, finiteNumber, format, humanize, intervalExtent, MAX_SEED, pairedSeeds, parseScenario, parseSeed, record, type JsonRecord } from './core';

type Actor = JsonRecord & { id: string; name: string; strategy: string };
type Scenario = JsonRecord & {
  id: string; name: string; description: string; question: string; classification: string;
  seed: number; horizon: number; actors: Actor[]; policy: JsonRecord; verification: JsonRecord;
};
type Frame = { tick: number; actors: Actor[]; institution: JsonRecord; metrics: JsonRecord };
type Event = { id: string; tick: number; kind: string; actor_id: string | null; summary: string; causes: string[]; data: JsonRecord; visibility: string };
type Run = { id: string; status: string; scenario: Scenario; model_version: string; completed_ticks: number; frames: Frame[]; events: Event[]; metrics: JsonRecord; warnings: unknown[]; branch: JsonRecord | null; terminal_cause: string | null; digests: JsonRecord };
type Stats = { mean: number | null; sd: number | null; ci_low: number | null; ci_high: number | null; n: number };
type GroupSummary = {actor_id: string; name: string; population: number; metrics: Record<string, Stats>};
type Summary = { policy: string; metrics: Record<string, Stats>; n: number; distribution?: GroupSummary[] };
type Comparison = { model_version: string; seeds: number[]; baseline: string; summaries: Summary[]; differences: Summary[]; note: string };
type Intervention = {tick: number; actor_id: string; action: JsonRecord};
type Child = Node | string | null | undefined;

function el<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, string> = {}, ...children: Child[]): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  for (const child of children) if (child !== null && child !== undefined) node.append(child);
  return node;
}
function get<T extends HTMLElement = HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (!element) throw new Error(`Missing interface element: ${id}`);
  return element as T;
}
const input = (id: string) => get<HTMLInputElement>(id);
function field(label: string, control: HTMLElement, help?: string): HTMLElement {
  const wrapper = el('div', { class: 'field' }, el('label', { for: control.id }, label), control);
  if (help) {
    const helpId = `${control.id}-help`;
    control.setAttribute('aria-describedby', helpId);
    wrapper.append(el('small', { id: helpId }, help));
  }
  return wrapper;
}
function numberField(id: string, label: string, value: number, min: number, max: number, step = '1', help?: string): HTMLElement {
  return field(label, el('input', { id, type: 'number', value: String(value), min: String(min), max: String(max), step, required: '' }), help);
}
function select(id: string, choices: Array<[string, string]>, value?: string): HTMLSelectElement {
  const control = el('select', { id });
  for (const [key, text] of choices) {
    const option = el('option', { value: key }, text);
    option.selected = key === value;
    control.append(option);
  }
  return control;
}
function button(id: string, text: string, kind = ''): HTMLButtonElement {
  return el('button', { id, type: 'button', class: kind }, text);
}
function details(title: string, ...children: Child[]): HTMLDetailsElement {
  return el('details', {}, el('summary', {}, title), ...children);
}
function table(headers: string[], rows: unknown[][], caption: string): HTMLElement {
  const node = el('table', {}, el('caption', { class: 'sr-only' }, caption), el('thead', {}, el('tr', {}, ...headers.map(h => el('th', { scope: 'col' }, h)))));
  node.append(el('tbody', {}, ...rows.map(row => el('tr', {}, ...row.map((value, i) => el(i === 0 ? 'th' : 'td', i === 0 ? {scope: 'row'} : {}, format(value)))))));
  return el('div', { class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': caption }, node);
}
const pretty = (data: unknown) => el('pre', {}, el('code', {}, JSON.stringify(data, null, 2)));
const clone = <T>(value: T): T => structuredClone(value);

let scenarios: Scenario[] = [], policies: string[] = [], strategies: string[] = [];
let draft: Scenario, runScenario: Scenario | null = null, run: Run | null = null;
let actions: Record<string, JsonRecord> = {}, frameIndex = 0, view = 'public';
let interventions: Intervention[] = [];
let comparison: Comparison | null = null, comparisonMetric = 'service_total', comparisonMode = 'summaries';
let comparisonScenario: Scenario | null = null;
let busy = false, playing: ReturnType<typeof setInterval> | undefined;

const metrics: Record<string, [string, string]> = {
  control_incidents: ['Control incidents', 'Sampled count; conditional on the chosen hazard model'],
  misuse_incidents: ['Misuse incidents', 'Sampled count, including already deployed capability'],
  service_total: ['Useful service', 'Cumulative synthetic service units'],
  denial_fraction: ['Benign requests denied', 'Fraction of benign requests'],
  privacy_fraction: ['Records exposed', 'Fraction of records'],
  appeal_success_fraction: ['Successful appeals', 'Overturned appeals / resolved appeals; unavailable when none resolved'],
  appeal_resolution_fraction: ['Appeals resolved', 'Resolved appeals / filed appeals; unavailable when none filed'],
  breaches: ['Actual breaches', 'Truth-only count, not a count of allegations'],
  cooperation_fraction: ['Cooperation', 'Truth-only fraction under the model definition'],
  power_concentration: ['Power concentration', 'Structural concentration index'],
  auditability_fraction: ['Inspectable decisions', 'Fraction of decisions'],
  readiness_gap: ['Readiness gap', 'Truth-only capability minus safety index'],
};

async function api<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/${path}`, body === undefined ? {} : {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
  } catch { throw new Error('The local server is not reachable. Start Isobar on 127.0.0.1:4318 and try again.'); }
  const data = await response.json().catch(() => ({error: 'The server returned an unreadable response. Restart the local server and try again.'}));
  if (!response.ok) {
    const info = record(data);
    const extra = Array.isArray(info.details) ? info.details.map(item => {
      const detail = record(item);
      const path = detail.path ?? (Array.isArray(detail.loc) ? detail.loc.join('.') : '');
      return `${path ? path + ': ' : ''}${detail.message ?? detail.msg ?? format(item)}`;
    }).join('\n') : '';
    throw new Error(`${String(info.error || 'Request failed. Check the scenario and try again.')}${extra ? '\n' + extra : ''}`);
  }
  return data as T;
}

function announce(message: string): void { get('status').textContent = message; }
function showError(error: unknown): void {
  get('error').textContent = error instanceof Error ? error.message : String(error);
  get('error').hidden = false;
  get('error').focus();
}
async function work(message: string, action: () => Promise<void>): Promise<void> {
  if (busy) return;
  busy = true;
  stopPlayback();
  get('error').hidden = true;
  announce(message);
  const controls = [...document.querySelectorAll<HTMLInputElement | HTMLButtonElement | HTMLSelectElement | HTMLTextAreaElement>('input, button, select, textarea')];
  const states = controls.map(control => control.disabled);
  controls.forEach(control => { control.disabled = true; });
  get('app').setAttribute('aria-busy', 'true');
  try { await action(); }
  catch (error) { showError(error); announce('Action did not complete. See the error for the next step.'); }
  finally {
    busy = false;
    controls.forEach((control, i) => { control.disabled = states[i]; });
    get('app').removeAttribute('aria-busy');
  }
}

function clearComparison(): void {
  comparison = null; comparisonScenario = null;
  get('comparison-results').replaceChildren();
}
function markDirty(): void {
  stopPlayback();
  run = null; runScenario = null; actions = {}; interventions = []; view = 'public';
  clearComparison();
  get('replay-controls').replaceChildren();
  get('run-content').replaceChildren(el('div', {class: 'empty-state'}, el('h3', {}, 'The conditions have changed.'), el('p', {}, 'Run this draft to inspect a fresh replay. Previous human interventions have been cleared.')));
  get('draft-state').textContent = 'Draft changed. Run to inspect the consequences.';
  announce('Draft changed. Previous replay and comparison cleared. Run the scenario to inspect the new conditions.');
}
function readDraft(): Scenario {
  const next = clone(draft);
  next.policy.family = get<HTMLSelectElement>('policy').value;
  next.seed = parseSeed(input('seed').value);
  next.horizon = finiteNumber(input('horizon').value, 'Horizon', 1, 240, true);
  for (const key of ['coverage', 'sensitivity', 'false_positive_rate']) next.verification[key] = finiteNumber(input(key).value, humanize(key), 0, 1);
  next.verification.delay = finiteNumber(input('delay').value, 'Evidence delay', 0, 24, true);
  next.actors.forEach(actor => { actor.strategy = get<HTMLSelectElement>(`strategy-${actor.id}`).value; });
  return next;
}

function build(): void {
  const app = get('app');
  app.replaceChildren(
    el('a', { href: '#workbench', class: 'skip-link' }, 'Skip to workbench'),
    el('header', { class: 'masthead' },
      el('a', { href: '#', class: 'wordmark', 'aria-label': 'Isobar home' }, el('span', { class: 'brand-symbol', 'aria-hidden': 'true' }, '≋'), 'isobar'),
      el('div', { class: 'masthead-meta' }, el('span', {class: 'local-label'}, 'LOCAL RESEARCH WORKBENCH'), el('span', {}, 'Reference model / 01')),
    ),
    el('main', {},
      el('section', { class: 'intro', 'aria-labelledby': 'title' },
        el('div', {}, el('p', { class: 'eyebrow' }, 'AI GOVERNANCE · UNDER IMPERFECT INFORMATION'), el('h1', { id: 'title' }, 'What holds ', el('em', {}, 'under pressure?'))),
        el('div', { class: 'intro-aside' }, el('p', {}, 'Change the rules. Inspect what actors can know. Follow the consequences.'), el('p', {class: 'caution'}, 'Synthetic scenarios, not forecasts. No single score, no recommended treaty.')),
      ),
      el('div', { id: 'error', class: 'error', role: 'alert', tabindex: '-1', hidden: '' }),
      el('p', { id: 'status', class: 'status', role: 'status', 'aria-live': 'polite' }, 'Loading local scenarios…'),
      el('div', { class: 'workbench', id: 'workbench', tabindex: '-1' },
        el('aside', { class: 'configuration', 'aria-labelledby': 'config-heading' },
          el('div', { class: 'section-heading' }, el('span', {class: 'section-index'}, '01'), el('h2', { id: 'config-heading' }, 'Set the conditions')),
          el('div', {id: 'config-fields'}),
        ),
        el('div', {class: 'workspace'},
          el('section', {class: 'question-strip'}, el('p', {class: 'eyebrow'}, 'RESEARCHER SETUP · THE QUESTION'), el('h2', {id: 'question'}), el('p', {id: 'scenario-description'}), el('p', {class: 'fine-print setup-note'}, 'Authoring context, not information available to actors.')),
          el('section', {id: 'replay', 'aria-labelledby': 'replay-heading'},
            el('div', {class: 'section-heading'}, el('span', {class: 'section-index'}, '02'), el('h2', {id: 'replay-heading'}, 'Observe the run')),
            el('div', {id: 'replay-controls'}), el('div', {id: 'run-content'}, el('div', {class: 'empty-state'}, el('p', {class: 'empty-kicker'}, 'A controlled thought experiment'), el('h3', {}, 'Begin with one scenario.'), el('p', {}, 'Read its assumptions, run it, then inspect the evidence. Change one condition and ask what actually changed.'))),
          ),
          el('section', {id: 'compare', class: 'compare-section', 'aria-labelledby': 'compare-heading'},
            el('div', {class: 'section-heading'}, el('span', {class: 'section-index'}, '03'), el('h2', {id: 'compare-heading'}, 'Compare the rules')),
            el('p', {class: 'section-deck'}, 'One replay is an example, not an estimate. Compare policies on matched seeds to separate a policy difference from a lucky draw.'),
            el('div', {class: 'comparison-controls'}, numberField('ensemble-count', 'Paired seeds', 6, 2, 20), button('compare-run', 'Compare all four policies', 'secondary')),
            el('p', {class: 'truth-notice'}, 'Post-run research comparison (includes hidden state). This is not the selected actor’s knowledge. Uses the draft scenario without human interventions and consecutive seeds starting at its seed. Maximum horizon: 120 ticks.'),
            el('div', {id: 'comparison-results'}),
          ),
        ),
      ),
    ),
    el('footer', {}, el('span', {}, 'Isobar / a laboratory for conditional questions'), el('span', {}, 'Local computation. No analytics. No hosted model calls.')),
  );
  get('compare-run').addEventListener('click', () => void compare());
  get('ensemble-count').addEventListener('change', clearComparison);
  get('run-content').addEventListener('focusin', event => {
    if ((event.target as HTMLElement).matches('input, select, button, textarea, summary')) stopPlayback();
  });
  renderConfig();
}

function renderConfig(): void {
  const fields = get('config-fields');
  fields.replaceChildren(
    field('Research scenario', select('scenario', scenarios.map(s => [s.id, `${s.id.toUpperCase()} · ${s.name}`]), draft.id)),
    field('Policy', select('policy', policies.map(p => [p, humanize(p)]), String(draft.policy.family))),
    el('div', {class: 'field-row'}, numberField('seed', 'Seed', draft.seed, 0, MAX_SEED), numberField('horizon', 'Horizon (ticks)', draft.horizon, 1, 240)),
    el('fieldset', {}, el('legend', {}, 'Verification'),
      numberField('coverage', 'Coverage', Number(draft.verification.coverage), 0, 1, '0.05', 'Share within the verification boundary, 0 to 1.'),
      el('div', {class: 'field-row'}, numberField('sensitivity', 'Sensitivity', Number(draft.verification.sensitivity), 0, 1, '0.05'), numberField('false_positive_rate', 'False-positive rate', Number(draft.verification.false_positive_rate), 0, 1, '0.01')),
      numberField('delay', 'Evidence delay (ticks)', Number(draft.verification.delay), 0, 24),
    ),
    details('Actor strategies', ...draft.actors.map(actor => field(actor.name, select(`strategy-${actor.id}`, strategies.map(s => [s, humanize(s)]), actor.strategy)))),
    details('Read the assumption card', el('p', {class: 'fine-print'}, 'Researcher setup, not actor knowledge.'), assumptionList(draft.assumptions), el('p', {class: 'fine-print'}, 'Time is measured in synthetic ticks, not calendar time. Parameters are illustrative and uncalibrated.')),
    el('p', {id: 'draft-state', class: 'fine-print'}, 'Draft scenario. Run to inspect the consequences.'),
    button('run', 'Run scenario', 'primary'),
    el('details', {id: 'advanced'}, el('summary', {}, 'Advanced scenario authoring'),
      el('p', {class: 'fine-print'}, 'Researcher setup, not an actor view. This editor contains complete synthetic starting conditions, including hidden capacity. Changes are validated by the local kernel before they apply. Browser seeds use the uint32 range, 0 to 4294967295. Use the CLI for larger model seeds.'),
      field('Complete scenario JSON', el('textarea', {id: 'scenario-json', rows: '16', spellcheck: 'false'})),
      el('div', {class: 'button-row'}, button('apply-json', 'Validate and apply JSON'), button('reset-json', 'Reload form values')),
      el('a', {href: '/api/schema', target: '_blank', rel: 'noopener'}, 'Open the versioned scenario schema'),
    ),
  );
  get('question').textContent = draft.question;
  get('scenario-description').textContent = draft.description;
  get<HTMLDetailsElement>('advanced').addEventListener('toggle', () => {
    if (get<HTMLDetailsElement>('advanced').open && !get<HTMLTextAreaElement>('scenario-json').value) refreshEditor();
  });
  fields.querySelectorAll('input, select').forEach(control => control.addEventListener('change', markDirty));
  get('scenario').addEventListener('change', () => {
    const preset = scenarios.find(s => s.id === get<HTMLSelectElement>('scenario').value);
    if (preset) { draft = clone(preset); renderConfig(); markDirty(); get('scenario').focus(); }
  });
  get('run').addEventListener('click', () => void startRun());
  get('reset-json').addEventListener('click', refreshEditor);
  get('apply-json').addEventListener('click', () => void work('Validating scenario against the kernel schema…', async () => {
    const candidate = parseScenario(get<HTMLTextAreaElement>('scenario-json').value);
    const validated = await api<Run>('run', {scenario: candidate, stop_at: 0, view: 'truth'});
    draft = validated.scenario;
    renderConfig(); markDirty();
    get('run').focus();
    announce('Scenario validated and applied. Run it to inspect the consequences.');
  }));
}

function refreshEditor(): void {
  try { get<HTMLTextAreaElement>('scenario-json').value = JSON.stringify(readDraft(), null, 2); }
  catch (error) { showError(error); }
}
async function startRun(): Promise<void> {
  await work('Running the scenario locally…', async () => {
    const candidate = readDraft();
    const result = await api<Run>('run', {scenario: candidate, view});
    draft = candidate; runScenario = clone(candidate); actions = {}; interventions = []; run = result;
    frameIndex = 0;
    get('draft-state').textContent = 'Replay matches the current scenario.';
    renderReplay();
    announce(`Run ${result.status}: ${result.completed_ticks} ticks. Use the timeline to inspect the trace.`);
  });
}
function stopPlayback(): void {
  if (playing) clearInterval(playing);
  playing = undefined;
  const play = document.getElementById('play');
  if (play) play.textContent = 'Play replay';
}
function renderReplay(): void {
  if (!run || !runScenario) return;
  get('replay-controls').replaceChildren(
    el('div', {class: 'view-row'},
      field('Observation boundary', select('view', [['public', 'Public record'], ...runScenario.actors.map(a => [a.id, `${a.name}’s observations`] as [string, string]), ['truth', 'Post-run ground truth']], view)),
      el('div', {class: 'run-label'}, el('span', {class: 'run-dot', 'aria-hidden': 'true'}), `${run.status} / ${run.completed_ticks} ticks`, el('small', {class: 'run-scenario'}, run.scenario.name ?? `Scenario ${run.scenario.id}`)),
    ),
    el('p', {class: view === 'truth' ? 'truth-notice' : 'view-notice'}, view === 'truth'
      ? 'POST-RUN GROUND TRUTH. Includes hidden state unavailable to actors when they decide. Do not read this as the public record.'
      : 'Filtered by the kernel. Hidden rival state and truth-only metrics are withheld. Reported capability is an observation, not ground truth.'),
    el('div', {class: 'timeline'}, button('play', 'Play replay'), field('Replay tick', el('input', {id: 'timeline', type: 'range', min: '0', max: String(Math.max(0, run.frames.length - 1)), value: String(frameIndex)})), el('output', {id: 'tick-label', for: 'timeline'})),
    el('nav', {class: 'panel-nav', 'aria-label': 'Run sections'}, ...[['actors', 'Actors'], ['evidence', 'Evidence & decisions'], ['outcomes', 'Outcomes'], ['assumptions', 'Assumptions']].map(([id, label]) => el('a', {href: `#${id}`}, label))),
  );
  get('view').addEventListener('change', () => {
    const requested = get<HTMLSelectElement>('view').value;
    void work('Reconstructing the selected observation boundary…', async () => {
      const filtered = await api<Run>('run', {scenario: runScenario, actions, interventions, view: requested});
      run = filtered; view = requested;
      frameIndex = Math.min(frameIndex, Math.max(0, run.frames.length - 1));
      renderReplay(); get('view').focus(); announce(`Observation boundary: ${requested === 'truth' ? 'post-run ground truth' : requested}.`);
    }).then(() => { get<HTMLSelectElement>('view').value = view; });
  });
  get('timeline').addEventListener('input', () => { stopPlayback(); frameIndex = Number(input('timeline').value); renderFrame(); });
  get('play').addEventListener('click', () => {
    if (playing) { stopPlayback(); return; }
    if (run && frameIndex >= run.frames.length - 1) frameIndex = 0;
    get('play').textContent = 'Pause replay';
    playing = setInterval(() => {
      if (!run || frameIndex >= run.frames.length - 1) { stopPlayback(); return; }
      frameIndex += 1; input('timeline').value = String(frameIndex); renderFrame();
    }, 900);
  });
  renderFrame();
}

function renderFrame(): void {
  if (!run || !runScenario) return;
  const frame = run.frames[frameIndex];
  if (!frame) { get('run-content').replaceChildren(el('p', {}, 'This run has no saved frames.')); return; }
  get('tick-label').textContent = `${frame.tick} / ${Math.max(0, run.completed_ticks - 1)}`;
  const actorKeys = ['declared_capacity', 'capability', 'safety', 'service'];
  const actorRows = frame.actors.map(actor => [actor.name, ...actorKeys.map(key => actor[key]), actor.knowledge ?? 'Post-run truth']);
  const events = run.events.filter(event => event.tick <= frame.tick);
  const displayedEvents = events.slice(-100);
  const visibleMetrics = record(frame.metrics);
  const rows = Object.entries(metrics).filter(([key]) => key in visibleMetrics).map(([key, [label, definition]]) => [label, visibleMetrics[key], definition]);
  const institutions = Object.entries(record(frame.institution));
  get('run-content').replaceChildren(
    el('div', {class: 'run-panels'},
      el('section', {id: 'actors', class: 'panel', 'aria-labelledby': 'actors-heading'},
        el('div', {class: 'panel-heading'}, el('h3', {id: 'actors-heading'}, 'Actors'), el('span', {}, `TICK ${frame.tick}`)),
        el('p', {class: 'fine-print'}, 'Post-action state for the selected tick. Decisions start at tick 0. The knowledge column distinguishes own state from declared-work estimates.'),
        table(['Actor', 'Declared capacity', 'Capability', 'Safety', 'Service', 'Knowledge'], actorRows, 'Actor states at the selected tick'),
        details('Inspect available actor fields', ...frame.actors.map(actor => el('div', {}, el('h4', {}, actor.name), pretty(actor)))),
      ),
      el('section', {id: 'evidence', class: 'panel', 'aria-labelledby': 'evidence-heading'},
        el('div', {class: 'panel-heading'}, el('h3', {id: 'evidence-heading'}, 'Evidence & decisions'), el('span', {}, `${events.length} RECORDS`)),
        events.length ? el('ol', {class: 'event-list'}, ...displayedEvents.map(event => el('li', {id: `event-${event.id}`},
          el('span', {class: 'event-tick'}, String(event.tick).padStart(2, '0')),
          el('div', {}, el('p', {class: 'event-kind'}, humanize(event.kind)), el('p', {}, event.summary),
            details('Inspect causal record', el('dl', {class: 'record-list'}, el('dt', {}, 'Record'), el('dd', {}, event.id), el('dt', {}, 'Visibility'), el('dd', {}, event.visibility), el('dt', {}, 'Actor'), el('dd', {}, event.actor_id ?? 'Institution')),
              event.causes.length ? el('p', {}, 'Caused by: ', ...event.causes.map(id => {
                const target = displayedEvents.find(item => item.id === id);
                return target ? el('a', {href: `#event-${id}`}, `${id} `) : el('span', {}, `${id} (outside the displayed event window) `);
              })) : el('p', {class: 'fine-print'}, 'No prior causal record.'), pretty(event.data)),
          ),
        ))) : el('p', {class: 'empty-note'}, 'No visible events at this tick. Advance the timeline to follow the record.'),
        events.length > 100 ? el('p', {class: 'fine-print'}, 'Showing the latest 100 visible events. Export the bundle for the complete record.') : null,
        details('Institutional state', table(['Field', 'Value'], institutions.map(([key, value]) => [humanize(key), value]), 'Institutional state')),
      ),
      el('section', {id: 'outcomes', class: 'panel', 'aria-labelledby': 'outcomes-heading'},
        el('div', {class: 'panel-heading'}, el('h3', {id: 'outcomes-heading'}, 'Outcomes'), el('span', {}, 'NO AGGREGATE SCORE')),
        el('p', {class: 'fine-print'}, 'Cumulative to the selected tick. Unavailable is not zero. These model quantities are not measurements of human welfare.'),
        table(['Measure', 'Value', 'Interpretation'], rows, 'Outcome vector at the selected tick'),
        details('Distribution across groups', pretty(visibleMetrics.distribution ?? run.metrics.distribution ?? 'No distribution available in this observation boundary.')),
      ),
      el('section', {id: 'assumptions', class: 'panel', 'aria-labelledby': 'assumptions-heading'},
        el('div', {class: 'panel-heading'}, el('h3', {id: 'assumptions-heading'}, 'Assumptions'), el('span', {}, String(runScenario.classification).toUpperCase())),
        el('p', {}, 'A simulation can reveal a consequence of its assumptions. It cannot establish that those assumptions describe the world.'),
        assumptionList(run.scenario.assumptions),
        el('dl', {class: 'record-list'}, el('dt', {}, 'Model'), el('dd', {}, run.model_version), el('dt', {}, 'Policy'), el('dd', {}, humanize(String(run.scenario.policy.family))), el('dt', {}, 'Seed'), el('dd', {}, run.scenario.seed === undefined ? 'Withheld in this view' : String(run.scenario.seed)), el('dt', {}, 'Record ID'), el('dd', {}, run.id ?? 'Withheld in this view')),
        details('Units and provenance', pretty(run.scenario.units)),
        details('Scenario available in this view', pretty(run.scenario)),
        run.warnings?.length ? el('div', {class: 'caution'}, el('h4', {}, 'Run warnings'), el('ul', {}, ...run.warnings.map(w => el('li', {}, format(w))))) : null,
        run.terminal_cause ? el('p', {class: 'caution'}, `Terminal cause: ${run.terminal_cause}`) : null,
        run.branch ? details('Branch provenance', pretty(run.branch)) : null,
        details('Result digests', pretty(run.digests ?? 'Withheld in this observation boundary. Select post-run truth to inspect the digests.')),
      ),
    ),
    buildBranch(frame),
    el('section', {class: 'export-section', 'aria-labelledby': 'export-heading'},
      el('h3', {id: 'export-heading'}, 'Keep a reproducible record'),
      el('p', {class: 'truth-notice'}, 'Every research bundle includes post-run hidden state, regardless of the selected observation boundary. Exports are regenerated and checked by the server. Public-classification export is denied for private scenarios. This is a classification gate, not approval to publish; downloads stay on this machine.'),
      el('div', {class: 'button-row'}, button('export-public', 'Export research bundle (includes hidden state)'), button('export-internal', 'Export internal bundle (includes hidden state)')),
    ),
  );
  get('branch-run').addEventListener('click', () => void branchRun());
  get('export-public').addEventListener('click', () => void exportRun(true));
  get('export-internal').addEventListener('click', () => void exportRun(false));
}

function assumptionList(value: unknown): HTMLElement {
  if (value === undefined || value === null) return el('p', {class: 'fine-print'}, 'Free-text assumptions are withheld from this observation boundary. The assumption card in researcher setup describes the model, not actor knowledge.');
  if (Array.isArray(value)) return el('ul', {class: 'assumption-list'}, ...value.map(item => {
    if (typeof item === 'string') return el('li', {}, item);
    const assumption = record(item);
    return el('li', {}, el('strong', {}, String(assumption.parameter ?? 'Assumption')), el('p', {}, String(assumption.rationale ?? '')), el('small', {}, `${assumption.evidence_type ?? 'Unspecified evidence'} · ${assumption.source ?? 'No source supplied'}`));
  }));
  return pretty(value);
}
function buildBranch(frame: Frame): HTMLElement {
  const lastDecision = Math.max(0, (run?.completed_ticks ?? 1) - 1);
  const tick = Math.min(frame.tick, lastDecision);
  const fractional = [['train', 'Training', 0.2], ['safety', 'Safety work', 0.3], ['service', 'Service', 0.4], ['idle', 'Idle', 0.1], ['conceal', 'Concealment', 0]] as const;
  return el('section', {class: 'branch-section', 'aria-labelledby': 'branch-heading'},
    el('div', {class: 'panel-heading'}, el('h3', {id: 'branch-heading'}, 'Make one different decision'), el('span', {}, 'COUNTERFACTUAL BRANCH')),
    el('p', {}, 'Choose an actor and replace one action. The kernel reuses the same exogenous draws and preserves the earlier history. This is one counterfactual, not an ensemble.'),
    el('div', {class: 'branch-controls'},
      field('Actor to control', select('branch-actor', (runScenario?.actors ?? []).map(a => [a.id, a.name]))),
      numberField('branch-tick', 'Decision tick', tick, 0, lastDecision),
      ...fractional.map(([key, label, value]) => numberField(`action-${key}`, label, value, 0, 1, '0.05')),
    ),
    el('p', {class: 'fine-print'}, 'Training + safety + service + idle must sum to 1. Concealment is a separate fraction. Physical feasibility and treaty compliance are not the same thing.'),
    el('div', {class: 'checkbox-row'}, ...[['appeal', 'Appeal allegations', true], ['inspect', 'Permit inspection', true], ['renew', 'Request renewal', false], ['request_restart', 'Request restart', false]].map(([key, label, checked]) => {
      const control = el('input', {id: `action-${key}`, type: 'checkbox'}); control.checked = Boolean(checked);
      return el('label', {}, control, String(label));
    })),
    button('branch-run', 'Run this branch', 'secondary'),
  );
}
async function branchRun(): Promise<void> {
  await work('Replaying one changed decision with matched exogenous draws…', async () => {
    if (!runScenario) throw new Error('Run a scenario before branching.');
    if (interventions.length >= 16) throw new Error('This replay has reached the 16-intervention limit. Run the scenario again to start a fresh branch chain.');
    const values: Record<string, string | boolean> = {};
    for (const key of ['train', 'safety', 'service', 'idle', 'conceal']) values[key] = input(`action-${key}`).value;
    for (const key of ['appeal', 'inspect', 'renew', 'request_restart']) values[key] = input(`action-${key}`).checked;
    const action = actionFromInputs(values);
    const tick = finiteNumber(input('branch-tick').value, 'Decision tick', 0, Math.max(0, (run?.completed_ticks ?? 1) - 1), true);
    const actor_id = get<HTMLSelectElement>('branch-actor').value;
    run = await api<Run>('branch', {scenario: runScenario, actions, interventions, tick, actor_id, action, view});
    interventions = [...interventions, {tick, actor_id, action}];
    frameIndex = Math.min(tick, run.frames.length - 1);
    renderReplay();
    get('branch-run').focus();
    announce(`Branch complete. Changed ${actor_id} at tick ${tick}. Earlier history is preserved; provenance is under Assumptions.`);
  });
}
async function exportRun(isPublic: boolean): Promise<void> {
  await work('Regenerating and checking the export bundle…', async () => {
    if (!runScenario) throw new Error('Run a scenario before exporting.');
    const bundle = await api('export', {scenario: runScenario, actions, interventions, public: isPublic});
    const url = URL.createObjectURL(new Blob([JSON.stringify(bundle, null, 2) + '\n'], {type: 'application/json'}));
    const anchor = el('a', {href: url, download: `isobar-${isPublic ? 'public' : 'internal-truth'}-${runScenario.id.replace(/[^a-z0-9_-]/gi, '_')}.json`});
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    announce(`${isPublic ? 'Public-classification research' : 'Internal research'} bundle downloaded with post-run hidden state. Nothing was published.`);
  });
}
async function compare(): Promise<void> {
  await work('Running paired policy ensembles locally…', async () => {
    const scenario = readDraft();
    if (scenario.horizon > 120) throw new Error('Browser comparisons allow at most 120 ticks. Lower the horizon or use the CLI for a larger experiment.');
    const count = finiteNumber(input('ensemble-count').value, 'Paired seeds', 2, 20, true);
    comparison = await api<Comparison>('compare', {scenario, policies, seeds: pairedSeeds(scenario.seed, count), view: 'truth'});
    comparisonScenario = clone(scenario);
    renderComparison(); announce(`Compared ${policies.length} policies across ${count} paired seeds. Inspect uncertainty and paired differences below.`);
  });
}
function renderComparison(): void {
  if (!comparison) return;
  const available = Object.keys(comparison.summaries[0]?.metrics ?? {}).filter(key => metrics[key]);
  if (!available.includes(comparisonMetric)) comparisonMetric = available[0] ?? '';
  const summaries = comparisonMode === 'differences' ? comparison.differences : comparison.summaries;
  const rows = summaries.map(s => ({policy: s.policy, stats: s.metrics[comparisonMetric]})).filter(row => row.stats && Number.isFinite(row.stats.mean));
  const groupRows = summaries.flatMap(summary => (summary.distribution ?? []).flatMap(group => Object.entries(group.metrics).map(([key, stats]) => [humanize(summary.policy), group.name, group.population, humanize(key), stats.mean, stats.ci_low, stats.ci_high, stats.n])));
  get('comparison-results').replaceChildren(
    el('div', {class: 'comparison-view-controls'}, field('Outcome to compare', select('compare-metric', available.map(key => [key, metrics[key][0]]), comparisonMetric)),
      field('Comparison view', select('compare-mode', [['summaries', 'Policy outcomes'], ['differences', `Paired difference from ${humanize(comparison.baseline)}`]], comparisonMode))),
    el('h3', {}, metrics[comparisonMetric]?.[0] ?? 'Outcome'),
    el('p', {class: 'fine-print'}, `${metrics[comparisonMetric]?.[1] ?? ''}. Points show means; bars show the server-reported 95% Monte Carlo interval where defined. These intervals do not cover model uncertainty.`),
    rows.length ? intervalPlot(rows) : el('p', {}, 'This outcome has no defined denominator in the selected runs.'),
    table(['Policy', 'Mean', '95% lower', '95% upper', 'SD', 'n'], rows.map(({policy, stats}) => [humanize(policy), stats.mean, stats.ci_low, stats.ci_high, stats.sd, stats.n]), 'Policy comparison and Monte Carlo uncertainty'),
    el('p', {class: 'caution'}, comparison.note),
    el('p', {class: 'fine-print'}, `${comparison.model_version} · Seeds: ${comparison.seeds.join(', ')} · Baseline: ${humanize(comparison.baseline)}. Post-run research view. Terminal runs remain in the sample.`),
    details('Experiment conditions (research truth)', pretty({scenario: comparisonScenario?.name, horizon: comparisonScenario?.horizon, verification: comparisonScenario?.verification, dynamics: comparisonScenario?.dynamics, institution: comparisonScenario?.institution, strategies: comparisonScenario?.actors.map(actor => ({actor: actor.name, strategy: actor.strategy}))})),
    details('All disaggregated outcomes', ...summaries.map(summary => el('div', {}, el('h4', {}, humanize(summary.policy)), table(['Measure', 'Mean', '95% lower', '95% upper', 'n'], Object.entries(summary.metrics).map(([key, stats]) => [metrics[key]?.[0] ?? humanize(key), stats.mean, stats.ci_low, stats.ci_high, stats.n]), `${summary.policy} outcome vector`)))),
    details('Distribution across groups', el('p', {class: 'fine-print'}, 'Inspect who receives service and who bears restrictions, privacy exposure and incidents. Population is a synthetic weight. Service per population uses that weight, not a real-world population estimate. Paired-difference mode shows differences from the same baseline as the main table.'),
      groupRows.length ? table(['Policy', 'Group', 'Population weight', 'Measure', 'Mean', '95% lower', '95% upper', 'n'], groupRows, 'Policy comparison outcomes by affected group') : el('p', {}, 'No per-group comparison data was returned by the server.')),
  );
  get('compare-metric').addEventListener('change', () => { comparisonMetric = get<HTMLSelectElement>('compare-metric').value; renderComparison(); get('compare-metric').focus(); });
  get('compare-mode').addEventListener('change', () => { comparisonMode = get<HTMLSelectElement>('compare-mode').value; renderComparison(); get('compare-mode').focus(); });
}
function intervalPlot(rows: Array<{policy: string; stats: Stats}>): SVGSVGElement {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  const height = rows.length * 57 + 64;
  svg.setAttribute('viewBox', `0 0 680 ${height}`);
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', `${metrics[comparisonMetric]?.[0] ?? comparisonMetric} by policy. Values and intervals are in the following table.`);
  svg.classList.add('interval-plot');
  const [low, high] = intervalExtent(rows.map(row => row.stats));
  const x = (value: number) => 152 + (value - low) / (high - low) * 464;
  function shape(tag: string, attrs: Record<string, string>, text?: string): void {
    const node = document.createElementNS(ns, tag);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    if (text) node.textContent = text;
    svg.append(node);
  }
  for (let i = 0; i <= 4; i++) {
    const value = low + (high - low) * i / 4;
    shape('line', {x1: String(x(value)), x2: String(x(value)), y1: '13', y2: String(height - 40), class: 'plot-grid'});
    shape('text', {x: String(x(value)), y: String(height - 14), 'text-anchor': 'middle', class: 'plot-tick'}, format(value));
  }
  if (low < 0) shape('line', {x1: String(x(0)), x2: String(x(0)), y1: '13', y2: String(height - 40), class: 'plot-zero'});
  rows.forEach(({policy, stats}, index) => {
    const y = 35 + index * 57;
    shape('text', {x: '0', y: String(y + 5), class: 'plot-label'}, humanize(policy));
    if (stats.ci_low !== null && stats.ci_high !== null) {
      shape('line', {x1: String(x(stats.ci_low)), x2: String(x(stats.ci_high)), y1: String(y), y2: String(y), class: 'plot-interval'});
      for (const value of [stats.ci_low, stats.ci_high]) shape('line', {x1: String(x(value)), x2: String(x(value)), y1: String(y - 6), y2: String(y + 6), class: 'plot-interval'});
    }
    shape('circle', {cx: String(x(Number(stats.mean))), cy: String(y), r: '5', class: 'plot-point'});
  });
  return svg;
}

async function initialize(): Promise<void> {
  get('app').replaceChildren(el('div', {class: 'loading-screen'}, el('p', {class: 'wordmark'}, 'isobar'), el('p', {role: 'status'}, 'Opening the local research workbench…')));
  try {
    const catalog = await api<{scenarios: Scenario[]; policies: string[]; strategies: string[]}>('catalog');
    scenarios = catalog.scenarios; policies = catalog.policies; strategies = catalog.strategies;
    if (!scenarios.length) throw new Error('No scenarios were returned. Check the local server installation.');
    draft = clone(scenarios.find(s => s.id.toLowerCase() === 's2') ?? scenarios[1] ?? scenarios[0]);
    build();
    announce('Ready. Choose a scenario, review the assumptions, then run it.');
  } catch (error) {
    get('app').replaceChildren(el('div', {class: 'loading-screen'}, el('p', {class: 'wordmark'}, 'isobar'), el('h1', {}, 'The workbench could not open.'), el('p', {role: 'alert'}, error instanceof Error ? error.message : String(error)), button('retry', 'Try loading again')));
    get('retry').addEventListener('click', () => void initialize());
  }
}

void initialize();
