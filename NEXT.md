# Next

## Current checkpoint

Archive preservation comes before conversion or visual redesign.

The 2026-08-21 live-site crawl now follows the legacy menu, ordinary links, frames, inline JavaScript references, CSS references, and linked static files recursively until the same-site link graph closes. It currently records:

- 1,321 referenced URLs
- 797 downloaded resources
- 209 downloaded HTML pages
- 207,463,185 downloaded bytes
- 524 source URLs returning explicit HTTP 400/404 responses
- zero transient or unclassified failures

An initial Internet Archive CDX comparison found at least 57 historical paths that are no longer present in the live snapshot, including older page variants, two PDFs, and several images. They belong in the separately provenance-tracked recovery phase below; some repeated captures share the digest of an old soft-404 page and must not be mistaken for recoverable content.

The source has no sitemap. “Complete” therefore means all static same-site resources reachable from the homepage, legacy menu, and recursively discovered references—not proof that no unlinked server files exist.

## 1. Independently harden the archive

- [ ] Compare the manifest against search-engine indexes and the Internet Archive CDX API to identify live or historical URLs that are not linked by the current site.
- [ ] Crawl any additional live same-site URLs found by that independent inventory and rerun link-closure verification.
- [ ] Record external dependencies referenced by source pages in a separate manifest without silently copying third-party sites.
- [ ] Create a snapshot tag/release once the independent inventory agrees with the live crawl.
- [ ] Consider producing a WARC alongside the browsable file tree for preservation-tool interoperability.

Done when the live crawl, independent URL inventory, checksums, and source-failure ledger agree, and `scripts/verify.sh` exits 0 from a fresh checkout.

## 2. Recover dead historical material

- [ ] Query the Internet Archive for the 524 URLs that are dead on the live host.
- [ ] Recover available historical files into a separate `archive/recovered/` tree; never mix them into the 2026-08-21 live snapshot.
- [ ] Store original URL, capture timestamp, Wayback URL, checksum, and recovery status for every recovered file.
- [ ] Distinguish genuine missing content from malformed Microsoft-generated and browser-support references.

Done when every dead live reference is classified as recovered, unavailable, malformed, or intentionally excluded.

## 3. Rebuild the Markdown edition from the complete inventory

- [ ] Convert all 209 archived HTML pages rather than the initial 44-page subset.
- [ ] Rewrite `.htm` links to Flowershow routes and add a link checker that fails on broken internal links or images.
- [ ] Remove legacy navigation, JavaScript handlers, spacer images, duplicated copyright blocks, and presentational tables while preserving substantive text, images, captions, and source order.
- [ ] Give every page accurate title, description, original URL, archive path, and source checksum frontmatter.
- [ ] Create a review queue for conversions requiring human judgment instead of treating them as mechanically complete.

Done when every archived content page has a readable Markdown counterpart or an explicit exclusion reason.

## 4. Replace source-folder navigation with a reader-facing structure

- [ ] Organize the site around Start Here, Generative Code, Action & Practice, Theory, Example Neighbourhoods, and Library & Archive.
- [ ] Build phase-by-phase navigation through the generative process.
- [ ] Add audience pathways for community members, planners, developers, architects, builders, and students.
- [ ] Hide implementation directories such as `ht-0`, `ht-1`, `ht-2`, and `packets` from the public sidebar.

## 5. Improve discovery and presentation

- [ ] Enable Flowershow search if the site plan supports it.
- [ ] Add tags, aliases, a glossary, related-page links, and useful page descriptions.
- [ ] Turn Eishin, Mexicali, West Dean, Fresno, Samarkand, and other examples into visual case studies.
- [ ] Replace table-based image strips with responsive galleries and add consistent captions and alt text.
- [ ] Refine the lessflowery theme with an Alexander-inspired visual system and test desktop and mobile layouts.

## 6. Publish project transparency

- [ ] Publish `changelog.md` as `/changelog` without creating two manually maintained sources of truth.
- [ ] Expand About with crawl scope, archive date, coverage figures, known gaps, methodology, attribution, and copyright guidance.
- [ ] Show archive and conversion progress from the manifests rather than hand-maintained numbers.
