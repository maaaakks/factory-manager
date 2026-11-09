'use strict';
(function(root){
 const normalize=s=>String(s).normalize('NFC').replace(/[’‘]/g,"'").replace(/\s+/g,' ').trim();
 const escape=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
 function convertNumbers(value,from,to){
  if(from===to)return value;
  if(to==='en')return value.replace(/(?<![\p{L}\p{N}_.])\d+(?:[\u00a0\u202f]\d{3})+(?:,\d+)?|(?<![\p{L}\p{N}_.])\d+,\d+/gu,n=>n.replace(',','.').replace(/[\u00a0\u202f]/g,','));
  return value.replace(/(?<![\p{L}\p{N}_.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\p{L}\p{N}_.])\d+\.\d+/gu,n=>n.replace(/,/g,'\u202f').replace('.',','));
 }
 function createTranslator(pack){
  const exact=new Map(),lower=new Map();for(const [fr,en]of Object.entries(pack)){exact.set(normalize(fr),en);lower.set(normalize(fr).toLocaleLowerCase('fr'),en);}
  const fragments=[...exact.keys()].filter(k=>k.length>1&&k.length<95&&/[A-Za-zÀ-ÿ]/.test(k)).sort((a,b)=>b.length-a.length);
  const pattern=new RegExp('(?<![\\p{L}\\p{N}_])(?:'+fragments.map(escape).join('|')+')(?![\\p{L}\\p{N}_])','giu');
  const counts={étage:['floor','floors'],fondation:['foundation','foundations'],machine:['machine','machines'],fonderie:['smelter','smelters'],constructeur:['constructor','constructors'],assembleuse:['assembler','assemblers'],convoyeur:['conveyor','conveyors'],élévateur:['lift','lifts'],bâtiment:['building','buildings'],construction:['building','buildings'],objet:['object','objects'],résultat:['result','results'],port:['port','ports'],niveau:['level','levels']};
  function translate(value,language='en',sourceLanguage='fr'){
   const raw=String(value??'');if(language==='fr'||!raw.trim())return convertNumbers(raw,sourceLanguage,language);
   const key=normalize(raw),match=exact.get(key)??lower.get(key.toLocaleLowerCase('fr'));
   const preserveCase=value=>key===key.toLocaleUpperCase('fr')&&/[A-ZÀ-Ÿ]/.test(key)?value.toLocaleUpperCase('en'):value;
   if(match!==undefined)return raw.slice(0,raw.indexOf(raw.trim()))+preserveCase(match)+raw.slice(raw.trimEnd().length);
   const icon=key.match(/^([^\p{L}\p{N}]+)(.+)$/u);if(icon){const label=exact.get(icon[2])??lower.get(icon[2].toLocaleLowerCase('fr'));if(label!==undefined)return icon[1]+label;}
   let text=convertNumbers(raw,sourceLanguage,language).replace(/Plan éditable de (\d+) par (\d+) fondations, hauteur ([\d.,]+) mètres/gi,'Editable plan: $1 × $2 foundations, height $3 m').replace(/(\d+)\s+à\s+([\d.,]+)\s*%/g,'$1 at $2 %');
   text=text.replace(/(\d+(?:[.,]\d+)?)\s+(étage|fondation|machine|fonderie|constructeur|assembleuse|convoyeur|élévateur|bâtiment|construction|objet|résultat|port|niveau)(?:\(s\)|s)?(?![\p{L}])/giu,(_,n,word)=>n+' '+counts[word.toLowerCase()][Number(n)===1?0:1]);
   text=text.replace(/Logistics floor de ([\d.,]+) m/gi,'$1 m logistics floor').replace(/pièces architecturales natives/gi,'native architectural parts').replace(/hauteur/gi,'height').replace(/minimum/gi,'minimum');
   return text.replace(pattern,fr=>{const en=exact.get(normalize(fr))??lower.get(normalize(fr).toLocaleLowerCase('fr'));return fr===fr.toLocaleUpperCase('fr')&&/[A-ZÀ-Ÿ]/.test(fr)?en.toLocaleUpperCase('en'):en;});
  }
  return translate;
 }
 if(typeof module!=='undefined'&&module.exports){module.exports={createTranslator,normalize};return;}
 const KEY='factoryTools.language',supported=['fr','en'];let language='fr';try{const saved=localStorage.getItem(KEY);if(supported.includes(saved))language=saved;}catch{}
 let translate=(s)=>String(s??''),observer,queued=false;const texts=new WeakMap(),attributes=new WeakMap();
 const excluded='script,style,noscript,textarea,pre,code,[data-i18n-ignore],#session,#fileName,#nativeSession option,.project-card strong,#saved option:not([value=""]),#savedFactories option:not([value=""]),#saves option:not([value=""])';
 function ignored(element){return !element||!!element.closest(excluded);}
 function sourceRecord(map,key,current){const previous=map.get(key);return previous&&current===previous.last?previous:{source:current,last:current,locale:language};}
 function translateText(node){if(ignored(node.parentElement)||!node.nodeValue.trim())return;const explicit=node.parentElement.getAttribute('data-i18n-'+language);if(explicit!==null){if(node.nodeValue!==explicit)node.nodeValue=explicit;return;}const full=node.parentElement.getAttribute('data-i18n-source');if(full!==null){const max=Number(node.parentElement.getAttribute('data-i18n-max')),label=translate(full,language),value=max>0&&label.length>max?label.slice(0,max-1)+'…':label;if(node.nodeValue!==value)node.nodeValue=value;return;}const record=sourceRecord(texts,node,node.nodeValue),value=translate(record.source,language,record.locale);record.last=value;texts.set(node,record);if(node.nodeValue!==value)node.nodeValue=value;}
 function translateAttributes(element){
  if(ignored(element))return;let records=attributes.get(element);if(!records){records=new Map();attributes.set(element,records);}
  for(const name of ['title','aria-label','aria-valuetext','placeholder','alt']){
   if(name==='aria-label'&&element.matches('.project-card,.delete-project'))continue;
   const current=element.getAttribute(name);if(current===null)continue;
   const record=sourceRecord(records,name,current),value=translate(record.source,language,record.locale);record.last=value;records.set(name,record);if(value!==current)element.setAttribute(name,value);
  }
 }
 function apply(){
  queued=false;const base=document.documentElement;if(!base)return;const walker=document.createTreeWalker(base,NodeFilter.SHOW_TEXT);let node;while((node=walker.nextNode()))translateText(node);
  for(const element of base.querySelectorAll('[title],[aria-label],[aria-valuetext],[placeholder],[alt]'))translateAttributes(element);
  for(const a of document.querySelectorAll('a[href^="https://satisfactory-calculator.com/"]')){const current=a.getAttribute('href'),next=current.replace(/^(https:\/\/satisfactory-calculator\.com)\/(?:fr|en)\//,'$1/'+language+'/');if(next!==current)a.setAttribute('href',next);}
  document.documentElement.lang=language;const select=document.getElementById('languageChoice');if(select){select.value=language;const label=language==='en'?'Interface language':'Langue de l’interface';if(select.getAttribute('aria-label')!==label)select.setAttribute('aria-label',label);}
 }
 function schedule(){if(queued)return;queued=true;queueMicrotask(apply);}
 function observe(){if(observer)return;observer=new MutationObserver(schedule);observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['title','aria-label','aria-valuetext','placeholder','alt']});apply();}
 const ready=fetch('/locales/en.json').then(r=>{if(!r.ok)throw new Error('Language pack unavailable');return r.json();}).then(pack=>{translate=createTranslator(pack);if(document.readyState!=='loading')observe();schedule();return pack;});
 const api={get language(){return language;},get locale(){return language==='en'?'en-US':'fr-FR';},text:value=>translate(value,language),translate:(value,lang)=>translate(value,lang),ready,
  async setLanguage(value){if(!supported.includes(value))throw new RangeError('Unsupported language');await ready;language=value;try{localStorage.setItem(KEY,value);}catch{}apply();window.dispatchEvent(new CustomEvent('factory-language-change',{detail:{language,locale:api.locale}}));}
 };
 root.FactoryI18n=api;document.documentElement.lang=language;
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',observe,{once:true});else observe();
 ready.catch(error=>console.error(error));
})(typeof globalThis!=='undefined'?globalThis:this);
