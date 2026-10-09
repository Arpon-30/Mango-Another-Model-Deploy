# mango-disease-ai 🥭

> AI-powered Amrapali mango disease detection - reject non-mango photos, classify 7 diseases, mark the affected area with Grad-CAM, and create PDF reports in English or Bangla.

[![PyPI version](https://badge.fury.io/py/mango-disease-ai.svg)](https://pypi.org/project/mango-disease-ai/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

`mango-disease-ai` is the engine behind **AmropaliNet**, a web app that helps Bangladeshi mango farmers detect disease from one photo. It runs the **AA-ENet** model (EfficientNet-B0 + CBAM + Transformer, trained on 3,500 Amrapali images) and ships the trained weights inside the package.

| Feature | |
|---|---|
| 🥭 Mango check | Rejects photos that are not a mango (CLIP zero-shot + a second model check) |
| 🔍 7 classes | Anthracnose, Bacterial Canker, Healthy, Powdery Mildew, Scab, Sooty Mould, Stem End Rot |
| 🔥 Grad-CAM | Heatmap of where the model looked |
| 🎯 Affected area | Likely affected area outlined on the photo, with its share of the image |
| 📄 PDF report | One page, **English or Bangla** |
| 🌐 REST API | `mango-api` starts a ready-made server with Swagger docs |

## Install

```bash
pip install mango-disease-ai            # Python library
pip install "mango-disease-ai[api]"     # + REST API server (FastAPI)
```

The first analysis downloads the CLIP mango checker (~600 MB) from Hugging Face once; later runs use the cache.

## Python quick start

```python
from mango_disease_ai import analyze, generate_pdf

result = analyze("mango.jpg")          # path, bytes, PIL.Image or file object

if not result["is_mango"]:
    print("Not a mango photo")
else:
    print(result["predicted_class"], f"{result['confidence']:.1%}")   # Anthracnose 95.4%
    print("Affected area:", result["affected_percent"], "%")          # None for Healthy
    for step in result["disease_info"]["remedies"]:
        print("-", step)

    # PDF report in English or Bangla
    open("report_en.pdf", "wb").write(generate_pdf(result, user_name="Arpon", lang="en"))
    open("report_bn.pdf", "wb").write(generate_pdf(result, user_name="আরপন", lang="bn"))
```

Fast mode (no heatmap): `analyze("mango.jpg", include_gradcam=False)`.

### Result fields

| Key | Meaning |
|---|---|
| `is_mango`, `mango_confidence` | Mango check result |
| `predicted_class`, `confidence` | Top class and its probability |
| `all_scores` | All 7 classes, highest first: `[{"class": ..., "score": ...}]` |
| `disease_info` | `scientific_name`, `description`, `symptoms`, `remedies` |
| `original_base64` | Photo (JPEG, base64, 448x448) |
| `gradcam_base64` | Grad-CAM heatmap overlay (JPEG, base64) |
| `marked_base64` | Photo with the likely affected area outlined (JPEG, base64; `None` for Healthy) |
| `affected_percent` | Share of the photo inside the outline, % (AI estimate) |

## REST API

```bash
mango-api                 # or: python -m mango_disease_ai.server  (--port 8080)
```

Open http://localhost:8000/docs to try every endpoint.

| Method | Path | What it does |
|---|---|---|
| GET | `/api/health` | Server + model status |
| GET | `/api/diseases` | Info for all 7 classes |
| POST | `/api/analyze` | `image` (+ `include_gradcam`) -> diagnosis JSON |
| POST | `/api/report` | `image`, `user_name`, `lang=en\|bn` -> PDF |

```bash
curl -F "image=@mango.jpg" http://localhost:8000/api/analyze
curl -F "image=@mango.jpg" -F "user_name=Arpon" -F "lang=bn" http://localhost:8000/api/report -o report_bn.pdf
```

```javascript
const form = new FormData();
form.append("image", fileInput.files[0]);
const res = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: form });
const data = await res.json();
if (!res.ok) console.log(data.detail.code);   // e.g. "not_mango"
else console.log(data.predicted_class, data.confidence);
```

Errors return `{"detail": {"code": ..., "message": ...}}`:
`400` bad_type / too_large / empty / bad_image / no_name / bad_lang ·
`422` not_mango (+ `mango_confidence`) ·
`503` model_missing / mango_check_unavailable / bn_pdf_unavailable ·
`500` analysis_failed / report_failed.

## What's new in 0.2.0

- Likely affected area outlined on the photo (`marked_base64`, `affected_percent`)
- PDF report in Bangla (`lang="bn"`) as well as English, with a new one-page design
- Stricter mango check (18 CLIP labels + second model check)
- Clear error codes, model status in `/api/health`, models load at server start
- Sharper 448 px images (JPEG)

## Team

AIUB Student Group - Arpon, Oni, Md. Ibtihazzaman · Supervised by Dr. Md. Saef Ullah Miah
Contact: arponamit.55@gmail.com · https://github.com/Arpon-30

For guidance only. Always consult a qualified agronomist for crop management decisions.

License: MIT. The bundled Hind Siliguri font is under the SIL Open Font License (`mango_disease_ai/fonts/OFL.txt`).
