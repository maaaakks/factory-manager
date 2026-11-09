'use strict';
const $ = id => document.getElementById(id);
const canvas = $('canvas'), ctx = canvas.getContext('2d');
const categories = { machine: ['Machines', '#d3ee88'], conveyor: ['Convoyeurs & ascenseurs', '#e3a779'], junction: ['Répartiteurs & fusions', '#86bacb'], storage: ['Stockage', '#b2a6cf'], wall: ['Murs & fenêtres', '#cfa487'], foundation: ['Fondations & rampes', '#738c82'], roof: ['Toitures', '#91aabd'], decoration: ['Décoration, éclairage & panneaux', '#d5b8ce'], structure: ['Poutres, passerelles & escaliers', '#839d91'], other: ['Autres constructions', '#637369'] };
const active = new Set(['machine','conveyor','junction','storage']);
let saveChoices=new Map(),currentSaveRef=null,viewTimer=null;
let world = null, byId = new Map(), ports = new Map(), selected = null, trace = null;
let factoryTransportCache=new Map(),factoryDiagnostic=null;
let factory = null, regionMode = false, savedFactories = [], densityZones = [];
// Same game coordinates in metres for both the raster and every object overlay.
const terrainBounds = {minX:-3246.98832031,maxX:4253.01832031,minY:-3750,maxY:3750};
const terrainImage = new Image();
let terrainReady = false;
terrainImage.onload = () => {terrainReady=true;draw();};
terrainImage.onerror = () => {terrainReady=false;if($('background').value==='terrain'){status('Fond de carte indisponible. La grille reste utilisable.',true);draw();}};
terrainImage.src='/assets/world-map.jpg';
try {const saved=localStorage.getItem('factoryTools.background');if(saved==='terrain')$('background').value='terrain';}catch{}

let width=600, height=500, cx=0, cy=0, zoom=1, visible=[], dragging=null, pending=false;
const fmt = n => new Intl.NumberFormat(FactoryI18n.locale,{maximumFractionDigits:1}).format(n);
function status(text,error=false){$('status').textContent=text;$('status').classList.toggle('error',error);}
function elem(tag,text,className){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;}
function screen(p){return [(p[0]-cx)*zoom+width/2,(p[1]-cy)*zoom+height/2];}
function visibleNow(){visible=world?world.buildings.filter(b=>active.has(b.category)):[];}
function fit(){visibleNow();const pts=visible.flatMap(b=>b.points.length?b.points:[b.position]);if(!pts.length){cx=cy=0;zoom=1;draw();return;}
let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(const p of pts){minX=Math.min(minX,p[0]);maxX=Math.max(maxX,p[0]);minY=Math.min(minY,p[1]);maxY=Math.max(maxY,p[1]);}cx=(minX+maxX)/2;cy=(minY+maxY)/2;zoom=Math.min((width-90)/Math.max(40,maxX-minX),(height-90)/Math.max(40,maxY-minY));draw();}
function updateLayers(){const holder=$('layers');holder.replaceChildren();const skin=['wall','roof','decoration','structure'];for(const [key,[label,color]]of Object.entries(categories)){if(skin.includes(key)&&key!=='wall')continue;const keys=key==='wall'?skin:[key],line=elem('label',undefined,'layer'),input=elem('input');input.type='checkbox';input.checked=keys.some(k=>active.has(k));input.indeterminate=input.checked&&!keys.every(k=>active.has(k));input.dataset.layer=key==='wall'?'habillage':key;input.addEventListener('change',()=>{for(const k of keys)input.checked?active.add(k):active.delete(k);visibleNow();draw();});const dot=elem('span',undefined,'dot');dot.style.backgroundColor=color;line.append(input,dot,elem('span',key==='wall'?'Habillage':label),elem('span',world?fmt(keys.reduce((n,k)=>n+(world.counts[k]||0),0)):'—','count'));holder.append(line);}}

function draw(){ctx.clearRect(0,0,width,height);ctx.fillStyle='#111915';ctx.fillRect(0,0,width,height);
 if($('background').value==='terrain' && terrainReady){
  const topLeft=screen([terrainBounds.minX,terrainBounds.minY]);
  ctx.drawImage(terrainImage,topLeft[0],topLeft[1],(terrainBounds.maxX-terrainBounds.minX)*zoom,(terrainBounds.maxY-terrainBounds.minY)*zoom);
  ctx.fillStyle='#07130b33';ctx.fillRect(0,0,width,height);
 }
 const step=Math.pow(10,Math.floor(Math.log10(70/zoom))),grid=step*zoom;ctx.strokeStyle=$('background').value==='terrain'?'#10201822':'#213027';ctx.lineWidth=1;ctx.beginPath();for(let x=((width/2-cx*zoom)%grid+grid)%grid;x<width;x+=grid){ctx.moveTo(x,0);ctx.lineTo(x,height);}for(let y=((height/2-cy*zoom)%grid+grid)%grid;y<height;y+=grid){ctx.moveTo(0,y);ctx.lineTo(width,y);}ctx.stroke();
 const members=trace?.members||factory?.members||new Set();
 for(const b of visible){if(b.category!=='conveyor')continue;const selectedB=b.id===selected,highlight=selectedB||members.has(b.id);ctx.strokeStyle=selectedB?'#efffd3':diagnosticColour(b.id)||(highlight?'#e2f1a8':categories.conveyor[1]);ctx.globalAlpha=((trace || factory) && !highlight) ? .22 : .7;ctx.lineWidth=highlight?4:Math.max(1.3,Math.min(3,zoom*.9));ctx.beginPath();const pts=b.points.length?b.points:[b.position];pts.forEach((p,i)=>{const[x,y]=screen(p);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();if(pts.length<2||Math.hypot(...screen(pts[0]).map((v,i)=>v-screen(pts.at(-1))[i]))<3){const[x,y]=screen(b.position);ctx.strokeRect(x-2,y-2,4,4);}}
 ctx.globalAlpha=1;
 for(const b of [...visible].sort((a,b)=>drawPriority(a)-drawPriority(b))){if(b.category==='conveyor')continue;const[x,y]=screen(b.position);if(x< -20||y< -20||x>width+20||y>height+20)continue;const hi=b.id===selected||members.has(b.id),r=Math.max(2.5,Math.min(8,zoom*2.5));ctx.save();ctx.translate(x,y);ctx.rotate(b.yaw);ctx.globalAlpha=((trace || factory) && !hi) ? .2 : .9;ctx.fillStyle=diagnosticColour(b.id)||(hi?'#e6f3b6':categories[b.category][1]);if(b.category==='wall'){const length=Math.max(3,8*zoom);ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,-length/2);ctx.lineTo(0,length/2);ctx.stroke();if(zoom>=1){ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.max(3,Math.min(10,zoom)),0);ctx.stroke();}}else if(['foundation','roof'].includes(b.category)){const size=Math.max(3,8*zoom);ctx.globalAlpha*=.45;ctx.fillRect(-size/2,-size/2,size,size);ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=.6;ctx.strokeRect(-size/2,-size/2,size,size);}else{ctx.fillRect(-r,-r,r*2,r*2);ctx.strokeStyle='#122017';ctx.lineWidth=1;ctx.strokeRect(-r,-r,r*2,r*2);}ctx.restore();}
 if(selected&&byId.has(selected)){const[x,y]=screen(byId.get(selected).position);ctx.strokeStyle='#f0ffd4';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(x,y,13,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(x-19,y);ctx.lineTo(x-15,y);ctx.moveTo(x+15,y);ctx.lineTo(x+19,y);ctx.moveTo(x,y-19);ctx.lineTo(x,y-15);ctx.moveTo(x,y+15);ctx.lineTo(x,y+19);ctx.stroke();}
 if (regionMode && dragging?.region) {
   const x=Math.min(dragging.x,dragging.ex),y=Math.min(dragging.y,dragging.ey);
   ctx.fillStyle='#d3ee881c';ctx.strokeStyle='#d3ee88';ctx.lineWidth=1.5;ctx.setLineDash([6,4]);ctx.fillRect(x,y,Math.abs(dragging.ex-dragging.x),Math.abs(dragging.ey-dragging.y));ctx.strokeRect(x,y,Math.abs(dragging.ex-dragging.x),Math.abs(dragging.ey-dragging.y));ctx.setLineDash([]);
 } else if(factory) {
   const a=screen([factory.rect.minX,factory.rect.minY]),b=screen([factory.rect.maxX,factory.rect.maxY]);ctx.strokeStyle='#d3ee8880';ctx.lineWidth=1;ctx.setLineDash([6,4]);ctx.strokeRect(a[0],a[1],b[0]-a[0],b[1]-a[1]);ctx.setLineDash([]);
 }
 renderZoneLabels();
 const meters=step; $('scale').textContent=fmt(meters)+' m';$('scale').style.width=Math.max(30,grid)+'px';persistView();
}
function zoomAt(factor,x=width/2,y=height/2){const old=zoom;zoom=Math.max(.015,Math.min(40,zoom*factor));cx+=(x-width/2)*(1/old-1/zoom);cy+=(y-height/2)*(1/old-1/zoom);draw();}
function segmentDistance(x,y,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy||1)));return Math.hypot(x-a[0]-t*dx,y-a[1]-t*dy);}
function hit(x,y){let best=null,dist=13;for(const b of visible){let d=Math.hypot(x-screen(b.position)[0],y-screen(b.position)[1]);if(b.category==='wall'){const ends=FactoryMetrics.wallEnds(b);d=segmentDistance(x,y,screen(ends[0]),screen(ends[1]));}else if(b.points.length>1){d=Infinity;for(let i=1;i<b.points.length;i++)d=Math.min(d,segmentDistance(x,y,screen(b.points[i-1]),screen(b.points[i])));}if(d<dist){dist=d;best=b;}}return best;}
canvas.addEventListener('pointerdown',e=>{dragging={x:e.offsetX,y:e.offsetY,ex:e.offsetX,ey:e.offsetY,cx,cy,moved:false,region:regionMode};canvas.setPointerCapture(e.pointerId);$('tooltip').hidden=true;});
canvas.addEventListener('pointermove',e=>{if(dragging?.region){dragging.ex=e.offsetX;dragging.ey=e.offsetY;draw();return;}if(dragging){const dx=e.offsetX-dragging.x,dy=e.offsetY-dragging.y;if(Math.hypot(dx,dy)>4)dragging.moved=true;if(dragging.moved){cx=dragging.cx-dx/zoom;cy=dragging.cy-dy/zoom;draw();}return;}const b=hit(e.offsetX,e.offsetY);$('tooltip').hidden=!b;if(b){$('tooltip').textContent=b.name+(factory&&factoryDiagnostic?.states.get(b.id)?' · '+factoryDiagnostic.states.get(b.id).reason:'')+(b.category==='wall'?' · axe '+fmt(FactoryMetrics.wallAxis(b.yaw))+'°':'');$('tooltip').style.left=Math.min(width-240,e.offsetX+15)+'px';$('tooltip').style.top=Math.max(5,e.offsetY-35)+'px';}});
canvas.addEventListener('pointerup',e=>{if(dragging?.region){dragging.ex=e.offsetX;dragging.ey=e.offsetY;makeFactory(dragging);dragging=null;setRegionMode(false);return;}if(dragging&&!dragging.moved){const saved=savedFactoryAt(e.offsetX,e.offsetY);const zone=zoneAt(e.offsetX,e.offsetY);if(saved)openSavedFactory(saved.id,false);else if(zone>=0)openDensityZone(zone,false);else{const b=hit(e.offsetX,e.offsetY);if(b)select(b.id);else clearInspection();}}dragging=null;persistView();});canvas.addEventListener('pointercancel',()=>dragging=null);canvas.addEventListener('pointerleave',()=>{$('tooltip').hidden=true;});canvas.addEventListener('wheel',e=>{e.preventDefault();zoomAt(Math.exp(-e.deltaY*.0015),e.offsetX,e.offsetY);},{passive:false});
new ResizeObserver(entries=>{const box=entries[0].contentRect;width=box.width;height=box.height;const dpr=window.devicePixelRatio||1;canvas.width=width*dpr;canvas.height=height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);draw();}).observe($('map'));
function spec(parent,label,value){const row=elem('div',undefined,'spec');row.append(elem('span',label),elem('strong',value));parent.append(row);}
function select(id,locate=false){const b=byId.get(id);if(!b)return;showInspection();selected=id;if(locate){active.add(b.category);updateLayers();visibleNow();cx=b.position[0];cy=b.position[1];zoom=Math.max(zoom,2);}renderDetail();draw();}
function renderDetail(){const b=byId.get(selected);$('detail').hidden=!b;$('noSelection').hidden=!!b;if(!b){$('detail').replaceChildren();return;}const panel=$('detail');panel.replaceChildren();panel.append(elem('div',categories[b.category][0].toUpperCase(),'kind'),elem('h2',b.name));spec(panel,'Position X / Y',`${fmt(b.position[0])} / ${fmt(b.position[1])} m`);spec(panel,'Altitude',fmt(b.position[2])+' m');spec(panel,'Recette enregistrée',b.recipe||'Non renseignée');spec(panel,'Connexions',String(b.ports.filter(p=>ports.get(p).state==='connected').length)+' / '+b.ports.length+' ports présents');spec(panel,'Débit réel','Non mesuré');
 if(b.category==='wall'){spec(panel,'Axe du mur (plan)',fmt(FactoryMetrics.wallAxis(b.yaw))+'°');spec(panel,'Rotation locale +X',fmt((b.yaw*180/Math.PI+360)%360)+'°');panel.append(elem('p','Trait = largeur du mur ; petit repère = face locale +X. Angle du trait : 0° vers la droite, 90° vertical. Projection schématique de 8 m, sans géométrie exacte des variantes.','note'));}
 if(b.savedClock!==null)spec(panel,'Cadence enregistrée',fmt(b.savedClock*100)+' %');
 const actions=elem('div',undefined,'traceactions');for(const [direction,label]of [['down','Suivre la sortie →'],['up','← Suivre l’entrée']]){const button=elem('button',label,'button');button.disabled=!b.ports.length;button.addEventListener('click',()=>runTrace(direction));actions.append(button);}const autoButton=elem('button','Proposer une usine autour de ce bâtiment','button');autoButton.disabled=!b.ports.length;autoButton.addEventListener('click',()=>proposeFactory(b.id));panel.append(actions,autoButton,elem('h2','Ports convoyeurs'));
 if(!b.ports.length)panel.append(elem('p','Aucun port convoyeur sérialisé. Les ports par défaut absents du fichier ne sont pas inventés.','note'));
 for(const pid of b.ports){const p=ports.get(pid),peer=byId.get(p.peerOwner);const direction=p.direction==='in'?'Entrée':p.direction==='out'?'Sortie':'Direction inconnue';const button=elem('button',`${direction} · ${p.name}`,'portbutton');let label=p.state==='open'?'Ouvert':p.state==='unresolved'?'Référence non résolue':peer?.name||'Bâtiment inconnu';button.append(elem('small',label+(peer?' ↗':'')));button.disabled=!peer;button.addEventListener('click',()=>select(peer.id,true));panel.append(button);}
 const details=elem('details'),summary=elem('summary','Détails et limites');details.append(summary,elem('p',b.type),elem('p',b.id),elem('p','Tracé convoyeur issu de la géométrie enregistrée. Les symboles des bâtiments ne représentent pas leur empreinte réelle.'),elem('p','Directions : noms Input/Output ou déduction par les connexions réciproques des convoyeurs. Les directions ambiguës restent inconnues.'));panel.append(details);
}
function runTrace(direction){if(!selected)return;const members=new Set([selected]),queue=[selected],ends=[],seenEdges=new Set();let capped=false;while(queue.length){const id=queue.shift(),b=byId.get(id);for(const pid of b.ports){const p=ports.get(pid),wanted=direction==='down'?'out':'in';if(!p.direction){ends.push({id,reason:'Direction inconnue'});continue;}if(p.direction!==wanted)continue;if(p.state!=='connected'){ends.push({id,reason:p.state==='open'?'Port ouvert':'Référence non résolue'});continue;}const next=byId.get(p.peerOwner);seenEdges.add([pid,p.peer].sort().join('|'));if(members.has(next.id))continue;if(members.size>=250){capped=true;continue;}members.add(next.id);if(next.passThrough)queue.push(next.id);else ends.push({id:next.id,reason:next.category==='storage'?'Arrêt au stockage':next.category==='machine'?'Arrêt à la machine':'Traversée non prise en charge'});}}
 let inputs=0,outputs=0,unknown=0;for(const p of ports.values()){if(!members.has(p.owner))continue;if(p.state==='unresolved'){unknown++;continue;}if(p.state==='connected'&&!members.has(p.peerOwner)){if(p.direction==='in')inputs++;else if(p.direction==='out')outputs++;else unknown++;}}
 trace={members,ends,capped,direction,inputs,outputs,unknown};renderScope();draw();status(`${members.size} bâtiments sélectionnés par le tracé ${direction==='down'?'aval':'amont'}.`);}
function renderScope(){const panel=$('scope');panel.hidden=!trace;panel.replaceChildren();if(!trace)return;panel.append(elem('h2',`Tracé ${trace.direction==='down'?'aval':'amont'} · ${trace.members.size} bâtiments`));panel.append(elem('p',`${trace.inputs} entrée(s) · ${trace.outputs} sortie(s) à la frontière`));if(trace.unknown)panel.append(elem('p',`${trace.unknown} port(s) de frontière non résolus.`));if(trace.capped)panel.append(elem('p','Tracé partiel : limite de 250 bâtiments atteinte.'));
 const list=elem('div',undefined,'stops');const unique=new Map(trace.ends.map(e=>[e.id+e.reason,e]));for(const e of [...unique.values()].slice(0,15)){const button=elem('button',`${byId.get(e.id).name} · ${e.reason}`,'result');button.addEventListener('click',()=>select(e.id,true));list.append(button);}panel.append(list,elem('p','Stockages et machines sont inclus comme extrémités, sans traverser leurs recettes. La sélection n’est pas sauvegardée.','note'));const clear=elem('button','Effacer le tracé','button');clear.addEventListener('click',()=>{trace=null;renderScope();draw();});panel.append(clear);}
function search(){const q=$('search').value.trim().toLowerCase(),holder=$('results');holder.replaceChildren();if(!q||!world)return;const synonyms={'convoyeur':'conveyor','répartiteur':'splitter','constructeur':'constructor','stockage':'storage','fonderie':'foundry'};const term=synonyms[q]||q;const matches=world.buildings.filter(b=>(b.name+' '+FactoryI18n.translate(b.name,'en')+' '+(b.recipe||'')+' '+FactoryI18n.translate(b.recipe||'','en')+' '+b.type+' '+b.id).toLowerCase().includes(term));for(const b of matches.slice(0,25)){const button=elem('button',b.name,'result');button.append(elem('small',`${b.recipe?b.recipe+' · ':''}Altitude ${fmt(b.position[2])} m · ${b.id.split('.').at(-1).slice(-14)}`));button.addEventListener('click',()=>select(b.id,true));holder.append(button);}holder.append(elem('p',`${matches.length} résultat(s)${matches.length>25?' · 25 premiers affichés':''}`,'micro'));}
async function request(url,body,headers={}){const response=await fetch(url,{method:'POST',headers:{'X-Factory-Tools':'local-viewer',...headers},body});const result=await response.json();if(!response.ok)throw new Error(result.error||'Échec de lecture.');return result;}
async function load(action,options={}){if(pending)return;pending=true;$('load').disabled=true;$('busy').hidden=false;status('Lecture locale en cours…');try{const data=await action();if(!data.buildings||!data.ports)throw new Error('Données invalides.');world=data;currentSaveRef=options.sourceRef||null;byId=new Map(data.buildings.map(b=>[b.id,b]));ports=new Map(data.ports.map(p=>[p.id,p]));selected=null;trace=null;factory=null;renderFactory();setRegionMode(false);$('search').value='';$('results').replaceChildren();$('empty').hidden=data.buildings.length>0;if(!data.buildings.length){$('empty').querySelector('h2').textContent='Aucun bâtiment dans cet instantané.';$('empty').querySelector('p').textContent='Cette sauvegarde est lisible. Essayez une partie plus avancée.';}$('saveInfo').hidden=false;$('session').textContent=data.save.session;$('saveMeta').textContent=`Format ${data.save.saveVersion} · Build ${data.save.build}`;$('fileName').textContent=`${data.save.name} · ${new Date(data.save.savedAt).toLocaleString(FactoryI18n.locale)}`;$('total').textContent=fmt(data.buildings.length);updateLayers();renderDetail();renderScope();fit();if(options.zones){densityZones=options.zones;draw();}else detectDensityZones();await refreshFactories();if(options.view)restoreView(options.view);if(!options.cached){try{await ExplorerCache.write({world,sourceRef:currentSaveRef,zones:densityZones.map(({contains,...zone})=>zone)});}catch{status('Cache navigateur indisponible ; le cache serveur reste utilisable.');}}persistView(true);status((options.cached?'Instantané restauré · ':data.cache?.hit?'Cache local · ':'')+`${fmt(data.buildings.length)} constructions · ${fmt(data.ports.length)} ports · ${data.quality.unresolvedPorts} références non résolues · ${data.quality.unknownDirections} directions inconnues.`);}catch(error){status(error.message,true);}finally{pending=false;$('busy').hidden=true;$('load').disabled=false;$('file').value='';}}
$('load').addEventListener('click',()=>{const id=$('saves').value;if(id)load(()=>request('/api/load',JSON.stringify({id}),{'Content-Type':'application/json'}),{sourceRef:saveChoices.get(id)});else $('file').click();});$('file').addEventListener('change',()=>{const file=$('file').files[0];if(!file)return;if(!file.name.toLowerCase().endsWith('.sav')||file.size>64*1024*1024||!file.size){status('Choisissez un fichier .sav de 1 octet à 64 Mo.',true);return;}load(()=>request('/api/upload',file,{'Content-Type':'application/octet-stream','X-File-Name':encodeURIComponent(file.name)}));});$('plus').addEventListener('click',()=>zoomAt(1.5));$('minus').addEventListener('click',()=>zoomAt(1/1.5));$('search').addEventListener('input',search);function showInspection(){document.querySelector('.workspace').classList.remove('inspection-closed');$('inspectToggle').hidden=true;}
$('clear').addEventListener('click',()=>{document.querySelector('.workspace').classList.add('inspection-closed');$('inspectToggle').hidden=!(factory||selected||trace);persistView();});$('inspectToggle').onclick=showInspection;document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!document.querySelector('dialog[open]')){setRegionMode(false);dragging=null;clearInspection();}});
updateLayers();fetch('/api/saves').then(r=>{if(!r.ok)throw new Error('Liste indisponible');return r.json();}).then(async saves=>{saveChoices=new Map(saves.map(s=>[s.id,{id:s.id,stamp:s.stamp+':'+(s.analysis||'')}]));$('saves').replaceChildren(new Option('Choisir une sauvegarde…',''));for(const s of saves)$('saves').append(new Option(`${s.name} · ${fmt(s.size/1024)} Ko`,s.id));if(!saves.length)$('saves').append(new Option('Aucune sauvegarde trouvée',''));await restoreSnapshot();}).catch(async()=>{$('saves').replaceChildren(new Option('Choisir un fichier .sav…',''));status('Liste indisponible. Utilisez Ouvrir la sauvegarde.',true);await restoreSnapshot();});




function setRegionMode(enabled){
 regionMode=enabled;$('region').setAttribute('aria-pressed',String(enabled));$('region').textContent=enabled?'Annuler la zone':'＋ Délimiter une usine';canvas.style.cursor=enabled?'crosshair':'grab';
 if(enabled)status('Tracez un rectangle autour de l’usine. Sélection de tous les bâtiments du périmètre, y compris les calques masqués. Échap pour annuler.');draw();
}
function makeFactory(d){
 if(Math.abs(d.ex-d.x)<8||Math.abs(d.ey-d.y)<8){status('Zone trop petite : tracez un rectangle autour de plusieurs bâtiments.',true);return;}
 const x1=(d.x-width/2)/zoom+cx,x2=(d.ex-width/2)/zoom+cx,y1=(d.y-height/2)/zoom+cy,y2=(d.ey-height/2)/zoom+cy;
 const rect={minX:Math.min(x1,x2),maxX:Math.max(x1,x2),minY:Math.min(y1,y2),maxY:Math.max(y1,y2)};
 const candidates=world.buildings.filter(b=>b.position[0]>=rect.minX&&b.position[0]<=rect.maxX&&b.position[1]>=rect.minY&&b.position[1]<=rect.maxY);
 if(!candidates.length){status('Aucun bâtiment visible dans cette zone. Vérifiez les calques et l’altitude.',true);return;}
 factory={members:new Set(candidates.map(b=>b.id)),rect,name:'Usine de référence',id:crypto.randomUUID(),source:'manual',dirty:true};selected=null;trace=null;renderScope();renderDetail();renderFactory();draw();status(`${candidates.length} constructions isolées. Référence à vérifier avec vos débits connus.`);
}
function renderFactory(){
 const panel=$('factoryScope');panel.hidden=!factory;panel.replaceChildren();if(factory)showInspection();$('noSelection').hidden=!!(factory||selected);if(!factory)return;
 factoryTransportCache=new Map();const members=[...factory.members].map(id=>byId.get(id)).filter(Boolean),machines=members.filter(b=>b.category==='machine').length;
 const name=elem('input');name.value=factory.name;name.maxLength=80;name.setAttribute('aria-label','Nom de l’usine de référence');name.addEventListener('input',()=>{factory.name=name.value;factory.dirty=true;$('factorySaveStatus').textContent='Modifications non enregistrées';persistView();});name.addEventListener('keydown',e=>{if(e.key==='Enter')saveFactory();});
 const save=elem('button','Enregistrer','button');save.setAttribute('aria-label','Enregistrer cette usine');save.addEventListener('click',saveFactory);const saveStatus=elem('p',factory.dirty?'Modifications non enregistrées':'Périmètre enregistré','note');saveStatus.id='factorySaveStatus';const nameRow=elem('div',undefined,'factory-name-row');nameRow.append(name,save);panel.append(nameRow,saveStatus,elem('p',`${machines} machines · ${factory.source==='walls'?'enveloppe guidée par les murs':'périmètre proposé à confirmer'}`,'micro'));
 const report=FactoryMetrics.flowReport(members,world.buildings,world.ports);
 factoryDiagnostic=FactoryMetrics.diagnostics(members,world.buildings,world.ports,{boundary:true,rect:factory.rect});
 const previewButton=elem('button','◈ Visualisation 3D','button primary');previewButton.addEventListener('click',()=>showFactoryPreview(members));panel.prepend(previewButton);
 renderEfficiency(panel,members);renderDashboard(panel,members,report);
 const details=elem('details');details.append(elem('summary','Détails de production et diagnostic'));renderBalance(details,members);renderEstimate(details,members);
 spec(details,'Périmètre',`${fmt(factory.rect.maxX-factory.rect.minX)} × ${fmt(factory.rect.maxY-factory.rect.minY)} m`);if(factory.missing)details.append(elem('p',`${factory.missing} construction(s) absente(s) : périmètre à revoir.`,'note warning'));panel.append(details);
 const actions=elem('div',undefined,'traceactions');const focus=elem('button','Cadrer cette usine','button');focus.addEventListener('click',()=>{cx=(factory.rect.minX+factory.rect.maxX)/2;cy=(factory.rect.minY+factory.rect.maxY)/2;zoom=Math.min((width-60)/(factory.rect.maxX-factory.rect.minX),(height-60)/(factory.rect.maxY-factory.rect.minY));draw();});actions.append(focus);panel.append(actions);
}
const diagnosticColours={good:'#65c98a',warning:'#f2ac52',critical:'#ec6464'};
function diagnosticColour(id){return factory&&factoryDiagnostic?diagnosticColours[factoryDiagnostic.states.get(id)?.level]:null;}
function renderEfficiency(panel,members){
 const section=elem('section',undefined,'factory-efficiency');section.append(elem('h3','Efficacité estimée'));
 const resources=factoryDiagnostic.resources.filter(r=>r.item.production>0);
 const known=resources.filter(r=>!r.actual.partial),score=known.length?known.reduce((sum,r)=>sum+Math.min(100,100*r.actual.delivered/r.item.production),0)/known.length:null;
 const value=elem('strong',score===null?'—':fmt(score)+' %','factory-efficiency-score');section.append(value);
 if(known.length<resources.length)section.append(elem('p','Estimation partielle','note'));
 const details=elem('details');details.append(elem('summary','Détail de l’efficacité'),elem('p','Moyenne des taux utiles par ressource identifiée. La consommation interne et les sorties utiles sont comptées. Les ressources aux trajets incomplets sont exclues du pourcentage global.','note'));
 if(!resources.length)details.append(elem('p','Aucune production calculable dans cette sélection.','note'));
 for(const {item,actual}of resources){const row=elem('div',undefined,'resource-card'),ratio=Math.min(100,100*actual.delivered/item.production);
  row.append(elem('strong',item.name+' · '+(actual.partial?'Partiel':fmt(ratio)+' % utiles')),elem('p',fmt(actual.delivered)+' / '+fmt(item.production)+' par min affectables · consommation + sorties','note'));details.append(row);
 }
 details.append(elem('p','Vert : besoin servi · Orange : perte jusqu’à 20 % · Rouge : perte supérieure à 20 %. Gris : données insuffisantes. Un manifold plein n’est pas un goulot à lui seul.','note'));section.append(details);panel.append(section);
}
function resourceIcon(id){const ns='http://www.w3.org/2000/svg',icon=document.createElementNS(ns,'svg');icon.setAttribute('viewBox','0 0 64 64');icon.setAttribute('aria-hidden','true');icon.classList.add('explorer-resource-icon');const base=document.createElementNS(ns,'circle');base.setAttribute('cx','32');base.setAttribute('cy','32');base.setAttribute('r','25');base.setAttribute('fill','var(--button)');icon.append(base);const use=document.createElementNS(ns,'use');use.setAttribute('href','/resource-icons.svg#'+id);icon.append(use);return icon;}
function renderDashboard(panel,members,report){
 const dashboard=elem('div',undefined,'factory-dashboard'),inside=new Set(members.map(b=>b.id)),supplies=new Map();
 const supplyFor=item=>{if(!supplies.has(item.id))supplies.set(item.id,FactoryMetrics.inputReport(item,members,world.buildings,world.ports));return supplies.get(item.id);};
 const incoming=report.items.filter(i=>i.demand>0&&(i.kind==='input'||supplyFor(i).sources.some(s=>!inside.has(s.id)))),outgoing=report.items.filter(i=>i.production>0&&transportFor(i,members).exported>.01);
 for(const [side,title,items]of [['input','Entrées',incoming],['output','Sorties',outgoing]]){
  const section=elem('section',undefined,'io-section'),heading=elem('h3',undefined,'io-section-heading');heading.append(elem('span',side==='input'?'↘':'↗','io-heading-icon'),elem('span',title));section.append(heading);
  for(const item of items){
   const row=elem('div',undefined,'io-resource io-resource-line'),body=elem('div',undefined,'io-resource-body'),amount=elem('div',undefined,'io-resource-amount'),t=item.production>0?transportFor(item,members):null;
   body.append(elem('strong',item.name));row.append(resourceIcon(item.id),body,amount);
   if(side==='input'){
    const supply=supplyFor(item),need=Math.max(0,item.demand-(t?.internal||0));amount.append(elem('strong',fmt(need)),elem('small','/ min requis'));
    if(supply.potential>0){const useful=factoryDiagnostic?.usefulInputs,adjusted=item.production===0&&useful?.settled?(useful.demands.get(item.id)??need):need,used=Math.min(adjusted,supply.capacity??adjusted),ratio=100*used/supply.potential,uncertain=supply.shared||supply.partial||!useful?.settled;body.append(elem('span',(uncertain?'Jusqu’à ':'')+fmt(ratio)+' % du potentiel des filons sollicité','io-badge'),elem('small',fmt(used)+' / '+fmt(supply.potential)+' par min · potentiel à la cadence enregistrée'+(supply.shared?' · source partagée avec d’autres branches':uncertain?' · estimation partielle':'')));}else if(supply.miners)body.append(elem('small','Utilisation du filon indéterminée : pureté inconnue'));
    const external=supply.sources.filter(s=>!inside.has(s.id));body.append(elem('small',supply.miners?supply.miners+' mineur(s) relié(s)':external.length?external.length+' source(s) amont':'Besoin des recettes'));
    const details=elem('details');details.append(elem('summary','Voir les sources et le transport'));if(supply.capacity!==null)details.append(elem('p','Capacité des chemins identifiés : '+fmt(supply.capacity)+' / min.','note'));
    for(const source of external){const b=elem('button',source.name,'portbutton');b.onclick=()=>select(source.id,true);details.append(b);}details.append(elem('p',supply.ambiguous?'Recette à plusieurs ingrédients : attribution exacte aux ports non établie.':'Débit entrant estimé ; extraction et alimentation effective non mesurées.','note'));row.append(details);
   }else{
    amount.append(elem('strong',fmt(t.exported)),elem('small','/ min estimés'));const destinations=[];if(t.storageIds.length)destinations.push(t.storageIds.length+' coffre(s)');if(t.exits.length)destinations.push(t.exits.length+' sortie(s) du périmètre');body.append(elem('small',destinations.join(' · ')));
    if(t.limited)body.append(elem('span','Capacité convoyeur limitante','io-badge warning'));else if(!t.partial){const rate=100*t.exported/Math.max(.000001,item.production-t.internal);body.append(elem('span',fmt(Math.min(100,rate))+' % acheminables','io-badge'));}
    const details=elem('details');details.append(elem('summary','Voir les destinations'));for(const id of [...t.storageIds,...t.exits.map(e=>e.id)]){const b=byId.get(id);if(!b)continue;const button=elem('button',b.name,'portbutton');button.onclick=()=>select(id,true);details.append(button);}if(t.partial)details.append(elem('p','Estimation sur les chemins identifiés ; certaines références ou ressources restent inconnues.','note'));row.append(details);
   }section.append(row);
  }
  if(!items.length)section.append(elem('p',side==='input'?'Aucun besoin externe identifié.':'Aucun trajet sortant relié aux recettes lues.','note'));dashboard.append(section);
 }
 const paths=elem('details');paths.append(elem('summary','Ressources intermédiaires et convoyeurs'));for(const item of report.items.filter(i=>i.production>0)){const t=transportFor(item,members),r=elem('div',undefined,'resource-card');r.append(elem('strong',item.name),elem('p',fmt(t.delivered)+' / '+fmt(item.production)+' par min acheminables · '+t.belts.length+' convoyeur(s)','note'));for(const belt of t.belts.slice(0,20)){const button=elem('button',belt.name+' · '+fmt(belt.estimated)+' / '+fmt(belt.capacity)+' par min'+(belt.saturated?' · saturé':''),'portbutton');button.onclick=()=>select(belt.id,true);r.append(button);}paths.append(r);}dashboard.append(paths,elem('p','Capacités estimées depuis la sauvegarde. Débit réel en jeu non mesuré.','note'));panel.append(dashboard);
}
function showFactoryPreview(members){
 const dialog=elem('dialog',undefined,'factory-preview'),head=elem('div',undefined,'preview-heading');head.append(elem('h2','Visualisation 3D'));const close=elem('button','Fermer','button');close.addEventListener('click',()=>dialog.close());head.append(close);dialog.append(head,elem('p','Positions, rotations et hauteurs approximatives. Les modèles, textures et formes exactes du jeu ne sont pas inclus.','note'));const host=elem('div');dialog.append(host);document.body.append(dialog);let preview;dialog.addEventListener('close',()=>{preview?.destroy();dialog.remove();},{once:true});dialog.showModal();const context=factoryDiagnostic?[...factoryDiagnostic.context].map(id=>byId.get(id)).filter(Boolean):members;preview=FactoryPreview.create(host,context.slice(0,10000),{diagnostics:factoryDiagnostic?.states});if((factoryDiagnostic?.context.size||members.length)>10000)dialog.append(elem('p','Aperçu limité à 10 000 constructions.','note'));
}
$('region').addEventListener('click',()=>{if(!world){status('Chargez d’abord une sauvegarde.',true);return;}setRegionMode(!regionMode);});


function suggestRole(recipes){
 const names=[...recipes.keys()];
 if(!names.length)return {title:'Rôle indéterminé',reason:'Aucune recette enregistrée dans cette sélection. Les bâtiments seuls ne suffisent pas à établir sa production.'};
 const materials=[['cuivre',/copper|cuivre/i],['fer',/\biron\b|\bfer\b/i],['acier',/steel|acier/i],['aluminium',/alumin/i],['plastique / caoutchouc',/plastic|rubber|plastique|caoutchouc/i]].filter(([,pattern])=>names.some(n=>pattern.test(n))).map(([label])=>label);
 let title=materials.length===1?'Transformation : '+materials[0]+' (probable)':materials.length>1?'Production mixte : '+materials.join(', '):names.every(n=>/wire|cable|fil|câble/i.test(n))?'Fabrication de fils / câbles':names.length===1?'Fabrication : '+names[0]:'Atelier à productions multiples';
 return {title,reason:'Suggestion à valider, déduite des noms de recettes de cette zone. Elle ne prouve ni la matière réellement fournie ni les débits. Les recettes sans matière explicite restent ambiguës.'};
}



$('background').addEventListener('change',()=>{
 try{localStorage.setItem('factoryTools.background',$('background').value);}catch{}
 if($('background').value==='terrain'&&!terrainReady)status('Chargement du fond de carte local…');
 draw();
});

function drawPriority(b){return ['foundation','roof'].includes(b.category)?0:b.category==='wall'?1:2;}
function refreshSavedList(){
 const list=$('savedFactories');list.replaceChildren();list.append(new Option(savedFactories.length?'Choisir une usine…':'Aucune usine enregistrée',''));
 for(const f of savedFactories)list.append(new Option(f.name,f.id));if(factory?.id)list.value=factory.id;$('savedFactorySection').hidden=!world;
}
async function refreshFactories(){
 const key=world.worldKey;try{const response=await fetch('/api/factories?worldKey='+encodeURIComponent(key));const result=await response.json();if(!response.ok)throw new Error(result.error);if(world.worldKey!==key)return;savedFactories=result.factories;refreshSavedList();}catch(error){savedFactories=[];refreshSavedList();status('Lecture des usines enregistrées : '+error.message,true);}
}
function openSavedFactory(id,focus=true){
 const record=savedFactories.find(f=>f.id===id);if(!record)return;
 factory={...record,members:new Set(record.members),dirty:false,missing:record.members.filter(m=>!byId.has(m)).length};
 selected=null;trace=null;visibleNow();renderDetail();renderScope();renderFactory();refreshSavedList();
 if(focus){cx=(factory.rect.minX+factory.rect.maxX)/2;cy=(factory.rect.minY+factory.rect.maxY)/2;zoom=Math.min((width-60)/(factory.rect.maxX-factory.rect.minX),(height-60)/(factory.rect.maxY-factory.rect.minY));}draw();status('Usine restaurée : '+factory.name);
}
async function saveFactory(){
 if(!factory||!world)return;const key=world.worldKey,id=factory.id||crypto.randomUUID();factory.id=id;
 try{const result=await request('/api/factories',JSON.stringify({worldKey:key,factory:{id,name:factory.name,members:[...factory.members],rect:factory.rect,source:factory.source}}),{'Content-Type':'application/json'});
 if(world.worldKey!==key)return;savedFactories=savedFactories.filter(f=>f.id!==id);savedFactories.push(result.factory);refreshSavedList();if(factory?.id===id){factory.name=result.factory.name;factory.dirty=false;renderFactory();}status('Usine enregistrée sur cet ordinateur : '+result.factory.name);
 }catch(error){status('Enregistrement impossible : '+error.message,true);if($('factorySaveStatus'))$('factorySaveStatus').textContent='Échec : '+error.message;}
}
$('restoreFactory').addEventListener('click',()=>openSavedFactory($('savedFactories').value));
function proposeFactory(seedId){
 const seed=byId.get(seedId),radius=60;if(!seed||!Number.isFinite(radius)||radius<10||radius>300){status('Choisissez un rayon de 10 à 300 m.',true);return;}
 const previous=factory?.members.has(seedId)?factory:null;const simpleChain=seed.rateModel?.inputs.length===1;const members=new Set([seedId]),queue=[seedId];let cuts=0,capped=false;
 const distance=p=>Math.hypot(p[0]-seed.position[0],p[1]-seed.position[1],p[2]-seed.position[2]);
 while(queue.length){const current=byId.get(queue.shift());if(current.category==='storage'&&current.id!==seedId)continue;
 for(const pid of current.ports){const p=ports.get(pid);if(p.state!=='connected'||members.has(p.peerOwner))continue;const next=byId.get(p.peerOwner);if(!next)continue;
 if((seed.recipe&&next.category==='machine'&&!next.recipe)||(simpleChain&&next.rateModel?.inputs.length>1)){cuts++;continue;}
 if(distance(next.position)>radius||next.points.some(point=>distance(point)>radius*1.5)){cuts++;continue;}if(members.size>=350){capped=true;continue;}members.add(next.id);queue.push(next.id);}}
 const objects=[...members].map(id=>byId.get(id)),points=objects.flatMap(b=>b.points.length?b.points:[b.position]);
 const rect={minX:Math.min(...points.map(p=>p[0]))-4,maxX:Math.max(...points.map(p=>p[0]))+4,minY:Math.min(...points.map(p=>p[1]))-4,maxY:Math.max(...points.map(p=>p[1]))+4};
 const minZ=Math.min(...points.map(p=>p[2]))-4,maxZ=Math.max(...points.map(p=>p[2]))+8;
 for(const b of world.buildings)if(['wall','foundation','roof','decoration','structure'].includes(b.category)&&b.position[0]>=rect.minX&&b.position[0]<=rect.maxX&&b.position[1]>=rect.minY&&b.position[1]<=rect.maxY&&b.position[2]>=minZ&&b.position[2]<=maxZ)members.add(b.id);
 factory={id:previous?.id||crypto.randomUUID(),name:previous?.name||'Usine proposée',members,rect,source:'automatic',dirty:true};trace=null;selected=null;
 visibleNow();renderDetail();renderScope();renderFactory();draw();status(`Proposition locale : ${members.size} objets, ${cuts} liaison(s) arrêtée(s) aux limites de rayon ou d’activité.${capped?' Limite de 350 objets de production atteinte.':''} À valider puis enregistrer.`);
}
function boundaryCandidates(port){
 if(!port.direction)return {names:[],uncertain:true};
 const forward=port.direction==='in',wanted=forward?'out':'in',items=new Map(),seen=new Set(),queue=[port.owner];let uncertain=false;
 while(queue.length&&seen.size<350){const id=queue.shift();if(seen.has(id))continue;seen.add(id);const b=byId.get(id);if(!b)continue;
 if(b.rateModel){const entries=forward?b.rateModel.inputs:b.rateModel.outputs;for(const item of entries)items.set(item.id,item.name);continue;}
 if(!b.passThrough){uncertain=true;continue;}for(const pid of b.ports){const p=ports.get(pid);if(!p.direction){uncertain=true;continue;}if(p.direction===wanted&&p.state==='connected'&&factory.members.has(p.peerOwner))queue.push(p.peerOwner);}}
 return {names:[...items.values()],uncertain};
}
function renderEstimate(panel,members){
 const section=elem('details');section.open=false;section.append(elem('summary','Connexions et hypothèses du bilan'));
 const boundaries=[...ports.values()].filter(p=>chainBoundary(p)&&p.state==='connected');
 if(!boundaries.length)section.append(elem('p','Aucune connexion convoyeur externe résolue dans ce périmètre.','note'));
 for(const p of boundaries.slice(0,16)){const data=boundaryCandidates(p),label=p.direction==='in'?'Connexion entrante':p.direction==='out'?'Connexion sortante':'Sens inconnu';const row=elem('button',label+' : '+(data.names.join(' / ')||'objet indéterminé'),'portbutton');row.append(elem('small','Objets possibles selon les recettes, sans mesure de débit'+(data.uncertain?' · parcours incomplet':'')));row.addEventListener('click',()=>select(p.owner,true));section.append(row);}
 if(boundaries.length>16)section.append(elem('p',`${boundaries.length-16} autres connexions de frontière.`,'note'));
 const totals=new Map();let supported=0,unsupported=0,assumptions=0;
 for(const b of members){if(!b.recipe)continue;const m=b.rateModel;if(!m?.supported){unsupported++;continue;}supported++;if(m.assumedClock||m.assumedBoost)assumptions++;
 for(const [sign,entries]of [[-1,m.inputs],[1,m.outputs]])for(const item of entries){if(!totals.has(item.id))totals.set(item.id,{name:item.name,value:0});totals.get(item.id).value+=sign*item.rate;}}
 section.append(elem('h2','Soldes bruts des recettes (pas les sorties)'));
 if(!supported)section.append(elem('p','Pas de recette solide calculable dans cette zone.','note'));
 for(const item of totals.values())if(Math.abs(item.value)>.01)spec(section,(item.value<0?'Solde négatif : ':'Solde positif : ')+item.name,fmt(Math.abs(item.value))+' / min');
 section.append(elem('p',`${supported} machine(s) calculée(s), ${unsupported} recette(s) non calculée(s). ${assumptions} machine(s) utilisent une cadence ou un bonus de 1× supposé, faute de valeur enregistrée.`,'note'));
 if(world.catalogBuild!==world.save.build)section.append(elem('p',`Catalogue installé build ${world.catalogBuild||'inconnu'} ; sauvegarde build ${world.save.build}. Versions différentes : chiffres à confirmer.`,'note warning'));
 section.append(elem('p','Capacité théorique : consommation et production nettes des recettes calculables, avec alimentation suffisante. Les mines, générateurs, fluides, blocages, arrêts et pertes de routage ne sont pas simulés. Un excédent interne n’est pas une sortie observée et un besoin net n’est pas une mesure d’entrée.','note'));panel.append(section);
}


function renderBalance(panel,members){
 const report=FactoryMetrics.flowReport(members,world.buildings,world.ports);
 const card=elem('div',undefined,'balance-card');card.append(elem('div','ENTRÉES → TRANSFORMATION → COFFRES','eyebrow'));
 card.append(elem('p','Affectation théorique par ressource. Le premier coffre termine la chaîne ; son contenu redistribué appartient à une autre liaison.','note'));
 if(report.assumed||world.catalogBuild!==world.save.build)card.append(elem('p','Estimation provisoire : cadences supposées et/ou versions différentes.','note warning'));
 if(report.unsupported)card.append(elem('p',`${report.unsupported} recette(s) non calculable(s) : pourcentages incomplets.`,'note warning'));
 renderResourceFlows(card,report);
 const details=elem('details');details.append(elem('summary','Comprendre les pourcentages'));
 details.append(elem('p','Intermédiaire : minimum entre la couverture du besoin interne et la part de production affectable aux besoins internes ou à un premier coffre. Sortie : part du disponible après besoins internes pouvant atteindre un premier coffre. Les besoins internes sont servis avant les coffres. Une ressource consommée sans production interne nécessite un débit externe : son pourcentage reste à confirmer.','note'));
 details.append(elem('p','Calcul sur les chemins de convoyeurs ordinaires et les capacités des recettes ; ne traverse ni machine ni coffre. Capacités des convoyeurs, règles avancées de répartition, niveau des coffres, énergie et débit réel non simulés. Un déficit ne réduit pas encore les capacités des recettes aval dans ce calcul. Les volumes vers les coffres sont des potentiels, sans preuve de débit réel. Optimisation réelle : non mesurée.','note'));card.append(details);panel.append(card);
}

function detectDensityZones(){
 const candidates=FactoryMetrics.density(world.buildings,28,2),claimed=new Set(),rooms=new Map();densityZones=[];
 // Closed wall envelopes partition a dense group instead of requiring the whole group to fit one room.
 for(const candidate of candidates){
  if(true)for(const id of candidate.machineIds.slice(0,24)){
   if(claimed.has(id))continue;const seed=byId.get(id),room=FactoryMetrics.wallRoom(seed,world.buildings)||FactoryMetrics.wallRoom(seed,world.buildings,true);if(!room)continue;
   const key=JSON.stringify(room.rect)+'|'+Math.round(seed.position[2]/8);if(rooms.has(key))continue;rooms.set(key,room);
   const ids=room.machineIds.filter(id=>!claimed.has(id));if(!ids.length)continue;densityZones.push({...room,machineIds:ids});ids.forEach(id=>claimed.add(id));
  }
  const remaining=candidate.machineIds.filter(id=>!claimed.has(id));if(remaining.length){const xs=remaining.map(id=>byId.get(id).position[0]),ys=remaining.map(id=>byId.get(id).position[1]);densityZones.push({...candidate,machineIds:remaining,rect:{minX:Math.min(...xs)-10,maxX:Math.max(...xs)+10,minY:Math.min(...ys)-10,maxY:Math.max(...ys)+10}});remaining.forEach(id=>claimed.add(id));}
 }
 // Follow local physical connections to join stacked production, stopping at storage and geographic borders.
 for(const zone of densityZones){const ids=new Set(zone.machineIds),seen=new Set(),queue=[...ids],r=zone.rect;
  for(let n=0;n<queue.length&&seen.size<2000;n++){const id=queue[n];if(seen.has(id))continue;seen.add(id);const b=byId.get(id);if(!b||b.category==='storage')continue;
   for(const pid of b.ports||[]){const port=ports.get(pid),next=port?.state==='connected'&&byId.get(port.peerOwner);if(!next||next.category==='storage'||next.position[0]<r.minX||next.position[0]>r.maxX||next.position[1]<r.minY||next.position[1]>r.maxY)continue;
    if(next.category==='machine'){if(!next.recipe)continue;ids.add(next.id);}else if(!next.passThrough)continue;queue.push(next.id);
   }
  }
  zone.machineIds=[...ids];const zs=zone.machineIds.map(id=>byId.get(id).position[2]);zone.minZ=Math.min(...zs)-8;zone.maxZ=Math.max(...zs)+24;
 }
 // A connection across storeys can make two initial density groups the same factory.
 for(let i=0;i<densityZones.length;i++)for(let j=i+1;j<densityZones.length;){const a=densityZones[i],b=densityZones[j];if(!a.machineIds.some(id=>b.machineIds.includes(id))){j++;continue;}a.machineIds=[...new Set([...a.machineIds,...b.machineIds])];a.rect={minX:Math.min(a.rect.minX,b.rect.minX),maxX:Math.max(a.rect.maxX,b.rect.maxX),minY:Math.min(a.rect.minY,b.rect.minY),maxY:Math.max(a.rect.maxY,b.rect.maxY)};a.minZ=Math.min(a.minZ,b.minZ);a.maxZ=Math.max(a.maxZ,b.maxZ);a.contains=null;a.outline=null;densityZones.splice(j,1);j=i+1;}
 densityZones.sort((a,b)=>a.rect.minX-b.rect.minX||a.rect.minY-b.rect.minY);draw();
}
function renderZoneLabels(){
 const holder=$('zoneLabels');holder.replaceChildren();if(!world||regionMode)return;
 const placed=[];
 densityZones.forEach((zone,i)=>{
 const r=zone.rect,a=screen([r.minX,r.minY]),b=screen([r.maxX,r.maxY]);if(!FactoryMetrics.zoneVisible(zoom,b[0]-a[0],b[1]-a[1]))return;if(b[0]<0||b[1]<0||a[0]>width||a[1]>height)return;
 ctx.save();ctx.globalAlpha=.7;ctx.strokeStyle='#86bacb';ctx.lineWidth=1;ctx.setLineDash([3,4]);if(zone.outline){ctx.beginPath();for(const [p,q]of zone.outline){const aa=screen(p),bb=screen(q);ctx.moveTo(...aa);ctx.lineTo(...bb);}ctx.stroke();}else ctx.strokeRect(a[0],a[1],b[0]-a[0],b[1]-a[1]);ctx.restore();
 const baseX=Math.max(0,Math.min(width-148,(a[0]+b[0])/2-65)),baseY=Math.max(3,Math.min(height-35,a[1]-25));let lx=baseX,ly=baseY;
 for(const dy of [0,-30,30,-60,60,-90,90,-120,120]){let found=false;for(const dx of [0,-150,150]){const x=Math.max(0,Math.min(width-148,baseX+dx)),y=Math.max(3,Math.min(height-35,baseY+dy));if(!placed.some(p=>x<p.x+148&&x+148>p.x&&y<p.y+28&&y+28>p.y)){lx=x;ly=y;found=true;break;}}if(found)break;}placed.push({x:lx,y:ly});
 if(lx!==baseX||ly!==baseY){ctx.save();ctx.strokeStyle='#86bacb88';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo((a[0]+b[0])/2,(a[1]+b[1])/2);ctx.lineTo(lx+65,ly+14);ctx.stroke();ctx.restore();}
 const button=elem('button',`Zone ${i+1} · ${zone.machineIds.length} machines`,'zone-label');button.style.left=lx+'px';button.style.top=ly+'px';button.setAttribute('aria-label',`Analyser la zone ${i+1} · ${zone.machineIds.length} machines`);button.addEventListener('click',()=>openDensityZone(i));holder.append(button);
 });
}
function openDensityZone(index,focus=true){
 const zone=densityZones[index];if(!zone)return;const r=zone.rect;
 const members=new Set(zone.machineIds);for(const b of world.buildings)if(b.category!=='machine'&&true&&b.position[0]>=r.minX&&b.position[0]<=r.maxX&&b.position[1]>=r.minY&&b.position[1]<=r.maxY&&b.position[2]>=zone.minZ&&b.position[2]<=zone.maxZ)members.add(b.id);
 // Only reuse saved density definitions with the same production membership.
 const signature=zone.machineIds.slice().sort().join('|');const previous=savedFactories.find(f=>['density','walls'].includes(f.source)&&f.members.filter(id=>byId.get(id)?.category==='machine').sort().join('|')===signature);
 factory={id:previous?.id||crypto.randomUUID(),name:previous?.name||`Zone ${index+1} — usine proposée`,members,rect:{...r},source:zone.wallGuided?'walls':'density',dirty:!previous};selected=null;trace=null;
 visibleNow();renderDetail();renderScope();renderFactory();if(focus){cx=(r.minX+r.maxX)/2;cy=(r.minY+r.maxY)/2;zoom=Math.min((width-80)/(r.maxX-r.minX),(height-80)/(r.maxY-r.minY));}draw();$('factoryScope').scrollIntoView({block:'start'});status(`Zone ${index+1} : entrées, ressources intermédiaires et sorties du périmètre. Frontières à confirmer.`);
}
function renderResourceFlows(panel,report){
 for(const [kind,title]of [['input','1 · ENTRÉES REQUISES'],['intermediate','2 · RESSOURCES INTERMÉDIAIRES'],['output','3 · SORTIES VERS UN COFFRE'],['unassigned','À DIAGNOSTIQUER · SANS COFFRE IDENTIFIÉ']]){
  panel.append(elem('div',title,'eyebrow flow-heading'));const rows=report.items.filter(i=>kind==='output'?i.stored>.01:kind==='unassigned'?i.production>0&&i.unassigned>.01&&!i.storageIds.length:i.kind===kind);if(kind==='unassigned'&&!rows.length){panel.lastChild.remove();continue;}
  if(!rows.length)panel.append(elem('p','Aucune ressource identifiée dans cette catégorie.','note'));
  for(const item of rows){const row=elem('div',undefined,'resource-card');row.append(elem('strong',item.name));
   const incomplete=factory.missing||report.unsupported;const value=kind==='input'||incomplete?null:kind==='output'?100*item.stored/Math.max(.000001,item.production-item.consumed):kind==='intermediate'?Math.min(item.use,item.coverage):item.use;
   const label=value===null||(item.partial&&value<.01)?'À confirmer':item.partial?'≥ '+fmt(value)+' % identifié':fmt(value)+' %';row.append(elem('div',label,'flow-percent'));const body=elem('details');body.append(elem('summary','Détails et destinations'));row.append(elem('p',kind==='input'?fmt(item.demand)+' / min':kind==='output'?fmt(item.stored)+' / min vers coffre':fmt(item.production)+' / min produits · '+fmt(item.consumed)+' / min affectables en interne','note'),body);
   if(kind==='input'){spec(body,'Besoin externe',fmt(item.demand)+' / min');body.append(elem('p','Débit entrant non mesuré : pureté, cadence et acheminement à confirmer.','note'));}
   else {if(kind==='output'){spec(body,'Disponible après besoins internes',fmt(item.production-item.consumed)+' / min');}else spec(body,'Production théorique',fmt(item.production)+' / min');if(kind==='intermediate'){spec(body,'Besoin interne',fmt(item.demand)+' / min');spec(body,'Affectable en interne',fmt(item.consumed)+' / min');spec(body,'Couverture interne',fmt(item.coverage)+' %');}
    spec(body,'Vers premier coffre',fmt(item.stored)+' / min');if(item.unassigned>.01)spec(body,'Débouché non identifié',fmt(item.unassigned)+' / min');
    if(item.storageIds.length){const show=elem('button',`Voir ${item.storageIds.length} coffre(s) terminal(aux)`,'portbutton');show.addEventListener('click',()=>{select(item.storageIds[0],true);status(`${item.name} : premier coffre terminal identifié sur un chemin de sortie. Débit réel non mesuré.`);});body.append(show);}else body.append(elem('p','Aucun coffre terminal retrouvé sur les chemins pris en charge.','note'));
    if(item.partial)body.append(elem('p','Parcours incomplet : les débouchés non identifiés ne prouvent pas un blocage.','note'));}
   panel.append(row);
  }
 }
 const sources=new Map(),seen=new Set(),queue=[];let partial=false;
 for(const p of ports.values())if(chainBoundary(p)&&p.direction==='in'&&p.state==='connected')queue.push(p.peerOwner);
 while(queue.length&&seen.size<1000){const id=queue.shift();if(seen.has(id)||factory.members.has(id))continue;seen.add(id);const b=byId.get(id);if(!b){partial=true;continue;}
  if(!b.passThrough){sources.set(id,b);continue;}for(const pid of b.ports){const p=ports.get(pid);if(!p.direction)partial=true;if(p.direction==='in'&&p.state==='connected')queue.push(p.peerOwner);}}
 if(queue.length)partial=true;
 if(sources.size||partial){const details=elem('details');details.append(elem('summary',`${sources.size} source(s) amont trouvée(s)${partial?' · parcours partiel':''}`));for(const b of sources.values()){const row=elem('button',b.name,'portbutton');row.addEventListener('click',()=>select(b.id,true));details.append(row);}details.append(elem('p','Arrêt aux premières machines ou aux stockages amont. Débit d’extraction non déduit du seul nombre de mineurs.','note'));panel.append(details);}
}

function chainBoundary(p){return factory.members.has(p.owner)&&byId.get(p.owner)?.category!=='storage'&&(!factory.members.has(p.peerOwner)||byId.get(p.peerOwner)?.category==='storage');}

function zoneAt(x,y){let best=-1,distance=Infinity;densityZones.forEach((zone,i)=>{const r=zone.rect,a=screen([r.minX,r.minY]),b=screen([r.maxX,r.maxY]),dx=Math.max(a[0]-x,0,x-b[0]),dy=Math.max(a[1]-y,0,y-b[1]),d=Math.hypot(dx,dy),area=Math.abs((b[0]-a[0])*(b[1]-a[1]));if(d<=8&&area<distance){best=i;distance=area;}});return best;}


function savedFactoryAt(x,y){const p=[(x-width/2)/zoom+cx,(y-height/2)/zoom+cy];return savedFactories.filter(f=>p[0]>=f.rect.minX&&p[0]<=f.rect.maxX&&p[1]>=f.rect.minY&&p[1]<=f.rect.maxY).sort((a,b)=>(a.rect.maxX-a.rect.minX)*(a.rect.maxY-a.rect.minY)-(b.rect.maxX-b.rect.minX)*(b.rect.maxY-b.rect.minY))[0];}
canvas.addEventListener('dblclick',e=>{const b=hit(e.offsetX,e.offsetY);if(b)select(b.id);});

function transportFor(item,members){if(!factoryTransportCache.has(item.id))factoryTransportCache.set(item.id,FactoryMetrics.transportReport(item,members,world.buildings,world.ports,{boundary:true,rect:factory.rect}));return factoryTransportCache.get(item.id);}

function clearInspection(){factory=null;selected=null;trace=null;renderFactory();renderDetail();renderScope();document.querySelector('.workspace').classList.add('inspection-closed');$('inspectToggle').hidden=true;draw();persistView();}

function persistView(immediate=false){
 if(!world)return;clearTimeout(viewTimer);const save=()=>{try{sessionStorage.setItem('factoryManager.explorer.view',JSON.stringify({worldKey:world.worldKey,sourceId:currentSaveRef?.id||null,cx,cy,zoom,active:[...active],selected,factory:factory?{...factory,members:[...factory.members]}:null,closed:document.querySelector('.workspace').classList.contains('inspection-closed')}));}catch{}};if(immediate)save();else viewTimer=setTimeout(save,120);
}
function restoreView(v){
 if(!v||v.worldKey!==world.worldKey||v.sourceId!==(currentSaveRef?.id||null))return;
 if(Array.isArray(v.active)){active.clear();for(const key of v.active)if(categories[key])active.add(key);}updateLayers();visibleNow();
 if(v.factory?.rect&&Array.isArray(v.factory.members)){factory={...v.factory,members:new Set(v.factory.members.filter(id=>byId.has(id))),missing:v.factory.members.filter(id=>!byId.has(id)).length};renderFactory();}
 if(v.selected&&byId.has(v.selected))select(v.selected);
 if([v.cx,v.cy,v.zoom].every(Number.isFinite)&&v.zoom>0){cx=v.cx;cy=v.cy;zoom=Math.max(.015,Math.min(40,v.zoom));}
 if(v.closed||!factory&&!selected){document.querySelector('.workspace').classList.add('inspection-closed');$('inspectToggle').hidden=!(factory||selected);}draw();
}
async function restoreSnapshot(){
 let view;try{view=JSON.parse(sessionStorage.getItem('factoryManager.explorer.view')||'null');}catch{}
 const record=await ExplorerCache.read();if(world||pending)return;
 if(!record?.world){const source=view?.sourceId&&saveChoices.get(view.sourceId);if(source){$('saves').value=source.id;await load(()=>request('/api/load',JSON.stringify({id:source.id}),{'Content-Type':'application/json'}),{sourceRef:source,view});}return;}
 const source=record.sourceRef?.id&&saveChoices.get(record.sourceRef.id);if(source)$('saves').value=source.id;
 if(source&&source.stamp!==record.sourceRef.stamp){await load(()=>request('/api/load',JSON.stringify({id:source.id}),{'Content-Type':'application/json'}),{sourceRef:source,view});return;}
 await load(()=>Promise.resolve(record.world),{cached:true,sourceRef:record.sourceRef,zones:record.zones,view});
}
window.addEventListener('pagehide',()=>persistView(true));
