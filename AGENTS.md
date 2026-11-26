# Agent guidance

## Project shape

- `archive/` is the preservation layer. Keep the crawled HTML and linked assets intact; do not use it as the Flowershow content root.
- `raw/` is machine Markdown of every archived page (`scripts/convert_raw.py`); never hand-edit it.
- `edition/` is the reader edition, built by `scripts/build_edition.py` from the page map `scripts/edition_map.py` (layout: `docs/plans/2026-11-26-edition-layout.md`). Pages with `edited: true` are hand-edited and never overwritten. `scripts/check_edition.py` checks it. It is synced into the Alexander Wiki's `living-neighborhoods/` section (plus one Works entry, `works/2006-building-living-neighborhoods`) by `scripts/sync_to_wiki.py`.
- `scripts/archive_site.py` refreshes the archive from the source site.
- `archive/www.livingneighborhoods.org/manifest.json` is the URL, status, checksum, and provenance ledger for the live snapshot.
- `archive/PAGE-INDEX.csv` is the human-readable inventory of archived and failed page requests; regenerate it with `scripts/build_archive_index.py` after any manifest change.
- `scripts/verify_archive.py` checks archived-file integrity and link-graph closure.
- `scripts/verify.sh` is the machine-checkable done condition.
- Plan: `docs/plans/2026-11-26-plan.md`. Tasks live in Beads (epic `ln-93z`); `NEXT.md` is superseded history.
- `git push` also pushes Beads through `.beads/hooks/pre-push`; `bd dolt push` is the manual fallback.

## Working rules

- Preserve the original source URL in converted page frontmatter.
- Keep the broad source navigation recognizable, but improve page titles, landing pages, links, and readability when converting.
- Treat `archive/` as immutable evidence of what was retrieved on its recorded crawl date. If refreshing it, record the new date and any changed failures in `ARCHIVE-METADATA.txt`.
- Keep live-crawl files and any future Wayback recovery in separate trees with separate provenance. Never overwrite the live snapshot with a historical capture.
- Do not publish `archive/`. The edition is published through the Alexander Wiki, not from this repo.
- Run `scripts/verify.sh` before handing off work.

## Loop-engineering guard rails

- Never edit a ledger or weaken a verification check just to make the check pass.
- Never delete or rewrite the archive to resolve a Markdown or site-layout problem.
- Make source-content judgments explicit in a review queue or documentation rather than pretending they are structural pass/fail checks.
- After three identical failures, stop and report the failure and the attempted alternatives.

## Changelog

This repo keeps a `changelog.md` (dated entries, newest first). At the end
of a work session, if something worth recording actually shipped — skip
trivial sessions (typo fixes, dead ends, no visible outcome) — draft a dated
entry. Match the entry's weight to what a reader would actually care about: a
real feature/fix/content gets a title, one or two sentences, and a screenshot
if something visual shipped; small stuff (cleanup, rename, reorg, tidying) gets
one plain sentence, no bullets, no screenshot — even if several small things
happened, that's still one combined sentence, not a bullet per thing. Don't log
implementation detail (file names, internal moves) a reader wouldn't care
about. First time writing an entry in this repo, or if the format is unclear:
fetch and follow
https://raw.githubusercontent.com/life-itself/changelog/main/CONVENTION.md
