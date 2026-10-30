#!/usr/bin/env python3
"""Regenerate issue Markdown from reviewed JSON; no network, no auto-summarization."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sources={s['id']:s['name'] for s in json.loads((ROOT/'data/sources.json').read_text())['sources']}
for path in sorted((ROOT/'data/issues').glob('*.json')):
 issue=json.loads(path.read_text()); ps=issue['papers']; lines=[f"# 学术论文日报｜{issue['date']}",'',f"检索窗口：{issue['window_start']} 至 {issue['window_end']}。本期为重建首期，回看近期资料；后续按来源增量。",'',f"收录 **{len(ps)} 篇**，按来源与领域双重分类。是经过筛选的日报，不是全量论文清单。所有研究结论按作者主张转述；局部正文阅读不等于完整证明复核。",'', '## 来源与覆盖','', '| 来源 | 本期状态 | 实际范围与局限 |','|---|---|---|']
 for c in issue['coverage']:lines.append(f"| [{c['name']}]({c['url']}) | {c['status']} | {c['scope']} {c['note']} |")
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
   if p.get('date_note'):lines.append('- **日期说明：** '+p['date_note'])
   if p.get('change_note'):lines.append('- **版本变化：** '+p['change_note'])
   refs=list(dict.fromkeys(p.get('evidence_urls',[])+p.get('affiliation_sources',[])))
   lines+=['','**原始证据：** '+'；'.join(f'[来源{i+1}]({u})' for i,u in enumerate(refs)),'']
 lines+=['## 编辑规范','', '- 客观呈现公开研究，不做个人研究相关性评价。','- 作者机构以论文署名为准，不据同名、声誉或猜测补职位与经历。','- 预印本、技术报告与正式发表分开；没有具体版本证据时标注未核。','- 不转载全文，不将摘要解读为独立安全背书、证明审计或性能复现。','- 保存历史日报；更正保留版本与更正说明，不悄悄覆盖历史结论。','']
 (ROOT/'reports'/f"{issue['date']}.md").write_text('\n'.join(lines))
