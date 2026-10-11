"""Split Blood Meridian's 23 chapters into 12 contiguous weeks, balanced by length.

Length is measured as words per chapter from a local copy of the text (not in this
repo; the text is in copyright). Words are converted to pages at the book's own
ratio: total words / 351 pages (Vintage International, the edition on his Goodreads).
The output is chapter numbers and counts only; no text leaves this script.

usage: python3 scripts/split_chapters.py <path-to-text> > cohorts/blood-meridian/split.json
"""
import json
import sys

ROMANS = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII".split()
PAGES = 351
WEEKS = 12


def chapter_words(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    # skip the contents block (headings listed with no body), find the 23 heading lines in order
    starts, want = [], 0
    for i, line in enumerate(lines):
        if want < 23 and line.strip() == ROMANS[want] and (want == 0 or i > starts[-1] + 40):
            starts.append(i)
            want += 1
    assert len(starts) == 23, len(starts)
    # the contents block also lists "I"; chapter I is the LAST bare "I" before chapter II
    starts[0] = max(i for i in range(starts[1]) if lines[i].strip() == "I")
    bounds = starts + [len(lines)]
    return [len(" ".join(lines[bounds[k] + 1:bounds[k + 1]]).split()) for k in range(23)]


def partition(words, k):
    """Contiguous split into k groups minimising the sum of squared group sizes,
    i.e. the most even weekly load (min-max alone left 19- and 39-page weeks)."""
    n = len(words)
    pre = [0]
    for w in words:
        pre.append(pre[-1] + w)
    INF = float("inf")
    best = [[INF] * (n + 1) for _ in range(k + 1)]
    cut = [[0] * (n + 1) for _ in range(k + 1)]
    best[0][0] = 0
    for g in range(1, k + 1):
        for j in range(g, n + 1):
            for i in range(g - 1, j):
                cost = best[g - 1][i] + (pre[j] - pre[i]) ** 2
                if cost < best[g][j]:
                    best[g][j], cut[g][j] = cost, i
    groups, j = [], n
    for g in range(k, 0, -1):
        i = cut[g][j]
        groups.append((i, j))
        j = i
    return groups[::-1]


if __name__ == "__main__":
    words = chapter_words(sys.argv[1])
    total = sum(words)
    per_page = total / PAGES
    out = []
    for wk, (i, j) in enumerate(partition(words, WEEKS), 1):
        w = sum(words[i:j])
        out.append({
            "week": wk,
            "chapters": [i + 1, j],
            "words": w,
            "pages_approx": round(w / per_page),
        })
    json.dump({"chapter_words": words, "total_words": total, "pages": PAGES,
               "weeks": out}, sys.stdout, indent=1)
