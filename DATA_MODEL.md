# Data model — Hard Books Club

Written from the need alone, before looking at what data exists (BUSINESS.md rule 5).
The need: a reader who wants to finish a hard book gets a weekly push, a guide who has
read it, and other people on the same page. A free reader gets one honest review a week.

## Entities

### book
| field | question it answers |
|---|---|
| book_id | which book, joined everywhere |
| title, author | what to call it |
| edition (publisher, year, ISBN) | which page numbers the syllabus means |
| pages | how heavy is it |
| chapters[] (number, title, words, pages) | how to cut it into even weeks |
| difficulty_notes | why it counts as hard (prose, length, violence, allusion) |
| in_copyright | how much text we may quote |

### review (free tier)
| field | question it answers |
|---|---|
| review_id, book_id | which book this is about |
| rating (1–5) | how much he liked it |
| read_date | when he read it (and re-reads) |
| body_text | his words, verbatim, never rewritten |
| words | is there enough to post as-is, or does it need writing |
| source (goodreads, substack, notes) | where the text lives, so it can be checked |
| needs_writing | can this go out next week without new prose |
| scheduled_date, substack_url | when it ships and where it lives after |

### quote
| field | question it answers |
|---|---|
| quote_id, book_id | which book |
| text | the passage, verbatim |
| location (chapter, page) | which week of a cohort it belongs to |
| source (Kindle, Goodreads, manual) | provenance |
| used_in[] (note date, week, review) | has it already gone out |

### cohort (paid tier)
| field | question it answers |
|---|---|
| cohort_id, book_id | which book this quarter |
| start_date, end_date | when the 12 weeks run |
| price_monthly, price_annual, founding_price | what it costs and who got the early rate |
| enrolled_count | how many are reading along |
| in_person_partner | which bookstore, if any, hosts a session |

### week
| field | question it answers |
|---|---|
| cohort_id, week_number, date | when this reading is due |
| chapter_start, chapter_end | what to read |
| words, pages_approx | how heavy this week is |
| quote_ids[] | his saved passages from these chapters |
| chapter_notes | his notes (his prose, empty until he writes it) |
| discussion_prompts[] (text, status: draft/approved) | what the thread opens with |
| thread_url, comment_count | did anyone talk |

### subscriber_tier
| field | question it answers |
|---|---|
| tier (free, paid, founding) | what they get |
| price_monthly, price_annual | what they pay |
| includes[] | weekly review / cohort notes / thread / in-person |
| subscriber_count | how many are on it (from Substack's dashboard) |

### evergreen_guide
| field | question it answers |
|---|---|
| guide_id, book_id, cohort_id | which finished cohort it was built from |
| weeks[] (notes, quotes, prompts) | the full 12-week guide, reusable after the cohort ends |
| price or tier | is it sold standalone or kept for paid subscribers |
| published_url | where a late reader can pick it up |

## Joins
book 1—n review · book 1—n quote · book 1—n cohort · cohort 1—12 week ·
week n—n quote (by location) · cohort 1—1 evergreen_guide · subscriber_tier gates cohort and guide.

## Reality check (2026-10-11)

| field | fillable? | source |
|---|---|---|
| book.title/author/pages/rating/read_date | yes | `writing-topology/data/personal_corpus/goodreads_reads.json` (485 reads) |
| book.chapters[].words | yes for Blood Meridian | measured from a local copy (`scripts/split_chapters.py`); text never enters this repo |
| book.chapters[].pages | approximate | words scaled to 351 pp; no print page map on disk |
| review.body_text | yes, for books he reviewed | Goodreads reviews (87) + Substack posts, via `book_review_inventory.json` |
| quote.text | yes | `quotes.json` (284) |
| **quote.location** | **no** | quotes.json carries book, author, source only. Blood Meridian has 4 quotes and none has a chapter. Each is listed once in the syllabus with a note; he places them. |
| week.chapter_notes | not yet, by design | his prose; empty slots per week |
| discussion_prompts | drafted, marked DRAFT | he approves or rewrites |
| cohort enrolled / subscriber_count / thread comments | after launch | Substack dashboard; nothing exists before the publication does |
| evergreen_guide | after cohort 1 ends (2027-03-28) | assembled from the 12 weeks |

Nothing the model needs is unfillable in principle. One field (quote.location) is
unfilled today; it is a five-minute job for him with the book open, not a data gap.
