# Data Preparation with DataForSEO

This guide replaces SEMrush for competitor data collection.
It keeps the same output filenames and core columns, so the current audit and deck scripts continue to work.

Use this with:
- [DATA_AUDIT.md](DATA_AUDIT.md)
- [INSTRUCTIONS.md](INSTRUCTIONS.md)

## 1. Environment setup

Store credentials in [.env.vars](../../../.env.vars):

- dataforseo_api_login
- dataforseo_api_password
- dataforseo_api_basic_auth

Shell setup:

```bash
set -a
source .env.vars
set +a
```

Base request headers:

```bash
AUTH="Authorization: Basic ${dataforseo_api_basic_auth}"
JSON="Content-Type: application/json"
```

## 2. Conventions

| Setting | Value |
|---|---|
| Search engine | google |
| Location | Australia |
| Language | English |
| Save folder | competitors/<slug>/data/raw/ |
| Encoding | UTF-8 |
| Freshness target | 45 days or less |

## 3. Required outputs

Create these files for each competitor domain.

### 3.1 Positions file

Target filename:

- <domain>-organic.Positions-au-<YYYYMMDD>.csv

DataForSEO source:

- DataForSEO Labs, Google, Ranked Keywords, Live
- Endpoint in docs: dataforseo_labs/google/ranked_keywords/live

Minimum output columns for pipeline compatibility:

- Keyword
- Position
- Search Volume
- Traffic
- URL

Recommended extra columns:

- Keyword Difficulty
- CPC
- Keyword Intents
- SERP Features by Keyword

Notes:

- Pull enough rows to reach at least 1,000 keywords, ideally 10,000.
- If the API uses pagination, continue until you hit your row target.

### 3.2 Pages file

Target filename:

- <domain>-organic.PagesV3-au-<YYYYMMDD>.csv

DataForSEO source:

- DataForSEO Labs, Google, Top Pages, Live
- Endpoint in docs: dataforseo_labs/google/top_pages/live

Minimum output columns for pipeline compatibility:

- URL
- Traffic

Recommended extra columns:

- Number of Keywords
- Top Keyword
- Primary Intent

### 3.3 Backlinks pages file

Target filename:

- <domain>-backlinks_pages.csv

DataForSEO source:

- Backlinks API, Pages, Live
- Endpoint in docs: backlinks/pages/live

Minimum output columns for pipeline compatibility:

- Source url

Recommended extra columns:

- Source title
- Backlinks
- Domains
- Response code
- External links

## 4. Optional outputs

### 4.1 Trends file

Target filename:

- <domain>-trends.csv

Suggested source:

- Domain visibility or keyword history endpoint from DataForSEO Labs

Target columns:

- date
- organic_traffic
- organic_keywords
- organic_cost

### 4.2 SERP features file

Target filename:

- <domain>-serp-features.csv

Target columns:

- keyword
- serp_features_present
- serp_features_owned

### 4.3 Share of voice file

Target filename:

- sov.csv

Target columns:

- domain
- organic_traffic
- organic_cost
- organic_keywords

### 4.4 New and lost backlinks file

Target filename:

- <domain>-backlinks-new-lost.csv

Suggested source:

- Backlinks history endpoint from DataForSEO Backlinks API

Target columns:

- week
- new_links
- lost_links
- new_referring_domains
- lost_referring_domains

## 5. Field mapping rules

Map DataForSEO fields to deck CSV fields during export.

| CSV field | Map from DataForSEO |
|---|---|
| Keyword | keyword |
| Position | rank_group or rank_absolute |
| Search Volume | keyword_info.search_volume |
| Traffic | estimated monthly traffic field from endpoint response |
| URL | url or target_url |
| CPC | keyword_info.cpc |
| Keyword Difficulty | keyword_info.keyword_difficulty |
| Source url | source_url |
| Source title | page_title or title |
| Backlinks | backlinks or backlinks_count |
| Domains | referring_domains |

If a field name is slightly different in your response, keep the CSV header as shown above.

## 6. Practical request flow

1. Create folder: competitors/<slug>/data/raw/.
2. Fetch ranked keywords for the domain and export Positions CSV.
3. Fetch top pages for the domain and export Pages CSV.
4. Fetch backlink pages and export backlinks pages CSV.
5. Run audit.
6. If audit passes, run analyse and build scripts.

Commands:

```bash
python3 competitors/_template/code/audit.py competitors/<slug> --brand '<brand-regex>'
python3 competitors/<slug>/code/analyze.py
python3 competitors/<slug>/code/build_offline.py
```

## 7. Data quality checks

Before building:

- Confirm AU targeting in request payload.
- Confirm all required files exist in competitors/<slug>/data/raw/.
- Confirm Positions has at least 200 rows, and ideally 1,000 plus.
- Confirm Pages has at least 25 rows.
- Confirm Backlinks pages has at least 50 rows.
- Confirm export date is recent.

If any blocker fails, re-run the API calls and rebuild CSV exports.

## 8. Documentation check list

When implementing this in scripts, verify each endpoint and parameter name against DataForSEO docs before committing:

- Authentication method
- Endpoint path
- Pagination parameters
- Location and language identifiers
- Exact response field names
- Rate limits and retry behaviour
