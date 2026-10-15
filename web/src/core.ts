export type JsonRecord = Record<string, unknown>;
export const MAX_SEED = 4_294_967_295;

export function record(value: unknown): JsonRecord {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as JsonRecord : {};
}

export function humanize(value: string): string {
  return value.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase());
}

export function format(value: unknown): string {
  if (value === null || value === undefined) return 'Not available';
  if (typeof value === 'number') return Number.isFinite(value)
    ? new Intl.NumberFormat('en', { maximumFractionDigits: 3 }).format(value)
    : 'Not available';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export function finiteNumber(value: string, label: string, min: number, max: number, integer = false): number {
  const parsed = Number(value);
  if (!value.trim() || !Number.isFinite(parsed) || parsed < min || parsed > max || (integer && !Number.isInteger(parsed))) {
    throw new Error(`${label} must be ${integer ? 'a whole number' : 'a number'} from ${min} to ${max}.`);
  }
  return parsed;
}

export function parseSeed(value: string): number {
  if (Number.isFinite(Number(value)) && Number(value) > MAX_SEED) throw new Error(`Browser seeds must be from 0 to ${MAX_SEED}. For larger seeds within the model's range, use the CLI.`);
  return finiteNumber(value, 'Seed', 0, MAX_SEED, true);
}

export function pairedSeeds(start: number, count: number): number[] {
  parseSeed(String(start));
  finiteNumber(String(count), 'Paired seeds', 2, 20, true);
  if (start + count - 1 > MAX_SEED) throw new Error(`For ${count} consecutive paired seeds, use a starting seed at or below ${MAX_SEED - count + 1}.`);
  return Array.from({length: count}, (_, index) => start + index);
}

export function actionFromInputs(values: Record<string, string | boolean>): JsonRecord {
  const action: JsonRecord = {};
  for (const key of ['train', 'safety', 'service', 'idle', 'conceal']) {
    action[key] = finiteNumber(String(values[key]), humanize(key), 0, 1);
  }
  const sum = ['train', 'safety', 'service', 'idle'].reduce((total, key) => total + Number(action[key]), 0);
  if (Math.abs(sum - 1) > 1e-9) throw new Error(`Training, safety, service and idle must sum to 1. Current total: ${format(sum)}.`);
  for (const key of ['appeal', 'renew', 'request_restart', 'inspect']) action[key] = Boolean(values[key]);
  return action;
}

export function intervalExtent(values: Array<{mean: number | null; ci_low: number | null; ci_high: number | null}>): [number, number] {
  const finite = values.flatMap(({mean, ci_low, ci_high}) => [mean, ci_low, ci_high]).filter((value): value is number => typeof value === 'number' && Number.isFinite(value));
  if (!finite.length) return [0, 1];
  const min = Math.min(0, ...finite), max = Math.max(0, ...finite);
  const pad = max === min ? 1 : (max - min) * 0.08;
  return [min < 0 ? min - pad : 0, max + pad];
}

export function parseScenario(text: string): JsonRecord {
  let value: unknown;
  try { value = JSON.parse(text); }
  catch { throw new Error('Scenario JSON is not valid. Check commas, quotes and brackets, then validate again.'); }
  if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new Error('A scenario must be a JSON object, not a list or a single value.');
  const seed = (value as JsonRecord).seed;
  if (typeof seed === 'number') parseSeed(String(seed));
  return value as JsonRecord;
}
