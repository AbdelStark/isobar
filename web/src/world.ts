import {geoDistance, geoEquirectangular, geoGraticule10, geoOrthographic, geoPath} from 'd3-geo';
import type {FeatureCollection, Feature, Geometry, LineString} from 'geojson';
import countries from './data/countries.json';
import {format, humanize, record, type JsonRecord} from './core';
import {layers, layerValue, number, relations, shares, type Layer} from './world-core';
import {el, field, select, button, details, table} from './ui';
import type {Actor, Frame, Run, Scenario} from './types';

type Country = Feature<Geometry, {name: string; center: [number, number]}>;
const geography = countries as FeatureCollection<Geometry, Country['properties']>;
const places = new Map(geography.features.map(feature => [String(feature.id), feature]));
const ns = 'http://www.w3.org/2000/svg';
function svg<K extends keyof SVGElementTagNameMap>(tag: K, attributes: Record<string, string> = {}, text?: string): SVGElementTagNameMap[K] {
  const node = document.createElementNS(ns, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  if (text) node.textContent = text;
  return node;
}
const percent = (value: number | null) => value === null ? 'Unavailable' : `${(value * 100).toFixed(1)}%`;
const strategyNotes: Record<string, string> = {
  compliant: 'Rule following: training stays within the legal allowance; remaining effort supports safety and service.',
  reciprocal: 'Conditional cooperation: restraint holds until the largest perceived probability of rival deviation exceeds the reciprocity threshold.',
  myopic: 'Myopic choice on a finite grid: maximize this period’s subjective benefit after expected enforcement and concealment costs.',
  bounded: 'Bounded choice: higher-utility allocations are more likely, with the configured inverse temperature determining how concentrated choices become.',
};
export type WorldState = {scenario: Scenario; run: Run | null; frameIndex: number; view: string; playing: boolean};
type Callbacks = {
  run: () => void; view: (value: string) => void; tick: (value: number) => void;
  play: () => void; edit: () => void; intervene: (actor: string) => void;
  decision: (actor: string, tick: number) => Promise<JsonRecord>;
};

export class WorldExplorer {
  readonly element = el('section', {id: 'world-explorer', class: 'world-explorer', 'aria-labelledby': 'world-heading'});
  private state: WorldState | null = null;
  private selected = 'fra';
  private layer: Layer = 'capability';
  private relation: 'coalition' | 'beliefs' = 'coalition';
  private mode = 'globe';
  private longitude = 20;
  private latitude = 20;
  private zoom = 1;
  private key = '';
  private runVersion = 0;
  private diagnosis: JsonRecord | null = null;
  private readonly map = svg('svg', {viewBox: '0 0 720 540', role: 'group', 'aria-label': 'Interactive Earth. Select a modeled country or use the nation list.'});
  private readonly mapBody = svg('g');
  private readonly roster = el('div', {class: 'nation-list', id: 'nation-list', 'aria-label': 'Modeled nations'});
  private readonly inspector = el('div', {id: 'nation-inspector', class: 'nation-inspector'});
  private readonly analysis = el('section', {id: 'decision-analysis', class: 'decision-analysis', 'aria-label': 'Decision analysis', hidden: ''});
  private readonly news = el('div', {class: 'world-news', id: 'world-news'});
  private readonly legend = el('p', {class: 'map-legend', id: 'map-legend'});
  private readonly notice = el('p', {class: 'world-boundary', id: 'world-boundary'});
  private readonly tickInput = el('input', {id: 'world-timeline', type: 'range', min: '0', max: '0', value: '0'});
  private readonly tickOutput = el('output', {for: 'world-timeline', id: 'world-tick'});
  private readonly playButton = button('world-play', 'Play world');
  private readonly viewControl = select('world-view', [['public', 'Public record']]);
  private readonly runButton = button('world-run', 'Simulate world', 'primary');

  constructor(private readonly callbacks: Callbacks) {
    const projection = select('world-projection', [['globe', 'Globe'], ['map', 'World map']]);
    const layer = select('world-layer', Object.entries(layers).map(([key, value]) => [key, value.label]));
    const relation = select('world-relations', [['coalition', 'Coalition membership'], ['beliefs', 'Perceived deviation']]);
    const defs = svg('defs');
    const gradient = svg('radialGradient', {id: 'earth-sea', cx: '35%', cy: '30%', r: '75%'});
    gradient.append(svg('stop', {offset: '0%', 'stop-color': '#284c49'}), svg('stop', {offset: '100%', 'stop-color': '#142f30'}));
    defs.append(gradient);
    this.map.append(defs, this.mapBody);
    const west = button('world-west', '←', 'map-button'), east = button('world-east', '→', 'map-button');
    const closer = button('world-zoom-in', '+', 'map-button'), farther = button('world-zoom-out', '−', 'map-button');
    west.setAttribute('aria-label', 'Rotate Earth west'); east.setAttribute('aria-label', 'Rotate Earth east');
    closer.setAttribute('aria-label', 'Zoom in'); farther.setAttribute('aria-label', 'Zoom out');
    const reset = button('world-reset', 'Reset view', 'map-button');
    const edit = button('world-edit', 'Edit conditions');
    this.element.append(
      el('div', {class: 'world-heading'},
        el('div', {}, el('p', {class: 'eyebrow'}, 'EARTH / STRATEGIC OBSERVATORY'), el('h2', {id: 'world-heading'}, 'The world, in motion.')),
        el('div', {class: 'world-actions'}, edit, this.runButton)),
      el('p', {class: 'world-provenance'}, 'Real geography. Illustrative states, strategies and values. This is a conditional simulation, not a forecast.'),
      el('div', {class: 'world-toolbar'}, field('Projection', projection), field('Map layer', layer), field('Relationships', relation), field('World observation boundary', this.viewControl)),
      this.notice,
      el('div', {class: 'world-layout'},
        el('div', {class: 'earth-column'},
          el('div', {class: 'earth-canvas'}, this.map,
            el('div', {class: 'earth-coordinate', 'aria-hidden': 'true'}, 'ISOBAR / EARTH'),
            el('div', {class: 'map-navigation', 'aria-label': 'Map controls'}, west, east, farther, closer, reset)),
          this.legend,
          el('div', {class: 'world-timeline'}, this.playButton, field('World replay tick', this.tickInput), this.tickOutput),
          this.news,
          el('p', {class: 'map-credit'}, 'Natural Earth · countries outside the scenario are not simulated. Boundary depiction is geographic context, not a political claim. ', el('a', {href:'/third-party.txt', target:'_blank', rel:'noopener'}, 'Map and library credits'))),
        el('div', {class: 'world-sidebar'}, el('h3', {}, 'Capability balance'), el('p', {class: 'fine-print'}, 'Share of displayed capability among modeled states. Select a state to inspect its trajectory.'), this.roster, this.inspector)),
      this.analysis,
    );
    projection.addEventListener('change', () => {this.mode = projection.value; this.zoom = 1; west.disabled = east.disabled = this.mode !== 'globe'; this.renderMap();});
    layer.addEventListener('change', () => {this.layer = layer.value as Layer; this.renderMap();});
    relation.addEventListener('change', () => {this.relation = relation.value as 'coalition' | 'beliefs'; this.renderMap();});
    this.viewControl.addEventListener('change', () => this.callbacks.view(this.viewControl.value));
    this.runButton.addEventListener('click', callbacks.run);
    this.playButton.addEventListener('click', callbacks.play);
    edit.addEventListener('click', callbacks.edit);
    this.tickInput.addEventListener('input', () => callbacks.tick(Number(this.tickInput.value)));
    for (const panel of [this.map, this.roster, this.inspector]) {
      panel.addEventListener('focusin', () => {if (this.state?.playing) callbacks.play();});
    }
    west.addEventListener('click', () => {this.longitude -= 30; this.renderMap();});
    east.addEventListener('click', () => {this.longitude += 30; this.renderMap();});
    closer.addEventListener('click', () => {this.zoom = Math.min(2, this.zoom + .2); this.renderMap();});
    farther.addEventListener('click', () => {this.zoom = Math.max(.8, this.zoom - .2); this.renderMap();});
    reset.addEventListener('click', () => {this.longitude = 20; this.latitude = 20; this.zoom = 1; this.renderMap();});
    let drag: {x: number; y: number; lon: number; lat: number} | null = null;
    let moved = false;
    this.map.addEventListener('pointerdown', event => {
      if (this.mode !== 'globe' || event.button !== 0) return;
      drag = {x: event.clientX, y: event.clientY, lon: this.longitude, lat: this.latitude}; moved = false;
    });
    this.map.addEventListener('pointermove', event => {
      if (!drag) return;
      if (Math.abs(event.clientX - drag.x) + Math.abs(event.clientY - drag.y) > 5) moved = true;
      if (!moved) return;
      this.map.setPointerCapture(event.pointerId);
      const scale = 180 / this.map.getBoundingClientRect().width;
      this.longitude = drag.lon - (event.clientX - drag.x) * scale;
      this.latitude = Math.max(-65, Math.min(65, drag.lat + (event.clientY - drag.y) * scale));
      this.renderMap();
    });
    this.map.addEventListener('pointerup', () => {drag = null;});
    this.map.addEventListener('pointercancel', () => {drag = null;});
    this.map.addEventListener('click', event => {
      if (moved) {moved = false; return;}
      const target = (event.target as Element).closest('[data-country]');
      if (target) this.selectNation(target.getAttribute('data-country')!);
    });
    this.map.addEventListener('keydown', event => {
      const target = (event.target as Element).closest('[data-country]');
      if (target && ['Enter', ' '].includes(event.key)) {event.preventDefault(); this.selectNation(target.getAttribute('data-country')!, true);}
    });
  }

  update(state: WorldState): void {
    if (this.state?.run !== state.run) {this.runVersion += 1; this.diagnosis = null;}
    this.state = state;
    if (!this.actors.some(actor => actor.id === this.selected)) this.selected = this.actors[0]?.id ?? '';
    const key = `${this.runVersion}:${state.frameIndex}:${this.selected}:${state.view}`;
    if (key !== this.key) {
      this.key = key; this.diagnosis = null;
      this.analysis.replaceChildren(); this.analysis.hidden = true;
    }
    const choices = [['public', 'Public record'], ...this.actors.map(actor => [actor.id, `${actor.name}’s observations`]), ['truth', 'Post-run ground truth']];
    if (this.viewControl.options.length !== choices.length || [...this.viewControl.options].some((option,i) => option.value !== choices[i]?.[0] || option.textContent !== choices[i]?.[1])) {
      this.viewControl.replaceChildren(...choices.map(([value, label]) => el('option', {value}, label)));
    }
    this.viewControl.value = state.view;
    this.viewControl.disabled = !state.run;
    this.playButton.disabled = !state.run?.frames.length;
    this.playButton.textContent = state.playing ? 'Pause world' : 'Play world';
    this.tickInput.disabled = !state.run?.frames.length;
    this.tickInput.max = String(Math.max(0, (state.run?.frames.length ?? 1) - 1));
    this.tickInput.value = String(state.frameIndex);
    this.tickOutput.textContent = state.run ? `${state.frameIndex} / ${this.tickInput.max}` : 'SETUP';
    this.runButton.textContent = state.run ? 'Run again' : 'Simulate world';
    this.notice.classList.toggle('truth-notice', Boolean(state.run) && state.view === 'truth');
    this.notice.textContent = !state.run ? 'INITIAL CONDITIONS · Researcher setup. Run the scenario to watch the balance shift.'
      : state.view === 'truth' ? 'POST-RUN TRUTH · Includes hidden state. Values describe this synthetic run only.'
      : state.view === 'public' ? 'PUBLIC RECORD · Capability and safety are declared-work estimates. Private incentives and hidden allocations are withheld.'
      : `${this.actors.find(actor=>actor.id===state.view)?.name ?? state.view}’S OBSERVATIONS · Own state plus observed rivals. Other nations’ private incentives are withheld.`;
    this.renderMap(); this.renderRoster(); this.renderInspector(); this.renderNews();
  }

  setPlaying(value: boolean): void {
    if (this.state) this.state.playing = value;
    this.playButton.textContent = value ? 'Pause world' : 'Play world';
  }

  private get actors(): Actor[] {
    return this.state?.run ? this.state.run.frames[this.state.frameIndex]?.actors ?? [] : this.state?.scenario.actors ?? [];
  }

  private selectNation(id: string, focus = false): void {
    if (this.state?.playing) this.callbacks.play();
    this.selected = id;
    const place = places.get(id);
    if (place) [this.longitude, this.latitude] = place.properties.center;
    this.diagnosis = null;
    if (this.state) this.update(this.state);
    if (focus) this.roster.querySelector<HTMLButtonElement>(`[data-nation="${id}"]`)?.focus();
  }

  private renderMap(): void {
    const projection = (this.mode === 'globe' ? geoOrthographic().rotate([-this.longitude, -this.latitude]) : geoEquirectangular())
      .translate([360,270]).scale((this.mode === 'globe' ? 248 : 108) * this.zoom);
    const path = geoPath(projection);
    this.mapBody.replaceChildren(svg('path', {d: path({type: 'Sphere'}) ?? '', fill: 'url(#earth-sea)', class: 'earth-sphere'}));
    this.mapBody.append(svg('path', {d: path(geoGraticule10()) ?? '', class: 'earth-grid', 'aria-hidden': 'true'}));
    const values = this.actors.map(actor => layerValue(actor, this.layer)).filter((value): value is number => value !== null);
    const low = Math.min(0, ...values), high = Math.max(1e-6, ...values);
    const fill = (value: number | null) => {
      if (value === null) return '#355652';
      const t = Math.max(0, Math.min(1, (value-low)/(high-low)));
      return this.layer === 'gap' ? `hsl(${45-27*t} 48% ${78-30*t}%)` : this.layer === 'service' ? `hsl(43 47% ${81-33*t}%)` : `hsl(158 ${20+10*t}% ${80-40*t}%)`;
    };
    for (const country of geography.features) {
      const id = String(country.id), actor = this.actors.find(actor => actor.id === id);
      const d = path(country);
      if (!d) continue;
      const shape = svg('path', {d, class: `earth-country${actor ? ' modeled' : ''}${id === this.selected ? ' selected' : ''}`, fill: actor ? fill(layerValue(actor, this.layer)) : '#355652'});
      if (actor) {
        shape.setAttribute('data-country', id); shape.setAttribute('role', 'button'); shape.setAttribute('tabindex', '0');
        shape.setAttribute('aria-label', `Select ${actor.name}`); shape.setAttribute('aria-pressed', String(id === this.selected));
      } else shape.setAttribute('aria-hidden', 'true');
      shape.append(svg('title', {}, actor ? `${actor.name} · ${layers[this.layer].unit}: ${format(layerValue(actor, this.layer))}` : `${country.properties.name} · not simulated`));
      this.mapBody.append(shape);
    }
    const origin = places.get(this.selected)?.properties.center;
    const connections = relations(this.actors, this.selected, this.relation);
    if (origin) for (const connection of connections) {
      const target = places.get(connection.id)?.properties.center;
      if (!target) continue;
      const line: LineString = {type: 'LineString', coordinates: [origin, target]};
      const arc = svg('path', {d: path(line) ?? '', class: `earth-link ${this.relation}`, 'stroke-width': String(this.relation === 'beliefs' ? 1+connection.value*3 : 1.5), 'aria-hidden': 'true'});
      this.mapBody.append(arc);
    }
    for (const actor of this.actors) {
      const point = places.get(actor.id)?.properties.center;
      if (!point || (this.mode === 'globe' && geoDistance(point, [this.longitude, this.latitude]) > Math.PI/2-.03)) continue;
      const projected = projection(point);
      if (!projected) continue;
      const [x,y] = projected;
      const active = this.state?.run?.events.some(event => event.tick === this.state?.frameIndex && event.actor_id === actor.id && event.kind !== 'allocation');
      const marker = svg('g', {transform:`translate(${x},${y})`, 'data-country': actor.id, class: `earth-marker${active ? ' has-event' : ''}`, 'aria-hidden':'true'});
      marker.append(svg('circle', {r: actor.id===this.selected ? '8' : '5', class: actor.member ? 'member' : 'outsider'}));
      marker.append(svg('text', {x:'12', y:'4'}, actor.id.toUpperCase()));
      if (active) marker.append(svg('circle', {r:'13', class:'event-ring'}));
      this.mapBody.append(marker);
    }
    const mapped = this.actors.filter(actor=>places.has(actor.id)).length;
    this.legend.replaceChildren(
      el('strong', {}, layers[this.layer].unit), el('span', {class:`legend-ramp ${this.layer}`, 'aria-hidden':'true'}),
      el('span', {}, `${values.length ? `${format(low)} — ${format(high)}` : 'Unavailable'} · ${mapped}/${this.actors.length} states on Earth`),
      el('small', {}, this.relation === 'coalition' ? 'Links: shared synthetic rule membership with the selected state, not real-world alliances.' : connections.length ? 'Links: selected state’s perceived probability of rival deviation; thicker means higher. These are beliefs, not facts.' : 'Private beliefs are unavailable in this view. Inspect the selected nation’s observations to reveal them.'),
      el('small', {}, mapped ? layers[this.layer].description : 'This fixture has fictional actors without geographic locations. Select the world scenario in conditions to use national geography.'),
    );
  }

  private renderRoster(): void {
    this.roster.replaceChildren(...shares(this.actors).sort((a,b)=>(b.share ?? 0)-(a.share ?? 0)).map(row=>{
      const actor = this.actors.find(actor=>actor.id===row.id)!;
      const control = button(`nation-${row.id}`, '', 'nation-row');
      control.setAttribute('data-nation', row.id); control.setAttribute('aria-pressed', String(this.selected===row.id));
      const bar = el('span', {class: 'nation-bar', 'aria-hidden':'true'}); bar.style.width=`${(row.share ?? 0)*100}%`;
      control.append(bar, el('span', {class: actor.member ? 'nation-dot member' : 'nation-dot', 'aria-hidden':'true'}), el('span', {class:'nation-name'}, row.name), el('span', {class:'nation-share'}, percent(row.share)));
      control.addEventListener('click', ()=>this.selectNation(row.id, true));
      return control;
    }));
  }

  private renderInspector(): void {
    const actor = this.actors.find(actor=>actor.id===this.selected);
    if (!actor || !this.state) {this.inspector.replaceChildren(); return;}
    const metrics = [['Capability', actor.capability], ['Safety readiness', actor.safety], ['Declared compute', actor.declared_capacity], ['Useful service', actor.service]];
    const factors = el('dl', {class:'nation-factors'}, ...metrics.flatMap(([label,value])=>[el('dt',{},String(label)),el('dd',{},format(value))]));
    const inspect = button('inspect-decision', 'Inspect this decision');
    const see = button('inspect-observations', 'See this nation’s observations');
    const intervene = button('world-intervene', 'Change its decision');
    const permitted = this.state.run && [this.selected,'truth'].includes(this.state.view);
    inspect.disabled = !permitted;
    see.disabled = !this.state.run;
    intervene.disabled = !this.state.run;
    inspect.addEventListener('click', ()=>void this.inspect());
    see.addEventListener('click', ()=>this.callbacks.view(this.selected));
    intervene.addEventListener('click', ()=>this.callbacks.intervene(this.selected));
    const beliefs = relations(this.actors, this.selected, 'beliefs');
    const relationRows = beliefs.map(peer=>[this.actors.find(actor=>actor.id===peer.id)?.name ?? peer.id, percent(peer.value)]);
    const ownEvents = this.state.run?.events.filter(event=>event.actor_id===this.selected && event.tick===this.state?.frameIndex && event.kind==='allocation');
    const work = record(ownEvents?.[0]?.data.work);
    this.inspector.replaceChildren(
      el('p',{class:'eyebrow'}, `STATE DOSSIER / ${this.selected.toUpperCase()}`),
      el('h3',{id:'selected-nation'},actor.name),
      el('p',{class:'fine-print'},`${actor.member ? 'Synthetic coalition member' : 'Outside the synthetic coalition'} · ${this.state.run ? actor.knowledge ?? 'Post-run truth' : 'Initial conditions'}`),
      factors,
      this.state.run ? this.trajectory(this.state.run.frames, actor.id) : el('p',{class:'empty-note'},'Run the world to reveal trajectories, institutional responses and strategic decisions.'),
      Object.keys(work).length ? this.allocation(work) : el('p',{class:'fine-print'},'Work allocations are private. They appear in this nation’s observations and post-run truth.'),
      el('p',{class:'strategy-caption'},actor.strategy ? `${humanize(actor.strategy)} · ${strategyNotes[actor.strategy] ?? 'Configured strategy.'}` : 'Strategy and subjective incentives are private in this view.'),
      el('div',{class:'dossier-actions'},see,intervene,inspect),
      ...(relationRows.length ? [details('Perceived rival deviation',table(['Rival','Belief'],relationRows,'Selected nation beliefs'))] : []),
    );
    if (this.diagnosis) this.renderDecision(this.diagnosis);
  }

  private trajectory(frames: Frame[], actorId: string): HTMLElement {
    const series = frames.map(frame=>frame.actors.find(actor=>actor.id===actorId));
    const values = series.flatMap(actor=>[number(actor?.capability),number(actor?.safety)]).filter((v): v is number=>v!==null);
    const high = Math.max(1,...values);
    const chart=svg('svg',{viewBox:'0 0 360 150',role:'img','aria-label':'Capability and safety through the full replay. The vertical line marks the selected tick.',class:'trajectory'});
    const x=(i:number)=>35+i/Math.max(1,frames.length-1)*310, y=(value:number)=>120-value/high*104;
    for (const value of [0,high/2,high]) {
      chart.append(svg('line',{x1:'35',x2:'345',y1:String(y(value)),y2:String(y(value)),class:'trajectory-grid'}),svg('text',{x:'0',y:String(y(value)+4)},format(value)));
    }
    for (const key of ['capability','safety']) {
      let d=''; let connected=false;
      series.forEach((actor,i)=> {const value=number(actor?.[key]); if(value===null){connected=false;return;} d+=`${connected?'L':'M'}${x(i)},${y(value)} `;connected=true;});
      chart.append(svg('path',{d,class:`trajectory-${key}`}));
    }
    const at=this.state?.frameIndex ?? 0;
    chart.append(svg('line',{x1:String(x(at)),x2:String(x(at)),y1:'10',y2:'122',class:'trajectory-cursor'}),svg('text',{x:'35',y:'145'},'0'),svg('text',{x:'320',y:'145'},String(frames.length-1)));
    const rows=frames.map((frame,i)=>[frame.tick,series[i]?.capability,series[i]?.safety]);
    return el('div',{class:'trajectory-wrap'},el('p',{class:'fine-print'},'Full replay · capability — / safety - -'),chart,details('Trajectory values',table(['Tick','Capability','Safety'],rows,'Nation trajectory')));
  }

  private allocation(work: JsonRecord, fractions = false): HTMLElement {
    const total = ['train','safety','service','idle'].reduce((sum,key)=>sum+(number(work[key]) ?? 0),0);
    const bar=el('div',{class:'allocation-bar','aria-hidden':'true'});
    for(const key of ['train','safety','service','idle']) {
      const segment=el('span',{class:`allocation-${key}`});segment.style.width=`${total ? Number(work[key] ?? 0)/total*100 : 0}%`;bar.append(segment);
    }
    return el('div',{class:'allocation'},el('h4',{},fractions ? 'Chosen allocation fractions' : 'Compute allocation (synthetic units)'),bar,el('p',{class:'fine-print'},...['train','safety','service','idle'].map(key=>`${humanize(key)} ${format(work[key])}  `)));
  }

  private renderNews(): void {
    const state=this.state;
    const events=state?.run?.events.filter(event=>event.tick===state.frameIndex && event.kind!=='allocation') ?? [];
    const frame=state?.run?.frames[state.frameIndex];
    this.news.replaceChildren(
      el('div',{class:'world-institution'},el('span',{},frame ? (frame.institution.active ? 'RULE ACTIVE' : 'RULE INACTIVE') : 'READY TO SIMULATE'),el('span',{},`${humanize(String(state?.scenario.policy.family ?? ''))} policy`)),
      el('h3',{},'At this tick'),
      events.length ? el('ul',{},...events.slice(-3).map(event=>el('li',{},el('strong',{},humanize(event.kind)),el('span',{},event.summary)))) : el('p',{class:'fine-print'},state?.run ? 'No visible institutional or incident events at this tick. Advance the timeline to follow what happens next.' : 'A shared world. Different incentives. Start the simulation to watch their consequences.'),
      ...(events.length>3 ? [el('p',{class:'fine-print'},`${events.length} visible records at this tick; the evidence panel contains the complete visible timeline.`)] : []),
    );
  }

  private async inspect(): Promise<void> {
    if(!this.state?.run) return;
    const key=this.key, at=this.state.frameIndex;
    const container=this.analysis;
    const control=this.inspector.querySelector<HTMLButtonElement>('#inspect-decision')!;
    control.disabled=true;container.hidden=false;
    container.replaceChildren(el('p',{role:'status'},'Reconstructing pre-decision incentives…'));
    try {
      const result=await this.callbacks.decision(this.selected,at);
      if(key!==this.key) return;
      this.diagnosis=result;this.renderDecision(result);
      container.scrollIntoView({block:'start'});
      container.querySelector<HTMLElement>('h3')?.focus({preventScroll:true});
    } catch(error) {
      if(key===this.key) {
        container.replaceChildren(el('p',{role:'alert'},error instanceof Error ? error.message : String(error)));
        container.scrollIntoView({block:'start'});
      }
    } finally {if(key===this.key) control.disabled=false;}
  }

  private renderDecision(data: JsonRecord): void {
    const container=this.analysis;container.hidden=false;
    const alternatives=Array.isArray(data.alternatives)?data.alternatives.map(record):[];
    const min=Math.min(0,...alternatives.map(row=>Number(row.utility))),max=Math.max(0,...alternatives.map(row=>Number(row.utility)));
    const chart=svg('svg',{viewBox:'0 0 360 226',role:'img','aria-label':'One-period utility by possible allocation. Values and components follow in a table.',class:'payoff-chart'});
    const x=(value:number)=>128+(value-min)/(max-min || 1)*175;
    alternatives.forEach((row,i)=> {
      const y=18+i*34;
      chart.append(svg('text',{x:'0',y:String(y+4)},String(row.label)),svg('line',{x1:String(x(0)),x2:String(x(Number(row.utility))),y1:String(y),y2:String(y),class:row.breach?'payoff-breach':'payoff-lawful'}),svg('circle',{cx:String(x(Number(row.utility))),cy:String(y),r:'4'}),svg('text',{x:'315',y:String(y+4)},format(row.utility)));
    });
    chart.append(svg('line',{x1:String(x(0)),x2:String(x(0)),y1:'4',y2:'200',class:'trajectory-cursor'}));
    const rows=alternatives.map(row=>[row.label,['train','safety','service','idle'].map(key=>format(record(row.action)[key])).join(' / '),record(row.action).conceal,row.utility,row.capability,row.service,row.safety,row.sanction,row.concealment,row.breach?'Above allowance':'Within allowance',row.probability===null?'Not sampled':percent(number(row.probability))]);
    const selected=record(data.selected_action);
    container.replaceChildren(
      el('p',{class:'eyebrow'},`STRATEGIC DECISION / ${this.actors.find(actor=>actor.id===data.actor_id)?.name ?? data.actor_id}`),
      el('h3',{tabindex:'-1'},`Decision at tick ${data.tick}`),el('p',{class:'fine-print'},`${humanize(String(data.source))} · pre-action observations. ${String(data.note)}`),
      el('div',{class:'decision-overview'},
        el('div',{},
          el('dl',{class:'nation-factors'},el('dt',{},'Available compute'),el('dd',{},format(data.available_capacity)),el('dt',{},'Legal training allowance'),el('dd',{},format(data.permitted_training)),el('dt',{},'Assumed detection'),el('dd',{},percent(number(data.detection_probability)))),
          this.allocation(selected, true),
          el('p',{class:'fine-print'},`Concealment ${percent(number(selected.conceal))} · Inspection ${selected.inspect ? 'permitted' : 'denied'} · Appeals ${selected.appeal ? 'enabled' : 'disabled'} · Renewal ${selected.renew ? 'requested' : 'not requested'} · Restart ${selected.request_restart ? 'requested' : 'not requested'}.`)),
        el('div',{},chart,el('p',{class:'fine-print'},'Utility = capability + service + safety − expected sanction − concealment. Rust marks allocations above the legal allowance.'))),
      details('Payoff components and choice probabilities',table(['Allocation','Train / safety / service / idle','Conceal fraction','Utility','Capability','Service','Safety','Sanction cost','Conceal cost','Legality','Choice probability'],rows,'Decision payoff alternatives')),
      ...(data.strategy==='reciprocal' ? [el('p',{class:'fine-print'},`Reciprocity threshold: ${percent(number(data.reciprocity_threshold))}. Highest pre-decision rival belief: ${percent(Math.max(0,...Object.values(record(data.beliefs)).map(Number)))}.`)] : []),
    );
  }
}
