"""Verify explicitly retained files; no fetching or authenticity decision is made."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath


def retained_file(root: Path, name: str) -> Path:
    """Accept canonical relative POSIX paths to regular, non-symlink files only."""
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError("Unsafe retained path")
    relative = PurePosixPath(name)
    if relative.is_absolute() or any(p in ('', '.', '..') for p in name.split('/')):
        raise ValueError(f"Unsafe retained path: {name}")
    base = root.resolve(strict=True)
    path = base
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Symlink retained path: {name}")
    if not path.is_file() or not path.resolve().is_relative_to(base):
        raise ValueError(f"Missing or unsafe retained file: {name}")
    return path


def verify_source(root: Path, manifest_name: str = 'source-manifest.json') -> dict:
    """Reject malformed inventories and verify SHA-256 and Git blob identity."""
    manifest = json.loads(retained_file(root, manifest_name).read_text(encoding='utf-8'))
    if (not isinstance(manifest, dict) or not isinstance(manifest.get('repository'), str)
            or not manifest['repository'] or not isinstance(manifest.get('commit'), str)
            or not re.fullmatch(r'[0-9a-f]{40}', manifest['commit'])
            or not isinstance(manifest.get('files'), list) or not manifest['files']):
        raise ValueError('Manifest requires repository, immutable commit and nonempty files')
    seen, upstream_seen = set(), set()
    for entry in manifest['files']:
        if not isinstance(entry, dict):
            raise ValueError('Malformed source entry')
        name = entry.get('path')
        path = retained_file(root, name)
        upstream = entry.get('upstream_path')
        if (not isinstance(upstream, str) or not upstream or upstream.startswith('/')
                or '\\' in upstream or any(p in ('', '.', '..') for p in upstream.split('/'))):
            raise ValueError('Unsafe upstream path')
        if name in seen or upstream in upstream_seen:
            raise ValueError(f'Duplicate source entry: {name}')
        seen.add(name)
        upstream_seen.add(upstream)
        expected_url = (f"https://github.com/{manifest['repository']}/blob/"
                        f"{manifest['commit']}/{upstream}")
        if entry.get('url') != expected_url:
            raise ValueError(f'Source URL disagrees with identity: {name}')
        for field, length in [('sha256', 64), ('git_blob_sha', 40)]:
            if not isinstance(entry.get(field), str) or not re.fullmatch(r'[0-9a-f]{%d}' % length, entry[field]):
                raise ValueError(f'Malformed {field}: {name}')
        data = path.read_bytes()
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError(f'SHA-256 mismatch: {name}')
        if hashlib.sha1(blob).hexdigest() != entry['git_blob_sha']:
            raise ValueError(f'Git blob mismatch: {name}')
    return manifest
