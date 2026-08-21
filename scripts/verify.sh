#!/bin/sh
set -eu

test -f README.md
test -f AGENTS.md
test -f changelog.md
test -f site/config.json
test -f site/index.md
test -f site/actions.md
test -f site/theory.md
test -f site/archive.md
test -f archive/www.livingneighborhoods.org/ARCHIVE-METADATA.txt
test -f archive/www.livingneighborhoods.org/manifest.json
test -f archive/PAGE-INDEX.csv

python3 -m unittest discover -s tests -v
python3 scripts/verify_archive.py

python3 - <<'PY'
import json
from pathlib import Path

config = json.loads(Path("site/config.json").read_text())
assert config["theme"] == "lessflowery"
assert config["showSidebar"] is True
assert config["nav"]["links"]
PY

html_count=$(find archive/www.livingneighborhoods.org -type f \( -name '*.htm' -o -name '*.html' \) | wc -l | tr -d ' ')
markdown_count=$(find site -type f -name '*.md' | wc -l | tr -d ' ')
asset_count=$(find site -type f \! -name '*.md' \! -name 'config.json' | wc -l | tr -d ' ')

test "$html_count" -ge 200
test "$markdown_count" -ge 40
test "$asset_count" -ge 50

git diff --check
printf 'verified: %s HTML pages, %s Markdown pages, %s published assets/files\n' "$html_count" "$markdown_count" "$asset_count"
