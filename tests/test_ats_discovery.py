import unittest
from scripts.discover_ats import normalize
class ATSParser(unittest.TestCase):
 def test_greenhouse(self):
  x={"id":123,"title":"Product Operations Analyst","location":{"name":"Bengaluru, India"},"absolute_url":"https://boards.greenhouse.io/example/jobs/123","content":"<p>Analyze operational KPIs</p>","first_published":"2026-10-30T09:00:00Z"}
  y=normalize("greenhouse","example",x)
  self.assertEqual(y["id"],"greenhouse:123")
  self.assertTrue(y["posting_date_verified"])
 def test_unrelated(self):
  x={"id":124,"title":"Senior Java Developer","location":{"name":"Bengaluru"},"absolute_url":"https://boards.greenhouse.io/example/jobs/124"}
  self.assertIsNone(normalize("greenhouse","example",x))
 def test_wrong_city(self):
  x={"id":125,"title":"Product Operations Analyst","location":{"name":"New York"},"absolute_url":"https://boards.greenhouse.io/example/jobs/125"}
  self.assertIsNone(normalize("greenhouse","example",x))
if __name__=="__main__":unittest.main()
