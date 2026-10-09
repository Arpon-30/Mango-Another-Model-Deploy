"""
mango-disease-ai
================
AI-powered Amropali mango disease detection package.

Quick start
-----------
    from mango_disease_ai import analyze, generate_pdf

    # Analyze an image
    result = analyze("path/to/mango.jpg")
    print(result["predicted_class"])   # e.g. "Anthracnose"
    print(result["confidence"])        # e.g. 0.9312

    # Generate a PDF report
    pdf_bytes = generate_pdf(result, user_name="Dr. Rahman")
    with open("report.pdf", "wb") as f:
        f.write(pdf_bytes)
"""

from mango_disease_ai.core import analyze
from mango_disease_ai.report import generate_pdf

__version__ = "0.2.0"
__author__ = "AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman)"
__all__ = ["analyze", "generate_pdf", "server"]
