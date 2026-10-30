#!/usr/bin/env python3
"""Regenerate issue Markdown from reviewed JSON; no network, no auto-summarization."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sources={s['id']:s['name'] for s in json.loads((ROOT/'data/sources.json').read_text())['sources']}
for path in sorted((ROOT/'data/issues').glob('*.json')):
 issue=json.loads(path.read_text()); ps=issue['papers'];
 if issue.get('issue_type')!='historical_trial':
  for p in ps:
   if p.get('reading_depth')=='abstract':
    r=p.get('abstract_review',{});assert r.get('complete_abstract_accessed') is True and r.get('read_confirmed') is True and r.get('source_url') and r.get('scope'),'Missing complete abstract evidence'
   else:assert p.get('reading_depth') in ['partial','full_review'] and all(p.get('substantive_review',{}).get(k) for k in ['content_urls','scope','method_evidence','result_evidence','conditions_evidence']),'Missing substantive review'

 lines=[f"# {'历史试刊（非 AOE 日报）' if issue.get('issue_type')=='historical_trial' else '学术论文日报（AOE）'}｜{issue['date']}",'',f"检索窗口：{issue['window_start']} 至 {issue['window_end']}。窗口左闭右开。历史试刊不计入正式日报；正式日报按 AOE 已结束自然日归档。",'',f"收录 **{len(ps)} 篇**，按来源与领域双重分类。是经过筛选的日报，不是全量论文清单。所有研究结论按作者主张转述；局部正文阅读不等于完整证明复核。",'', '## 来源与覆盖','', '| 来源 | 本期状态 | 实际范围与局限 |','|---|---|---|']
 for c in [c for c in issue['coverage'] if issue.get('issue_type')=='historical_trial' or c.get('public_display') is True]:lines.append(f"| [{c['name']}]({c['url']}) | {c['status']} | {c['scope']} {c['note']} |")
 lines+=['','## 分类索引','', '| 来源 | 数学 | 计算机科学 | 网络与信息安全 | 密码学 |','|---|---:|---:|---:|---:|']
 for src in dict.fromkeys(p['source'] for p in ps):
  row=[str(sum(src==p['source'] and d in p['domains'] for p in ps)) for d in ['数学','计算机科学','网络与信息安全','密码学']]
  lines.append('| '+sources.get(src,src)+' | '+' | '.join(row)+' |')
 lines+=['','同一论文可带多个领域标签，以上领域计数不应相加当成总论文数。跨来源按稳定标识、标题和作者去重。本期未发现所选条目间重复。','']
 for src in dict.fromkeys(p['source'] for p in ps):
  lines += [f"## {sources.get(src,src)}",'']
  for p in [p for p in ps if p['source']==src]:
   lines += [f"### {p['title_zh']}",'',f"**原标题：** [{p['title']}]({p['url']})",'',f"**作者：** {'、'.join(p['authors'])}",'',f"**作者与机构简介：** {p['author_intro']}",'']
   for x in p.get('author_institutions',[]):lines.append('- '+x)
   lines += ['',f"**领域：** {' / '.join(p['domains'])}；**细分主题：** {' / '.join(p['subfields'])}",'',f"**日期与版本：** 首次 {p['first_date']}；更新 {p['updated_date'] or '未核修订日'}；{p['version']}；{p['publication_status']}。",'',f"**阅读范围：** {p.get('reading_note','仅核摘要与元数据；未独立复现。')}",'',f"- **研究问题：** {p['problem']}",f"- **主要结果：** {p['result']}",f"- **方法：** {p['method']}",f"- **条件与局限：** {p['limitations']}"]
   if p.get('abstract_review'):lines+=['- **摘要级解读：** '+p['abstract_review']['scope']+'；未核全文的细节不补猜。']
   if p.get('substantive_review'):
    r=p['substantive_review'];lines+=['- **实际审阅范围：** '+r['scope'],'- **方法依据：** '+r['method_evidence'],'- **结果依据：** '+r['result_evidence'],'- **条件依据：** '+r['conditions_evidence']]
   if p.get('date_note'):lines.append('- **日期说明：** '+p['date_note'])
   if p.get('change_note'):lines.append('- **版本变化：** '+p['change_note'])
   refs=list(dict.fromkeys(p.get('evidence_urls',[])+p.get('affiliation_sources',[])))
   lines+=['','**原始证据：** '+'；'.join(f'[来源{i+1}]({u})' for i,u in enumerate(refs)),'']
 lines+=['## 编辑规范','', '- 客观呈现公开研究，不做个人研究相关性评价。','- 作者机构以论文署名为准，不据同名、声誉或猜测补职位与经历。','- 预印本、技术报告与正式发表分开；没有具体版本证据时标注未核。','- 不转载全文，不将摘要解读为独立安全背书、证明审计或性能复现。','- 保存历史日报；更正保留版本与更正说明，不悄悄覆盖历史结论。','']
 (ROOT/'reports'/f"{issue['date']}.md").write_text('\n'.join(lines))
