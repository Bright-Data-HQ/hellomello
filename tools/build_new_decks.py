#!/usr/bin/env python3
"""
One-shot builder for the six new competitor decks
(easykind, acacia, dispensed, greencare, healingleaves, nuleaf).

For each slug:
  1. Enrich data/notes.json with the template fields the full deck expects
     (period, tagline, verdict_label, verdict_tone, eeat, gap_matrix,
     extra steal/avoid items where the original notes are too thin).
  2. Re-run code/analyze.py so data.js picks up the enriched notes.
  3. Clone competitors/alternaleaf/presentation/presentation.html into
     competitors/<slug>/presentation/presentation.html and replace
     every Alternaleaf-specific string with the right one for the slug.
  4. Run code/build_offline.py to produce presentation-offline.html.
  5. Copy the offline file into public/hellomello/competitors/<slug>/index.html.

Prose is bespoke per slug; numbers are pulled from data.js totals so the
hard-coded lede / footer counts stay truthful.
"""
import json, os, re, shutil, subprocess, sys, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP = os.path.join(ROOT, 'competitors')
PUB  = os.path.join(ROOT, 'public', 'hellomello', 'competitors')
REF  = os.path.join(COMP, 'alternaleaf', 'presentation', 'presentation.html')


# ---------------------------------------------------------------------------
# Per-slug spec
# ---------------------------------------------------------------------------
# Each entry contains:
#   brand          — display brand name on the cover
#   domain         — primary domain
#   meta2_label    — second cover-meta label (replaces "Parent")
#   meta2_value    — value for that label
#   period         — period eyebrow (top right of cover + slide 02)
#   tagline        — cover tagline
#   verdict_label  — verdict text on cover (e.g. "Model off this")
#   verdict_colour — CSS var for verdict word ("--moss-3" green / "--clay" amber)
#   end_tag        — slide 20 footer (END · X · v1)
#
#   slide_02_title          — "The size of the prize." replacement
#   slide_02_lede           — exec snapshot lede
#   slide_02_footprint      — digital-footprint panel small text
#   slide_02_compliance     — compliance panel small text
#
#   slide_03_title          — "A healthcare brand, not a dispensary."
#   slide_03_lede           — brand & UX read lede
#
#   slide_04_lede           — position-distribution lede (cite kw count)
#
#   slide_07_title          — intent mix title
#   slide_07_lede           — intent mix lede (cite brand %)
#   slide_07_read           — small "Read:" caption on right
#
#   slide_10_title          — content clusters title
#   slide_10_lede           — content clusters lede
#   slide_10_bullets        — list of <li>...</li> strings (4 items)
#
#   slide_11_eyebrow        — "X location keywords"
#   slide_11_title          — location strategy title
#   slide_11_lede           — location strategy lede
#   slide_11_play           — small "Hellomello play:" caption
#
#   slide_12_lede           — conditions & clinical lede
#   slide_12_footer         — "N = X CONDITIONS + Y CLINIC KEYWORDS"
#   slide_12_play           — small "Hellomello play:" caption
#
#   slide_13_title          — top pages title
#   slide_13_lede           — top pages lede
#
#   slide_14_fortress       — left small text under fortress table
#   slide_14_opportunity    — right small text under non-brand table
#
#   slide_17_title          — technical & E-E-A-T title
#   slide_17_lede           — technical & E-E-A-T lede
#
#   slide_18_lede           — what to steal lede
#   slide_19_lede           — what to avoid lede
#
#   slide_20_lede           — implications lede
#   slide_20_bottom         — bottom-line small text
#
#   eeat / gap_matrix       — enrichment objects merged into notes.json
#   extra_steal / extra_avoid — additional verdict items appended if notes
#                              don't have enough (slide 18 / 19 need >=2)

SPECS = {
    'easykind': {
        'brand': 'Easykind',
        'domain': 'easykind.com.au',
        'meta2_label': 'Type',
        'meta2_value': 'Telehealth clinic',
        'period': 'June 2026',
        'tagline': 'A brand-led, app-first clinic targeting a younger price-aware audience. Big on awareness, almost invisible in organic content.',
        'verdict_label': 'Model off this',
        'verdict_colour': '--moss-3',
        'end_tag': 'END · EASYKIND · v1',
        'slide_02_title': 'Brand demand, <em class="display italic">almost nothing else</em>.',
        'slide_02_lede': 'Six metrics, one read: this is a marketing-led, portal-first acquisition engine. 98% of organic traffic is people typing the brand name. The non-brand content surface is tiny and open to displace.',
        'slide_02_footprint': 'Three-property setup on paper: marketing site, app and patient portal subdomains. In practice only a handful of marketing pages rank, and the portal funnels brand demand into the product.',
        'slide_02_compliance': 'Sits a little in the grey. Pricing is upfront and the audience is younger and price-aware, but disclaimers are thin and consultation framing is light in places. Borrow the clarity, tighten the wording.',
        'slide_03_title': 'A consumer app, <em class="display italic">not</em> a content site.',
        'slide_03_lede': 'The visual and content system is built for sign-up and app onboarding, not for organic discovery. That is why brand demand carries the whole site and the content surface is almost empty.',
        'slide_04_lede': '182 ranking keywords across the domain — but 98% of the traffic sits on a handful of brand terms at position #1. The non-brand tail is small and shallow, which means there is barely any inventory to displace and every category term is open.',
        'slide_07_title': 'It is the brand. <em class="display italic">All of it</em>.',
        'slide_07_lede': 'Two cuts of the same question — by intent label and by brand vs non-brand. Both say the same thing: roughly 98% of organic traffic is people typing &ldquo;easykind&rdquo; or a misspelling. There is no real category footprint to defend.',
        'slide_07_read': '<b>Read:</b> 87% of keywords are non-brand but they yield under 2% of traffic. The brand fortress is doing all the work; the rest of the inventory is parked.',
        'slide_10_title': 'A few pages <em class="display italic">do the work</em>. The rest are noise.',
        'slide_10_lede': '9 ranking pages plotted on pages-published × traffic-earned. Almost everything sits in one cluster: the homepage and portal entry. There is no editorial layer to speak of and no clinical or condition hub.',
        'slide_10_bullets': [
            '<b>Star</b> · homepage + portal carry ~98% of traffic on a handful of URLs.',
            '<b>Empty</b> · no content hub, no clinical authority pages, no help centre.',
            '<b>Bloat</b> · none — the site is too small to be bloated.',
            '<b>Gap</b> · conditions, locations and education are entirely open.',
        ],
        'slide_11_eyebrow': 'Location keywords · thin coverage',
        'slide_11_title': 'No real <em class="display italic">geo</em> strategy.',
        'slide_11_lede': 'Easykind ranks for a handful of incidental location terms but has no programmatic suburb or city template. The geo surface is essentially empty — every metro and every &ldquo;near me&rdquo; query is undefended.',
        'slide_11_play': '<b>Hellomello play:</b> suburb-level pSEO across the top 5 metros plus a templated &ldquo;near me&rdquo; funnel. There is nothing to fight.',
        'slide_12_lede': 'A small set of condition and clinic keywords ranking, producing almost no traffic. The site is structurally too thin for clinical authority — there is no condition hub, no clinician bios, no review content. The category sits open.',
        'slide_12_footer': 'CONDITIONS + CLINIC SURFACE · NEAR ZERO',
        'slide_12_play': '<b>Hellomello play:</b> condition-led landing pages with real E-E-A-T (clinician bios, citations, dated reviews). Easykind has nothing here.',
        'slide_13_title': 'Homepage and portal <em class="display italic">are</em> the site.',
        'slide_13_lede': 'The homepage and the portal carry almost all of the traffic. Below them, the inventory is tiny and most pages earn nothing — there is no decaying long tail, just a missing one.',
        'slide_14_fortress': 'Brand spellings, login, portal. Defensive. Not contestable in months.',
        'slide_14_opportunity': 'Category and price terms — <i>medical cannabis</i>, <i>online medical cannabis australia</i>, <i>cbd pharmacies</i>. Contestable. Steal these first.',
        'slide_17_title': 'App polish is real. <em class="display italic">Content authority</em> is not.',
        'slide_17_lede': 'Their commercial pages convert but the wider site lacks the credibility signals patients look for: no clinician bylines, light schema, thin disclaimers. Hellomello can outrank by being more demonstrably expert on the same intent.',
        'slide_18_lede': 'Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. With Easykind there is no big play to copy — the wins are small clarity moves like pricing and portal onboarding, while the content category sits wide open for us.',
        'slide_19_lede': 'Where Easykind&rsquo;s strategy quietly costs them — almost no content surface, no clinical depth, thin disclaimers. The traps are about what is missing, not what is misplaced.',
        'slide_20_lede': 'Ten topics, scored 0–5 for Easykind&rsquo;s presence and Hellomello&rsquo;s current presence. The orange row is the gap we own — every row where Easykind scores 2 or less is an open field.',
        'slide_20_bottom': '<b>Bottom line.</b> Easykind wins on brand demand, not on content. Match their pricing clarity and out-publish them on conditions, locations and education. The category is open against them.',
        'eeat': {
            'https': 'green',
            'schema_medical': 'red',
            'author_bylines': 'red',
            'medical_reviewer': 'amber',
            'core_web_vitals': 'amber',
            'freshness': 'amber',
            'notes': 'App polish does not extend to the content surface. No clinician bylines or medical-page schema. Pricing is public and clear — the strongest commercial signal on the site.',
        },
        'gap_matrix': [
            {'topic': 'Brand defence',         'easykind': 5, 'hellomello': 1, 'comment': 'Their moat. Owned.'},
            {'topic': 'Pricing transparency',  'easykind': 4, 'hellomello': 1, 'comment': 'Match it on day one.'},
            {'topic': 'Clinic / doctor SEO',   'easykind': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Conditions content',    'easykind': 0, 'hellomello': 0, 'comment': 'Open field — highest impact.'},
            {'topic': 'Locations / pSEO',      'easykind': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': '"Near me" queries',     'easykind': 0, 'hellomello': 0, 'comment': 'Undefended.'},
            {'topic': 'Wellness / lifestyle',  'easykind': 0, 'hellomello': 0, 'comment': 'Skip.'},
            {'topic': 'Reviews / social proof','easykind': 2, 'hellomello': 0, 'comment': 'Replicate properly.'},
            {'topic': 'Editorial link bait',   'easykind': 0, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Help / support SEO',    'easykind': 0, 'hellomello': 0, 'comment': 'Open field.'},
        ],
        'extra_steal': [
            {'play': 'Tighter portal onboarding flow', 'effort': 3, 'impact': 3, 'note': 'Their portal sits very close to the brand search; we should mirror the funnel without copying the grey framing.'},
        ],
        'extra_avoid': [
            {'trap': 'Thin compliance disclaimers', 'evidence': 'Pricing and product framing run ahead of disclaimers in places. Borrow the clarity, never the grey edges.'},
            {'trap': 'Brand-only fortress', 'evidence': '98% of traffic comes from brand spellings. A single non-brand displacement weakens the whole strategy.'},
        ],
    },

    'acacia': {
        'brand': 'Acacia Clinic',
        'domain': 'acacia-medical.com',
        'meta2_label': 'Type',
        'meta2_value': 'Clinic + pharmacy access',
        'period': 'June 2026',
        'tagline': 'A small, compliant clinic with a tiny but loyal brand footprint. Almost no non-brand search surface — every category topic is white space against them.',
        'verdict_label': 'Model off this',
        'verdict_colour': '--moss-3',
        'end_tag': 'END · ACACIA · v1',
        'slide_02_title': 'A <em class="display italic">trustworthy</em> sliver of a footprint.',
        'slide_02_lede': 'Six metrics, one read: this is a brand-fortress with effectively no content engine. 96% of organic traffic is brand demand; the site itself is four pages deep. Safe to copy the tone, plenty of room to out-publish.',
        'slide_02_footprint': 'A single domain. Home, pharmacies and compassionate-access pages do the heavy lifting. No app subdomain in the index, no separate help centre, no editorial layer.',
        'slide_02_compliance': 'Conservative and consultation-led. Compassionate-access pages are partner focused rather than product pushy. Light on disclaimers but nothing high risk. A safe reference point on tone.',
        'slide_03_title': 'A healthcare brand, <em class="display italic">not</em> a dispensary.',
        'slide_03_lede': 'The visual and content system signals clinic and pharmacy access, not a shop. That positioning is what lets them defend brand search and keeps copy compliant — there just is not very much of it.',
        'slide_04_lede': '141 ranking keywords across the domain — and almost all of the traffic sits on the brand terms at position #1. The non-brand tail is short and shallow, which means there is barely any inventory to displace and the whole category is open for us.',
        'slide_07_title': 'Brand. <em class="display italic">Almost all of it</em>.',
        'slide_07_lede': 'Two cuts of the same question. The answer is the same: 96% of organic traffic is people typing &ldquo;acacia&rdquo; or a misspelling. The non-brand category sliver is tiny — and it is the only place a category competitor can fight.',
        'slide_07_read': '<b>Read:</b> 73% of keywords are non-brand but they yield ~4% of traffic. The brand fortress is doing all the work; the rest of the inventory is parked.',
        'slide_10_title': 'Four pages <em class="display italic">are</em> the site.',
        'slide_10_lede': 'Just 4 ranking pages plotted on pages-published × traffic-earned. The homepage carries most of the load; the pharmacy and compassionate-access pages add a thin layer of trust signal but very little organic surface.',
        'slide_10_bullets': [
            '<b>Star</b> · homepage carries the brand demand.',
            '<b>Trust</b> · pharmacy partner pages add credibility.',
            '<b>Empty</b> · no condition hub, no education, no programmatic surface.',
            '<b>Gap</b> · the whole category sits open.',
        ],
        'slide_11_eyebrow': 'Location keywords · incidental',
        'slide_11_title': 'No real <em class="display italic">geo</em> footprint.',
        'slide_11_lede': 'Acacia ranks for a small set of location terms — mostly through pharmacy partner pages — but has no programmatic location strategy. Capital cities, suburbs and &ldquo;near me&rdquo; queries are all undefended.',
        'slide_11_play': '<b>Hellomello play:</b> suburb-level pSEO across the top 5 metros plus a templated &ldquo;near me&rdquo; funnel. There is nothing to fight.',
        'slide_12_lede': 'A handful of condition and clinic keywords ranking, producing single-digit visits. There is no condition hub and no clinician authorship — the safety of their positioning is paid for with structural thinness.',
        'slide_12_footer': 'CONDITIONS + CLINIC SURFACE · MINIMAL',
        'slide_12_play': '<b>Hellomello play:</b> condition-led landing pages with real E-E-A-T (clinician bios, citations, dated reviews). Acacia is not contesting this space.',
        'slide_13_title': 'One page <em class="display italic">prints</em>. The rest are trust.',
        'slide_13_lede': 'The homepage carries the brand demand; the pharmacy and compassionate-access pages are credibility, not traffic. There is no decaying long tail because there is no long tail to decay.',
        'slide_14_fortress': 'Brand spellings, partner pharmacies, compassionate access. Defensive. Not contestable in months.',
        'slide_14_opportunity': 'Category and partner-pharmacy terms. Contestable. The category itself sits open.',
        'slide_17_title': 'Compliance is <em class="display italic">solid</em>. Surface is the gap.',
        'slide_17_lede': 'Commercial pages are clean and consultation-led. The weakness is structural: nothing for crawlers or patients to find beyond the homepage. Hellomello can match the tone and out-publish on the same audience.',
        'slide_18_lede': 'Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. With Acacia the play is to borrow their compliance posture and partner-pharmacy idea, then build the content engine they never bothered with.',
        'slide_19_lede': 'Where Acacia&rsquo;s strategy quietly costs them — near-zero content, no clinical hub, no location surface. The trap is choosing safety over visibility.',
        'slide_20_lede': 'Ten topics, scored 0–5 for Acacia&rsquo;s presence and Hellomello&rsquo;s current presence. The orange row is the gap we own — every row where Acacia scores 2 or less is an open field.',
        'slide_20_bottom': '<b>Bottom line.</b> Acacia is a safe brand fortress with no search content. Borrow the tone, borrow the pharmacy idea, then publish the conditions, locations and education content they have never written.',
        'eeat': {
            'https': 'green',
            'schema_medical': 'amber',
            'author_bylines': 'red',
            'medical_reviewer': 'amber',
            'core_web_vitals': 'amber',
            'freshness': 'red',
            'notes': 'Clinical posture is sound but credibility signals are largely visual. No clinician bylines, no medical-page schema, freshness lags. The safe positioning is real, the visibility is thin.',
        },
        'gap_matrix': [
            {'topic': 'Brand defence',         'acacia': 4, 'hellomello': 1, 'comment': 'Owned.'},
            {'topic': 'Pricing transparency',  'acacia': 2, 'hellomello': 1, 'comment': 'Worth matching.'},
            {'topic': 'Clinic / doctor SEO',   'acacia': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Conditions content',    'acacia': 0, 'hellomello': 0, 'comment': 'Open field — highest impact.'},
            {'topic': 'Locations / pSEO',      'acacia': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': '"Near me" queries',     'acacia': 0, 'hellomello': 0, 'comment': 'Undefended.'},
            {'topic': 'Wellness / lifestyle',  'acacia': 0, 'hellomello': 0, 'comment': 'Skip.'},
            {'topic': 'Reviews / social proof','acacia': 1, 'hellomello': 0, 'comment': 'Replicate properly.'},
            {'topic': 'Editorial link bait',   'acacia': 0, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Pharmacy partners',     'acacia': 3, 'hellomello': 0, 'comment': 'Borrow the model.'},
        ],
        'extra_steal': [
            {'play': 'Conservative consultation tone',   'effort': 1, 'impact': 3, 'note': 'A safe reference point for compliance language and product framing.'},
            {'play': 'Compassionate-access framing',     'effort': 2, 'impact': 2, 'note': 'Partner-focused page that adds credibility without pushing product.'},
        ],
        'extra_avoid': [
            {'trap': 'Safety over visibility', 'evidence': 'Four ranking pages and a footprint that depends entirely on brand demand. Compliance must not become invisibility.'},
        ],
    },

    'dispensed': {
        'brand': 'Dispensed',
        'domain': 'dispensed.com.au',
        'meta2_label': 'Type',
        'meta2_value': 'Telehealth clinic',
        'period': 'June 2026',
        'tagline': 'A big-brand telehealth player riding awareness, not content. Real location coverage on the five majors and a leaky dev / qa surface that needs tightening.',
        'verdict_label': 'Careful · model with edits',
        'verdict_colour': '--clay',
        'end_tag': 'END · DISPENSED · v1',
        'slide_02_title': 'Big brand. <em class="display italic">Thin</em> engine.',
        'slide_02_lede': 'Six metrics, one read: this is a brand-led acquisition engine with a shallow location surface bolted on. 92% of traffic is brand demand; the rest is a five-city template and a small blog. Easy to displace beneath the brand line.',
        'slide_02_footprint': 'Marketing site plus a large app / portal subdomain for patients. Real location pages for Melbourne, Sydney, Brisbane, Perth and the Gold Coast. Small blog and a few info pages. Dev and qa subdomains leak into the index.',
        'slide_02_compliance': 'Sits in the grey. Free-consultation and pricing language is prominent and the framing leans product over consultation in places. Borrow the location idea, tighten the wording before copying anything.',
        'slide_03_title': 'A telehealth brand, <em class="display italic">not</em> a content site.',
        'slide_03_lede': 'The visual and content system is conversion-first: reviews and login pushed hard, free-consult banners above the fold. The brand carries the weight; the rest of the site is functional rather than authoritative.',
        'slide_04_lede': '236 ranking keywords across the domain — yet ~92% of traffic comes from brand terms at position #1. There is a meaningful tail of non-brand location and category keywords below page 1 that produce almost nothing. That tail is the inventory we displace first.',
        'slide_07_title': 'Brand is <em class="display italic">most</em> of it.',
        'slide_07_lede': 'Two cuts of the same question. The answer is consistent: roughly 92% of organic traffic is people typing &ldquo;dispensed&rdquo; or a misspelling. The non-brand category and location sliver is where any competitor has to fight.',
        'slide_07_read': '<b>Read:</b> 92% of keywords are non-brand but they yield only ~8% of traffic. The brand carries the site; the rest of the inventory is parked.',
        'slide_10_title': 'A small location set <em class="display italic">does the work</em>. The rest is brand and dev.',
        'slide_10_lede': '14 ranking pages plotted on pages-published × traffic-earned. The homepage and portal carry most of the traffic; the city template adds a thin geo layer. Dev and qa subdomains rank where they should not — a hygiene problem more than a strategy.',
        'slide_10_bullets': [
            '<b>Star</b> · homepage + portal carry the brand demand.',
            '<b>Workhorse</b> · five city pages (Melbourne, Sydney, Brisbane, Perth, Gold Coast).',
            '<b>Bloat</b> · small blog earning very few clicks.',
            '<b>Leak</b> · dev / qa subdomains rank and dilute trust.',
        ],
        'slide_11_eyebrow': 'Location keywords · five cities',
        'slide_11_title': 'Five cities deep. <em class="display italic">Silent</em> on suburbs.',
        'slide_11_lede': 'Dispensed ranks for a real but shallow set of location terms — capital-city pages only, no suburb depth, no &ldquo;near me&rdquo; templates. They have planted the flag but not built the surface beneath it.',
        'slide_11_play': '<b>Hellomello play:</b> suburb-level pSEO inside their five metros plus a properly templated &ldquo;near me&rdquo; funnel. Catchable in a quarter on most cities.',
        'slide_12_lede': 'A modest set of clinic and condition keywords ranking, producing two-figure visits. There is no condition hub and no clinician authorship — the credibility signals patients look for are missing.',
        'slide_12_footer': 'CONDITIONS + CLINIC SURFACE · SHALLOW',
        'slide_12_play': '<b>Hellomello play:</b> condition-led landing pages with real E-E-A-T (clinician bios, citations, dated reviews). Dispensed has nothing to defend the category with.',
        'slide_13_title': 'A few pages <em class="display italic">print money</em>. Dev / qa leaks the rest.',
        'slide_13_lede': 'Homepage, portal and the five city pages carry the site. Beneath them, a long tail of dev and qa URLs ranking where they should not — a tidy-up problem as much as a content one.',
        'slide_14_fortress': 'Brand spellings, login, portal. Defensive. Not contestable in months.',
        'slide_14_opportunity': 'City and category terms — <i>medical cannabis melbourne</i>, <i>dispensed australia</i>, <i>cbd pharmacies</i>. Contestable. We out-rank by depth and clinician signal.',
        'slide_17_title': 'Brand polish is real. <em class="display italic">Hygiene</em> is the weak seam.',
        'slide_17_lede': 'Commercial pages are conversion-tuned but grey in places; dev / qa subdomains leak into the index; clinician bylines and medical-page schema are missing. Hellomello can outrank by being tidier and more demonstrably expert.',
        'slide_18_lede': 'Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. With Dispensed the wins are borrowable — city pages, visible reviews — but the compliance tone needs editing on the way in.',
        'slide_19_lede': 'Where Dispensed&rsquo;s strategy quietly costs them — grey framing, leaky subdomains, shallow geo depth. The traps are about hygiene as much as content.',
        'slide_20_lede': 'Ten topics, scored 0–5 for Dispensed&rsquo;s presence and Hellomello&rsquo;s current presence. The orange row is the gap we own — every row where Dispensed scores 2 or less is a contested or open field.',
        'slide_20_bottom': '<b>Bottom line.</b> Dispensed proved the city-page idea works at brand scale. Tighten the language, deepen the geo template to suburb level, and out-author the clinical content they never wrote.',
        'eeat': {
            'https': 'green',
            'schema_medical': 'red',
            'author_bylines': 'red',
            'medical_reviewer': 'amber',
            'core_web_vitals': 'amber',
            'freshness': 'amber',
            'notes': 'Strong brand signal, weak hygiene. Dev and qa subdomains rank publicly, schema is shallow, clinician bylines are missing. Compliance framing leans product in places.',
        },
        'gap_matrix': [
            {'topic': 'Brand defence',         'dispensed': 5, 'hellomello': 1, 'comment': 'Their moat.'},
            {'topic': 'Pricing transparency',  'dispensed': 3, 'hellomello': 1, 'comment': 'Match it cleanly.'},
            {'topic': 'Clinic / doctor SEO',   'dispensed': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Conditions content',    'dispensed': 0, 'hellomello': 0, 'comment': 'Open field — highest impact.'},
            {'topic': 'Locations / pSEO',      'dispensed': 3, 'hellomello': 0, 'comment': 'Capital cities only — go suburb-deep.'},
            {'topic': '"Near me" queries',     'dispensed': 1, 'hellomello': 0, 'comment': 'Undefended.'},
            {'topic': 'Wellness / lifestyle',  'dispensed': 0, 'hellomello': 0, 'comment': 'Skip.'},
            {'topic': 'Reviews / social proof','dispensed': 3, 'hellomello': 0, 'comment': 'Replicate properly.'},
            {'topic': 'Editorial link bait',   'dispensed': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Site hygiene',          'dispensed': 1, 'hellomello': 2, 'comment': 'Their leak — our edge.'},
        ],
        'extra_steal': [
            {'play': 'Suburb-deep location template', 'effort': 3, 'impact': 4, 'note': 'Their five-city model proves the geo plays. Going deeper is unconfested.'},
        ],
        'extra_avoid': [
            {'trap': 'Grey consultation framing', 'evidence': 'Product-led language sits in front of consultation framing on several pages. Higher CTR, higher regulator risk.'},
            {'trap': 'Brand-only fortress', 'evidence': '92% of traffic is brand. The non-brand surface is small and easy to displace beneath the brand line.'},
        ],
    },

    'greencare': {
        'brand': 'Greencare',
        'domain': 'greencare.com.au',
        'meta2_label': 'Type',
        'meta2_value': 'Clinic + Folium dispensary',
        'period': 'June 2026',
        'tagline': 'A wellness-led clinic with a Folium dispensary and a long lifestyle blog. Publishes broadly, earns from very few pages — the blog is bloat and the cannabis intent sits underweighted.',
        'verdict_label': 'Model off this',
        'verdict_colour': '--moss-3',
        'end_tag': 'END · GREENCARE · v1',
        'slide_02_title': 'A wide blog, <em class="display italic">narrow</em> wins.',
        'slide_02_lede': 'Six metrics, one read: this is a wellness blog with a clinic attached. About half the traffic is brand, the other half is wellness rather than cannabis. Plenty of pages, very little organic return — and the cannabis intent sits underweighted.',
        'slide_02_footprint': 'A single domain with a /pages/ commercial set (Folium dispensary, treatments, practitioners) and a large wellness blog covering yoga, ice baths, hair loss and burnout. No portal, no subdomains — everything sits on the main site.',
        'slide_02_compliance': 'Generally safe. Cannabis is kept at arm&rsquo;s length from the blog and the commercial pages stay consultation-led. The blog is broad enough to read as a lifestyle publisher rather than a clinic — useful cover, weak focus.',
        'slide_03_title': 'A wellness blog <em class="display italic">with</em> a clinic.',
        'slide_03_lede': 'The visual and content system is soft, calming and editorial. That positioning keeps compliance low risk but means the cannabis intent — which is the only intent that actually converts — sits buried under yoga and burnout articles.',
        'slide_04_lede': '242 ranking keywords across the domain — but only ~52% of the traffic is brand and the rest is split across a wide wellness blog. Almost everything sits below #10, which means most of the inventory is dormant page-2-or-worse rankings.',
        'slide_07_title': 'About half brand. The rest is <em class="display italic">wellness</em>, not cannabis.',
        'slide_07_lede': 'Two cuts of the same question. The brand share is unusually low for this category — ~52% — because the wellness blog mops up informational queries that have nothing to do with cannabis. The category intent that matters is small.',
        'slide_07_read': '<b>Read:</b> 98% of keywords are non-brand but they yield only ~49% of traffic. Most of that non-brand traffic is wellness, not cannabis intent.',
        'slide_10_title': 'Their <em class="display italic">/pages/</em> earns. Their <em class="display italic">/blog/</em> is bloat.',
        'slide_10_lede': '27 ranking pages plotted on pages-published × traffic-earned. The Folium dispensary and treatment pages do the commercial work; the wellness blog publishes volume that ranks nowhere meaningful.',
        'slide_10_bullets': [
            '<b>Star</b> · Folium dispensary + treatments pages carry the cannabis intent.',
            '<b>Bloat</b> · wellness blog — yoga, ice baths, hair loss, burnout — ranking but not winning.',
            '<b>Trust</b> · practitioner and health-summary pages add credibility.',
            '<b>Gap</b> · no programmatic location surface, no clinical condition hub.',
        ],
        'slide_11_eyebrow': 'Location keywords · thin coverage',
        'slide_11_title': 'No real <em class="display italic">geo</em> strategy.',
        'slide_11_lede': 'Greencare ranks for a small set of location-tagged terms but has no programmatic city or suburb template. Capital cities and &ldquo;near me&rdquo; queries are undefended — the geo surface they could own sits empty.',
        'slide_11_play': '<b>Hellomello play:</b> suburb-level pSEO across the top 5 metros plus a templated &ldquo;near me&rdquo; funnel. There is nothing to fight.',
        'slide_12_lede': 'A modest set of clinic and condition keywords ranking, producing two-figure visits. The condition surface is shallow and the practitioner pages stop short of authored clinical content. The category sits half-published.',
        'slide_12_footer': 'CONDITIONS + CLINIC SURFACE · SHALLOW',
        'slide_12_play': '<b>Hellomello play:</b> condition-led landing pages with real E-E-A-T (clinician bios, citations, dated reviews). Greencare has the practitioners but not the content.',
        'slide_13_title': 'A few pages <em class="display italic">print</em>. Most are decay.',
        'slide_13_lede': 'The Folium dispensary, treatments and a couple of brand pages carry most of the traffic. Below them, a long blog tail of wellness articles ranking but not earning. The inventory of decay is unusually large here.',
        'slide_14_fortress': 'Brand spellings, Folium dispensary, treatments. Defensive on brand, soft on category.',
        'slide_14_opportunity': 'Wellness and category crossovers — <i>inner calmness</i>, <i>wellness routines</i>. Useful intent, but cannabis category terms are the real prize.',
        'slide_17_title': 'Soft framing. <em class="display italic">Weak</em> clinical depth.',
        'slide_17_lede': 'The wellness positioning keeps the site safe but soft — practitioner pages stop short of authored clinical content, schema is shallow, freshness is mixed. Hellomello can outrank by tightening focus and writing the clinical content they avoid.',
        'slide_18_lede': 'Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. With Greencare the lesson is what not to copy: the broad wellness blog. Borrow the practitioner page idea, focus the rest on cannabis intent.',
        'slide_19_lede': 'Where Greencare&rsquo;s strategy quietly costs them — a wellness blog that earns nothing, a thin condition surface, no geo template. The traps are about focus, not safety.',
        'slide_20_lede': 'Ten topics, scored 0–5 for Greencare&rsquo;s presence and Hellomello&rsquo;s current presence. The orange row is the gap we own — every row where Greencare scores 2 or less is a contested or open field.',
        'slide_20_bottom': '<b>Bottom line.</b> Greencare published the volume without the focus. Borrow the practitioner credibility model, skip the wellness blog, and own the cannabis intent they leave open.',
        'eeat': {
            'https': 'green',
            'schema_medical': 'amber',
            'author_bylines': 'amber',
            'medical_reviewer': 'amber',
            'core_web_vitals': 'amber',
            'freshness': 'amber',
            'notes': 'Practitioner pages signal credibility but the clinical content layer is thin. Wellness positioning keeps risk low at the cost of focus. Schema and authorship signals lag the bigger players.',
        },
        'gap_matrix': [
            {'topic': 'Brand defence',          'greencare': 2, 'hellomello': 1, 'comment': 'Small brand — fight here too.'},
            {'topic': 'Pricing transparency',   'greencare': 2, 'hellomello': 1, 'comment': 'Match cleanly.'},
            {'topic': 'Clinic / doctor SEO',    'greencare': 2, 'hellomello': 0, 'comment': 'Practitioner pages — contestable.'},
            {'topic': 'Conditions content',     'greencare': 1, 'hellomello': 0, 'comment': 'Open field — highest impact.'},
            {'topic': 'Locations / pSEO',       'greencare': 1, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': '"Near me" queries',      'greencare': 0, 'hellomello': 0, 'comment': 'Undefended.'},
            {'topic': 'Wellness / lifestyle',   'greencare': 4, 'hellomello': 0, 'comment': 'Their bloat — skip.'},
            {'topic': 'Reviews / social proof', 'greencare': 1, 'hellomello': 0, 'comment': 'Replicate properly.'},
            {'topic': 'Editorial link bait',    'greencare': 2, 'hellomello': 0, 'comment': 'Cannabis explainers, not wellness.'},
            {'topic': 'Dispensary integration', 'greencare': 3, 'hellomello': 0, 'comment': 'Folium model worth studying.'},
        ],
        'extra_steal': [
            {'play': 'Practitioner credibility pages', 'effort': 3, 'impact': 3, 'note': 'Clinician profile pages with credentials, used as authorship anchors for condition content.'},
            {'play': 'Eligibility explainer template', 'effort': 2, 'impact': 3, 'note': 'Their health-summary content captures useful pre-consult search intent.'},
        ],
        'extra_avoid': [
            {'trap': 'Broad wellness blogging', 'evidence': 'Most of the 27 pages are off-topic wellness articles producing single-digit visits. Publishing volume without focus is a tax.'},
        ],
    },

    'healingleaves': {
        'brand': 'Healing Leaves',
        'domain': 'healingleaves.com.au',
        'meta2_label': 'Type',
        'meta2_value': 'Telehealth clinic',
        'period': 'June 2026',
        'tagline': 'A switcher-focused clinic with programmatic region pages and aggressive comparison content. The model works for reach; the framing is grey and needs cleaning before we borrow it.',
        'verdict_label': 'Careful · don\'t copy',
        'verdict_colour': '--clay',
        'end_tag': 'END · HEALINGLEAVES · v1',
        'slide_02_title': 'Reach through <em class="display italic">comparison</em> and region pages.',
        'slide_02_lede': 'Six metrics, one read: this is a switcher-targeted clinic using programmatic region pages and versus-competitor content to chase non-brand intent. About half the traffic is brand; the rest is geo and comparison reach. Effective, grey at the edges.',
        'slide_02_footprint': 'A single domain with programmatic state and regional telehealth pages, a set of versus-competitor pages (vs Easykind, vs Polln, vs Dispensed) and supporting education and FAQ sections. No separate portal subdomain.',
        'slide_02_compliance': 'Sits in the grey. Comparison framing is aggressive, switcher and price talk runs ahead of safer clinics, and external links into TGA-style content are positioned commercially. Useful patterns, hazardous wording — do not copy verbatim.',
        'slide_03_title': 'A <em class="display italic">switcher</em> story, not a clinic story.',
        'slide_03_lede': 'The visual and content system pitches Healing Leaves directly against named rivals. That positioning earns brand-versus searches and regional reach — and it walks straight up to the TGA line on terminology and claims.',
        'slide_04_lede': '176 ranking keywords across the domain — only ~54% of traffic is brand, the rest is regional and competitor-comparison terms. There is a real non-brand surface here, much of it sitting on page 2 and ripe to displace with cleaner content.',
        'slide_07_title': 'Brand is <em class="display italic">half</em> of it.',
        'slide_07_lede': 'Two cuts of the same question. The brand share is low for this category — ~54% — because the comparison and regional pages mop up non-brand intent. They are competing in the open category, not behind a brand moat.',
        'slide_07_read': '<b>Read:</b> 97% of keywords are non-brand and they earn ~46% of traffic. Region pages and versus content are doing real work — and competing with us directly.',
        'slide_10_title': 'Regions and <em class="display italic">versus</em> pages do the work.',
        'slide_10_lede': '27 ranking pages plotted on pages-published × traffic-earned. The regional telehealth pages carry geo traffic; the versus pages capture brand-comparison searches; the homepage handles brand demand. Compact, focused — and grey in places.',
        'slide_10_bullets': [
            '<b>Star</b> · regional telehealth pages — programmatic local reach across states and regions.',
            '<b>Workhorse</b> · versus-competitor pages — vs Easykind, vs Polln, vs Dispensed.',
            '<b>Brand</b> · homepage carries brand and navigational queries.',
            '<b>Grey</b> · TGA-style external links and comparison claims sit close to the line.',
        ],
        'slide_11_eyebrow': 'Location keywords · programmatic',
        'slide_11_title': 'Regional-first. <em class="display italic">Programmatic</em>. Grey at the edges.',
        'slide_11_lede': 'Healing Leaves ranks for a real set of location terms — region and state pages, with thin capital-city coverage. The model works; the framing pushes against safer clinics&rsquo; language and against TGA expectations.',
        'slide_11_play': '<b>Hellomello play:</b> mirror the regional template at suburb depth, cleanly. Their best region page is catchable in a quarter without copying the grey wording.',
        'slide_12_lede': 'A real condition and clinic-comparison surface ranking but earning modestly. The credibility signals patients trust (clinician credentials, real review process, dated authorship) are not what is being optimised — they are being out-flanked by aggressive framing.',
        'slide_12_footer': 'CONDITIONS + CLINIC SURFACE · CONTESTED',
        'slide_12_play': '<b>Hellomello play:</b> condition-led landing pages with real E-E-A-T. Healing Leaves is competing on framing; we win by being more demonstrably expert.',
        'slide_13_title': 'Regions <em class="display italic">print</em>. Versus pages amplify.',
        'slide_13_lede': 'The homepage, the top region pages and the versus-competitor pages carry the site. Below them, a long tail of region permutations with thin traffic. The inventory works, but a chunk of it sits in the grey.',
        'slide_14_fortress': 'Brand spellings plus versus-competitor terms. The brand moat is small; the comparison moat is the real defence.',
        'slide_14_opportunity': 'Region and category terms — <i>medical cannabis [state]</i>, <i>telehealth cannabis [region]</i>. Contestable. We out-rank with deeper, compliant content.',
        'slide_17_title': 'Compliance is <em class="display italic">weak</em>. Comparison is the moat.',
        'slide_17_lede': 'Grey terminology, comparison claims that risk sharpening, external TGA-style links framed commercially. The model earns traffic but exposes them on regulatory review. Hellomello can take the same intent without the risk.',
        'slide_18_lede': 'Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. With Healing Leaves the model is borrowable — regional templates and comparison content — but the language must be rebuilt cleanly before any of it ships.',
        'slide_19_lede': 'Where Healing Leaves&rsquo; strategy quietly costs them — grey claims, aggressive framing, external links into restricted content. Effective today, fragile under regulator scrutiny.',
        'slide_20_lede': 'Ten topics, scored 0–5 for Healing Leaves&rsquo; presence and Hellomello&rsquo;s current presence. The orange row is the gap we own — every row where Healing Leaves scores 2 or less is a contested or open field.',
        'slide_20_bottom': '<b>Bottom line.</b> Healing Leaves proved the regional + comparison playbook moves real traffic. Take the structure, leave the grey framing, and own the same intent cleanly.',
        'eeat': {
            'https': 'green',
            'schema_medical': 'red',
            'author_bylines': 'red',
            'medical_reviewer': 'red',
            'core_web_vitals': 'amber',
            'freshness': 'amber',
            'notes': 'Grey terminology, comparison claims and TGA-style external links framed commercially. Schema and clinician bylines are missing. Effective for reach, fragile on regulatory review.',
        },
        'gap_matrix': [
            {'topic': 'Brand defence',          'healingleaves': 2, 'hellomello': 1, 'comment': 'Small brand moat.'},
            {'topic': 'Pricing transparency',   'healingleaves': 3, 'hellomello': 1, 'comment': 'Match it cleanly.'},
            {'topic': 'Clinic / doctor SEO',    'healingleaves': 2, 'hellomello': 0, 'comment': 'Contested.'},
            {'topic': 'Conditions content',     'healingleaves': 1, 'hellomello': 0, 'comment': 'Open field — highest impact.'},
            {'topic': 'Locations / pSEO',       'healingleaves': 3, 'hellomello': 0, 'comment': 'Region template works.'},
            {'topic': '"Near me" queries',      'healingleaves': 1, 'hellomello': 0, 'comment': 'Open.'},
            {'topic': 'Wellness / lifestyle',   'healingleaves': 0, 'hellomello': 0, 'comment': 'Skip.'},
            {'topic': 'Reviews / social proof', 'healingleaves': 1, 'hellomello': 0, 'comment': 'Replicate properly.'},
            {'topic': 'Versus / comparison',    'healingleaves': 3, 'hellomello': 0, 'comment': 'Borrow cleanly.'},
            {'topic': 'Compliance posture',     'healingleaves': 1, 'hellomello': 3, 'comment': 'Their risk — our edge.'},
        ],
        'extra_steal': [
            {'play': 'Suburb-deep region template', 'effort': 3, 'impact': 4, 'note': 'Their regional model proves the demand. We can go deeper without the grey wording.'},
        ],
        'extra_avoid': [
            {'trap': 'External TGA-style links framed commercially', 'evidence': 'Linking users to TGA-style content from commercial pages reads as advertising of restricted goods.'},
            {'trap': 'Aggressive comparison claims',                 'evidence': 'Versus pages risk crossing the line if claims sharpen. Comparison intent is winnable without it.'},
        ],
    },

    'nuleaf': {
        'brand': 'Nuleaf Clinics',
        'domain': 'nuleafclinics.com.au',
        'meta2_label': 'Type',
        'meta2_value': 'Early-stage clinic',
        'period': 'June 2026',
        'tagline': 'An early-stage clinic with almost no organic surface. Two ranking pages, twenty-one keywords, and some crossover with the Cannihelp brand. Nothing to copy yet — everything is white space.',
        'verdict_label': 'Watch · too thin',
        'verdict_colour': '--clay',
        'end_tag': 'END · NULEAF · v1',
        'slide_02_title': 'Barely <em class="display italic">there</em> in search.',
        'slide_02_lede': 'Six metrics, one read: this is an early-stage clinic with almost no organic footprint. Two ranking pages, twenty-one keywords, ~96% of it brand demand. Useful only as a watching brief.',
        'slide_02_footprint': 'Essentially a homepage plus one explainer page on the main domain. No portal subdomain, no programmatic surface, some crossover with the Cannihelp brand which sits adjacent in the data.',
        'slide_02_compliance': 'Too little content to read a clear posture. Consultation framing where present, no obvious grey edges. Worth re-auditing if and when the footprint grows.',
        'slide_03_title': 'A site that <em class="display italic">barely</em> exists.',
        'slide_03_lede': 'The visual and content system is conventional clinic — brand mark, consultation framing, a single explainer. Without a real content surface there is nothing to read more deeply from.',
        'slide_04_lede': '21 ranking keywords across the domain — almost all brand and Cannihelp crossover at position #1 or #2. There is no real distribution to analyse and no tail to displace. The category itself is the opportunity.',
        'slide_07_title': 'Brand. <em class="display italic">There is nothing else</em>.',
        'slide_07_lede': 'Two cuts of the same question. Both say the same thing: ~96% of organic traffic is brand and Cannihelp crossover. There is no non-brand category surface to read from.',
        'slide_07_read': '<b>Read:</b> the non-brand surface is too small to draw meaningful conclusions from. There is nothing to fight here — the whole category is open.',
        'slide_10_title': 'Two pages. <em class="display italic">No</em> strategy.',
        'slide_10_lede': '2 ranking pages plotted on pages-published × traffic-earned. The homepage carries the brand demand; the one explainer adds a token informational signal. There is no cluster to study.',
        'slide_10_bullets': [
            '<b>Star</b> · homepage carries the brand demand and Cannihelp crossover.',
            '<b>Token</b> · one explainer page is the entire content surface.',
            '<b>Empty</b> · no conditions, no locations, no clinical authority pages.',
            '<b>Gap</b> · the whole category sits open against them.',
        ],
        'slide_11_eyebrow': 'Location keywords · none of note',
        'slide_11_title': 'No <em class="display italic">geo</em> footprint at all.',
        'slide_11_lede': 'Nuleaf does not rank for any meaningful set of location terms. There is no programmatic surface, no city or suburb template, no &ldquo;near me&rdquo; coverage. The geo opportunity is uncontested.',
        'slide_11_play': '<b>Hellomello play:</b> suburb-level pSEO across the top 5 metros plus a templated &ldquo;near me&rdquo; funnel. There is nothing to fight.',
        'slide_12_lede': 'Barely any condition or clinic surface to speak of. A handful of keywords ranking at single-digit traffic. The credibility signals patients look for — clinician bios, dated reviews, authored content — are missing because there is almost nothing on the site.',
        'slide_12_footer': 'CONDITIONS + CLINIC SURFACE · NEAR ZERO',
        'slide_12_play': '<b>Hellomello play:</b> condition-led landing pages with real E-E-A-T. Nothing on Nuleaf&rsquo;s side to contest the space.',
        'slide_13_title': 'The homepage <em class="display italic">is</em> the site.',
        'slide_13_lede': 'The homepage carries everything. There is no second page printing money, no decaying long tail. The inventory is missing rather than declining.',
        'slide_14_fortress': 'Brand spellings and Cannihelp crossover. Tiny and defensive.',
        'slide_14_opportunity': 'The non-brand surface is too small to map. Treat the whole category as open.',
        'slide_17_title': 'No surface, <em class="display italic">no signal</em>.',
        'slide_17_lede': 'With almost no content there is little to assess. HTTPS is in place; everything else is essentially absent. Hellomello can take any topic in any city without contention.',
        'slide_18_lede': 'Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. With Nuleaf there is nothing to copy yet. The play is to move into every gap they have not filled.',
        'slide_19_lede': 'Where Nuleaf&rsquo;s strategy quietly costs them — there is no strategy yet. The trap is to dismiss small brands and miss them when they start to scale.',
        'slide_20_lede': 'Ten topics, scored 0–5 for Nuleaf&rsquo;s presence and Hellomello&rsquo;s current presence. The orange row is the gap we own — almost every row is open.',
        'slide_20_bottom': '<b>Bottom line.</b> Nuleaf has almost no organic presence. Nothing to copy, everything to take. Monitor in case the footprint grows.',
        'eeat': {
            'https': 'green',
            'schema_medical': 'red',
            'author_bylines': 'red',
            'medical_reviewer': 'red',
            'core_web_vitals': 'amber',
            'freshness': 'red',
            'notes': 'Too little content to assess meaningfully. HTTPS in place, everything else missing. Worth re-auditing in six months if the site grows.',
        },
        'gap_matrix': [
            {'topic': 'Brand defence',          'nuleaf': 2, 'hellomello': 1, 'comment': 'Small brand only.'},
            {'topic': 'Pricing transparency',   'nuleaf': 1, 'hellomello': 1, 'comment': 'Open.'},
            {'topic': 'Clinic / doctor SEO',    'nuleaf': 0, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': 'Conditions content',     'nuleaf': 0, 'hellomello': 0, 'comment': 'Open field — highest impact.'},
            {'topic': 'Locations / pSEO',       'nuleaf': 0, 'hellomello': 0, 'comment': 'Open field.'},
            {'topic': '"Near me" queries',      'nuleaf': 0, 'hellomello': 0, 'comment': 'Undefended.'},
            {'topic': 'Wellness / lifestyle',   'nuleaf': 0, 'hellomello': 0, 'comment': 'Skip.'},
            {'topic': 'Reviews / social proof', 'nuleaf': 0, 'hellomello': 0, 'comment': 'Open.'},
            {'topic': 'Editorial link bait',    'nuleaf': 0, 'hellomello': 0, 'comment': 'Open.'},
            {'topic': 'Help / support SEO',     'nuleaf': 0, 'hellomello': 0, 'comment': 'Open.'},
        ],
        'extra_steal': [
            {'play': 'Nothing material yet', 'effort': 1, 'impact': 1, 'note': 'Watch for growth signals; revisit if the footprint expands.'},
            {'play': 'Re-audit on growth',   'effort': 1, 'impact': 1, 'note': 'Set a six-month check-in to re-run the deck if their content surface grows.'},
        ],
        'extra_avoid': [
            {'trap': 'Dismissing early-stage entrants', 'evidence': 'Small footprints can scale fast in this category. Today&rsquo;s 21 keywords can become tomorrow&rsquo;s 500.'},
            {'trap': 'Brand-only fortress',             'evidence': '~96% of traffic is brand and Cannihelp crossover. Any non-brand competitor walks past them.'},
        ],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def enrich_notes(slug, spec):
    """Merge template fields into competitors/<slug>/data/notes.json."""
    path = os.path.join(COMP, slug, 'data', 'notes.json')
    with open(path, 'r', encoding='utf-8') as f:
        notes = json.load(f)

    notes['period'] = spec['period']
    notes['tagline'] = spec['tagline']
    notes['verdict_label'] = spec['verdict_label']
    notes['verdict_tone'] = 'green' if spec['verdict_colour'] == '--moss-3' else 'amber'
    notes['eeat'] = spec['eeat']
    notes['gap_matrix'] = spec['gap_matrix']

    verdict = notes.setdefault('verdict', {})
    steal = verdict.setdefault('steal', [])
    avoid = verdict.setdefault('avoid', [])
    for item in spec.get('extra_steal', []):
        if not any(s.get('play') == item['play'] for s in steal):
            steal.append(item)
    for item in spec.get('extra_avoid', []):
        if not any(a.get('trap') == item['trap'] for a in avoid):
            avoid.append(item)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def run(cmd, cwd=None):
    print(f'  $ {cmd}  (cwd={cwd or os.getcwd()})')
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout)
        sys.stderr.write(r.stderr)
        raise SystemExit(f'Command failed: {cmd}')
    return r.stdout


def replace_once(html, old, new, label):
    if old not in html:
        raise SystemExit(f'  ! pattern not found ({label}): {old[:80]}...')
    n = html.count(old)
    if n > 1:
        raise SystemExit(f'  ! pattern matched {n}x — needs more context ({label}): {old[:80]}...')
    return html.replace(old, new)


def customise_html(slug, spec):
    """Clone alternaleaf presentation.html and substitute per-slug strings."""
    with open(REF, 'r', encoding='utf-8') as f:
        html = f.read()

    brand = spec['brand']
    domain = spec['domain']
    colour = spec['verdict_colour']

    # --- Title + cover ---
    html = replace_once(
        html,
        '<title>Competitor Analysis — Alternaleaf</title>',
        f'<title>Competitor Analysis — {brand}</title>',
        'title',
    )
    html = replace_once(
        html,
        '<h1 class="display">Alternaleaf<span style="color:var(--moss-3)">.</span></h1>',
        f'<h1 class="display">{brand}<span style="color:var(--moss-3)">.</span></h1>',
        'cover h1',
    )
    html = replace_once(
        html,
        '<div><span class="eyebrow">Domain</span><b>alternaleaf.com.au</b></div>\n        <div><span class="eyebrow">Parent</span><b>Montu</b></div>',
        f'<div><span class="eyebrow">Domain</span><b>{domain}</b></div>\n        <div><span class="eyebrow">{spec["meta2_label"]}</span><b>{spec["meta2_value"]}</b></div>',
        'cover meta domain+parent',
    )
    html = replace_once(
        html,
        '<div><span class="eyebrow">Verdict</span><b style="color:var(--moss-3)" data-bind="verdict_label"></b></div>',
        f'<div><span class="eyebrow">Verdict</span><b style="color:var({colour})" data-bind="verdict_label"></b></div>',
        'cover verdict colour',
    )

    # --- Slide 02 ---
    html = replace_once(
        html,
        '<div class="head"><span class="eyebrow">02 · Executive snapshot</span><span class="eyebrow">Alternaleaf · May 2026</span></div>',
        f'<div class="head"><span class="eyebrow">02 · Executive snapshot</span><span class="eyebrow">{brand} · {spec["period"]}</span></div>',
        '02 head',
    )
    html = replace_once(
        html,
        '<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:14px 0 4px">The size of the <em class="display italic">prize</em>.</h2>\n    <p class="lede">Six metrics, one read: this is a brand-powered, portal-led organic engine. The category-level moat is thinner than the headline numbers suggest.</p>',
        f'<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:14px 0 4px">{spec["slide_02_title"]}</h2>\n    <p class="lede">{spec["slide_02_lede"]}</p>',
        '02 title+lede',
    )
    html = replace_once(
        html,
        '<div class="panel"><h4>Digital footprint</h4><p class="small" style="margin:0">Three properties working together: <b class="mono">www</b> for acquisition, <b class="mono">patient</b> for retention, <b class="mono">support</b> for the long-tail informational. The support hub alone earns 4.4K visits/mo from defensive informational queries.</p></div>\n      <div class="panel"><h4>Legal &amp; compliance posture</h4><p class="small" style="margin:0">Conservative. No product claims, careful clinical language, clean linking — defensible if the regulator pushes. Anything we copy from here is safe by definition.</p></div>',
        f'<div class="panel"><h4>Digital footprint</h4><p class="small" style="margin:0">{spec["slide_02_footprint"]}</p></div>\n      <div class="panel"><h4>Legal &amp; compliance posture</h4><p class="small" style="margin:0">{spec["slide_02_compliance"]}</p></div>',
        '02 panels',
    )

    # --- Slide 03 ---
    html = replace_once(
        html,
        '<div class="head"><span class="eyebrow">03 · Brand &amp; UX read</span><span class="eyebrow">alternaleaf.com.au</span></div>\n    <h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:14px 0 4px">A healthcare brand, <em class="display italic">not</em> a dispensary.</h2>\n    <p class="lede">The visual and content system is the deliberate signal: this is a clinic, not a shop. That positioning is what lets them defend high-volume brand search and what makes their copy compliant.</p>',
        f'<div class="head"><span class="eyebrow">03 · Brand &amp; UX read</span><span class="eyebrow">{domain}</span></div>\n    <h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:14px 0 4px">{spec["slide_03_title"]}</h2>\n    <p class="lede">{spec["slide_03_lede"]}</p>',
        '03 head+title+lede',
    )

    # --- Slide 04 ---
    html = replace_once(
        html,
        "4,536 ranking keywords across the domain — yet almost 90% of traffic comes from position #1. They have an enormous footprint of dormant rankings on page 2+ that produce nothing. That's the gap below the surface.",
        spec['slide_04_lede'],
        '04 lede',
    )
    # 04 footer
    totals = read_totals(slug)
    html = replace_once(
        html,
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = 4,536 KEYWORDS</span></div>',
        f'<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = {totals["keywords"]:,} KEYWORDS</span></div>',
        '04 footer',
    )

    # --- Slide 07 ---
    html = replace_once(
        html,
        '<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:14px 0 4px">It\'s the brand. Almost <em class="display italic">all of it</em>.</h2>\n    <p class="lede">Two cuts of the same question: by intent label, and by brand vs non-brand. The verdict is the same — 90% of organic traffic is people typing "alternaleaf" or a misspelling. The non-brand category sliver is where the real fight is.</p>',
        f'<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:14px 0 4px">{spec["slide_07_title"]}</h2>\n    <p class="lede">{spec["slide_07_lede"]}</p>',
        '07 title+lede',
    )
    html = replace_once(
        html,
        '<p class="small" style="margin-top:14px"><b>Read:</b> 71% of keywords are non-brand but they yield 10% of traffic. The brand fortress is doing the work; the rest of the inventory is parked.</p>',
        f'<p class="small" style="margin-top:14px">{spec["slide_07_read"]}</p>',
        '07 read',
    )

    # --- Slide 09 footer ---
    html = replace_once(
        html,
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = 4,536 KEYWORDS · 13 PILLARS</span></div>',
        f'<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = {totals["keywords"]:,} KEYWORDS</span></div>',
        '09 footer',
    )

    # --- Slide 10 ---
    html = replace_once(
        html,
        '<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">Their <em class="display italic">/hub/</em> is bloat. Their <em class="display italic">/support/</em> is the workhorse.</h2>\n    <p class="lede">106 ranking pages plotted on pages-published × traffic-earned. The diagonal separates the workhorses from the bloat. The wellness hub sits in the bottom-right bloat quadrant; the support subdomain sits as a hidden workhorse.</p>',
        f'<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">{spec["slide_10_title"]}</h2>\n    <p class="lede">{spec["slide_10_lede"]}</p>',
        '10 title+lede',
    )
    old10bullets = (
        '<li><b>Star</b> · homepage + patient portal carry 92% of traffic on ~3 pages.</li>\n'
        '          <li><b>Workhorse</b> · support / help centre — 30 pages → 4.4K visits.</li>\n'
        '          <li><b>Bloat</b> · /hub/ wellness — 21 pages → 82 visits. Cannabis-adjacent in name only.</li>\n'
        '          <li><b>Hidden gem</b> · medical-cannabis hub — small footprint, decent links.</li>'
    )
    new10bullets = '\n          '.join(f'<li>{b}</li>' for b in spec['slide_10_bullets'])
    html = replace_once(html, old10bullets, new10bullets, '10 bullets')
    html = replace_once(
        html,
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = 106 PAGES · 9 CLUSTERS</span></div>',
        f'<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = {totals["pages"]} PAGES</span></div>',
        '10 footer',
    )

    # --- Slide 11 ---
    html = replace_once(
        html,
        '<div class="head"><span class="eyebrow">11 · Location strategy</span><span class="eyebrow">1,128 location keywords</span></div>\n    <h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">National framing. <em class="display italic">Soft</em> on capital cities. Silent on "near me".</h2>\n    <p class="lede">They rank for 1,128 location-tagged keywords but pin most to a national "Australia" framing. Capital-city coverage is uneven; "near me" queries are essentially undefended — the highest-intent geo terms in the category.</p>',
        f'<div class="head"><span class="eyebrow">11 · Location strategy</span><span class="eyebrow">{spec["slide_11_eyebrow"]}</span></div>\n    <h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">{spec["slide_11_title"]}</h2>\n    <p class="lede">{spec["slide_11_lede"]}</p>',
        '11 head+title+lede',
    )
    html = replace_once(
        html,
        '<p class="small" style="margin-top:8px"><b>Hellomello play:</b> pSEO at the suburb level for the top 5 metros + a properly templated "near me" funnel. They aren\'t fighting page by page.</p>',
        f'<p class="small" style="margin-top:8px">{spec["slide_11_play"]}</p>',
        '11 play',
    )
    html = replace_once(
        html,
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = 1,128 LOCATION KEYWORDS</span></div>',
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">LOCATION SURFACE · LIMITED</span></div>',
        '11 footer',
    )

    # --- Slide 12 ---
    html = replace_once(
        html,
        '<p class="lede">81 condition keywords ranking, 663 clinic / doctor keywords ranking — together producing 1,367 visits (under 2% of total). The compliance posture that protects them on commercial pages is the same posture that keeps them invisible on the searches patients actually run.</p>',
        f'<p class="lede">{spec["slide_12_lede"]}</p>',
        '12 lede',
    )
    html = replace_once(
        html,
        "<p class=\"small\" style=\"margin-top:8px\"><b>Hellomello play:</b> condition-led landing pages with real E-E-A-T (clinician bios, citations, dated reviews). They can't author this aggressively — we can.</p>",
        f'<p class="small" style="margin-top:8px">{spec["slide_12_play"]}</p>',
        '12 play',
    )
    html = replace_once(
        html,
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">N = 81 CONDITIONS + 663 CLINIC KEYWORDS</span></div>',
        f'<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">{spec["slide_12_footer"]}</span></div>',
        '12 footer',
    )

    # --- Slide 13 ---
    html = replace_once(
        html,
        '<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">Two pages <em class="display italic">print money</em>. Ten pages are decaying.</h2>\n    <p class="lede">Homepage and patient portal carry the entire site. Below them, a layer of pages with real keyword coverage but no traffic — the inventory of decay.</p>',
        f'<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">{spec["slide_13_title"]}</h2>\n    <p class="lede">{spec["slide_13_lede"]}</p>',
        '13 title+lede',
    )

    # --- Slide 14 ---
    html = replace_once(
        html,
        '<p class="small" style="margin-top:8px">Brand spellings, login, patient portal. Defensive. Not contestable in months.</p>',
        f'<p class="small" style="margin-top:8px">{spec["slide_14_fortress"]}</p>',
        '14 fortress',
    )
    html = replace_once(
        html,
        '<p class="small" style="margin-top:8px">Category terms — <i>medical cannabis</i>, <i>medical marijuanas australia</i>, <i>aus medical weed</i>. Contestable. Steal these first.</p>',
        f'<p class="small" style="margin-top:8px">{spec["slide_14_opportunity"]}</p>',
        '14 opportunity',
    )

    # --- Slide 15 backlinks: hide because all 6 have 0 backlinks ---
    html = replace_once(
        html,
        '<!-- 15 · BACKLINKS PROFILE · D (stacked bar + histogram) -->\n<section class="slide dark" data-slide="15">',
        '<!-- 15 · BACKLINKS PROFILE · D (hidden — no backlinks export available) -->\n<section class="slide dark" data-slide="15" hidden>',
        '15 hide',
    )

    # --- Slide 17 ---
    html = replace_once(
        html,
        '<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">Compliance is solid. <em class="display italic">Authorship</em> is the weak seam.</h2>\n    <p class="lede">Their commercial pages are conservative and clean; the wellness hub leaks credibility — author bylines without credentials, schema gaps on medical pages, mixed freshness. Hellomello can outrank by being more demonstrably expert.</p>',
        f'<h2 class="display" style="font-size:clamp(34px,3.4vw,48px);margin:12px 0 4px">{spec["slide_17_title"]}</h2>\n    <p class="lede">{spec["slide_17_lede"]}</p>',
        '17 title+lede',
    )

    # --- Slide 18 ---
    html = replace_once(
        html,
        '<p class="lede">Plotted on a 2×2 of how hard it is to ship vs how much organic upside it unlocks. The top-left quadrant — <i>low effort, high impact</i> — is where Hellomello should spend the next two release cycles.</p>',
        f'<p class="lede">{spec["slide_18_lede"]}</p>',
        '18 lede',
    )

    # --- Slide 19 ---
    html = replace_once(
        html,
        "<p class=\"lede\">Where Alternaleaf's strategy quietly costs them — published in volume, returns nothing. Each trap is annotated with the exact inventory and the visits it produces.</p>",
        f'<p class="lede">{spec["slide_19_lede"]}</p>',
        '19 lede',
    )

    # --- Slide 20 ---
    html = replace_once(
        html,
        "<p class=\"lede\">Ten topics, scored 0–5 for Alternaleaf's presence and Hellomello's current presence. The orange row is the gap we own — every row Alternaleaf scores 2 or less is a contested or open field.</p>",
        f'<p class="lede">{spec["slide_20_lede"]}</p>',
        '20 lede',
    )
    html = replace_once(
        html,
        "<p class=\"small\" style=\"margin-top:6px\"><b>Bottom line.</b> Alternaleaf is the safest reference point in the category. The gaps they leave — conditions, locations, \"near me\", clinical authority — are real and undefended. Speed wins.</p>",
        f'<p class="small" style="margin-top:6px">{spec["slide_20_bottom"]}</p>',
        '20 bottom',
    )
    html = replace_once(
        html,
        '<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">END · ALTERNALEAF · v2</span></div>',
        f'<div class="foot pg-foot"><span class="pg pg-num"></span><span class="pg">{spec["end_tag"]}</span></div>',
        'end tag',
    )

    # --- JS gap-matrix column key ---
    html = replace_once(
        html,
        "const cols = [['Alternaleaf','alternaleaf'],['Hellomello','hellomello']];",
        f"const cols = [['{brand}','{slug}'],['Hellomello','hellomello']];",
        'JS gap cols',
    )
    html = replace_once(
        html,
        "if (c[1]==='hellomello' && (r.alternaleaf<=2) && r.hellomello<=1){",
        f"if (c[1]==='hellomello' && (r.{slug}<=2) && r.hellomello<=1){{",
        'JS gap highlight',
    )

    return html


def read_totals(slug):
    """Pull totals dict from competitors/<slug>/presentation/data.js."""
    path = os.path.join(COMP, slug, 'presentation', 'data.js')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'"totals":\s*(\{[^}]+\})', content)
    if not m:
        raise SystemExit(f'Could not find totals in {path}')
    return json.loads(m.group(1))


def main(slugs):
    for slug in slugs:
        spec = SPECS[slug]
        print(f'\n=== {slug} ({spec["brand"]}) ===')

        # 1) enrich notes.json
        print(' 1. enrich notes.json')
        enrich_notes(slug, spec)

        # 2) re-run analyze.py (notes embedded into data.js)
        print(' 2. analyze.py')
        run('python3 analyze.py', cwd=os.path.join(COMP, slug, 'code'))

        # 3) clone + customise presentation.html
        print(' 3. customise presentation.html')
        html = customise_html(slug, spec)
        out_path = os.path.join(COMP, slug, 'presentation', 'presentation.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        line_count = html.count('\n') + 1
        print(f'    wrote {line_count} lines -> {out_path}')

        # 4) build_offline.py
        print(' 4. build_offline.py')
        run('python3 build_offline.py', cwd=os.path.join(COMP, slug, 'code'))

        # 5) publish offline -> public/hellomello/competitors/<slug>/index.html
        print(' 5. publish')
        pub_dir = os.path.join(PUB, slug)
        os.makedirs(pub_dir, exist_ok=True)
        src = os.path.join(COMP, slug, 'presentation', 'presentation-offline.html')
        dst = os.path.join(pub_dir, 'index.html')
        shutil.copyfile(src, dst)
        size = os.path.getsize(dst)
        print(f'    -> {dst} ({size:,} bytes)')


if __name__ == '__main__':
    slugs = sys.argv[1:] or list(SPECS.keys())
    main(slugs)
