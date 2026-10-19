import test from 'node:test';
import assert from 'node:assert/strict';
import {canonical,digest,independentlyAttribute} from '../scripts/check.mjs';
test('independent permutation accounting gives complementary sources equal fractions',()=>{
 const x=independentlyAttribute(['NEITHER','NEITHER','NEITHER','SUPPORT'],2);
 assert.deepEqual(x.intervals,[{source_index:0,lower:1,upper:1,denominator:2},{source_index:1,lower:1,upper:1,denominator:2}]);
});
test('refutation remains signed rather than normalized to positive credit',()=>{
 const x=independentlyAttribute(['NEITHER','NEITHER','REFUTE','REFUTE'],2);
 assert.deepEqual(x.intervals.map(x=>x.lower),[0,-2]);
});
test('all-unknown three-player bounds enumerate 2187 games without point attribution',()=>{
 const x=independentlyAttribute(['NEITHER',...Array(7).fill('UNKNOWN')],3);
 assert.equal(x.status,'BOUNDED');
 assert.deepEqual(x.intervals.map(x=>[x.lower,x.upper,x.denominator]),[[-10,10,6],[-10,10,6],[-10,10,6]]);
});
test('canonical hashes use sorted keys and Python-compatible ASCII Unicode escaping',()=>{
 assert.equal(canonical({z:'é',a:'💡'}),'{"a":"\\ud83d\\udca1","z":"\\u00e9"}');
 assert.equal(digest({z:'é',a:'💡'}),digest({a:'💡',z:'é'}));
});
