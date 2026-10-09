"""
Inference utilities: mango validation, classification, and Grad-CAM.
"""

import io
import base64

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from scipy.ndimage import gaussian_filter
from torchvision import transforms

from model import CLASSES, IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD, load_model, load_mango_detector

# ── Transforms ───────────────────────────────────────────────────────────────
eval_tf = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


def _denorm(t: torch.Tensor) -> torch.Tensor:
    """Undo ImageNet normalisation for display."""
    m = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    s = torch.tensor(IMAGENET_STD).view(3, 1, 1)
    return (t * s + m).clamp(0, 1)


# ── Mango detection via CLIP zero-shot (openai/clip-vit-base-patch32) ────────
MANGO_CONFIDENCE_THRESHOLD = 0.50  # reject when combined mango score < 50%

# Candidate labels for CLIP zero-shot classification
MANGO_LABELS = [
    "a photo of a mango fruit",
    "a photo of a mango leaf",
    "a photo of another type of fruit",
    "a photo of a non-mango plant leaf",
    "a photo of a vegetable",
    "a photo of an animal or person",
    "a photo of an indoor scene or man-made object",
]

# Indices in MANGO_LABELS that count as "mango"
MANGO_POSITIVE_INDICES = {0}  # mango fruit or mango leaf


def is_mango(pil_img: Image.Image) -> tuple[bool, float]:
    """
    Check if image is a mango using CLIP zero-shot classification.
    Returns (is_mango, confidence).
    """
    model, processor = load_mango_detector()

    inputs = processor(
        text=MANGO_LABELS,
        images=pil_img,
        return_tensors="pt",
        padding=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)
        # logits_per_image shape: [1, num_labels]
        logits = outputs.logits_per_image
        probs = torch.softmax(logits, dim=-1).squeeze(0)

    # Sum probabilities for mango-positive labels
    mango_conf = sum(float(probs[i]) for i in MANGO_POSITIVE_INDICES)

    is_mango_pred = mango_conf >= MANGO_CONFIDENCE_THRESHOLD
    return is_mango_pred, round(mango_conf, 4)


# ── Image validation (confidence-based) ──────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.90  # reject if top prediction < 90 %


def validate_image(pil_img: Image.Image) -> tuple[bool, float]:
    """
    Check whether the image is a valid mango leaf/fruit by running the model
    and inspecting the top prediction confidence.

    Returns (is_valid, top_confidence).
    A truly irrelevant image (car, selfie, etc.) will produce low, spread-out
    softmax scores across all 7 classes, while a genuine mango image will
    produce a confident peak.
    """
    model = load_model()
    x = eval_tf(pil_img.convert("RGB")).unsqueeze(0)

    with torch.no_grad():
        logits = model(x)
        probs = F.softmax(logits, dim=1).squeeze(0)

    top_conf = float(probs.max())
    return top_conf >= CONFIDENCE_THRESHOLD, round(top_conf, 4)


# ── Classification ───────────────────────────────────────────────────────────
def classify_image(pil_img: Image.Image) -> dict:
    """
    Run the AA-ENet model on a PIL image.

    Returns dict with keys:
        predicted_class, confidence, all_scores (list of {class, score})
    """
    model = load_model()
    x = eval_tf(pil_img.convert("RGB")).unsqueeze(0)

    with torch.no_grad():
        logits = model(x)
        probs = F.softmax(logits, dim=1).squeeze(0)

    scores = {CLASSES[i]: round(float(probs[i]), 5) for i in range(len(CLASSES))}
    sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    pred_class, pred_conf = sorted_scores[0]

    return {
        "predicted_class": pred_class,
        "confidence": round(pred_conf, 5),
        "all_scores": [{"class": c, "score": s} for c, s in sorted_scores],
    }


# ── Grad-CAM ────────────────────────────────────────────────────────────────
class _GradCAM:
    """
    Grad-CAM++ on the last spatial feature map (CBAM output).

  Uses torch.autograd.grad w.r.t. hooked activations — the same approach as the
    research notebook — instead of backward hooks on detached tensors.
    """

    def __init__(self, model, target_layer):
        self.model = model
        self.activations = None
        self._handle = target_layer.register_forward_hook(self._capture_activation)

    def _capture_activation(self, module, inputs, output):
        # Keep the tensor on the autograd graph (do not detach).
        self.activations = output

    def __call__(self, x, class_idx=None):
        self.model.zero_grad(set_to_none=True)
        logits = self.model(x)

        if class_idx is None:
            class_idx = int(logits.argmax(dim=1).item())

        score = logits[0, class_idx]
        if self.activations is None:
            raise RuntimeError("Failed to capture target-layer activations")

        grads = torch.autograd.grad(
            outputs=score,
            inputs=self.activations,
            retain_graph=False,
            create_graph=False,
            allow_unused=False,
        )[0]

        # Grad-CAM++ channel weights (better localization than plain Grad-CAM).
        grad_2 = grads.pow(2)
        grad_3 = grads.pow(3)
        denom = 2.0 * grad_2 + self.activations.mul(grad_3).sum(dim=(2, 3), keepdim=True)
        alpha = grad_2 / (denom + 1e-8)
        weights = (alpha * F.relu(grads)).sum(dim=(2, 3), keepdim=True)

        cam = (weights * self.activations).sum(dim=1)
        cam = F.relu(cam)

        cam_min = cam.amin(dim=(1, 2), keepdim=True)
        cam_max = cam.amax(dim=(1, 2), keepdim=True)
        cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)

        return cam.detach().cpu().numpy(), class_idx

    def remove_hook(self):
        self._handle.remove()


def _normalize_cam(cam: np.ndarray) -> np.ndarray:
    """Suppress low-confidence noise and stretch the salient range."""
    lo, hi = np.percentile(cam, (5, 99))
    cam = np.clip(cam, lo, hi)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    return cam


def generate_gradcam(pil_img: Image.Image, class_idx: int | None = None) -> dict:
    """
    Generate a Grad-CAM++ heatmap overlay aligned with the model input.

    Returns dict with:
        original_b64  — base64 PNG of the original (resized) image
        heatmap_b64   — base64 PNG of the heatmap overlay
    """
    model = load_model()
    was_training = model.training
    model.eval()

    # CBAM is the last spatial layer before pooling / transformer fusion.
    cam_engine = _GradCAM(model, model.cbam)

    img_rgb = pil_img.convert("RGB")
    x = eval_tf(img_rgb).unsqueeze(0)

    with torch.enable_grad():
        for param in model.parameters():
            param.requires_grad_(True)
        cam, _ = cam_engine(x, class_idx=class_idx)

    cam_engine.remove_hook()
    for param in model.parameters():
        param.requires_grad_(False)
    if was_training:
        model.train()

    cam = cam[0]

    cam_tensor = torch.from_numpy(cam).unsqueeze(0).unsqueeze(0)
    cam_upscaled = F.interpolate(
        cam_tensor,
        size=(IMG_SIZE, IMG_SIZE),
        mode="bilinear",
        align_corners=False,
    ).squeeze().numpy()

    cam_upscaled = gaussian_filter(cam_upscaled, sigma=1.2)
    cam_upscaled = _normalize_cam(cam_upscaled)

    base = _denorm(eval_tf(img_rgb)).permute(1, 2, 0).numpy()
    base = np.clip(base * 255, 0, 255).astype(np.uint8)

    cam_uint8 = (cam_upscaled * 255).astype(np.uint8)
    heatmap_color = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Match the research notebook overlay (45% heatmap opacity).
    overlay = np.clip(
        0.55 * base.astype(np.float32) + 0.45 * heatmap_color.astype(np.float32),
        0,
        255,
    ).astype(np.uint8)

    return {
        "original_b64": _to_b64(base),
        "heatmap_b64": _to_b64(overlay),
    }


def _to_b64(arr: np.ndarray) -> str:
    """Convert a uint8 numpy RGB array to a base64-encoded PNG string."""
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
