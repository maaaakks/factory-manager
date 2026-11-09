const fs=require('fs'),path=require('path'),assert=require('assert/strict'),S=path.resolve(process.argv[2]||path.join(__dirname,'..')),F=require(path.join(S,'dist/creation-fitting')),D=require(path.join(S,'dist/workshop-design')),M=require(path.join(S,'dist/workshop-model'));
const source=require(path.join(S,'tests/fixtures/living-calibrated.json')),initial=F.apply(source,'compact',['concrete','metal','glass']),recipes=p=>p.objects.filter(o=>o.recipe).map(o=>[o.id,o.recipe,o.clock]),belts=p=>p.links.filter(l=>l.kind!=='power');let p=initial;
for(let i=0;i<5;i++){
 const bare=F.detach(p);assert.equal(bare.floors.length,0);assert(!bare.design.living);assert.equal(bare.objects.filter(o=>o.type==='wallPole').length,source.objects.filter(o=>o.type==='wallPole').length);assert.deepEqual(bare.links.filter(l=>l.kind==='power'),initial.design.living.powerOriginal.links);
 p=F.apply(bare,'compact',['concrete','metal','glass']);assert.equal(p.size,initial.size);assert.equal(p.objects.length,initial.objects.length);assert.deepEqual(recipes(p),recipes(source));assert.deepEqual(belts(p),belts(initial));M.read(p);
}
for(const size of[48,64,80,96]){const C=require(path.join(S,'dist/design-campus')),parts=D.envelope(C.project('compact',size,size));for(const z of[1,5,9,13])assert(parts.some(q=>q.x===size-20&&q.y===size-8&&q.z===z&&['wall','window'].includes(q.component)),'Rear bay must be closed');assert.equal(parts.filter(q=>q.asset==='Wall_Door_8x4_01'&&!q.compactAssembly).length,1);}
const v=p.design.living,n=(p.size-32)/8;assert.equal(v.accessParts.filter(q=>q.asset==='Wall_Window_Thin_8x4_01').length,n);assert(!v.accessParts.some(q=>q.asset==='Railing_01'||q.asset==='Wall_Window_Thin_8x4_02'));
assert.equal(v.levels[0].missing.length,0);
const broken=[];
for(const kind of['floating-glass','missing-slab','door-beam']){
 const bad=structuredClone(p),items=bad.design.living.accessParts;
 if(kind==='floating-glass')items.find(q=>q.asset==='Wall_Window_Thin_8x4_01').x+=4;
 if(kind==='missing-slab')items.splice(items.findIndex(q=>q.asset==='Foundation_ConcretePolished_8x1'),1);
 if(kind==='door-beam')items.push({name:'Bad beam across door',asset:'Beam_Painted',component:'beam',x:12,y:12,z:3.5,w:8,d:.3,h:.3,rotation:0,color:'#ffffff',start:[10,12,4],end:[14,12,4],beamRadius:.5,compactAssembly:'ceiling-electric'});
 assert.throws(()=>D.envelope(bad),/Compact/);broken.push(bad);
}
fs.writeFileSync(path.join(process.argv[3]||__dirname,'broken.json'),JSON.stringify(broken));
console.log('PASS 5 stable cycles, original electricity restored on removal, belts/recipes preserved; floating glass, missing support and blocked doorway refused. Gallery bays:',n);

const atlas=F.apply(initial,'atlas',['concrete','metal','glass']);assert.equal(atlas.objects.length,source.objects.filter(o=>o.type!=='storage').length);assert(!atlas.objects.some(o=>o.native?.ceilingMounted));console.log('PASS changing away from Compact restores the original electrical layout before fitting.');
