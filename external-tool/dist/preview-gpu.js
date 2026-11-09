'use strict';
// Both preview modes use cached GPU geometry. Transparent mode keeps an X-ray
// view through all layers; opaque mode uses the hardware depth buffer.
// Geometry is uploaded once per immutable project; camera moves update uniforms.
(function(root){
 const states=new WeakMap(),colors=new Map();let probe,pixel;
 // Remove identical geometry once per scene, independently of winding.
 function prepareGeometry(faces,lines){
  const point=p=>p.map(v=>Math.round(v*100000)).join(','),seenFaces=new Set(),seenLines=new Set();
  const unique=(items,seen)=>items.filter(item=>{const key=item.coords.map(point).sort().join('|');if(seen.has(key))return false;seen.add(key);return true;});
  const cleanFaces=unique(faces,seenFaces),cleanLines=unique(lines,seenLines),bounds=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]];
  for(const item of [...cleanFaces,...cleanLines])for(const p of item.coords)for(let i=0;i<3;i++){bounds[0][i]=Math.min(bounds[0][i],p[i]);bounds[1][i]=Math.max(bounds[1][i],p[i]);}
  const valid=Number.isFinite(bounds[0][0]),center=valid?bounds[0].map((v,i)=>(v+bounds[1][i])/2):[0,0,0],radius=valid?Math.max(1,Math.hypot(...bounds[1].map((v,i)=>v-center[i]))*1.05):1;
  return {faces:cleanFaces,lines:cleanLines,depthFrame:[...center,radius]};
 }
 function rgba(value){
  const theme=document.documentElement.dataset.theme||'';const key=theme+'|'+value;if(colors.has(key))return colors.get(key);
  if(!probe){probe=document.createElement('span');probe.hidden=true;document.body.append(probe);pixel=document.createElement('canvas').getContext('2d',{willReadFrequently:true});pixel.canvas.width=pixel.canvas.height=1;}
  probe.style.color=value;pixel.clearRect(0,0,1,1);pixel.fillStyle=getComputedStyle(probe).color;pixel.fillRect(0,0,1,1);const result=[...pixel.getImageData(0,0,1,1).data].map(v=>v/255);colors.set(key,result);return result;
 }
 function state(svg){
  if(states.has(svg))return states.get(svg);
  const canvas=document.createElement('canvas');canvas.className='preview-gpu';canvas.setAttribute('aria-hidden','true');svg.parentElement.append(canvas);
  const gl=canvas.getContext('webgl',{alpha:false,antialias:true,depth:true,preserveDrawingBuffer:true});if(!gl){canvas.remove();states.set(svg,null);return null;}
  const shader=(type,code)=>{const s=gl.createShader(type);gl.shaderSource(s,code);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader de prévisualisation indisponible.');return s;};
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec3 position; attribute vec4 color; uniform vec4 screenX; uniform vec4 screenY; uniform vec3 near; uniform vec4 depthFrame; varying vec4 shade; void main(){vec4 p=vec4(position,1.0); gl_Position=vec4(dot(p,screenX),dot(p,screenY),-dot(position-depthFrame.xyz,near)/depthFrame.w,1.0);shade=color;}'));
  gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float; varying vec4 shade; void main(){gl_FragColor=shade;}'));gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Prévisualisation GPU indisponible.');
  const s={gl,canvas,program,key:null,triangles:gl.createBuffer(),lines:gl.createBuffer(),glassBuffer:gl.createBuffer(),glassFaces:[],triangleCount:0,lineCount:0,locations:{}};
  for(const k of ['screenX','screenY','near','depthFrame'])s.locations[k]=gl.getUniformLocation(program,k);for(const k of ['position','color'])s.locations[k]=gl.getAttribLocation(program,k);
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();s.key=null;canvas.hidden=true;svg.classList.remove('gpu-active');svg.dataset.renderer='lost';});
  canvas.addEventListener('webglcontextrestored',()=>{states.delete(svg);canvas.remove();window.dispatchEvent(new Event('resize'));});states.set(svg,s);return s;
 }
 function draw(view,key,faces,lines,{opaque=true}={}){
  let s;try{s=state(view.svg);}catch{return false;}if(!s||s.gl.isContextLost())return false;
  const {gl,canvas}=s;
  if(s.key!==key||s.opaque!==opaque){
   if(!faces)return false;
   const prepared=prepareGeometry(faces,lines);faces=prepared.faces;lines=prepared.lines;s.depthFrame=prepared.depthFrame;
   const tri=[],segments=[],vertex=(arr,p,c)=>arr.push(...p,...c),colour=(source,attribute)=>{const value=rgba(source.getAttribute(attribute)||'var(--muted)').slice();if(!opaque){const raw=source.getAttribute(attribute==='fill'?'fill-opacity':'stroke-opacity'),alpha=raw===null?1:Number(raw);value[3]*=Number.isFinite(alpha)?alpha:1;}else value[3]=1;return value;};
   s.glassFaces=[];for(const f of faces){const c=colour(f.source,'fill');if(opaque&&f.source.getAttribute('data-glass')==='true'){c[3]=Number(f.source.getAttribute('fill-opacity')||.28);s.glassFaces.push({coords:f.coords,color:c});continue;}for(let i=1;i<f.coords.length-1;i++)for(const p of [f.coords[0],f.coords[i],f.coords[i+1]])vertex(tri,p,c);}
   for(const l of lines){const c=colour(l.source,'stroke');for(const p of l.coords)vertex(segments,p,c);}
   gl.bindBuffer(gl.ARRAY_BUFFER,s.triangles);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(tri),gl.STATIC_DRAW);s.triangleCount=tri.length/7;
   gl.bindBuffer(gl.ARRAY_BUFFER,s.lines);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(segments),gl.STATIC_DRAW);s.lineCount=segments.length/7;s.key=key;s.opaque=opaque;
   view.svg.dataset.geometryUploads=String(Number(view.svg.dataset.geometryUploads||0)+1);
  }
  const rect=view.svg.getBoundingClientRect(),parent=view.svg.parentElement.getBoundingClientRect(),ratio=Math.min(2,devicePixelRatio||1);
  canvas.style.left=rect.left-parent.left+'px';canvas.style.top=rect.top-parent.top+'px';canvas.style.width=rect.width+'px';canvas.style.height=rect.height+'px';
  const width=Math.max(1,Math.round(rect.width*ratio)),height=Math.max(1,Math.round(rect.height*ratio));if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;}
  let [x,y,w,h]=view.svg.getAttribute('viewBox').split(' ').map(Number);const aspect=width/height;if(w/h<aspect){const nw=h*aspect;x-=(nw-w)/2;w=nw;}else{const nh=w/aspect;y-=(nh-h)/2;h=nh;}
  const origin=view.project([0,0,0]),axes=[[1,0,0],[0,1,0],[0,0,1]].map(view.project),u=axes.map(p=>2*(p[0]-origin[0])/w),v=axes.map(p=>-2*(p[1]-origin[1])/h);
  gl.viewport(0,0,width,height);gl.clearColor(...rgba(getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()));gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(s.program);
  gl.uniform4fv(s.locations.screenX,[...u,2*(origin[0]-x)/w-1]);gl.uniform4fv(s.locations.screenY,[...v,1-2*(origin[1]-y)/h]);gl.uniform3fv(s.locations.near,view.near);gl.uniform4fv(s.locations.depthFrame,s.depthFrame);
  if(opaque){gl.enable(gl.DEPTH_TEST);gl.depthMask(true);gl.depthFunc(gl.LEQUAL);gl.disable(gl.BLEND);}else{gl.disable(gl.DEPTH_TEST);gl.depthMask(false);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);}
  const bind=buffer=>{gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.enableVertexAttribArray(s.locations.position);gl.vertexAttribPointer(s.locations.position,3,gl.FLOAT,false,28,0);gl.enableVertexAttribArray(s.locations.color);gl.vertexAttribPointer(s.locations.color,4,gl.FLOAT,false,28,12);};
  gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);bind(s.triangles);gl.drawArrays(gl.TRIANGLES,0,s.triangleCount);gl.disable(gl.POLYGON_OFFSET_FILL);bind(s.lines);gl.drawArrays(gl.LINES,0,s.lineCount);
  if(opaque&&s.glassFaces.length){const near=view.near,depth=f=>f.coords.reduce((sum,p)=>sum+p.reduce((a,v,i)=>a+v*near[i],0),0)/f.coords.length,arr=[];for(const f of s.glassFaces.slice().sort((a,b)=>depth(a)-depth(b)))for(let i=1;i<f.coords.length-1;i++)for(const p of[f.coords[0],f.coords[i],f.coords[i+1]])arr.push(...p,...f.color);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);gl.bindBuffer(gl.ARRAY_BUFFER,s.glassBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(arr),gl.DYNAMIC_DRAW);bind(s.glassBuffer);gl.drawArrays(gl.TRIANGLES,0,arr.length/7);gl.disable(gl.BLEND);}
  gl.depthMask(true);canvas.hidden=false;view.svg.classList.add('gpu-active');view.svg.dataset.renderer='webgl';view.svg.dataset.renderMode=opaque?'opaque':'transparent';return true;
 }
 function hide(svg){const s=states.get(svg);if(s)s.canvas.hidden=true;svg.classList.remove('gpu-active');svg.dataset.renderer='svg';}
 const api={draw,hide,prepareGeometry};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.PreviewGPU=api;
})(typeof globalThis!=='undefined'?globalThis:this);
