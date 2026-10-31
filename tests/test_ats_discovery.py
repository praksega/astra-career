import unittest
from scripts.discover_ats import normalize, candidate_signals
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
 def test_process_excellence(self):
  x={"id":126,"title":"Process Excellence Specialist","location":{"name":"Hyderabad"},"absolute_url":"https://boards.greenhouse.io/example/jobs/126","content":"<p>Process improvement and operational efficiency</p>"}
  self.assertIsNotNone(normalize("greenhouse","example",x))
 def test_jd_recovery(self):
  x={"id":127,"title":"Business Associate","location":{"name":"Pune"},"absolute_url":"https://boards.greenhouse.io/example/jobs/127","content":"<p>Stakeholder management, workflow automation, performance metrics and process optimization.</p>"}
  self.assertEqual(normalize("greenhouse","example",x)["matching_method"],"jd_responsibilities")
 def test_software_engineer_exclusion(self):
  self.assertEqual(candidate_signals("Senior Software Engineer, Business Operations","process improvement and workflow automation")[1],"excluded_specialist_title")
 def test_india_only_not_remote(self):
  x={"id":128,"title":"Business Analyst","location":{"name":"India"},"absolute_url":"https://boards.greenhouse.io/example/jobs/128"}
  self.assertIsNone(normalize("greenhouse","example",x))
if __name__=="__main__":unittest.main()
