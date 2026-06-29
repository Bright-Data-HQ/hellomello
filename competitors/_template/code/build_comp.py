#!/usr/bin/env python3
"""Build a populated presentation.html from the template + data.json + notes.json.

Reads:  competitors/<slug>/data/data.json, data/notes.json
Writes: competitors/<slug>/presentation/presentation.html  (window.COMP filled)

Usage: python3 build_comp.py <slug> --brand "Name" --domain example.com.au --date "Jun 2026"
"""
import os, sys, json, argparse, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TPL = os.path.join(REPO, "competitors", "_template", "presentation", "presentation.html")

VERDICT = {
    "model":   ("Model off this", "green"),
    "careful": ("Be careful",     "red"),
    "watch":   ("Watch",          "amber"),
}


def k(n):
    n = float(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(round(n)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--brand", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--date", default="Jun 2026")
    ap.add_argument("--segment", default="Telehealth · Medicinal cannabis · AU")
    a = ap.parse_args()

    root = os.path.join(REPO, "competitors", a.slug)
    d = json.load(open(os.path.join(root, "data", "data.json")))
    notes = json.load(open(os.path.join(root, "data", "notes.json")))
    t = d["totals"]
    pos = notes.get("position", "watch")
    verdict, tone = VERDICT.get(pos, ("Watch", "amber"))
    brand_pct = round(100 * t["brand_traffic"] / max(1, t["traffic"]))
    top_share = round(100 * (d["top_pages"][0]["traffic"] / max(1, t["traffic"]))) if d["top_pages"] else 0

    pages = [{"url": p["url"].replace(f"https://", "").replace("www.", ""),
              "kw": p["kw"], "traffic": round(p["traffic"]), "intent": p.get("intent", "—") or "—"}
             for p in d["top_pages"][:6]]
    kws = [{"kw": x["kw"], "pos": x["pos"], "vol": x["vol"], "kd": round(x.get("kd", 0)),
            "intent": (x.get("intents") or "—")} for x in d["top_keywords"][:8]]
    nb = d.get("nonbrand_keywords", [])

    comp = {
        "brand": a.brand, "domain": a.domain,
        "tagline": notes.get("brand", {}).get("visual_system", ["—"])[0],
        "segment": a.segment, "prepared_for": "Hellomello", "prepared_by": "Bright Data",
        "date": a.date, "logo": "", "verdict": verdict, "verdict_tone": tone,
        "overview": {
            "summary": f"{k(t['traffic'])} monthly organic visits across {t['keywords']:,} ranking keywords; about {brand_pct}% is brand demand. Non-brand search is the open ground.",
            "facts": [["Ranking keywords", f"{t['keywords']:,}"], ["Ranking pages", str(t["pages"])],
                      ["Brand traffic share", f"{brand_pct}%"], ["Position", verdict]],
            "legal": " ".join(notes.get("brand", {}).get("tone_compliance", [])),
        },
        "brand_read": {"notes": " ".join(notes.get("brand", {}).get("site_architecture", [])), "screenshots": []},
        "seo": {
            "kpis": [
                {"label": "Monthly Organic Traffic", "value": k(t["traffic"]), "delta": ""},
                {"label": "Ranking Keywords", "value": f"{t['keywords']:,}", "delta": ""},
                {"label": "Brand Share", "value": f"{brand_pct}%", "delta": ""},
                {"label": "Top Page Share", "value": f"{top_share}%", "delta": ""},
            ],
            "narrative": f"Traffic concentrates on brand terms ({brand_pct}%). Non-brand reach sits across {t['nonbrand_kw']:,} keywords for {k(t['nonbrand_traffic'])} visits.",
        },
        "pages": {"headline": "Where the traffic lives", "rows": pages,
                  "insight": next((x for x in [notes.get('verdict', {}).get('avoid', [{}])[0].get('evidence')] if x), "Most pages earn little; the brand homepage dominates.")},
        "keywords": {"headline": "What they rank for", "rows": kws,
                     "insight": f"{len(nb)} non-brand winners include " + ", ".join(x['kw'] for x in nb[:3]) + "." if nb else "Almost entirely brand keywords."},
        "backlinks": {"kpis": [{"label": "Link data", "value": "n/a"}], "notes": "Backlink export not collected for this build; slide intentionally light."},
        "swot": {
            "s": ["Strong brand demand", f"{brand_pct}% brand traffic"],
            "w": ["Thin non-brand content", f"{t['pages']} ranking pages"],
            "o": ["Location and condition pages open", "Education content gap"],
            "t": ["Could scale content fast"],
        },
        "takeaways": [
            {"title": "What to copy", "body": (notes.get("verdict", {}).get("steal") or [{}])[0].get("note", "Brand-led funnel.")},
            {"title": "What to avoid", "body": (notes.get("verdict", {}).get("avoid") or [{}])[0].get("trap", "Thin content.")},
            {"title": "Where to win", "body": (notes.get("verdict", {}).get("implications") or ["Out-publish on education and locations."])[0]},
        ],
    }

    html = open(TPL, encoding="utf-8").read()
    block = "window.COMP = " + json.dumps(comp, indent=2) + ";"
    html = re.sub(r"window\.COMP = \{.*?\n\};", lambda m: block, html, count=1, flags=re.S)
    html = html.replace("Competitor Analysis — Template", f"Competitor Analysis — {a.brand}")
    out = os.path.join(root, "presentation", "presentation.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"{a.slug}: COMP written ({t['keywords']} kw, {brand_pct}% brand, {t['pages']} pages)")


if __name__ == "__main__":
    main()
