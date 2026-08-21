#!/bin/sh
set -eu

if [ ! -f archive/www.livingneighborhoods.org/ARCHIVE-METADATA.txt ]; then
  python3 scripts/archive_site.py
fi
python3 scripts/convert_site.py
scripts/verify.sh
