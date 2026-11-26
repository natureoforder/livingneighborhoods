---
title: Living Neighborhoods edition — what we are doing, in one page
date: 2026-11-26
status: agreed with Rufus, 26 Nov
---

# Living Neighborhoods edition — what we are doing

## The problem

livingneighborhoods.org has about 100 pages of real content spread across 209 HTML files in the authors' working folders (`ht-0/`, `ht-1/`, `actions/`, `packets/`, `unfoldings/`, `noorefs/`…). About 60 files are copies or older versions of other files. You reach things through frames and a JavaScript menu, so it's easy to get lost.

## What we are doing about it

Three steps, each in its own place:

1. **Preserve** (this repo, `archive/`): the crawl of the live site, untouched. Done.
2. **Re-route and clean** (this repo, `edition/`): every one of the 209 files gets a decision: it becomes a page, is merged into another page, is a duplicate, or holds nothing (a frame, a menu, a notice). The pages are cleaned of old HTML and laid out in a new structure for readers. The decisions are listed in `scripts/edition_map.py`; the reasoning is in `2026-11-26-edition-layout.md`. Done for all 209; most hub pages still need hand-polishing.
3. **Publish** (Alexander Wiki): copy `edition/` into the wiki. A pilot of nine pages is live now.

## We do not keep the original URLs

The old folder names mean nothing to a reader, so the new structure replaces them. Every page keeps its original URL in its frontmatter and links to it at the foot, and the About page has a full table from each old URL to its new page. Examples:

| Original URL | What it is | New page |
|---|---|---|
| `packets/publicspaces-phase.htm` | phase 5 overview | `generative-code/5-public-spaces/` |
| `actions/maincenter.htm` | a step in phase 5 | `generative-code/5-public-spaces/main-center` |
| `unfoldings/maincenter.htm` | older copy of the same step | duplicate, not published |
| `ht-0/eishincampus.htm` + `ht-0/eishincollege.htm` | the authors' account of Eishin | `examples/eishin-campus` |
| `ht-1/implementation.htm` | older version of "main steps of work", with extra material | merged into `running-a-project/main-steps-of-work` |
| `noorefs/*.htm` (16 small files) | Nature of Order cross-references | one page, `ideas/nature-of-order-references` |
| `ht-2/*.htm` | "one time message" pop-ups | left out |

## The new structure (the routing)

It follows the original site's own two halves, Action and Theory & Examples, but in reading order: do it, then understand it, then see it.

```
living-neighborhoods/                 entry page: what it is, who wrote it, ways in
├── start-here                        the authors' welcome: who it is for, how the process works
├── generative-code/                  the core: the step-by-step method
│   ├── 1-startup-and-vision/         parameters, people, vision, basemap, poetic pattern language
│   ├── 2-diagnosis/                  wholeness, precious places, repair, latent centers, GPS…
│   ├── 3-density/
│   ├── 4-modifying-the-code/         entities, baseline code, writing a generative code…
│   ├── 5-public-spaces/              pedestrians first, main center, positive space…
│   └── 6-building-volumes/           building fronts, building shape
├── unfoldings/                       further steps from the older "Library of Unfoldings": surveying, land tenure, zoning, cars, foundations, colour and light
├── running-a-project/                main steps of work, community, developers, contracts, construction
├── examples/                         Eishin, Mexicali, West Dean, Fresno, Strood, Samarkand, Texas…
├── ideas/                            generative codes, wholeness, fifteen properties, Nature of Order references
├── library/                          papers (25 PDFs), essays, interviews
├── tools/                            workbook, drawing pad (dead Java applet)
└── about/                            how the edition was made; old URL → new page table
```

Eishin sits under `examples/` because it is the authors' own Living Neighborhoods account of Eishin, one of their example projects. It only makes sense inside the Living Neighborhoods section, which is where it should live.

## Where it goes in the wiki: correcting the pilot

I put the pilot under `works/living-neighborhoods/`, reading your "reference material, like a folder, maybe under works" literally. You're right that that is wrong: Works is a shelf of one-page entries (one per book), and a whole section doesn't belong there.

Proposal:

- **The edition becomes the wiki's `living-neighborhoods/` section**, replacing the current three thin pages (`index`, `collection`, `first-walk`). The nav's existing "Living Neighborhoods" link then leads straight into it. This was the original brief's direction.
- **Works gets one entry page**, `works/2006-building-living-neighborhoods.md`, like the other books: authors, date, what it is, and a link into the section.
- **The wiki's own Eishin pages** (`practice/eishin-campus` and its reading) stay where they are and cross-link to `living-neighborhoods/examples/eishin-campus`, which is the authors' first-hand account.
- **Build with Alexander** later links into `living-neighborhoods/generative-code/…` steps, rather than copying them.

Moving the nine pilot pages from `works/living-neighborhoods/` to `living-neighborhoods/` is a single re-sync.

## Order from here

1. You OK the placement above. I move the pilot, add the Works entry, and replace the thin pages.
2. Hand-polish the remaining hub pages (phases 1–4 and 6, unfoldings, examples, ideas, library).
3. Sync the whole edition.
4. Later, separately: Wayback recovery of dead links, the unfolding movies, the permission letter.
