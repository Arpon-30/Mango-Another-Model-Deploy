"""
mango_disease_ai.report
-----------------------
PDF report generation for the mango-disease-ai package.
Uses the bundled report_engine module.
"""

from __future__ import annotations


def generate_pdf(result: dict, user_name: str = "User", lang: str = "en") -> bytes:
    """
    Generate a professional A4 PDF diagnosis report.

    Parameters
    ----------
    result : dict
        The dict returned by :func:`mango_disease_ai.analyze`.
        Must contain: ``predicted_class``, ``confidence``, ``all_scores``,
        ``original_base64``, ``gradcam_base64``, ``disease_info``.
    user_name : str
        Name printed on the report (e.g. researcher / farmer name).
    lang : str
        "en" (English, default) or "bn" (Bangla; needs the uharfbuzz package).

    Returns
    -------
    bytes
        Raw PDF bytes. Write to a file or send as HTTP response.

    Raises
    ------
    ValueError
        If ``result["is_mango"]`` is ``False``, or if Grad-CAM images
        are missing (re-run ``analyze()`` with ``include_gradcam=True``).

    Examples
    --------
    >>> from mango_disease_ai import analyze, generate_pdf
    >>> result = analyze("mango_leaf.jpg")
    >>> pdf_bytes = generate_pdf(result, user_name="Dr. Arpon")
    >>> open("report.pdf", "wb").write(pdf_bytes)
    """
    if not result.get("is_mango", False):
        raise ValueError(
            "Cannot generate a report: the image was not detected as a mango. "
            "Check result['is_mango'] before calling generate_pdf()."
        )

    if result.get("original_base64") is None or result.get("gradcam_base64") is None:
        raise ValueError(
            "PDF generation requires Grad-CAM images. "
            "Re-run analyze() with include_gradcam=True (default)."
        )

    # Import the bundled PDF engine (report_engine.py is inside the package)
    from mango_disease_ai.report_engine import generate_report

    classification = {
        "predicted_class": result["predicted_class"],
        "confidence": result["confidence"],
        "all_scores": result["all_scores"],
    }

    return generate_report(
        user_name=user_name,
        original_b64=result["original_base64"],
        heatmap_b64=result["gradcam_base64"],
        classification=classification,
        disease_info=result.get("disease_info", {}),
        marked_b64=result.get("marked_base64"),
        affected_percent=result.get("affected_percent"),
        lang=lang,
    )
