import unittest
from lab.domain import demo
class RecoveryOrchestrationTests(unittest.TestCase):
    def test_actual_orchestration_has_seven_successful_checks(self):
        result=demo()
        self.assertEqual(len(result['checks']),7)
        self.assertTrue(all(c['passed'] for c in result['checks']))
