#!/usr/bin/env python3
"""Convert every archived HTML page to raw Markdown in raw/, mirroring the source folders.

raw/ is machine output: regenerate it at any time and never hand-edit it. Assets are not
copied; image links still point at the archive's relative paths. The clean edition is
built separately (scripts/build_edition.py).
"""

from html import unescape
from pathlib import Path
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive/www.livingneighborhoods.org"
RAW = ROOT / "raw"
BASE = "https://www.livingneighborhoods.org/"


def manifest_by_path():
    records = json.loads((ARCHIVE / "manifest.json").read_text())["records"]
    return {r["local_path"]: r for r in records if r.get("local_path")}


def html_title(html):
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", unescape(match.group(1))).strip()


def yaml_str(value):
    return json.dumps(value, ensure_ascii=False)


def main():
    records = manifest_by_path()
    if RAW.exists():
        shutil.rmtree(RAW)
    count = 0
    for source in sorted(ARCHIVE.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in {".htm", ".html"}:
            continue
        relative = source.relative_to(ARCHIVE)
        archive_path = source.relative_to(ROOT).as_posix()
        record = records.get(archive_path, {})
        html = source.read_text(encoding="utf-8", errors="replace")
        body = subprocess.run(
            ["pandoc", "--from=html", "--to=gfm", "--wrap=none"],
            input=html, check=True, capture_output=True, text=True,
        ).stdout.strip()
        frames = re.findall(r"<i?frame[^>]+src=[\"']?([^\"' >]+)", html, re.I)
        title = html_title(html) or relative.stem.replace("-", " ").title()
        front = [
            "---",
            f"title: {yaml_str(title)}",
            f"source: {yaml_str(record.get('url', BASE + relative.as_posix()))}",
            f"archive_path: {yaml_str(archive_path)}",
            f"source_sha256: {yaml_str(record.get('sha256', ''))}",
        ]
        if frames:
            front.append(f"frames: {yaml_str(frames)}")
        front.append("---")
        destination = RAW / relative.with_suffix(".md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("\n".join(front) + "\n\n" + body + "\n", encoding="utf-8")
        count += 1
    print(f"Converted {count} HTML pages into {RAW.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
