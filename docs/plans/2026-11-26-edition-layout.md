---
title: Living Neighborhoods edition — reader layout
date: 2026-11-26
status: draft
---

# Living Neighborhoods edition — reader layout

The page-by-page map is `scripts/edition_map.py`; this doc explains it.

## What the old site was

Two halves. **Action**: an action page with six phases ("packets"), each linking to steps in `actions/`, plus a workbook and a Java drawing pad. **Theory & Examples**: basics, generative codes, creating community, main steps of work, a Library of Unfoldings (`unfoldings/`, an older and broader set of steps), example neighbourhoods, and an archive of papers. Underneath sit an older copy of much of the site (`ht-1`, "Environmental Structure"), Nature of Order reference snippets (`noorefs`), frames, a click-through terms page and "one time message" interstitials (`ht-2`). Navigation ran through a JavaScript menu and frames, which is why it was so easy to get lost.

About 60 of the 209 pages are duplicates: the same text at two addresses, an `ht-1` older version of an `ht-0` page, or a Library of Unfoldings version of an action step.

## Reader structure

Under `works/living-neighborhoods/` in the wiki (and `edition/` here):

| Section | What it is | Pages |
|---|---|---|
| `index` | What the collection is, who made it, four ways in: do it (generative code), understand it (ideas), see it (examples), go deeper (library) | hand-written |
| `start-here` | The original welcome (who it is for) and the overall process | 1 |
| `generative-code/` | The heart: six phases in order, each a folder with an intro and its steps: 1 startup and vision, 2 diagnosis, 3 density, 4 modifying the code, 5 public spaces, 6 building volumes | 34 |
| `unfoldings/` | The Library of Unfoldings steps not already in the six phases: survey, land tenure, zoning, cars, foundations, colour and light, who designs, community discussion | 13 |
| `running-a-project/` | People, money and contracts: main steps of work, creating community, developers and their charter, main contract and craftsperson's subcontract, construction organisation, conversations, writing a generative code | 11 |
| `examples/` | Eishin, Mexicali, West Dean, Fresno, Schumacher College, Strood, Samarkand, Back of the Moon (Texas), Santa Rosa, Agate, Komagome, St Mark's, a village story | 14 |
| `ideas/` | The theory: generative codes, key features, morphogenesis, the order things are done, wholeness, the fifteen properties restated for neighbourhoods, pattern languages, relationship, and one page gathering the Nature of Order references | 14 |
| `library/` | Papers (the 25 PDFs, listed with descriptions) and essays and interviews | 8 |
| `tools/` | The workbook and workpads; the drawing pad, with a note that its Java applet no longer runs | 4 |
| `about/` | This edition: authors, CES, provenance, crawl date, what was merged or left out, old URL → new page concordance; the original services, contact and terms pages as historical records | hand-written + 3 |

Order in the sidebar follows that table: do, then understand, then see.

## Rules

- **Canonical version**: newest wins (`ht-0` over `ht-1`; the phase step in `actions/` over its Library of Unfoldings copy). Where a variant adds real material it is merged as a section ("Earlier version" or the variant's own title); otherwise it is listed as a duplicate in About.
- **Page titles** in plain words, sentence case. Old shouty titles ("VISION", "Environmental Structure -- Neighborhoods -- …") are dropped.
- **Steps keep their phase order** with previous/next links, so the code reads like a manual.
- **Every page** has `title`, `description`, `source` (original URL), `archive_path`, `source_sha256`, and for merged pages a `merged_from` list.
- **Removed**: legacy menus, "Back to…" links, spacer images, repeated "© 2006 CES" lines (one credit in the footer of every page instead), font and span markup, layout tables.
- **Images and PDFs** at full size, at their original relative paths under `assets/`, byte-identical to the archive.
- **Links** to pages that were dead on the live site are unlinked and listed in the review queue (the Wayback task may recover some).
- **Dead applets** (drawing pad, unfolding movies): the page stays, with a short note; reviving them is a separate task.
- **Third-party articles** in the library (Science in Society, Science & Theology News, a newspaper series) are kept, credited and flagged in the review queue.

## Build with Alexander hooks

The generative code is the backbone the wiki's room/house/hamlet pages link into: hamlet-scale steps (main center, pedestrian centers, positive space, density, car positions, land tenure), house-scale (building fronts, building shape, foundations and plinth, colour and light), process and money (`running-a-project/`), and the examples (Eishin, Mexicali first).
