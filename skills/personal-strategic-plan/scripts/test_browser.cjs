/* Synthetic end-to-end verification. Run from a workspace with Playwright installed. */
const {chromium}=require('playwright');
const fs=require('node:fs');const path=require('node:path');const os=require('node:os');
const {execFileSync}=require('node:child_process');const {pathToFileURL}=require('node:url');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const testBase=path.resolve(process.env.SP_TEST_TMP||path.join(process.cwd(),'outputs/strategic-plan-test-tmp'));
fs.mkdirSync(testBase,{recursive:true});
const tmp=fs.mkdtempSync(path.join(testBase,'browser-'));
function build(data,name){const src=path.join(tmp,name+'.json');const out=path.join(tmp,name+'.html');fs.writeFileSync(src,JSON.stringify(data));execFileSync('python',[path.join(__dirname,'build_dashboard.py'),src,'--output',out]);return pathToFileURL(out).href;}
const blank=JSON.parse(fs.readFileSync(path.join(root,'assets/plan-template.json'),'utf8'));
const d=structuredClone(blank);d.person={name:'Example Planner',initials:'EP'};d.updated_at='2030-01-01';
d.brand={status:'accepted',source:'Synthetic style v1',colors:{accent:'#f3c745',sidebar:'#183b47',background:'#f6f5ee'},font_family:'Georgia',logo_path:''};
d.foundation={purpose:{text:'Present-day purpose',review_state:'accepted'},tenets:{text:['Practice deliberately','Keep promises'],review_state:'accepted'},grit:{text:'Build lasting possibilities.',review_state:'draft'}};
const annual={id:'fit-2030',pillar:'Fit',quarter:null,description:'Walk 100 miles',status:'Doing',review_state:'accepted',metric:'#',unit:'miles',measurement:'Logged calendar-year miles',comparison_key:'walking',start:0,target:100,current:25,due_date:'2030-12-31',as_of:'2030-01-01'};
const rows=[annual,
 {...annual,id:'fit-q1a',quarter:1,parent_id:annual.id,description:'Walk the first 25 miles',weight:60,target:25,current:25,status:'Done'},
 {...annual,id:'fit-q1b',quarter:1,parent_id:annual.id,description:'Walk another 25 miles',weight:40,target:25,current:0},
 {...annual,id:'fit-q2',quarter:2,parent_id:annual.id,description:'Q2 walking commitment',weight:100,start:0,target:25,current:null}];
d.years=[{year:2030,status:'draft',current_quarter:1,word:{text:'Follow Through',meaning:'Finish meaningful commitments.',review_state:'accepted',examples:['Practice consistently']},objectives:rows,reviews:[{title:'Q1 learning',date:'2030-03-31',text:'Adjust the route.'}]},
 {year:2029,status:'draft',objectives:[{...annual,id:'fit-2029',current:80,target:90}],reviews:[]}];
fs.writeFileSync(path.join(tmp,'pixel.png'),Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII=','base64'));
fs.writeFileSync(path.join(tmp,'worksheet.md'),'# Synthetic reflection\nWhat did I learn?\n<script>window.worksheetInjected=true</script>');
for(const row of [annual,rows[1]])Object.assign(row,{importance:'A meaningful synthetic reason.',importance_review_state:'draft',personal_notes:[{text:'<img src=x onerror="window.noteInjected=true">',source:'Synthetic source'}],related_assets:['pixel.png'],related_asset_details:{'pixel.png':{title:'Synthetic image',alt:'A one-pixel test image',caption:'Offline source preview'}},worksheets:[{title:'Reflection worksheet',path:'worksheet.md'}]});
d.years[0].quarter_reviews={'1':{state:'locked',locked_at:'2029-12-01',open_items:[]}};
const hostile=structuredClone(d);hostile.person.name='</script><script>window.injected=true</script>';hostile.years[0].objectives[0].description='<img src=x onerror="window.injected=true">';
(async()=>{
 let browser;
 try {
  browser=await chromium.launch({headless:true,channel:process.env.SP_BROWSER_CHANNEL||'msedge'});
  const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[];const requests=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
  await page.goto(build(blank,'blank'));
  assert.equal(await page.locator('.pillar-name').count(),6);
  assert.match(await page.locator('h1').textContent(),/Make \d{4} count/);
  assert.equal(await page.getByRole('heading',{name:'Your six life pillars'}).count(),1);
  await page.getByRole('link',{name:'Start here',exact:true}).click();await page.getByRole('heading',{name:'A thoughtful plan. A manageable process.'}).waitFor();
  await page.goBack();await page.locator('.pillar-name').first().waitFor();assert.equal(await page.locator('.pillar-name').count(),6);
  if(process.env.SP_SCREENSHOT_DIR){fs.mkdirSync(process.env.SP_SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.SP_SCREENSHOT_DIR,'strategic-plan-standard-desktop.png'),fullPage:true});}
  await page.goto(build(d,'populated'));
  assert.equal(await page.locator('.hero .word').textContent(),'Follow Through');
  assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()),'#f3c745');
  await page.locator('[data-to="fit-2030"]').click();
  assert.equal(await page.getByRole('dialog').getByRole('heading',{name:'Why this matters',exact:true}).count(),1);
  await page.getByRole('dialog').getByText('Reflection worksheet',{exact:true}).click();
  await page.getByRole('dialog').getByRole('button',{name:'Copy template',exact:true}).click();
  await page.waitForFunction(()=>/Copied|selected/.test(document.querySelector('.copy-status').textContent));
  await page.waitForFunction(()=>[...document.querySelectorAll('dialog .to-images img')].every(i=>i.complete&&i.naturalWidth>0));
  assert.equal(await page.evaluate(()=>window.worksheetInjected),undefined);
  assert.equal(await page.evaluate(()=>window.noteInjected),undefined);
  if(process.env.SP_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.SP_SCREENSHOT_DIR,'strategic-plan-synthetic-details.png')});
  await page.keyboard.press('Escape');
  await page.getByRole('link',{name:'Target Objectives',exact:true}).click();await page.getByRole('heading',{name:'Target Objectives (TOs)',exact:true}).waitFor();
  await page.getByRole('group',{name:'Filter by planning year'}).getByRole('button',{name:'2029',exact:true}).click();
  assert.equal(await page.locator('#year-select').inputValue(),'2029');
  assert.match(await page.locator('main').textContent(),/80 \/ 90/);
  await page.getByRole('group',{name:'Filter by planning year'}).getByRole('button',{name:'2030',exact:true}).click();
  assert.equal(await page.getByRole('combobox',{name:'Pillars'}).count(),1);
  await page.getByRole('link',{name:'Quarterly focus',exact:true}).click();await page.getByRole('heading',{name:'Focus on the next right results.',exact:true}).waitFor();
  assert.equal(await page.locator('.intro').getByText('Q1 locked',{exact:true}).count(),1);
  await page.getByRole('group',{name:'Filter by planning year'}).getByRole('button',{name:'2029',exact:true}).click();
  assert.equal(await page.locator('article.objective').count(),0);
  await page.getByRole('group',{name:'Filter by planning year'}).getByRole('button',{name:'2030',exact:true}).click();
  assert.equal(await page.locator('article.card').filter({has:page.getByRole('heading',{name:'Fit',exact:true})}).locator('.count').textContent(),'60%');
  await page.locator('#status-filter').selectOption('Done');
  assert.equal(await page.locator('article.objective').count(),1);assert.equal(await page.locator('article.card').filter({has:page.getByRole('heading',{name:'Fit',exact:true})}).locator('.count').textContent(),'60%');
  await page.getByRole('button',{name:'Explore TO →'}).click();
  await page.getByRole('dialog').waitFor();assert.match(await page.getByRole('dialog').textContent(),/Walk 100 miles/);
  assert.equal(await page.getByRole('dialog').getByRole('heading',{name:'Why this matters',exact:true}).count(),1);
  await page.keyboard.press('Escape');assert.equal(await page.getByRole('dialog').isVisible(),false);
  await page.locator('#status-filter').selectOption('');await page.locator('#quarter-select').selectOption('2');
  assert.equal(await page.locator('article.card').filter({has:page.getByRole('heading',{name:'Fit',exact:true})}).locator('.count').textContent(),'—');
  await page.getByRole('link',{name:'Year over year',exact:true}).click();await page.getByRole('heading',{name:'See how your direction evolves.',exact:true}).waitFor();assert.match(await page.locator('main').textContent(),/2029: 80 miles/);
  await page.locator('#year-select').selectOption('2029');await page.getByRole('link',{name:'Foundation',exact:true}).click();await page.getByRole('heading',{name:'Know what guides you.',exact:true}).waitFor();
  assert.equal(await page.locator('main').getByText('Present-day purpose',{exact:true}).count(),0);
  await page.locator('#year-select').selectOption('2030');await page.getByRole('link',{name:'Overview',exact:true}).click();await page.locator('.pillar-name').first().waitFor();
  if(process.env.SP_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.SP_SCREENSHOT_DIR,'strategic-plan-synthetic-brand.png'),fullPage:true});
  const deferred=structuredClone(d);deferred.years[0].objectives[1].measurement_review_state='deferred';deferred.years[0].quarter_reviews['1'].open_items=['Synthetic counting clarification'];
  await page.goto(build(deferred,'deferred')+'#quarter');
  assert.equal(await page.getByRole('region',{name:'Tracking details to finish'}).getByText('Synthetic counting clarification',{exact:true}).count(),1);
  assert.equal(await page.locator('article.card').filter({has:page.getByRole('heading',{name:'Fit',exact:true})}).locator('.count').textContent(),'—');
  assert.equal(await page.locator('.intro').getByText('Q1 locked',{exact:true}).count(),1);
  const decreasing=structuredClone(d);Object.assign(decreasing.years[0].objectives[0],{start:20,target:10,current:20});
  await page.goto(build(decreasing,'decreasing'));assert.equal(await page.getByText('-0% toward target',{exact:true}).count(),0);
  await page.goto(build(hostile,'hostile'));assert.equal(await page.evaluate(()=>window.injected),undefined);assert.equal(await page.locator('main img').count(),0);
  await page.goto(build(blank,'mobile'));await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.getByRole('link',{name:'Target Objectives',exact:true}).click();await page.getByRole('heading',{name:'Target Objectives (TOs)',exact:true}).waitFor();await page.getByRole('heading',{name:'Target Objectives (TOs)'}).waitFor();
  await page.getByRole('button',{name:'Update my view',exact:true}).click();await page.getByRole('dialog').waitFor();
  await page.keyboard.press('Escape');assert.equal(await page.getByRole('button',{name:'Update my view',exact:true}).evaluate(el=>el===document.activeElement),true);
  await page.getByRole('link',{name:'Overview',exact:true}).click();await page.locator('.pillar-name').first().waitFor();
  if(process.env.SP_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.SP_SCREENSHOT_DIR,'strategic-plan-standard-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
  console.log('Browser checks passed: blank/populated views, brand overrides, locks, independent definition review, weights/filters, context/images/worksheets, copy action, history, injection, mobile, keyboard, and offline.');
 } finally {if(browser)await browser.close();const relative=path.relative(testBase,path.resolve(tmp));if(!relative||relative.startsWith('..')||path.isAbsolute(relative))throw new Error('Unsafe cleanup path');fs.rmSync(tmp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
