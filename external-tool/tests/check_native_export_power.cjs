const assert=require('node:assert/strict'),M=require('../dist/workshop-model.js'),A=require('../dist/workshop-assist.js');
const p=M.fresh('power-export');p.objects=[[10,10],[22,10],[16,21]].map(([x,y],i)=>({id:'c'+i,type:'constructor',name:'Constructeur',x,y,z:0,w:8,d:10,h:6,rotation:0,recipe:'Recipe_IronPlate_C',clock:1}));
const result=A.addPoles(p),poles=result.objects.filter(o=>o.type==='pole');assert.ok(poles.length>=2);
for(const pole of poles)assert.ok(result.links.filter(l=>l.kind==='power'&&(l.from===pole.id||l.to===pole.id)).length<=4);
assert.equal(A.addPoles(result).objects.length,result.objects.length);
console.log('PASS: automatic poles reserve backbone slots and never exceed four native cable connections');
