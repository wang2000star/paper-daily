#!/usr/bin/env python3
"""Validate reviewed issues, AoE time eligibility, separate pending items and archives."""
import json,re,hashlib
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlparse
R=Path(__file__).resolve().parents[1]
FIELDS=['id','title','title_zh','authors','source','url','first_date','updated_date','version','publication_status','primary_category','canonical_primary_category','arxiv_group','arxiv_archive','cross_categories','arxiv_categories','category_evidence','problem','result','method','limitations','reading_depth','author_intro','author_institutions','affiliation_sources','evidence_urls']
TAXONOMY=json.loads((R/'data/arxiv-taxonomy.json').read_text())
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
   assert not any(k in p for k in ['domains','subfields','keywords']),(p['id'],'custom classification is not allowed')
   cat=TAXONOMY['category_catalog'];primary=p['primary_category'];assert primary in cat
   c=cat[primary];assert p['canonical_primary_category']==c['canonical_code']
   assert p['arxiv_group']==c['canonical_group'] and p['arxiv_group'] in TAXONOMY['groups']
   canonical=cat[c['canonical_code']];assert p['arxiv_archive']==canonical['archive']
   assert isinstance(p['cross_categories'],list) and all(x in cat for x in p['cross_categories'])
   assert len(p['cross_categories'])==len(set(p['cross_categories'])) and primary not in p['cross_categories']
   assert p['arxiv_categories']==[primary]+p['cross_categories']
   ce=p['category_evidence'];assert ce['method']=='official_primary_subject' and ce['source_urls']
   assert all(urlparse(u).hostname in ['arxiv.org','info.arxiv.org','rss.arxiv.org'] for u in ce['source_urls'])
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
def validate_screening(j,proof):
 screen=j['screening'];count=screen['candidate_count']
 assert type(count) is int and count>=0
 assert screen['abstract_screened_count']==count
 assert screen['selected_count']==len(j['papers'])<=count
 assert all(p.get('why_selected') and p.get('selection_evidence_limit') and p.get('selection_stage')=='full_inventory_abstract_screening' for p in j['papers'])
 parts=proof['screening_parts'];assert len({p['part'] for p in parts})==len(parts)
 if count:
  assert parts and screen['screen_sha256'],'Nonempty inventory needs actual screening evidence'
  assert sum(p['expected'] for p in parts)==count
  assert all(p['complete'] and p['read']==p['expected']>0 and p['missing']==0 for p in parts)
 else:
  assert parts==[] and screen['screen_sha256']=={},'Zero inventory cannot fabricate screening parts'
  zero=proof.get('zero_inventory_verification',{})
  assert zero.get('complete') is True and zero.get('confirmed_new_count')==0,'Zero inventory needs verified official evidence'
  sources=zero.get('official_sources',[]);assert sources
  archives=set()
  for evidence in sources:
   assert evidence.get('http_status')==200 and re.fullmatch(r'[0-9a-f]{64}',evidence.get('sha256','')),'Zero inventory needs successful response hashes'
   u=urlparse(evidence['url']);assert u.scheme=='https' and u.hostname in ['arxiv.org','rss.arxiv.org','info.arxiv.org']
   assert utc(evidence['checked_at'])>=utc(j['window_end']),'Zero inventory must be rechecked after cutoff'
   for archive in ['cs','math']:
    if (u.hostname=='arxiv.org' and u.path==f'/list/{archive}/new') or (u.hostname=='rss.arxiv.org' and u.path==f'/rss/{archive}'):
     archives.add(archive)
  assert archives=={'cs','math'},'Both official cs and math inventories must be checked'
 assert all(type(n) is int and n>=0 for n in proof['decision_counts'].values())
 assert sum(proof['decision_counts'].values())==count
 assert {str(p['part']):p['sha256'] for p in parts}==screen['screen_sha256']
 assert len(proof['selected_ids'])==len(set(proof['selected_ids']))==len(j['papers'])
 assert set(proof['selected_ids'])=={p['id'].removeprefix('arxiv-') for p in j['papers']}
def main():
 manifest=json.loads((R/'data/issues.json').read_text());cat=json.loads((R/'data/sources.json').read_text())
 assert manifest['source_scope']=='arxiv_only' and cat['active_scope']=='arxiv_only'
 assert [s['id'] for s in cat['sources']]==['arxiv'] and cat.get('discovery_indexes',[])==[]
 assert (manifest['latest'] in [i['date'] for i in manifest['issues']]) if manifest['issues'] else manifest['latest'] is None
 formal_ids={}
 for item in manifest['issues']:
  assert item['path'].startswith('data/arxiv/') and item['report'].startswith('reports/arxiv/')
  j=json.loads((R/item['path']).read_text());assert j['source_scope']=='arxiv_only'
  assert j['retrieval_log'].startswith('data/retrieval/arxiv/')
  assert j.get('classification')=='arxiv_official_primary' and j.get('taxonomy')=='data/arxiv-taxonomy.json'
  validate_issue(j,item,{'arxiv'},True)
  for p in j['papers']+j.get('pending_papers',[]):
   evidence=[p['url'],p['public_time_source']]+p['affiliation_sources']+p['evidence_urls']
   evidence+=p.get('substantive_review',{}).get('content_urls',[])
   if p.get('abstract_review'):evidence.append(p['abstract_review']['source_url'])
   assert all(urlparse(u).hostname in ['arxiv.org','www.arxiv.org','rss.arxiv.org','info.arxiv.org'] for u in evidence),(p['id'],'research evidence must be arXiv official')
  if j.get('screening',{}).get('status')=='complete':
   validate_screening(j,json.loads((R/j['retrieval_log']).read_text()))
  assert item['confirmed_count']==len(j['papers']) and item.get('pending_count',0)==len(j.get('pending_papers',[]))
  for p in j['papers']:
   assert p['id'] not in formal_ids,(p['id'],'repeated as new across days');formal_ids[p['id']]=j['date']
 preserved=json.loads((R/'data/history/multisource-preservation.json').read_text())
 for path,expected in preserved['sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==expected,(path,'historical content changed')
 seen=json.loads((R/manifest['active_seen']).read_text());assert seen['source_scope']=='arxiv_only'
 assert set(formal_ids)<=set(r['id'] for r in seen['records'])
 print('arXiv-only index, counts, review, time, dedup and historical preservation PASS')
if __name__=='__main__':main()
