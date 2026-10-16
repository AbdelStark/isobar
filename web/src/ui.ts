import {format} from './core';

export type Child = Node | string | null | undefined;

export function el<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, string> = {}, ...children: Child[]): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  for (const child of children) if (child !== null && child !== undefined) node.append(child);
  return node;
}
export function get<T extends HTMLElement = HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (!element) throw new Error(`Missing interface element: ${id}`);
  return element as T;
}
export const input = (id: string) => get<HTMLInputElement>(id);
export function field(label: string, control: HTMLElement, help?: string): HTMLElement {
  const wrapper = el('div', { class: 'field' }, el('label', { for: control.id }, label), control);
  if (help) {
    const helpId = `${control.id}-help`;
    control.setAttribute('aria-describedby', helpId);
    wrapper.append(el('small', { id: helpId }, help));
  }
  return wrapper;
}
export function numberField(id: string, label: string, value: number, min: number, max: number, step = '1', help?: string): HTMLElement {
  return field(label, el('input', { id, type: 'number', value: String(value), min: String(min), max: String(max), step, required: '' }), help);
}
export function select(id: string, choices: Array<[string, string]>, value?: string): HTMLSelectElement {
  const control = el('select', { id });
  for (const [key, text] of choices) {
    const option = el('option', { value: key }, text);
    option.selected = key === value;
    control.append(option);
  }
  return control;
}
export function button(id: string, text: string, kind = ''): HTMLButtonElement {
  return el('button', { id, type: 'button', class: kind }, text);
}
export function details(title: string, ...children: Child[]): HTMLDetailsElement {
  return el('details', {}, el('summary', {}, title), ...children);
}
export function table(headers: string[], rows: unknown[][], caption: string): HTMLElement {
  const numeric = headers.map((_, i) => rows.some(row => typeof row[i] === 'number'));
  const node = el('table', {}, el('caption', { class: 'sr-only' }, caption), el('thead', {}, el('tr', {}, ...headers.map((h, i) => el('th', { scope: 'col', class: numeric[i] ? 'numeric' : '' }, h)))));
  node.append(el('tbody', {}, ...rows.map(row => el('tr', {}, ...row.map((value, i) => el(i === 0 ? 'th' : 'td', { ...(i === 0 ? {scope: 'row'} : {}), class: numeric[i] ? 'numeric' : '' }, format(value)))))));
  return el('div', { class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': caption }, node);
}
export const pretty = (data: unknown) => el('pre', {}, el('code', {}, JSON.stringify(data, null, 2)));
