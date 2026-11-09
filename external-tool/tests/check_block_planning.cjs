const assert=require('node:assert/strict'),fs=require('node:fs'),cp=require('node:child_process'),P=require('../dist/workshop-planning'),D=require('../dist/workshop-design'),M=require('../dist/workshop-model'),data=require('../dist/planner-data');
const compact=async body=>JSON.parse(cp.execFileSync('C:/Users/maxbr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['-c','import json,sys,native_compact as c;p=c.proposal(json.load(sys.stdin));c.build_project(p);print(json.dumps(p))'],{encoding:'utf8',stdio:['pipe','pipe','pipe'],input:JSON.stringify({...body.options,outputRate:body.outputs[0].rate})}));
(async()=>{
 const flows={inputs:[{id:'Desc_OreIron_C',rate:60}],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},source={...M.fresh('block67'),name:'60 → 5 · blocs natifs',size:56,design:D.preset('m05-kit',{packs:['concrete','metal','glass']})},before=JSON.stringify(source);
 for(const layoutStyle of ['compact','balanced','spacious'])for(const storeyMode of ['single','auto'])for(const reserveCladding of[false,true]){
  const g=D.generation({layoutStyle,storeyMode,reserveCladding});
  const p=await P.build({source,flows,data,generation:g},{compact});
  assert.equal(p.size,layoutStyle==='compact'?(reserveCladding?48:40):layoutStyle==='balanced'?48:(reserveCladding?64:56));assert.equal(p.nativeProfile,'iron-plates-blocks-flat-v1');assert.equal(p.floors.length,1);assert.equal(p.objects.filter(o=>o.type==='lift').length,13);assert.equal(p.objects.filter(o=>o.recipe).length,8);assert.ok(p.links.filter(l=>l.kind==='belt').every(l=>l.native&&l.rate>0));assert.equal(JSON.stringify(source),before);M.read(p);
  assert.equal(p.objects.filter(o=>o.io?.side==='input').length,1);assert.equal(p.objects.filter(o=>o.io?.side==='output').length,1);
  if(reserveCladding)assert.equal(D.openings(p),0);
  fs.writeFileSync('../../outputs/blocks69-'+layoutStyle+'-'+storeyMode+'-'+reserveCladding+'.factory-blueprint.json',JSON.stringify(p));
  if(storeyMode==='single')await assert.rejects(P.build({source,flows,data,generation:g,dimensions:{size:32,height:32}},{compact}));
  else if(layoutStyle==='compact'){const fixed=await P.build({source,flows,data,generation:{...g,reserveCladding:false},dimensions:{size:32,height:48}},{compact});assert.equal(fixed.size,32);assert.equal(fixed.nativeProfile,'iron-plates-pairs-v1');assert.equal(fixed.floors.length,3);}
 }
 console.log('PASS: Calculator uses complete native blocks, Compact/Normal/Spacious, Bas and Auto choose eight machines on one floor, 5x5 / protected 6x6, actual connections and interfaces, fixed 4x4 rejected atomically.');
})().catch(e=>{console.error(e,e.cause);process.exitCode=1;});
