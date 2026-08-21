# Living Neighbourhoods Edition Implementation Plan

**Goal:** Preserve the Living Neighbourhoods website and publish a cleaner, searchable Markdown edition through Flowershow.

**Architecture:** Keep a direct crawl under `archive/` as the source snapshot. Convert its HTML pages and assets into the separate `site/` content root, then add curated landing pages and Flowershow configuration around the converted material.

**Tech Stack:** Python standard library, Pandoc, Markdown, Flowershow `config.json`, shell verification.

## Delivery decisions

1. Archive the live site in its own directory, including images, PDFs, JavaScript, and other linked files.
2. Publish only `site/`, keeping the archive out of the public Flowershow content tree.
3. Preserve the recognizable top-level structure—Action & Practice, Theory & Examples, and Archive—while improving entry points and page readability.
4. Record unavailable source URLs rather than fabricating replacements.
5. Make the archive and conversion repeatable through scripts, with a machine-checkable verification command.

## Follow-up review queue

- Review converted Markdown pages for tables, image captions, and legacy JavaScript artifacts.
- Decide whether additional pages should be promoted into curated landing pages.
- Connect the repository or `site/` directory to Flowershow and inspect the rendered navigation.
- Add screenshots to future changelog entries when a visual site milestone is reviewed.
