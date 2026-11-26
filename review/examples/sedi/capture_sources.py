"""Acquire SEDI public sources locally; no assessment or publication claim."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 16 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Unexpected redirect; inspect source inventory")


def capture(inventory, output, opener=None):
    output = Path(output).resolve()
    # Prevent accidental publication from this checkout.
    checkout = ROOT.parents[2]
    if output.is_relative_to(checkout):
        raise ValueError("Output must be outside the repository")
    output.mkdir(parents=False, exist_ok=False)
    opener = opener or build_opener(NoRedirect())
    entries = []
    for entry in inventory["sources"]:
        source_id, url = entry["id"], entry["url"]
        if not source_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in source_id):
            raise ValueError("Unsafe source identifier")
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.netloc not in {"sedi.utah.gov", "le.utah.gov"}
                or parsed.query or parsed.fragment):
            raise ValueError("Unexpected source URL")
        expected = "application/pdf" if parsed.path.endswith(".pdf") else "text/html"
        with opener.open(Request(url, headers={"Accept-Encoding": "identity",
                                               "User-Agent": "RAHP-SEDI-source-capture/1"}),
                         timeout=30) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError("Unexpected source response")
            if response.headers.get_content_type() != expected:
                raise ValueError("Unexpected media type")
            if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                raise ValueError("Unexpected content encoding")
            data = response.read(MAX_BYTES + 1)
            if not data or len(data) > MAX_BYTES:
                raise ValueError("Empty or oversized source")
            if expected == "application/pdf" and not data.startswith(b"%PDF-"):
                raise ValueError("Invalid PDF signature")
        name = source_id + (".pdf" if expected == "application/pdf" else ".html")
        with (output / name).open("xb") as handle:
            handle.write(data)
        entries.append({"id": source_id, "url": url, "path": name,
                        "media_type": expected, "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "retrieved_at": datetime.now(timezone.utc).isoformat()})
    # Manifest only exists for complete captures. Failed runs leave partial files
    # for inspection, never a success manifest.
    manifest = {"kind": "local-web-acquisition", "source_identity": "unqualified",
                "redistribution": "not-established", "files": entries}
    with (output / "capture-manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    inventory = json.loads((ROOT / "source-inventory.json").read_text(encoding="utf-8"))
    manifest = capture(inventory, args.output)
    print(f"Captured {len(manifest['files'])} sources; source identity remains unqualified")


if __name__ == "__main__":
    main()
