# Hellomello

Client workspace for the Hellomello × Bright Data SEO and growth engagement (15 May to 14 November 2026).

Start with the [knowledge base](knowledge-base/README.md). It is the single source of truth for who the client is, what was agreed, and what is in flight.

## Folder layout

| Folder | What it holds |
| :-- | :-- |
| [knowledge-base/](knowledge-base/README.md) | The single source of truth: client profile, engagement terms, strategy, compliance, comms log, decisions, contacts, FAQs, and action items. |
| [proposal/](proposal/) | The signed proposal and scope of work. |
| [strategy/](strategy/) | The published strategy document (HTML source). |
| [competitors/](competitors/) | Per-competitor analysis. Each competitor has `code/` (analysis scripts), `data/` (raw and processed), and `presentation/` (the deck). `_template/` is the starting point for a new competitor. |
| [brand/](brand/) | Brand guidelines and kit (HTML source). |
| [communication/](communication/) | Email thread log and draft replies. |
| [meetings/](meetings/) | Meeting notes and transcripts. |
| [reference/](reference/) | Supporting reference material: meta tags, and `screenshots/` of the live site. |
| [tasks/](tasks/) | Work status tracking. |
| [public/](public/) | The published website that deploys to Vercel. See below. |

## Source vs published output

- The working source for each page lives in its own root folder: `strategy/`, `brand/`, and the per-competitor `presentation/` folders under `competitors/`.
- [public/hellomello/](public/hellomello/) is the published site that Vercel deploys, with the landing `index.html`, plus `brand/`, `competitors/`, and `strategy/` sections. Treat it as the deploy output. When a source page changes, copy the updated build into the matching path under `public/hellomello/`.
- There is no `dist/` folder. It was a stale build artefact and has been removed. Anything generated for deployment goes under `public/`.

## Conventions

- Prose is written in plain Australian English, simple and conversational, with no em dashes. See the writing-style guidance in `.github/`.
- All client content must stay inside TGA and AHPRA boundaries. See [knowledge-base/04-compliance-tga-ahpra.md](knowledge-base/04-compliance-tga-ahpra.md).
- Rod holds final sign-off on all content and website changes.