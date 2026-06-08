"""Educational content research for the Hellomello sign-off.

Scope is EDUCATIONAL ONLY, across four sub-types:
  - product forms (oil, cbd, thc, indica/sativa, flower, gummies, vape, cannabinoids)
  - conditions (handled with TGA care)
  - symptoms
  - general education (how it works, the plant science, driving)

For every topic it captures EVIDENCE:
  - real AU search volume (Google Ads)
  - the live SERP top 10 with EXACT URLs
  - which competitors rank and the EXACT URL they rank with
  - the best non-competitor result (who currently owns the topic)

Output: strategy/research/education-evidence.json
"""
import os, json, time, urllib.request, urllib.error
TOKEN = os.environ["dataforseo_api_basic_auth"]

def call(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Basic {TOKEN}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {"err": e.read()[:400].decode("utf-8", "replace")}

COMP = ("alternaleaf", "polln", "herbly", "candor", "montu", "cannatrek",
        "honahlee", "astrid", "releaf", "dispensed", "umeds", "medreleaf",
        "cannadoc", "grovehealth", "ivymed", "cdaclinic", "heyabby", "leafwell")

# (id, title, subtype, tga, seed_keyword)
TOPICS = [
    # --- PRODUCT FORMS ---
    ("cbd-oil",        "What is CBD oil",                         "Product form", "Needs care", "cbd oil"),
    ("what-is-cbd",    "What is CBD",                             "Product form", "Safe",       "what is cbd"),
    ("what-is-thc",    "What is THC",                             "Product form", "Safe",       "what is thc"),
    ("cbd-vs-thc",     "CBD and THC: the difference",            "Product form", "Safe",       "cbd vs thc"),
    ("indica-sativa",  "Indica and Sativa explained",            "Product form", "Needs care", "indica vs sativa"),
    ("cannabinoids",   "What are cannabinoids",                  "Product form", "Safe",       "medicinal cannabinoids"),
    ("cannabis-oil",   "Medical cannabis oil explained",         "Product form", "Needs care", "medical cannabis oil"),
    ("flower",         "Medical cannabis flower explained",      "Product form", "Needs care", "medical cannabis flower"),
    ("gummies",        "Medical cannabis gummies and edibles",   "Product form", "Needs care", "thc gummies australia"),
    ("vape",           "Medical cannabis vapes explained",       "Product form", "Needs care", "medical cannabis vape"),
    # --- GENERAL EDUCATION ---
    ("endocannabinoid","How the endocannabinoid system works",   "Education",    "Safe",       "endocannabinoid system"),
    ("what-is-mc",     "What is medical cannabis",               "Education",    "Needs care", "what is medical cannabis"),
    ("how-works",      "How medical cannabis works",             "Education",    "Needs care", "how does medical cannabis work"),
    ("driving",        "Medical cannabis and driving",           "Education",    "Safe",       "how long does thc stay in your system"),
    # --- SYMPTOMS ---
    ("muscle-pain",    "Easing muscle pain: general guide",      "Symptom",      "Needs care", "how to relieve muscle pain"),
    ("sleep",          "Sleep quality: general guide",           "Symptom",      "Needs care", "how to sleep better"),
    ("nausea",         "Nausea: causes and relief",              "Symptom",      "Needs care", "how to stop nausea"),
    # --- CONDITIONS (TGA care) ---
    ("anxiety-holistic","Holistic approaches to anxiety",        "Condition",    "Needs care", "holistic medicine for anxiety"),
    ("menopause",      "Women's health: menopause",              "Condition",    "Needs care", "natural remedies for menopause"),
    ("inflammation",   "Inflammation: general guide",            "Condition",    "Needs care", "how to reduce inflammation"),
]

def volume(keywords):
    body = [{"keywords": keywords, "location_name": "Australia", "language_name": "English"}]
    d = call("https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live", body)
    res = (d.get("tasks") or [{}])[0].get("result") or []
    return {it.get("keyword"): it.get("search_volume") for it in res}, d.get("cost", 0) or 0

def serp(kw):
    body = [{"keyword": kw, "location_name": "Australia", "language_name": "English", "depth": 20}]
    cost = 0.0
    for attempt in range(3):
        d = call("https://api.dataforseo.com/v3/serp/google/organic/live/advanced", body)
        cost += d.get("cost", 0) or 0
        res = (d.get("tasks") or [{}])[0].get("result") or []
        items = (res[0].get("items") or []) if res else []
        rows = []
        for it in items:
            if it.get("type") != "organic":
                continue
            rows.append({"rank": it.get("rank_group"), "domain": it.get("domain"),
                         "url": it.get("url"), "title": it.get("title")})
        if rows:
            return rows, cost
        time.sleep(1.0)
    return rows, cost

def main():
    total = 0.0
    vols, c = volume([t[4] for t in TOPICS])
    total += c
    results = []
    for tid, title, sub, tga, seed in TOPICS:
        rows, c = serp(seed)
        total += c
        comp_hits = []
        for r in rows:
            dom = r["domain"] or ""
            if any(c0 in dom for c0 in COMP):
                comp_hits.append(r)
        owner = rows[0] if rows else None
        results.append({
            "id": tid, "title": title, "subtype": sub, "tga": tga, "seed": seed,
            "volume": vols.get(seed),
            "owner": owner,
            "competitors": comp_hits,
            "serp": rows[:20],
        })
        cn = ", ".join(f"{h['domain']}#{h['rank']}" for h in comp_hits) or "none in top 10"
        print(f"[{sub[:7]:7}] {seed:38} vol={vols.get(seed)} | owner={owner['domain'] if owner else '-'} | comps: {cn}")
        time.sleep(0.25)
    json.dump({"topics": results, "total_cost": round(total, 4)},
              open("strategy/research/education-evidence.json", "w"), indent=2)
    print(f"\nSaved strategy/research/education-evidence.json | TOTAL cost ${round(total,4)}")

if __name__ == "__main__":
    main()
