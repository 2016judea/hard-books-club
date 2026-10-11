"""Find which chapter each saved Blood Meridian quote sits in, by matching its opening
words against a local copy of the text (never committed). quotes.json has no location.

usage: python3 scripts/locate_quotes.py <path-to-text>
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from split_chapters import ROMANS

def squash(s):
    return re.sub(r"[^a-z]", "", s.lower().replace("’", "'"))

lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
starts, want = [], 0
for i, l in enumerate(lines):
    if want < 23 and l.strip() == ROMANS[want] and (want == 0 or i > starts[-1] + 40):
        starts.append(i); want += 1
starts[0] = max(i for i in range(starts[1]) if lines[i].strip() == "I")
bounds = starts + [len(lines)]
chapters = [squash(" ".join(lines[bounds[k]+1:bounds[k+1]])) for k in range(23)]
quotes = json.load(open(os.path.expanduser(
    "~/Desktop/writing-topology/data/personal_corpus/quotes.json")))
for q in quotes:
    if q["book"] != "Blood Meridian":
        continue
    key = squash(q["quote"])[:60]
    hit = [k + 1 for k, c in enumerate(chapters) if key in c]
    print(json.dumps({"chapter": hit, "quote": q["quote"][:70]}))
