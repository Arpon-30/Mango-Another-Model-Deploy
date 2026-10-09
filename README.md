---
title: AmropaliNet
emoji: 🥭
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: AI mango disease doctor for Bangladeshi farmers (Bangla + English)
---

# AmropaliNet 🥭

**AI mango doctor for the farmers of Bangladesh - বাংলাদেশের কৃষকদের জন্য এআই আম ডাক্তার**

Take one photo of an Amrapali mango. AmropaliNet checks that it is a mango, finds the disease
(7 classes), marks the affected area with Grad-CAM and tells you what to do - in Bangla or English,
with a PDF report. Detect early, spray less, waste less.

- **Model:** AA-ENet (EfficientNet-B0 + CBAM + Transformer), trained on 3,500 Amrapali images
- **Library:** [`mango-disease-ai`](https://pypi.org/project/mango-disease-ai/) on PyPI - the website runs on its REST API
- **Docs:** `docs/AmropaliNet_Documentation.pdf` (English + Bangla) · live API docs at `/docs`

## Run locally

```bash
python -m pip install -r api/requirements.txt   # first time
python run.py                                     # opens http://localhost:8000
```

## Deploy

See [`DEPLOY.md`](DEPLOY.md) - free 24/7 on **Streamlit Community Cloud** (`streamlit_app.py`), a free public link from your laptop (Cloudflare Tunnel), or Hugging Face Spaces (PRO).

## Team

AIUB Student Group - Arpon, Oni, Md. Ibtihazzaman · Supervised by Dr. Md. Saef Ullah Miah
Contact: arponamit.55@gmail.com · https://github.com/Arpon-30

For guidance only. Always consult a qualified agronomist for crop management decisions.
