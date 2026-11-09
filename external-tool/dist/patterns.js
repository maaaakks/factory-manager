'use strict';
(()=>{
 const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';let references=[],current=null;
 function node(tag,attrs,parent,text){const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;}
 function rotate(q,v){const [x,y,z,w]=q,[a,b,c]=v;return [(1-2*y*y-2*z*z)*a+(2*x*y-2*z*w)*b+(2*x*z+2*y*w)*c,(2*x*y+2*z*w)*a+(1-2*x*x-2*z*z)*b+(2*y*z-2*x*w)*c,(2*x*z-2*y*w)*a+(2*y*z+2*x*w)*b+(1-2*x*x-2*y*y)*c];}
 function world(a,p){const v=rotate(a.rotation,p);return v.map((v,i)=>v+a.position[i]);}
 function machine(a){return /Build_(Smelter|Constructor|Assembler)Mk/.test(a.type);}
 function project(p,plane){return plane==='XY'?[p[0],p[1]]:plane==='YZ'?[p[1],-p[2]]:[p[0],-p[2]];}
 function range(){if($('level').value==='all')return [-Infinity,Infinity];const z=Number($('level').value),levels=[...new Set(current.actors.filter(machine).map(a=>a.position[2]))].sort((a,b)=>a-b);return [z,levels.find(v=>v>z+.01)??Infinity];}
 function cut(a,b){const [low,high]=range(),dz=b[2]-a[2];if(Math.abs(dz)<1e-6)return a[2]>=low-.01&&a[2]<high-.01?[a,b]:null;let t0=(low-a[2])/dz,t1=(high-a[2])/dz;if(t0>t1)[t0,t1]=[t1,t0];t0=Math.max(0,t0);t1=Math.min(1,t1);return t0<=t1?[a.map((v,i)=>v+t0*(b[i]-v)),a.map((v,i)=>v+t1*(b[i]-v))]:null;}
 function draw(svg,plane){svg.replaceChildren();const extents=[];const all=current.actors,by=new Map(all.map(a=>[a.id,a]));
  function line(a,b,color,width=.12,dash=null){const segment=cut(a,b);if(!segment)return;const p=project(segment[0],plane),q=project(segment[1],plane);extents.push(p,q);node('path',{d:`M${p.join(' ')} L${q.join(' ')}`,fill:'none',stroke:color,'stroke-width':width,...(dash?{'stroke-dasharray':dash}:{})},svg);}
  function box(a,x,y,z,w,d,h,color,opacity=.12){if(a.position[2]+z<range()[0]-.01||a.position[2]+z>=range()[1]-.01)return;
   const points=[];for(const dx of [-w/2,w/2])for(const dy of [-d/2,d/2])for(const dz of [0,h])points.push(project(world(a,[x+dx,y+dy,z+dz]),plane));extents.push(...points);const min=points[0].map((v,i)=>Math.min(...points.map(p=>p[i]))),max=points[0].map((v,i)=>Math.max(...points.map(p=>p[i])));const n=node('rect',{x:min[0],y:min[1],width:Math.max(.1,max[0]-min[0]),height:Math.max(.1,max[1]-min[1]),fill:color,'fill-opacity':opacity,stroke:color,'stroke-width':.07},svg);node('title',{},n,a.type+' · X '+a.position[0]+' · Y '+a.position[1]+' · Z '+a.position[2]+' m');
  }
  if($('structure').checked)for(const a of all)if(/Foundation|Flat_Frame/.test(a.type))box(a,0,0,-.4,8,8,.8,'#92a695',.05);
  for(const a of all){
   if(a.type.includes('SmelterMk')){box(a,0,0,0,5,10,4.5,'#b9d58e');box(a,0,1.45,4.5,5,7.1,4,'#b9d58e',.07);}
   else if(a.type.includes('ConstructorMk')){box(a,0,0,0,8,10,6,'#91bdad');line(world(a,[-1.65,-4.65,6]),world(a,[-1.65,-4.65,8.5]),'#91bdad',.08);line(world(a,[2.1,-4.65,6]),world(a,[2.1,-4.65,7.3]),'#91bdad',.08);}
   else if(a.type.includes('AssemblerMk')){box(a,0,-.5,0,9,17,3,'#8cb3ce');box(a,0,.75,3,9,5.5,5,'#8cb3ce',.06);line(world(a,[1.75,-.6,8]),world(a,[1.75,-.6,10.75]),'#8cb3ce',.08);}
  }
  for(const a of all)if(a.path){const connected=a.ports.map(p=>by.get(p.connected.split('.').slice(0,-1).join('.'))).filter(Boolean),color=connected.some(o=>o.type.includes('Merger'))?'#f5b46b':'#69c9d7';for(let i=1;i<a.path.length;i++)line(a.path[i-1],a.path[i],color,.14);}
  for(const a of all)if(a.top)line(a.position,a.top,'#c3a1eb',.21);
  for(const a of all)if(a.type.includes('Attachment'))box(a,0,0,-.6,2,2,1.2,a.type.includes('Splitter')?'#69c9d7':'#f5b46b',.36);
  for(const a of all){if(a.position[2]<range()[0]-.01||a.position[2]>=range()[1]-.01)continue;
   if(machine(a)){const p=project(world(a,[0,0,plane==='XY'?0:2]),plane);node('text',{x:p[0],y:p[1],'font-size':.72,'text-anchor':'middle','dominant-baseline':'middle'},svg,a.type.includes('Smelter')?'F':a.type.includes('Constructor')?'C':'A');}
   if($('electric').checked&&a.type.includes('PowerPole')){const p=project(a.position,plane);extents.push(p);const c=node('circle',{cx:p[0],cy:p[1],r:.23,fill:'#e6ce96'},svg);node('title',{},c,a.type+' · Z '+a.position[2]+' m');if(!a.type.includes('Wall'))line(a.position,[a.position[0],a.position[1],a.position[2]+7],'#e6ce96',.1);}
   if($('electric').checked&&a.endpoints){const owners=a.endpoints.map(id=>by.get(id.split('.').slice(0,-1).join('.')));if(owners.length===2&&owners.every(Boolean))line(owners[0].position,owners[1].position,'#e6ce9677',.06,'.2 .25');}
  }
  if(!extents.length)return;
  const min=[0,1].map(i=>Math.min(...extents.map(p=>p[i]))-1.5),max=[0,1].map(i=>Math.max(...extents.map(p=>p[i]))+1.5);
  if(plane!=='XY'){
   const heights=current.id==='rotors'?[...new Set(all.filter(machine).map(a=>a.position[2]))]:[0,...current.pairs.flatMap(p=>[p.feedZ,p.outputZ])];
   for(const z of [...new Set(heights)])if(z>=range()[0]-.01&&z<range()[1]-.01){node('path',{d:`M${min[0]} ${-z} H${max[0]}`,stroke:'#9cac9c55','stroke-width':.04,'stroke-dasharray':'.2 .3'},svg);node('text',{x:min[0]+.05,y:-z-.2,'font-size':.5},svg,'Z '+z+' m');}
  }
  svg.setAttribute('viewBox',`${min.join(' ')} ${max[0]-min[0]} ${max[1]-min[1]}`);
 }
 function render(){if(!current)return;draw($('top'),'XY');draw($('side'),$('section').value);$('title').textContent=current.name;const m=current.metrics;$('stats').textContent=`${m.machineCount} machines · ${m.liftCount} élévateurs · ${m.wallConnectors} raccord${m.wallConnectors>1?'s muraux':' mural'} · ${m.floorPoles} poteaux`;$('notes').replaceChildren();for(const note of current.notes){const li=document.createElement('li');li.textContent=note;$('notes').append(li);}$('source').textContent='Source locale : blueprints / kouyère / '+current.name+'.sbp · SHA-256 '+current.sha256;}
 function select(){current=references.find(r=>r.id===$('reference').value);const levels=[...new Set(current.actors.filter(machine).map(a=>a.position[2]))].sort((a,b)=>a-b);$('level').replaceChildren();for(const [value,label]of [['all','Tous les niveaux'],...levels.map(z=>[String(z),'Machines à Z = '+z+' m'])]){const o=document.createElement('option');o.value=value;o.textContent=label;$('level').append(o);}$('section').value=current.id==='rotors'?'XZ':'YZ';render();}
 fetch('/compact-patterns.json').then(r=>{if(!r.ok)throw new Error('Références indisponibles.');return r.json();}).then(data=>{references=data;const initial=new URLSearchParams(location.search).get('ref');if(data.some(r=>r.id===initial))$('reference').value=initial;select();}).catch(e=>$('error').textContent=e.message);
 $('reference').onchange=select;for(const id of ['level','section','electric','structure'])$(id).onchange=render;
})();
