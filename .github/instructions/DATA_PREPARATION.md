# Data Preparation — SEMrush MCP Brief

This is the **single source of truth** for preparing competitor data via the SEMrush MCP.
Every competitor deck is built from the files described here. The audit script
([code/audit.py](code/audit.py)) and the deck template both depend on these
exact filenames, columns, and folder locations.

Read this together with [DATA_AUDIT.md](DATA_AUDIT.md) (the readiness check)
and [INSTRUCTIONS.md](INSTRUCTIONS.md) (the deck spec).

---

## 0. Conventions (apply to every request)

| Setting | Value | Notes |
|---|---|---|
| Database / region | **`au`** | Never `us` or global — AU TGA market only |
| Date | as fresh as available | Audit will fail if export > 45 days old |
| Format | **CSV** | Except Lighthouse (JSON) |
| Encoding | UTF-8 | |
| Row limits | request the max the report allows | 10K for Positions, 1K for Pages, 2K for Backlinks |
| Filename date | `YYYYMMDD` of the export day | Matches SEMrush filename pattern |
| **Save location** | **`competitors/<SLUG>/data/raw/`** | **Each competitor has its own `data/` folder. Audit + analyze scripts only look here. Create the folder if it doesn't exist.** |

---

## 1. Required exports (3 files — unlocks 13 of 20 slides)

Without all three, **do not build the deck**.

### 1.1 Organic Positions
- **SEMrush report:** *Domain Analytics → Organic Research → Positions*
- **MCP tool:** `domain_organic` (or equivalent)
- **Params:** `domain=<DOMAIN>`, `database=au`, `display_limit=10000`
- **Required columns:**
  `keyword, position, search_volume, cpc, competition, kd, traffic, traffic_cost, url, intents, serp_features, timestamp`
- **Save as:** `<DOMAIN>-organic.Positions-au-<YYYYMMDD>.csv`
- **Unlocks slides:** 02, 04, 07, 09, 11, 12, 14, 19

### 1.2 Organic Pages
- **SEMrush report:** *Domain Analytics → Organic Research → Pages*
- **MCP tool:** `domain_organic_pages`
- **Params:** `domain=<DOMAIN>`, `database=au`, `display_limit=1000`
- **Required columns:**
  `url, traffic, traffic_cost, number_of_keywords, last_seen`
- **Save as:** `<DOMAIN>-organic.PagesV3-au-<YYYYMMDD>.csv`
- **Unlocks slides:** 02, 10, 13

### 1.3 Indexed Backlink Pages
- **SEMrush report:** *Backlink Analytics → Indexed Pages*
- **MCP tool:** `backlinks_pages`
- **Params:** `target=<DOMAIN>`, `target_type=root_domain`, `display_limit=2000`
- **Required columns:**
  `source_url, source_title, response_code, backlinks_count, referring_domains, external_links, internal_links, last_seen`
- **Save as:** `<DOMAIN>-backlinks_pages.csv`
- **Unlocks slides:** 02, 15

---

## 2. Optional exports (each unlocks one extra slide)

Decks degrade gracefully — missing optional files auto-hide their slides.
Request these only when cheap or strategically important for that competitor.

### 2.1 Domain Trends — 12 months
- **SEMrush report:** *Domain Overview → Trends* / *Historical Data*
- **MCP tool:** `domain_rank_history` (monthly granularity)
- **Params:** `domain=<DOMAIN>`, `database=au`, `display_date=last 12 months`
- **Required columns:** `date, organic_traffic, organic_keywords, organic_cost`
- **Save as:** `<DOMAIN>-trends.csv`
- **Unlocks slide:** 05 Trajectory

### 2.2 SERP Features
- **SEMrush report:** *Position Tracking → SERP Features* (or richer column set on Positions)
- **MCP tool:** `domain_organic` with `export_columns` including `Fp` (features present) + `Fl` (features owned)
- **Params:** `domain=<DOMAIN>`, `database=au`, `display_limit=5000`
- **Required columns:** `keyword, serp_features_present, serp_features_owned`
- **Save as:** `<DOMAIN>-serp-features.csv`
- **Unlocks slide:** 06 SERP features & AI Overviews

### 2.3 Share of Voice (multi-domain)
- **SEMrush report:** *Domain vs Domain* / *Market Explorer*
- **MCP tool:** `domain_vs_domain`
- **Params:** `domains=alternaleaf.com.au|polln.com|herbly.com.au|easykind.com.au|hellomello.com.au`, `database=au`
- **Required columns:** `domain, organic_traffic, organic_cost, organic_keywords`
- **Save as:** `sov.csv` *(one shared file — same SOV table is used across every deck)*
- **Unlocks slide:** 08 Share of voice

### 2.4 New & Lost Backlinks — 90 days
- **SEMrush report:** *Backlink Analytics → New & Lost*
- **MCP tool:** `backlinks_overview` + `backlinks_new_lost`
- **Params:** `target=<DOMAIN>`, `target_type=root_domain`, `display_date=last 90 days` (weekly buckets)
- **Required columns:** `week, new_links, lost_links, new_referring_domains, lost_referring_domains`
- **Save as:** `<DOMAIN>-backlinks-new-lost.csv`
- **Unlocks slide:** 16 Backlink velocity & quality

### 2.5 Lighthouse / Core Web Vitals *(not from SEMrush)*
Run locally on the top 5 URLs from the Pages CSV:
```bash
npx lighthouse <url> --output=json \
  --output-path=<slug>-lighthouse-<n>.json \
  --only-categories=performance,seo,best-practices
```
Combine into a single `<DOMAIN>-lighthouse.json` array.
- **Required fields:** LCP, INP, CLS, performance score, SEO score, schema presence (`script[type="application/ld+json"]`)
- **Unlocks slide:** 17 Technical & E-E-A-T (combined with `notes.json`)

---

## 3. Cost reference

| File | Approx SEMrush units | Slides unlocked |
|---|---|---|
| 1.1 Positions (10K) | ~10,000 | 8 |
| 1.2 Pages (1K) | ~1,000 | 3 |
| 1.3 Backlinks pages (2K) | ~2,000 | 2 |
| 2.1 Trends history | ~50 | 1 |
| 2.2 SERP features | included in 1.1 | 1 |
| 2.3 SOV (5 domains) | ~500 | 1 |
| 2.4 New/lost backlinks | ~500 | 1 |

- **Minimum viable deck** (items 1.1–1.3 only): ≈ 13K units, 13 slides
- **Full 20-slide deck** (items 1.1–2.4 + Lighthouse + notes.json): ≈ 14K units

---

## 4. Ready-to-send MCP prompt

Paste this into the SEMrush MCP, replacing `<DOMAIN>`, `<SLUG>`, and `<YYYYMMDD>`.

> **All files MUST be saved into** `competitors/<SLUG>/data/raw/` — this is the
> data folder for that specific domain. The audit script and `analyze.py` discover
> files by globbing this exact folder; files placed anywhere else will be invisible.
> If the folder doesn't exist yet, create it first: `mkdir -p competitors/<SLUG>/data/raw`.

```
For competitor domain <DOMAIN> in database au, please export the following CSVs
and save ALL of them into the folder:

    competitors/<SLUG>/data/raw/

(Create the folder if it doesn't exist. Do not place files anywhere else —
the audit and build pipeline only reads from this exact path.)

REQUIRED:
1. Organic Positions — top 10,000 ranking keywords with columns:
   keyword, position, search_volume, cpc, competition, kd,
   traffic (estimated monthly visits), traffic_cost,
   url, intents (commercial/info/nav/trans), serp_features, timestamp.
   Save as: competitors/<SLUG>/data/raw/<DOMAIN>-organic.Positions-au-<YYYYMMDD>.csv

2. Organic Pages — top 1,000 pages with columns:
   url, traffic, traffic_cost, number_of_keywords, last_seen.
   Save as: competitors/<SLUG>/data/raw/<DOMAIN>-organic.PagesV3-au-<YYYYMMDD>.csv

3. Indexed Backlink Pages — top 2,000 with columns:
   source_url, source_title, response_code, backlinks_count,
   referring_domains, external_links, internal_links, last_seen.
   Save as: competitors/<SLUG>/data/raw/<DOMAIN>-backlinks_pages.csv

OPTIONAL (please include if cheap to fetch):
4. Domain Trends — monthly history for last 12 months:
   date, organic_traffic, organic_keywords, organic_cost.
   Save as: competitors/<SLUG>/data/raw/<DOMAIN>-trends.csv

5. SERP Features — for top 5,000 keywords:
   keyword, serp_features_present, serp_features_owned.
   Save as: competitors/<SLUG>/data/raw/<DOMAIN>-serp-features.csv

6. Domain vs Domain (share of voice) — compare:
   alternaleaf.com.au, polln.com, herbly.com.au, easykind.com.au,
   hellomello.com.au — organic_traffic, organic_cost, organic_keywords.
   Save as: competitors/<SLUG>/data/raw/sov.csv

7. New & Lost Backlinks — last 90 days, weekly:
   week, new_links, lost_links, new_referring_domains,
   lost_referring_domains.
   Save as: competitors/<SLUG>/data/raw/<DOMAIN>-backlinks-new-lost.csv
```

---

## 5. Competitor request list

Use the slugs and domains below when generating MCP requests. Domains are best-guess from
[competitors.md](../competitors.md) — confirm any 🟡 entry before spending units.

| Slug | Domain | Position | Notes |
|---|---|---|---|
| alternaleaf | alternaleaf.com.au | ✅ Model | Already done — reference build |
| polln | polln.com | ✅ Model | Data already in repo, not yet processed |
| herbly | herbly.com.au | 🟡 Watch | Confirm domain |
| dispensed | dispensed.com.au | ⚠️ Careful | Confirm domain |
| easykind | easykind.com.au | ✅ Model | Confirm domain |
| healing-leaves | healingleaves.com.au | ⚠️ Careful | Confirm domain |
| candor-medical | candormedical.com.au | ✅ Model | Confirm domain |
| acacia-clinic | acaciaclinic.com.au | ✅ Model | Confirm domain |
| nuleaf-clinics | nuleafclinics.com.au | 🟡 Unsure | Confirmed in `competitors.md` |
| greencare | — | ✅ Model | **Domain unknown — confirm before fetching** |
| horizon-health | — | ✅ Model | **Domain unknown — confirm before fetching** |
| econohealth | econohealth.com.au | ✅ Model | Confirm domain |

> Each MCP fetch costs ~13K units for the minimum viable deck. With 11 outstanding
> competitors that is ~143K units. Do a cheap **domain probe** (single Positions
> call with `display_limit=10`) before committing the full 10K-keyword pull.

---

## 6. Workflow per competitor

```bash
# 1. scaffold the folder
mkdir -p competitors/<slug>/data/raw competitors/<slug>/data/screenshots competitors/<slug>/presentation/assets

# 2. fire the MCP prompt (§4) and save outputs into data/raw/

# 3. audit
python3 competitors/_template/code/audit.py competitors/<slug> --brand '<brand-regex>'

# 4. if VERDICT: BUILD, copy the template and process
cp competitors/_template/presentation/presentation.html competitors/<slug>/presentation/
cp -r competitors/_template/code competitors/<slug>/
python3 competitors/<slug>/code/analyze.py
python3 competitors/<slug>/code/build_offline.py

# 5. open presentation/presentation.html, QA against INSTRUCTIONS.md §9 checklist
```

---

## 7. When to refresh

- Before every deck rebuild
- After SEMrush announces a column / API change
- Every **45 days** for "living" decks we keep refreshed (matches audit freshness threshold)
- Whenever a competitor publishes a major site change (re-pull §1.2 Pages at minimum)
