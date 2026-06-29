#!/usr/bin/env python3
"""Fetch competitor SEO data from DataForSEO and write pipeline-compatible CSVs.

Replaces the SEMrush manual exports. Produces the three files the audit and
analyze scripts expect, with the same headers:

  <domain>-organic.Positions-au-<YYYYMMDD>.csv
  <domain>-organic.PagesV3-au-<YYYYMMDD>.csv
  <domain>-backlinks_pages.csv

Credentials are read from the environment (source .env.vars first):
  dataforseo_api_basic_auth   (base64 of "login:password")
  -- or --
  dataforseo_api_login + dataforseo_api_password

Usage:
  python3 fetch_dataforseo.py <domain> <out_dir> [--date YYYYMMDD]
                              [--kw-max 3000] [--pages-max 1000] [--bl-max 1000]
  python3 fetch_dataforseo.py --probe <domain>     # cheap 10-row sanity probe
"""
import os, sys, csv, json, base64, argparse, time
import urllib.request, urllib.error
from datetime import date

BASE = "https://api.dataforseo.com/v3"
LOCATION = "Australia"
LANGUAGE = "English"
PAGE_LIMIT = 1000  # DataForSEO Labs max rows per request


def auth_header():
    b = os.environ.get("dataforseo_api_basic_auth")
    if not b:
        login = os.environ.get("dataforseo_api_login")
        pw = os.environ.get("dataforseo_api_password")
        if login and pw:
            b = base64.b64encode(f"{login}:{pw}".encode()).decode()
    if not b:
        sys.exit("ERROR: set dataforseo_api_basic_auth (or login/password) in env")
    return "Basic " + b


def post(path, payload, retries=3):
    data = json.dumps(payload).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            BASE + path, data=data, method="POST",
            headers={"Authorization": auth_header(), "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"POST {path} HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"POST {path} failed after {retries} tries: {last}")


def task_items(resp):
    task = (resp.get("tasks") or [{}])[0]
    if task.get("status_code") != 20000:
        raise RuntimeError(f"task {task.get('status_code')}: {task.get('status_message')}")
    res = task.get("result") or []
    if not res:
        return []
    return res[0].get("items") or []


def g(d, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur or cur[k] is None:
            return default
        cur = cur[k]
    return cur


# ---------------------------------------------------------------- ranked keywords
def fetch_positions(domain, kw_max):
    rows = []
    offset = 0
    while offset < kw_max:
        limit = min(PAGE_LIMIT, kw_max - offset)
        payload = [{
            "target": domain,
            "location_name": LOCATION,
            "language_name": LANGUAGE,
            "limit": limit,
            "offset": offset,
            "load_rank_absolute": True,
            "order_by": ["ranked_serp_element.serp_item.etv,desc"],
        }]
        items = task_items(post("/dataforseo_labs/google/ranked_keywords/live", payload))
        if not items:
            break
        for it in items:
            se = g(it, "ranked_serp_element", "serp_item", default={})
            pos = se.get("rank_group") or se.get("rank_absolute")
            url = se.get("url") or ""
            if not pos or not url:
                continue
            intents = []
            mi = g(it, "keyword_data", "search_intent_info", "main_intent")
            if mi:
                intents.append(mi)
            serp_feats = g(it, "keyword_data", "serp_info", "serp_item_types", default=[]) or []
            rows.append({
                "Keyword": g(it, "keyword_data", "keyword", default=""),
                "Position": pos,
                "Search Volume": g(it, "keyword_data", "keyword_info", "search_volume", default=0) or 0,
                "Traffic": round(se.get("etv") or 0.0, 2),
                "URL": url,
                "Keyword Difficulty": g(it, "keyword_data", "keyword_properties", "keyword_difficulty", default=0) or 0,
                "CPC": round(g(it, "keyword_data", "keyword_info", "cpc", default=0) or 0, 2),
                "Keyword Intents": ",".join(intents),
                "SERP Features by Keyword": ",".join(serp_feats),
            })
        if len(items) < limit:
            break
        offset += limit
    return rows


# ---------------------------------------------------------------- relevant pages
def fetch_pages(domain, pages_max):
    payload = [{
        "target": domain,
        "location_name": LOCATION,
        "language_name": LANGUAGE,
        "limit": min(PAGE_LIMIT, pages_max),
        "order_by": ["metrics.organic.etv,desc"],
    }]
    items = task_items(post("/dataforseo_labs/google/relevant_pages/live", payload))
    raw = []
    for it in items:
        org = g(it, "metrics", "organic", default={}) or {}
        etv = org.get("etv") or 0.0
        if etv <= 0:
            continue
        raw.append({
            "URL": it.get("page_address") or "",
            "Traffic": round(etv, 2),
            "Number of Keywords": org.get("count") or 0,
            "_etv": etv,
        })
    total = sum(r["_etv"] for r in raw) or 1.0
    rows = []
    for r in raw:
        rows.append({
            "URL": r["URL"],
            "Traffic": r["Traffic"],
            "Number of Keywords": r["Number of Keywords"],
            "Traffic (%)": round(r["_etv"] / total * 100, 2),
            "Primary Intent": "—",
            "Top Keyword": "—",
        })
    return rows


# ---------------------------------------------------------------- backlinks pages
def fetch_backlinks(domain, bl_max):
    payload = [{
        "target": domain,
        "limit": min(PAGE_LIMIT, bl_max),
        "order_by": ["backlinks,desc"],
        "filters": [["backlinks", ">", 0]],
    }]
    items = task_items(post("/backlinks/pages/live", payload))
    rows = []
    for it in items:
        url = it.get("url") or ""
        if not url:
            continue
        rows.append({
            "Source url": url,
            "Source title": g(it, "meta", "title", default="") or it.get("title", "") or "",
            "Backlinks": it.get("backlinks") or 0,
            "Domains": it.get("referring_domains") or 0,
            "Response code": it.get("status_code") or "",
            "External links": it.get("external_links_count") or "",
            "First seen": it.get("first_seen") or "",
            "Last seen": it.get("last_visited") or it.get("last_seen") or "",
        })
    return rows


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def probe(domain):
    payload = [{
        "target": domain, "location_name": LOCATION, "language_name": LANGUAGE,
        "limit": 10, "order_by": ["ranked_serp_element.serp_item.etv,desc"],
    }]
    items = task_items(post("/dataforseo_labs/google/ranked_keywords/live", payload))
    print(f"PROBE {domain}: {len(items)} keywords (top 10 by traffic)")
    for it in items:
        kw = g(it, "keyword_data", "keyword", default="")
        vol = g(it, "keyword_data", "keyword_info", "search_volume", default=0)
        pos = g(it, "ranked_serp_element", "serp_item", "rank_group")
        etv = g(it, "ranked_serp_element", "serp_item", "etv", default=0)
        print(f"  pos {pos:>3}  vol {vol:>7}  etv {etv:>7.1f}  {kw}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("domain")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    ap.add_argument("--kw-max", type=int, default=3000)
    ap.add_argument("--pages-max", type=int, default=1000)
    ap.add_argument("--bl-max", type=int, default=1000)
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()

    if args.probe:
        probe(args.domain)
        return

    if not args.out_dir:
        sys.exit("ERROR: out_dir required unless --probe")
    os.makedirs(args.out_dir, exist_ok=True)
    d, slug_date = args.domain, args.date

    print(f"Fetching positions for {d} ...")
    pos = fetch_positions(d, args.kw_max)
    write_csv(os.path.join(args.out_dir, f"{d}-organic.Positions-au-{slug_date}.csv"),
              pos, ["Keyword", "Position", "Search Volume", "Traffic", "URL",
                    "Keyword Difficulty", "CPC", "Keyword Intents", "SERP Features by Keyword"])
    print(f"  {len(pos)} keywords")

    print(f"Fetching pages for {d} ...")
    pages = fetch_pages(d, args.pages_max)
    write_csv(os.path.join(args.out_dir, f"{d}-organic.PagesV3-au-{slug_date}.csv"),
              pages, ["URL", "Traffic", "Number of Keywords", "Traffic (%)",
                      "Primary Intent", "Top Keyword"])
    print(f"  {len(pages)} pages")

    print(f"Fetching backlink pages for {d} ...")
    try:
        bl = fetch_backlinks(d, args.bl_max)
        write_csv(os.path.join(args.out_dir, f"{d}-backlinks_pages.csv"),
                  bl, ["Source url", "Source title", "Backlinks", "Domains",
                       "Response code", "External links", "First seen", "Last seen"])
        print(f"  {len(bl)} backlink pages")
    except Exception as e:
        print(f"  backlinks skipped ({e}) — slides 15/16 auto-hide")


if __name__ == "__main__":
    main()
