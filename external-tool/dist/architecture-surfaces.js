'use strict';
(function(root){
 const categories=['machines','logistics','power','floors','walls','frames','windows','roofs'];
 function group(part){const a=part.asset||'';return part.panelUnits?'walls':a.startsWith('Foundation')?'floors':a.includes('PowerPole')?'power':part.component==='window'||a.includes('Window')?'windows':part.component==='roof'||a.startsWith('Roof_')?'roofs':part.component==='beam'||a.startsWith('Beam_')||part.component==='corner'?'frames':part.component==='wall'||part.component==='gable'||a.startsWith('Wall_')?'walls':'frames';}
 function material(asset,choice){const m=/^Wall_(?:Concrete_|Orange_)?8x([124])(?:_01)?$/.exec(asset);if(!m||!choice||choice==='original')return asset;return choice==='concrete'?'Wall_Concrete_8x'+m[1]:m[1]==='4'?'Wall_8x4_01':'Wall_Orange_8x'+m[1];}
 function apply(parts,design){return parts.map(part=>({...part,asset:material(part.asset,design.wallMaterial),color:design.colors?.[group(part)]||part.color}));}
 const api={categories,group,material,apply};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ArchitectureSurfaces=api;
})(typeof globalThis!=='undefined'?globalThis:this);
