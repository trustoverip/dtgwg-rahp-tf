import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'review'))
from source_integrity import verify_source

spec = importlib.util.spec_from_file_location('trqp_replay', ROOT / 'review/examples/standalone-trqp/replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
EXAMPLE = replay.HERE


class RetainedSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'example'
        shutil.copytree(EXAMPLE, self.root)

    def manifest(self, mutate):
        path = self.root / 'source-manifest.json'
        record = json.loads(path.read_text())
        mutate(record)
        path.write_text(json.dumps(record))

    def test_replay_matches_and_preserves_semantic_failure(self):
        result = replay.replay(self.root)
        self.assertEqual(json.loads((EXAMPLE / 'expected-replay.json').read_text()), result)
        self.assertTrue(result['api_example']['schema_valid'])
        self.assertFalse(result['api_example']['requested_time_matches'])
        self.assertEqual('review-required', result['overall_assurance'])

    def test_altered_and_missing_source_rejected(self):
        path = self.root / 'source/spec.md.txt'
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            verify_source(self.root)
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            verify_source(self.root)

    def test_unsafe_paths_rejected(self):
        for name in ['../outside', '/etc/passwd', 'source/../cases.json', './cases.json', 'source//spec.md.txt', 'source\\spec.md.txt']:
            with self.subTest(name=name):
                self.manifest(lambda m: m['files'][0].update(path=name))
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    verify_source(self.root)

    def test_symlink_file_and_directory_rejected(self):
        path = self.root / 'source/spec.md.txt'
        data = path.read_bytes()
        path.unlink()
        outside = Path(self.temp.name) / 'outside'
        outside.write_bytes(data)
        path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            verify_source(self.root)
        path.unlink()
        path.write_bytes(data)
        shutil.move(self.root / 'source', self.root / 'moved')
        (self.root / 'source').symlink_to(self.root / 'moved', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            verify_source(self.root)

    def test_duplicate_entries_rejected(self):
        self.manifest(lambda m: m['files'].append(dict(m['files'][0])))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            verify_source(self.root)

    def test_malformed_identity_digest_and_empty_inventory_rejected(self):
        original = (EXAMPLE / 'source-manifest.json').read_text()
        for mutate in [lambda m: m.update(commit='main'), lambda m: m.update(files=[]),
                       lambda m: m['files'][0].update(sha256='bad'),
                       lambda m: m['files'][0].update(git_blob_sha='0'*40),
                       lambda m: m['files'][0].update(url='https://example.org/mutable')]:
            (self.root / 'source-manifest.json').write_text(original)
            self.manifest(mutate)
            with self.assertRaises(ValueError):
                verify_source(self.root)

    def test_missing_and_malformed_http_examples_rejected(self):
        path = self.root / 'broken.txt'
        for content in ['no blocks', '```http\n{}\n```\n```http\n{bad}\n```']:
            path.write_text(content)
            with self.assertRaises(ValueError):
                replay.authorization_examples(path)

    def test_removed_source_entry_rejected(self):
        self.manifest(lambda m: m['files'].pop(0))
        with self.assertRaisesRegex(ValueError, 'omits'):
            replay.replay(self.root)

    def test_wrong_case_expectation_rejected(self):
        path = self.root / 'cases.json'
        cases = json.loads(path.read_text())
        cases[0]['schema_valid'] = False
        path.write_text(json.dumps(cases))
        with self.assertRaisesRegex(ValueError, 'Unexpected schema result'):
            replay.replay(self.root)

    def test_duplicate_and_malformed_cases_rejected(self):
        path = self.root / 'cases.json'
        original = json.loads(path.read_text())
        for cases in [[], original + [original[0]], [{'id': 'bad', 'schema_valid': 'true', 'response': {}}]]:
            path.write_text(json.dumps(cases))
            with self.assertRaises(ValueError):
                replay.replay(self.root)


if __name__ == '__main__':
    unittest.main()
