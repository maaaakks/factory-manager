'use strict';
// A schematic ribbon with depth, following the saved or planned 3D centreline.
(function(root){
 function mesh(points,width=.8,height=.2){
  const faces=[];for(let i=1;i<points.length;i++){
   const a=points[i-1],b=points[i],delta=b.map((n,k)=>n-a[k]),length=Math.hypot(...delta);if(length<1e-6)continue;
   const t=delta.map(n=>n/length),horizontal=Math.hypot(t[0],t[1]),side=horizontal>1e-6?[-t[1]/horizontal,t[0]/horizontal,0]:[1,0,0];
   const up=[t[1]*side[2]-t[2]*side[1],t[2]*side[0]-t[0]*side[2],t[0]*side[1]-t[1]*side[0]],corners=[];
   for(const p of [a,b])for(const [s,u]of [[-1,-1],[1,-1],[1,1],[-1,1]])corners.push(p.map((n,k)=>n+side[k]*s*width/2+up[k]*u*height/2));
   for(const indices of [[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]])faces.push(indices.map(n=>corners[n]));
  }return faces;
 }
 const api={mesh};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.TransportGeometry=api;
})(typeof globalThis!=='undefined'?globalThis:this);
