"""Offline regression checks for SEDI local source acquisition."""
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from email.message import Message
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sedi_capture", ROOT / "review/examples/sedi/capture_sources.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Response(io.BytesIO):
    status = 200

    def __init__(self, url, body, media):
        super().__init__(body)
        self.url = url
        self.headers = Message()
        self.headers["Content-Type"] = media

    def geturl(self):
        return self.url


class Opener:
    def __init__(self, body=b"<html>fixture</html>", media="text/html", redirect=None):
        self.body = body
        self.media = media
        self.redirect = redirect

    def open(self, request, timeout):
        return Response(self.redirect or request.full_url, self.body, self.media)


class SediCaptureTests(unittest.TestCase):
    inventory = {"sources": [{"id": "overview", "url": "https://sedi.utah.gov/implementation-guide/"}]}

    def test_capture_is_not_qualified_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "capture"
            manifest = MODULE.capture(self.inventory, output, Opener())
            data = (output / "overview.html").read_bytes()
            self.assertEqual(manifest["files"][0]["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(manifest["source_identity"], "unqualified")
            self.assertEqual(json.loads((output / "capture-manifest.json").read_text()), manifest)

    def test_invalid_response_has_no_success_manifest(self):
        for opener in (Opener(body=b""), Opener(media="application/json"),
                       Opener(redirect="https://example.org/")):
            with self.subTest(opener=opener), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "capture"
                with self.assertRaises(ValueError):
                    MODULE.capture(self.inventory, output, opener)
                self.assertFalse((output / "capture-manifest.json").exists())

    def test_unapproved_url_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                MODULE.capture({"sources": [{"id": "bad", "url": "http://example.org/"}]},
                               Path(tmp) / "capture", Opener())

    def test_checkout_output_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.capture(self.inventory, ROOT / "do-not-create-sedi-capture", Opener())

    def test_inventory_and_initial_objective_coverage(self):
        example = ROOT / "review/examples/sedi"
        inventory = json.loads((example / "source-inventory.json").read_text())
        records = json.loads((example / "initial-requirements.json").read_text())
        self.assertEqual(len(inventory["sources"]), 20)
        self.assertEqual(len({r["url"] for r in inventory["sources"]}), 20)
        self.assertEqual(len(set(inventory["domain_inventory"]["domains"])), 18)
        self.assertEqual({r["id"] for r in records["requirements"]},
                         {"SEDI-BOR-03", "SEDI-BOR-04", "SEDI-BOR-09"})
        for record in records["requirements"]:
            self.assertEqual(set(record["verification"]), {"AUTO", "EXPT", "ADMN"})
            covered = set().union(*(set(m["objectives"]) for m in record["verification"].values()))
            self.assertEqual(covered, set(record["objectives"]))


if __name__ == "__main__":
    unittest.main()
