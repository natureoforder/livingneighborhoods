# Agent guidance

## Project shape

- `archive/` is the preservation layer. Keep the crawled HTML and linked assets intact; do not use it as the Flowershow content root.
- `site/` is the editable Markdown publication and Flowershow content root.
- `scripts/archive_site.py` refreshes the archive from the source site.
- `archive/www.livingneighborhoods.org/manifest.json` is the URL, status, checksum, and provenance ledger for the live snapshot.
- `scripts/verify_archive.py` checks archived-file integrity and link-graph closure.
- `scripts/convert_site.py` converts archived HTML to Markdown and copies non-HTML assets into `site/`.
- `scripts/verify.sh` is the machine-checkable done condition.
- `NEXT.md` is the ordered handoff plan; archive hardening and historical recovery precede conversion work.

## Working rules

- Preserve the original source URL in converted page frontmatter.
- Keep the broad source navigation recognizable, but improve page titles, landing pages, links, and readability when converting.
- Treat `archive/` as immutable evidence of what was retrieved on its recorded crawl date. If refreshing it, record the new date and any changed failures in `ARCHIVE-METADATA.txt`.
- Keep live-crawl files and any future Wayback recovery in separate trees with separate provenance. Never overwrite the live snapshot with a historical capture.
- Do not publish `archive/` through Flowershow. Publish `site/` (for example, with `fl --yes ./site`) or connect `site/` as the repository's Flowershow content root.
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
