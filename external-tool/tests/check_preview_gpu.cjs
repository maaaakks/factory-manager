const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const calls=[],uploads=[],gl=new Proxy({canvas:null,isContextLost:()=>false,getShaderParameter:()=>true,getProgramParameter:()=>true,getUniformLocation:(_,k)=>k,getAttribLocation:(_,k)=>k,bufferData:(_,a)=>uploads.push([...a])},{get:(o,k)=>k in o?o[k]:(...args)=>{calls.push([k,...args]);return k;}});
const canvas={style:{},hidden:false,width:0,height:0,setAttribute(){},addEventListener(){},getContext:()=>gl};
const pixel={canvas:{},clearRect(){},fillRect(){},getImageData:()=>({data:[120,180,120,255]})};
const document={documentElement:{dataset:{}},body:{append(){}},createElement:tag=>tag==='span'?{style:{}}:tag==='canvas'?{...canvas,getContext:type=>type==='2d'?pixel:gl}:null};
const context={module:{exports:{}},document,devicePixelRatio:1,getComputedStyle:()=>({color:'#78b478',getPropertyValue:()=> '#202426'}),Float32Array,WeakMap,Map,Math,Number,window:{dispatchEvent(){}}};vm.runInNewContext(fs.readFileSync(require.resolve('../dist/preview-gpu'),'utf8'),context);const GPU=context.module.exports;
const svg={dataset:{},classList:{add(){},remove(){}},parentElement:{append(){},getBoundingClientRect:()=>({left:0,top:0})},getBoundingClientRect:()=>({left:0,top:0,width:400,height:300}),getAttribute:()=>'-10 -10 20 20'};
const view={svg,near:[0,1,0],project:([x,y,z])=>[x,y-z]},key={},source={getAttribute:k=>({'fill':'#78b478','fill-opacity':'.16','stroke':'#78b478','stroke-opacity':'.5'}[k]??null)},faces=[{coords:[[0,0,0],[1,0,0],[1,1,0]],source}],lines=[{coords:[[0,0,0],[1,0,0]],source}];
assert.equal(GPU.draw(view,key,faces,lines,{opaque:false}),true);assert.equal(svg.dataset.renderMode,'transparent');assert.equal(svg.dataset.geometryUploads,'1');assert.ok(Math.abs(uploads[0][6]-.16)<1e-6);assert.ok(Math.abs(uploads[1][6]-.5)<1e-6);
for(let i=0;i<20;i++){view.near=[Math.sin(i),Math.cos(i),0];assert.equal(GPU.draw(view,key,undefined,undefined,{opaque:false}),true);}
assert.equal(svg.dataset.geometryUploads,'1');assert.equal(uploads.length,2,'Camera rotation must not upload geometry');
assert.equal(GPU.draw(view,key,undefined,undefined,{opaque:true}),false,'A mode change needs its own geometry colours');
assert.equal(GPU.draw(view,key,faces,lines,{opaque:true}),true);assert.equal(svg.dataset.renderMode,'opaque');assert.equal(svg.dataset.geometryUploads,'2');assert.equal(uploads[2][6],1);
assert.equal(GPU.draw(view,key,faces,lines,{opaque:false}),true);assert.equal(svg.dataset.geometryUploads,'3');
GPU.hide(svg);assert.equal(svg.dataset.renderer,'svg');
context.document.createElement=()=>({...canvas,remove(){},getContext:()=>null});const fallback={...svg,dataset:{}};assert.equal(GPU.draw({...view,svg:fallback},{},faces,lines,{opaque:false}),false);
console.log('PASS: GPU transparency alpha, camera-only cache, opaque/transparent switching, complete geometry uploads per mode, hide and missing-WebGL fallback.');

// Architectural glazing retains transparency with opaque geometry in the same scene.
context.document.createElement=tag=>tag==='span'?{style:{}}:tag==='canvas'?{...canvas,getContext:type=>type==='2d'?pixel:gl}:null;
const glazedSvg={...svg,dataset:{}},glazedSource={getAttribute:k=>({'fill':'#a8d1cc','fill-opacity':'.28','data-glass':'true'}[k]??null)};
const beforeUploads=uploads.length;
assert.equal(GPU.draw({...view,svg:glazedSvg},{},[{...faces[0],source:glazedSource}],[],{opaque:true}),true);
assert.equal(uploads.length,beforeUploads+3);
assert.equal(uploads[beforeUploads].length,0,'Glass is excluded from the opaque depth-writing pass');
assert(Math.abs(uploads[beforeUploads+2][6]-.28)<1e-6);
console.log('PASS: architectural glass retains alpha in the opaque scene pass');
