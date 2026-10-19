import fs from 'node:fs';
import crypto from 'node:crypto';
import dns from 'node:dns';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
dns.setDefaultResultOrder('ipv4first');
export const canonical=x=>x===null||typeof x!=='object'?JSON.stringify(x).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0')):
 Array.isArray(x)?'['+x.map(canonical).join(',')+']':'{'+Object.keys(x).sort().map(k=>canonical(k)+':'+canonical(x[k])).join(',')+'}';
export const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
export const digest=x=>sha(canonical(x));
// Match Python str.split() whitespace, including NEL and U+001C..U+001F,
// without treating U+FEFF as whitespace as JavaScript trim() would.
export const normalizedText=x=>x.split(/[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+/u).filter(Boolean).join(' ');
export async function rpc(method,params){
 const r=await fetch('https://studio.genlayer.com/api',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params}),signal:AbortSignal.timeout(20000)});
 if(!r.ok)throw Error('HTTP failure');const p=await r.json();if(p.error||p.result==null)throw Error('RPC failure');return p.result;
}
export const client=createClient({chain:studionet});
export const read=(address,functionName,args)=>client.readContract({address,functionName,args});
export async function receipt(hash,expected='SUCCESS',message,allowedConsensus=['MAJORITY_AGREE']){
 let tx=await rpc('eth_getTransactionByHash',[hash]);
 for(let i=0;tx.status!=='FINALIZED'&&i<20;i++){await new Promise(r=>setTimeout(r,2500));tx=await rpc('eth_getTransactionByHash',[hash]);}
 const leader=tx.consensus_data?.leader_receipt?.find(x=>x.mode==='leader');
 const raw=leader?.genvm_result?.stderr||leader?.result;
 const decoded=typeof raw!=='string'?'':(/^[A-Za-z0-9+/]*={0,2}$/.test(raw)&&raw.length%4===0?Buffer.from(raw,'base64').toString('utf8'):raw);
 const result={hash,address:tx.to_address??tx.to,status:tx.status,execution:leader?.execution_result,consensus:tx.result_name,
  ...(message?{expected_error_matched:decoded.includes(message)}:{})};
 if(tx.status!=='FINALIZED'||leader?.execution_result!==expected||!allowedConsensus.includes(tx.result_name)||(message&&!decoded.includes(message)))throw Error('Receipt unverified');
 return result;
}
export async function source(address){
 const normalize=x=>x.replace(/\r\n/g,'\n').trimEnd()+'\n';
 const actual=normalize(Buffer.from(await rpc('gen_getContractCode',[address]),'base64').toString('utf8'));
 const local=normalize(fs.readFileSync('contracts/CoalitionEvidenceAttribution.py','utf8'));
 if(actual!==local)throw Error('Source mismatch');return {address,source_match:true,sha256:sha(actual)};
}
const permutations=a=>a.length===0?[[]]:a.flatMap((x,i)=>permutations(a.filter((_,j)=>i!==j)).map(p=>[x,...p]));
// Independent checker uses permutations and exhaustive unknown completions,
// rather than the contract's subset-factorial interval formula.
export function independentlyAttribute(labels,n){
 const orders=permutations(Array.from({length:n},(_,i)=>i));
 const utility={SUPPORT:1,REFUTE:-1,NEITHER:0};
 const unknown=labels.flatMap((x,i)=>x==='UNKNOWN'?[i]:[]),low=Array(n).fill(Infinity),high=Array(n).fill(-Infinity);
 const values=labels.map(x=>utility[x]??0);
 function visit(k){
  if(k<unknown.length){for(const v of [-1,0,1]){values[unknown[k]]=v;visit(k+1);}return;}
  const sums=Array(n).fill(0);
  for(const order of orders){let mask=0;for(const i of order){const next=mask|(1<<i);sums[i]+=values[next]-values[mask];mask=next;}}
  if(sums.reduce((a,b)=>a+b,0)!==values.at(-1)*orders.length)throw Error('Efficiency mismatch');
  sums.forEach((v,i)=>{low[i]=Math.min(low[i],v);high[i]=Math.max(high[i],v);});
 }
 visit(0);return {status:unknown.length?'BOUNDED':'EXACT',intervals:low.map((v,i)=>({source_index:i,lower:v,upper:high[i],denominator:orders.length})),
 full_coalition:labels.at(-1),utility_map:utility,unknown_domain:[-1,1],document_attribution_only:true};
}
export async function state(address,key){
 const c=await read(address,'get_case',[key]),record=await read(address,'get_resolution',[key]),{root,...body}=record;
 if(digest(c.spec)!==c.input_root||digest(body)!==root||c.spec.contract!==address||
  digest({contract:address,creator:c.spec.creator,nonce:c.spec.nonce})!==key||
  canonical(record.report.binding)!==canonical({case:key,contract:address,input_root:c.input_root,policy:c.spec.policy}))throw Error('Root/binding mismatch');
 const rows=record.report.sources,specs=c.spec.sources,n=specs.length;
 if(![2,3].includes(n)||c.spec.policy!=='coalition-evidence-attribution-v1'||rows.length!==n||record.report.labels.length!==(1<<n)||record.report.labels[0]!=='NEITHER'||
  record.report.labels.some(x=>!['SUPPORT','REFUTE','NEITHER','UNKNOWN'].includes(x)))throw Error('Coverage/schema mismatch');
 let ok=true;
 for(let i=0;i<n;i++){
  const r=rows[i],s=specs[i];if(r.url!==s.url||!Number.isInteger(r.http)||r.http<0||r.http>599||typeof r.body!=='string')throw Error('Source binding/types');
  if(['OK','HASH_MISMATCH'].includes(r.status)){
   if(r.http!==200||Buffer.byteLength(r.body)<1||Buffer.byteLength(r.body)>5000||r.body.includes('\0')||!normalizedText(r.body)||sha(r.body)!==r.hash||sha(normalizedText(r.body))!==r.fingerprint||r.status!==(r.hash===s.sha256?'OK':'HASH_MISMATCH'))throw Error('Source integrity');
  }else if(r.body||r.hash||r.fingerprint||!['UNAVAILABLE','HTTP_ERROR','SIZE_ERROR','ENCODING_ERROR','TEXT_ERROR'].includes(r.status))throw Error('Invalid source failure');
  if(r.status!=='OK')ok=false;
 }
 const acquisition=!ok?'HELD':new Set(rows.map(x=>x.fingerprint)).size!==n?'DUPLICATE':'READY';
 if(record.report.acquisition!==acquisition)throw Error('Acquisition state mismatch');
 const expected=acquisition==='READY'?independentlyAttribute(record.report.labels,n):{status:'HELD',intervals:[],reason:acquisition,document_attribution_only:true};
 if(acquisition!=='READY'&&record.report.labels.slice(1).some(x=>x!=='UNKNOWN'))throw Error('Failed evidence promoted');
 if(canonical(expected)!==canonical(record.output))throw Error('Attribution mismatch');
 if(expected.status==='EXACT'){
  const artifact=await read(address,'exact_attribution',[key,c.input_root]);
  if(canonical(artifact)!==canonical({root,input_root:c.input_root,attribution:expected}))throw Error('Exact consumer mismatch');
 }else{
  let rejected=false;try{await read(address,'exact_attribution',[key,c.input_root]);}catch(e){rejected=e.code===-32000&&e.details==='execution failed';}
  if(!rejected)throw Error('Exact consumer denial unverified');
 }
 return {case:key,input_root:c.input_root,root,verified:true,labels:record.report.labels,acquisition,output:expected};
}
if(process.argv[1]?.endsWith('check.mjs'))try{
 const [mode,value,extra]=process.argv.slice(2);
 const result=mode==='source'?await source(value):mode==='state'?await state(value,extra):
  ['success','error'].includes(mode)?await receipt(value,mode==='error'?'ERROR':'SUCCESS',extra):null;
 if(!result)throw Error('Unknown mode');console.log(JSON.stringify(result));
}catch{console.error('Sanitized verification failure; inspect known hash before retrying');process.exitCode=1;}
