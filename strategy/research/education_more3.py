"""Gap-fill deep SERP (depth 60) for NEW topics needing more competitor links.
Output: education-more3.json
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
    ("edibles", "cannabis edibles"),
    ("gummies", "cbd gummies"),
    ("capsules", "cannabis capsules"),
    ("tinctures", "what is a tincture"),
    ("cbdthc", "difference between cbd and thc"),
    ("entourage", "what is the entourage effect"),
    ("howworks", "how does medical cannabis work in the body"),
    ("depression", "cannabis for depression"),
    ("ptsd", "cannabis for ptsd"),
    ("ms", "cannabis for multiple sclerosis"),
    ("ibd", "cannabis for crohn's disease"),
    ("fullspec3", "full spectrum cbd benefits"),
]

def serp(kw):
    body = [{"keyword": kw, "location_name": "Australia", "language_name": "English", "depth": 60}]
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
        print(f"{sid:12} {kw}")
        for h in hits:
            print(f"    #{h['rank']:<2} {h['url']}")
        time.sleep(0.2)
    json.dump(out, open("strategy/research/education-more3.json", "w"), indent=2)
    print(f"\nTOTAL cost ${round(total,4)}")

if __name__ == "__main__":
    main()
