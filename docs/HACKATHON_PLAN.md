# AmropaliNet - Hackathon Frontend Plan

## 1. What exists today (audit)

| Area | Finding | Action |
|---|---|---|
| Backend | FastAPI in `api/main.py` (used by `Dockerfile`): `/api/analyze`, `/api/report`, `/api/diseases`, `/api/health` | Keep. Serve the new frontend from it |
| Old frontend | `templates/index.html` + `static/js/main.js` call `/api/classify`, which does not exist (there is no Flask `app.py`) | Rewrite and wire to `/api/analyze` |
| Theme | Dark by default, generic "AI" look | Light orchard palette by default, forest-green dark mode |
| Language | English only | Full English / Bangla switch |
| Mobile | Upload only, no camera, big photos can exceed 10 MB | Camera capture + in-browser resize |
| Story | Only a classifier | Garden spread, environment impact, heritage |

## 2. Requirements checklist

- [x] Light, mango/agriculture colours (green, mango yellow, light white); dark mode as an option
- [x] Header with section options; every item leads to details
- [x] Light / Dark toggle, remembered
- [x] English / বাংলা toggle for all information, remembered
- [x] Environment-solution framing for Hack for Humanity | Hack to Protect the Environment
- [x] Gentle environment animations (tree, farmer, sun, clouds, leaves), not messy
- [x] Minimal, farmer-friendly
- [x] Garden section: how each disease affects the full garden + symptoms to detect
- [x] Always-visible animated 1-2 lines: Amrapali in Bangladesh and its history
- [x] No long dashes in text
- [x] Distinct, legible button colours
- [x] Friendlier upload, moved up and simplified; phone camera option
- [x] Clickable, animated Disease Encyclopedia
- [x] Smooth and optimised (no framework, inline SVG, reduced-motion support)

## 3. File plan

```
api/main.py            serve templates/index.html at "/" and mount /static
Dockerfile             copy templates/ and static/ into the image
templates/index.html   new page (plain HTML, no Jinja needed)
static/css/style.css   design tokens, light/dark, layout, animations
static/js/i18n.js      all UI strings in English and Bangla
static/js/diseases.js  7 diseases in both languages (+ parts, spread, risk, prevention)
static/js/main.js      theme, language, upload/camera, API, results, garden, encyclopedia, modal
static/img/favicon.svg mango icon
```

## 4. Build order (error-free path)

1. Backend wiring: serve page + static files from FastAPI; keep API untouched.
2. Content layer: i18n strings and bilingual disease data (single source for the UI).
3. Page structure: header, ticker, hero, detect, garden, diseases, environment, how it works, footer.
4. Styles: tokens first, then components, then animations with reduced-motion fallback.
5. Behaviour: theme + language, upload/camera/resize, analyze, results, report, garden animation, encyclopedia modal, scroll reveal, mobile menu.
6. Verify: Playwright with mocked `/api/analyze`, phone (390px) and desktop (1440px), EN/BN, light/dark; check console errors and horizontal overflow; `?demo=1` flow.

## 5. Demo tips for judges

- Open on a phone, tap **Scan with camera**, point at a mango leaf or fruit.
- Switch to **বাংলা** mid-demo to show the farmer-first design.
- Open **Garden Impact**, pick Anthracnose, show the spread animation, then the **Environment** section.
- Without the model weights, use `/?demo=1` to walk through a labelled sample result.
