import { test } from 'node:test';
import assert from 'node:assert/strict';
import { actionFromInputs, finiteNumber, format, intervalExtent, MAX_SEED, pairedSeeds, parseScenario, parseSeed, record } from './core.ts';

test('numeric controls reject empty, nonfinite, fractional seeds and out-of-range values', () => {
  for (const value of ['', ' ', 'Infinity', 'NaN', '-1', '1.5']) assert.throws(() => finiteNumber(value, 'Seed', 0, 100, true));
  assert.equal(finiteNumber('42', 'Seed', 0, 100, true), 42);
});
test('human actions conserve allocation and reject invalid fractions before calling the server', () => {
  const values = { train: '0.2', safety: '0.3', service: '0.4', idle: '0.1', conceal: '0', appeal: true, inspect: true };
  assert.equal(actionFromInputs(values).train, 0.2);
  assert.equal(actionFromInputs(values).appeal, true);
  assert.equal(actionFromInputs({...values, inspect: false}).inspect, false);
  assert.throws(() => actionFromInputs({ ...values, train: '0.9' }), /sum to 1/);
  assert.throws(() => actionFromInputs({ ...values, conceal: 'Infinity' }));
});
test('JSON editor requires an object and preserves hostile text as text', () => {
  for (const value of ['null', '[]', '42', '{oops']) assert.throws(() => parseScenario(value));
  assert.equal(parseScenario('{"name":"<img onerror=alert(1)>"}').name, '<img onerror=alert(1)>');
  assert.throws(() => parseScenario('{"seed":9007199254740992}'), /use the CLI/);
  assert.deepEqual(record(null), {});
});

test('JSON authoring and numeric controls share the full uint32 seed range', () => {
  for (const seed of [0, 3_000_000_000, MAX_SEED]) {
    assert.equal(parseSeed(String(seed)), seed);
    assert.equal(parseScenario(JSON.stringify({seed})).seed, seed);
  }
  for (const seed of [-1, 0.5, MAX_SEED + 1]) {
    assert.throws(() => parseSeed(String(seed)));
    assert.throws(() => parseScenario(JSON.stringify({seed})));
  }
});

test('paired seeds stay inside the model range without silently wrapping', () => {
  assert.deepEqual(pairedSeeds(3_000_000_000, 2), [3_000_000_000, 3_000_000_001]);
  assert.deepEqual(pairedSeeds(MAX_SEED - 1, 2), [MAX_SEED - 1, MAX_SEED]);
  assert.throws(() => pairedSeeds(MAX_SEED, 2), /starting seed at or below/);
  assert.throws(() => pairedSeeds(1, 1), /Paired seeds/);
});
test('interval charts include zero and negative differences; zero-denominator metrics are not zero', () => {
  assert.deepEqual(intervalExtent([]), [0, 1]);
  assert.deepEqual(intervalExtent([{mean: null, ci_low: null, ci_high: null}]), [0, 1]);
  const [lo, hi] = intervalExtent([{mean: -2, ci_low: -3, ci_high: -1}]);
  assert.ok(lo < -3 && hi > 0);
  assert.equal(format(null), 'Not available');
});
