#!/usr/bin/env python3
"""Verify archive checksums, resolved failures, and link-graph closure."""

from hashlib import sha256
import json
from pathlib import Path
import sys

try:
    from scripts.archive_site import links_from
    from scripts.build_archive_index import render_page_index
except ModuleNotFoundError:  # direct execution adds scripts/, not the repo root
    from archive_site import links_from
    from build_archive_index import render_page_index


def verify_manifest(manifest_path):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    represented = {
        url
        for record in records
        for url in (record.get("url"), record.get("final_url"))
        if url
    }
    errors = []

    for record in records:
        url = record.get("url", "<unknown>")
        local_path = record.get("local_path")
        if not local_path:
            if not isinstance(record.get("status"), int):
                errors.append(f"transient or unclassified failure: {url}")
            continue

        path = Path(local_path)
        if not path.is_file():
            errors.append(f"missing archived file: {path} ({url})")
            continue
        content = path.read_bytes()
        if len(content) != record.get("bytes"):
            errors.append(f"byte count mismatch: {path}")
        if sha256(content).hexdigest() != record.get("sha256"):
            errors.append(f"checksum mismatch: {path}")

        content_type = record.get("content_type") or ""
        if any(kind in content_type for kind in ("html", "css", "javascript")):
            for link in links_from(content, content_type, record.get("final_url") or url):
                if link not in represented:
                    errors.append(f"referenced URL not represented in manifest: {link} ({path})")

    return sorted(set(errors))


def verify_page_index(manifest_path, index_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    index_path = Path(index_path)
    if not index_path.is_file():
        return [f"missing page index: {index_path}"]
    expected = render_page_index(manifest)
    actual = index_path.read_text(encoding="utf-8")
    if actual != expected:
        return [f"page index is out of date: {index_path}"]
    return []


def main():
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "archive/www.livingneighborhoods.org/manifest.json"
    )
    errors = verify_manifest(manifest_path)
    index_path = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        Path("archive/PAGE-INDEX.csv") if len(sys.argv) == 1 else None
    )
    if index_path:
        errors.extend(verify_page_index(manifest_path, index_path))
    if errors:
        print("Archive verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest["records"]
    downloaded = sum(bool(record.get("local_path")) for record in records)
    failed = len(records) - downloaded
    print(f"archive verified: {downloaded} files, {failed} resolved source failures, closed link graph")


if __name__ == "__main__":
    main()
