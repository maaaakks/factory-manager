const assert=require('node:assert/strict');
const {flowReport}=require('../dist/factory-metrics.js');
function fixture(){
 const item=(id,rate)=>({id,name:id,rate});
 const buildings=[
  {id:'p',category:'machine',recipe:'produce',rateModel:{supported:true,inputs:[item('ore',360)],outputs:[item('ingot',360),item('wire',340)]}},
  {id:'c',category:'machine',recipe:'consume',rateModel:{supported:true,inputs:[item('ingot',330),item('wire',240)],outputs:[item('product',100)]}},
  {id:'split',category:'junction',passThrough:true},
  {id:'storage',category:'storage'},
  {id:'after',category:'storage'}
 ];
 const ports=[];buildings.forEach(b=>b.ports=[]);
 const link=(from,to)=>{const a={id:'out'+ports.length,owner:from,direction:'out',state:'connected',peerOwner:to},b={id:'in'+ports.length,owner:to,direction:'in',state:'connected',peerOwner:from};a.peer=b.id;b.peer=a.id;ports.push(a,b);buildings.find(b=>b.id===from).ports.push(a.id);buildings.find(b=>b.id===to).ports.push(b.id);};
 link('p','split');link('split','c');link('split','storage');link('c','storage');link('storage','after');
 return {buildings,ports};
}
let {buildings,ports}=fixture();
let report=flowReport(buildings.slice(0,2),buildings,ports);
const find=id=>report.items.find(i=>i.id===id);
assert.equal(find('wire').consumed,240);
assert.equal(find('wire').stored,100);
assert.equal(find('wire').use,100);
assert.equal(find('ingot').stored,30);
assert.equal(find('ingot').coverage,100);
assert.equal(find('product').stored,100);
assert.deepEqual(find('product').storageIds,['storage'],'Must stop at first chest');
assert.equal(find('ore').use,null,'External supply is unknown');
// A geometric surplus without a chest is not an output.
({buildings,ports}=fixture());
ports=ports.filter(p=>p.peerOwner!=='storage'&&p.owner!=='storage'&&p.peerOwner!=='after');
buildings.forEach(b=>b.ports=b.ports.filter(id=>ports.some(p=>p.id===id)));
report=flowReport(buildings.slice(0,2),buildings,ports);
assert.equal(find('wire').stored,0);
assert.equal(find('wire').unassigned,100);
assert.equal(find('product').stored,0);
assert.equal(find('product').use,0);
// Producers with no route to the consumer must not count as internal supply.
({buildings,ports}=fixture());
ports=ports.filter(p=>p.owner!=='split'&&p.peerOwner!=='split');
buildings.forEach(b=>b.ports=b.ports.filter(id=>ports.some(p=>p.id===id)));
report=flowReport(buildings.slice(0,2),buildings,ports);
assert.equal(find('ingot').coverage,0);
console.log('PASS: internal demand priority, export regression, first chest boundary, external uncertainty, no chest and disconnected producers');
