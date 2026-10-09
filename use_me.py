# HOW TO USE mango-disease-ai — Step by Step Guide
# =====================================================
# Run this file to analyze a mango image
# 
# STEP 1: Open Anaconda Prompt (search "Anaconda Prompt" in Windows Start menu)
# STEP 2: Type this command and press Enter:
#          cd "E:\AIUB R&D ICCA\Updated Deploy\LastUpdatedmango"
# STEP 3: Type this command and press Enter:
#          python use_me.py
# =====================================================

from mango_disease_ai import analyze, generate_pdf

# ── CHANGE THIS LINE: put your mango image path here ──────────────────────────
IMAGE_PATH = r"E:\AIUB R&D ICCA\Amrapali Mango Diseases Dataset\Amrapali Mango Diseases Dataset\Anthracnose\Anthracnose_001.jpg"
# ──────────────────────────────────────────────────────────────────────────────

print("\nAnalyzing your mango image... please wait (30 seconds first time)...\n")

result = analyze(IMAGE_PATH)

if not result["is_mango"]:
    print("This does not look like a mango image. Please use a mango photo.")
else:
    print("------------------------------")
    print("RESULT:")
    print(f"  Disease  : {result['predicted_class']}")
    print(f"  Confidence: {result['confidence']:.1%}")
    print("------------------------------")
    print("\nAll scores:")
    for s in result["all_scores"]:
        print(f"  {s['class']:20s} : {s['score']*100:.1f}%")

    print("\nSaving heatmap image...")
    import base64
    with open("heatmap_output.png", "wb") as f:
        f.write(base64.b64decode(result["gradcam_base64"]))
    print("  Saved: heatmap_output.png")

    print("\nGenerating PDF report...")
    pdf = generate_pdf(result, user_name="Dr. Arpon")
    with open("mango_report.pdf", "wb") as f:
        f.write(pdf)
    print("  Saved: mango_report.pdf")

    print("\nDone! Open heatmap_output.png and mango_report.pdf to see results.")
