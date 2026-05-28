# Data Audit — Competitor Deck Readiness Check

Run this audit **before** building a competitor deck. It answers two questions:

1. **Do we have enough data to build a defensible deck?**
2. **Is the data we have correct, fresh, and matching the right entity?**

If the audit fails on any **🔴 blocker**, do not build the deck. Fix the data first.

---

## How to run

```bash
cd competitors/<competitor-slug>
python3 ../_template/code/audit.py
```

The script prints a coloured report and exits non-zero if any blocker fails.
You can also run the manual checklist below if you don't trust the script for a borderline case.

---

## 1. Identity & scope check (🔴 blockers)

| # | Check | How to verify | Why it matters |
|---|---|---|---|
| 1.1 | Domain matches the competitor in `competitors.md` | Open one Positions CSV row, confirm `Url` starts with the expected domain | Wrong domain = entire deck is about the wrong company |
| 1.2 | Database is **`au`** | SEMrush filename contains `-au-` or column "Database" = `au` | An `us` or global export tells us nothing about the AU market |
| 1.3 | Export date is within the last **45 days** | Date suffix in filename, e.g. `20260528` | SEO moves fast; >45 days old = stale narrative |
| 1.4 | All 3 required CSVs are present | `*-organic.Positions-*.csv`, `*-organic.PagesV3-*.csv`, `*-backlinks_pages.csv` | Without these, the diagnostic + topic slides cannot render |
| 1.5 | All 3 CSVs are from the **same export date** (±7 days) | Compare date suffixes | Mixing dates produces incoherent KPIs |
| 1.6 | Files are not truncated | Each file > 5 KB and last row parses cleanly | Half-downloaded CSVs are a frequent silent failure |

---

## 2. Volume & coverage check (🟠 quality)

A deck with too little data is misleading rather than informative. Minimums:

| Metric | Minimum | Healthy | Source |
|---|---|---|---|
| Ranking keywords | 200 | 1,000+ | Positions CSV row count |
| Pages with traffic | 25 | 100+ | Pages CSV row count |
| Indexed backlink pages | 50 | 500+ | Backlinks CSV row count |
| Distinct subdomains seen | 1 | 2+ | unique `Url` host in Positions |
| Brand-keyword share | <85% | <60% | rows where keyword matches brand regex |

**If ranking kw < 200**: the competitor is too small for a full deck. Produce a one-page snapshot instead.
**If brand share > 85%**: most "traffic" is just people Googling their name — most non-brand insights will be noise. Flag this prominently on slide 02.

---

## 3. Column / schema check (🔴 blockers)

SEMrush occasionally changes column names. Each CSV must expose the columns we read.

### Positions CSV — must contain:
- `Keyword`
- `Position`
- `Search Volume`
- `Traffic` *(or `Estimated Traffic`)*
- `Url`
- `Keyword Intents` *(or `Intents`)*

### Pages CSV — must contain:
- `URL` *(or `Url`)*
- `Traffic`
- `Number of Keywords` *(or `Keywords`)*

### Backlinks CSV (`*-backlinks_pages.csv`) — must contain:
- `Source url`
- `Source title` *(optional)*
- `Backlinks`, `Domains`, `External links` *(optional, used for ranking)*

> Note: the `backlinks_pages` export carries source-side columns only; the target
> is implicit (the competitor's own domain). If you also have the SEMrush
> `backlinks-overview` export, drop it in to unlock slide 16.

If column names have drifted, update `analyze.py` first — do **not** rename CSV columns by hand.

---

## 4. Sanity check (🟠 quality)

Run these "smell tests" on the loaded data:

| Check | Pass condition | Fail meaning |
|---|---|---|
| Positions: at least one row with `Position` = 1 | yes | Almost certainly a broken export |
| Positions: traffic sum > 0 | yes | Export ran but returned empty traffic estimates |
| Pages: top page traffic < 90% of total | yes | One URL hoarding all traffic = look for an analytics anomaly |
| Backlinks: distinct source domains > 10 | yes | Profile is too thin to draw any backlink conclusion |
| Top 10 keywords contain ≥3 distinct stems | yes | Otherwise the topic chart will be degenerate |

---

## 5. Optional data (🟢 nice-to-have — unlocks extra slides)

| File suffix | Unlocks slide | What to check |
|---|---|---|
| `*-trends.csv` | 05 Trajectory | ≥6 months of monthly rows |
| `*-serp-features.csv` | 06 SERP features | Covers tracked keywords from Positions |
| `*-sov.csv` | 08 Share of voice | Contains Hellomello + ≥2 other competitors from `competitors.md` |
| `*-backlinks-new-lost.csv` | 16 Velocity | ≥90 days of rows |
| `*-lighthouse.json` | 17 E-E-A-T | Run on top 5 URLs from Pages CSV |

Missing optional files → those slides auto-hide. Do not fake them.

---

## 6. Qualitative inputs check (🟠 quality)

| File | Required keys | Notes |
|---|---|---|
| `data/notes.json` | `brand.visual_system`, `brand.site_architecture`, `brand.tone_compliance`, `position` | Slides 3, 17, 18, 19, 20 |
| Screenshots / reference (optional) | — | Used for analyst reference only; never embedded in deck |

`position` must be one of `model | careful | watch` and must match `competitors.md`.

---

## 7. Comparability check (🟠 — required if building multiple competitors)

When building several decks in the same week:

- [ ] All competitors exported from SEMrush within the same 14-day window
- [ ] All on the `au` database
- [ ] Same topic taxonomy in `analyze.py` (don't fork per-competitor)
- [ ] Same date format on KPI tiles (e.g. "May 2026")
- [ ] Share-of-voice slide (08) uses the **same competitor set** across all decks

If any competitor was exported on a materially different date, mark its slide 02 with the date and never compare absolute numbers across decks from different windows.

---

## 8. Decision matrix — should we build?

| Required CSVs | Ranking kw | Brand share | Verdict |
|---|---|---|---|
| ✅ all 3 | ≥1,000 | <60% | **Build full 20-slide deck** |
| ✅ all 3 | 200–1,000 | <85% | **Build, but flag thin data** on slide 02 |
| ✅ all 3 | <200 | any | **One-page snapshot only**, not a full deck |
| ❌ missing any | any | any | **Do not build.** Re-export from SEMrush |

---

## 9. Audit report format

The `audit.py` script outputs:

```
COMPETITOR AUDIT — <slug>
────────────────────────────────────────────────
[BLOCKERS]
  ✓ Domain matches expected
  ✓ AU database
  ✓ Exports within 45 days
  ✓ All 3 required CSVs present
  ✓ Schema OK

[VOLUME]
  ✓ 4,536 ranking keywords (healthy)
  ✓ 312 pages with traffic (healthy)
  ⚠ Brand share 72% — flag on slide 02

[OPTIONAL]
  ✗ trends.csv         → slide 05 will auto-hide
  ✗ serp-features.csv  → slide 06 will auto-hide
  ✓ sov.csv

[QUALITATIVE]
  ✓ notes.json present with all required keys

VERDICT: BUILD (with thin-data flag on brand share)
```

Non-zero exit code if any 🔴 blocker fails.

---

## 10. When to re-audit

- Before every deck build
- After any SEMrush re-export
- When SEMrush announces a column / API change
- Every 45 days for "living" decks we keep refreshed
