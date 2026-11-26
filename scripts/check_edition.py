#!/usr/bin/env python3
"""Machine checks for the reader edition in edition/ (or a copy synced elsewhere, via --root).

Fails (exit 1) on any of:
- an archived HTML page that the map does not account for, or a page the map promises that is missing
- per-folder counts of mapped pages that do not match archive/PAGE-INDEX.csv
- missing required frontmatter (title, description, source, archive_path, source_sha256)
- leftover legacy markup: <span, <font, <table, links to .htm/.html, "Back to" lines, CES copyright lines
- empty pages
- broken internal links or images
- assets that are not byte-identical to the archive
"""

from pathlib import Path, PurePosixPath
from urllib.parse import unquote
import argparse
import csv
import collections
import hashlib
import os
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from edition_map import MAP, P, M, D, X  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive/www.livingneighborhoods.org"
REQUIRED = ["title", "description", "source", "archive_path", "source_sha256"]
HAND_WRITTEN = {"index", "about/index", "running-a-project/index", "tools/index"}
LEFTOVERS = [
    (re.compile(r"<span\b", re.I), "<span markup"),
    (re.compile(r"<font\b", re.I), "<font markup"),
    (re.compile(r"<table\b", re.I), "<table markup"),
    (re.compile(r"\]\((?!https?:)[^)\s]*\.s?html?(#[^)]*)?\)", re.I), "internal link to .htm page"),
    (re.compile(r"(?im)^\W*back to\b"), "'Back to' line"),
    (re.compile(r"(?im)^\W*©\s*\d{4}\s*CES\b"), "old CES copyright line"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def front_and_body(text):
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    front = {}
    for line in head.splitlines():
        m = re.match(r"^([a-z0-9_]+):\s*(.*)$", line)
        if m:
            front[m.group(1)] = m.group(2).strip().strip('"')
    return front, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "edition"), help="edition root to check")
    ap.add_argument("--partial", action="store_true", help="only check pages present (for a pilot sync)")
    args = ap.parse_args()
    root = Path(args.root)
    errors = []

    # 1. coverage
    archived = {p.relative_to(ARCHIVE).as_posix() for p in ARCHIVE.rglob("*") if p.suffix.lower() in (".htm", ".html")}
    unmapped = archived - set(MAP)
    if unmapped:
        errors.append(f"archived pages missing from the map: {sorted(unmapped)}")
    stale = set(MAP) - archived
    if stale:
        errors.append(f"map entries with no archived page: {sorted(stale)}")
    for src, (role, dest, note) in MAP.items():
        if role == X and not note:
            errors.append(f"exclusion without a reason: {src}")
    pages = {dest for role, dest, _ in MAP.values() if role == P}
    if not args.partial:
        for dest in sorted(pages):
            if not (root / f"{dest}.md").is_file():
                errors.append(f"missing edition page: {dest}.md")

    # 2. per-folder counts against the page index
    index_counts = collections.Counter()
    with open(ROOT / "archive/PAGE-INDEX.csv", newline="") as f:
        for row in csv.DictReader(f):
            if row["result"] == "archived" and row["content_type"] == "text/html":
                rel = row["archive_path"].removeprefix("archive/www.livingneighborhoods.org/")
                index_counts[str(PurePosixPath(rel).parent)] += 1
    map_counts = collections.Counter(str(PurePosixPath(src).parent) for src in MAP)
    if index_counts != map_counts:
        diff = {k: (index_counts[k], map_counts[k]) for k in set(index_counts) | set(map_counts) if index_counts[k] != map_counts[k]}
        errors.append(f"per-folder page counts differ from PAGE-INDEX.csv (index, map): {diff}")

    # 3-6. each page
    md_files = sorted(p for p in root.rglob("*.md") if "_build" not in p.parts)
    for path in md_files:
        dest = path.relative_to(root).with_suffix("").as_posix()
        text = path.read_text(encoding="utf-8")
        front, body = front_and_body(text)
        need = ["title", "description"] if dest in HAND_WRITTEN else REQUIRED
        for key in need:
            if not front.get(key):
                errors.append(f"{dest}: missing frontmatter '{key}'")
        prose = re.sub(r"\*From\* Building Living Neighborhoods.*", "", body, flags=re.S).strip()
        if len(re.findall(r"[A-Za-z]{2,}", prose)) < 15 and "![" not in prose:
            errors.append(f"{dest}: page is empty or nearly empty")
        for rx, label in LEFTOVERS:
            for m in rx.finditer(body):
                errors.append(f"{dest}: {label}: {m.group(0)[:60]!r}")
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", body):
            url = m.group(1)
            if re.match(r"^[a-z]+:", url) or url.startswith("#"):
                continue
            target = (path.parent / unquote(url.split("#")[0])).resolve()
            if not target.exists():
                if args.partial and target.suffix == ".md":
                    continue
                errors.append(f"{dest}: broken link {url}")

    # 7. assets byte-identical
    assets = root / "assets"
    n_assets = 0
    if assets.is_dir():
        for a in assets.rglob("*"):
            if a.is_file():
                n_assets += 1
                src = ARCHIVE / a.relative_to(assets)
                if not src.is_file():
                    errors.append(f"asset not in archive: {a.relative_to(root)}")
                elif a.stat().st_size != src.stat().st_size or sha(a) != sha(src):
                    errors.append(f"asset differs from archive: {a.relative_to(root)}")

    roles = collections.Counter(r for r, _, _ in MAP.values())
    if errors:
        for e in errors:
            print("FAIL", e)
        print(f"{len(errors)} problems")
        sys.exit(1)
    print(f"edition ok: {len(md_files)} pages, {n_assets} assets; map: {len(MAP)} archived pages "
          f"({roles[P]} pages, {roles[M]} merged, {roles[D]} duplicates, {roles[X]} excluded)")


if __name__ == "__main__":
    main()
