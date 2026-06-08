#!/usr/bin/env python3
"""Mine the four main competitors' SEMrush Positions CSVs for EDUCATIONAL
keywords and pull the exact ranking URL as evidence. Educational only:
product forms, conditions, symptoms, general "what is / how" education.
No location, no prescription/access, no cost terms.
"""
import csv, glob, json, re, os

COMPS = {
    "alternaleaf": "competitors/alternaleaf/data/raw/alternaleaf.com.au-organic.Positions-au-*.csv",
    "polln":       "competitors/polln/data/raw/polln.com-organic.Positions-au-*.csv",
    "herbly":      "competitors/herbly/data/raw/herbly.com.au-organic.Positions-au-*.csv",
    "candor":      "competitors/candor/data/raw/candormedical.com-organic.Positions-au-*.csv",
}

# Topic buckets. Each: id -> (title, subtype, regex of educational intent terms)
TOPICS = [
    ("cbd-oil",       "What is CBD oil",                 "Product form", r"\bcbd oil\b|\bcbd\b.*oil"),
    ("what-is-cbd",   "What is CBD",                     "Education",     r"what is cbd|\bcbd\b(?!.*oil)"),
    ("what-is-thc",   "What is THC",                     "Education",     r"what is thc|\bthc\b"),
    ("cbd-vs-thc",    "CBD vs THC",                      "Education",     r"cbd vs thc|cbd and thc|difference.*cbd.*thc|thc vs cbd"),
    ("indica-sativa", "Indica vs sativa",                "Education",     r"indica|sativa"),
    ("cannabinoids",  "Cannabinoids explained",          "Education",     r"cannabinoid"),
    ("terpenes",      "Terpenes explained",              "Education",     r"terpene"),
    ("cannabis-oil",  "Medical cannabis oil",            "Product form",  r"cannabis oil|marijuana oil"),
    ("flower",        "Medical cannabis flower",         "Product form",  r"\bflower\b|dried cannabis|\bbud\b"),
    ("gummies",       "THC / CBD gummies",               "Product form",  r"gumm|edible"),
    ("vape",          "Medical cannabis vaporiser",      "Product form",  r"\bvape\b|vaporis|vaporiz"),
    ("capsules",      "Cannabis capsules",               "Product form",  r"capsule|tablet"),
    ("topicals",      "Cannabis topicals",               "Product form",  r"topical|\bcream\b|balm|lotion"),
    ("endocannabinoid","Endocannabinoid system",         "Education",     r"endocannabinoid|\becs\b"),
    ("what-is-mc",    "What is medical cannabis",        "Education",     r"what is medical (cannabis|marijuana)|medical cannabis(?!.*for )"),
    ("how-works",     "How medical cannabis works",      "Education",     r"how (does|do).*(cannabis|cbd|thc|marijuana).*(work|help)"),
    ("driving",       "Cannabis and driving / how long THC stays", "Education", r"driv|how long.*(thc|weed|cannabis|system)|stay in (your )?system"),
    ("sleep",         "Cannabis and sleep",              "Symptom",       r"sleep|insomnia"),
    ("nausea",        "Cannabis and nausea",             "Symptom",       r"nausea|vomit"),
    ("muscle-pain",   "Muscle and body pain relief",     "Symptom",       r"muscle (pain|ache)|body pain|relieve.*pain"),
    ("inflammation",  "Inflammation",                    "Symptom",       r"inflammat"),
    ("appetite",      "Appetite",                        "Symptom",       r"appetite"),
    ("anxiety",       "Anxiety (general/holistic)",      "Condition",     r"anxiet"),
    ("menopause",     "Menopause / women's health",      "Condition",     r"menopause|perimenopause"),
    ("migraine",      "Migraine / headache",             "Condition",     r"migraine|headache"),
    ("arthritis",     "Arthritis / joint",               "Condition",     r"arthritis|joint pain"),
    ("endometriosis", "Endometriosis",                   "Condition",     r"endometrios"),
    ("fibromyalgia",  "Fibromyalgia",                    "Condition",     r"fibromyalg"),
    ("epilepsy",      "Epilepsy / seizures",             "Condition",     r"epilep|seizure"),
    ("adhd",          "ADHD",                            "Condition",     r"\badhd\b"),
]

# Exclude obviously transactional / brand / location / cost / access keywords so
# we keep evidence EDUCATIONAL only.
EXCLUDE = re.compile(
    r"login|sign in|near me|clinic|appointment|book|price|cost|cheap|prescription|"
    r"prescri|script|doctor|gp |chemist|pharmacy|dispensary|buy |order |online|"
    r"alternaleaf|polln|herbly|candor|montu|review|coupon|promo|discount|\.com|telehealth|"
    r"how to get|where to|access|eligib|legal|au |aus |australia card", re.I)


def load(slug, pattern):
    files = sorted(glob.glob(pattern))
    if not files:
        return []
    rows = []
    with open(files[-1], newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def num(x):
    try:
        return int(float(x))
    except Exception:
        return 0


def main():
    data = {slug: load(slug, pat) for slug, pat in COMPS.items()}
    out = []
    for tid, title, sub, pat in TOPICS:
        rx = re.compile(pat, re.I)
        evidence = []  # one best row per competitor
        for slug, rows in data.items():
            best = None
            for r in rows:
                kw = (r.get("Keyword") or "").strip()
                if not kw or not rx.search(kw):
                    continue
                if EXCLUDE.search(kw):
                    continue
                url = (r.get("URL") or "").strip()
                # skip the bare homepage / non-content URLs for education proof
                pos = num(r.get("Position"))
                vol = num(r.get("Search Volume"))
                intents = (r.get("Keyword Intents") or "").strip()
                cand = {"comp": slug, "keyword": kw, "position": pos,
                        "volume": vol, "url": url, "intents": intents}
                # prefer the row with the highest volume that has a real content URL
                score = vol + (10000 if "/blog" in url or "/learn" in url or "/guide" in url
                               or "/resource" in url or "/education" in url else 0)
                if best is None or score > best["_score"]:
                    cand["_score"] = score
                    best = cand
            if best:
                best.pop("_score", None)
                evidence.append(best)
        evidence.sort(key=lambda e: -e["volume"])
        out.append({"id": tid, "title": title, "subtype": sub,
                    "covered_by": [e["comp"] for e in evidence],
                    "evidence": evidence})

    json.dump({"topics": out}, open("strategy/research/education-evidence-csv.json", "w"), indent=2)

    # report
    for t in out:
        cb = ", ".join(t["covered_by"]) if t["covered_by"] else "NONE"
        print(f"[{t['subtype'][:7]:<7}] {t['title']:<38} covered: {cb}")
        for e in t["evidence"]:
            print(f"        {e['comp']:<11} pos{e['position']:<3} vol{e['volume']:<6} {e['keyword'][:40]:<40} {e['url']}")
    print("\nSaved strategy/research/education-evidence-csv.json")


if __name__ == "__main__":
    main()
