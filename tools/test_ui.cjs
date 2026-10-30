'use strict';
// Dependency-free UI regression using actual reviewed arXiv content.
// Temporary test states are never saved as research data.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
const trial=JSON.parse(fs.readFileSync(path.join(root,'data/arxiv/2026-10-29.json')));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'data/issues.json')));
const original=JSON.parse(fs.readFileSync(path.join(root,'data/issues/2026-10-29.json')));
let response=trial;let fetchedPath='';
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/sources.json')));
const elements=new Map();
function element(selector){if(!elements.has(selector))elements.set(selector,{value:'',innerHTML:'',textContent:'',hidden:false,addEventListener(){},querySelectorAll(){return []}});return elements.get(selector);}
const panels=new Map();
const context=vm.createContext({console,URL,URLSearchParams,location:{href:'https://example.test/',search:''},history:{replaceState(){}},window:{addEventListener(){}},document:{querySelector:element,getElementById:id=>panels.get(id)},fetch:async url=>{fetchedPath=url;return {ok:true,json:async()=>structuredClone(response)}}});
let code=fs.readFileSync(path.join(root,'assets/app.js'),'utf8');
assert.ok(code.endsWith('init();\n'),'test harness must suppress only the final initialization');
code=code.slice(0,-'init();\n'.length);
vm.runInContext(code+'\nglobalThis.api={card,render,toggleSummary,overview,eligible,loadIssue,expandedPapers,setTaxonomy:x=>taxonomy=x,setIssue:x=>issue=x,setSources:x=>sources=x,setRefs:x=>issueRefs=new Map(x.map(i=>[i.date,i]))};',context);
const api=context.api;
api.setTaxonomy(JSON.parse(fs.readFileSync(path.join(root,'data/arxiv-taxonomy.json'))));
api.setRefs(manifest.issues);
assert.ok(!code.includes("$('#source')")&&!code.includes('source-counts'),'obsolete source UI removed');
api.setSources(Object.fromEntries(catalog.sources.map(s=>[s.id,s])));
api.setIssue(trial);
element('#issue-select').value=trial.date;
const paper=trial.papers[0];
let html=api.card(paper);
assert.match(html,/class="paper-title"[^>]+aria-expanded="false"/);
assert.match(html,/class="paper-summary"[^>]+ hidden>/);
assert.ok(html.includes(paper.result),'complete result remains available in the hidden summary');
assert.ok(html.includes(paper.method)&&html.includes(paper.limitations));
assert.match(html,/原始论文 ↗<\/a>/);
assert.doesNotMatch(html,/<h3><a/,'title must disclose the summary, not navigate away');
assert.equal(Array.from(api.overview({result:'界'.repeat(151)})).length,151);
assert.equal(api.overview({result:'原有结果'}),'原有结果');
assert.ok(!api.card({...paper,title_zh:'<img src=x onerror=alert(1)>',result:'<script>alert(1)</script>'}).includes('<script>'));
const controls=[{attrs:{'aria-expanded':'false','aria-controls':'test-panel'}},{attrs:{'aria-expanded':'false','aria-controls':'test-panel'}}];
const label={textContent:'展开总结'};
const article={id:paper.id,querySelectorAll:()=>controls,querySelector:()=>label};
controls.forEach(c=>{c.getAttribute=k=>c.attrs[k];c.setAttribute=(k,v)=>c.attrs[k]=v;c.closest=()=>article;});
const panel={hidden:true};panels.set('test-panel',panel);
function click(control){api.toggleSummary({target:{closest:()=>control}});}
for(let i=0;i<4;i++){
 click(controls[i%2]);const open=i%2===0;
 assert.equal(panel.hidden,!open);assert.equal(api.expandedPapers.has(paper.id),open);
 assert.ok(controls.every(c=>c.attrs['aria-expanded']===String(open)));
 assert.equal(label.textContent,open?'收起总结':'展开总结');
}
click(controls[0]);
api.render();assert.match(element('#results').innerHTML,/aria-expanded="true"/);
element('#search').value='no matching paper sentinel';api.render();assert.match(element('#results').innerHTML,/没有符合/);
element('#search').value='';element('#arxiv-group').value=paper.arxiv_group;element('#category').value=paper.canonical_primary_category;element('#depth').value=paper.reading_depth;api.render();
assert.ok(element('#results').innerHTML.includes(`id="${paper.id}"`));assert.match(element('#results').innerHTML,/aria-expanded="true"/);
assert.equal(element('#results-heading').textContent,'按 arXiv 主分类浏览');
for(const id of ['search','arxiv-group','category','depth'])element('#'+id).value='';api.render();
assert.equal((element('#results').innerHTML.match(/class="paper-card"/g)||[]).length,trial.papers.length);
assert.ok(api.eligible(paper),'actual reviewed arxiv paper qualifies');
assert.equal((element('#results').innerHTML.match(/class="arxiv-category"/g)||[]).length,34);
assert.equal((element('#results').innerHTML.match(/class="arxiv-group"/g)||[]).length,3);
for(const [group,category,count] of [['cs','cs.CR',12],['physics','math-ph',2]]){
 element('#arxiv-group').value=group;element('#category').value=category;api.render();
 assert.equal((element('#results').innerHTML.match(/class="paper-card"/g)||[]).length,count);
 assert.ok(element('#results').innerHTML.includes(`data-arxiv-group="${group}"`));
}
for(const id of ['arxiv-group','category'])element('#'+id).value='';api.render();
assert.ok(!code.includes('p.domains')&&!code.includes('p.subfields')&&!code.includes('p.keywords'));

// Pending entries remain a distinct filtered list and never inflate confirmed counts.
api.setIssue({...trial,papers:trial.papers.slice(1),pending_papers:[{...paper,eligibility:'pending'}]});
api.render();
assert.ok(element('#count').textContent.includes(`${trial.papers.length-1} / ${trial.papers.length-1} 篇 arXiv 论文`));
assert.match(element('#pending-count').textContent,/1 \/ 1 篇时间待核实/);
assert.equal(element('#pending-section').hidden,false);
assert.match(element('#pending-results').innerHTML,/时间待核实 · 不计入当日新增/);
assert.ok(!element('#results').innerHTML.includes(`id="${paper.id}"`));
element('#search').value='no matching paper sentinel';api.render();
assert.match(element('#pending-count').textContent,/0 \/ 1/);
element('#search').value='';api.render();
assert.match(element('#pending-results').innerHTML,/aria-expanded="true"/);

(async()=>{
 response={...trial,papers:[...trial.papers,original.papers.find(p=>p.source!=='arxiv')],pending_papers:original.pending_papers};
 await api.loadIssue(trial.date);
 assert.equal(fetchedPath,manifest.issues[0].path,'load indexed arxiv path, never hardcoded legacy path');
 assert.equal(api.expandedPapers.size,0,'date loading resets expansion');
 assert.equal((element('#results').innerHTML.match(/class="paper-card"/g)||[]).length,trial.papers.length,'non-arxiv data is defensively excluded');
 assert.equal(element('#pending-section').hidden,true,'foreign pending entries cannot leak into current view');
 assert.equal(element('#markdown-link').href,'reports/arxiv/2026-10-29.md');
 assert.equal(element('#retrieval-link').href,'data/retrieval/arxiv/2026-10-29.json');
 assert.ok(element('#issue-meta').innerHTML.includes(`${trial.papers.length} 篇 arXiv 论文`));
 const before=fetchedPath;await api.loadIssue('1900-01-01');assert.equal(fetchedPath,before,'unknown dates are not fetched');assert.match(element('#results').innerHTML,/不在 arXiv 日报索引/);
 console.log('PASS: arXiv-only selected set, indexed data/download paths, defensive scope guard, collapsed summaries, repeated toggles, escaping, filters/reset/state and unknown-date guard.');
})().catch(e=>{console.error(e);process.exitCode=1;});
