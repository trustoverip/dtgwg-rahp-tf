import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RepositoryCommandTests(unittest.TestCase):
    def run_command(self, name, cwd, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / name), *args], cwd=cwd,
            capture_output=True, text=True, timeout=60,
        )

    def test_validation_resolves_repository_inputs_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_command('validate.py', directory, '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report['ok'])
        self.assertEqual(report['errors'], [])
        self.assertGreater(report['counts']['RK'], 0)

    def test_generated_jsonld_context_is_local_to_the_output_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            out = pathlib.Path(directory) / 'output'
            result = self.run_command('build.py', directory, '--out', str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            bundle = json.loads((out / 'rahp.json').read_text())
            self.assertGreater(len(bundle['records']['risk']), 0)
            self.assertTrue((out / 'site' / 'index.html').is_file())
            for path in (out / 'jsonld').glob('*.jsonld'):
                context = path.parent / json.loads(path.read_text())['@context']
                self.assertEqual(context.read_bytes(), (ROOT / 'rahp.jsonld').read_bytes())

    def test_alternate_record_directory_does_not_hide_invalid_references(self):
        with tempfile.TemporaryDirectory() as directory:
            data = pathlib.Path(directory)
            instance = yaml.safe_load((ROOT / 'instance.yaml').read_text())
            (data / 'instance.yaml').write_bytes((ROOT / 'instance.yaml').read_bytes())
            for entry in instance['namespaces'].values():
                name = entry['file']
                (data / name).write_bytes((ROOT / name).read_bytes())
            risks = yaml.safe_load((data / 'risks.yaml').read_text())
            risks['records'][0]['controls'] = ['CT-999']
            (data / 'risks.yaml').write_text(yaml.safe_dump(risks))
            result = self.run_command('validate.py', directory, '--data', str(data), '--json')
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report['ok'])
        self.assertTrue(any('CT-999' in error for error in report['errors']))


if __name__ == '__main__':
    unittest.main()
