"""
MAF-Net: Lightweight Multi-scale Attention-Fusion Network for Amrapali mango
disease classification (7 classes, ~2.4 M parameters).

Architecture: ImageNet MobileNetV2 backbone (stride-8 / 16 / 32 features)
-> Multi-Scale Fusion (MSF) at stride 16 -> Coordinate Attention (CA)
-> [global stride-32 feature ++ fused feature] -> linear classifier.
Trained with ensemble knowledge distillation (training only, no inference cost).

The deployed model takes an RGB image scaled to [0, 1] at 224x224 and does its
own ImageNet normalisation (see ``Normalized``).
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm

# ── Constants ────────────────────────────────────────────────────────────────
MODEL_NAME = "MAF-Net"
IMG_SIZE = 224
CACHE_SIZE = 256  # training images were first resized to 256x256, then to 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# MAF-Net hyper-parameters (must match the training notebook)
FUSION_DIM = 128
CA_REDUCTION = 32
DROP_RATE = 0.2

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

MODEL_FILENAME = "MAF-Net_final_weights.pt"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)


class ModelNotReadyError(RuntimeError):
    """The MAF-Net weights file is missing or is only a Git LFS placeholder."""


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
    Find the real MAF-Net weights. Checks, in order: $MANGO_MODEL_PATH,
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
            f"{MODEL_FILENAME} is only a Git LFS placeholder (a few bytes, not the real 10 MB model): "
            f"{placeholders[0]}. Run `git lfs pull`, or download the real file from GitHub and "
            "put it in the project folder, then restart."
        )
    raise ModelNotReadyError(
        f"{MODEL_FILENAME} was not found. Put the 10 MB model file in the mango_disease_ai "
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


# ── Building blocks ─────────────────────────────────────────────────────────
class ConvBNAct(nn.Sequential):
    def __init__(self, cin, cout, k=1, s=1, groups=1):
        super().__init__(
            nn.Conv2d(cin, cout, k, s, k // 2, groups=groups, bias=False),
            nn.BatchNorm2d(cout),
            nn.SiLU(inplace=True),
        )


class CoordAtt(nn.Module):
    """Coordinate Attention (Hou et al., CVPR 2021)."""

    def __init__(self, ch, reduction=32):
        super().__init__()
        mid = max(8, ch // reduction)
        self.conv1 = nn.Conv2d(ch, mid, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(mid)
        self.act = nn.Hardswish()
        self.conv_h = nn.Conv2d(mid, ch, 1)
        self.conv_w = nn.Conv2d(mid, ch, 1)

    def forward(self, x):
        h, w = x.shape[-2:]
        xh = x.mean(dim=3, keepdim=True)  # B,C,H,1
        xw = x.mean(dim=2, keepdim=True).transpose(2, 3)  # B,C,W,1
        y = self.act(self.bn1(self.conv1(torch.cat([xh, xw], dim=2))))
        yh, yw = torch.split(y, [h, w], dim=2)
        a_h = torch.sigmoid(self.conv_h(yh))  # B,C,H,1
        a_w = torch.sigmoid(self.conv_w(yw.transpose(2, 3)))  # B,C,1,W
        return x * a_h * a_w


class MultiScaleFusion(nn.Module):
    """Fuses stride-8 / 16 / 32 maps at stride 16 with fast-normalised learnable weights."""

    def __init__(self, in_chs, d):
        super().__init__()
        self.lat = nn.ModuleList([ConvBNAct(c, d, 1) for c in in_chs])
        self.down = ConvBNAct(d, d, 3, 2, groups=d)  # stride 8 -> 16 (depthwise)
        self.w = nn.Parameter(torch.ones(len(in_chs)))
        self.refine = nn.Sequential(ConvBNAct(d, d, 3, 1, groups=d), ConvBNAct(d, d, 1))

    def forward(self, f8, f16, f32):
        size = f16.shape[-2:]
        p8 = self.down(self.lat[0](f8))
        if p8.shape[-2:] != size:
            p8 = F.interpolate(p8, size=size, mode="nearest")
        p16 = self.lat[1](f16)
        p32 = F.interpolate(self.lat[2](f32), size=size, mode="nearest")
        w = F.relu(self.w)
        w = w / (w.sum() + 1e-4)
        return self.refine(w[0] * p8 + w[1] * p16 + w[2] * p32)


# ── MAF-Net: proposed lightweight model ──────────────────────────────────────
class MAFNet(nn.Module):
    """
    MobileNetV2 -> MSF (stride 8/16/32 fused at 14x14) -> Coordinate Attention
    -> concat(GAP of stride-32 feature, GAP of fused feature) -> classifier.
    """

    def __init__(self, num_classes=NUM_CLASSES, use_msf=True, use_ca=True):
        super().__init__()
        # Backbone - pretrained=False at load time; weights come from the .pt file
        self.backbone = timm.create_model(
            "mobilenetv2_100", pretrained=False, num_classes=0, global_pool=""
        )
        self.use_msf, self.use_ca = use_msf, use_ca
        top = self.backbone.num_features  # 1280
        self.tap = (2, 4)  # blocks -> stride 8 (32 ch), stride 16 (96 ch)
        chs = [self.backbone.blocks[i][-1].conv_pwl.out_channels for i in self.tap]
        if use_msf:
            self.msf = MultiScaleFusion(chs + [top], FUSION_DIM)
        self.ca = CoordAtt(FUSION_DIM if use_msf else top, CA_REDUCTION) if use_ca else nn.Identity()
        self.drop = nn.Dropout(DROP_RATE)
        self.head = nn.Linear(top + (FUSION_DIM if use_msf else 0), num_classes)

    def features(self, x):
        b = self.backbone
        x = b.bn1(b.conv_stem(x))
        taps = []
        for i, blk in enumerate(b.blocks):
            x = blk(x)
            if i in self.tap:
                taps.append(x)
        return taps[0], taps[1], b.bn2(b.conv_head(x))

    def forward(self, x):
        f8, f16, f32 = self.features(x)
        if self.use_msf:
            fused = self.ca(self.msf(f8, f16, f32))
            z = torch.cat([f32.mean((2, 3)), fused.mean((2, 3))], dim=1)
        else:
            z = self.ca(f32).mean((2, 3))
        return self.head(self.drop(z))


class Normalized(nn.Module):
    """Wraps the network so it takes RGB in [0, 1] and normalises it itself."""

    def __init__(self, net, mean=IMAGENET_MEAN, std=IMAGENET_STD):
        super().__init__()
        self.net = net
        self.register_buffer("mean", torch.tensor(mean, dtype=torch.float32).view(1, 3, 1, 1))
        self.register_buffer("std", torch.tensor(std, dtype=torch.float32).view(1, 3, 1, 1))

    def forward(self, x):
        return self.net((x - self.mean) / self.std)


def build_mafnet(num_classes=NUM_CLASSES):
    """MAF-Net exactly as saved by the training notebook (state_dict keys ``net.*``)."""
    return Normalized(MAFNet(num_classes))


# ── Model loader ─────────────────────────────────────────────────────────────
_cached_model = None
_cached_mango_detector = None


def load_model(device="cpu"):
    """Load MAF-Net with trained weights (singleton, cached)."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    model = build_mafnet(NUM_CLASSES)
    state = torch.load(resolve_model_path(), map_location=device, weights_only=True)
    # Also accept the full checkpoint (MAF-Net_final_checkpoint.pt)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
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
