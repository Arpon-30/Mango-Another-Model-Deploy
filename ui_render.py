"""
Dashboard HTML panels for AmropaliNet (modern green mango theme).

Generates HTML fragments rendered via st.html() — supports both
dark and light themes via CSS custom properties in dashboard.css.
"""

from __future__ import annotations

import html
import textwrap

from model import CLASSES, DISEASE_INFO

DISEASE_EMOJI = {
    "Anthracnose": "🍂",
    "Bacterial Canker": "🦠",
    "Healthy": "🌿",
    "Powdery Mildew": "🌫️",
    "Scab": "🔶",
    "Sooty Mould": "🖤",
    "Stem End Rot": "⚫",
}


def _esc(text: str) -> str:
    return html.escape(str(text or ""), quote=True)


def _clean(fragment: str) -> str:
    return textwrap.dedent(fragment).strip()


# ═══════════════════════════════════════════════════════════════════════════
# Brand header (theme toggle is a Streamlit button in the header row)
# ═══════════════════════════════════════════════════════════════════════════
def brand_html(theme: str = "dark") -> str:
    return _clean(
        f"""
        <div class="dash-brand" data-theme-state="{_esc(theme)}">
          <div class="dash-brand__left">
            <div class="dash-brand__mark">🥭</div>
            <div>
              <h1>AmropaliNet</h1>
              <p>Amrapali mango disease classification · AA-ENet + CLIP</p>
            </div>
          </div>
          <div class="dash-brand__right">
            <div class="dash-brand__badge">CPU · Streamlit Cloud</div>
          </div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Sidebar section titles
# ═══════════════════════════════════════════════════════════════════════════
def side_title(icon: str, title: str) -> str:
    return _clean(
        f"""
        <div class="side-section-title"><span>{icon}</span>{_esc(title)}</div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# File upload chip
# ═══════════════════════════════════════════════════════════════════════════
def file_chip_html(name: str, size_mb: float) -> str:
    return _clean(
        f"""
        <div class="dash-file">
          <div class="dash-file__ok">✓</div>
          <div>{_esc(name)} · {size_mb:.2f} MB</div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Upload requirements
# ═══════════════════════════════════════════════════════════════════════════
def upload_requirements_html() -> str:
    return _clean(
        """
        <ul class="dash-req">
          <li>Formats: JPG, PNG, WebP, BMP, TIFF</li>
          <li>Max size: 10 MB per image</li>
          <li>Clear photo of mango fruit or leaf</li>
          <li>Non-mango images are rejected by CLIP</li>
        </ul>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Empty result state
# ═══════════════════════════════════════════════════════════════════════════
def empty_result_html() -> str:
    return _clean(
        """
        <div class="dash-panel">
          <div class="dash-panel__head">
            <div class="dash-panel__ico">🎯</div>
            <h3>Classification Result</h3>
          </div>
          <div class="dash-empty">
            <div class="dash-empty__icon">🥭</div>
            <div>
              <strong>No result yet</strong>
              Upload a mango image and classify it to see the diagnosis.
            </div>
            <div class="dash-empty__steps">
              <div class="dash-empty__step">
                <div class="dash-empty__num">1</div>
                <span>Upload a clear photo of a mango fruit or leaf</span>
              </div>
              <div class="dash-empty__step">
                <div class="dash-empty__num">2</div>
                <span>Click <em>Analyze &amp; Classify</em> to run the model</span>
              </div>
              <div class="dash-empty__step">
                <div class="dash-empty__num">3</div>
                <span>Use <em>GradCAM Visualization</em> to inspect attention maps</span>
              </div>
            </div>
          </div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Classification result
# ═══════════════════════════════════════════════════════════════════════════
def classification_result_html(predicted: str, confidence: float, disease_info: dict) -> str:
    pct = confidence * 100
    sci = disease_info.get("scientific_name", "")
    desc = disease_info.get("description", "")
    is_healthy = predicted.lower() == "healthy"
    status_class = "healthy" if is_healthy else "disease"
    status_text = "Plant appears healthy" if is_healthy else "Disease detected"

    return _clean(
        f"""
        <div class="dash-panel">
          <div class="dash-panel__head">
            <div class="dash-panel__ico">🎯</div>
            <h3>Classification Result</h3>
          </div>
          <p class="dash-result-label">PREDICTED CLASS</p>
          <h2 class="dash-result-title">{_esc(predicted)}</h2>
          <div class="dash-status-row">
            <div class="dash-status-dot {status_class}"></div>
            <span class="dash-status-text">{status_text}</span>
          </div>
          <div class="dash-conf-row">
            <span>CONFIDENCE</span>
            <span>{pct:.1f}%</span>
          </div>
          <div class="dash-bar"><i style="width:{pct:.2f}%"></i></div>
          <p class="dash-diagnosis">
            <b>{_esc(sci)}</b><br/>{_esc(desc)}
          </p>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Class probabilities with rank badges
# ═══════════════════════════════════════════════════════════════════════════
def probabilities_html(all_scores: list) -> str:
    rows = []
    for i, entry in enumerate(all_scores):
        pct = float(entry["score"]) * 100
        top = "is-top" if i == 0 else ""
        delay = f"animation-delay:{i * 0.08:.2f}s"
        rows.append(
            f"""
            <div class="dash-prob__row">
              <div class="dash-prob__rank {top}">{i + 1}</div>
              <div class="dash-prob__name {top}">{_esc(entry['class'])}</div>
              <div class="dash-bar"><i class="{top}" style="width:{pct:.2f}%;{delay}"></i></div>
              <div class="dash-prob__pct {top}">{pct:.1f}%</div>
            </div>
            """
        )
    return _clean(
        f"""
        <div class="dash-panel">
          <div class="dash-panel__head">
            <div class="dash-panel__ico">📊</div>
            <h3>Class Probabilities</h3>
          </div>
          <div class="dash-prob">{''.join(rows)}</div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Grad-CAM panel
# ═══════════════════════════════════════════════════════════════════════════
def gradcam_panel_html(original_b64: str, heatmap_b64: str) -> str:
    return _clean(
        f"""
        <div class="dash-panel">
          <div class="dash-panel__head">
            <div class="dash-panel__ico">👁</div>
            <h3>GradCAM — Model Attention Map</h3>
          </div>
          <div class="dash-cam-grid">
            <div class="dash-cam-card">
              <img src="data:image/png;base64,{original_b64}" alt="Original" />
              <span>🖼️ ORIGINAL IMAGE</span>
            </div>
            <div class="dash-cam-card">
              <img src="data:image/png;base64,{heatmap_b64}" alt="Grad-CAM overlay" />
              <span>🔥 GRADCAM OVERLAY</span>
            </div>
          </div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Remedies / Treatment panel
# ═══════════════════════════════════════════════════════════════════════════
def remedies_panel_html(disease_name: str, disease_info: dict) -> str:
    symptoms = disease_info.get("symptoms") or []
    remedies = disease_info.get("remedies") or []
    if not symptoms and not remedies:
        return ""
    s = "".join(f"<li>{_esc(x)}</li>" for x in symptoms)
    r = "".join(f"<li>{_esc(x)}</li>" for x in remedies)
    return _clean(
        f"""
        <div class="dash-panel">
          <div class="dash-panel__head">
            <div class="dash-panel__ico">💊</div>
            <h3>Diagnosis &amp; Treatment — {_esc(disease_name)}</h3>
          </div>
          <div class="dash-remedies-grid">
            <div class="dash-remedies-section symptoms">
              <p class="dash-result-label">🔴 SYMPTOMS</p>
              <ul class="dash-req">{s}</ul>
            </div>
            <div class="dash-remedies-section treatment">
              <p class="dash-result-label">💚 TREATMENT</p>
              <ul class="dash-req">{r}</ul>
            </div>
          </div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Disease encyclopedia
# ═══════════════════════════════════════════════════════════════════════════
def encyclopedia_html() -> str:
    cards = []
    for name in CLASSES:
        info = DISEASE_INFO.get(name, {})
        emoji = DISEASE_EMOJI.get(name, "🥭")
        sci = info.get("scientific_name", "")
        desc = (info.get("description") or "")[:140]
        if info.get("description") and len(info["description"]) > 140:
            desc += "…"
        cards.append(
            f"""
            <div class="dash-enc-card">
              <h4>{emoji} {_esc(name)}</h4>
              <p><em>{_esc(sci)}</em><br/>{_esc(desc)}</p>
            </div>
            """
        )
    return _clean(
        f"""
        <div class="dash-panel" id="encyclopedia-section">
          <div class="dash-panel__head">
            <div class="dash-panel__ico">📚</div>
            <h3>Disease Encyclopedia</h3>
          </div>
          <div class="dash-enc-grid">{''.join(cards)}</div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Error / notice toast (centered overlay above all content)
# ═══════════════════════════════════════════════════════════════════════════
def error_banner_html(message: str) -> str:
    # Unique id so multiple toasts in one run don't collide on dismiss
    toast_id = f"dash-toast-{abs(hash(message)) % 10_000_000}"
    return _clean(
        f"""
        <input type="checkbox" id="{toast_id}" class="dash-toast-check" aria-hidden="true" />
        <div class="dash-toast-backdrop" role="presentation">
          <div class="dash-toast dash-error" role="alertdialog" aria-labelledby="{toast_id}-title">
            <div class="dash-toast__head">
              <div class="dash-toast__ico">⚠️</div>
              <h3 id="{toast_id}-title">Notice</h3>
              <label for="{toast_id}" class="dash-toast__close" title="Dismiss" aria-label="Dismiss">×</label>
            </div>
            <p>{_esc(message)}</p>
            <p class="dash-toast__hint">Click × to dismiss</p>
          </div>
        </div>
        """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════════
def footer_html() -> str:
    return _clean(
        """
        <div class="dash-footer">
          <p class="dash-footer__title">🥭 MangoAI</p>
          <p class="dash-footer__line">Amrapali Mango Disease Detection · AA-ENet Model</p>
          <p class="dash-footer__line">AA-ENet Model developed by AIUB R&amp;D Club</p>
          <p class="dash-footer__line">(Arpon, Oni, Md. Ibtihazzaman) Group · Supervised by Dr. Md. Saef Ullah Miah</p>
          <p class="dash-footer__disclaimer">
            ⚠️ For research and educational purposes only. Always consult a qualified agronomist for crop management decisions.
          </p>
        </div>
        """
    )
