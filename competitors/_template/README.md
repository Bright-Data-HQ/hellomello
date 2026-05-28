# Competitor presentation template

A single self-contained HTML deck (10 slides) used to present each competitor to the Hellomello team.

## How to use

1. Copy `presentation.html` from this folder into the competitor's folder, e.g.
   `competitors/herbly/presentation.html`.
2. Open it and edit the `window.COMP = { ... }` block near the top — that is the only thing you need to change. All ten slides re-render from that object.
3. Drop screenshots into the same folder and reference their filenames in `brand.screenshots` (up to 6 show on slide 3).
4. Open the file in a browser. Use:
   - `→` / `←` or the toolbar to navigate
   - `P` (or the **Present** button) to enter full-screen present mode
   - the **PDF** button (or browser print) to export a 16:9 PDF

## Slide order

1. Cover — brand, domain, verdict
2. Company overview — who they are + legal posture
3. Brand & visual identity — screenshots
4. SEO snapshot — KPIs and narrative
5. Top pages — table
6. Keyword strategy — table
7. Backlink profile — KPIs and narrative
8. SWOT vs Hellomello
9. Strategic takeaways — three moves
10. Verdict

## Notes

- Self-contained: one HTML file, no build step, no dependencies beyond Google Fonts.
- Designed for 1280×720 (16:9). Prints to PDF at the same ratio.
- See `competitors/alternaleaf/presentation.html` for a fully populated example.
