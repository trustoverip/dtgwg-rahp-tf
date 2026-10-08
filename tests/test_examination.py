import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'review'))
import examine


class ExaminationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'example'
        shutil.copytree(examine.EXAMPLE, self.root)

    def update(self, mutate):
        path = self.root / 'evidence.json'
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value))

    def reject(self, message=None):
        with self.assertRaises((ValueError, OSError, KeyError, TypeError)) as caught:
            examine.examine(self.root)
        if message:
            self.assertIn(message, str(caught.exception))

    def test_success_is_bounded_validation_not_assurance(self):
        result = examine.examine(self.root)
        self.assertEqual('complete', result['validation'])
        self.assertEqual('review-required', result['overall_assurance'])
        self.assertEqual(2, result['findings'])
        self.assertTrue(all(v == 'not-assessed' for v in result['unassessed'].values()))

    def test_each_finding_requires_evidence_coverage(self):
        self.update(lambda s: s['findings'].pop())
        self.reject('every review finding')

    def test_missing_evidence_reference_rejected(self):
        self.update(lambda s: s['evidence'].pop(0))
        self.reject('missing evidence')

    def test_missing_evidence_file_rejected(self):
        (self.root / 'cases.json').unlink()
        self.reject()

    def test_execution_failure_or_incomplete_state_rejected(self):
        original = (self.root / 'evidence.json').read_text()
        for state in ['failed', 'incomplete']:
            (self.root / 'evidence.json').write_text(original)
            self.update(lambda s: s['execution'].update(state=state))
            self.reject('Execution incomplete')

    def test_stale_observations_rejected(self):
        self.update(lambda s: s['execution']['observations']['api_example'].update(requested_time_matches=True))
        self.reject('observations disagree')

    def test_target_and_method_disagreement_rejected(self):
        original = (self.root / 'evidence.json').read_text()
        for mutate in [lambda s: s['target'].update(revision='0'*40),
                       lambda s: s.update(method_revision='0'*40),
                       lambda s: s.update(assessment_id='SR-999')]:
            (self.root / 'evidence.json').write_text(original)
            self.update(mutate)
            self.reject('disagrees')

    def test_review_and_corpus_bytes_are_bound(self):
        for name in ['review.yaml', 'risks.yaml']:
            path = self.root / name
            old = path.read_bytes()
            path.write_bytes(old + b'\n')
            self.reject('digest mismatch')
            path.write_bytes(old)

    def test_review_target_disagrees_with_manifest_even_after_rebinding(self):
        path = self.root / 'review.yaml'
        record = yaml.safe_load(path.read_text())
        record['target']['revision'] = '0'*40
        path.write_text(yaml.safe_dump(record))
        self.update(lambda s: s['review_binding'].update(sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        self.reject('retained-source manifest')

    def test_duplicate_evidence_and_findings_rejected(self):
        original = (self.root / 'evidence.json').read_text()
        for key in ['evidence', 'findings']:
            (self.root / 'evidence.json').write_text(original)
            self.update(lambda s: s[key].append(copy.deepcopy(s[key][0])))
            self.reject('Duplicate')

    def test_result_reference_and_contradiction_rejected(self):
        original = (self.root / 'evidence.json').read_text()
        for pointer, expected in [('/missing', True), ('/cases/99/schema_valid', True),
                                  ('/api_example/requested_time_matches', True),
                                  ('/api_example/schema_valid', 1)]:
            (self.root / 'evidence.json').write_text(original)
            self.update(lambda s: s['evidence'][5].update(pointer=pointer, expected=expected))
            self.reject('E-006')

    def test_unsafe_and_unretained_source_references_rejected(self):
        self.update(lambda s: s['evidence'][0].update(path='../outside'))
        self.reject('Unsafe')
        (self.root / 'evidence.json').write_text((examine.EXAMPLE / 'evidence.json').read_text())
        self.update(lambda s: s['evidence'][0].update(path='cases.json'))
        self.reject('not retained')

    def test_invalid_source_lines_rejected(self):
        self.update(lambda s: s['evidence'][0].update(lines=[1, 99999]))
        self.reject('lines do not resolve')

    def test_finding_risk_reasoning_required_and_unknown_risk_rejected(self):
        self.update(lambda s: s['findings'][0]['risk_reasoning'].pop('RK-AU01'))
        self.reject('risk reasoning')
        record = yaml.safe_load((self.root / 'review.yaml').read_text())
        record['findings'][0]['risks'] = ['RK-ZZ99']
        (self.root / 'review.yaml').write_text(yaml.safe_dump(record))
        self.reject('does not resolve')

    def test_unassessed_cannot_be_relabelled_success(self):
        self.update(lambda s: s['unassessed'].update(authority='verified'))
        self.reject('evidence schema')

    def test_unknown_members_and_empty_reasoning_rejected(self):
        original = (self.root / 'evidence.json').read_text()
        for mutate in [lambda s: s.update(overall_assurance='PASS'),
                       lambda s: s['findings'][0].update(inference=''),
                       lambda s: s['findings'][0].update(evidence=[]),
                       lambda s: s['findings'][0].update(limitations=[])]:
            (self.root / 'evidence.json').write_text(original)
            self.update(mutate)
            self.reject('evidence schema')

    def test_cli_failure_has_nonzero_exit_and_no_success_json(self):
        (self.root / 'evidence.json').unlink()
        run = subprocess.run([sys.executable, str(ROOT / 'review/examine.py'), '--example', str(self.root)], capture_output=True, text=True)
        self.assertEqual(1, run.returncode)
        self.assertEqual('', run.stdout)
        self.assertIn('incomplete', run.stderr)

    def test_user_bundle_code_is_not_executed(self):
        (self.root / 'replay.py').write_text('raise RuntimeError("must not execute")')
        self.assertEqual('complete', examine.examine(self.root)['validation'])

    def test_pointer_escapes_and_invalid_indices(self):
        self.assertEqual(3, examine.pointer_value({'a/b': {'~x': [3]}}, '/a~1b/~0x/0'))
        for pointer in ['/a~2b', '/items/01', '/items/-1', 'items']:
            with self.assertRaises((ValueError, KeyError)):
                examine.pointer_value({'items': [1]}, pointer)


if __name__ == '__main__':
    unittest.main()
