import {test} from 'node:test';
import assert from 'node:assert/strict';
import {layerValue, shares, relations} from './world-core.ts';

test('visual layers preserve missing information and use only displayed values', () => {
  assert.equal(layerValue({capability: 4, safety: 1}, 'gap'), 3);
  assert.equal(layerValue({capability: 4}, 'gap'), null);
  assert.equal(layerValue({service: null}, 'service'), null);
  assert.equal(layerValue({capability: 2, hidden_capacity: 1000}, 'capability'), 2);
  assert.deepEqual(shares([{id:'a',name:'A',capability:3},{id:'b',name:'B',capability:1}]).map(row=>row.share),[.75,.25]);
  assert.equal(shares([{id:'a',name:'A',capability:0}])[0].share,null);
  assert.equal(shares([{id:'a',name:'A',capability:3},{id:'b',name:'B'}])[0].share,null);
});

test('relationship overlays do not infer beliefs or membership of absent actors', () => {
  const actors = [{id:'a',member:true,beliefs:{b:.2,c:.8}},{id:'b',member:true},{id:'c',member:false}];
  assert.deepEqual(relations(actors,'a','coalition'),[{id:'b',value:1}]);
  assert.deepEqual(relations(actors,'c','coalition'),[]);
  assert.deepEqual(relations(actors,'b','beliefs'),[]);
  assert.deepEqual(relations(actors,'a','beliefs'),[{id:'b',value:.2},{id:'c',value:.8}]);
});
