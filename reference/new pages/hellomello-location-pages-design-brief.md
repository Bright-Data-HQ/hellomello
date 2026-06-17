# HelloMello Location Landing Pages: Design Brief

**Prepared by:** Bright Data
**For:** Design
**Date:** 17 June 2026
**Status:** Ready for design. Template v1.
**Handover to Rod:** Thursday 18 June 2026

---

## 1. The short version

We need one flexible landing page template for HelloMello's location pages. It is the first pillar of the SEO roadmap (pSEO), and it is the first batch we are shipping to the client this week.

The template gets built once, then filled programmatically for the top 20 suburbs to start, and scaled to hundreds after that. So the design has to hold up when the suburb name, the local copy and the delivery or pickup details swap in and out. Design the system, not a single page.

Two things make HelloMello win here: suburb-level depth (most competitors stop at capital cities) and a credibility layer on top (named practitioner, real reviews, clear eligibility copy). The design needs to carry both.

---

## 2. Why we are doing this

Local intent is where this category actually competes. Herbly built their whole engine on location pages and most of the smaller players follow them. The gap in the market is not the idea, it is depth and authority. Competitors publish thin city stubs. We go one level deeper to the suburb, and we add clinical authority and trust on top.

So the design job is to make a page that:

- reads as genuinely local, not a mail-merge,
- looks more credible and more human than a competitor city stub,
- and stays comfortably inside TGA and AHPRA boundaries (more on this in section 8).

Full strategy context: the published strategy doc, pillar 01.
https://clients.brightdata.com.au/hellomello/strategy/

---

## 3. What you are designing

**One template, two intent variants, two zoom levels.**

**Intent variants**

1. **Delivery suburb** (the default, most pages). Medication is posted to the patient. No physical location.
2. **Pickup suburb** (a small set). The patient can collect from a partner pharmacy, and delivery is still offered. These pages get an extra "collect locally" block.

The pickup suburbs are:

- Melbourne: Bayswater, Caulfield South, South Melbourne
- Brisbane: Wakerley
- Gold Coast: Upper Coomera

Everything else is delivery only.

**Zoom levels**

- **City level** (e.g. Melbourne, Brisbane). Broader page, links down to its suburbs.
- **Suburb level** (e.g. Caboolture, Frankston). The high-intent page, links back up to its city.

The design should handle both from the same component set. The difference is mostly the heading copy and the internal links, not a different layout.

---

## 4. Page structure (wireframe)

Build it from the same blocks as the new homepage so it slots straight into the brand. Order from top to bottom:

1. **Announcement bar** (reuse the site one).

2. **Hero**
   - Eyebrow: small label with the location, e.g. `ALTERNATIVE HEALTHCARE IN [SUBURB]`.
   - H1: one clear, human headline that names the location, e.g. `Alternative healthcare in [Suburb], delivered to your door.` One H1 only, this matters for SEO.
   - Subhead: one line on the local promise.
   - Price callout: `$49 to get started`.
   - Primary CTA: `Get started`. Secondary CTA: `Check my eligibility`.
   - Delivery line where relevant: `Next Business Day Delivery for orders placed before 12pm`.

3. **Trust bar** (reuse): 4.7 Google rating, 50,000+ patients, AHPRA-registered clinicians, 100% online, Australia-wide, same day dispatch.

4. **Local availability block** (the heart of the page, this is what makes it local)
   - **Delivery variant:** local delivery copy (see the patterns in section 6), expected delivery timing, "how it reaches you" in two or three steps.
   - **Pickup variant:** the same, plus a "collect locally" panel naming the pickup option, with room for an address, hours and a small map or map placeholder.

5. **What we help with** (reuse the four cards from the homepage): Sleep, Pain Management, Chronic Health, Stress and Wellbeing. Framed as support, not treatment.

6. **How HelloMello works** (reuse the four steps): Pre-screening, Telehealth consult, Treatment delivered, Ongoing aftercare.

7. **Pricing teaser**: a short version of the three pricing cards (free nurse call, $49 initial, $29 follow up), with a link to the full pricing page. Do not rebuild the whole pricing page here.

8. **Practitioner / credibility block** (the E-E-A-T layer)
   - A named, AHPRA-registered practitioner with a short bio, registration line and photo slot. This is the named reviewer for the page. Design it as a reusable component because it appears across pillars.

9. **Reviews / testimonials** (reuse). Leave room to swap inline quotes for a Trustpilot embed later.

10. **Local FAQ** (4 to 6 questions). Some shared, some location-flavoured, e.g. "How long does delivery to [Suburb] take?" This block also powers FAQ schema, so keep question and answer as clean, separate fields.

11. **Closing CTA band**: `Get started today`, eligibility check in two minutes, no referral needed.

12. **Internal links block**: nearby suburbs and the parent city. Keeps the location cluster linked together.

13. **Footer** (reuse the site footer).

---

## 5. Brand and design system

Use the existing HelloMello design kit. Do not invent new styles. Everything below is in the kit.

**Live kit and components:** https://clients.brightdata.com.au/hellomello/brand/
**Design kit page (buttons, badges, cards, pills):** https://client.brightdata.com.au/hellomello/brand/kit
**Source files in the workspace:** `brand/kit.html`, `brand/index.html`, and `brand/Hellomello Brand Bible May 26.pdf`

Quick reference:

- **Fonts:** League Spartan (display and headings), Inter (body), JetBrains Mono (small labels and eyebrows).
- **Core colours:** green `#283718`, cream `#FEFAE0`, terracotta `#BC6C25`, terracotta light `#DDA15E`, lavender `#BEB8EB`, sage `#B2DCD0`, blue `#2A78A0`.
- **Buttons, badges, cards, pills:** all defined in the kit. Reuse them.
- **Tone of the look:** warm and human, not clinical.

For copy patterns and section wording, mirror the approved new homepage and pricing pages:

- `reference/new pages/hellomello-homepage-content.md`
- `reference/new pages/hellomello-pricing-content.md`
- Homepage visual mockup (Canva): https://canva.link/ah286nnf2gpv5ut

---

## 6. Copy patterns and variables

Treat anything in `[SQUARE BRACKETS]` as a field that gets filled per page. Keep these as obvious, swappable placeholders in the design.

**Variables**

- `[Suburb]` or `[City]`, the location name.
- `[State]`, e.g. VIC, QLD, NSW.
- `[Practitioner name]` and bio.
- Delivery timing line.

**Approved delivery copy patterns** (from the client):

- "prescription delivery services to [INSERT]"
- "dispensary delivery services to [INSERT]"
- "alternative healthcare prescription delivery to [INSERT]"
- "Next Business Day Delivery for orders placed before 12pm"

**Framing note (important for SEO):** lead with "alternative healthcare", not "telehealth". "Telehealth" is a crowded national term we cannot win. "Alternative healthcare" is the winnable term the whole category chases (over 4,500 searches a month). It only needs to land in a couple of natural spots per page: the small eyebrow label and the first line of body copy. Keep the headline human.

---

## 7. SEO and technical requirements

These are build rules, but they shape the design, so please bake them in:

- **One H1 per page**, and it names the location. Then a clean heading hierarchy (H2s for sections, H3s inside).
- **Schema:** the template must support `LocalBusiness` (or `MedicalBusiness`) and `FAQPage` schema. Keep FAQ questions and answers as separate, clean fields.
- **Clean URLs**, e.g. `/locations/[suburb]`.
- **Mobile first.** Most local searches are on a phone. Design mobile first, desktop second.
- **Core Web Vitals must pass.** Keep it light. Lazy-load images, keep the map block cheap, no heavy embeds above the fold.
- **Meta title and description** fields per page (handled in build, just leave room for them).
- Space for a featured local image, with sensible alt text per page.

Background on what is already covered technically: the SEO handover doc.
https://docs.google.com/spreadsheets/d/1qT3972ykMl2jVu4chdMuvdBqaKGrocdsfBwxnm0wvZc/edit?usp=sharing

---

## 8. Compliance guardrails (TGA and AHPRA)

This is non-negotiable and the client watches it closely. The page must not read like a cannabis storefront.

- **No product claims and no naming of restricted products.** No cannabis claims in copy or imagery.
- **Eligibility-first language.** We talk about checking eligibility and support, not treatment outcomes.
- **Use the support framing** for the "what we help with" cards (e.g. "Pain Management Support", not "pain treatment").
- **Named reviewer must be a real, registered practitioner.** A third-party AHPRA-registered doctor is fine as the named reviewer for now.
- **No testimonials that imply a clinical outcome from a restricted product.**
- Rod holds final sign-off on every page before publish.

Full detail: `knowledge-base/04-compliance-tga-ahpra.md`.

---

## 9. The data behind the pages

The priority list is the client's top 20 suburbs by patient residence, split into delivery and pickup as above.

- **Suburb dataset (client, source of truth):** https://docs.google.com/spreadsheets/d/1e6A8p3uBi0ZsDqZpbie7wxbfjpEN89cqn07-PlLYYaY/edit?usp=sharing
  - Column B: everyone who signed up (broad intent, larger sample). Use this for page priority.
  - Column F: patients who paid (conversion signal). Secondary measure.
- **Local copy of the density data:** `reference/Quick - Postcode _Suburb - Patient Density - Suburb_Output.csv`

Top suburbs to design against first (so you can see real names in the template): Caboolture, Deception Bay, Morayfield, Port Macquarie, Melbourne, Kallangur, Redbank Plains, Coffs Harbour, Kelso, Emerald, Newtown, Kingston, Southport, Preston, Dubbo, Orange, Pakenham, Kirwan, Pimpama, Frankston.

---

## 10. Look at the competition

We are deliberately out-templating Herbly at suburb depth and adding authority on top. Worth a look before you start, so the page clearly beats a competitor city stub:

- **Competitor analysis decks (Herbly, Polln, Candor, Alternaleaf):** https://clients.brightdata.com.au/hellomello/competitors/
- **Live HelloMello site for current brand in the wild:** https://www.hellomello.com.au

---

## 11. What we need back

- A **mobile and desktop design** of the template, with both intent variants shown (one delivery example, one pickup example).
- The **reusable components** called out: hero, local availability block, pickup panel, practitioner block, local FAQ, internal links block.
- **One worked example** filled with a real suburb (suggest Caboolture for delivery, Upper Coomera for pickup) so we can see it with real copy.
- Editable source plus an export we can share with Rod.

Keep it consistent with the kit, keep it light, keep it human.

---

## 12. All the links in one place

| Resource | Link |
| :-- | :-- |
| Strategy doc (pillar 01, location pages) | https://clients.brightdata.com.au/hellomello/strategy/ |
| Brand kit and components (live) | https://clients.brightdata.com.au/hellomello/brand/ |
| Design kit page (components) | https://client.brightdata.com.au/hellomello/brand/kit |
| Brand kit source | `brand/kit.html`, `brand/index.html`, `brand/Hellomello Brand Bible May 26.pdf` |
| Competitor analysis decks | https://clients.brightdata.com.au/hellomello/competitors/ |
| Homepage mockup (Canva) | https://canva.link/ah286nnf2gpv5ut |
| Approved homepage content | `reference/new pages/hellomello-homepage-content.md` |
| Approved pricing content | `reference/new pages/hellomello-pricing-content.md` |
| Suburb dataset (client) | https://docs.google.com/spreadsheets/d/1e6A8p3uBi0ZsDqZpbie7wxbfjpEN89cqn07-PlLYYaY/edit?usp=sharing |
| Suburb density data (local copy) | `reference/Quick - Postcode _Suburb - Patient Density - Suburb_Output.csv` |
| SEO handover doc | https://docs.google.com/spreadsheets/d/1qT3972ykMl2jVu4chdMuvdBqaKGrocdsfBwxnm0wvZc/edit?usp=sharing |
| Compliance rules (TGA and AHPRA) | `knowledge-base/04-compliance-tga-ahpra.md` |
| Live HelloMello site | https://www.hellomello.com.au/ |

Any questions, send them through before you start and we will jump on a quick call to walk through the template.
