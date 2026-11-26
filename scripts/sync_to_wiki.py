#!/usr/bin/env python3
"""Copy edition pages and the assets they use into the Alexander Wiki.

    python3 scripts/sync_to_wiki.py --wiki ~/src/natureoforder/alexander-wiki --pilot
    python3 scripts/sync_to_wiki.py --wiki ~/src/natureoforder/alexander-wiki --all

Pages land under <wiki>/works/living-neighborhoods/. In a partial sync, links to edition pages
that are not (yet) in the wiki are pointed at the original page on livingneighborhoods.org, so
nothing breaks. Build-only frontmatter (`edited`, `generated`) is dropped. Assets are copied
byte-for-byte. Re-running is safe: synced files are overwritten from edition/.
"""

from pathlib import Path
import argparse
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
EDITION = ROOT / "edition"
TARGET = "works/living-neighborhoods"

PILOT = [
    "index",
    "start-here",
    "generative-code/index",
    "generative-code/5-public-spaces/index",
    "generative-code/5-public-spaces/pedestrians-first",
    "generative-code/5-public-spaces/main-center",
    "generative-code/5-public-spaces/positive-space",
    "generative-code/5-public-spaces/recursive-positive-space",
    "examples/eishin-campus",
]


def source_url(dest):
    path = EDITION / f"{dest}.md"
    m = re.search(r'^source: (".*")$', path.read_text(encoding="utf-8"), re.M)
    return json.loads(m.group(1)) if m else "https://www.livingneighborhoods.org/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", required=True)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", action="store_true")
    group.add_argument("--all", action="store_true")
    args = ap.parse_args()

    out_root = Path(args.wiki).expanduser() / TARGET
    if args.all:
        pages = sorted(p.relative_to(EDITION).with_suffix("").as_posix()
                       for p in EDITION.rglob("*.md") if "_build" not in p.parts)
    else:
        pages = PILOT
    page_set = set(pages)
    assets = set()

    for dest in pages:
        src = EDITION / f"{dest}.md"
        text = src.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^(edited|generated): .*\n", "", text)

        def fix(m):
            bang, label, url = m.group(1), m.group(2), m.group(3)
            if re.match(r"^[a-z]+:", url) or url.startswith("#"):
                return m.group(0)
            target = (src.parent / url.split("#")[0]).resolve()
            try:
                rel = target.relative_to(EDITION.resolve()).as_posix()
            except ValueError:
                return m.group(0)
            if rel.startswith("assets/"):
                assets.add(rel)
                return m.group(0)
            if rel.endswith(".md"):
                linked = rel[:-3]
                if linked in page_set:
                    return m.group(0)
                if (EDITION / rel).exists() and not bang:
                    return f"[{label}]({source_url(linked) if 'source:' in (EDITION / rel).read_text() else 'https://www.livingneighborhoods.org/'})"
            return m.group(0)

        text = re.sub(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)", fix, text)
        out = out_root / f"{dest}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")

    if args.all:  # every asset, including PDFs that no page links to
        assets |= {p.relative_to(EDITION).as_posix() for p in (EDITION / "assets").rglob("*") if p.is_file()}
    for a in sorted(assets):
        target = out_root / a
        if not target.exists() or target.stat().st_size != (EDITION / a).stat().st_size:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(EDITION / a, target)
    print(f"synced {len(pages)} pages and {len(assets)} assets to {out_root}")


if __name__ == "__main__":
    main()
