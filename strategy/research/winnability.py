"""Step 3: judge winnability. Pull live AU SERP top-5 for the corrected head terms
so we can see whether HM realistically competes (mid-tier AU sites) or faces
unbeatable government / global health giants. Also flags where HM already appears.
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

TERMS = {
    "telehealth-consult": "medical cannabis consultation",
    "access-pathways": "how to get medical marijuanas australia",
    "costs": "medical marijuanas cost",
    "practitioners": "medical cannabis prescriber",
    "clinic": "medicinal cannabis clinic australia",
    "what-is-mc": "what is medical cannabis",
    "endocannabinoid": "endocannabinoid system",
    "cbd-vs-thc": "what is cbd",
    "is-it-legal": "medical cannabis laws australia",
    "driving": "how long does thc stay in your system",
}

GOV = ("gov.au", "gov", "racgp", "tga", "healthdirect", "sahealth", "health.vic")
GLOBAL = ("webmd", "healthline", "mayoclinic", "clevelandclinic", "harvard", "wikipedia",
          "nhs.uk", "ncbi", "goodrx", "drugs.com")
KNOWN_COMP = ("alternaleaf", "polln", "herbly", "candor", "montu", "dispensed", "cannatrek",
              "medreleaf", "honahlee", "astrid", "releaf")

total = 0.0
out = {}
for tid, kw in TERMS.items():
    s = call("https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
             [{"keyword": kw, "location_name": "Australia", "language_name": "English", "depth": 10}])
    total += s.get("cost", 0) or 0
    res = (s.get("tasks") or [{}])[0].get("result") or []
    items = (res[0].get("items") or []) if res else []
    top = [(i.get("rank_group"), i.get("domain")) for i in items if i.get("type") == "organic"][:8]
    gov = sum(1 for _, d in top[:5] if d and any(g in d for g in GOV))
    glob = sum(1 for _, d in top[:5] if d and any(g in d for g in GLOBAL))
    comp = [(r, d) for r, d in top if d and any(c in d for c in KNOWN_COMP)]
    hm = [(r, d) for r, d in top if d and "mello" in d]
    # winnability heuristic
    hostile = gov + glob
    verdict = "HARD (gov/global lock-in)" if hostile >= 3 else ("MIXED" if hostile >= 1 else "WINNABLE (commercial SERP)")
    out[tid] = {"kw": kw, "top": top, "gov5": gov, "global5": glob, "competitors": comp, "hm": hm, "verdict": verdict}
    print(f"\n[{tid}] '{kw}'  -> {verdict}  (gov {gov}/5, global {glob}/5)")
    print("   top5:", [d for _, d in top[:5]])
    if comp: print("   known competitors:", comp)
    if hm:   print("   HM appears:", hm)
    time.sleep(0.3)

json.dump(out, open("strategy/research/winnability.json", "w"), indent=2)
print(f"\nTOTAL SERP cost: ${round(total,4)}")
