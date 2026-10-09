"""
PDF diagnosis report for AmropaliNet (one A4 page), in English or Bangla.

Layout: brand header · who/when · diagnosis card · photo / heatmap / marked area ·
about the disease · signs + treatment · all class scores · disclaimer footer.

Bangla uses the bundled Hind Siliguri font (SIL OFL, see fonts/OFL.txt) and needs
`uharfbuzz` for correct letter joining. Lines are wrapped here and drawn one by one:
fpdf2's own multi_cell wrapping can mis-shape Bangla on wrapped lines.
"""

from __future__ import annotations

import base64
import io
import json
import uuid
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

_HERE = Path(__file__).resolve().parent
FONT_DIR = _HERE / "fonts"

# ── Brand ────────────────────────────────────────────────────────────────────
GREEN_DARK = (27, 94, 32)
GREEN = (46, 125, 50)
GREEN_TINT = (241, 247, 232)
MANGO = (251, 140, 0)
INK = (29, 58, 31)
INK_SOFT = (78, 107, 74)
MUTED = (120, 135, 115)
BORDER = (220, 235, 205)
RED = (198, 40, 40)

DISEASE_STYLE = {
    "Anthracnose": ((181, 84, 28), "high"),
    "Bacterial Canker": ((142, 106, 0), "high"),
    "Healthy": ((46, 125, 50), "none"),
    "Powdery Mildew": ((96, 112, 130), "high"),
    "Scab": ((141, 110, 99), "medium"),
    "Sooty Mould": ((55, 71, 79), "medium"),
    "Stem End Rot": ((93, 64, 55), "high"),
}

TEXT = {
    "en": {
        "subtitle": "Amrapali Mango Disease Report",
        "prepared": "Prepared for",
        "report_id": "Report ID",
        "diagnosis": "DIAGNOSIS",
        "healthy_title": "Healthy mango",
        "confidence": "AI confidence",
        "risk": "Garden risk",
        "risk.high": "High", "risk.medium": "Medium", "risk.none": "None",
        "unsure": "The AI is not fully sure. Take another photo in daylight, closer to the spot, "
                  "and compare with the signs below.",
        "img.photo": "Your photo",
        "img.heat": "Where the AI looked (Grad-CAM)",
        "img.marked": "Likely affected area",
        "img.none": "No affected area",
        "heat_note": "Heatmap: red and yellow areas mattered most for the answer.",
        "affected_note": " The red outline covers about {pct}% of the photo (AI estimate, not a measurement).",
        "about": "About {name}",
        "about_healthy": "About this result",
        "signs": "Signs to check",
        "signs_healthy": "What a healthy mango looks like",
        "todo": "What to do now",
        "todo_healthy": "Keep it healthy",
        "scores": "How sure the AI is for each class",
        "disclaimer": "For guidance only. This report is produced by an AI model and can be wrong. "
                      "Always consult a qualified agronomist for crop management decisions.",
        "team": "AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman) - Supervised by Dr. Md. Saef Ullah Miah"
                " - arponamit.55@gmail.com",
        "farmer": "Farmer",
    },
    "bn": {
        "subtitle": "আম্রপালি আমের রোগ নির্ণয় রিপোর্ট",
        "prepared": "যার জন্য",
        "report_id": "রিপোর্ট আইডি",
        "diagnosis": "রোগ নির্ণয়",
        "healthy_title": "সুস্থ আম",
        "confidence": "এআই নিশ্চয়তা",
        "risk": "বাগানের ঝুঁকি",
        "risk.high": "বেশি", "risk.medium": "মাঝারি", "risk.none": "নেই",
        "unsure": "এআই পুরোপুরি নিশ্চিত নয়। দিনের আলোয়, দাগের কাছ থেকে আরেকটি ছবি তুলুন এবং নিচের লক্ষণগুলোর সাথে মিলিয়ে দেখুন।",
        "img.photo": "আপনার ছবি",
        "img.heat": "এআই কোথায় দেখেছে (Grad-CAM)",
        "img.marked": "সম্ভাব্য আক্রান্ত অংশ",
        "img.none": "কোনো আক্রান্ত অংশ নেই",
        "heat_note": "হিটম্যাপ: লাল ও হলুদ অংশ উত্তরের জন্য সবচেয়ে গুরুত্বপূর্ণ ছিল।",
        "affected_note": " লাল দাগের ভেতরের অংশ ছবির প্রায় {pct}% (এআই অনুমান, মাপা নয়)।",
        "about": "{name} সম্পর্কে",
        "about_healthy": "এই ফলাফল সম্পর্কে",
        "signs": "যে লক্ষণগুলো দেখবেন",
        "signs_healthy": "সুস্থ আম দেখতে যেমন",
        "todo": "এখন কী করবেন",
        "todo_healthy": "সুস্থ রাখতে যা করবেন",
        "scores": "প্রতিটি শ্রেণিতে এআই কতটা নিশ্চিত",
        "disclaimer": "শুধু পরামর্শের জন্য। এই রিপোর্ট একটি এআই মডেল তৈরি করেছে এবং ভুল হতে পারে। "
                      "ফসল ব্যবস্থাপনার সিদ্ধান্তের আগে সবসময় একজন অভিজ্ঞ কৃষিবিদের পরামর্শ নিন।",
        "team": "AIUB শিক্ষার্থী দল (Arpon, Oni, Md. Ibtihazzaman) - তত্ত্বাবধানে: Dr. Md. Saef Ullah Miah"
                " - arponamit.55@gmail.com",
        "farmer": "কৃষক",
    },
}

BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
BN_MONTHS = ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই", "আগস্ট",
             "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"]

# A4 portrait, millimetres
PAGE_W, PAGE_H = 210, 297
MARGIN = 14
CONTENT_W = PAGE_W - 2 * MARGIN


class BanglaPdfUnavailable(RuntimeError):
    """Bangla PDF needs the `uharfbuzz` package for correct letter joining."""


def _load_bn_info() -> dict:
    try:
        return json.loads((_HERE / "disease_info_bn.json").read_text(encoding="utf-8"))
    except OSError:
        return {}


def _latin1(text) -> str:
    """Normalise dashes/quotes and keep only characters the core Latin fonts can draw."""
    s = str(text or "")
    for a, b in {"–": "-", "—": "-", "‘": "'", "’": "'",
                 "“": '"', "”": '"', "…": "...", "×": "x"}.items():
        s = s.replace(a, b)
    return "".join(ch for ch in s if ch.encode("latin-1", "ignore"))


def _is_latin1(text: str) -> bool:
    return all(ch.encode("latin-1", "ignore") for ch in text)


def _pdf_name(name: str) -> str:
    """Kept for backwards compatibility: Latin-1 only version of a name."""
    return " ".join(_latin1(name).split()) or "Farmer"


def _img(b64: str | None):
    return io.BytesIO(base64.b64decode(b64)) if b64 else None


class _ReportPDF(FPDF):
    """Knows the report language and draws text with the right font."""

    def __init__(self, lang: str, unicode_font: bool):
        super().__init__(format="A4")
        self.lang = lang
        self.unicode_font = unicode_font
        if unicode_font:
            self.add_font("Hind", "", str(FONT_DIR / "HindSiliguri-Regular.ttf"))
            self.add_font("Hind", "B", str(FONT_DIR / "HindSiliguri-Bold.ttf"))
            self.set_text_shaping(True)

    # -- text helpers -----------------------------------------------------
    def font(self, style: str = "", size: float = 9, latin: bool = False, text: str = "") -> None:
        """Hind Siliguri for Bangla text; Helvetica for English and Latin names."""
        use_hind = self.unicode_font and not latin and (self.lang == "bn" or not _is_latin1(text))
        if use_hind:
            self.set_font("Hind", "B" if "B" in style else "", size)
        else:
            self.set_font("Helvetica", style, size)

    def clean(self, text) -> str:
        s = " ".join(str(text or "").split())
        if self.lang == "bn":
            return s.replace("–", "-").replace("—", "-")
        return " ".join(_latin1(s).split())

    def num(self, text) -> str:
        return str(text).translate(BN_DIGITS) if self.lang == "bn" else str(text)

    def wrap(self, text: str, width: float) -> list[str]:
        lines, cur = [], ""
        for word in text.split():
            cand = f"{cur} {word}".strip()
            if not cur or self.get_string_width(cand) <= width:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, text: str, x: float, y: float, w: float, lh: float, align: str = "L") -> float:
        """Draw wrapped text line by line; return the y below it."""
        for line in self.wrap(text, w):
            self.set_xy(x, y)
            self.cell(w, lh, line, align=align)
            y += lh
        return y

    def footer(self):
        t = TEXT[self.lang]
        self.set_draw_color(*BORDER)
        self.line(MARGIN, PAGE_H - 22, PAGE_W - MARGIN, PAGE_H - 22)
        self.set_text_color(*MUTED)
        self.font("I", 7.5)
        y = self.para(self.clean(t["disclaimer"]), MARGIN, PAGE_H - 20, CONTENT_W, 3.8, align="C")
        self.font("", 7.5)
        self.para(self.clean(t["team"]), MARGIN, y, CONTENT_W, 3.8, align="C")


def _heading(pdf: _ReportPDF, text: str, x: float, y: float, w: float) -> float:
    pdf.font("B", 10.5)
    pdf.set_text_color(*GREEN_DARK)
    pdf.set_xy(x, y)
    pdf.cell(w, 6, pdf.clean(text))
    return y + 7


def _bullets(pdf: _ReportPDF, items, x: float, y: float, w: float, numbered: bool = False) -> float:
    lh = 4.6 if pdf.lang == "bn" else 4.4
    for i, item in enumerate(items, 1):
        pdf.set_text_color(*(GREEN if numbered else MANGO))
        pdf.font("B", 8.8)
        pdf.set_xy(x, y)
        pdf.cell(5, lh, pdf.num(f"{i}.") if numbered else "-")
        pdf.font("", 8.8)
        pdf.set_text_color(*INK)
        y = pdf.para(pdf.num(pdf.clean(item)) if numbered else pdf.clean(item), x + 5, y, w - 5, lh) + 1
    return y


def generate_report(
    user_name: str,
    original_b64: str,
    heatmap_b64: str,
    classification: dict,
    disease_info: dict | None = None,
    marked_b64: str | None = None,
    affected_percent: float | None = None,
    lang: str = "en",
) -> bytes:
    """Build the one-page PDF (lang 'en' or 'bn') and return its bytes."""
    lang = "bn" if lang == "bn" else "en"
    try:
        import uharfbuzz  # noqa: F401  (needed by fpdf2 for Bangla shaping)
        shaping = True
    except ImportError:
        shaping = False
    if lang == "bn" and not shaping:
        raise BanglaPdfUnavailable(
            "Bangla PDF needs the 'uharfbuzz' package. Install it with: pip install uharfbuzz"
        )

    t = TEXT[lang]
    info = dict(disease_info or {})
    pred = classification["predicted_class"]
    conf = float(classification["confidence"])
    tone, risk_key = DISEASE_STYLE.get(pred, (GREEN, "none"))
    healthy = pred == "Healthy"
    bn_info = _load_bn_info() if lang == "bn" else {}
    names = {k: (bn_info.get(k, {}).get("name") or k) for k in DISEASE_STYLE} if lang == "bn" else {}
    if lang == "bn" and pred in bn_info:
        info.update({k: v for k, v in bn_info[pred].items() if k in ("description", "symptoms", "remedies")})
    local_name = names.get(pred, pred)

    pdf = _ReportPDF(lang, unicode_font=shaping)
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # ── Header band ──────────────────────────────────────────────────────
    pdf.set_fill_color(*GREEN_DARK)
    pdf.rect(0, 0, PAGE_W, 28, style="F")
    pdf.set_fill_color(*MANGO)
    pdf.rect(0, 28, PAGE_W, 1.4, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.font("B", 20, latin=True)
    pdf.set_xy(MARGIN, 6.5)
    pdf.cell(100, 9, "AmropaliNet")
    pdf.set_text_color(220, 240, 210)
    pdf.font("", 10)
    pdf.set_xy(MARGIN, 16)
    pdf.cell(110, 6, t["subtitle"])

    now = datetime.now()
    if lang == "bn":
        date_txt = pdf.num(f"{now.day} {BN_MONTHS[now.month - 1]} {now.year}, {now.strftime('%I:%M')}")
    else:
        date_txt = now.strftime("%d %B %Y, %I:%M %p")
    pdf.font("", 8.5)
    pdf.set_xy(PAGE_W - MARGIN - 80, 8)
    pdf.cell(80, 5, date_txt, align="R")
    pdf.set_xy(PAGE_W - MARGIN - 80, 14)
    pdf.cell(80, 5, f"{t['report_id']}: {uuid.uuid4().hex[:8].upper()}", align="R")

    # ── Prepared for ─────────────────────────────────────────────────────
    name = " ".join(str(user_name or "").split()) or t["farmer"]
    if not shaping:
        name = _pdf_name(name)
    pdf.set_text_color(*MUTED)
    pdf.font("", 9)
    pdf.set_xy(MARGIN, 34)
    pdf.cell(26, 6, t["prepared"])
    pdf.set_text_color(*INK)
    pdf.font("B", 10.5, text=name)
    pdf.set_xy(MARGIN + 26, 34)
    pdf.cell(120, 6, name)

    # ── Diagnosis card ───────────────────────────────────────────────────
    y = 44
    card_h = 30
    pdf.set_fill_color(*GREEN_TINT)
    pdf.set_draw_color(*BORDER)
    pdf.rect(MARGIN, y, CONTENT_W, card_h, style="DF", round_corners=True, corner_radius=3)
    pdf.set_fill_color(*tone)
    pdf.rect(MARGIN, y, 3, card_h, style="F")

    pdf.set_text_color(*MANGO)
    pdf.font("B", 7.8)
    pdf.set_xy(MARGIN + 8, y + 3.5)
    pdf.cell(80, 4.5, t["diagnosis"])
    pdf.set_text_color(*tone)
    pdf.font("B", 18)
    pdf.set_xy(MARGIN + 8, y + 9)
    pdf.cell(115, 9, t["healthy_title"] if healthy else pdf.clean(local_name))
    pdf.set_text_color(*INK_SOFT)
    pdf.font("I", 9, latin=True)
    pdf.set_xy(MARGIN + 8, y + 20)
    pdf.cell(115, 5, _latin1(info.get("scientific_name", "")))

    rx = PAGE_W - MARGIN - 62
    pdf.set_text_color(*INK)
    pdf.font("B", 20, latin=lang == "en")
    pdf.set_xy(rx, y + 4.5)
    pdf.cell(56, 9, pdf.num(f"{conf * 100:.1f}%"), align="R")
    pdf.set_text_color(*MUTED)
    pdf.font("", 8)
    pdf.set_xy(rx, y + 14)
    pdf.cell(56, 4.5, t["confidence"], align="R")
    pdf.set_text_color(*(RED if risk_key == "high" else GREEN if risk_key == "none" else MANGO))
    pdf.font("B", 8.5)
    pdf.set_xy(rx, y + 20)
    pdf.cell(56, 5, f"{t['risk']}: {t['risk.' + risk_key]}", align="R")

    y += card_h + 3
    if conf < 0.7:
        pdf.set_text_color(*MANGO)
        pdf.font("I", 8.5)
        y = pdf.para(pdf.clean(t["unsure"]), MARGIN, y, CONTENT_W, 4.4) + 1

    # ── Images ───────────────────────────────────────────────────────────
    y += 2
    gap = 5
    img_w = (CONTENT_W - 2 * gap) / 3
    panels = [
        (original_b64, t["img.photo"]),
        (heatmap_b64, t["img.heat"]),
        (original_b64 if healthy else marked_b64, t["img.none"] if healthy else t["img.marked"]),
    ]
    for i, (b64, caption) in enumerate(panels):
        x = MARGIN + i * (img_w + gap)
        data = _img(b64)
        if data:
            pdf.image(data, x=x, y=y, w=img_w, h=img_w)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x, y, img_w, img_w)
        pdf.set_text_color(*INK_SOFT)
        pdf.font("B", 8.5)
        pdf.set_xy(x, y + img_w + 1.5)
        pdf.cell(img_w, 5, caption, align="C")
    y += img_w + 7.5

    note = t["heat_note"]
    if not healthy and affected_percent is not None:
        note += t["affected_note"].format(pct=pdf.num(f"{affected_percent:.0f}"))
    pdf.set_text_color(*MUTED)
    pdf.font("", 7.8)
    y = pdf.para(pdf.clean(note), MARGIN, y, CONTENT_W, 4) + 3

    # ── About ────────────────────────────────────────────────────────────
    desc = info.get("description")
    if desc:
        y = _heading(pdf, t["about_healthy"] if healthy else t["about"].format(name=local_name), MARGIN, y, CONTENT_W)
        pdf.set_text_color(*INK)
        pdf.font("", 8.8)
        y = pdf.para(pdf.clean(desc), MARGIN, y, CONTENT_W, 4.6 if lang == "bn" else 4.4) + 3

    # ── Signs + treatment (two columns) ─────────────────────────────────
    col_w = (CONTENT_W - 8) / 2
    right_x = MARGIN + col_w + 8
    top = y
    _heading(pdf, t["signs_healthy"] if healthy else t["signs"], MARGIN, top, col_w)
    y_left = _bullets(pdf, info.get("symptoms", []), MARGIN, top + 7, col_w)
    _heading(pdf, t["todo_healthy"] if healthy else t["todo"], right_x, top, col_w)
    y_right = _bullets(pdf, info.get("remedies", []), right_x, top + 7, col_w, numbered=True)
    y = max(y_left, y_right) + 3

    # ── All scores (compact bars, two columns) ───────────────────────────
    scores = classification.get("all_scores", [])
    if scores:
        y = _heading(pdf, t["scores"], MARGIN, y, CONTENT_W)
        half = (CONTENT_W - 8) / 2
        name_w, pct_w = 36, 14
        bar_w = half - name_w - pct_w - 2
        for i, s in enumerate(scores):
            col, row = divmod(i, 4)
            x = MARGIN + col * (half + 8)
            yy = y + row * 6
            top_row = i == 0
            label = names.get(s["class"], s["class"]) if lang == "bn" else s["class"]
            pdf.set_text_color(*INK)
            pdf.font("B" if top_row else "", 8.5)
            pdf.set_xy(x, yy)
            pdf.cell(name_w, 4.6, pdf.clean(label))
            pdf.set_fill_color(*GREEN_TINT)
            pdf.rect(x + name_w, yy + 1, bar_w, 2.6, style="F", round_corners=True, corner_radius=1.3)
            fill = max(0.8, bar_w * float(s["score"]))
            pdf.set_fill_color(*(tone if top_row else (156, 204, 101)))
            # Rounded corners only when the bar is wider than its height (tiny bars glitch otherwise)
            pdf.rect(x + name_w, yy + 1, fill, 2.6, style="F", round_corners=fill > 2.6, corner_radius=1.3)
            pdf.set_xy(x + name_w + bar_w + 1, yy)
            pdf.cell(pct_w, 4.6, pdf.num(f"{float(s['score']) * 100:.1f}%"), align="R")

    return bytes(pdf.output())
