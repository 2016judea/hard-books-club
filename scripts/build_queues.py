"""Build archive/queue.csv (52 weekly free-tier reviews) and notes/queue.csv (90 daily
Substack Notes) from Aidan's reading corpus. Re-run after the corpus changes.

Sources (writing-topology/data/personal_corpus/):
  book_review_inventory.json  every place he has written about a book (preferred)
  goodreads_reads.json        ratings and read dates (fallback for rating)
  quotes.json                 his 284 saved passages, the single master

Rules, and why:
- existing_words counts HIS words only: the longer of his Goodreads review and his
  Substack passage on the book. Apple Notes and Dropbox entries are excluded because
  on inspection they are mostly copied book text or journal pages, not reviews.
  The two counted sources often hold the SAME text, so it is max, never sum.
- A row needs no new writing when existing_words >= 100 (a short Note-length post;
  his 2026 median Substack post is 236 words). Under 100 it is flagged Y.
- Rows with text come first, ranked by existing_words x rating, then rated books with
  no text (5 stars first, most recent read first). Same author never within 3 weeks.
- Blood Meridian is pinned to the week of 2026-11-30, the week the cohort is announced
  (12/01), so the free review is the door to the paid read.
- Notes: quotes of 500 chars or fewer (fits a phone screen), verbatim, no caption.
  Same author never within 4 days.
"""
import csv
import datetime as dt
import json
import os
import re

CORPUS = os.path.expanduser("~/Desktop/writing-topology/data/personal_corpus")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_START = dt.date(2026, 11, 16)
NOTES_START = dt.date(2026, 10, 12)  # bfe2dd8 moved the committed queue to 10/12 by hand; the generator must agree or a re-run silently pushes every Note back five weeks
NEEDS_WRITING_UNDER = 100
PIN = {"Blood Meridian": dt.date(2026, 11, 30)}


def load(name):
    return json.load(open(os.path.join(CORPUS, name), encoding="utf-8"))


def norm(title):
    return re.split(r"[:(,]", title)[0].strip().lower()


def short_title(title):
    return re.split(r"[:(]|, or,", title)[0].strip()


def spaced(rows, gap, key):
    """Greedy: take rows in rank order, skipping any whose key appeared in the last `gap`."""
    out, pool = [], list(rows)
    while pool:
        recent = {key(r) for r in out[-gap:]}
        pick = next((r for r in pool if key(r) not in recent), pool[0])
        pool.remove(pick)
        out.append(pick)
    return out


def archive():
    reads = load("goodreads_reads.json")
    gr = {norm(b["title"]): b for b in reads}
    inv_path = os.path.join(CORPUS, "book_review_inventory.json")
    inv = json.load(open(inv_path)) if os.path.exists(inv_path) else []

    rows, seen = [], set()
    for b in inv:
        if b["title"].startswith("["):  # "[Author — book unspecified]"
            continue
        g = gr.get(norm(b["title"]), {})
        rating = b.get("rating") or g.get("rating") or 0
        best, src = 0, ""
        for s in b["sources"]:
            if s["source"] in ("goodreads_review", "substack") and s["words"] > best:
                best, src = s["words"], s["source"] + (f": {s['ref']}" if s.get("ref") else "")
        if not rating and not best:
            continue
        rows.append(dict(title=short_title(b["title"]), author=b["author"], rating=rating,
                         existing_words=best, source=src or "goodreads_rating",
                         read=g.get("read_year") or b.get("read_year") or 0))
        seen.add(norm(b["title"]))
    for b in reads:  # rated books the inventory does not list
        if norm(b["title"]) not in seen and b["rating"]:
            rows.append(dict(title=short_title(b["title"]), author=b["author"], rating=b["rating"],
                             existing_words=0, source="goodreads_rating", read=b["read_year"] or 0))

    pinned = {r["title"]: r for r in rows if r["title"] in PIN}
    rows = [r for r in rows if r["title"] not in PIN]
    with_text = sorted((r for r in rows if r["existing_words"] >= NEEDS_WRITING_UNDER),
                       key=lambda r: -r["existing_words"] * r["rating"])
    short = sorted((r for r in rows if 0 < r["existing_words"] < NEEDS_WRITING_UNDER and r["rating"] >= 4),
                   key=lambda r: -r["existing_words"] * r["rating"])
    blank = sorted((r for r in rows if r["existing_words"] == 0 and r["rating"] >= 4),
                   key=lambda r: (-r["rating"], -r["read"]))
    order = spaced(with_text, 3, lambda r: r["author"])
    order += [r for r in spaced(short + blank, 3, lambda r: r["author"])]

    weeks = []
    for i in range(52):
        date = ARCHIVE_START + dt.timedelta(weeks=i)
        pin = next((pinned[t] for t, d in PIN.items() if d == date and t in pinned), None)
        weeks.append(pin)
    # fill around the pins, keeping the 3-week author gap across them too
    for i in range(52):
        if weeks[i] is None:
            near = {w["author"] for w in weeks[max(0, i - 3):i + 4] if w}
            pick = next((r for r in order if r["author"] not in near), order[0])
            order.remove(pick)
            weeks[i] = pick
    with open(os.path.join(ROOT, "archive", "queue.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["week", "date", "title", "author", "rating", "existing_words", "needs_writing", "source"])
        for i, r in enumerate(weeks):
            w.writerow([i + 1, (ARCHIVE_START + dt.timedelta(weeks=i)).isoformat(), r["title"], r["author"],
                        r["rating"], r["existing_words"],
                        "N" if r["existing_words"] >= NEEDS_WRITING_UNDER else "Y", r["source"]])
    return weeks


def notes():
    q = [x for x in load("quotes.json") if len(x["quote"].strip()) <= 500]
    by_author = {}
    for x in q:
        by_author.setdefault(x["author"], []).append(x)
    for v in by_author.values():
        v.sort(key=lambda x: len(x["quote"]))
    picked, recent = [], []
    while len(picked) < 90:
        choices = [a for a in by_author if by_author[a] and a not in recent[-4:]]
        if not choices:
            choices = [a for a in by_author if by_author[a]]
        # the author with the most passages left goes next, so the lane (McCarthy,
        # Chandler, Fitzgerald) recurs and the one-offs still appear
        a = max(choices, key=lambda a: (len(by_author[a]), a))
        picked.append(by_author[a].pop(0))
        recent.append(a)
    with open(os.path.join(ROOT, "notes", "queue.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day", "date", "book", "author", "quote", "source"])
        for i, x in enumerate(picked):
            w.writerow([i + 1, (NOTES_START + dt.timedelta(days=i)).isoformat(), x["book"], x["author"],
                        x["quote"].strip(), x["source"]])
    return picked


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "archive"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "notes"), exist_ok=True)
    weeks = archive()
    n = notes()
    print(f"archive: 52 weeks, {sum(r['existing_words'] >= NEEDS_WRITING_UNDER for r in weeks)} need no writing, "
          f"{sum(r['existing_words'] > 0 for r in weeks)} have some text")
    print(f"notes: {len(n)} days, {len({x['author'] for x in n})} authors")
