const assert=require('node:assert/strict'),R=require('../dist/m05-roof');
for(const size of [32,40,48])for(let seed=1;seed<=8;seed++){
 const p={size,depth:size,height:48,objects:[],design:{roof:true,roofSeed:seed}},wall={name:'Façade conservée',component:'wall',x:0,y:0,z:0},parts=[wall];
 for(let x=4;x<size;x+=8)for(let y=4;y<size;y+=8)parts.push({name:'Verrière à ossature',component:'roof',asset:'Roof_Window_01',x,y,z:24,w:8,d:8,h:.5});
 const before=JSON.stringify(parts),result=R.apply(parts,p),details=result.filter(q=>q.roofDetail),roof=details.filter(q=>q.component==='module'&&q.asset.startsWith('Roof_'));
 assert.equal(JSON.stringify(parts),before);assert.strictEqual(result[0],wall);assert.deepEqual(R.apply(parts,p),result);
 assert.ok(roof.length>=2,'Composition must use several central bays, including existing glass cells');
 const bounds=[0,1].map(i=>[Math.min(...details.map(q=>q.signatureBounds[i][0])),Math.max(...details.map(q=>q.signatureBounds[i][1]))]);
 for(const b of bounds)assert.ok(Math.abs((b[0]+b[1])/2-size/2)<=4.3,'Composition remains central');
 assert.ok(details.every(q=>q.signatureBounds.every((b,i)=>b[0]>.009&&b[1]<[size,size,48][i]-.009)));
 const blocked={...p,objects:[{x:size/2,y:size/2,z:24,w:size,d:size,h:20,rotation:0}]};assert.equal(R.apply(parts,blocked).filter(q=>q.roofDetail).length,0);
 assert.deepEqual(R.apply(parts,{...p,design:{...p.design,roof:false}}),parts);
}
console.log('PASS: 24 roof compositions; repeated central bays, glazed supports, unchanged walls, deterministic generation and collision refusal.');
