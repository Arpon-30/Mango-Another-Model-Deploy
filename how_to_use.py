"""
HOW TO USE mango-disease-ai
=============================
Run this file: python how_to_use.py

Make sure you have a mango image file ready.
Change "your_mango_image.jpg" to your actual image path.
"""

# ── STEP 1: Import the package ───────────────────────────────────────────────
from mango_disease_ai import analyze, generate_pdf

print("=" * 60)
print("  mango-disease-ai — Quick Demo")
print("=" * 60)

# ── STEP 2: Analyze a mango image ────────────────────────────────────────────
# Change this path to your actual mango image
IMAGE_PATH = "test_mango.jpg"   # ← put your image path here

print(f"\n📸 Analyzing image: {IMAGE_PATH}")
print("   (This may take 10–30 seconds on first run — loading AI models...)\n")

result = analyze(IMAGE_PATH)

# ── STEP 3: Read the results ─────────────────────────────────────────────────
if not result["is_mango"]:
    print("❌ This image does not look like a mango!")
    print(f"   Mango confidence: {result['mango_confidence']:.1%}")
else:
    print(f"✅ Mango detected! (confidence: {result['mango_confidence']:.1%})")
    print()
    print(f"🔬 Disease detected : {result['predicted_class']}")
    print(f"📊 Confidence       : {result['confidence']:.1%}")
    print()

    # All 7 scores
    print("📋 All class scores:")
    for s in result["all_scores"]:
        bar = "█" * int(s["score"] * 30)
        print(f"   {s['class']:20s} {s['score']:.1%}  {bar}")

    # Disease info
    info = result["disease_info"]
    print(f"\n🌿 Scientific name: {info.get('scientific_name', 'N/A')}")
    print(f"\n📖 Description:\n   {info.get('description', '')[:120]}...")

    print(f"\n⚠️  Symptoms:")
    for symptom in info.get("symptoms", []):
        print(f"   • {symptom}")

    print(f"\n💊 Recommended treatment:")
    for remedy in info.get("remedies", []):
        print(f"   ✓ {remedy}")

    # Save heatmap image
    if result["gradcam_base64"]:
        import base64
        heatmap_bytes = base64.b64decode(result["gradcam_base64"])
        with open("heatmap_output.png", "wb") as f:
            f.write(heatmap_bytes)
        print(f"\n🌡️  Grad-CAM heatmap saved → heatmap_output.png")

    # ── STEP 4: Generate PDF Report ───────────────────────────────────────────
    print("\n📄 Generating PDF report...")
    pdf_bytes = generate_pdf(result, user_name="Dr. Arpon")
    with open("mango_diagnosis_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ PDF saved → mango_diagnosis_report.pdf")

print("\n" + "=" * 60)
print("  Done! Check the output files in this folder.")
print("=" * 60)
