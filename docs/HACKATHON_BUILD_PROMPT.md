# AmropaliNet - Hackathon Build Prompt

Use this prompt (as-is) with any AI coding assistant or give it to a team member to rebuild or extend the frontend. It is the single source of truth for the hackathon version.

---

## The prompt

> You are a senior product designer and frontend engineer. Rebuild the web frontend of **AmropaliNet**, an AI system that detects 7 diseases of the Amrapali (Amropali) mango from a photo, so it can be showcased at **Hack for Humanity | Hack to Protect the Environment 🌱** ("Ideas for Today, a Greener Tomorrow").
>
> **Who uses it:** farmers and ordinary people in Bangladesh, mostly on low-end Android phones, often outdoors in sunlight. Many read Bangla first. Judges will see it on a laptop and a projector.
>
> **Story to tell:** a sick mango tree is not one tree's problem - disease spreads through the whole garden, farmers then spray the whole orchard "just in case", harvests are wasted and soil, water and pollinators suffer. AmropaliNet catches disease early from one photo, so the farmer treats only what is sick. That is the environmental solution.
>
> **Stack (keep it):** FastAPI backend (already exists: `POST /api/analyze`, `POST /api/report`, `GET /api/diseases`, `GET /api/health`). Frontend in plain HTML + CSS + vanilla JS served by FastAPI from `templates/index.html` and `static/`. No build step, no framework, no heavy libraries. Only Google Fonts (Poppins + Hind Siliguri) as an external request.
>
> **Look & feel**
> - Light theme by default, colours from the orchard: leaf green, fresh lime, mango yellow/orange, cream/light white, a touch of soil brown. No dark, neon or "hacker" look by default.
> - A dark mode exists, but it is a deep forest green, not black.
> - Rounded, friendly cards, big touch targets (min 48px), high contrast text (WCAG AA).
> - Every button has a clear, different colour for its role: primary (green), camera/action (mango), secondary (outline), danger (soft red). Visible focus ring.
>
> **Header:** sticky; logo; nav links to every section (Home, Detect, Garden Impact, Diseases, Environment, How it works); a **language toggle (English / বাংলা)** and a **theme toggle (Light / Dark)**, both remembered in `localStorage`. On phones the nav collapses into a menu.
>
> **Always-visible heritage ticker** (thin animated strip above the header): 1-2 lines about Amrapali as Bangladesh's beloved mango and its short history, in the selected language.
>
> **Sections (all connected, short text, no filler):**
> 1. **Hero** - one clear headline, one sentence, two big buttons: "Scan with camera" and "Upload a photo". An animated SVG scene: sun, drifting clouds, a swaying mango tree with bobbing mangoes, a Bangladeshi farmer, falling leaves. Hackathon badge.
> 2. **Detect** - 3 simple steps. Big upload card with camera capture (`capture="environment"`), gallery pick, and drag-and-drop on desktop. Resize photos in the browser before upload (phones take 5-12 MB photos; limit is 10 MB). Friendly loading animation. Result in plain language first ("Your mango looks healthy" / "This looks like Anthracnose"), colour-coded, then: what to do now, symptoms, all scores and Grad-CAM heatmap for experts, and the PDF report form.
> 3. **Garden Impact** - pick a disease and watch an animated row of trees show how it spreads through the garden (one tree - neighbours - whole garden). Show which parts are affected, how it spreads, early signs to look for and the risk to the garden.
> 4. **Disease Encyclopedia** - 7 cards with filter chips (leaf / flower / fruit / branch). Clicking a card opens an animated detail panel (bottom sheet on phones) with symptoms, spread, treatment and prevention.
> 5. **Environment** - why this protects the planet: targeted spraying, less fruit waste, healthier soil and pollinators, safer farmer income; linked to UN SDGs 2, 12, 13 and 15. No invented statistics.
> 6. **How it works** - Photo - mango check (CLIP) - AA-ENet - heatmap - advice + PDF. Credits.
> 7. **Footer** - brand, quick links, credits, disclaimer, hackathon line.
>
> **Language:** every visible string (including disease data, error messages and numbers) must switch between English and Bangla instantly without reload. Set `<html lang>`. Use Bangla digits in Bangla mode.
>
> **Writing rules:** short sentences, farmer-friendly words, no jargon in the first layer. Never use a long dash (— or --); use a single hyphen "-". No emoji walls.
>
> **Motion:** gentle, nature-themed (sway, float, drift, grow). Scroll reveal for sections. Everything respects `prefers-reduced-motion`. No motion that blocks reading.
>
> **Mobile first:** works from 320px wide, no horizontal scroll, floating "Scan" button on phones, camera opens directly.
>
> **Quality bar:** no console errors, all API errors mapped to friendly localised messages (400 bad file, 422 not a mango, 500 server, network offline), keyboard accessible (Esc closes panels, focus trapped in modal), `?demo=1` shows a clearly labelled sample result so the UI can be presented without the model.

---

## Tools, plugins and skills used for this build

| Need | What to use | Why |
|---|---|---|
| Backend + serving the page | FastAPI `StaticFiles` + `FileResponse` | Already in `api/requirements.txt`; zero new dependencies |
| Fonts | Google Fonts: Poppins, Hind Siliguri | Clean Latin + excellent Bangla rendering |
| Illustrations & animation | Inline SVG + CSS keyframes | No image downloads, crisp on any screen, tiny |
| Camera | `<input type="file" accept="image/*" capture="environment">` | Opens the rear camera on every modern phone without permissions code |
| Image resize | `<canvas>` + `toBlob` | Keeps uploads small and under the 10 MB limit |
| Testing | Playwright (Chromium) with the API mocked | Screenshots at phone and desktop width in both languages and themes |
| Container | Existing `Dockerfile` (python:3.10-slim, port 7860) | Hugging Face Spaces compatible |

Nothing else (no React, no Tailwind, no npm build) is required.
