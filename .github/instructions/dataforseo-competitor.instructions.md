---
name: "DataForSEO Competitor Data"
description: "Use DataForSEO as the default source for competitor SEO data collection and exports. Keep exported files compatible with the existing competitor deck audit and analysis scripts."
applyTo: ["competitors/**/*.md", "competitors/**/*.py", "competitors/**/*.json"]
---

# DataForSEO Competitor Data

Use these rules for all competitor data preparation work.

## Source of truth
- Use DataForSEO as the default provider instead of SEMrush.
- Keep output file naming and CSV headers compatible with the existing competitor pipeline.

## Required output files per competitor
- `<domain>-organic.Positions-au-<YYYYMMDD>.csv`
- `<domain>-organic.PagesV3-au-<YYYYMMDD>.csv`
- `<domain>-backlinks_pages.csv`

## Required minimum headers
- Positions: `Keyword`, `Position`, `Search Volume`, `Traffic`, `URL`
- Pages: `URL`, `Traffic`
- Backlinks pages: `Source url`

## Compatibility rule
- Do not change audit or analysis expectations unless explicitly requested.
- If DataForSEO field names differ, map them during export while preserving the expected CSV headers.

## Region and quality
- Target Australia for competitor analysis unless a task explicitly says otherwise.
- Keep export freshness within 45 days when possible.

## Implementation references
- For detailed workflow and field mapping, follow [DATA_PREPARATION_DATAFORSEO.md](DATA_PREPARATION_DATAFORSEO.md).
