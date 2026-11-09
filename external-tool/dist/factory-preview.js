'use strict';
// Schematic volumes, saved rotations and the Atelier GPU renderer.
(function(root){
 function dimensions(b){
  if(b.extraction||/^Build_MinerMk/.test(b.type))return [6,14,18];
  const h=Number(/8x(\d+)/.exec(b.type)?.[1])||4;
  if(b.category==='wall')return [.3,8,Math.min(8,h)];
  if(b.category==='foundation')return [8,8,Math.min(4,h)];
  if(b.category==='roof'){const n=Number(/_(\d+)_C$/.exec(b.type)?.[1]);return [8,8,/Corner/.test(b.type)?([0,1,2,4][n]||.4):([0,.4,1,2,4][n]||.4)];}
  if(b.category==='machine')return /Smelter/.test(b.type)?[6,9,9]:/Constructor/.test(b.type)?[8,10,8]:/Assembler/.test(b.type)?[10,15,11]:[5,7,6];
  if(b.category==='storage')return [5,8,5];return [1.5,1.5,1.5];
 }
 function project(p,angle,pitch=Math.atan(.45)){const x=p[0]*Math.cos(angle)-p[1]*Math.sin(angle),y=p[0]*Math.sin(angle)+p[1]*Math.cos(angle);return [x,Math.sin(pitch)*y-Math.cos(pitch)*p[2],Math.cos(pitch)*y+Math.sin(pitch)*p[2]];}
 function layerOf(b){return ['wall','roof','decoration','structure'].includes(b.category)?'habillage':b.category;}
 function diagnosticTint(b,diagnostic){return b.category==='conveyor'?({warning:'#f2ac52',critical:'#ec6464'}[diagnostic?.level]||'#8ca6b2'):null;}
 function vertices(b){
  const [sx,sy,sz]=dimensions(b),wall=b.category==='wall',roof=b.category==='roof',foundation=b.category==='foundation',angular=/Angular/.test(b.type),flipped=/FlipTris/.test(b.type),sloped=/Ramp|Slope|Sloped|Angle|Angular|Tris|Triangle|Corner/i.test(b.type)||(roof&&sz>.4);
  const local=[];for(const z of [0,sz])for(const [x,y]of [[-sx/2,-sy/2],[sx/2,-sy/2],[sx/2,sy/2],[-sx/2,sy/2]]){
   let zz=z,xx=x;
   if(sloped&&wall&&!angular){if(flipped&&z===0)zz=y<0?sz:0;else if(!flipped&&z>0)zz=y<0?0:sz;}
   if(angular&&z>0)xx+=sz/2;
   // Native roof pivots are at the centre of the rise; downhill is local +X.
   if(roof&&sloped){const along=/InCorner/.test(b.type)?Math.min(x,y):/OutCorner/.test(b.type)?Math.max(x,y):x;zz=-along*sz/sx+(z>0?.15:-.15);}
   // Native ramp pivot is centred, downhill along +X (327 saved ramp joins).
   // Inverted ramps keep a flat top and a sloping underside.
   else if(foundation&&sloped)zz=/Inverted/.test(b.type)?(z>0?sz/2:-x*sz/sx):(z>0?-x*sz/sx:-sz/2);
   else if(roof||foundation)zz-=sz/2;
   local.push([xx,y,zz]);
  }
  return local.map(p=>{const scale=b.scale||[1,1,1],v=p.map((n,i)=>n*scale[i]);let rotated;
   if(Array.isArray(b.rotation)&&b.rotation.length===4){const [x,y,z,w]=b.rotation,[vx,vy,vz]=v,t=[2*(y*vz-z*vy),2*(z*vx-x*vz),2*(x*vy-y*vx)];rotated=[vx+w*t[0]+y*t[2]-z*t[1],vy+w*t[1]+z*t[0]-x*t[2],vz+w*t[2]+x*t[1]-y*t[0]];}else{const a=b.yaw||0;rotated=[v[0]*Math.cos(a)-v[1]*Math.sin(a),v[0]*Math.sin(a)+v[1]*Math.cos(a),v[2]];}return rotated.map((n,i)=>n+b.position[i]);});
 }
 function create(host,buildings,options={}){
  buildings=buildings.map(b=>b.extraction||/^Build_MinerMk/.test(b.type)?{...b,category:'extractor'}:b);
  const node=(tag,text)=>{const n=document.createElement(tag);if(text)n.textContent=text;return n;},controls=node('div');controls.className='preview-controls';
  const categories={extractor:'Mineurs reliés',machine:'Machines',conveyor:'Convoyeurs',junction:'Logistique',storage:'Stockages',habillage:'Habillage',foundation:'Sols',other:'Autres'},active=new Set(buildings.map(layerOf)),counts=new Map();for(const b of buildings)counts.set(layerOf(b),(counts.get(layerOf(b))||0)+1);
  const views=node('div');views.className='preview-view-buttons';views.append(node('strong','Perspective'));
  const reset=node('button','⌖');reset.className='button preview-recenter';reset.setAttribute('aria-label','Recentrer la perspective');reset.title='Recentrer';views.append(reset);controls.append(views);
  const layerControls=node('div');layerControls.className='preview-layer-controls';layerControls.setAttribute('role','group');layerControls.setAttribute('aria-label','Calques de la vue 3D');
  for(const [key,text]of Object.entries(categories)){if(!counts.has(key))continue;const label=node('label'),input=node('input');input.type='checkbox';input.checked=true;input.dataset.previewLayer=key;input.onchange=()=>{input.checked?active.add(key):active.delete(key);geometry();schedule();};label.append(input,document.createTextNode(text+' · '+counts.get(key)));layerControls.append(label);}
  const stage=node('div');stage.className='explorer-preview-stage';const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.classList.add('explorer-preview-svg');svg.setAttribute('aria-label','Vue 3D de l’usine');svg.setAttribute('role','img');stage.append(svg);host.append(controls,layerControls,stage,node('p','Couleurs des bâtiments conservées · Convoyeurs : gris bleuté · Blocage : orange / rouge · Glisser : tourner · Molette : zoomer · Maj + glisser ou clic droit : déplacer'));
  const colours={wall:'#cfa487',foundation:'#617e70',roof:'#91aabd',machine:'#c4dc88',storage:'#b2a6cf',junction:'#86bacb',decoration:'#d5b8ce',structure:'#839d91',extractor:'#cab66e',other:'#637369'};
  if(!buildings.length)return {destroy(){},draw(){}};
  const bounds=[0,1,2].map(i=>[Math.min(...buildings.map(b=>b.position[i])),Math.max(...buildings.map(b=>b.position[i]))]),center=bounds.map(([a,b])=>(a+b)/2),unit=Math.max(1,...bounds.map(([a,b])=>(b-a)/100)),norm=p=>p.map((n,i)=>(n-center[i])/unit);
  let fitted=false,baseRadius=86;let yaw=Math.PI/4,pitch=Math.PI/6,zoom=1,pan=[0,0],drag=null,frame=0,disposed=false,key={},faces=[],lines=[];
  function geometry(){faces=[];lines=[];for(const b of buildings){const diagnostic=options.diagnostics?.get(b.id),tint=diagnosticTint(b,diagnostic);if(!active.has(layerOf(b)))continue;if(b.category==='conveyor'){const pts=(b.points?.length?b.points:[b.position]).map(norm);for(const coords of root.TransportGeometry.mesh(pts,.8/unit,.22/unit))faces.push({coords,source:{getAttribute:()=> tint||'#8d969d'}});for(let i=1;i<pts.length;i++)lines.push({coords:[pts[i-1],pts[i]],source:{getAttribute:()=> tint||'#8d969d'}});continue;}const v=vertices(b).map(norm),colour=colours[b.category]||colours.other;for(const indices of [[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7],[0,3,2,1]])faces.push({coords:indices.map(i=>v[i]),source:{getAttribute:()=>colour}});for(const [a,c]of [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]])lines.push({coords:[v[a],v[c]],source:{getAttribute:()=> '#26332d'}});}if(!fitted)baseRadius=faces.flatMap(f=>f.coords).concat(lines.flatMap(l=>l.coords)).reduce((r,p)=>Math.max(r,Math.hypot(...p)*1.18),8);fitted=true;key={};}
  function draw(){frame=0;if(disposed)return;const a=yaw,p=pitch,projectPoint=v=>project(v,a,p),radius=baseRadius/zoom;svg.setAttribute('viewBox',[pan[0]-radius,pan[1]-radius,2*radius,2*radius].join(' '));const view={svg,project:projectPoint,near:[Math.sin(a)*Math.cos(p),Math.cos(a)*Math.cos(p),Math.sin(p)]};if(root.PreviewGPU?.draw(view,key,faces,lines)){svg.replaceChildren();return;}
   const polygons=faces.map(f=>({...f,points:f.coords.map(projectPoint)})).sort((a,b)=>a.points.reduce((n,p)=>n+p[2],0)-b.points.reduce((n,p)=>n+p[2],0));svg.replaceChildren();for(const f of polygons){const poly=document.createElementNS(svg.namespaceURI,'polygon');poly.setAttribute('points',f.points.map(p=>p.slice(0,2).join(',')).join(' '));poly.setAttribute('fill',f.source.getAttribute('fill'));poly.setAttribute('stroke','#23342a');poly.setAttribute('stroke-width','.08');svg.append(poly);}for(const l of lines){const path=document.createElementNS(svg.namespaceURI,'polyline');path.setAttribute('points',l.coords.map(projectPoint).map(p=>p.slice(0,2).join(',')).join(' '));path.setAttribute('stroke',l.source.getAttribute('stroke'));path.setAttribute('stroke-width','.2');svg.append(path);}
  }
  function schedule(){if(!disposed&&!frame)frame=requestAnimationFrame(draw);}
  stage.oncontextmenu=e=>e.preventDefault();stage.onpointerdown=e=>{if(![0,1,2].includes(e.button))return;drag={x:e.clientX,y:e.clientY,pan:e.shiftKey||e.button!==0};stage.setPointerCapture(e.pointerId);};stage.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.x=e.clientX;drag.y=e.clientY;if(drag.pan){const scale=2*baseRadius/zoom/stage.clientHeight;pan[0]-=dx*scale;pan[1]-=dy*scale;}else{yaw-=dx*.008;pitch=Math.max(.06,Math.min(Math.PI/2-.04,pitch+dy*.006));}schedule();};stage.onpointerup=stage.onpointercancel=()=>drag=null;
  stage.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.3,Math.min(12,zoom*Math.exp(-e.deltaY*.0015)));schedule();},{passive:false});reset.onclick=()=>{fitted=false;geometry();yaw=Math.PI/4;pitch=Math.PI/6;zoom=1;pan=[0,0];schedule();};const observer=new ResizeObserver(schedule);observer.observe(stage);geometry();draw();return {draw:schedule,destroy(){disposed=true;cancelAnimationFrame(frame);observer.disconnect();root.PreviewGPU?.hide(svg);}};
 }
 const api={layerOf,dimensions,project,vertices,create,diagnosticTint};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FactoryPreview=api;
})(typeof globalThis!=='undefined'?globalThis:this);
