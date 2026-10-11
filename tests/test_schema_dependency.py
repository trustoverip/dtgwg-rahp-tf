"""Fail-closed regression: a missing jsonschema package must not be a PASS."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RequiredSchemaDependency(unittest.TestCase):
    def test_missing_jsonschema_aborts_before_validating(self):
        # Force only jsonschema imports to fail in a fresh interpreter. Keep
        # PyYAML present so this checks the precise dependency boundary.
        script = """
import builtins, runpy, sys
real_import = builtins.__import__
def rejecting_import(name, *args, **kwargs):
    if name == 'jsonschema' or name.startswith('jsonschema.'):
        raise ModuleNotFoundError("simulated missing jsonschema")
    return real_import(name, *args, **kwargs)
builtins.__import__ = rejecting_import
sys.argv = ['tools/validate.py', '--summary']
runpy.run_path('tools/validate.py', run_name='__main__')
"""
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("schema validation unavailable", result.stderr + result.stdout)
        self.assertNotIn("PASS", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
