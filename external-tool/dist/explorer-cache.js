'use strict';
(function(root){
 const version=2;let connection;
 function open(){if(connection)return connection;connection=new Promise((resolve,reject)=>{const req=indexedDB.open('factory-manager-explorer',1);req.onupgradeneeded=()=>req.result.createObjectStore('snapshots');req.onerror=()=>reject(req.error);req.onsuccess=()=>resolve(req.result);req.onblocked=()=>reject(new Error('Cache occupé'));});return connection;}
 async function read(){try{const db=await open();return await new Promise((resolve,reject)=>{const request=db.transaction('snapshots').objectStore('snapshots').get('current');request.onsuccess=()=>resolve(request.result?.version===version?request.result:null);request.onerror=()=>reject(request.error);});}catch{return null;}}
 async function write(record){const db=await open();return new Promise((resolve,reject)=>{const tx=db.transaction('snapshots','readwrite');tx.objectStore('snapshots').put({...record,version},'current');tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);});}
 root.ExplorerCache={read,write};
})(globalThis);
