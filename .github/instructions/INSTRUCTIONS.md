# Hellomello — Competitor Deck Instruction Manual

This is the **canonical instruction** for producing a competitor analysis deck.
Every competitor (Alternaleaf, Polln, Herbly, Easykind, …) is built against this spec
so the decks are comparable, fast to produce, and consistent in voice.

For DataForSEO collection and export mapping, use [DATA_PREPARATION_DATAFORSEO.md](DATA_PREPARATION_DATAFORSEO.md).

> **Audience for the deck:** Hellomello leadership + marketing team.
> **Purpose:** Decide what to copy, what to avoid, and where the white space is.
> **Voice:** Editorial, confident, evidence-led. Not "agency slideware".

---

## 0. TL;DR — how to produce a deck

1. Copy `competitors/_template/` → `competitors/<competitor-slug>/`
2. Drop prepared CSV exports into `<competitor>/data/raw/` (see §3 for required + optional files, or use DataForSEO guide above)
3. Fill `<competitor>/data/notes.json` with qualitative observations (§4)
4. Run `python3 code/analyze.py` → produces `presentation/data.js`
5. Open `presentation/presentation.html` in a browser to QA
6. Run `python3 code/build_offline.py` → produces `presentation/presentation-offline.html` (sharable single file)
7. Update `competitors/competitors.md` legend if our position on them changes

---

## 1. Design principles (non-negotiable)

| # | Principle | Why |
|---|---|---|
| 1 | **One idea per slide** | If a slide needs two charts to make its point, split it |
| 2 | **Evidence before opinion** | Every claim must be backed by a number from the data or a screenshot we can defend |
| 3 | **Position/length over angle/area** | Bars beat pies. Always. |
| 4 | **Sort by value, not alphabetical** | Unless there's a natural order (time, geography, ranking buckets) |
| 5 | **Annotate, don't decorate** | Every chart has at least one inline callout pointing at the insight |
| 6 | **No legends if avoidable** | Label directly on bars/lines |
| 7 | **Print-safe palette** | Deck must read in B&W |
| 8 | **No emojis, no clipart, no stock photos** | Editorial type + restrained palette only |
| 9 | **The data may be incomplete — say so** | If we don't have trends or SERP-feature exports for a competitor, the slide auto-hides; never fake it |
| 10 | **Recommendation is the product** | The deck exists to drive a decision, not to dump data |
| 11 | **Attribution is "Bright Data"** | Never mention SEMrush, Ahrefs, or any data vendor in the deck. Footers and source captions read **"PREPARED BY BRIGHT DATA"**. Internal docs and code may name vendors freely |

---

## 2. Visual system

### Typography
- **Fraunces** (display serif, italics for emphasis) — slide titles, big numbers
- **Inter** (body) — paragraph text, table cells
- **JetBrains Mono** (eyebrows, labels, captions) — small metadata

### Palette (CSS variables)
```css
--ink:    #0E1411   /* primary text on light, background on dark slides */
--paper:  #F4EFE6   /* primary background on light, text on dark slides */
--moss:   #3E5641   /* primary accent (deep) */
--moss-2: #6B8E68   /* primary data bars (neutral) */
--moss-3: #A9CDA0   /* tertiary / highlights */
--sand:   #C9B58A   /* secondary metric bars */
--clay:   #B96A3D   /* warning / loss / failure callouts */
```

**Colour rules** (apply to every chart):
- Neutral data → `--moss-2`
- Secondary metric in a paired chart → `--sand`
- Failure / loss / risk / "<5 visits" → `--clay`
- Tertiary highlight → `--moss-3`
- Never rainbow palettes. Never gradients on data.

### Slide format
- 1280 × 720 (16:9), `aspect-ratio:16/9`
- Subtle SVG noise + radial vignette for editorial finish
- Alternating light/dark rhythm (see §5 below)

### Navigation (always present)
- `←` / `→` / `space` next, `P` present-mode fullscreen, `Esc` exit
- PDF export via `window.print()` with `@page{size:1280px 720px}`

---

## 3. Data inputs

Place all CSVs in `<competitor>/data/raw/`. Naming must follow the patterns below — `analyze.py` discovers files by suffix.

### Required (deck will not build without these)
| File suffix | Source | Used by slides |
|---|---|---|
| `*-organic.Positions-*.csv` | SEMrush → Organic Research → Positions | 02, 04, 07, 09, 11, 12, 14 |
| `*-organic.PagesV3-*.csv` | SEMrush → Organic Research → Pages | 02, 10, 13 |
| `*-backlinks_pages.csv` | SEMrush → Backlink Analytics → Indexed Pages | 02, 15 |

### Optional (slide auto-hides if absent)
| File suffix | Source | Unlocks slide |
|---|---|---|
| `*-trends.csv` | SEMrush → Domain Overview → Trends export | 05 Trajectory |
| `*-serp-features.csv` | SEMrush → Position Tracking → SERP Features | 06 SERP features |
| `*-backlinks-overview.csv` | SEMrush → Backlink Analytics → Overview | 16 Backlink velocity |
| `*-backlinks-new-lost.csv` | SEMrush → Backlink Analytics → New & Lost | 16 Backlink velocity |
| `*-sov.csv` | SEMrush → Market Explorer (multi-domain) | 08 Share of voice |
| `*-lighthouse.json` | Lighthouse CLI run on top 5 URLs | 17 Technical & E-E-A-T |

---

## 4. Qualitative notes (`notes.json`)

Several slides (03, 17, 18, 19, 20) are partially or fully qualitative. They read from `data/notes.json`:

```json
{
  "brand": {
    "visual_system": ["…", "…", "…"],
    "site_architecture": ["…", "…", "…"],
    "tone_compliance": ["…", "…", "…"]
  },
  "eeat": {
    "core_web_vitals": "amber",
    "schema_medical": "green",
    "author_bylines": "red",
    "medical_reviewer": "amber",
    "https": "green",
    "freshness": "amber",
    "notes": "Authors listed but no credentials shown."
  },
  "verdict": {
    "steal": [
      { "play": "Programmatic location pages", "effort": 3, "impact": 4, "note": "…" }
    ],
    "avoid": [
      { "trap": "Generic wellness hub", "evidence": "21 pages → 82 visits/mo" }
    ],
    "implications": ["…", "…", "…"]
  },
  "position": "model | careful | watch"
}
```

If a section is missing, its slide hides automatically.

---

## 5. Slide structure — 20 slides in 5 acts

| Act | Slides | Theme |
|---|---|---|
| 1 — **Frame** | 01–03 | Who they are, what the site looks like |
| 2 — **Diagnose** | 04–08 | Where they rank, what intent, trajectory, SERP features, share of voice |
| 3 — **Topic story** | 09–13 | What they publish and where it works / fails |
| 4 — **Authority** | 14–17 | Keywords, backlinks, trust signals |
| 5 — **Verdict** | 18–20 | What to steal, what to avoid, implications for Hellomello |

### Light/dark rhythm
```
01 D · 02 L · 03 L · 04 D · 05 L · 06 D · 07 L · 08 D ·
09 L · 10 D · 11 L · 12 L · 13 D ·
14 L · 15 D · 16 L · 17 D ·
18 L · 19 D · 20 L
```

### Slide-by-slide spec

#### Act 1 — Frame
| # | Title | Chart / Component | Required data | Insight target (the line we want the reader to say) |
|---|---|---|---|---|
| 01 | Cover | Editorial type only | Competitor name + period | — |
| 02 | Executive snapshot | KPI tile grid (6 tiles + delta arrows) | Positions + Pages + Backlinks | "Here's the size of the prize" |
| 03 | Brand & UX read | 3-column text panels | `notes.brand` | "This is what their brand promises" |

#### Act 2 — Diagnose
| # | Title | Chart / Component | Required data | Insight target |
|---|---|---|---|---|
| 04 | Position distribution | **Vertical bar**, green→grey gradient by depth | Positions | "Most of their wins are not on page 1" *(or vice versa)* |
| 05 | Trajectory 12mo | **Small-multiple line charts** (traffic / kw / links) | Trends *(optional)* | "Growing, flat, or bleeding?" |
| 06 | SERP features & AI Overviews | **Horizontal bullet bars** (owned vs available) | SERP features *(optional)* | "They own the snippets we want" |
| 07 | Search intent mix | **100% stacked horizontal bar** ×2 (intent, brand/non-brand) | Positions | "How much of their traffic is just brand?" |
| 08 | Share of voice | **Grouped horizontal bar** (traffic + $ value) vs competitor set | SOV *(optional)* | "They are N× our voice" |

#### Act 3 — Topic story (the core)
| # | Title | Chart / Component | Required data | Insight target |
|---|---|---|---|---|
| 09 | Topic map | **Paired horizontal bars** (kw count vs traffic) | Positions | "They rank in many topics but earn from few" |
| 10 | Content clusters | **Scatter / quadrant** — x:pages, y:traffic, size:avg pos, quadrants labelled Workhorse / Star / Bloat / Hidden gem | Pages | "Their /hub/ is bloat; their /support/ is the workhorse" |
| 11 | Location strategy | **AU choropleth map** + small bar of cities | Positions | "They've ignored Perth and 'near me'" |
| 12 | Conditions & clinical | **Dot plot / lollipop** + clinic non-brand keyword table | Positions | "They rank for chronic pain but earn 1 visit/mo" |
| 13 | Top pages — winners & losers | **Two ranked tables** with sparkbar cells | Pages | "Here's exactly which URLs print money — and which are decaying" |

#### Act 4 — Authority & trust
| # | Title | Chart / Component | Required data | Insight target |
|---|---|---|---|---|
| 14 | Keywords — top + non-brand opportunities | **Two ranked tables** with pos/vol/KD chips | Positions | "Here are the keywords we should steal" |
| 15 | Backlinks profile | **Horizontal stacked bar** by domain type + **DR histogram** | Backlinks | "Their link profile is N% news, M% directory" |
| 16 | Backlinks velocity & quality | **Diverging bar** (+new / −lost) by week | Backlinks new/lost *(optional)* | "They're gaining / bleeding links" |
| 17 | Technical & E-E-A-T scorecard | **Heatmap grid** (signals × competitors) | Lighthouse + `notes.eeat` *(optional)* | "Their YMYL posture is weak on author credentials" |

#### Act 5 — Verdict
| # | Title | Chart / Component | Required data | Insight target |
|---|---|---|---|---|
| 18 | What to steal | **Effort × Impact 2×2** with labelled dots | `notes.verdict.steal` | "These three plays first" |
| 19 | What to avoid | **Annotated callouts** over a failure bar chart | `notes.verdict.avoid` + Positions | "Don't repeat their mistakes" |
| 20 | Implications for Hellomello | **Gap matrix** (topic × competitor heatmap, Hellomello column highlighted) | All competitor data | "Here is our white space" |

---

## 6. Chart library — rules per chart type

| Chart | Use for | Encoding rules | Forbidden |
|---|---|---|---|
| Vertical bar | Ordered buckets (positions) | Bars share baseline; sort by natural order | 3D, gradients |
| Horizontal bar | Long category labels | Sort by value desc; labels right-aligned to bar end | — |
| Paired horizontal bars | Two metrics per category (e.g. kw + traffic) | Same scale family or normalised; label each bar | Stacking the two |
| 100% stacked bar | Composition of a single whole | Always 100%; segments labelled inline | More than 5 segments |
| Grouped bar | Comparing 2–3 metrics across few categories | ≤4 groups, ≤4 series | Beyond 4 series |
| Line (small multiples) | Time series with multiple metrics | One metric per panel, shared x-axis | Dual y-axis |
| Scatter / quadrant | Two continuous metrics + categorical insight | Quadrants labelled; outliers annotated | Trend lines unless meaningful |
| Dot plot / lollipop | Small numbers across many categories | Sort by value; dot colour = secondary metric | When values are large (use bars) |
| Diverging bar | Gains vs losses | Green right, red left, shared zero axis | Two separate charts |
| Heatmap | Categorical scorecard, dense comparison | 3–5 colour stops max; legend top-right | Continuous gradient |
| Bullet bar | Actual vs target/possible | Inner bar = actual, outer bracket = possible | — |
| Choropleth | Geography | One metric per map; legend with 4 stops | Bubble + map combined |
| 2×2 matrix | Prioritisation | Quadrants labelled; ≤8 dots; non-overlapping labels | More than 10 dots |
| Ranked table | When the row identity (URL, keyword) IS the insight | Sparkbars in numeric cells; freeze first column | More than 12 rows |
| KPI tile | Top-level numbers | Number > label; delta arrow + % vs prior period | Sparklines inside tiles unless space allows |

---

## 7. Voice & copy rules

- **Slide titles**: declarative, not interrogative. *"They publish 21 wellness articles for 82 visits"* — not *"How is their wellness content performing?"*
- **Eyebrows** (mono caps above title): section label, e.g. `03 · BRAND READ`
- **Body copy**: max 3 sentences per paragraph; max 3 paragraphs per slide
- **Numbers**: always with unit (`/mo`, `kw`, `visits`, `pgs`). Abbreviate 1,200 → `1.2K`, 1,234,567 → `1.2M`.
- **Compliance language**: never claim a competitor is non-compliant unless we cite the breach. Use *"plays in the grey"* / *"safe"* per the `competitors.md` legend.
- **Tense**: present tense ("they rank for…"), not future or speculative.

---

## 8. Build pipeline (file layout)

```
.github/
  instructions/
    INSTRUCTIONS.md                    ← this file
    DATA_AUDIT.md
    DATA_PREPARATION.md
    DATA_PREPARATION_DATAFORSEO.md

competitors/
  _template/
    README.md                           ← short quick-start
    presentation/
      presentation.html                 ← 20-slide skeleton
      assets/                           ← logo + any per-deck images
    code/
      analyze.py                        ← CSVs → data.json + presentation/data.js
      audit.py                          ← pre-build data check
      build_offline.py                  ← single-file bundle
  <competitor-slug>/
    data/
      raw/                              ← raw SEO export CSVs
      screenshots/                      ← reference visuals (not embedded by default)
      notes.json                        ← hand-written qualitative notes
      data.json                         ← generated by analyze.py
    presentation/
      data.js                           ← generated (window.DATA = …)
      presentation.html                 ← copy of template, no edits needed
      presentation-offline.html
      assets/logo.png
    code/                              ← per-competitor scripts (analyze.py is customised)
```

**Rule:** never edit `presentation.html` per-competitor. All variation comes from `data.js` + `notes.json`. If a chart needs a new feature, add it to the template and re-render every competitor.

---

## 9. QA checklist (run before sharing)

- [ ] All 20 slides render without console errors (or fewer slides, with auto-hidden ones absent — never broken)
- [ ] Every chart has an inline insight callout
- [ ] No placeholder text (`TODO`, `Lorem`, `XXX`)
- [ ] Footer page numbers reflect actual slide count
- [ ] Offline file < 3 MB (sanity check: no screenshots leaked in)
- [ ] Deck reads coherently in B&W (print preview)
- [ ] Verdict slides cite specific evidence from earlier slides
- [ ] `notes.json` `position` matches `competitors.md` for that competitor
- [ ] **Zero mentions of SEMrush / Ahrefs / any vendor in the rendered deck**: `grep -i 'semrush\|ahrefs' presentation/presentation*.html` returns nothing
- [ ] Cover slide `Prepared by` reads **"Bright Data"**

---

## 10. Per-competitor workflow

```bash
# 1. scaffold
cp -r competitors/_template competitors/polln
cd competitors/polln

# 2. drop CSV exports
mv ~/Downloads/polln.com-organic.Positions-*.csv     data/raw/
mv ~/Downloads/polln.com-organic.PagesV3-*.csv       data/raw/
mv ~/Downloads/polln.com-backlinks_pages.csv         data/raw/
# optional:
mv ~/Downloads/polln.com-trends.csv                  data/raw/
mv ~/Downloads/polln.com-serp-features.csv           data/raw/

# 3. write qualitative notes
$EDITOR data/notes.json

# 4. build
python3 code/analyze.py
python3 code/build_offline.py

# 5. QA
open presentation/presentation.html
```

---

## 11. Open questions / decisions log

Track per-competitor decisions in `<competitor>/docs/decisions.md` so the next deck refresh can pick them up:

- Which competitor set to compare on slide 08 (SOV)
- Whether to override topic taxonomy for this competitor
- Any data anomalies (e.g. branded traffic spike from a viral campaign)

---

## 12. Versioning

The template version is recorded at the top of `presentation.html` as `<meta name="template-version" content="X.Y">`.
Bump on any structural change. Each competitor deck records the template version it was last built against, so we know when a refresh is due.
