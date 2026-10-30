import unittest
from datetime import datetime,timezone,timedelta
from scripts.linkedin_rules import filtered
NOW=datetime(2026,10,30,12,0,tzinfo=timezone.utc)
BASE=dict(url="https://www.linkedin.com/posts/example_activity-7499999999999999999-test",posted_at=(NOW-timedelta(hours=2)).isoformat(),timestamp_verified=True,timestamp_evidence_url="https://www.linkedin.com/posts/example_activity-7499999999999999999-test",role="Product Operations Analyst",location="Bengaluru",summary="Hiring Product Operations Analyst")
class Rules(unittest.TestCase):
    def test_good(self):self.assertEqual(len(filtered([BASE],NOW)[0]),1)
    def test_old(self):
        x=dict(BASE,posted_at="2026-08-12T10:00:00+05:30")
        self.assertEqual(filtered([x],NOW)[1]["outside_24h"],1)
    def test_undated(self):
        x=dict(BASE,posted_at=None)
        self.assertEqual(filtered([x],NOW)[1]["missing_verified_timestamp"],1)
    def test_no_evidence(self):
        x=dict(BASE,timestamp_verified=False)
        self.assertEqual(filtered([x],NOW)[1]["timestamp_evidence_missing"],1)
    def test_duplicate(self):
        x=dict(BASE,url="https://in.linkedin.com/feed/update/urn:li:activity:7499999999999999999?trk=feed")
        good,err=filtered([BASE,x],NOW)
        self.assertEqual(len(good),1)
        self.assertEqual(err["duplicate"],1)
    def test_wrong_city(self):
        x=dict(BASE,location="Mumbai",summary="Product Operations Analyst opening")
        self.assertEqual(filtered([x],NOW)[1]["location_not_relevant"],1)
    def test_wrong_role(self):
        x=dict(BASE,role="Java Backend Engineer",summary="We are hiring software developers")
        self.assertEqual(filtered([x],NOW)[1]["role_not_relevant"],1)
if __name__=="__main__":unittest.main()
