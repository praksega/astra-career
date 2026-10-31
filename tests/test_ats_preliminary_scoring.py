import unittest
from datetime import datetime,timezone
from scripts.preliminary_scoring import assess
NOW=datetime(2026,11,1,0,0,tzinfo=timezone.utc)
class PreliminaryScoringTests(unittest.TestCase):
 def test_qualified_estimate_remains_unverified(self):
  j={"title":"Product Operations Analyst","location":"Bengaluru","source_date":"2026-10-30T10:00:00Z","posting_date_verified":True,"description_excerpt":"Product operations, reporting, metrics, dashboard, Excel, SQL, automation, process improvement, stakeholder and cross-functional collaboration, program management, SOP documentation and business operations.","jd_evidence":{"capability_categories_matched":7,"capability_evidence_coverage_pct":100}}
  x=assess(j,NOW)
  self.assertGreaterEqual(x["preliminary_score"],71)
  self.assertFalse(x["verified_for_main_match_tiers"])
  self.assertTrue(x["fresh_within_5_days"])
  self.assertEqual(x["rubric"]["compensation"],0)
 def test_old_date_does_not_promote(self):
  j={"title":"Operations Analyst","location":"Pune","source_date":"2024-03-25T10:00:00Z","posting_date_verified":True,"description_excerpt":"a"*1800,"jd_evidence":{"capability_categories_matched":7,"capability_evidence_coverage_pct":100}}
  self.assertFalse(assess(j,NOW)["fresh_within_5_days"])
 def test_unverified_date_is_not_fresh(self):
  j={"title":"Business Analyst","location":"Hyderabad","source_date":None,"posting_date_verified":False,"description_excerpt":"analysis","jd_evidence":{"capability_categories_matched":5,"capability_evidence_coverage_pct":71}}
  self.assertIn("original_posting_date_unverified",assess(j,NOW)["review_flags"])
if __name__=="__main__":unittest.main()
