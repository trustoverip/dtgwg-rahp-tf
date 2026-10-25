import copy
import json
from pathlib import Path
import unittest
from evaluate import evaluate
ROOT=Path(__file__).resolve().parent
CASES=json.loads((ROOT/"cases.json").read_text())
class FixtureTests(unittest.TestCase):
    def test_replay(self):
        self.assertEqual(evaluate(CASES),json.loads((ROOT/"expected.json").read_text()))
    def test_revoked_execution_is_failure(self):
        x=copy.deepcopy(CASES);x["scenarios"][1]["booking_executed"]=True
        self.assertEqual(evaluate(x)["results"][1]["outcome"],"FAIL")
    def test_missing_authority_is_not_pass(self):
        x=copy.deepcopy(CASES);x["scenarios"][0]["evidence"].remove("authority")
        self.assertEqual(evaluate(x)["results"][0]["outcome"],"INDETERMINATE")
    def test_scope_violation(self):
        x=copy.deepcopy(CASES);x["scenarios"][0]["permission_scope"]="other"
        self.assertEqual(evaluate(x)["results"][0]["outcome"],"FAIL")
    def test_duplicate_rejected(self):
        x=copy.deepcopy(CASES);x["scenarios"].append(x["scenarios"][0])
        with self.assertRaises(ValueError):evaluate(x)
    def test_invalid_disposition_rejected(self):
        x=copy.deepcopy(CASES);x["material_change"]["dispositions"][0]["state"]="PASS"
        with self.assertRaises(ValueError):evaluate(x)
if __name__=="__main__": unittest.main()
