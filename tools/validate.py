#!/usr/bin/env python3
"""Validate reviewed issues, AoE time eligibility, separate pending items and archives."""
import json,re
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlparse
R=Path(__file__).resolve().parents[1]
FIELDS=['id','title','title_zh','authors','source','url','first_date','updated_date','version','publication_status','domains','subfields','problem','result','method','limitations','reading_depth','author_intro','author_institutions','affiliation_sources','evidence_urls']
DOMAINS=['数学','计算机科学','网络与信息安全','密码学']
def utc(value):
 assert isinstance(value,str) and re.search(r'T.*(?:Z|[+-]\d\d:\d\d)$',value),'Timezone-qualified timestamp required'
 return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc)
def valid_url(value):
 return isinstance(value,str) and urlparse(value).scheme=='https' and bool(urlparse(value).netloc)
def validate_review(p):
 if p['reading_depth']=='abstract':
  r=p.get('abstract_review',{})
  assert r.get('complete_abstract_accessed') is True and r.get('read_confirmed') is True,(p['id'],'complete abstract not accessed/read')
  assert valid_url(r.get('source_url')),(p['id'],'missing original abstract URL')
  assert isinstance(r.get('scope'),str) and r['scope'].strip(),(p['id'],'missing actual reading scope')
 else:
  r=p.get('substantive_review',{})
  assert p['reading_depth'] in ['partial','full_review']
  assert isinstance(r.get('content_urls'),list) and r['content_urls'] and all(valid_url(u) for u in r['content_urls'])
  assert all(isinstance(r.get(k),str) and r[k].strip() for k in ['scope','method_evidence','result_evidence','conditions_evidence']),(p['id'],'missing substantive reading evidence')
def validate_time(p,start,end,pending=False):
 assert p.get('eligibility')==('pending' if pending else 'confirmed'),(p['id'],'wrong eligibility section')
 assert valid_url(p.get('public_time_source')),(p['id'],'missing public-time evidence URL')
 assert isinstance(p.get('public_time_precision'),str) and p['public_time_precision'].strip()
 if pending:
  assert isinstance(p.get('date_note'),str) and p['date_note'].strip(),(p['id'],'pending needs uncertainty explanation')
  return
 if p.get('public_time_range'):
  r=p['public_time_range'];a,b=utc(r['start']),utc(r['end'])
  assert start<=a<b<=end,(p['id'],'supported public-time range crosses daily boundary')
 else:
  assert p['public_time_precision'] not in ['date','day','unknown'],(p['id'],'date-only time cannot be confirmed')
  assert start<=utc(p.get('public_at'))<end,(p['id'],'first public time outside window')
def validate_issue(j,item,source_ids,formal=True):
 assert j['date']==item['date'];ids=set();titles=set()
 if formal:
  start,end=utc(j['window_start']),utc(j['window_end'])
  expected=datetime.fromisoformat(j['date']).replace(hour=12,tzinfo=timezone.utc)
  assert start==expected and end==start+timedelta(days=1),'AOE date must map to UTC 12:00–12:00'
  assert utc(j['generated_at'])>=end,'Cannot publish an unfinished window'
  assert j.get('timezone')=='Etc/GMT+12'
  assert isinstance(j.get('editorial_note'),str) and j['editorial_note'].strip()
  assert isinstance(j.get('pending_papers',[]),list)
 for pending,entries in [(False,j['papers']),(True,j.get('pending_papers',[]))]:
  for p in entries:
   assert all(k in p for k in FIELDS),(p.get('id'),'missing fields')
   assert p['id'] not in ids,(p['id'],'duplicate stable id');ids.add(p['id'])
   title=re.sub(r'\W','',p['title']).casefold();assert title not in titles,(p['id'],'duplicate title');titles.add(title)
   assert p['source'] in source_ids and p['authors'] and p['author_institutions']
   assert p['reading_depth'] in ['abstract','partial','full_review']
   assert p['domains'] and all(d in DOMAINS for d in p['domains'])
   assert all(valid_url(u) for u in [p['url']]+p['evidence_urls']+p['affiliation_sources'])
   assert all(p[k] is None or re.fullmatch(r'\d{4}-\d{2}-\d{2}',p[k]) for k in ['first_date','updated_date'])
   assert not any(x in json.dumps(p,ensure_ascii=False) for x in ['与你的研究','我的已有研究','我们研究路线'])
   if formal:
    assert all(isinstance(p.get(k),str) and p[k].strip() for k in ['title','title_zh','problem','result','method','limitations','author_intro'])
    validate_review(p);validate_time(p,start,end,pending)
    for discovery in p.get('discovered_via',[]):
     assert valid_url(discovery.get('record_url')) and isinstance(discovery.get('index_id'),str)
     utc(discovery.get('accessed_at'))
 assert (R/item.get('report',f"reports/{j['date']}.md")).exists()
 if formal:
  assert (R/j['retrieval_log']).exists(),'Detailed retrieval log must be archived'
  for c in j['coverage']:
   assert c.get('id') in source_ids and all(isinstance(c.get(k),str) and c[k].strip() for k in ['name','url','status','scope','note'])
   assert isinstance(c.get('public_display'),bool)
 print(j['date'],len(j['papers']),'confirmed/legacy;',len(j.get('pending_papers',[])),'pending: PASS')
def main():
 manifest=json.loads((R/'data/issues.json').read_text());cat=json.loads((R/'data/sources.json').read_text());source_ids={s['id'] for s in cat['sources'] if s.get('role')!='discovery_index'}
 assert (manifest['latest'] in [i['date'] for i in manifest['issues']]) if manifest['issues'] else manifest['latest'] is None
 formal_ids={}
 for item in manifest['issues']+manifest.get('historical_trials',[]):
  j=json.loads((R/item['path']).read_text());formal=item in manifest['issues'];validate_issue(j,item,source_ids,formal)
  if formal:
   for p in j['papers']:
    assert p['id'] not in formal_ids,(p['id'],'repeated as new across formal days',formal_ids.get(p['id']))
    formal_ids[p['id']]=j['date']
 print('Archive index, review, public-time and cross-day dedup PASS')
if __name__=='__main__':main()
