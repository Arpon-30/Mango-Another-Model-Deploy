"""
Project-root shortcut to the MAF-Net inference code (mango check, classification,
Grad-CAM). The real implementation lives in ``mango_disease_ai/inference.py``;
this file only re-exports it so older scripts that run ``from inference import ...``
keep working.
"""

from mango_disease_ai.inference import *  # noqa: F401,F403
from mango_disease_ai.inference import (  # noqa: F401
    classify_image,
    generate_gradcam,
    is_mango,
    preprocess,
)
