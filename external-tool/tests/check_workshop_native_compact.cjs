const assert=require('node:assert/strict'),M=require('../dist/workshop-model.js'),A=require('../dist/workshop-assist.js');
const p=M.read(require('./fixtures/compact-iron-plates.json'));
assert.equal(M.problems(p).length,0);assert.deepEqual(M.read(JSON.stringify(p)),p);
assert.equal(p.objects.filter(o=>['smelter','constructor','assembler'].includes(o.type)).length,16);
assert.equal(p.objects.filter(o=>o.type==='wallPole').length,7);
assert.equal(p.objects.filter(o=>o.type==='lift').length,21);
assert.ok(p.links.every(l=>l.kind!=='planned'));
const old=JSON.stringify(p),paths=p.links.filter(l=>l.native&&!l.native.snap);
for(const l of paths){const points=A.physicalPath(p,l);assert.ok(points.length>=25);assert.ok(points.every(pt=>['x','y','z'].every(k=>Number.isFinite(pt[k]))));assert.ok(points.every(pt=>pt.x>=0&&pt.x<=32&&pt.y>=0&&pt.y<=32&&pt.z>=0&&pt.z<=32));assert.equal(points,A.physicalPath(p,l));}
assert.equal(JSON.stringify(p),old);
const shifted=M.clone(p);for(const o of shifted.objects){o.x+=4;o.y+=4;}shifted.size=40;
for(const l of shifted.links.filter(l=>l.native&&!l.native.snap)){const source=p.links.find(x=>x.from===l.from&&x.to===l.to);const before=A.physicalPath(p,source)[0],after=A.physicalPath(shifted,l)[0];assert.ok(Math.abs(after.x-before.x-4)<1e-6);assert.ok(Math.abs(after.y-before.y-4)<1e-6);}
for(const mutate of [o=>o.native.quaternion=[0],o=>o.native.prototype=-1,o=>o.native.ports={Input0:[NaN,0,0]}]){const broken=M.clone(p);mutate(broken.objects[0]);assert.throws(()=>M.read(broken));}
const broken=M.clone(p);broken.links.find(l=>l.native&&!l.native.snap).native.spans=[[[0,0,0]]];assert.throws(()=>M.read(broken));
console.log('PASS: calibrated scene JSON persistence, physical routes at all levels, route caching, translations, 7 wall connectors, 21 real lifts, malformed geometry rejection and no render-time mutation');
