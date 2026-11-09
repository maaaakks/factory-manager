'use strict';
(function(root){
 const types={smelter:{label:'Fonderie',plural:'fonderies',recipe:'Recipe_IngotIron_C'},constructor:{label:'Constructeur',plural:'constructeurs',recipe:'Recipe_IronRod_C'},assembler:{label:'Assembleuse',plural:'assembleuses',recipe:'Recipe_IronPlateReinforced_C'}};
 function recipes(data,type){const defaults=data.productionDefaults||data.defaultRecipes;return Object.entries({...data.productionRecipes,...data.recipes}).filter(([id,r])=>r.type===type&&r.outputs.length===1&&r.inputs.length>=1&&r.inputs.length<=2&&[...r.inputs,...r.outputs].every(i=>i.solid)&&defaults[r.outputs[0].id]===id).sort((a,b)=>a[1].name.localeCompare(b[1].name,'fr'));}
 function payload(data,type,recipeId,count,logisticsFloor=true){
  const recipe=recipes(data,type).find(([id])=>id===recipeId)?.[1];
  if(!types[type]||!recipe)throw new Error('Choisissez une recette compatible avec ce pattern.');
  if(!Number.isInteger(count)||count<1||count>16)throw new Error('Choisissez entre 1 et 16 machines.');
  const rates=rows=>rows.map(i=>({id:i.id,rate:i.amount*60/recipe.seconds*count}));
  const inputs=rates(recipe.inputs),outputs=rates(recipe.outputs);if([...inputs,...outputs].some(r=>r.rate>1200+1e-6))throw new Error('Le manifold dépasse 1 200 unités/min. Réduisez le nombre de machines.');
  return {inputs,outputs,options:{logisticsFloor,layoutPolicy:'simple-patterns-v1',layoutStyle:'balanced',storeyMode:'single',shape:'rectangle'}};
 }
 const api={types,recipes,payload};if(typeof module!=='undefined'&&module.exports){module.exports=api;return;}root.WorkshopPatterns=api;
 let type='smelter',busy=false;
 const $=id=>document.getElementById(id);
 function refresh(){
  if(!plannerData)return;const result=$('patternRates');
  try{const p=payload(plannerData,type,$('patternRecipe').value,Number($('patternCount').value)),format=rows=>rows.map(r=>new Intl.NumberFormat(FactoryI18n.locale,{maximumFractionDigits:2}).format(r.rate)+' '+plannerData.names[r.id]+'/min').join(' + ');result.textContent=format(p.inputs)+' → '+format(p.outputs);$('buildPattern').disabled=busy;}
  catch(e){result.textContent=e.message;$('buildPattern').disabled=true;}
 }
 function selectType(value){type=value;for(const b of document.querySelectorAll('[data-pattern]'))b.setAttribute('aria-pressed',String(b.dataset.pattern===type));if(!plannerData)return;const select=$('patternRecipe');select.replaceChildren();for(const[id,r]of recipes(plannerData,type)){const option=document.createElement('option');option.value=id;option.textContent=r.name;select.append(option);}if([...select.options].some(o=>o.value===types[type].recipe))select.value=types[type].recipe;select.disabled=false;refresh();}
 root.refreshPatternLevels=function(){if(!$('patternBuilder'))return;const active=project.nativeProfile==='clean-manifold-v1';for(const b of document.querySelectorAll('[data-pattern-level]')){if(b.dataset.patternRole==='production')b.dataset.patternLevel=project.floors?.find(f=>f.role==='production')?.z??0;b.hidden=b.dataset.patternRole==='technical'&&!project.floors?.some(f=>f.role==='technical');b.disabled=!active;b.setAttribute('aria-pressed',String(active&&Number(b.dataset.patternLevel)===level));}document.body.dataset.hasSelection=String(selection.size>0);};
 for(const b of document.querySelectorAll('[data-pattern]'))b.onclick=()=>selectType(b.dataset.pattern);
 for(const b of document.querySelectorAll('[data-pattern-level]'))b.onclick=()=>{setEditorView('construction');level=Number(b.dataset.patternLevel);render();};
 $('patternLogisticsFloor').onchange=()=>{document.querySelector('.pattern-floors > div:last-child').hidden=!$('patternLogisticsFloor').checked;refresh();};$('patternRecipe').onchange=refresh;$('patternCount').oninput=refresh;
 $('openPatterns').onclick=()=>{setEditorView('construction');$('patternBuilder').scrollIntoView({block:'start'});$('patternRecipe').focus();};
 $('buildPattern').onclick=async()=>{
  const source=project,result=$('patternResult');busy=true;refresh();result.textContent='Création des rangées et de leur réseau…';result.setAttribute('aria-busy','true');
  try{const count=Number($('patternCount').value),body=payload(plannerData,type,$('patternRecipe').value,count,$('patternLogisticsFloor').checked),response=await fetch('/api/workshop/manifold',{method:'POST',headers:{'Content-Type':'application/json','X-Factory-Tools':'local-viewer'},body:JSON.stringify(body)}),data=await response.json();if(!response.ok)throw new Error(data.error||'Ce pattern ne peut pas être raccordé.');if(project!==source)throw new Error('Le projet a changé. Relancez la création du pattern.');const next=M.read(data.project);next.id=source.id;next.name=FactoryI18n.text(count+' '+(count===1?types[type].label.toLowerCase():types[type].plural))+' · '+$('patternRecipe').selectedOptions[0].textContent;next.buffer=M.clone(source.buffer||[]);if(!commit(next,''))throw new Error('Le pattern n’a pas pu être appliqué.');finishCalculator();result.textContent='✓ '+WorkshopPlanning.describe(next)+' · Annuler pour revenir au plan précédent.';}
  catch(e){result.textContent=e.message;}finally{busy=false;refresh();result.removeAttribute('aria-busy');}
 };
 document.addEventListener('planner-ready',()=>selectType(type));if(plannerData)selectType(type);refreshPatternLevels();
})(typeof globalThis!=='undefined'?globalThis:this);
