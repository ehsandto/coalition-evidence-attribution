import fs from 'node:fs';
import {spawn} from 'node:child_process';
import {receipt,source,state,read,digest,sha} from './check.mjs';
const file='PROOFS.json';
const signer='0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42';
let proofs;
if(fs.existsSync(file))proofs=JSON.parse(fs.readFileSync(file,'utf8'));
else{
 const commit=process.argv[2];
 if(!/^[0-9a-f]{40}$/.test(commit??''))throw Error('Supply the full published fixture commit');
 proofs={network:'studionet',chain_id:61999,signer,fixture_commit:commit,transactions:[],cases:{}};
}
const save=()=>fs.writeFileSync(file,JSON.stringify(proofs,null,2)+'\n');
function broadcast(args,onHash){
 return new Promise((resolve,reject)=>{
  const proc=spawn(process.execPath,['--dns-result-order=ipv4first','scripts/run-cli.cjs',...args],{
   windowsHide:true,env:{...process.env,COALITION_TEST_ACCOUNT:process.env.COALITION_TEST_ACCOUNT||'studio-proof-deployer'},stdio:['ignore','pipe','pipe']});
  let carry='';proc.stderr.resume();
  proc.stdout.on('data',chunk=>{carry+=chunk.toString();const lines=carry.split(/\r?\n/);carry=lines.pop();
   for(const line of lines)if(/^BROADCAST_HASH 0x[0-9a-fA-F]{64}$/.test(line))onHash(line.split(' ')[1]);});
  proc.on('error',()=>reject(Error('CLI launch failed')));proc.on('close',resolve);
 });
}
async function transaction(step,args,expected='SUCCESS',message){
 let entry=proofs.transactions.find(x=>x.step===step);
 if(!entry){entry={step,verified:false,broadcast_unknown:true};proofs.transactions.push(entry);save();
  await broadcast(args,hash=>{entry.hash=hash;delete entry.broadcast_unknown;save();console.log(step+' '+hash);});
 }
 if(!entry.hash)throw Error('Unknown broadcast outcome; inspect sender history');
 const inspected=await receipt(entry.hash,expected,message);Object.assign(entry,inspected,{verified:true});save();
 console.log(JSON.stringify({step,status:entry.status,execution:entry.execution}));return entry;
}
const claim='Every stored archive is encrypted at rest and deleted after thirty days.';
const sources=(names,bad=false)=>names.map((name,i)=>{
 const path='examples/'+name+'.txt',hash=bad&&i===0?'f'.repeat(64):sha(fs.readFileSync(path));
 return 'ehsandto/coalition-evidence-attribution/'+proofs.fixture_commit+'/'+path+'|'+hash;
}).join('\n');
try{
 const deploy=await transaction('deploy',['deploy','--contract','contracts/CoalitionEvidenceAttribution.py']);
 proofs.address=deploy.address;proofs.source=await source(proofs.address);save();
 const scenarios=[
  {name:'complementary-v1',claim,sources:sources(['encryption','deletion'])},
  {name:'uncertain-v1',claim:'The selected archive profile requires both encryption at rest and deletion after thirty days.',sources:sources(['encryption','ambiguity'])},
  {name:'bad-commitment-v1',claim,sources:sources(['encryption','deletion'],true)}
 ];
 for(const scenario of scenarios){
  const key=digest({contract:proofs.address,creator:proofs.signer,nonce:scenario.name});
  await transaction('open-'+scenario.name,['write',proofs.address,'open_case','--args',scenario.name,scenario.claim,scenario.sources]);
  const input=await read(proofs.address,'get_case',[key]);
  if(digest(input.spec)!==input.input_root)throw Error('Input root mismatch');
  await transaction('resolve-'+scenario.name,['write',proofs.address,'resolve','--args',key,input.input_root]);
  proofs.cases[scenario.name]=await state(proofs.address,key);save();
  console.log(JSON.stringify({scenario:scenario.name,...proofs.cases[scenario.name]}));
 }
 const first=proofs.cases['complementary-v1'];
 await transaction('replay-resolution',['write',proofs.address,'resolve','--args',first.case,first.input_root],'ERROR','Already resolved');
 await transaction('wrong-input-root',['write',proofs.address,'resolve','--args',first.case,'f'.repeat(64)],'ERROR','Input root mismatch');
 for(const [name,prior] of Object.entries(proofs.cases)){
  const current=await state(proofs.address,prior.case);
  if(current.root!==prior.root)throw Error('Negative test changed old result');
  proofs.cases[name]=current;
 }
 proofs.source=await source(proofs.address);proofs.final_readback_verified=true;save();
 console.log(JSON.stringify({complete:true,address:proofs.address,source_match:proofs.source.source_match,
  cases:Object.fromEntries(Object.entries(proofs.cases).map(([name,c])=>[name,c.output.status]))}));
}catch{console.error('Sanitized proof workflow stopped; inspect journal hashes and state before any retry');process.exitCode=1;}
