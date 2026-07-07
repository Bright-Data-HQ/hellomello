# Hellomello Brand UI Kit and Guidelines

Feel-good healthcare, delivered. This is the single markdown reference for the Hellomello identity: the voice, the visual system, the UI components, and the compliance language that keeps every piece of content TGA and AHPRA aligned.

| | |
| :-- | :-- |
| **System** | Hellomello UI |
| **Version** | 1.0 |
| **Last updated** | 2026-05-28 |
| **Owner** | Hellomello Brand |
| **Status** | Live |
| **Questions** | brand@hellomello.com.au (guidelines), design@hellomello.com.au (kit) |

## Source files

This document is the plain-text companion to the design sources in this folder. When any of these change, update this file to match.

- `index.html` - Brand guidelines (rendered HTML).
- `kit.html` - Design kit (rendered HTML, live component demos).
- `Hellomello Brand Bible May 26.pdf` - The original brand bible this system is built from.
- Published copies live under `public/hellomello/brand/`.

## Contents

**Part 1 - Brand guidelines**

1. [Who we are](#1-who-we-are)
2. [Brand heart and values](#2-brand-heart-and-values)
3. [Colour palette](#3-colour-palette)
4. [Typography](#4-typography)
5. [Logo usage](#5-logo-usage)
6. [Brand voice](#6-brand-voice)
7. [Tone by channel](#7-tone-by-channel)
8. [TGA and AHPRA language guide](#8-tga-and-ahpra-language-guide)
9. [Conditions we can mention](#9-conditions-we-can-mention)
10. [Testimonials](#10-testimonials)

**Part 2 - Design kit (UI)**

11. [Design tokens](#11-design-tokens)
12. [Buttons](#12-buttons)
13. [Badges and tags](#13-badges-and-tags)
14. [Cards](#14-cards)
15. [Forms](#15-forms)
16. [Alerts and toasts](#16-alerts-and-toasts)
17. [Navigation](#17-navigation)
18. [Data and status](#18-data-and-status)
19. [Marketing patterns](#19-marketing-patterns)

---

# Part 1 - Brand guidelines

## 1. Who we are

An Australian alternative telehealth clinic. AHPRA-registered doctors and nurse practitioners. 100% online. No physical clinics. No GP referral needed. Available anywhere in Australia.

**What we do.** Patients complete a short pre-screening questionnaire, book a telehealth consultation, and if eligible receive a personalised care plan with medication dispatched through pharmacy partners. Care is delivered end to end online (eligibility, consultation, plan, dispatch and aftercare) without the friction of a traditional GP funnel.

**The numbers we can quote.**

| Stat | Value |
| :-- | :-- |
| Patients supported | 50K+ |
| Average Google rating | 4.7 stars |
| Dispatch turnaround | Same day (subject to eligibility and ordering cut-off) |

**What makes us different.**

1. **Feel-good healthcare.** We care about how the experience feels. Every interaction should leave the patient feeling better, not drained.
2. **Simple, stress-free process.** From eligibility to receiving care, every step is designed to feel effortless. No waiting rooms, no referrals.
3. **Laid-back but legit.** AHPRA-registered clinicians. Regulated. Compliant. We just do not make it feel stiff or formal.
4. **Warm, human-centred care.** Hellomello cares about the person behind the patient, and it shows in every interaction.

## 2. Brand heart and values

Every campaign, page and conversation rolls up to one of these three statements.

- **Our why.** Healthcare should help with headaches, not cause them. We exist to give Australians access to alternative care that actually makes them feel good.
- **Mission.** To keep things simple: we are here to help you feel better. Feel-good healthcare that takes the stress out of getting help.
- **Vision.** A world where healthcare does not suck. Where people feel like a person, not a chart. Where relief is accessible, not a battle to earn.

**Our values.**

1. **Kindness and empathy.** We are not here to rush you out the door. Every person deserves to feel heard and supported.
2. **Patient-centred care.** You are more than a chart. Your care should be personal and feel good, every time.
3. **Zero judgement.** No cold stares, no intimidating jargon. A safe, kind space where you can talk about what you need.
4. **Accessible and convenient.** Healthcare should be set up for the people who need it. Online, simple, no barriers.
5. **Laid-back but legit.** We keep it chill, but we are serious about providing the best care. Approachable and expert.
6. **Going above and beyond.** "Good enough" is not good enough. We go all in because our patients deserve it.

## 3. Colour palette

Cream and dark green are the load-bearing pair. Terracotta is the primary accent for emphasis, numerals and section markers. Lavender, sage and blue act as supporting tones for illustrations and section tiles.

### Primary colours

| Name | Hex | Token |
| :-- | :-- | :-- |
| Cream | `#FEFAE0` | `--cream` |
| Light Terracotta | `#DDA15E` | `--terra-light` |
| Terracotta | `#BC6C25` | `--terra` |
| Lavender | `#BEB8EB` | `--lavender` |
| Sage | `#B2DCD0` | `--sage` |
| Blue | `#2A78A0` | `--blue` |
| Dark Green | `#283718` | `--green` |

### Usage rules

| Role | Colour | When to use | Hex |
| :-- | :-- | :-- | :-- |
| `background.default` | Cream | The warm canvas behind body content. | `#FEFAE0` |
| `background.inverse` | Dark green | Full-bleed sections, footers, value tiles. | `#283718` |
| `accent.primary` | Terracotta | Section numerals, emphasis, primary CTA hover. | `#BC6C25` |
| `accent.soft` | Light terracotta | Eyebrows on dark, highlights, illustration. | `#DDA15E` |
| `accent.cool` | Sage | Approved tags, soft surfaces on dark sections. | `#B2DCD0` |
| `accent.support` | Lavender | Illustration and tertiary supporting moments. | `#BEB8EB` |
| `accent.info` | Blue | Informational labels, links inside dark sections. | `#2A78A0` |

White (`#FFFFFF`) is used for raised surfaces such as cards. On dark green, ink flips to cream, and light terracotta or sage carry the eyebrows and highlights.

## 4. Typography

Three families. League Spartan does the heavy lifting for display. Neue Einstellung is reserved for secondary display moments. Inter carries everything readable. Never substitute, never mix in a fourth.

- **League Spartan** (primary display). All headings (H1, H2, H3), nav, CTAs, buttons, eyebrows, pricing, and section numerals. H1 at 54 to 64px, weight 900, line-height 0.92, letter-spacing -0.025em.
- **Neue Einstellung** (secondary display). Sub-headings and secondary display text, retained from the original brand bible. Never for body copy. Use the licensed file in production; a serif renders as fallback when it is not installed.
- **Inter** (body copy). Website body paragraphs, card descriptions, FAQ answers, and blog posts. Body at 15px, weight 400, line-height 1.7. Use Inter 600 for inline emphasis.
- **JetBrains Mono** (mono). Eyebrows, labels, and code. 11px, weight 500, uppercase, letter-spacing 0.14em.

### Type scale

| Token | Family | Spec |
| :-- | :-- | :-- |
| display / h1 | League Spartan 900 | 54 to 64px, line-height 0.92, -0.025em |
| section / h2 | League Spartan 700 | 38px, line-height 1.05, -0.02em |
| sub / h3 | League Spartan 700 | 18 to 20px, uppercase, letter-spacing 0.02em |
| lead | Inter 400 | 17px, line-height 1.55, muted |
| body | Inter 400 | 15px, line-height 1.7 |
| small / caption | Inter 500 | 13px, line-height 1.55 |
| eyebrow / mono | JetBrains Mono 500 | 11px, uppercase, letter-spacing 0.14em |

### Font stacks

```css
--font-display: "League Spartan", "Helvetica Neue", system-ui, sans-serif;
--font-sub:     "League Spartan", Georgia, serif;
--font-body:    "Inter", "Helvetica Neue", system-ui, -apple-system, sans-serif;
--font-mono:    "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
```

## 5. Logo usage

Hellomello has a primary wordmark, a secondary cream-on-green lockup, a coloured-letters alternative, and a single-letter submark. Always use the approved files.

| Logo | Background | Use for |
| :-- | :-- | :-- |
| Primary wordmark (`hellomello`, dark green) | Cream or white | Default, most surfaces |
| Secondary wordmark (`hellomello`, cream) | Dark green | Inverse sections and footers |
| Coloured wordmark (letters in brand palette) | Cream or white | Social and merchandising |
| Submark (single `h`, cream on terracotta tile) | Any | App icons and avatars |
| Tile lockup (five-by-two grid, one letter per swatch) | Any | Social grids and packaging |

**Always do.**

- Use approved logo files. Never recreate from type.
- Keep minimum clear space equal to the height of the "h" on all sides.
- Use the dark green logo on cream and white backgrounds.
- Use the cream logo on dark green backgrounds.
- Use the submark for social profile images and app icons.
- Use the alternative tile logo for social content and merchandising.

**Never do.**

- Never stretch, distort or rotate the logo.
- Never apply gradient fills.
- Never place it on a busy photographic background without a container.
- Never use unapproved colours.
- Never add drop shadows or glow effects.
- Never reproduce the wordmark from type. Always use the file.

## 6. Brand voice

**The friendly fello.** Like a mate who knows when to crack a joke and when to get serious. Chill, supportive, smart, but never too formal. When Hellomello talks it feels relaxed, simple and warm, with a bit of humour but always with kindness and respect. Yes, we can be clinical, but it is always done with a warm and friendly tone.

**Voice pillars.**

1. **Friendly but professional.** Casual, not too casual. Warm and approachable, but you can trust us.
2. **Empathetic and caring.** We listen. You never feel like just another number. We have always got your back.
3. **Honest and transparent.** Clear, simple answers. No medical jargon. No sugarcoating.
4. **Laid-back but legit.** Chill, but serious about providing the best care.

**We are:** warm, human, confident, non-judgemental, accessible, trustworthy.

**We never sound like:** a GP waiting room, corporate or clinical, jargon-heavy, preachy, confusing or formal, overpromising results.

## 7. Tone by channel

The voice is constant. The tone flexes per channel. Use this as the first reference when drafting any new copy.

| Channel | Tone | Example |
| :-- | :-- | :-- |
| Website | Clear, confident, warm | "Telehealth consultations built around you. Not the other way round." |
| Blog / SEO | Informational, helpful, approachable | "Here's everything you need to know about telehealth in Australia." |
| Social media | Fun, laid-back, positive | "No judgement, just good vibes. Check your eligibility in 2 minutes." |
| Email | Warm, calm, one clear action | "You're almost there. Finish your sign-up and we'll guide you through the rest." |
| Customer service | Warm, patient, helpful | "Hey there! Don't worry, we've got this. Let's get you booked in." |
| Reminders | Friendly, clear, considerate | "Your appointment is just around the corner. Let us know if you need anything." |
| Ads / paid media | Direct, benefit-led, compliant | "Check your eligibility in 2 minutes. AHPRA-registered doctors, 100% online." |
| Follow-up | Supportive, positive, relaxed | "How are you doing? We're all ears, reach out any time." |

**Three rules that apply everywhere.**

- **No urgency language.** "Limited time only", "Act now" and "Don't miss out" create pressure. Hellomello is calm and supportive, not pushy.
- **Short and mobile-first.** Most traffic is on mobile. Short sentences, short paragraphs, scannable. Never walls of text.
- **Emoji.** Social and informal comms only. Never in website copy, blog posts or professional documents.

## 8. TGA and AHPRA language guide

This is the single most important section in this document. Run every piece of promotional, social and ad content through this guide before publishing.

> **This section is non-negotiable.** Apply it to every piece of Hellomello content before it is published. When in doubt, default to the approved list. **Never guess.**

### Use freely (approved)

- **What we do:** telehealth consultations, online telehealth clinic, alternative telehealth clinic, alternative healthcare, alternative medicine, AHPRA-registered clinicians, access to alternative healthcare, personalised care plans.
- **Process and eligibility:** check your eligibility, if eligible we'll guide you, pre-screening questionnaire, book a telehealth consultation, subject to eligibility, results may vary, outcomes are patient-specific.
- **Service and care:** support for your health journey, ongoing care, ongoing aftercare, compassionate care, feel-good healthcare, 100% online, same day dispatch, fast discreet delivery, non-judgemental environment.
- **Credentials:** AHPRA-registered doctors, AHPRA-registered nurse practitioners, qualified practitioners, licensed and confidential.

### Never use (banned)

- **Treatment claims:** treatment for [condition], relief from [condition], cure, fix, guaranteed results, proven to treat, clinically proven.
- **Restricted substance references:** medicinal cannabis, cannabis, marijuana, weed / pot, CBD / THC, plant-based medicine, natural medicine.
- **Conditions in ads or social:** anxiety, depression, chronic pain, insomnia, fibromyalgia, PTSD.
- **Pressure language:** limited time only, act now, don't miss out, we're the best, miracle solution.

### Grey area, handle with care

| Term | Risk | Use instead |
| :-- | :-- | :-- |
| "Help with [condition]" | Implies treatment outcome | "Support for your health" |
| "Manage your [condition]" | Can imply treatment claim | "Ongoing health management" |
| "Feel better" | Implies clinical outcome | "Feel-good healthcare" only |
| "Alternative treatment" | TGA regulates "treatment" | "Alternative care" |
| "Symptoms" | Risky in ads | Blog content only |
| "Pain" | Named condition | Blog only, never in ads |
| "Sleep" in copy | Named condition | "Sleep Quality Support" as website label only |
| "Anxiety" / "stress" | Named conditions | "Stress & Wellbeing Support" as website label only |

### Before and after

| Don't | Do |
| :-- | :-- |
| "Treatment for pain" | "Support for your health journey" |
| "Relief from anxiety" | "Access to alternative healthcare" |
| "Cure your sleep problems" | "Sleep Quality Support, check your eligibility" |
| "We'll fix your chronic illness" | "Ongoing health management, if eligible" |
| "Medicinal cannabis clinic" | "Alternative telehealth clinic" |
| "Limited time, act now" | "If you've been thinking about it, this may be a good time to start" |
| "Best doctors in Australia" | "AHPRA-registered doctors who truly listen" |
| "Guaranteed results" | "Outcomes are patient-specific, our doctors will guide you" |
| "Cannabis for your anxiety" | "Alternative healthcare, if eligible" |

## 9. Conditions we can mention

Naming a condition is permitted when it is framed around why someone seeks care, not what the treatment does. Use "may be helpful with issues relating to" or "our clinicians may support patients experiencing". Never use "treats", "relieves" or "fixes". The "when [other thing] isn't working" pattern is compliant.

| Area | When to reach for it | Approved framing | Website label |
| :-- | :-- | :-- | :-- |
| Pain Management | When massage, physio or chiro only provide limited relief. | "Our clinicians may support patients experiencing issues relating to pain management." | Pain Management Support |
| Sleep Support | When sleep apps, acupuncture or white noise aren't improving your rest. | "Our services may be helpful with issues relating to sleep." | Sleep Quality Support |
| Stress and Wellbeing | When meditation, psychology or breathwork aren't easing day-to-day stress. | "Our clinicians may support patients experiencing issues with stress and mental wellbeing." | Stress & Wellbeing Support |
| Women's Health | When you're looking for more personalised options for your health. | "Our clinicians may support patients experiencing issues relating to women's health and hormonal wellbeing." | Women's Health Support |
| Chronic Health | When ongoing symptoms are affecting your daily life. | "Our services may be helpful with issues relating to chronic and ongoing health management." | Chronic Health Management |
| Neurological Support | When conventional options haven't provided the relief you need. | "Our clinicians may support patients experiencing issues relating to neurological symptoms and conditions." | Neurological Support |

**Framing rules.**

| Approved | Never |
| :-- | :-- |
| "issues relating to pain management" | "treatment for chronic pain" |
| "issues with sleep" | "fixes your sleep problems" |
| "may be helpful with issues relating to" | "helps with / treats / relieves" |
| "our clinicians may support patients experiencing" | "we treat patients with anxiety" |
| "depending on your situation" | "guaranteed to work" |
| "check your eligibility" | "get started with pain relief" |
| "when [other thing] isn't working" | "better than physio / medication" |
| "if eligible, we'll guide you through the rest" | "get the relief you deserve" |

## 10. Testimonials

A comment becomes a regulated testimonial the moment it references any clinical aspect of care. Use the one-question filter: does this review mention why they came, what they were treated for, or what changed in their health? If yes, it cannot be used.

**The three triggers.**

1. **Symptom.** The specific symptom or reason the person sought treatment. Mentioning why they came is a clinical aspect.
2. **Diagnosis or treatment.** The specific diagnosis they received or treatment provided by the practitioner.
3. **Outcome.** Any specific result, improvement, or reference to the practitioner's skill or effectiveness, directly or by comparison.

**Examples we can use.**

- "The booking process was so easy. I was set up within a day."
- "The nurses were so kind and easy to talk to. I never felt judged."
- "I was surprised how simple the whole process was."
- "The team was professional and the whole experience felt really smooth."
- "I wish I had done this sooner. Getting started was the easiest part."

**Examples we cannot use.**

- "My pain is so much better since starting with Hellomello." (outcome)
- "I finally got a good night's sleep after my first month." (outcome referencing symptom)
- "The doctor understood my anxiety and knew exactly what I needed." (symptom plus clinical skill)
- "After years of chronic pain I finally found something that works." (outcome)

**Review prompts.**

| What we can ask for | What we steer away from |
| :-- | :-- |
| How easy was the booking process? | Why they originally came to Hellomello. |
| How did the team make you feel? | Any health changes since starting. |
| How was the communication throughout? | Their specific condition or diagnosis. |
| Would you recommend the experience to a friend? | How effective the treatment or prescription was. |

---

# Part 2 - Design kit (UI)

The UI primitives that bring the Hellomello identity into product surfaces: buttons, forms, cards, alerts, navigation and marketing patterns. Every token here maps back to the brand guidelines above. Override values at the `:root` level only.

## 11. Design tokens

### Colour tokens

```css
:root{
  /* Brand */
  --green:#283718; --green-2:#1F2B12; --green-3:#34481F; --green-4:#41562A;
  --cream:#FEFAE0; --cream-2:#F6F0CC; --cream-3:#FBF6D6;

  /* Accent */
  --terra:#BC6C25; --terra-light:#DDA15E; --terra-hover:#A35C1E;
  --lavender:#BEB8EB; --sage:#B2DCD0; --blue:#2A78A0;

  /* Surfaces */
  --paper:#FBF6D6; --paper-2:#F6F0CC;
  --surface:#FFFFFF; --surface-2:#FAF7E8;

  /* Ink */
  --ink:#283718; --ink-2:#34481F; --muted:#5C6849; --muted-2:#8C9779; --disabled:#B5BCA6;

  /* Borders */
  --border:#E8E1B8; --border-strong:#CFC68C; --ring:#BC6C25;

  /* Status */
  --ok-bg:#E4F1D6;  --ok-fg:#3F6A1A;  --ok-bd:#C5DFA6;
  --warn-bg:#FBE7C4; --warn-fg:#8A4A0E; --warn-bd:#EFC788;
  --bad-bg:#F8D7D2;  --bad-fg:#9B2418;  --bad-bd:#EDB5AC;
  --info-bg:#DCE9F1; --info-fg:#1F587A; --info-bd:#B6CFDF;
}
```

### Radius

| Token | Value |
| :-- | :-- |
| `--r-sm` | 4px |
| `--r-md` | 8px |
| `--r-card` | 14px |
| `--r-lg` | 18px |
| `--r-xl` | 24px |
| `--r-pill` | 9999px (full) |

### Shadow

| Token | Value | Use |
| :-- | :-- | :-- |
| `--sh-soft` | `0 1px 16px rgba(40,55,24,.07)` | Quiet lift on light surfaces |
| `--sh-card` | `0 6px 22px rgba(40,55,24,.10)` | Default card elevation |
| `--sh-pop` | `0 8px 28px rgba(40,55,24,.18)` | Toasts, popovers, overlays |

### Spacing scale

`4px` (space-1), `8px` (space-2), `12px` (space-3), `16px` (space-4), `20px` (space-5), `24px` (space-6), `32px` (space-8), `48px` (space-12), `64px` (space-16).

Content max-width is `1100px`.

## 12. Buttons

Pill-shaped, League Spartan 700. Primary is dark green. Secondary is terracotta for emphasis (for example "Check eligibility"). Use one primary per view. Focus ring is terracotta. Active state nudges down 1px.

| Variant | Class | Look |
| :-- | :-- | :-- |
| Primary | `.btn .btn-primary` | Dark green fill, cream text; hover to `--green-2` |
| Secondary | `.btn .btn-secondary` | Terracotta fill, cream text; hover to `--terra-hover` |
| Tertiary | `.btn .btn-tertiary` | Cream fill, green text, strong border |
| Ghost | `.btn .btn-ghost` | Transparent, green text; cream hover |
| Link | `.btn .btn-link` | Blue text, no fill; underlines on hover |
| Icon | `.btn .btn-icon` | Round, cream-2 fill, green icon |
| Disabled | `.btn[disabled]` | Muted fill, not-allowed cursor |

Sizes: `.btn-lg`, default, `.btn-sm`, `.btn-xs`.

```html
<button class="btn btn-primary">Check eligibility</button>
<button class="btn btn-secondary">Book consultation</button>
<button class="btn btn-tertiary">Learn more</button>
<a class="btn btn-link" href="#">View FAQs &rarr;</a>
```

On dark green sections, lead with the terracotta secondary or the cream tertiary. Keep link buttons in light terracotta so they stay readable.

## 13. Badges and tags

Mono-cased, pill-shaped. Reserve status colours for status. Use brand-tinted badges for filters and categories. Add `.badge-dot` for a leading status dot.

| Type | Class | Use |
| :-- | :-- | :-- |
| Success | `.badge-ok` | Approved, confirmed |
| Warning | `.badge-warn` | Pending review |
| Danger | `.badge-bad` | Banned, failed |
| Info | `.badge-info` | In progress, in review |
| Neutral | `.badge-neutral` | Draft, completed |
| Terra | `.badge-terra` | Category or filter |
| Sage | `.badge-sage` | Category or filter |
| Lavender | `.badge-lavender` | Category or filter |
| Blue | `.badge-blue` | Category or filter (for example AHPRA-registered) |

```html
<span class="badge badge-ok badge-dot">Approved</span>
<span class="badge badge-sage">Sleep support</span>
```

## 14. Cards

Default cards sit on the cream paper. Feature cards invert to dark green. Service cards use a coloured square icon from the brand palette.

- **Content card** (`.card`): white surface, strong border, 14px radius, optional mono eyebrow, League Spartan title, muted body, terracotta CTA footer.
- **Feature card** (`.card .card-feature`): dark green fill, cream text, light-terracotta title, sage eyebrow.
- **Soft card** (`.card .card-soft`): cream-2 fill for quieter content.
- **Service card** (`.svc-card`): a 48px rounded icon tile (`.terra`, `.lavender`, `.blue`, default sage), title, short description, and a small tertiary CTA.

```html
<div class="card card-feature">
  <span class="eyebrow">Featured</span>
  <h4>Telehealth built around you.</h4>
  <p>Australia-wide care from AHPRA-registered clinicians. 100% online, no GP referral needed.</p>
  <div class="cta">Check eligibility <span>&rarr;</span></div>
</div>
```

## 15. Forms

Quiet by default. Focus rings use terracotta. Always pair labels with helpful microcopy, never with urgency.

- **Fields** (`.field`): League Spartan 600 label, optional `.hint`, 10px radius inputs with a strong border. Focus swaps the border to `--ring` with a soft terracotta glow.
- **Invalid** (`.field.invalid`): red border and a warm `.err` message. Keep the wording kind, for example "That date doesn't look quite right, mind double-checking?".
- **Input group** (`.input-group`): for prefixes such as `+61`.
- **Choice controls**: `.check` (rounded-square checkbox), `.radio`, and `.toggle` (switch). Checked state fills dark green.
- **Stepper** (`.stepper`): pill segmented control for multi-step flows such as Eligibility, Details, Booking, Confirm. Pair with `.progress`.

```html
<div class="field">
  <label for="email">Email address</label>
  <input type="email" id="email" placeholder="you@hellomello.com.au">
  <span class="hint">We'll only use this to confirm your booking.</span>
</div>
```

## 16. Alerts and toasts

Always warm and supportive, even when delivering bad news. Never use the alert pattern for urgency or pressure.

| Variant | Class | Use |
| :-- | :-- | :-- |
| Success | `.alert .alert-ok` | Confirmations, "you're all set" |
| Warning | `.alert .alert-warn` | Soft heads-up, "one quick thing" |
| Danger | `.alert .alert-bad` | Something went wrong, kept low-key |
| Info | `.alert .alert-info` | Neutral, compliance-safe notes |

A `.toast` is a dark green pill with a status icon and one short line, lifted with `--sh-pop`. Use for transient confirmations such as "Reminder sent."

```html
<div class="alert alert-ok">
  <div class="ic">&check;</div>
  <div>
    <h5>You're all set</h5>
    <p>Your booking is confirmed for Thursday at 4:30pm. We'll send a reminder the day before.</p>
  </div>
</div>
```

## 17. Navigation

Cream-on-white headers, dark-green footers. Pills for tabs and pagination keep the laid-back feel.

- **Top nav** (`.nav-bar`): cream bar, League Spartan 900 logo, plain links that hover to terracotta, ghost "Sign in" plus primary "Check eligibility".
- **Breadcrumb** (`.breadcrumb`): mono, muted, terracotta hover, current page in ink.
- **Tabs** (`.tabs`): pill segmented control; active tab fills dark green.
- **Pagination** (`.pagination`): round pill buttons; active fills dark green.

## 18. Data and status

Stat tiles read in League Spartan 900. Tables stay quiet: no zebra striping, just a rule and a soft hover.

- **Stat tile** (`.stat-tile`): dark green tile, light-terracotta number, sage mono label, optional muted description. Example: "50K+ / Patients supported".
- **Progress** (`.progress`): 8px track with a terracotta gradient bar. Pair with step copy such as "Step 3 of 5, you're 64% of the way there."
- **Table** (`.tbl`): white surface, mono uppercase headers on cream-2, thin rules, soft cream hover. Use status badges in the status column.

## 19. Marketing patterns

Compositions used across the marketing site, built only from the primitives above.

- **Hero** (`.hero`): dark green panel, League Spartan 900 headline with a light-terracotta emphasis word, one supporting line, and two CTAs (secondary plus tertiary). Example: "Telehealth built *around you*."
- **Trust bar** (`.trust-bar`): cream bar of short proof points with sage icon chips, for example "AHPRA-registered clinicians", "4.7 Google rating", "Same-day dispatch", "Licensed and confidential".
- **CTA band** (`.cta-band`): soft cream-to-sage gradient panel, a short green headline, muted line, and one primary CTA. Keep it calm, never pushy.
- **Footer** (`.foot-mock`): dark green, cream logo and tagline, mono light-terracotta column headings, and a mono legal line. Example legal: "© 2026 Hellomello Pty Ltd · AHPRA-registered clinicians · Outcomes are patient-specific · Subject to eligibility."

---

*Keep this document in step with `index.html` and `kit.html`. When the brand system changes, update the source, the published copies under `public/hellomello/brand/`, and this file together.*
