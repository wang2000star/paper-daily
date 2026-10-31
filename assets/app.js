'use strict';
const $=s=>document.querySelector(s);
let taxonomy={groups:{},archives:{},category_catalog:{}};
const contentTypes={paper:'论文 / 预印本',research_blog:'研究博客',technical_report:'技术报告',research_code:'研究代码',model_release:'模型技术发布'};
const timePrecisions={second:'来源秒级时间戳',minute:'来源分钟级时间戳',date:'仅日期',day:'仅日期',rss_batch_timestamp:'RSS 公告批次时间',scheduled_batch:'计划公告批次',unknown:'精度待核实'};
let issue=null, sources={}, issueRefs=new Map(), request=0;
const expandedPapers=new Set();
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeURL=s=>{try{const u=new URL(s,location.href);return ['https:','http:'].includes(u.protocol)?esc(u.href):'#';}catch{return '#';}};
const list=a=>Array.isArray(a)?a:[];
function options(el,values,all){const old=el.value;el.innerHTML=`<option value="">${all}</option>`+values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');if(values.includes(old))el.value=old;}
function eligible(p){if(p.reading_depth==='abstract'){const r=p.abstract_review;return Boolean(p.title&&r&&/^https:\/\//.test(r.source_url||'')&&r.complete_abstract_accessed===true&&r.read_confirmed===true&&typeof r.scope==='string'&&r.scope.trim());}const r=p.substantive_review;return ['partial','full_review'].includes(p.reading_depth)&&r&&Array.isArray(r.content_urls)&&r.content_urls.length>0&&['scope','method_evidence','result_evidence','conditions_evidence'].every(k=>typeof r[k]==='string'&&r[k].trim().length>0);}
function depth(p){return p.reading_depth==='full_review'?'full_review':p.reading_depth==='partial'?'partial':'abstract';}
function overview(p){const text=String(p.overview||p.result||p.problem||'').trim();const chars=Array.from(text);return chars.length>150?chars.slice(0,150).join('')+'…':text;}
function categoryInfo(code){return taxonomy.category_catalog[code]||{code,name:code};}
function canonicalCategory(code){return categoryInfo(code).canonical_code||code;}
function groupLabel(id){const g=taxonomy.groups[id];return g?`${g.name_zh||g.name} · ${g.name}`:id;}
function categoryLabel(code){const c=categoryInfo(code);return `${code} · ${c.name_zh?c.name_zh+' / ':''}${c.name}`;}
function categoryShort(code){const c=categoryInfo(code);return `${code} · ${c.name_zh||c.name}`;}
function classified(p){const c=categoryInfo(p.primary_category);return Boolean(c.canonical_code&&p.canonical_primary_category===c.canonical_code&&p.arxiv_group===c.canonical_group&&list(p.arxiv_categories).every(x=>taxonomy.category_catalog[x]));}
function selectOptions(el,rows,all){const old=el.value;el.innerHTML=`<option value="">${all}</option>`+rows.map(r=>`<option value="${esc(r.value)}">${esc(r.label)}</option>`).join('');el.value=rows.some(r=>r.value===old)?old:'';}
function categoryOptions(){if(!issue)return;const ps=[...issue.papers,...issue.pending_papers].filter(p=>!$('#arxiv-group').value||p.arxiv_group===$('#arxiv-group').value);selectOptions($('#category'),[...new Set(ps.map(p=>p.canonical_primary_category))].sort().map(value=>({value,label:categoryLabel(value)})),'全部主分类');}
function card(p){
 const title=p.title_zh||p.title, expanded=expandedPapers.has(p.id), panelID=`paper-summary-${p.id}`, titleID=`paper-title-${p.id}`;
 const review=p.substantive_review, abstract=p.abstract_review;
 return `<article class="paper-card" id="${esc(p.id)}"><div class="badges"><span class="badge source">${esc(sources[p.source]?.name||p.source)}</span><span class="badge">${esc(p.publication_status)}</span>${p.content_type?`<span class="badge">${esc(contentTypes[p.content_type]||p.content_type)}</span>`:''}${p.eligibility==='pending'?'<span class="badge pending">时间待核实 · 不计入当日新增</span>':''}<span class="badge depth">${depth(p)==='full_review'?'正文审阅（范围见说明）':depth(p)==='partial'?'核心内容局部审阅':'摘要级解读'}</span><span class="badge primary-category" title="${esc(categoryLabel(p.primary_category))}">主分类：${esc(categoryShort(p.primary_category))}</span>${list(p.cross_categories).map(code=>`<span class="badge cross-category" title="${esc(categoryLabel(code))}">交叉：${esc(categoryShort(code))}</span>`).join('')}</div>
 <h4><button class="paper-title" id="${esc(titleID)}" type="button" data-paper-toggle aria-expanded="${expanded}" aria-controls="${esc(panelID)}">${esc(title)}</button></h4>
 ${p.title_zh&&p.title_zh!==p.title?`<p class="original-title">${esc(p.title)}</p>`:''}
 <p class="paper-overview"><strong>概览</strong> ${esc(overview(p))}</p>
 ${p.why_selected?`<p class="selection-reason paper-overview"><strong>入选理由（据论文所述贡献）</strong> ${esc(p.why_selected)}</p>`:''}
 <button class="summary-toggle" type="button" data-paper-toggle aria-expanded="${expanded}" aria-controls="${esc(panelID)}"><span class="toggle-label">${expanded?'收起总结':'展开总结'}</span><span class="toggle-chevron" aria-hidden="true">⌄</span><span class="sr-only">：${esc(title)}</span></button>
 <div class="paper-summary" id="${esc(panelID)}" role="region" aria-labelledby="${esc(titleID)}"${expanded?'':' hidden'}>
 <p class="authors"><strong>作者</strong> ${esc(list(p.authors).join(' · '))}</p><p class="authors">${esc(p.author_intro||'作者及机构信息待核实')}</p>
 <p class="dates">首次：${esc(p.first_date||'未核实')} · 更新：${esc(p.updated_date||'未核修订日')} · 版本：${esc(p.version||'未核实')}${p.announcement_date?' · 公告：'+esc(p.announcement_date):''}</p>
 <dl>${p.public_time_source?`<dt>公开时间</dt><dd>${esc(p.public_at||'未确认精确时间')}（${esc(timePrecisions[p.public_time_precision]||p.public_time_precision||'精度未确认')}）${p.public_time_range?`；已证实区间：${esc(p.public_time_range.start)} 至 ${esc(p.public_time_range.end)}`:''} · <a href="${safeURL(p.public_time_source)}">时间证据</a>${p.date_note?`<p class="detail-note">${esc(p.date_note)}</p>`:''}</dd>`:''}<dt>研究问题</dt><dd>${esc(p.problem)}</dd><dt>作者报告的结果</dt><dd>${esc(p.result)}</dd><dt>方法</dt><dd>${esc(p.method)}</dd><dt>条件与局限</dt><dd>${esc(p.limitations)}</dd>
 ${review?`<dt>实际审阅范围</dt><dd>${esc(review.scope)}</dd>${[['method_evidence','方法依据'],['result_evidence','结果依据'],['conditions_evidence','条件依据']].filter(([key])=>review[key]).map(([key,label])=>`<dt>${label}</dt><dd>${esc(review[key])}</dd>`).join('')}`:abstract?`<dt>摘要阅读范围</dt><dd>${esc(abstract.scope)} · 仅据完整摘要/实质研究概述解读，不表示已核验全文。</dd>`:''}
 ${p.pending_reason?`<dt>待核实原因</dt><dd>${esc(p.pending_reason)}</dd>`:''}
 ${list(p.discovered_via).length?`<dt>发现入口（非发布来源）</dt><dd>${p.discovered_via.map(d=>`<a href="${safeURL(d.record_url)}">${esc(d.method==='publisher_search'?'出版方检索':d.index_id)}</a>`).join(' · ')}</dd>`:''}
 ${p.selection_evidence_limit?`<dt>筛选依据的边界</dt><dd>${esc(p.selection_evidence_limit)}</dd>`:''}
 ${p.reading_note?`<dt>阅读说明</dt><dd>${esc(p.reading_note)}</dd>`:''}
 <dt>作者与机构</dt><dd>${esc(Array.isArray(p.author_institutions)?p.author_institutions.join('；'):(p.author_institutions||'待核实'))}${p.affiliation_note?`<p class="detail-note">${esc(p.affiliation_note)}</p>`:''}</dd>
 ${p.date_note&&!p.public_time_source?`<dt>日期说明</dt><dd>${esc(p.date_note)}</dd>`:''}${p.change_note?`<dt>版本变化</dt><dd>${esc(p.change_note)}</dd>`:''}<dt>arXiv 主分类</dt><dd>${esc(groupLabel(p.arxiv_group))} / ${esc(categoryLabel(p.primary_category))}${p.primary_category!==p.canonical_primary_category?'（官方别名对应 '+esc(p.canonical_primary_category)+'）':''}</dd>${list(p.cross_categories).length?`<dt>交叉分类</dt><dd>${p.cross_categories.map(c=>esc(categoryLabel(c))).join('；')}</dd>`:''}</dl></div>
 <div class="paper-links"><a href="${safeURL(p.url)}">${p.content_type==='research_blog'?'原始研究':'原始论文'} ↗</a>${list(p.evidence_urls).filter(u=>u!==p.url).slice(0,2).map((u,i)=>`<a href="${safeURL(u)}">${i===0?'补充来源':'其他来源'} ↗</a>`).join('')}${p.code_url?`<a href="${safeURL(p.code_url)}">代码 ↗</a>`:''}</div></article>`;
}
function toggleSummary(event){
 const button=event.target.closest('[data-paper-toggle]');if(!button)return;
 const article=button.closest('.paper-card'), panel=document.getElementById(button.getAttribute('aria-controls'));
 if(!article||!panel)return;
 const expanded=button.getAttribute('aria-expanded')!=='true';
 if(expanded)expandedPapers.add(article.id);else expandedPapers.delete(article.id);
 panel.hidden=!expanded;
 article.querySelectorAll('[data-paper-toggle]').forEach(control=>control.setAttribute('aria-expanded',String(expanded)));
 article.querySelector('.toggle-label').textContent=expanded?'收起总结':'展开总结';
}
function syncURL(){const q=new URLSearchParams();q.set('date',$('#issue-select').value);for(const id of ['arxiv-group','category','depth','search'])if($('#'+id).value)q.set(id,$('#'+id).value);history.replaceState(null,'','?'+q.toString());}
function render(){
 if(!issue)return;
 const q=$('#search').value.trim().toLowerCase();
 const matches=p=>(!$('#arxiv-group').value||p.arxiv_group===$('#arxiv-group').value)&&(!$('#category').value||p.canonical_primary_category===$('#category').value)&&(!$('#depth').value||depth(p)===$('#depth').value)&&(!q||[p.title,p.title_zh,...list(p.authors),...list(p.arxiv_categories).map(categoryLabel),p.problem,p.result].join(' ').toLowerCase().includes(q));
 const filtered=issue.papers.filter(matches),pending=list(issue.pending_papers).filter(matches);
 function sections(papers){if(!papers.length)return '<p class="empty">没有符合这些筛选条件的论文。请调整条件或清除筛选。</p>';return Object.keys(taxonomy.groups).filter(g=>papers.some(p=>p.arxiv_group===g)).map(g=>{const ps=papers.filter(p=>p.arxiv_group===g),codes=[...new Set(ps.map(p=>p.canonical_primary_category))].sort();return `<section class="arxiv-group" data-arxiv-group="${esc(g)}" aria-label="${esc(groupLabel(g))}"><h2 class="group-heading">${esc(groupLabel(g))} <small>${ps.length}</small></h2>${codes.map(code=>{const rows=ps.filter(p=>p.canonical_primary_category===code),archive=rows[0].arxiv_archive,archiveName=taxonomy.archives[archive]?.name;return `<section class="arxiv-category" data-arxiv-category="${esc(code)}" data-arxiv-archive="${esc(archive)}" aria-label="${esc(categoryLabel(code))}">${g==='physics'&&archiveName&&archive!==code?`<p class="archive-label">${esc(archiveName)}</p>`:''}<h3 class="category-heading">${esc(categoryLabel(code))} <small>${rows.length}</small></h3>${rows.map(card).join('')}</section>`;}).join('')}</section>`;}).join('');}
 $('#results-heading').textContent='按 arXiv 主分类浏览';
 $('#count').textContent=`显示 ${filtered.length} / ${issue.papers.length} 篇 arXiv 论文（确认新增，去重后）`;
 const emptyIssue=issue.screening?.status!=='complete'?'本期检索或摘要初筛尚未完成。':issue.screening.candidate_count===0?'本期未确认新增论文。':'本期暂无入选论文。';
 $('#results').innerHTML=issue.papers.length?sections(filtered):`<p class="empty">${emptyIssue}</p>`;
 $('#pending-section').hidden=!list(issue.pending_papers).length;
 $('#pending-count').textContent=`显示 ${pending.length} / ${list(issue.pending_papers).length} 篇时间待核实；不计入确认新增`;
 $('#pending-results').innerHTML=sections(pending);syncURL();
}
async function loadIssue(date,initial=false){
 const token=++request;$('#results').innerHTML='<p>正在读取日报…</p>';$('#pending-section').hidden=true;$('#pending-results').innerHTML='';
 try{
  const ref=issueRefs.get(date);if(!ref)throw Error('该日期不在 arXiv 日报索引中');
  const res=await fetch(ref.path);if(!res.ok)throw Error('日报文件暂时不可用');const data=await res.json();if(token!==request)return;
  if(data.source_scope!=='arxiv_only'||data.date!==date)throw Error('日报范围或日期不匹配');
  issue={...data,papers:list(data.papers).filter(p=>p.source==='arxiv'&&classified(p)&&eligible(p)&&p.eligibility==='confirmed'),pending_papers:list(data.pending_papers).filter(p=>p.source==='arxiv'&&classified(p)&&eligible(p)&&p.eligibility==='pending')};expandedPapers.clear();
  const allPapers=[...issue.papers,...issue.pending_papers];$('#issue-editorial').textContent=issue.editorial_note||'';$('#issue-editorial').hidden=!issue.editorial_note;
  $('#issue-meta').innerHTML=`<span class="meta-pill">${esc(issue.date)}</span><span class="meta-pill">${issue.papers.length} 篇 arXiv 论文</span>${issue.pending_papers.length?`<span class="meta-pill">${issue.pending_papers.length} 篇时间待核实</span>`:''}<span class="meta-pill">${esc(issue.window_label)}</span>`;
  selectOptions($('#arxiv-group'),Object.keys(taxonomy.groups).filter(g=>allPapers.some(p=>p.arxiv_group===g)).map(value=>({value,label:groupLabel(value)})),'全部学科组');categoryOptions();
  $('#markdown-link').href=ref.report;$('#retrieval-link').href=issue.retrieval_log;
  $('#coverage-list').innerHTML=list(issue.coverage).filter(c=>c.id==='arxiv'&&c.public_display===true).map(c=>`<div class="coverage-item"><div><strong><a href="${safeURL(c.url)}">arXiv</a></strong><span class="state">${esc(c.status)}</span></div><div><p>${esc(c.scope)}</p><p>${esc(c.note)}</p></div></div>`).join('');
  if(initial){const qs=new URLSearchParams(location.search);for(const id of ['arxiv-group','category','depth','search'])if(qs.has(id))$('#'+id).value=qs.get(id);categoryOptions();}
  render();
 }catch(e){if(token===request){issue=null;$('#results').innerHTML=`<p class="error">${esc(e.message)}。请刷新重试，或通过 GitHub reports/arxiv 目录阅读日报。</p>`;$('#count').textContent='加载失败';}}
}
async function init(){
 try{
  const [ir,sr,tr]=await Promise.all([fetch('data/issues.json'),fetch('data/sources.json'),fetch('data/arxiv-taxonomy.json')]);if(!ir.ok||!sr.ok||!tr.ok)throw Error('目录加载失败');const manifest=await ir.json(),catalog=await sr.json();taxonomy=await tr.json();
  if(manifest.source_scope!=='arxiv_only')throw Error('日报索引范围不匹配');
  sources=Object.fromEntries(catalog.sources.filter(s=>s.id==='arxiv').map(s=>[s.id,s]));issueRefs=new Map(manifest.issues.map(i=>[i.date,i]));
  $('#issue-select').innerHTML=manifest.issues.map(i=>`<option value="${esc(i.date)}">${esc(i.date)}${i.kind?' · '+esc(i.kind):''}</option>`).join('');
  if(!manifest.issues.length){$('#issue-select').innerHTML='<option>暂无已发布日报</option>';$('.controls').hidden=true;$('#issue-meta').textContent='AOE（UTC−12）每日 24:00 更新 · 北京时间次日 20:00';$('#results').innerHTML='<p class="empty">暂无已结束窗口的 arXiv 日报。</p>';$('#markdown-link').hidden=true;$('#retrieval-link').hidden=true;return;}
  const wanted=new URLSearchParams(location.search).get('date');$('#issue-select').value=issueRefs.has(wanted)?wanted:manifest.latest;await loadIssue($('#issue-select').value,true);
 }catch(e){$('#results').innerHTML=`<p class="error">${esc(e.message)}。请稍后刷新或查看 GitHub 归档。</p>`;$('#issue-meta').textContent='暂时无法读取日报';}
}
$('#results').addEventListener('click',toggleSummary);$('#pending-results').addEventListener('click',toggleSummary);
$('#arxiv-group').addEventListener('change',()=>{categoryOptions();render();});for(const id of ['category','depth'])$('#'+id).addEventListener('change',render);$('#search').addEventListener('input',render);$('#issue-select').addEventListener('change',()=>loadIssue($('#issue-select').value));$('#reset').addEventListener('click',()=>{for(const id of ['arxiv-group','category','depth','search'])$('#'+id).value='';categoryOptions();render();});window.addEventListener('popstate',()=>location.reload());init();
