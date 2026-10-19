import assert from 'node:assert/strict';
import {abi} from 'genlayer-js';
const {calldata}=abi;
for(const [name,args] of [
 ['open_case',['demo','Every stored archive is encrypted at rest and deleted after thirty days.','owner/repo/'+'a'.repeat(40)+'/a.txt|'+'b'.repeat(64)+'\nowner/repo/'+'a'.repeat(40)+'/b.txt|'+'c'.repeat(64)]],
 ['resolve',['a'.repeat(64),'b'.repeat(64)]],['get_case',['a'.repeat(64)]],
 ['get_resolution',['a'.repeat(64)]],['exact_attribution',['a'.repeat(64),'b'.repeat(64)]]]){
 const encoded=calldata.encode(calldata.makeCalldataObject(name,args,{}));
 assert.deepEqual(calldata.encode(calldata.decode(encoded)),encoded);
}
console.log('5 SDK calldata roundtrips passed');
