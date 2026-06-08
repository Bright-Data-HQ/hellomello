#!/usr/bin/env python3
"""List every content-page URL each competitor ranks with, plus its best
(highest-volume) keyword. Used to curate topic -> competitor link mapping by hand.
"""
import csv, glob, re, collections

COMPS = {
    "Alternaleaf": "competitors/alternaleaf/data/raw/alternaleaf.com.au-organic.Positions-au-*.csv",
    "Polln":       "competitors/polln/data/raw/polln.com-organic.Positions-au-*.csv",
    "Herbly":      "competitors/herbly/data/raw/herbly.com.au-organic.Positions-au-*.csv",
    "Candor":      "competitors/candor/data/raw/candormedical.com-organic.Positions-au-*.csv",
}
CONTENT = re.compile(r"/(library|blog|blogs|hub|pages|learn|guide|resource|article|post|education)", re.I)


def num(x):
    try:
        return int(float(x))
    except Exception:
        return 0


for name, pat in COMPS.items():
    files = sorted(glob.glob(pat))
    if not files:
        continue
    best = {}  # url -> (vol, keyword)
    with open(files[-1], newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            url = (r.get("URL") or "").split("?")[0].strip()
            if not CONTENT.search(url):
                continue
            kw = (r.get("Keyword") or "").strip()
            vol = num(r.get("Search Volume"))
            if url not in best or vol > best[url][0]:
                best[url] = (vol, kw)
    print(f"\n===== {name}: {len(best)} content pages =====")
    for url, (vol, kw) in sorted(best.items(), key=lambda x: -x[1][0]):
        print(f"  vol{vol:<6} {url}   <= '{kw}'")
