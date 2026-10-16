import {record, type JsonRecord} from './core.ts';

export const layers = {
  capability: {label: 'Capability', unit: 'Capability index', description: 'Declared-work estimates in public and rival views; true capability only for own state or post-run truth.'},
  gap: {label: 'Readiness gap', unit: 'Capability − safety', description: 'Difference of the displayed capability and safety indices, before the model’s hazard threshold. It is not a probability.'},
  service: {label: 'Useful service', unit: 'Cumulative service', description: 'Synthetic useful service delivered through the selected tick.'},
} as const;
export type Layer = keyof typeof layers;
export function number(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}
export function layerValue(actor: JsonRecord, layer: Layer): number | null {
  if (layer !== 'gap') return number(actor[layer]);
  const capability = number(actor.capability), safety = number(actor.safety);
  return capability === null || safety === null ? null : capability - safety;
}
export function shares(actors: JsonRecord[]): Array<{id: string; name: string; share: number | null; capability: number | null}> {
  const values = actors.map(actor => number(actor.capability));
  const total = values.reduce<number>((sum, value) => sum + (value ?? 0), 0);
  const complete = values.every(value => value !== null && value >= 0);
  return actors.map((actor, i) => ({id: String(actor.id), name: String(actor.name), capability: values[i], share: complete && total > 0 ? values[i]! / total : null}));
}
export function relations(actors: JsonRecord[], selected: string, mode: 'coalition' | 'beliefs'): Array<{id: string; value: number}> {
  const own = actors.find(actor => actor.id === selected);
  if (!own) return [];
  if (mode === 'coalition') return own.member === true ? actors.filter(actor => actor.id !== selected && actor.member === true).map(actor => ({id: String(actor.id), value: 1})) : [];
  return Object.entries(record(own.beliefs)).filter(([id, value]) => id !== selected && actors.some(actor => actor.id === id) && number(value) !== null).map(([id, value]) => ({id, value: Number(value)}));
}
