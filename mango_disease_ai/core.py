"""
mango_disease_ai.core
---------------------
Core analysis function: mango validation + disease classification +
Grad-CAM heatmap generation.

All imports are self-contained within this package.
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Union

# ── Model weight path ────────────────────────────────────────────────────────
# When installed via `pip install mango-disease-ai`, the .pt file lives
# right here alongside this module inside the installed package directory.
_PKG_DIR = Path(__file__).parent
_MODEL_PT = _PKG_DIR / "MAF-Net_final_weights.pt"

# Allow override via environment variable (useful in Docker / HF Spaces)
_MODEL_PATH = Path(os.environ.get("MANGO_MODEL_PATH", str(_MODEL_PT)))


def analyze(
    image: Union[str, "os.PathLike", "PIL.Image.Image", bytes, io.IOBase],  # noqa: F821
    *,
    include_gradcam: bool = True,
) -> dict:
    """
    Analyze a mango image for disease.

    Parameters
    ----------
    image : str | Path | PIL.Image | bytes | file-like
        The mango image to analyze. Accepts:
        - A file path (str or Path)
        - A PIL.Image.Image object
        - Raw image bytes
        - A file-like object  (e.g. ``open("img.jpg", "rb")``)

    include_gradcam : bool, optional
        Whether to generate the Grad-CAM heatmap overlay.
        Default ``True``. Set ``False`` for ~2× faster inference
        when you only need the classification result.

    Returns
    -------
    dict with keys:

    ``is_mango`` : bool
        True if the image is detected as a mango (CLIP validation).
    ``mango_confidence`` : float
        CLIP confidence score (0.0 – 1.0).
    ``predicted_class`` : str | None
        Top predicted disease class, one of:
        "Anthracnose", "Bacterial Canker", "Healthy",
        "Powdery Mildew", "Scab", "Sooty Mould", "Stem End Rot".
        ``None`` when ``is_mango`` is ``False``.
    ``confidence`` : float | None
        Confidence of the top prediction (0.0 – 1.0).
    ``all_scores`` : list[dict]
        All 7 class scores sorted descending.
        Each entry: ``{"class": str, "score": float}``.
    ``disease_info`` : dict
        Scientific name, description, symptoms, remedies.
    ``gradcam_base64`` : str | None
        Base64-encoded PNG of the Grad-CAM heatmap overlay.
        ``None`` when ``include_gradcam=False`` or ``is_mango=False``.
    ``original_base64`` : str | None
        Base64-encoded PNG of the resized input image.
        ``None`` when ``include_gradcam=False`` or ``is_mango=False``.

    Raises
    ------
    FileNotFoundError
        If the model weights file cannot be found.
    TypeError
        If ``image`` is an unsupported type.

    Examples
    --------
    >>> from mango_disease_ai import analyze
    >>> result = analyze("leaf.jpg")
    >>> print(result["predicted_class"], f"{result['confidence']:.1%}")
    Anthracnose 93.1%

    >>> # Fast mode — skip Grad-CAM for speed
    >>> result = analyze("leaf.jpg", include_gradcam=False)
    """
    from PIL import Image as _PILImage
    from PIL import ImageOps as _PILImageOps

    # ── Validate model weights (clear error for missing / LFS placeholder) ───
    from mango_disease_ai.model import resolve_model_path
    resolve_model_path()

    # ── Convert input to PIL Image ───────────────────────────────────────────
    def _upright(img):
        # Phone photos: apply the EXIF rotation, as in training
        return _PILImageOps.exif_transpose(img).convert("RGB")

    if isinstance(image, _PILImage.Image):
        pil_img = image.convert("RGB")
    elif isinstance(image, (str, os.PathLike)):
        pil_img = _upright(_PILImage.open(image))
    elif isinstance(image, bytes):
        pil_img = _upright(_PILImage.open(io.BytesIO(image)))
    elif hasattr(image, "read"):
        pil_img = _upright(_PILImage.open(image))
    else:
        raise TypeError(
            f"Unsupported image type: {type(image).__name__}. "
            "Pass a file path (str/Path), PIL.Image, bytes, or file-like object."
        )

    # ── Import internal package modules (lazy — avoids slow startup) ─────────
    from mango_disease_ai.inference import is_mango, classify_image, generate_gradcam
    from mango_disease_ai.model import DISEASE_INFO

    # ── Step 1: Mango validation via CLIP ────────────────────────────────────
    mango_ok, mango_conf = is_mango(pil_img)

    if not mango_ok:
        return {
            "is_mango": False,
            "mango_confidence": mango_conf,
            "predicted_class": None,
            "confidence": None,
            "all_scores": [],
            "disease_info": {},
            "gradcam_base64": None,
            "original_base64": None,
            "marked_base64": None,
            "affected_percent": None,
        }

    # ── Step 2: Disease classification ───────────────────────────────────────
    classification = classify_image(pil_img)
    pred_class = classification["predicted_class"]

    # Second safety check: both models unsure -> most likely not a mango photo
    from mango_disease_ai.inference import UNSURE_MANGO_CONFIDENCE, UNSURE_MODEL_CONFIDENCE
    if classification["confidence"] < UNSURE_MODEL_CONFIDENCE and mango_conf < UNSURE_MANGO_CONFIDENCE:
        return {
            "is_mango": False,
            "mango_confidence": mango_conf,
            "predicted_class": None,
            "confidence": None,
            "all_scores": [],
            "disease_info": {},
            "gradcam_base64": None,
            "original_base64": None,
            "marked_base64": None,
            "affected_percent": None,
        }
    disease_info = DISEASE_INFO.get(pred_class, {})

    # ── Step 3: Grad-CAM heatmap ─────────────────────────────────────────────
    gradcam_b64 = None
    original_b64 = None
    marked_b64 = None
    affected_percent = None

    if include_gradcam:
        gradcam_result = generate_gradcam(pil_img)
        gradcam_b64 = gradcam_result["heatmap_b64"]
        original_b64 = gradcam_result["original_b64"]
        # A healthy mango has no diseased area to outline.
        if pred_class != "Healthy":
            marked_b64 = gradcam_result["marked_b64"]
            affected_percent = gradcam_result["affected_percent"]

    return {
        "is_mango": True,
        "mango_confidence": mango_conf,
        "predicted_class": pred_class,
        "confidence": classification["confidence"],
        "all_scores": classification["all_scores"],
        "disease_info": disease_info,
        "gradcam_base64": gradcam_b64,
        "original_base64": original_b64,
        "marked_base64": marked_b64,
        "affected_percent": affected_percent,
    }
