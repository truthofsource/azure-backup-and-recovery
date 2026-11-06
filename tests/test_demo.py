import unittest
from lab.demo import report


class DemonstrationTests(unittest.TestCase):
    def test_report_is_successful_and_has_evidence(self):
        result = report()
        self.assertTrue(result["records"])
        self.assertTrue(all(check["passed"] for check in result["checks"]))
        self.assertIn("fictional", result["boundary"])
