'use strict';
(function(root){
 const node=typeof module!=='undefined'&&module.exports,clone=v=>JSON.parse(JSON.stringify(v));
 const catalog=()=>node?require('./architecture-catalog'):root.ArchitectureCatalog;
 function assembly(spec,p){const key=[p.size,p.depth??p.size,p.design.campusLevels??3].join('x'),a=spec.grammar.assemblies[key];if(!a)throw new Error('Noyau : largeurs 64 ou 96 m, longueurs 48 / 64 / 80 m et 1 à 3 niveaux.');return a;}
 function parts(spec,p){
  const a=assembly(spec,p),out=[],seen=new Set();
  for(const inst of a.instances)for(const source of spec.grammar.prefabs[inst.prefab]){
   const q=clone(source);for(let i=0;i<3;i++)q[['x','y','z'][i]]+=inst.at[i];q.name=inst.prefix+' · '+q.name;q.color=spec.floorPalette?q.color:spec.grammar.palettes[spec.interiorStyles?Math.max(0,spec.interiorStyles.indexOf(p.design.interiorStyle||'creuset')):inst.phase][q.colorSlot||'wall'];if(q.ledPanel){const color=p.design.ledColor||spec.ledColor;if(!/^#[0-9a-f]{6}$/i.test(color))throw new Error('Couleur LED invalide.');q.color=color;}q.campusLevel=inst.level;q.campusRole=inst.prefab;
   if(q.signatureBounds)q.signatureBounds=q.signatureBounds.map((r,i)=>r.map(v=>v+inst.at[i]));
   for(const key of ['walkStart','walkEnd'])if(q[key])q[key]=q[key].map((v,i)=>v+inst.at[i]);
   const key=[q.asset,...['x','y','z'].map(k=>Math.round(q[k]*1e5)/1e5),q.asset.startsWith('Wall_')?q.rotation%180:q.rotation].join('|')+(spec.squareModule&&q.quat?'|'+q.quat.join(','):'');if(!seen.has(key)){seen.add(key);out.push(q);}
  }
  return out;
 }
 function project(family='noyau',width,depth,levels){
  const C=catalog(),spec=C.studies[family];if(!spec?.designFirst)throw new Error('Étude architecturale inconnue.');
  width=width??spec.dimensions[0];depth=depth??spec.dimensions[1];
  const D=node?require('./workshop-design'):root.WorkshopDesign;
  const p={schemaVersion:2,kind:'factory-tools-paper-blueprint',id:family+'-architecture',name:spec.title,size:width,depth,height:32,objects:[],links:[],buffer:[],flows:{inputs:[],outputs:[]},structure:{gap:4,pitch:16,thickness:1,material:'concrete',color:'#53666b'},floors:[{z:0,thickness:1,material:'concrete',color:'#a8b8b8',shaft:2,profile:'solid'}],design:D.preset(family,{packs:['concrete','metal','glass']})};
  if(spec.sourceArchitecture){p.floors=[];p.design.studyFitted=true;p.design.studyFloors=[];}
  if(spec.ledColor)p.design.ledColor=spec.ledColor;
  if(spec.grammar){levels=levels??spec.defaultLevels??3;p.height=spec.dimensions[2];p.design.campusLevels=levels;if(spec.interiorStyles)p.design.interiorStyle='creuset';const a=assembly(spec,p);p.height=a.height;p.floors=clone(a.floors);p.design.studyFitted=true;p.design.studyFloors=clone(a.studyFloors);}
  return family==='compact'?(node?require('./creation-living'):root.CreationLiving).plan(p):p;
 }
 function floorColor(p,f,x,y,fallback){
  const spec=catalog().studies[p.design?.family];if(!spec?.designFirst)return fallback;
  if(spec.floorPalette){const pal=spec.floorPalette,cx=p.size/2,plan=spec.floorPlan;const lane=plan==='creuset'?Math.abs(x-cx)<8:plan==='atelier'?Math.abs(x-cx)<8:plan==='horizon'?(Math.abs(x-cx)>8||y<16||y>(p.depth??48)-20):false;return lane?pal.lane:pal.floor;}
  let color=fallback;if(p.design.family==='noyau'&&f.z>0)color=spec.grammar.palettes[Math.max(0,spec.interiorStyles.indexOf(p.design.interiorStyle||'creuset'))].floor;if(p.design.family==='noyau'&&f.z>0&&Math.abs(x-p.size/2)<8.1){const phase=Math.max(0,Math.min(2,catalog().studies.noyau.interiorStyles.indexOf(p.design.interiorStyle||'creuset')));color=catalog().studies.noyau.grammar.palettes[phase].frame;}
  if(!color||!/^#[0-9a-f]{6}$/i.test(color))return fallback;
  const factor=(Math.floor(x/8)+Math.floor(y/8))%2?.94:1;return '#'+color.slice(1).match(/../g).map(v=>Math.round(parseInt(v,16)*factor).toString(16).padStart(2,'0')).join('');
 }
 const api={floorColor,assembly,parts,project};if(node)module.exports=api;else root.DesignCampus=api;
})(typeof globalThis!=='undefined'?globalThis:this);
