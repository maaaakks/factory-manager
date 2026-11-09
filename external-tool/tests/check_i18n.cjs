const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),root=path.resolve(process.argv[2]||path.join(__dirname,'..'));
const pack=require(path.join(root,'dist/locales/en.json')),t=require(path.join(root,'dist/i18n.js')).createTranslator(pack);
for(const [fr,en]of Object.entries(pack)){assert.equal(t(fr).toLowerCase(),en.toLowerCase(),fr);assert.equal(t(fr,'fr'),fr,'French source changed');}
assert.equal(t('4 fonderies · Lingot de fer'),'4 smelters · Iron Ingot');
assert.equal(t('← Atelier'),'← Workshop');assert.equal(t('14,5 MW'),'14.5 MW');
assert.equal(t('1,234.5 MW','en','en'),'1,234.5 MW');assert.equal(t('1,234.5 MW','fr','en'),'1\u202f234,5 MW');
assert.equal(t('3 convoyeur(s)'),'3 conveyors');assert.equal(t('2 étages'),'2 floors');
for(const page of fs.readdirSync(path.join(root,'dist')).filter(p=>p.endsWith('.html'))){const text=fs.readFileSync(path.join(root,'dist',page),'utf8');assert(text.includes('src="/i18n.js"'),page);}
const code=fs.readFileSync(path.join(root,'dist/i18n.js'),'utf8');for(const selector of ['#session','#fileName','#saved option','#savedFactories option','#saves option','.project-card strong'])assert(code.includes(selector),selector);
assert(!code.includes('.value=translate'),'Input values must never be translated');
console.log('PASS: '+Object.keys(pack).length+' translations, exact French roundtrip, dynamic counts, locale-aware numbers, all six pages and user-name exclusions');
