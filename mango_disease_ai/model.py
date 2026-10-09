"""
AA-ENet: Lightweight CNN–Transformer hybrid for Amropali Mango Leaf Disease Classification.

Architecture: EfficientNet-B0 backbone + CBAM attention + 1-layer Transformer encoder.
Trained on 7 classes (500 images each): Anthracnose, Bacterial Canker, Healthy,
Powdery Mildew, Scab, Sooty Mould, Stem End Rot.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm

# ── Constants ────────────────────────────────────────────────────────────────
IMG_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

CLASSES = [
    "Anthracnose",
    "Bacterial Canker",
    "Healthy",
    "Powdery Mildew",
    "Scab",
    "Sooty Mould",
    "Stem End Rot",
]
NUM_CLASSES = len(CLASSES)

MODEL_FILENAME = "AA-ENet_proposed.pt"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)


class ModelNotReadyError(RuntimeError):
    """The AA-ENet weights file is missing or is only a Git LFS placeholder."""


def _is_lfs_pointer(path: str) -> bool:
    """A Git LFS placeholder is a ~130-byte text file instead of the real weights."""
    try:
        if os.path.getsize(path) > 1024:
            return False
        with open(path, "rb") as fh:
            return fh.read(40).startswith(b"version https://git-lfs")
    except OSError:
        return False


def resolve_model_path() -> str:
    """
    Find the real AA-ENet weights. Checks, in order: $MANGO_MODEL_PATH,
    this module's folder, the project root and the current folder.
    Skips Git LFS placeholders (what a GitHub ZIP download contains).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.environ.get("MANGO_MODEL_PATH"),
        os.path.join(here, MODEL_FILENAME),
        os.path.join(here, "mango_disease_ai", MODEL_FILENAME),
        os.path.join(os.path.dirname(here), MODEL_FILENAME),
        os.path.join(os.getcwd(), MODEL_FILENAME),
    ]
    placeholders = []
    for path in candidates:
        if not path or not os.path.isfile(path):
            continue
        if _is_lfs_pointer(path):
            placeholders.append(path)
            continue
        return path
    if placeholders:
        raise ModelNotReadyError(
            f"{MODEL_FILENAME} is only a Git LFS placeholder (a few bytes, not the real 18 MB model): "
            f"{placeholders[0]}. Run `git lfs pull`, or download the real file from GitHub and "
            "put it in the project folder, then restart."
        )
    raise ModelNotReadyError(
        f"{MODEL_FILENAME} was not found. Put the 18 MB model file in the mango_disease_ai "
        "folder (or next to run.py) and restart."
    )
MANGO_DETECTOR_MODEL_ID = "openai/clip-vit-base-patch32"

# ── Disease information database ─────────────────────────────────────────────
DISEASE_INFO = {
    "Anthracnose": {
        "scientific_name": "Colletotrichum gloeosporioides",
        "description": "A major fungal disease affecting mango leaves, flowers, and fruits. It causes significant post-harvest losses and can devastate entire crops if not managed promptly.",
        "symptoms": [
            "Dark brown to black irregular spots on leaves",
            "Water-soaked lesions that enlarge rapidly",
            "Premature leaf drop and defoliation",
            "Blossom blight and twig dieback",
            "Fruit rot that remains latent until ripening",
        ],
        "remedies": [
            "Apply copper-based fungicides (Bordeaux mixture)",
            "Use systemic fungicides like Carbendazim or Mancozeb",
            "Prune and destroy infected branches and leaves to improve ventilation",
            "Post-harvest: Hot water treatment (50-55°C for 5-10 minutes) to reduce decay",
            "Maintain good orchard hygiene and spacing",
        ],
    },
    "Bacterial Canker": {
        "scientific_name": "Xanthomonas campestris pv. mangiferaeindicae",
        "description": "A serious bacterial infection that affects all above-ground parts of the mango tree. It causes severe economic losses especially in commercial orchards during wet seasons.",
        "symptoms": [
            "Water-soaked angular lesions on leaves",
            "Yellow halo surrounding dark lesions",
            "Cracking and gummosis on twigs and branches",
            "Lesions may ooze a yellow bacterial exudate",
            "Severe cases lead to defoliation and fruit drop",
        ],
        "remedies": [
            "Spray copper oxychloride (0.3%) at 15-day intervals",
            "Apply Streptomycin sulfate (500 ppm) sprays",
            "Prune and burn infected plant materials",
            "Avoid overhead irrigation to reduce humidity",
            "Apply copper-based bactericides during the rainy season",
        ],
    },
    "Healthy": {
        "scientific_name": "Mangifera indica (Normal)",
        "description": "The mango leaf shows no signs of disease or infection. The plant appears to be in excellent health with normal leaf coloration, texture, and structure.",
        "symptoms": [
            "Vibrant green leaf coloration",
            "Smooth and glossy leaf surface",
            "No spots, lesions, or discoloration",
            "Normal leaf shape and size",
            "Healthy growth pattern",
        ],
        "remedies": [
            "Continue regular monitoring of the plant",
            "Maintain balanced fertilization schedule",
            "Ensure proper irrigation practices",
            "Keep orchard clean and well-maintained",
            "Monitor for early signs of pest or disease",
        ],
    },
    "Powdery Mildew": {
        "scientific_name": "Oidium mangiferae",
        "description": "A common fungal disease that appears as a white powdery coating on mango leaves, flowers, and young fruits. It thrives in dry weather with cool nights and warm days.",
        "symptoms": [
            "White powdery coating on leaf surfaces",
            "Affected leaves curl and distort",
            "Flower panicles covered in white powder",
            "Premature flower and fruit drop",
            "Reduced fruit set and yield",
        ],
        "remedies": [
            "Spray wettable sulfur (0.2%) or Karathane",
            "Apply Triadimefon (0.1%) fungicide",
            "Use sulfur-based fungicides during the dry season",
            "Ensure good orchard ventilation through proper pruning",
            "Apply fungicides starting at the early flowering stage",
        ],
    },
    "Scab": {
        "scientific_name": "Elsinoë mangiferae",
        "description": "A fungal disease causing rough, corky, raised spots on mango leaves, twigs, and fruits. It significantly reduces the market value of affected fruits even when severity is moderate.",
        "symptoms": [
            "Dark brown to gray corky scab lesions",
            "Raised, rough-textured spots on leaves",
            "Distortion of young leaves and shoots",
            "Small raised grey-to-brownish lesions on fruit",
            "Leaves may become deformed or crinkled",
        ],
        "remedies": [
            "Apply Zineb or Maneb fungicides",
            "Spray Copper oxychloride at 15-day intervals",
            "Remove and destroy dead leaves and twigs",
            "Apply copper-based fungicides from flower bud emergence",
            "Continue treatment until the fruit reaches half size",
        ],
    },
    "Sooty Mould": {
        "scientific_name": "Capnodium mangiferae",
        "description": "A secondary fungal disease that grows on honeydew excreted by sap-sucking insects. While not directly infecting plant tissue, it blocks sunlight and reduces photosynthesis significantly.",
        "symptoms": [
            "Black sooty coating covering leaf surfaces",
            "Coating easily wiped off revealing green leaf",
            "Presence of scale insects or aphids nearby",
            "Reduced photosynthesis and plant vigor",
            "Black velvety coating on twigs and fruits",
        ],
        "remedies": [
            "Control the sap-sucking insects first (use insecticides or neem oil)",
            "Spray starch solution to remove sooty coating",
            "Prune heavily infected, dense branches to increase light",
            "Apply systemic insecticides to eliminate hoppers and mealybugs",
            "Maintain good air circulation in the orchard",
        ],
    },
    "Stem End Rot": {
        "scientific_name": "Lasiodiplodia theobromae",
        "description": "A devastating post-harvest fungal disease that begins at the stem end of harvested mango fruits. It can cause up to 60% post-harvest losses if proper handling and treatment protocols are not followed.",
        "symptoms": [
            "Dark brown to black rotting starting at stem end",
            "Soft, water-soaked lesion spreading rapidly",
            "White to gray fungal growth on rotted area",
            "Pulp becomes soft and brown",
            "Rapid deterioration after harvest",
        ],
        "remedies": [
            "Hot water treatment (52°C for 5 min) post-harvest",
            "Apply Prochloraz (0.05%) fungicide dip",
            "Avoid harvesting immature fruit and prevent mechanical injury",
            "Pre-harvest sprays of carbendazim to reduce incidence",
            "Post-harvest hot water dips with or without fungicides",
        ],
    },
}


# ── CBAM: Convolutional Block Attention Module ───────────────────────────────
class CBAM(nn.Module):
    """Channel + Spatial attention (Woo et al., 2018)."""

    def __init__(self, ch, r=8):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(ch, ch // r),
            nn.ReLU(inplace=True),
            nn.Linear(ch // r, ch),
        )
        self.conv = nn.Conv2d(2, 1, 7, padding=3, bias=False)

    def forward(self, x):
        b, c, _, _ = x.shape
        avg = F.adaptive_avg_pool2d(x, 1).view(b, c)
        mx = F.adaptive_max_pool2d(x, 1).view(b, c)
        ca = torch.sigmoid(self.mlp(avg) + self.mlp(mx)).view(b, c, 1, 1)
        x = x * ca
        sa = torch.cat(
            [x.mean(1, keepdim=True), x.max(1, keepdim=True)[0]], dim=1
        )
        sa = torch.sigmoid(self.conv(sa))
        return x * sa


# ── AA-ENet: Proposed lightweight hybrid ─────────────────────────────────────
class AAENet(nn.Module):
    """
    EfficientNet-B0 backbone  →  1×1 conv reduce  →  CBAM  →  Transformer
    encoder (1 layer) with [CLS] token  →  GAP + CLS concat  →  classifier.
    """

    def __init__(
        self,
        num_classes=NUM_CLASSES,
        dropout=0.3,
        embed=192,
        use_cbam=True,
        use_transformer=True,
    ):
        super().__init__()
        # Backbone — pretrained=False at load time; weights come from .pt file
        self.backbone = timm.create_model(
            "efficientnet_b0", pretrained=False, num_classes=0, global_pool=""
        )
        feat_ch = self.backbone.num_features  # 1280

        self.reduce = nn.Sequential(
            nn.Conv2d(feat_ch, embed, 1, bias=False),
            nn.BatchNorm2d(embed),
            nn.ReLU(inplace=True),
        )

        self.use_cbam = use_cbam
        self.cbam = CBAM(embed) if use_cbam else nn.Identity()

        self.use_transformer = use_transformer
        if use_transformer:
            self.cls = nn.Parameter(torch.zeros(1, 1, embed))
            self.pos = nn.Parameter(torch.zeros(1, 50, embed))  # 49 + cls
            enc = nn.TransformerEncoderLayer(
                d_model=embed,
                nhead=4,
                dim_feedforward=embed * 2,
                dropout=dropout,
                batch_first=True,
                activation="gelu",
            )
            self.transformer = nn.TransformerEncoder(enc, num_layers=1)

        fuse_dim = embed * 2 if use_transformer else embed
        self.drop = nn.Dropout(dropout)
        self.head = nn.Linear(fuse_dim, num_classes)

    def forward(self, x):
        x = self.backbone(x)  # [B, 1280, 7, 7]
        x = self.reduce(x)  # [B, embed, 7, 7]
        x = self.cbam(x)
        gap = F.adaptive_avg_pool2d(x, 1).flatten(1)  # [B, embed]
        if self.use_transformer:
            b = x.size(0)
            tok = x.flatten(2).transpose(1, 2)  # [B, 49, embed]
            cls = self.cls.expand(b, -1, -1)
            tok = torch.cat([cls, tok], dim=1) + self.pos[:, : tok.size(1) + 1]
            tok = self.transformer(tok)
            feat = torch.cat([gap, tok[:, 0]], dim=1)
        else:
            feat = gap
        return self.head(self.drop(feat))


# ── Model loader ─────────────────────────────────────────────────────────────
_cached_model = None
_cached_mango_detector = None


def load_model(device="cpu"):
    """Load AA-ENet with trained weights (singleton, cached)."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    model = AAENet(NUM_CLASSES, dropout=0.276633)
    state = torch.load(resolve_model_path(), map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.to(device).eval()
    _cached_model = model
    return model


# Low-memory mode (e.g. Streamlit Community Cloud, ~1 GB RAM): set MANGO_LOW_MEMORY=1.
# The CLIP text encoder runs once for the fixed labels and is then freed, and the
# vision encoder is kept in bfloat16 - about 175 MB instead of about 600 MB.
LOW_MEMORY = os.environ.get("MANGO_LOW_MEMORY", "0") == "1"
CLIP_LOGIT_SCALE = 100.0  # exp(logit_scale) of the trained openai/clip-vit-base-patch32


class LightClip:
    """Zero-shot CLIP with precomputed label embeddings and a bfloat16 vision encoder."""

    def __init__(self, processor, labels, model_id=None, device="cpu"):
        import gc

        from transformers import CLIPTextModelWithProjection, CLIPVisionModelWithProjection

        model_id = model_id or MANGO_DETECTOR_MODEL_ID
        self.processor = processor
        self.device = device

        # 1) Text side once: embeddings for the fixed labels, then free the text model.
        text_model = CLIPTextModelWithProjection.from_pretrained(model_id, torch_dtype=torch.bfloat16).eval()
        tokens = processor.tokenizer(list(labels), padding=True, return_tensors="pt")
        with torch.no_grad():
            text = text_model(**tokens).text_embeds.float()
        self.text_embeds = text / text.norm(dim=-1, keepdim=True)
        del text_model
        gc.collect()

        # 2) Vision side stays loaded, in bfloat16.
        self.vision = CLIPVisionModelWithProjection.from_pretrained(model_id, torch_dtype=torch.bfloat16)
        self.vision.to(device).eval()

    def probs(self, pil_img):
        pixels = self.processor(images=pil_img, return_tensors="pt")["pixel_values"].to(torch.bfloat16)
        with torch.no_grad():
            image = self.vision(pixel_values=pixels.to(self.device)).image_embeds.float()
        image = image / image.norm(dim=-1, keepdim=True)
        return torch.softmax(CLIP_LOGIT_SCALE * image @ self.text_embeds.T, dim=-1).squeeze(0)


def load_mango_detector(device="cpu"):
    """Load CLIP (openai/clip-vit-base-patch32) for zero-shot mango detection."""
    global _cached_mango_detector
    if _cached_mango_detector is not None:
        return _cached_mango_detector

    from transformers import CLIPProcessor

    processor = CLIPProcessor.from_pretrained(MANGO_DETECTOR_MODEL_ID)
    if LOW_MEMORY:
        try:
            from mango_disease_ai.inference import MANGO_LABELS
        except ImportError:  # running from the project root copy
            from inference import MANGO_LABELS
        model = LightClip(processor, MANGO_LABELS, device=device)
    else:
        from transformers import CLIPModel

        model = CLIPModel.from_pretrained(MANGO_DETECTOR_MODEL_ID)
        model.to(device).eval()
    _cached_mango_detector = (model, processor)
    return _cached_mango_detector
