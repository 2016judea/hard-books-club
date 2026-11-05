# Intellectual Reads

**Live:** https://intellectualreads.substack.com

A paid Substack for reading the books people start and don't finish.

- **Free:** one book review a week, from Aidan's own reading archive (485 books logged on Goodreads).
- **Paid ($8/mo, $70/yr):** one hard book a quarter, read slowly over 12 weeks. Each week brings his chapter notes, his saved quotes and a discussion thread.
- **Cohort 1:** *Blood Meridian*, Cormac McCarthy. Starts Monday 2027-01-04 and ends 2027-03-28.

## Launch timeline

| Date | What happens |
|---|---|
| by 2026-11-15 | Publication set up: name, about page, tiers, welcome email |
| 2026-11-16 | Free archive reviews start, one every Monday (`archive/queue.csv`). Daily Notes start the same day (`notes/queue.csv`) |
| 2026-11-30 | The Blood Meridian review runs as the free post the week of the announcement |
| 2026-12-01 | Cohort announced. Paid and founding-member tiers open |
| 2026-12-01 → 2027-01-03 | Founding-member pricing window. Recommendation swaps go out (`growth/swaps.md`) |
| 2027-01-04 | Cohort 1, week 1: chapters I–II |
| 2027-03-28 | Cohort 1 ends. The 12 weeks become the evergreen guide |

On Substack, "Founding Member" is a fourth plan priced **above** the annual one, for
readers who want to pay more. It isn't a discount. If what you want is a launch
discount, that's a separate time-limited offer on the $70 plan. The price is your call.
Nothing here sets it.

## What's in the repo

| Path | What it is |
|---|---|
| `DATA_MODEL.md` | The ideal model, written first, with a field-by-field check against the real data |
| `cohorts/blood-meridian/syllabus.md` | 12 weeks, chapters split evenly by measured length, his 4 saved quotes placed by chapter, DRAFT prompts, empty slots for his notes |
| `cohorts/blood-meridian/split.json` | Word counts per chapter and the 12-week split |
| `archive/queue.csv` | 52 weekly free-tier reviews, existing text first |
| `notes/queue.csv` | 90 daily Notes, each one of his saved quotes, verbatim, with no captions |
| `growth/swaps.md` | 20 Substacks to ask for swaps, 20 subreddits, 8 Twin Cities bookstores |
| `brand/covers/<slug>/` | Three cover options per drafted post (first edition, then his imprints), with `sources.csv` |
| `archive/buy_links.csv` | Amazon and eBay links per post, with each eBay search's result count on 2026-10-11 |
| `scripts/` | The generators. Re-run them, never hand-edit the CSVs |

## Post checklist

- Every post opens with a vintage cover: first edition, or Vintage International / Picador / Penguin Classics.
- Every post closes with Buy it: Amazon for the in-print paperback, eBay saved searches for his preferred vintage editions.

## What still needs him

- **Chapter notes**, 12 empty slots in the syllabus. His prose, and nobody else writes it.
- **Discussion prompts** are marked DRAFT. Approve, rewrite or cut.
- **Archive weeks 12–52** are flagged `needs_writing=Y`. Each has a fragment of 14–91 words. Weeks 1–11 have 100+ words of his own review text and can go out as written.
- **Founding-member price**, the publication name, and every send, post and swap request.

## Rebuild

```sh
python3 scripts/build_queues.py            # archive/queue.csv + notes/queue.csv
python3 scripts/split_chapters.py <text>   > cohorts/blood-meridian/split.json
python3 scripts/locate_quotes.py  <text>   # which chapter each saved quote is in
```

Sources are in `~/Desktop/workspace/writing-topology/data/personal_corpus/`
(`goodreads_reads.json`, `quotes.json`, `book_review_inventory.json`). The book's text is
in copyright, so it's read from a local copy and never committed. Only counts and chapter
numbers come out of it.

Private repo. The reviews and quotes are his, and the quoted passages belong to their
authors.

*2026-10-18 note: the daily Notes queue was moved to start 2026-10-12 (commit bfe2dd8), five weeks before the archive reviews; `notes/queue.csv` and `scripts/build_queues.py` now agree on that date.*
