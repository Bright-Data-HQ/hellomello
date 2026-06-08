#!/usr/bin/env python3
"""
Topic coverage analysis for the Hellomello content-pillar sign-off.

For each proposed educational topic it answers two questions:
  1. Do our audited competitors already cover this topic, and who ranks best?
     (mined from the local Positions CSVs in competitors/<slug>/data/raw/)
  2. What does the live market look like right now?
     (validated via DataForSEO: search volume + the live SERP top results)

Output: strategy/research/topic-coverage.json  (consumed when writing the doc)

Run:
    set -a && source .env.vars && set +a
    python3 strategy/research/topic_coverage.py
"""
from __future__ import annotations
import os, re, csv, json, glob, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN = os.environ.get("dataforseo_api_basic_auth", "")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "topic-coverage.json")

COMPETITORS = {
    "alternaleaf": "alternaleaf.com.au",
    "polln": "polln.com",
    "herbly": "herbly.com.au",
    "candor": "candormedical.com",
}

# Topic = (id, title, pillar, tga_note, seed_keyword, match_regex)
# match_regex is used to find related keywords inside the competitor CSVs.
TOPICS = [
    ("how-it-works-consult", "What to expect from a telehealth consultation", "Education",
     "Safe", "telehealth consultation", r"(telehealth|online consult|consultation|appointment)"),
    ("endocannabinoid", "How the endocannabinoid system works", "Education",
     "Safe", "endocannabinoid system", r"(endocannabinoid|ecs|cannabinoid system)"),
    ("cbd-vs-thc", "CBD and THC: the difference explained", "Education",
     "Safe", "cbd vs thc", r"(cbd vs thc|thc vs cbd|difference between cbd|what is cbd|what is thc)"),
    ("driving-laws", "Medical cannabis and driving laws in Australia", "Education",
     "Safe", "cbd and driving australia", r"(driv|thc.*system|road|licence|license)"),
    ("access-pathways", "How patients access treatment in Australia (SAS, Authorised Prescriber)", "Education",
     "Needs care", "how to access medical cannabis australia", r"(how to get|how to access|sas|authorised prescriber|apply|eligib|qualify)"),
    ("is-it-legal", "Is medical cannabis legal in Australia", "Education",
     "Safe", "is medical cannabis legal in australia", r"(legal|legalis|is it legal|laws)"),
    ("costs-medicare", "What treatment costs and how Medicare fits in", "Education",
     "Safe", "medical cannabis cost australia", r"(cost|price|pricing|medicare|how much|cheap|bulk bill)"),
    ("practitioners", "Meet the practitioners: what a plant medicine doctor does", "Clinical expertise",
     "Safe", "plant medicine doctor", r"(doctor|gp|practitioner|prescriber|plant medicine|clinician|nurse)"),
    ("what-is-mc", "What is medical cannabis: a plain guide", "Education",
     "Needs care", "what is medical cannabis", r"(what is medical cannabis|what is medicinal|medicinal cannabis explained|guide)"),
    ("sleep-education", "Sleep quality: general education", "Condition (careful)",
     "Needs care", "how to sleep better", r"(sleep|insomnia|sleepless|rest)"),
    ("womens-health", "Women's health and natural therapies", "Condition (careful)",
     "Needs care", "natural therapies womens health", r"(women|menopause|period|endometri|pms|hormone)"),
    ("nausea", "Nausea: causes and relief options", "Condition (careful)",
     "Needs care", "nausea relief", r"(nausea|vomit|sickness)"),
    ("delivery", "How medication delivery works", "Location / service",
     "Safe", "medication delivery australia", r"(deliver|shipping|post|mail|pickup|pick up|dispensary)"),
    ("near-me", "Finding a clinic near you", "Location / service",
     "Safe", "medical cannabis clinic near me", r"(near me|clinic|dispensary|local|in my area)"),
    ("eligibility", "Am I eligible: who can be treated", "Education",
     "Needs care", "medical cannabis eligibility australia", r"(eligib|qualify|am i eligible|who can|criteria)"),
]


def call(url: str, body: list) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Basic {TOKEN}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {"err": e.read()[:300].decode("utf-8", "replace")}


def load_competitor_rows() -> dict:
    data = {}
    for slug in COMPETITORS:
        files = sorted(glob.glob(os.path.join(ROOT, f"competitors/{slug}/data/raw/*organic.Positions*.csv")))
        if not files:
            data[slug] = []
            continue
        with open(files[-1], encoding="utf-8") as f:
            data[slug] = list(csv.DictReader(f))
    return data


def local_coverage(rows_by_comp: dict, pattern: str) -> dict:
    rx = re.compile(pattern, re.I)
    out = {}
    for slug, rows in rows_by_comp.items():
        hits = []
        for r in rows:
            kw = r.get("Keyword", "")
            if rx.search(kw):
                try:
                    pos = int(r.get("Position") or 0)
                    tr = float(r.get("Traffic") or 0)
                    vol = int(r.get("Search Volume") or 0)
                except ValueError:
                    continue
                hits.append({"kw": kw, "pos": pos, "vol": vol, "traffic": tr,
                             "url": r.get("URL", "")})
        hits.sort(key=lambda x: (x["pos"], -x["traffic"]))
        out[slug] = {
            "kw_count": len(hits),
            "traffic": round(sum(h["traffic"] for h in hits)),
            "best": hits[0] if hits else None,
        }
    return out


def live_volume(keyword: str) -> dict:
    body = [{"keywords": [keyword], "location_name": "Australia", "language_name": "English"}]
    d = call("https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live", body)
    cost = d.get("cost", 0) or 0
    res = (d.get("tasks") or [{}])[0].get("result") or []
    item = (res[0].get("items") or [{}])[0] if res else {}
    ki = item.get("keyword_info", {}) if item else {}
    return {"volume": ki.get("search_volume"), "cpc": ki.get("cpc"),
            "competition": ki.get("competition"), "cost": cost}


def live_serp(keyword: str) -> dict:
    body = [{"keyword": keyword, "location_name": "Australia", "language_name": "English",
             "depth": 10}]
    d = call("https://api.dataforseo.com/v3/serp/google/organic/live/advanced", body)
    cost = d.get("cost", 0) or 0
    res = (d.get("tasks") or [{}])[0].get("result") or []
    items = (res[0].get("items") or []) if res else []
    top = []
    for it in items:
        if it.get("type") != "organic":
            continue
        top.append({"rank": it.get("rank_group"), "domain": it.get("domain"),
                    "url": it.get("url")})
        if len(top) >= 10:
            break
    return {"top": top, "cost": cost}


def main():
    if not TOKEN:
        raise SystemExit("Missing dataforseo_api_basic_auth. Run: set -a && source .env.vars && set +a")
    rows_by_comp = load_competitor_rows()
    known_domains = set(COMPETITORS.values())
    total_cost = 0.0
    results = []
    for tid, title, pillar, tga, seed, pat in TOPICS:
        cov = local_coverage(rows_by_comp, pat)
        vol = live_volume(seed)
        total_cost += vol["cost"]
        serp = live_serp(seed)
        total_cost += serp["cost"]
        # which known competitors appear live in the SERP top 10
        live_known = [t for t in serp["top"] if any(kd in (t["domain"] or "") for kd in known_domains)]
        results.append({
            "id": tid, "title": title, "pillar": pillar, "tga": tga,
            "seed": seed, "volume": vol["volume"], "cpc": vol["cpc"],
            "local_coverage": cov,
            "live_serp_top": serp["top"],
            "live_known_competitors": live_known,
        })
        print(f"[{tid:20}] vol={vol['volume']} | "
              f"local: " + ", ".join(f"{s}:{cov[s]['kw_count']}" for s in COMPETITORS) +
              f" | live_known={len(live_known)} | cost so far ${round(total_cost,4)}")
        time.sleep(0.3)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"topics": results, "total_cost": round(total_cost, 4)}, f, indent=2)
    print(f"\nSaved {OUT}")
    print(f"TOTAL DataForSEO cost: ${round(total_cost,4)}")


if __name__ == "__main__":
    main()
