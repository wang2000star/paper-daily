'use strict';
// Dependency-free regression checks. Historical papers are rendering fixtures only;
// they are never added to the formal index or given fabricated review evidence.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
const trial=JSON.parse(fs.readFileSync(path.join(root,'data/trials/2026-10-30.json')));
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/sources.json')));
const elements=new Map();
function element(selector){if(!elements.has(selector))elements.set(selector,{value:'',innerHTML:'',textContent:'',hidden:false,addEventListener(){},querySelectorAll(){return []}});return elements.get(selector);}
const panels=new Map();
const context=vm.createContext({console,URL,URLSearchParams,location:{href:'https://example.test/',search:''},history:{replaceState(){}},window:{addEventListener(){}},document:{querySelector:element,getElementById:id=>panels.get(id)},fetch:async()=>({ok:true,json:async()=>structuredClone(trial)})});
let code=fs.readFileSync(path.join(root,'assets/app.js'),'utf8');
assert.ok(code.endsWith('init();\n'),'test harness must suppress only the final initialization');
code=code.slice(0,-'init();\n'.length);
vm.runInContext(code+'\nglobalThis.api={sourceCounts,sourceCountLabel,renderSourceSummary,card,render,toggleSummary,overview,eligible,loadIssue,expandedPapers,setIssue:x=>issue=x,setSources:x=>sources=x};',context);
const api=context.api;
// Metadata-only fixtures verify overlapping confirmed/pending sources without paper claims.
const rows=api.sourceCounts({papers:[{source:'arxiv'},{source:'arxiv'},{source:'eccc'}],pending_papers:[{source:'openai-research'},{source:'arxiv'}]});
assert.equal(rows.filter(row=>row.confirmed>0).length,2,'pending-only sources do not inflate confirmed-source count');
assert.equal(rows.filter(row=>row.confirmed===0&&row.pending>0).length,1);
assert.equal(api.sourceCountLabel(rows.find(row=>row.id==='openai-research')),'确认 0 / 待核实 1');
assert.equal(api.sourceCountLabel(rows.find(row=>row.id==='arxiv')),'确认 2 / 待核实 1');
api.renderSourceSummary(rows);assert.match(element('#source-counts').innerHTML,/确认 0 \/ 待核实 1/);
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
element('#search').value='';element('#source').value=paper.source;element('#domain').value=paper.domains[0];element('#subfield').value=paper.subfields[0];element('#depth').value=paper.reading_depth;api.render();
assert.ok(element('#results').innerHTML.includes(`id="${paper.id}"`));assert.match(element('#results').innerHTML,/aria-expanded="true"/);
element('#group').value='source';api.render();assert.equal(element('#results-heading').textContent,'按来源浏览');
for(const id of ['search','source','domain','subfield','depth','group'])element('#'+id).value='';api.render();
assert.equal((element('#results').innerHTML.match(/class="paper-card"/g)||[]).length,trial.papers.length);
assert.ok(!api.eligible(paper),'historical fixture must not acquire fabricated review eligibility');
// Pending entries remain a distinct filtered list and never inflate confirmed counts.
api.setIssue({...trial,papers:trial.papers.slice(1),pending_papers:[{...paper,eligibility:'pending'}]});
api.render();
assert.match(element('#count').textContent,/22 \/ 22 篇确认新增/);
assert.match(element('#pending-count').textContent,/1 \/ 1 篇时间待核实/);
assert.equal(element('#pending-section').hidden,false);
assert.match(element('#pending-results').innerHTML,/时间待核实 · 不计入当日新增/);
assert.ok(!element('#results').innerHTML.includes(`id="${paper.id}"`));
element('#search').value='no matching paper sentinel';api.render();
assert.match(element('#pending-count').textContent,/0 \/ 1/);
element('#search').value='';api.render();
assert.match(element('#pending-results').innerHTML,/aria-expanded="true"/);

(async()=>{await api.loadIssue(trial.date);assert.equal(api.expandedPapers.size,0,'date loading resets expansion');assert.match(element('#results').innerHTML,/没有符合/,'ineligible trial entries stay excluded');console.log('PASS: collapsed markup, full summary preservation, escaping, title/link separation, repeated synchronized toggles, filtering, grouping, clearing, state retention and date reset.');})().catch(e=>{console.error(e);process.exitCode=1;});
