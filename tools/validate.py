#!/usr/bin/env python3
"""Validate reviewed issue schema, identifiers, URLs and archive consistency."""
import json,re
from pathlib import Path
from urllib.parse import urlparse
R=Path(__file__).resolve().parents[1]; m=json.loads((R/'data/issues.json').read_text()); cat=json.loads((R/'data/sources.json').read_text()); ss={s['id'] for s in cat['sources']}
assert (m['latest'] in [i['date'] for i in m['issues']]) if m['issues'] else m['latest'] is None
seen=set(); fields=['id','title','title_zh','authors','source','url','first_date','updated_date','version','publication_status','domains','subfields','problem','result','method','limitations','reading_depth','author_intro','author_institutions','affiliation_sources','evidence_urls']
for item in m['issues']+m.get('historical_trials',[]):
 p=R/item['path']; j=json.loads(p.read_text()); assert j['date']==item['date']; ids=set();titles=set()
 for x in j['papers']:
  assert all(k in x for k in fields),(x.get('id'),'missing fields')
  assert x['id'] not in ids;ids.add(x['id']);t=re.sub(r'\W','',x['title']).casefold();assert t not in titles; titles.add(t)
  assert x['source'] in ss; assert x['reading_depth'] in ['abstract','partial','full_review'];assert x['authors'] and x['author_institutions']
  assert all(d in ['数学','计算机科学','网络与信息安全','密码学'] for d in x['domains'])
  for u in [x['url']]+x['evidence_urls']+x['affiliation_sources']:assert urlparse(u).scheme=='https' and urlparse(u).netloc
  for k in ['first_date','updated_date']:assert x[k] is None or re.fullmatch(r'\d{4}-\d{2}-\d{2}',x[k]),(x['id'],k,x[k])
  assert not any(t in json.dumps(x,ensure_ascii=False) for t in ['与你的研究','我的已有研究','我们研究路线'])
 assert (R/item.get('report',f"reports/{j['date']}.md")).exists()
 print(j['date'],len(ids),'papers: schema, dates, URLs, dedup, editorial checks PASS')
print('Archive index PASS')
