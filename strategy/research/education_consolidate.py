#!/usr/bin/env python3
"""Consolidate educational evidence into one review-ready dataset.
Merges live AU volume + SERP owner (education-evidence.json) with the best
competitor CONTENT-PAGE ranking URL (education-evidence-csv.json).
Educational only: product forms, conditions, symptoms, education.
"""
import json, re

live = {t["id"]: t for t in json.load(open("strategy/research/education-evidence.json"))["topics"]}
csv = {t["id"]: t for t in json.load(open("strategy/research/education-evidence-csv.json"))["topics"]}

# Map csv id -> live id for volume/owner (where a match exists)
LIVE_OF = {
    "cbd-oil": "cbd-oil", "what-is-cbd": "what-is-cbd", "what-is-thc": "what-is-thc",
    "cbd-vs-thc": "cbd-vs-thc", "indica-sativa": "indica-sativa", "cannabinoids": "cannabinoids",
    "cannabis-oil": "cannabis-oil", "flower": "flower", "gummies": "gummies", "vape": "vape",
    "endocannabinoid": "endocannabinoid", "what-is-mc": "what-is-mc", "how-works": "how-works",
    "driving": "driving", "sleep": "sleep", "nausea": "nausea", "muscle-pain": "muscle-pain",
    "inflammation": "inflammation", "anxiety": "anxiety-holistic", "menopause": "menopause",
}

DOMAIN = {"alternaleaf": "alternaleaf.com.au", "polln": "polln.com",
          "herbly": "herbly.com.au", "candor": "candormedical.com"}


def is_content(url):
    """A real content page, not just the homepage / domain root."""
    m = re.sub(r"^https?://", "", url).rstrip("/")
    path = m.split("/", 1)[1] if "/" in m else ""
    if not path:
        return False
    return bool(re.search(r"/(library|blog|blogs|hub|pages|learn|guide|resource|article)", url, re.I)) or len(path) > 3


def best_evidence(rows):
    """Pick the strongest single content-page URL per competitor."""
    by_comp = {}
    for r in rows:
        comp = r["comp"]
        content = is_content(r["url"])
        score = r["volume"] + (50000 if content else 0)
        if comp not in by_comp or score > by_comp[comp][0]:
            by_comp[comp] = (score, r, content)
    out = []
    for comp, (score, r, content) in by_comp.items():
        out.append({"comp": comp, "url": r["url"], "keyword": r["keyword"],
                    "position": r["position"], "volume": r["volume"], "content_page": content})
    out.sort(key=lambda e: (not e["content_page"], -e["volume"]))
    return out


# TGA flags per topic id (csv ids)
TGA = {
    "cbd-oil": "Care", "what-is-cbd": "Safe", "what-is-thc": "Safe", "cbd-vs-thc": "Safe",
    "indica-sativa": "Safe", "cannabinoids": "Safe", "terpenes": "Safe", "cannabis-oil": "Care",
    "flower": "Care", "gummies": "Care", "vape": "Care", "capsules": "Care", "topicals": "Care",
    "endocannabinoid": "Safe", "what-is-mc": "Care", "how-works": "Care", "driving": "Safe",
    "sleep": "Care", "nausea": "Care", "muscle-pain": "Care", "inflammation": "Care",
    "appetite": "Care", "anxiety": "Restricted", "menopause": "Care", "migraine": "Care",
    "arthritis": "Care", "endometriosis": "Care", "fibromyalgia": "Care", "epilepsy": "Restricted",
    "adhd": "Restricted",
}

ORDER = ["Product form", "Education", "Symptom", "Condition"]
final = []
for cid, t in csv.items():
    lid = LIVE_OF.get(cid)
    lv = live.get(lid, {}) if lid else {}
    owner = (lv.get("owner") or {}).get("domain") if lv.get("owner") else None
    ev = best_evidence(t["evidence"])
    final.append({
        "id": cid, "title": t["title"], "subtype": t["subtype"],
        "volume": lv.get("volume"), "serp_owner": owner,
        "tga": TGA.get(cid, "Care"),
        "evidence": ev,
        "has_content_evidence": any(e["content_page"] for e in ev),
    })

final.sort(key=lambda x: (ORDER.index(x["subtype"]), -(x["volume"] or 0)))
json.dump({"topics": final}, open("strategy/research/education-final.json", "w"), indent=2)

cur = None
for t in final:
    if t["subtype"] != cur:
        cur = t["subtype"]
        print(f"\n===== {cur.upper()} =====")
    star = "*" if t["has_content_evidence"] else " "
    print(f"{star} {t['title']:<34} vol={str(t['volume']):<6} tga={t['tga']:<10} owner={t['serp_owner'] or '-'}")
    for e in t["evidence"]:
        tag = "PAGE" if e["content_page"] else "home"
        print(f"      [{tag}] {e['comp']:<11} pos{e['position']:<4} {e['url']}")
print("\nSaved strategy/research/education-final.json")
