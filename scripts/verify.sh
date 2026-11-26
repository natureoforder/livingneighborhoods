#!/bin/sh
set -eu

test -f README.md
test -f AGENTS.md
test -f changelog.md
test -f edition/index.md
test -f edition/start-here.md
test -f edition/generative-code/index.md
test -f scripts/edition_map.py
test -f archive/www.livingneighborhoods.org/ARCHIVE-METADATA.txt
test -f archive/www.livingneighborhoods.org/manifest.json
test -f archive/PAGE-INDEX.csv

python3 -m unittest discover -s tests -v
python3 scripts/verify_archive.py

html_count=$(find archive/www.livingneighborhoods.org -type f \( -name '*.htm' -o -name '*.html' \) | wc -l | tr -d ' ')
raw_count=$(find raw -type f -name '*.md' | wc -l | tr -d ' ')
markdown_count=$(find edition -type f -name '*.md' \! -path '*/_build/*' | wc -l | tr -d ' ')
asset_count=$(find edition/assets -type f | wc -l | tr -d ' ')

test "$html_count" -ge 200
test "$raw_count" -eq "$html_count"
test "$markdown_count" -ge 90
test "$asset_count" -ge 50
python3 scripts/check_edition.py

git diff --check
printf 'verified: %s HTML pages, %s raw pages, %s edition pages, %s edition assets\n' "$html_count" "$raw_count" "$markdown_count" "$asset_count"
