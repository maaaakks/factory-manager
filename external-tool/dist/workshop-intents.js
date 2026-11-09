'use strict';
function syncIntentChoices(){
 for(const b of document.querySelectorAll('[data-intent]')){const design=b.dataset.intent==='design',key=b.dataset.intentKey,value=key==='shape'?(design?designShape:calculatorShape):document.getElementById((design?{layoutStyle:'variationLayout',storeyMode:'variationStoreys'}:{layoutStyle:'layoutStyle',storeyMode:'storeyMode'})[key]).value;b.setAttribute('aria-pressed',String(value===b.dataset.intentValue));const unavailable=design&&key==='shape'&&b.dataset.intentValue==='exotic'&&project.design?.enabled&&project.design.family==='m05';b.disabled=unavailable;b.title=unavailable?'Les angles rentrants M05 ne sont pas encore assemblés automatiquement.':'';}
}
function planInBackground(request,result){
 return new Promise((resolve,reject)=>{const worker=new Worker('/workshop-planner-worker.js');result.textContent='Recherche d’une implantation…';result.setAttribute('aria-busy','true');let done=false;const stop=()=>{done=true;clearTimeout(timer);worker.terminate();result.removeAttribute('aria-busy');};const timer=setTimeout(()=>{stop();reject(new Error('Cette implantation prend trop de temps. Essayez Rectangle et Auto, ou réduisez les débits. Le plan actuel est conservé.'));},20000);
 worker.onmessage=e=>{if(done)return;if(e.data.progress){result.textContent=e.data.progress.label;return;}stop();if(e.data.error)reject(new Error(e.data.error));else resolve(e.data.project);};worker.onerror=()=>{if(done)return;stop();reject(new Error('Le calcul a été interrompu. Le plan actuel est conservé.'));};worker.postMessage(request);});
}
document.addEventListener('DOMContentLoaded',()=>{
 document.getElementById('layoutStyle').value='balanced';document.getElementById('resourceEditor').open=!project.flows?.outputs?.length;
 for(const b of document.querySelectorAll('[data-intent]'))b.onclick=()=>{const design=b.dataset.intent==='design',key=b.dataset.intentKey;if(key==='shape'){if(design)designShape=b.dataset.intentValue;else calculatorShape=b.dataset.intentValue;}else{const id=(design?{layoutStyle:'variationLayout',storeyMode:'variationStoreys'}:{layoutStyle:'layoutStyle',storeyMode:'storeyMode'})[key];document.getElementById(id).value=b.dataset.intentValue;if(key==='layoutStyle'){document.getElementById(design?'reserveCladding':'calcReserveCladding').checked=b.dataset.intentValue==='spacious'&&(design?!!project.design?.enabled:document.getElementById('generationPriority').value==='architecture');if(design)updateTerrainHint();}}syncIntentChoices();};
 for(const id of ['layoutStyle','storeyMode','variationLayout','variationStoreys'])document.getElementById(id).addEventListener('change',syncIntentChoices);
 document.getElementById('refreshFloor').onclick=()=>{const select=document.getElementById('floorMaterial');select.selectedIndex=(select.selectedIndex+1)%select.options.length;document.getElementById('floorAppearance').click();};
 document.getElementById('floorMaterial').addEventListener('change',()=>document.getElementById('floorAppearance').click());
 document.getElementById('designFloorProfile').addEventListener('change',()=>document.getElementById('floorAppearance').click());
 syncIntentChoices();
});
