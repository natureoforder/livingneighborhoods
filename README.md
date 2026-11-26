# Living Neighbourhoods

This project preserves and reorganizes the [Living Neighbourhoods website](https://www.livingneighborhoods.org/), a valuable collection of Christopher Alexander's work that is currently difficult to browse and search.

The original site will be retained as a literal HTML archive. Alongside that archive, its content will be cleaned, converted into Markdown, and published through [Flowershow](https://flowershow.app/) as a more accessible, searchable, and browsable version.

The aim is not simply to make a copy of the existing site, but to preserve its contents while creating a clearer and more useful way to explore them.

## How it is organised

- `archive/` — the crawl of the live site (21 August 2026), untouched, with a checksummed manifest.
- `raw/` — machine Markdown of all 209 original pages.
- `edition/` — the clean reader edition, built by `scripts/build_edition.py` from the page map in `scripts/edition_map.py`, and published as the [Living Neighborhoods section of the Alexander Wiki](https://alexander.wiki/living-neighborhoods) by `scripts/sync_to_wiki.py`.

The edition replaces the original site's working folders with a structure for readers:

```
living-neighborhoods/
├── start-here           the authors' welcome and how the process works
├── generative-code/     the method: six phases, each with its steps
├── unfoldings/          further steps (surveying, land tenure, cars…)
├── running-a-project/   main steps of work, contracts, developers
├── examples/            Eishin, Mexicali, West Dean, Fresno, Strood…
├── ideas/               the theory, Nature of Order references
├── library/             papers, essays, interviews
├── tools/               workbook, drawing pad
└── about/               how it was made; old URL → new page table
```

Plan: [docs/plans/2026-11-26-edition-plan-explained.md](docs/plans/2026-11-26-edition-plan-explained.md). Tasks: Beads epic `ln-93z`.

