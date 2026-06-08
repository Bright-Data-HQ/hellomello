"""List Hellomello pages that DataForSEO sees ranking in Australia."""
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

body = [{
    "target": "hellomello.com.au",
    "location_name": "Australia",
    "language_name": "English",
    "limit": 200,
    "order_by": ["metrics.organic.etv,desc"],
}]
d = call("https://api.dataforseo.com/v3/dataforseo_labs/google/relevant_pages/live", body)
print("cost:", d.get("cost"), "| status:", d.get("status_message"))
res = (d.get("tasks") or [{}])[0].get("result") or []
total = res[0].get("total_count") if res else None
items = (res[0].get("items") or []) if res else []
print("total ranking pages:", total, "| pulled:", len(items))

rows = []
for it in items:
    page = it.get("page_address")
    m = it.get("metrics", {}).get("organic", {})
    rows.append({"url": page, "kw": m.get("count"), "etv": round(m.get("etv") or 0, 1),
                 "pos1": m.get("pos_1"), "top3": (m.get("pos_1") or 0) + (m.get("pos_2_3") or 0)})

json.dump(rows, open("strategy/research/hm-pages.json", "w"), indent=2)
print(f"\n{'KWs':>5} {'ETV':>7}  URL")
for r in sorted(rows, key=lambda x: -(x["kw"] or 0)):
    print(f"{str(r['kw']):>5} {str(r['etv']):>7}  {r['url']}")
