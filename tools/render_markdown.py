#!/usr/bin/env python3
"""Render formal reviewed issues only; preserve historical trial reports verbatim."""
import json
from pathlib import Path
from validate import validate_review
ROOT=Path(__file__).resolve().parents[1]
DOMAINS=['数学','计算机科学','网络与信息安全','密码学']
def render_paper(p):
 lines=[f"### {p['title_zh']}",'',f"**原标题：** [{p['title']}]({p['url']})",'',f"**作者：** {'、'.join(p['authors'])}",'',f"**作者与机构简介：** {p['author_intro']}",'']
 lines += ['- '+x for x in p.get('author_institutions',[])]
 lines += ['',f"**领域：** {' / '.join(p['domains'])}；**细分主题：** {' / '.join(p['subfields'])}",'',f"**日期与版本：** 首次记录 {p['first_date'] or '未核实'}；更新 {p['updated_date'] or '未核修订日'}；{p['version']}；{p['publication_status']}。",'',f"**已核来源公开时间：** {p.get('public_at') or '精确时间未确认'}（精度：{p['public_time_precision']}）；[时间证据]({p['public_time_source']})。"]
 if p.get('public_time_range'):
  r=p['public_time_range'];lines += [f"**已证实时间区间：** [{r['start']}, {r['end']})。"]
 if p.get('date_note'):lines+=['**日期说明：** '+p['date_note']]
 if p['eligibility']=='pending':lines+=['**时间待核实：不计入本期确认新增。**',p.get('pending_reason','')]
 if p.get('discovered_via'):lines+=['**发现入口（非发布来源）：** '+'；'.join(f"[{d.get('method',d['index_id'])}]({d['record_url']})" for d in p['discovered_via'])]
 label={'abstract':'摘要级解读','partial':'核心内容局部审阅','full_review':'正文审阅（范围见说明）'}[p['reading_depth']]
 lines += ['',f"**阅读深度：** {label}。{p.get('reading_note','未独立复现或核验完整证明。')}",'',f"- **研究问题：** {p['problem']}",f"- **主要结果：** {p['result']}",f"- **方法：** {p['method']}",f"- **条件与局限：** {p['limitations']}"]
 if p.get('abstract_review'):
  r=p['abstract_review'];lines+=['- **摘要/实质概述实际阅读范围：** '+r['scope']+'；未核全文的细节不补猜。']
 if p.get('substantive_review'):
  r=p['substantive_review'];lines+=['- **实际审阅范围：** '+r['scope'],'- **方法依据：** '+r['method_evidence'],'- **结果依据：** '+r['result_evidence'],'- **条件依据：** '+r['conditions_evidence']]
 if p.get('change_note'):lines+=['- **版本变化：** '+p['change_note']]
 if p.get('affiliation_note'):lines+=['- **机构核验说明：** '+p['affiliation_note']]
 refs=list(dict.fromkeys(p.get('evidence_urls',[])+p.get('affiliation_sources',[])+[p['public_time_source']]))
 lines+=['','**原始证据：** '+'；'.join(f'[来源{i+1}]({u})' for i,u in enumerate(refs)),'']
 return lines
def render(issue,sources):
 ps=issue['papers'];pending=issue.get('pending_papers',[])
 for p in ps+pending:validate_review(p)
 lines=[f"# 学术论文日报（AOE）｜{issue['date']}",'',f"检索窗口：{issue['window_start']} 至 {issue['window_end']}，左闭右开。AOE（UTC−12）已结束自然日。",'',f"**确认新增 {len(ps)} 篇；时间待核实 {len(pending)} 篇（另列，不计入新增）。**",'', '**实际覆盖范围：** '+issue['editorial_note'],'','研究结论按原作者主张转述；摘要或局部正文阅读不等于完整证明审计、性能复现或安全背书。','','## 发布来源与实际覆盖','', '| 来源 | 本期状态 | 实际范围与局限 |','|---|---|---|']
 for c in issue['coverage']:
  if c.get('public_display') is True:
   row=f"| [{c['name']}]({c['url']}) | {c['status']} | {c['scope']} {c['note']} |";lines.append(row.replace('\n',' '))
 lines+=['',f"完整检索记录与未读/未通过条目仅存于 [检索归档](../{issue['retrieval_log']})；不作为论文卡片或已覆盖声明。",'', '## 确认新增：来源与领域索引','', '| 来源 | 数学 | 计算机科学 | 网络与信息安全 | 密码学 |','|---|---:|---:|---:|---:|']
 for src in dict.fromkeys(p['source'] for p in ps):
  row=[str(sum(src==p['source'] and d in p['domains'] for p in ps)) for d in DOMAINS]
  lines.append('| '+sources.get(src,src)+' | '+' | '.join(row)+' |')
 lines+=['',f"确认收录来源 {len(set(p['source'] for p in ps))} 个；仅待核实来源 {len(set(p['source'] for p in pending)-set(p['source'] for p in ps))} 个。检索索引不计为发布来源。",'','一篇研究可带多个领域标签；领域计数不可相加视为总数。同一研究的预印本、正式版本、研究博客与代码按稳定身份和标题/作者合并。','']
 if not ps:lines+=['本窗口未取得同时满足阅读门槛及时间证据要求的确认新增；不以旧稿或未读标题补数。','']
 for src in dict.fromkeys(p['source'] for p in ps):
  lines += [f"## {sources.get(src,src)}",'']
  for p in [p for p in ps if p['source']==src]:lines+=render_paper(p)
 if pending:
  lines+=['## 时间待核实（不计入确认新增）','','以下条目已阅读完整摘要或实质研究材料，但日期/时区/首次公开边界证据尚不足。待核实不是当日新增的替代称谓。','']
  for p in pending:lines+=render_paper(p)
 lines+=['## 编辑规范','','- 仅整理公开学术资料，不包含私人研究进度或个人相关性评价。','- 作者机构依据原始署名；无法核实者明确注明，不猜职位与经历。','- 来源、研究领域、内容类型和同行评审状态是独立维度。','- 历史试刊独立保留；其旧索引不阻止确实符合本期窗口的研究进入首份正式日报。','- 不转载论文全文；更正保留版本和更正说明。','']
 return '\n'.join(lines)
def main():
 sources={s['id']:s['name'] for s in json.loads((ROOT/'data/sources.json').read_text())['sources']}
 manifest=json.loads((ROOT/'data/issues.json').read_text())
 for item in manifest['issues']:
  issue=json.loads((ROOT/item['path']).read_text())
  (ROOT/item.get('report',f"reports/{issue['date']}.md")).write_text(render(issue,sources))
if __name__=='__main__':main()
