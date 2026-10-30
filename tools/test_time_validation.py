#!/usr/bin/env python3
"""Synthetic timing-only tests; no paper content or review claims are fabricated."""
import unittest
from validate import utc,validate_time
class TimeEligibility(unittest.TestCase):
 def setUp(self):
  self.start=utc('2026-10-29T12:00:00Z');self.end=utc('2026-10-30T12:00:00Z')
  self.base={'id':'timing-only-test','eligibility':'confirmed','public_time_source':'https://example.org/original-timestamp','public_time_precision':'second'}
 def check(self,**fields):validate_time(dict(self.base,**fields),self.start,self.end)
 def test_left_boundary_included(self):self.check(public_at='2026-10-29T12:00:00Z')
 def test_right_boundary_excluded(self):
  with self.assertRaises(AssertionError):self.check(public_at='2026-10-30T12:00:00Z')
 def test_previous_day_excluded(self):
  with self.assertRaises(AssertionError):self.check(public_at='2026-10-29T11:59:59Z')
 def test_timezone_conversion(self):self.check(public_at='2026-10-29T15:00:00+02:00')
 def test_naive_time_excluded(self):
  with self.assertRaises(AssertionError):self.check(public_at='2026-10-29T15:00:00')
 def test_date_not_promoted(self):
  with self.assertRaises(AssertionError):self.check(public_at='2026-10-29',public_time_precision='date')
 def test_range_within_window(self):self.check(public_time_precision='range',public_time_range={'start':'2026-10-29T20:00:00Z','end':'2026-10-30T04:00:00Z'})
 def test_range_crossing_window_rejected(self):
  with self.assertRaises(AssertionError):self.check(public_time_precision='range',public_time_range={'start':'2026-10-29T00:00:00Z','end':'2026-10-30T00:00:00Z'})
 def test_date_pending_with_reason(self):
  validate_time(dict(self.base,eligibility='pending',public_at='2026-10-29',public_time_precision='date',date_note='Date only; timezone and boundary unresolved.'),self.start,self.end,True)
 def test_pending_needs_reason(self):
  with self.assertRaises(AssertionError):validate_time(dict(self.base,eligibility='pending'),self.start,self.end,True)
if __name__=='__main__':unittest.main()
