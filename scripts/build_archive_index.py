#!/usr/bin/env python3
"""Build a human-friendly CSV index of archived and missing pages."""

import csv
import io
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse


FIELDS = (
    "source_url",
    "final_url",
    "status",
    "result",
    "content_type",
    "byte_size",
    "archive_path",
    "archive_link",
    "sha256",
    "discovered_from",
    "notes",
)


def is_page_record(record):
    """Identify page requests without treating HTML-formatted asset 404s as pages."""
    path = unquote(urlparse(record.get("url", "")).path).lower()
    requested_as_page = path.endswith(("/", ".htm", ".html")) or not path
    archived_as_html = bool(record.get("local_path")) and "html" in (
        record.get("content_type") or ""
    ).lower()
    return requested_as_page or archived_as_html


def archive_link(local_path):
    if not local_path:
        return ""
    path = Path(local_path).as_posix()
    return path.removeprefix("archive/")


def result_for(record):
    if record.get("local_path"):
        return "archived"
    if isinstance(record.get("status"), int):
        return "http_error"
    return "transient_error"


def render_page_index(manifest):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    records = sorted(manifest.get("records", []), key=lambda record: record.get("url", ""))
    for record in records:
        if not is_page_record(record):
            continue
        writer.writerow(
            {
                "source_url": record.get("url") or "",
                "final_url": record.get("final_url") or "",
                "status": record.get("status") if record.get("status") is not None else "",
                "result": result_for(record),
                "content_type": record.get("content_type") or "",
                "byte_size": record.get("bytes") or 0,
                "archive_path": record.get("local_path") or "",
                "archive_link": archive_link(record.get("local_path")),
                "sha256": record.get("sha256") or "",
                "discovered_from": record.get("discovered_from") or "",
                "notes": record.get("error") or "",
            }
        )
    return output.getvalue()


def write_page_index(manifest_path, output_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    content = render_page_index(manifest)
    Path(output_path).write_text(content, encoding="utf-8", newline="")


def main():
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "archive/www.livingneighborhoods.org/manifest.json"
    )
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("archive/PAGE-INDEX.csv")
    write_page_index(manifest_path, output_path)
    row_count = sum(1 for _ in csv.DictReader(output_path.open(encoding="utf-8")))
    print(f"wrote {row_count} page records to {output_path}")


if __name__ == "__main__":
    main()
