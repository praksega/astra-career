import unittest
from scripts.jd_evidence import evaluate
class EvidenceTests(unittest.TestCase):
 def test_verified_capabilities(self):
  v=evaluate("Product Operations Analyst","Excel reporting dashboards, SQL, stakeholder management, workflow automation and SOP documentation.","Bengaluru")
  self.assertIsNone(v["score"])
  self.assertGreaterEqual(v["capability_categories_matched"],4)
  self.assertTrue(all(x["candidate_evidence"] for x in v["evidence"]))
 def test_platform_gap(self):
  v=evaluate("TA Operations","Workday Recruiting administrator mandatory.","Hyderabad")
  self.assertIn("workday recruiting",v["potential_unverified_requirements"])
  self.assertIsNone(v["score"])
if __name__=="__main__":unittest.main()
