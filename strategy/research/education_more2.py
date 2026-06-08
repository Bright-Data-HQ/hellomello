"""Deep SERP (depth 50) for refined NEW-topic seeds, to surface competitor URLs
(AU + Leafwell/Releaf) that rank below position 20. Output: education-more2.json
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

SETS = ("polln", "herbly", "alternaleaf.com.au", "leafwell", "releaf", "candor", "montu", "honahlee", "astrid")

SEEDS = [
    # product forms
    ("gummies", "cannabis edibles"),
    ("gummies2", "thc gummies"),
    ("capsules", "cbd capsules"),
    ("topicals", "cbd cream"),
    ("topicals2", "cbd topical"),
    ("tinctures", "cbd tincture"),
    ("howtaken", "ways to take cbd"),
    # education
    ("cbdthc", "cbd vs thc"),
    ("howlong", "how long does weed stay in your system"),
    ("fullspec", "full spectrum vs isolate"),
    ("entourage", "entourage effect"),
    ("howworks", "how does cbd work"),
    # symptoms
    ("stress", "natural stress relief"),
    ("chronicpain", "natural pain relief"),
    ("energy", "how to boost energy naturally"),
    ("period", "period pain remedies"),
    ("nerve", "neuropathic pain"),
    # conditions
    ("depression", "natural remedies for depression"),
    ("ptsd", "ptsd treatment"),
    ("ms", "multiple sclerosis treatment"),
    ("sciatica", "sciatica treatment"),
    ("ibd", "natural remedies for ulcerative colitis"),
]

def serp(kw):
    body = [{"keyword": kw, "location_name": "Australia", "language_name": "English", "depth": 50}]
    cost = 0.0
    rows = []
    for attempt in range(3):
        d = call("https://api.dataforseo.com/v3/serp/google/organic/live/advanced", body)
        cost += d.get("cost", 0) or 0
        res = (d.get("tasks") or [{}])[0].get("result") or []
        items = (res[0].get("items") or []) if res else []
        rows = [{"rank": it.get("rank_group"), "domain": it.get("domain"), "url": it.get("url")}
                for it in items if it.get("type") == "organic"]
        if rows:
            return rows, cost
        time.sleep(1.0)
    return rows, cost

def main():
    total = 0.0
    out = {}
    for sid, kw in SEEDS:
        rows, c = serp(kw)
        total += c
        hits = [r for r in rows if any(s in (r["domain"] or "") for s in SETS) and "support." not in (r["domain"] or "")]
        out[sid] = {"seed": kw, "hits": hits}
        print(f"{sid:12} {kw:42}")
        for h in hits:
            print(f"    #{h['rank']:<2} {h['url']}")
        time.sleep(0.2)
    json.dump(out, open("strategy/research/education-more2.json", "w"), indent=2)
    print(f"\nTOTAL cost ${round(total,4)}")

if __name__ == "__main__":
    main()
