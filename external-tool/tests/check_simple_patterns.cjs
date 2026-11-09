const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(process.argv[2]),data=require(path.join(root,'dist/planner-data')),Patterns=require(path.join(root,'dist/workshop-patterns')),M=require(path.join(root,'dist/workshop-model')),P=require(path.join(root,'dist/workshop-planning'));
for(const type of Object.keys(Patterns.types)){
 const recipe=Patterns.types[type].recipe,p=Patterns.payload(data,type,recipe,4);assert.equal(p.options.layoutPolicy,'simple-patterns-v1');
 for(const invalid of [0,1.5,17,NaN])assert.throws(()=>Patterns.payload(data,type,recipe,invalid));
}
assert.throws(()=>Patterns.payload(data,'assembler','Recipe_IngotIron_C',4));
const rows=JSON.parse(fs.readFileSync(process.argv[3]));for(const row of rows)M.read(row.project);
(async()=>{for(const style of ['compact','balanced','spacious']){let calls=0;const sample=rows.find(r=>r.type==='smelter'&&r.count===4).project;const next=await P.build({id:'patterns-check',flows:sample.flows,data,generation:{layoutStyle:style,storeyMode:'auto',shape:'rectangle',reserveCladding:false}},{compact:()=>{throw Error('Legacy blueprint must never be used');},manifold:async body=>{calls++;assert.equal(body.options.layoutPolicy,'simple-patterns-v1');return M.clone(sample);}});assert(calls>0);assert.equal(next.generation.storeyMode,'single');M.read(next);}console.log('PASS: readable native patterns, payload validation and all densities route through individual machines');})().catch(e=>{console.error(e);process.exitCode=1;});
