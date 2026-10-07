import importlib.util
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('worked_review_validator', ROOT / 'review' / 'validate_spec_review.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class WorkedAdoptionTests(unittest.TestCase):
    def test_published_review_examples_conform_to_the_existing_contract(self):
        directory = ROOT / 'review' / 'examples' / 'worked-adoption'
        for name in ['baseline-review.yaml', 'reassessed-review.yaml']:
            with self.subTest(record=name):
                record = yaml.safe_load((directory / name).read_text())
                self.assertEqual(validator.validate_record(record), [])


if __name__ == '__main__':
    unittest.main()
