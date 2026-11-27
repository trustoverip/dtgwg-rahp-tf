"""Verify an exact, locally supplied SEDI ZIP and its substantive members.

No extraction, network access, publisher authentication or assurance decision.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

ROOT = Path(__file__).resolve().parent
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_MEMBER = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_archive(path, manifest):
    path = Path(path)
    with path.open("rb") as handle:
        payload = handle.read(MAX_ARCHIVE + 1)
    if len(payload) > MAX_ARCHIVE or digest(payload) != manifest["sha256"]:
        raise ValueError("Archive digest or size mismatch")
    import io
    records = manifest["files"]
    expected = {r["path"]: r for r in records}
    if not expected or len(expected) != len(records):
        raise ValueError("Empty or duplicate manifest paths")
    seen = set()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        infos = archive.infolist()
        if len({i.filename for i in infos}) != len(infos):
            raise ValueError("Duplicate ZIP member")
        if sum(i.file_size for i in infos) > MAX_TOTAL:
            raise ValueError("Archive expanded size exceeds limit")
        for info in infos:
            name = info.filename
            parts = PurePosixPath(name).parts
            if (not parts or name.startswith("/") or "\\" in name
                    or any(p in ("", ".", "..") for p in name.rstrip("/").split("/"))
                    or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError("Unsafe ZIP member")
            if info.is_dir() or parts[0] == "__MACOSX":
                continue
            if name not in expected:
                raise ValueError("Unexpected substantive member")
            record = expected[name]
            if info.file_size != record["bytes"] or info.file_size > MAX_MEMBER:
                raise ValueError("Member size mismatch")
            data = archive.read(info)
            if digest(data) != record["sha256"]:
                raise ValueError("Member digest mismatch")
            seen.add(name)
    if seen != set(expected):
        raise ValueError("Missing substantive member")
    return {"archive_sha256": manifest["sha256"], "verified_members": len(seen),
            "source_integrity": "verified-local-input",
            "publisher_release_identity": "not-established"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "archive-manifest.json").read_text(encoding="utf-8"))
    print(json.dumps(verify_archive(args.archive, manifest), indent=2))


if __name__ == "__main__":
    main()
