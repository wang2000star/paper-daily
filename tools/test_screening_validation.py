#!/usr/bin/env python3
"""Synthetic validation fixtures only; not evidence for any published issue."""
import copy,json,unittest
from pathlib import Path
from validate import validate_screening
class ScreeningValidation(unittest.TestCase):
 def setUp(self):
  self.j={'window_end':'2000-01-02T12:00:00Z','papers':[],'screening':{'candidate_count':0,'abstract_screened_count':0,'selected_count':0,'screen_sha256':{}}}
  self.proof={'screening_parts':[],'selected_ids':[],'decision_counts':{'shortlist':0,'reserve':0,'not_selected':0},'zero_inventory_verification':{'complete':True,'confirmed_new_count':0,'official_sources':[{'url':'https://arxiv.org/list/'+c+'/new','checked_at':'2000-01-02T12:01:00Z','http_status':200,'sha256':'0'*64} for c in ['cs','math']]}}
 def test_verified_zero(self):validate_screening(self.j,self.proof)
 def test_missing_evidence(self):
  del self.proof['zero_inventory_verification']
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_unfinished_check(self):
  self.proof['zero_inventory_verification']['complete']=False
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_missing_archive(self):
  self.proof['zero_inventory_verification']['official_sources'].pop()
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_missing_response_hash(self):
  del self.proof['zero_inventory_verification']['official_sources'][0]['sha256']
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_failed_response(self):
  self.proof['zero_inventory_verification']['official_sources'][0]['http_status']=503
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_before_cutoff(self):
  self.proof['zero_inventory_verification']['official_sources'][0]['checked_at']='2000-01-02T11:59:59Z'
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_foreign_source(self):
  self.proof['zero_inventory_verification']['official_sources'][0]['url']='https://example.org/list/cs/new'
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_fabricated_zero_part(self):
  self.proof['screening_parts']=[{'part':1,'expected':0,'read':0,'missing':0,'complete':True,'sha256':'0'*64}]
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_nonzero_requires_parts(self):
  self.j['screening'].update(candidate_count=1,abstract_screened_count=1)
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_count_mismatch(self):
  self.j['screening']['abstract_screened_count']=1
  with self.assertRaises(AssertionError):validate_screening(self.j,self.proof)
 def test_previous_complete_issue(self):
  r=Path(__file__).resolve().parents[1];j=json.loads((r/'data/arxiv/2026-10-29.json').read_text());proof=json.loads((r/j['retrieval_log']).read_text());validate_screening(j,proof)
  bad=copy.deepcopy(proof);bad['screening_parts'][0]['read']-=1
  with self.assertRaises(AssertionError):validate_screening(j,bad)
if __name__=='__main__':unittest.main()
