#!/usr/bin/env python3
"""Render formal reviewed issues only; preserve historical trial reports verbatim."""
import json,os
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
def render(issue,sources,report_path):
 ps=issue['papers'];pending=issue.get('pending_papers',[])
 for p in ps+pending:validate_review(p)
 retrieval=os.path.relpath(ROOT/issue['retrieval_log'],(ROOT/report_path).parent)
 lines=[f"# arXiv 论文日报（AOE）｜{issue['date']}",'',f"检索窗口：{issue['window_start']} 至 {issue['window_end']}，左闭右开。AOE（UTC−12）已结束自然日。",'',f"**arXiv 确认新增 {len(ps)} 篇；时间待核实 {len(pending)} 篇（另列，不计入新增）。**",'','**实际阅读范围：** '+issue['editorial_note'],'','研究结论按原作者主张转述；摘要或局部正文阅读不等于完整证明审计、性能复现或安全背书。','','## arXiv 公告与阅读范围','']
 for c in issue['coverage']:
  if c.get('public_display') is True:lines += [c['scope'],c['note'],'']
 lines += [f"[本期检索记录]({retrieval})",'','## 领域索引','']
 for d in DOMAINS:lines += [f"- {d}：{sum(d in p['domains'] for p in ps)} 篇"]
 lines += ['','一篇论文可带多个领域标签；领域计数不能相加作为论文总数。按主要领域编排，每篇只出现一次。','']
 if not ps:lines += ['本窗口未取得同时满足阅读门槛及时间证据要求的确认新增；不以旧稿或未读标题补数。','']
 for d in DOMAINS:
  entries=[p for p in ps if p['domains'][0]==d]
  if entries:
   lines += [f'## {d}','']
   for p in entries:lines+=render_paper(p)
 if pending:
  lines += ['## 时间待核实（不计入确认新增）','','以下条目已阅读完整摘要或实质研究材料，但 arXiv 公告时间尚不能确认落在本期窗口内。','']
  for p in pending:lines+=render_paper(p)
 lines += ['## 编辑规范','','- 仅研究 arXiv 的公开论文，不包含私人研究进度或个人相关性评价。','- 作者机构依据所读 arXiv 版本署名；无法核实者明确注明。','- 不执行论文代码或实验，不转载原始摘要和论文全文。','- 更正保留版本与实际阅读范围，不把旧稿修订当新论文。','']
 return '\n'.join(lines)
def main():
 sources={s['id']:s['name'] for s in json.loads((ROOT/'data/sources.json').read_text())['sources']}
 manifest=json.loads((ROOT/'data/issues.json').read_text())
 for item in manifest['issues']:
  issue=json.loads((ROOT/item['path']).read_text())
  report=item['report'];(ROOT/report).parent.mkdir(parents=True,exist_ok=True)
  (ROOT/report).write_text(render(issue,sources,report))
if __name__=='__main__':main()
