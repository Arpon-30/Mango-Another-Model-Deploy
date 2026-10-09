"""
Project-root shortcut to the MAF-Net model code.

The real implementation lives in the ``mango_disease_ai`` package
(``mango_disease_ai/model.py``); this file only re-exports it so older
scripts that run ``from model import ...`` keep working.
"""

from mango_disease_ai.model import *  # noqa: F401,F403
from mango_disease_ai.model import (  # noqa: F401
    DISEASE_INFO,
    CLASSES,
    MAFNet,
    build_mafnet,
    load_model,
    load_mango_detector,
    resolve_model_path,
)
