"""
DEVELOPER WORKFLOW — mango-disease-ai
=======================================
This is exactly how another developer uses your package in VS Code.

SETUP (only once):
  pip install mango-disease-ai

Then run this file: python developer_workflow.py
"""

# ── 1. Install (run once in VS Code terminal) ─────────────────────────────
# pip install mango-disease-ai

# ── 2. Import ─────────────────────────────────────────────────────────────
from mango_disease_ai import analyze, generate_pdf
import base64
import os

# ── 3. Give your image ────────────────────────────────────────────────────
# Option A: Use a file path
IMAGE_PATH = r"E:\AIUB R&D ICCA\Amrapali Mango Diseases Dataset\Amrapali Mango Diseases Dataset\Anthracnose\Anthracnose_001.jpg"

# Option B: Use bytes (e.g., from a web upload / Flask request)
# with open("mango.jpg", "rb") as f:
#     image_bytes = f.read()
# result = analyze(image_bytes)

# Option C: Use PIL Image
# from PIL import Image
# pil_img = Image.open("mango.jpg")
# result = analyze(pil_img)

# ── 4. Run analysis ───────────────────────────────────────────────────────
print("Step 1: Analyzing image...")
result = analyze(IMAGE_PATH)

# ── 5. Check if it's a mango ──────────────────────────────────────────────
if not result["is_mango"]:
    print(f"Rejected: not a mango (confidence={result['mango_confidence']:.1%})")
    exit()

# ── 6. Read results ───────────────────────────────────────────────────────
print("Step 2: Results ready!\n")
print(f"  Disease    : {result['predicted_class']}")
print(f"  Confidence : {result['confidence']:.1%}")
print(f"  Is mango   : {result['is_mango']}")
print()

print("  All disease scores:")
for score in result["all_scores"]:
    print(f"    {score['class']:20s}  {score['score']*100:.2f}%")
print()

disease = result["disease_info"]
print(f"  Scientific name: {disease['scientific_name']}")
print(f"  Description    : {disease['description'][:80]}...")
print(f"  Symptoms:")
for s in disease["symptoms"]:
    print(f"    - {s}")
print(f"  Remedies:")
for r in disease["remedies"]:
    print(f"    + {r}")
print()

# ── 7. Save Grad-CAM heatmap image ───────────────────────────────────────
print("Step 3: Saving Grad-CAM heatmap...")
heatmap_bytes = base64.b64decode(result["gradcam_base64"])
with open("gradcam_heatmap.png", "wb") as f:
    f.write(heatmap_bytes)

original_bytes = base64.b64decode(result["original_base64"])
with open("original_resized.png", "wb") as f:
    f.write(original_bytes)

print("  Saved: gradcam_heatmap.png")
print("  Saved: original_resized.png")
print()

# ── 8. Generate PDF report ───────────────────────────────────────────────
print("Step 4: Generating PDF report...")
pdf_bytes = generate_pdf(result, user_name="Dr. Arpon")

with open("diagnosis_report.pdf", "wb") as f:
    f.write(pdf_bytes)

print("  Saved: diagnosis_report.pdf")
print()
print("=" * 50)
print("WORKFLOW COMPLETE!")
print("=" * 50)
print()
print("Output files in your current folder:")
print("  gradcam_heatmap.png   <- AI heatmap visualization")
print("  original_resized.png  <- original image (224x224)")
print("  diagnosis_report.pdf  <- full PDF report")
