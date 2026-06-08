"""Keyword gap: terms competitors rank for in Australia that Hellomello does NOT.
Uses DataForSEO Labs domain_intersection in 'gap' mode (intersections=false would
not work here), so we pull each competitor's ranked keywords, then subtract HM's.
This is the reliable, well-documented path for a content-gap list.
"""
import os, json, urllib.request, urllib.error, time
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

COMPETITORS = ["alternaleaf.com.au", "polln.com", "herbly.com.au"]

def ranked(domain, limit=1000):
    body = [{
        "target": domain,
        "location_name": "Australia",
        "language_name": "English",
        "limit": limit,
        "order_by": ["keyword_data.keyword_info.search_volume,desc"],
        "filters": [
            ["ranked_serp_element.serp_item.rank_group", "<=", 20],
            "and",
            ["keyword_data.keyword_info.search_volume", ">", 50],
        ],
    }]
    d = call("https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live", body)
    cost = d.get("cost", 0) or 0
    res = (d.get("tasks") or [{}])[0].get("result") or []
    items = (res[0].get("items") or []) if res else []
    out = {}
    for it in items:
        kd = it.get("keyword_data", {})
        kw = kd.get("keyword")
        ki = kd.get("keyword_info", {})
        se = it.get("ranked_serp_element", {}).get("serp_item", {})
        if not kw:
            continue
        out[kw] = {"vol": ki.get("search_volume") or 0, "pos": se.get("rank_group"),
                   "cpc": ki.get("cpc")}
    return out, cost

# HM's own ranked keywords (any position) to subtract
hm, c0 = ranked("hellomello.com.au", limit=1000)
hm_terms = set(hm.keys())
total_cost = c0
print(f"HM ranked terms (vol>50, pos<=20): {len(hm_terms)} | cost ${round(c0,4)}")

comp_data = {}
for dom in COMPETITORS:
    data, c = ranked(dom)
    total_cost += c
    comp_data[dom] = data
    print(f"{dom}: {len(data)} terms | cost ${round(c,4)}")
    time.sleep(0.3)

# Build gap: term -> {vol, competitors:[(dom,pos)]}
gap = {}
for dom, data in comp_data.items():
    for kw, m in data.items():
        if kw in hm_terms:
            continue  # HM already ranks
        g = gap.setdefault(kw, {"vol": m["vol"], "cpc": m["cpc"], "by": []})
        g["by"].append((dom.split(".")[0], m["pos"]))

# Rank gap by (number of competitors covering it, volume)
ranked_gap = sorted(gap.items(), key=lambda kv: (-len(kv[1]["by"]), -kv[1]["vol"]))

json.dump({"hm_terms": sorted(hm_terms), "gap": {k: v for k, v in ranked_gap}},
          open("strategy/research/keyword-gap.json", "w"), indent=2)

print(f"\nTOTAL gap terms competitors rank for but HM does not: {len(ranked_gap)}")
print(f"TOTAL cost: ${round(total_cost,4)}\n")

# shared by all 3
shared3 = [(k, v) for k, v in ranked_gap if len(v["by"]) == 3]
print(f"=== Covered by ALL 3 competitors, HM absent ({len(shared3)}) ===")
for k, v in sorted(shared3, key=lambda kv: -kv[1]["vol"])[:40]:
    by = ", ".join(f"{d}:{p}" for d, p in v["by"])
    print(f"  {str(v['vol']):>6}  {k:45} [{by}]")

print(f"\n=== Top 40 gap terms by volume (any competitor) ===")
for k, v in sorted(ranked_gap, key=lambda kv: -kv[1]["vol"])[:40]:
    by = ", ".join(f"{d}:{p}" for d, p in v["by"])
    print(f"  {str(v['vol']):>6}  {k:45} [{by}]")
