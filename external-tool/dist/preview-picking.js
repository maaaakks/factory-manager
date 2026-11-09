'use strict';
(function(root){
 let previousFaces,previousView,projected;
 function hit(faces,view,point,opaque=true){
  if(faces!==previousFaces||view!==previousView){
   previousFaces=faces;previousView=view;
   projected=faces.map(face=>{const points=face.coords.map(view.project),depth=face.coords.map(p=>p.reduce((n,v,i)=>n+v*view.near[i],0));return {points,depth,label:face.source.getAttribute('data-preview-machine'),minX:Math.min(...points.map(p=>p[0])),maxX:Math.max(...points.map(p=>p[0])),minY:Math.min(...points.map(p=>p[1])),maxY:Math.max(...points.map(p=>p[1]))};});
  }
  let closest=-Infinity,label=null;
  for(const face of projected){
   if(!opaque&&!face.label||point[0]<face.minX-1e-6||point[0]>face.maxX+1e-6||point[1]<face.minY-1e-6||point[1]>face.maxY+1e-6)continue;
   const a=face.points[0];
   for(let i=1;i<face.points.length-1;i++){
    const b=face.points[i],c=face.points[i+1],den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(Math.abs(den)<1e-10)continue;
    const u=((b[1]-c[1])*(point[0]-c[0])+(c[0]-b[0])*(point[1]-c[1]))/den,v=((c[1]-a[1])*(point[0]-c[0])+(a[0]-c[0])*(point[1]-c[1]))/den,w=1-u-v;
    if(u< -1e-6||v< -1e-6||w< -1e-6)continue;
    const depth=u*face.depth[0]+v*face.depth[i]+w*face.depth[i+1];if(depth>closest+1e-7){closest=depth;label=face.label;}
   }
  }
  return label||null;
 }
 const api={hit};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.PreviewPicking=api;
})(typeof globalThis!=='undefined'?globalThis:this);
