"""Live SERP + volume research for the 20 NEW educational topics (5 per group).

Finds the exact competitor-ranking URLs (AU + international) so each new topic
can carry 2-3 real, verified competitor links. Output: education-more.json
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

# (id, title, group, tga, seed_keyword)
TOPICS = [
    # --- PRODUCT FORMS ---
    ("gummies",    "Cannabis gummies and edibles",   "Product form", "Care", "cannabis gummies"),
    ("capsules",   "Medical cannabis capsules",      "Product form", "Care", "cbd capsules"),
    ("topicals",   "Cannabis topicals and creams",   "Product form", "Care", "cbd cream"),
    ("tinctures",  "Cannabis tinctures",             "Product form", "Care", "cbd tincture"),
    ("consumed",   "How medical cannabis is taken",  "Product form", "Care", "how to take medical cannabis"),
    # --- EDUCATION ---
    ("cbd-vs-thc", "CBD versus THC",                 "Education", "Safe", "cbd vs thc"),
    ("how-long",   "How long cannabis stays in you", "Education", "Safe", "how long does weed stay in your system"),
    ("full-spec",  "Full spectrum versus isolate",   "Education", "Safe", "full spectrum vs isolate"),
    ("entourage",  "The entourage effect",           "Education", "Safe", "entourage effect"),
    ("how-works",  "How medical cannabis works",     "Education", "Care", "how does medical cannabis work"),
    # --- SYMPTOMS ---
    ("stress",     "Stress",                         "Symptom", "Care", "natural stress relief"),
    ("chronic-pain","Chronic pain",                  "Symptom", "Care", "chronic pain management"),
    ("fatigue",    "Low energy and fatigue",         "Symptom", "Care", "how to boost energy naturally"),
    ("period",     "Period and menstrual pain",      "Symptom", "Care", "natural period pain relief"),
    ("nerve-pain", "Nerve and neuropathic pain",     "Symptom", "Care", "neuropathic pain relief"),
    # --- CONDITIONS ---
    ("depression", "Depression and low mood",        "Condition", "Restricted", "natural remedies for depression"),
    ("ptsd",       "PTSD",                           "Condition", "Restricted", "ptsd treatment"),
    ("ms",         "Multiple sclerosis",             "Condition", "Care", "multiple sclerosis treatment"),
    ("sciatica",   "Sciatica",                       "Condition", "Care", "sciatica treatment"),
    ("ibd",        "Ulcerative colitis and IBD",     "Condition", "Care", "natural treatment for ulcerative colitis"),
]

def volume(keywords):
    body = [{"keywords": keywords, "location_name": "Australia", "language_name": "English"}]
    d = call("https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live", body)
    res = (d.get("tasks") or [{}])[0].get("result") or []
    return {it.get("keyword"): it.get("search_volume") for it in res}, d.get("cost", 0) or 0

def serp(kw):
    body = [{"keyword": kw, "location_name": "Australia", "language_name": "English", "depth": 20}]
    cost = 0.0
    rows = []
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
    for tid, title, grp, tga, seed in TOPICS:
        rows, c = serp(seed)
        total += c
        comp_hits = [r for r in rows if any(c0 in (r["domain"] or "") for c0 in COMP)]
        results.append({
            "id": tid, "title": title, "group": grp, "tga": tga, "seed": seed,
            "volume": vols.get(seed), "competitors": comp_hits, "serp": rows[:20],
        })
        cn = ", ".join(f"{h['domain']}#{h['rank']}" for h in comp_hits) or "none"
        print(f"[{grp[:7]:7}] {seed:42} vol={vols.get(seed)} | comps: {cn}")
        time.sleep(0.25)
    json.dump({"topics": results, "total_cost": round(total, 4)},
              open("strategy/research/education-more.json", "w"), indent=2)
    print(f"\nSaved education-more.json | TOTAL cost ${round(total,4)}")

if __name__ == "__main__":
    main()
