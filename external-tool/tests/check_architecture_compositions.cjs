const assert=require('node:assert/strict'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js');
function groups(cells){const remaining=new Set(cells);let n=0;while(remaining.size){n++;const queue=[remaining.values().next().value];remaining.delete(queue[0]);for(const key of queue){const [x,y]=key.split(',').map(Number);for(const [dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const k=(x+dx)+','+(y+dy);if(remaining.delete(k))queue.push(k);}}}return n;}
for(const size of [32,40,48])for(const seed of [1,6,7,13,998,999]){
 for(const [layout,count]of [['central',1],['pair',2],['quartet',4],['triple',3],['band',1],['ring',1]]){
  const pattern=D.roofComposition(size,seed,layout);assert.equal(groups(pattern.cells),count,`${size} / ${seed} / ${layout}`);assert.deepEqual(pattern,D.roofComposition(size,seed,layout));
  const n=size/8,reflectX=pattern.cells.map(k=>{const [x,y]=k.split(',').map(Number);return(n-1-x)+','+y;}).sort(),reflectY=pattern.cells.map(k=>{const [x,y]=k.split(',').map(Number);return x+','+(n-1-y);}).sort();assert.ok(JSON.stringify(reflectX)===JSON.stringify(pattern.cells)||JSON.stringify(reflectY)===JSON.stringify(pattern.cells),'At least one symmetry axis');
 }
}
const scene={...M.fresh('architecture'),size:48,objects:[{id:'c',type:'constructor',name:'Test',x:24,y:24,z:1,w:8,d:10,h:6,rotation:0}],design:D.settings({enabled:true,roof:true,roofStyle:'skylights',roofLayout:'quartet',wallDecoration:'lattice',footprint:'stepped',packs:['concrete','metal','glass']})};
const cells=D.footprint(scene),parts=D.envelope(scene);assert.equal(cells.size,32);assert.equal(D.openings(scene),0,'Recessed corners are an intentional contour, not missing walls');assert.ok(parts.some(p=>p.component==='beam'));assert.equal(parts.filter(p=>p.component==='roof').length,32);assert.ok(parts.some(p=>p.asset==='Roof_Window_01'));
for(const part of parts){const b=M.bounds(part);assert.ok(b.minX>=0&&b.minY>=0&&b.maxX<=48&&b.maxY<=48);assert.ok(part.z>=0&&part.z+part.h<=48);}
const occupied={...scene,objects:[{...scene.objects[0],x:4,y:5}]};assert.ok(D.footprint(occupied).has('0,0'),'Occupied corner cannot be cut');
const gapScene={...scene,size:32,objects:[{...scene.objects[0],x:4,y:10,z:8}],design:{...scene.design,footprint:'rectangle',wallDecoration:'frames'}};
assert.ok(D.openings(gapScene)>0);assert.ok(D.envelope(gapScene).some(p=>p.name.includes('Baie industrielle')),'Mandatory openings receive native beam framing where it fits');
const grown=M.resize({...gapScene,design:D.settings()},48);assert.equal(grown.objects[0].x,12);assert.equal(grown.objects[0].y,18);assert.equal(gapScene.objects[0].x,4,'Resize does not mutate source');
const centered=M.centerPlan({...grown,links:[{kind:'belt',from:'a',to:'b',waypoints:[[4,4,2]],physicalRoute:[{x:4,y:4,z:2}]}]});assert.equal(centered.objects[0].x,24);assert.equal(centered.objects[0].y,24);assert.equal(centered.links[0].waypoints[0][0],16);assert.equal(centered.links[0].physicalRoute[0].y,10);
assert.throws(()=>D.settings({roofLayout:'random-scatter'}),/invalide/);
const shaft={...M.fresh('shaft'),size:32,objects:[{id:'l',type:'lift',name:'Lift',x:1.5,y:12,z:1,w:1,d:1,h:12,rotation:0,recipe:null,clock:1}],floors:[{z:10,thickness:1,material:'concrete',profile:'solid',shaft:2}]};
assert.deepEqual(M.resize(shaft,48).floors[0].holes,[[1,2]],'A lift moved away from the peripheral shaft receives a new floor opening');
console.log('PASS: 108 grouped roof compositions, 1/2/3/4 wells, symmetry, recessed contours, collision-safe bay framing, enlarged margins and translated paths');
