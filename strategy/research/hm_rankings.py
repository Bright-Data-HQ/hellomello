"""Step 1: pull Hellomello's own Australian organic rankings + account balance."""
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

bal = call("https://api.dataforseo.com/v3/appendix/user_data", [])
res = (bal.get("tasks") or [{}])[0].get("result") or []
print("BALANCE:", (res[0].get("money", {}) if res else {}).get("balance"))

body = [{
    "target": "hellomello.com.au",
    "location_name": "Australia",
    "language_name": "English",
    "limit": 200,
    "order_by": ["ranked_serp_element.serp_item.rank_group,asc"],
    "filters": [["ranked_serp_element.serp_item.rank_group", "<=", 100]],
}]
d = call("https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live", body)
print("ranked_keywords cost:", d.get("cost"))
res = (d.get("tasks") or [{}])[0].get("result") or []
total = res[0].get("total_count") if res else None
items = (res[0].get("items") or []) if res else []
print("HM total ranked keywords:", total, "| pulled:", len(items))

rows = []
for it in items:
    kd = it.get("keyword_data", {})
    ki = kd.get("keyword_info", {})
    se = it.get("ranked_serp_element", {}).get("serp_item", {})
    rows.append({
        "kw": kd.get("keyword"),
        "pos": se.get("rank_group"),
        "vol": ki.get("search_volume"),
        "etv": se.get("etv"),
        "url": se.get("url"),
    })

json.dump(rows, open("strategy/research/hm-rankings.json", "w"), indent=2)

# Brand vs non-brand split
brand = [r for r in rows if r["kw"] and ("mello" in r["kw"].lower())]
nonbrand = [r for r in rows if r["kw"] and ("mello" not in r["kw"].lower())]
print(f"\nBrand kws: {len(brand)} | Non-brand kws: {len(nonbrand)}")
print("\nTop 40 NON-BRAND keywords HM ranks for (by position):")
for r in sorted(nonbrand, key=lambda x: (x["pos"] or 999))[:40]:
    print(f"  pos {r['pos']:>3} | vol {str(r['vol']):>6} | {r['kw']}")
