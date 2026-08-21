#!/usr/bin/env python3
"""Convert archived HTML pages to Markdown while preserving relative assets."""

from pathlib import Path
import shutil
import subprocess


ARCHIVE = Path("archive/www.livingneighborhoods.org")
SITE = Path("site")
CURATED = {"index.md", "actions.md", "theory.md", "archive.md", "about.md"}


def main():
    SITE.mkdir(parents=True, exist_ok=True)
    converted = 0
    copied = 0
    for source in ARCHIVE.rglob("*"):
        if not source.is_file() or source.name == "ARCHIVE-METADATA.txt":
            continue
        relative = source.relative_to(ARCHIVE)
        if source.suffix.lower() in {".htm", ".html"}:
            destination = SITE / relative.with_suffix(".md")
            if destination.name in CURATED and destination.parent == SITE:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["pandoc", "--from=html", "--to=gfm", "--wrap=none", str(source)],
                check=True,
                capture_output=True,
                text=True,
            )
            title = relative.stem.replace("-", " ").replace("_", " ").title()
            body = result.stdout.strip()
            destination.write_text(
                f"---\ntitle: {title}\nsource: https://www.livingneighborhoods.org/{relative.as_posix()}\n---\n\n{body}\n",
                encoding="utf-8",
            )
            converted += 1
        else:
            destination = SITE / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied += 1
    print(f"Converted {converted} HTML pages and copied {copied} assets/files.")


if __name__ == "__main__":
    main()
