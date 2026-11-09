const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js'),P=require('../dist/workshop-planning.js'),K=require('../dist/m05-kit.js'),data=require('../dist/planner-data.json');
const rows=[];
for(const size of [32,40,48])for(const seed of [1,2,3,4,5,6]){
 const project={...M.fresh('patterns60'),size,depth:size,height:48,name:'M05 · Petites façades',objects:[{id:'m',type:'constructor',name:'Constructeur',x:size/2,y:size/2,z:25,w:8,d:10,h:6,rotation:0,clock:1,recipe:'Recipe_IronPlate_C'}],links:[],floors:[{z:0,thickness:1,material:'concrete'},{z:24,thickness:1,material:'concrete'}],design:{...D.preset('m05-kit',{packs:['concrete','metal','glass']},seed),fit:'plot',entrance:'none'}};
 project.structure={gap:4,pitch:'minimum',thickness:1,material:'concrete',color:'#536454'};for(const floor of project.floors){floor.color='#536454';floor.shaft=2;}M.read(JSON.stringify(project));
 const before=JSON.stringify(project),bands=D.facadeBands(project),parts=D.envelope(project);
 assert.equal(JSON.stringify(project),before);
 assert.ok(bands.some(b=>b.cells.size<size*size/64),'At least one true setback on a small terrain');
 const accentSides=[0,1,2,3].filter(side=>K.profile(seed,side)>=0);assert.equal(accentSides.length,seed%2?1:2);
 assert.ok(parts.some(q=>q.name==='Terrasse de retrait'));
 assert.ok(parts.some(q=>q.name==='Sous-face du volume saillant'));
 assert.ok(parts.every(q=>q.x>=0&&q.x<=size&&q.y>=0&&q.y<=size&&q.z+q.h<=48));
 for(const band of bands){const cell=Math.floor(size/16)+','+Math.floor(size/16);if(band.top>25&&band.bottom<31)assert.ok(band.cells.has(cell),'Production cell retained');}
 rows.push({project,parts});
}
fs.writeFileSync('../../outputs/patterns60-scenes.json',JSON.stringify(rows));
(async()=>{
 const source=JSON.parse(fs.readFileSync('../../outputs/reflow59-4x4-3.factory-blueprint.json','utf8')),g=D.generation({layoutStyle:'compact',priority:'architecture',storeyMode:'vertical',maxStoreys:3}),before=JSON.stringify(source);
 assert.equal(P.candidates(source.flows,data,g)[0].size,32);
 let calls=0;
 const compact=async body=>{calls++;assert.equal(body.options.size,32);assert.equal(body.options.priority,'production');return JSON.parse(require('node:child_process').execFileSync('C:/Users/maxbr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['-c','import sys,json,native_compact as c;print(json.dumps(c.proposal(json.load(sys.stdin))))'],{input:JSON.stringify({...body.options,outputRate:body.outputs[0].rate,inputItem:body.inputs[0].id}),encoding:'utf8'}));};
 const next=await P.build({id:source.id,source,data,flows:source.flows,generation:g},{compact});
 const bare=await P.build({id:source.id,source:{...source,design:{...source.design,enabled:false}},data,flows:source.flows,generation:{...g,priority:'production'}},{compact});
 assert.equal(calls,2);assert.equal(next.size,32);assert.equal(next.layoutInfo.edgeMargin,0);assert.equal(JSON.stringify(source),before);
 assert.deepEqual(next.objects.map(({id,...o})=>o),bare.objects.map(({id,...o})=>o));assert.deepEqual(next.flows,bare.flows);
 fs.writeFileSync('../../outputs/compact60-4x4.factory-blueprint.json',JSON.stringify(next));
 const copper=await P.build({id:'copper60',source:{...M.fresh('copper60'),design:D.preset('m05-kit',{packs:['concrete','metal','glass']})},data,flows:{inputs:[{id:'Desc_OreCopper_C',rate:60}],outputs:[{id:'Desc_CopperIngot_C',rate:60}]},generation:D.generation({layoutStyle:'compact',storeyMode:'single'})});
 assert.equal(copper.size,32);assert.equal(copper.generation.priority,'production');M.read(JSON.stringify(copper));fs.writeFileSync('../../outputs/compact60-copper.factory-blueprint.json',JSON.stringify(copper));
 console.log('PASS: 18 small M05 silhouettes, one/two accent faces, capped setbacks, protected occupied cells, compact copper and iron start at 4x4, no cladding reservation or production changes.');
})().catch(e=>{console.error(e);process.exitCode=1;});
