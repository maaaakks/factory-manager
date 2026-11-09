const assert=require('node:assert/strict'),M=require('../dist/workshop-model.js');
const p=M.fresh('appearance');assert.equal(p.appearance?.enabled??false,false);assert.equal(M.read(p).appearance,undefined);
const custom={...p,appearance:{enabled:true,color:'#f0a050'}};assert.deepEqual(M.read(JSON.stringify(custom)).appearance,custom.appearance);assert.deepEqual(M.read({...custom,appearance:{...custom.appearance,enabled:false}}).appearance,{enabled:false,color:'#f0a050'});
for(const appearance of [null,{enabled:'yes',color:'#ffffff'},{enabled:true,color:'red'},{enabled:true,color:'#fff'}])assert.throws(()=>M.read({...p,appearance}),/couleurs/);
assert.equal(p.appearance,undefined);console.log('PASS: neutral legacy defaults, optional global appearance persistence and validation');
