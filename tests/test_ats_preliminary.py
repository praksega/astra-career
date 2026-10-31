import unittest
from scripts.score_preliminary_fit import preliminary
class PreliminaryFitTests(unittest.TestCase):
 def test_preliminary_score(self):
  x=preliminary({"title":"Product Operations Analyst","jd_evidence":{"capability_categories_matched":6}})
  self.assertEqual(x["tier"],"possible_provisional")
  self.assertEqual(x["component_scores"]["compensation_unverified"],0)
 def test_specialist_penalty(self):
  x=preliminary({"title":"Senior Application Development Analyst","jd_evidence":{"capability_categories_matched":6}})
  self.assertLess(x["score"],71)
if __name__=="__main__":unittest.main()
