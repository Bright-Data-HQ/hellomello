#!/usr/bin/env python3
"""Build a per-topic list of ALL competitors and their real topic-specific link.
Merges:
  1. Content-page rankings from the 4 AU competitors' Positions CSVs.
  2. Competitor content pages that appeared in the live SERP top 20.
Only real content pages count as proof (homepage-only rankings are dropped).
"""
import json, re

csv = {t["id"]: t for t in json.load(open("strategy/research/education-evidence-csv.json"))["topics"]}
live = {t["id"]: t for t in json.load(open("strategy/research/education-evidence.json"))["topics"]}

# csv id -> live id
LIVE_OF = {
    "cbd-oil": "cbd-oil", "what-is-cbd": "what-is-cbd", "what-is-thc": "what-is-thc",
    "cbd-vs-thc": "cbd-vs-thc", "indica-sativa": "indica-sativa", "cannabinoids": "cannabinoids",
    "cannabis-oil": "cannabis-oil", "flower": "flower", "gummies": "gummies", "vape": "vape",
    "endocannabinoid": "endocannabinoid", "what-is-mc": "what-is-mc", "how-works": "how-works",
    "driving": "driving", "sleep": "sleep", "nausea": "nausea", "muscle-pain": "muscle-pain",
    "inflammation": "inflammation", "anxiety": "anxiety-holistic", "menopause": "menopause",
}

VOL = {tid: live.get(lid, {}).get("volume") for tid, lid in LIVE_OF.items()}

# Pretty competitor names by domain root
NAME = {
    "polln.com": "Polln", "alternaleaf.com.au": "Alternaleaf", "herbly.com.au": "Herbly",
    "candormedical.com": "Candor", "leafwell.com": "Leafwell", "releaf.co.uk": "Releaf",
    "alternaleaf.co.nz": "Alternaleaf NZ",
}
SLUGNAME = {"polln": "Polln", "alternaleaf": "Alternaleaf", "herbly": "Herbly", "candor": "Candor"}


def is_content(url):
    m = re.sub(r"^https?://", "", url).split("?")[0].rstrip("/")
    path = m.split("/", 1)[1] if "/" in m else ""
    if not path:
        return False
    return bool(re.search(r"/(library|blog|blogs|hub|pages|learn|guide|resource|article|post|education)", url, re.I))


def short(url):
    p = re.sub(r"^https?://", "", url).split("?")[0].rstrip("/")
    seg = p.rsplit("/", 1)[-1]
    return seg.replace("-", " ")


def domain_root(domain):
    return re.sub(r"^www\.", "", domain)


def main():
    out = []
    for cid, t in csv.items():
        comps = {}  # name -> {url, keyword/label}

        # 1. CSV content pages
        for e in t["evidence"]:
            if is_content(e["url"]):
                name = SLUGNAME.get(e["comp"], e["comp"])
                if name not in comps:
                    comps[name] = {"url": e["url"], "label": short(e["url"])}

        # 2. live SERP competitor content pages
        lid = LIVE_OF.get(cid)
        if lid:
            for c in (live.get(lid, {}).get("competitors") or []):
                url = c.get("url") or ""
                if not is_content(url):
                    continue
                root = domain_root(c["domain"])
                name = NAME.get(root, root)
                if name not in comps:
                    comps[name] = {"url": url, "label": short(url)}

        rows = [{"name": n, **v} for n, v in comps.items()]
        out.append({"id": cid, "title": t["title"], "subtype": t["subtype"],
                    "volume": VOL.get(cid), "competitors": rows})

    json.dump({"topics": out}, open("strategy/research/education-competitors.json", "w"), indent=2)

    ORDER = ["Product form", "Education", "Symptom", "Condition"]
    out.sort(key=lambda x: (ORDER.index(x["subtype"]), -(x["volume"] or 0)))
    cur = None
    urls = set()
    for t in out:
        if t["subtype"] != cur:
            cur = t["subtype"]
            print(f"\n===== {cur.upper()} =====")
        print(f"{t['title']:<34} vol={t['volume']}  ({len(t['competitors'])} competitors)")
        for c in t["competitors"]:
            print(f"      {c['name']:<14} {c['url']}")
            urls.add(c["url"])
    # dump unique urls for verification
    open("strategy/research/_urls.txt", "w").write("\n".join(sorted(urls)))
    print(f"\n{len(urls)} unique URLs -> strategy/research/_urls.txt")


if __name__ == "__main__":
    main()
