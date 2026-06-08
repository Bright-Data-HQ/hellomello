"""Step 2: verify accurate AU search volumes for candidate head terms per topic.
Uses Google Ads search volume (exact, reliable) in one bulk call.
"""
import os, json, urllib.request, urllib.error
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

# topic_id -> candidate head terms (we take the max-volume relevant one)
CANDIDATES = {
    "telehealth-consult": ["medical cannabis telehealth", "telehealth cannabis", "online cannabis consultation", "medical cannabis consultation", "cannabis telehealth australia"],
    "endocannabinoid": ["endocannabinoid system", "what is the endocannabinoid system", "endocannabinoid"],
    "cbd-vs-thc": ["cbd vs thc", "difference between cbd and thc", "what is cbd", "what is thc"],
    "driving-laws": ["medical cannabis and driving", "driving on medical cannabis", "can you drive on medical cannabis", "how long does thc stay in your system"],
    "access-pathways": ["how to get medical cannabis", "how to get a medical cannabis prescription", "how to get medical marijuanas australia", "medical cannabis prescription online", "online cannabis prescription"],
    "is-it-legal": ["is medical cannabis legal in australia", "is weed legal in australia", "medical cannabis laws australia"],
    "costs-medicare": ["medical cannabis cost australia", "how much is medical cannabis", "medical marijuanas cost", "is medical cannabis covered by medicare"],
    "practitioners": ["medical cannabis doctor", "cannabis doctor", "medical cannabis prescriber", "plant medicine doctor", "cannabis clinic australia"],
    "what-is-mc": ["what is medical cannabis", "what is medicinal cannabis", "medicinal cannabis australia"],
    "sleep": ["medical cannabis for sleep", "cannabis for insomnia", "how to sleep better", "natural sleep remedies"],
    "womens-health": ["medical cannabis for menopause", "cannabis for periods", "natural therapies womens health"],
    "nausea": ["medical cannabis for nausea", "how to stop nausea", "nausea relief"],
    "delivery": ["medical cannabis delivery australia", "online dispensary australia", "cannabis delivery australia"],
    "clinic-near-me": ["medical cannabis clinic near me", "cannabis clinic", "medicinal cannabis clinic australia"],
    "eligibility": ["am i eligible for medical cannabis", "medical cannabis eligibility australia", "who can prescribe medical cannabis"],
    # extra: HM's existing big footholds (to size the optimise-what-we-have option)
    "_hm-head-terms": ["medical marijuanas australia", "medical cannabis australia online", "cannabidiol oil australia", "medicinal marijuanas online", "medical marijuanas nsw", "thc oil australia"],
}

allkw = sorted({k for v in CANDIDATES.values() for k in v})
body = [{"keywords": allkw, "location_name": "Australia", "language_name": "English"}]
d = call("https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live", body)
print("google_ads volume cost:", d.get("cost"))
res = (d.get("tasks") or [{}])[0].get("result") or []
vol = {}
for it in res:
    vol[it.get("keyword")] = it.get("search_volume")

out = {}
print("\n=== Topic head-term volumes (AU, Google Ads exact) ===")
for tid, cands in CANDIDATES.items():
    pairs = [(k, vol.get(k)) for k in cands]
    best = max(pairs, key=lambda p: (p[1] or 0))
    out[tid] = {"best_term": best[0], "best_vol": best[1], "all": pairs}
    print(f"\n[{tid}] head ~ {best[1]} ('{best[0]}')")
    for k, v in pairs:
        print(f"     {str(v):>6}  {k}")

json.dump(out, open("strategy/research/topic-volumes.json", "w"), indent=2)
print("\nSaved strategy/research/topic-volumes.json")
