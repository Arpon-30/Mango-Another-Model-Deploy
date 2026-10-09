"""AmropaliNet on Streamlit Community Cloud.

Shows the real website (templates/index.html + static/) unchanged, full screen, as a
Streamlit component. The page's fetch("/api/...") calls go through
static/js/streamlit_bridge.js to Python, which answers them with the mango_disease_ai
REST API in memory (FastAPI TestClient) - same answers, errors and PDFs as `python run.py`.

Run locally:  streamlit run streamlit_app.py
Deploy:       see DEPLOY.md (Streamlit Community Cloud, Python 3.11)
"""
import os

# Before the library is imported: small-memory mango checker (Streamlit's free tier has
# about 1 GB RAM) and no TensorFlow import from transformers.
os.environ.setdefault("MANGO_LOW_MEMORY", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import base64
import ctypes
import gc
import json
import re
import shutil
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent

# Keep memory low on Streamlit's ~1 GB free tier: few malloc arenas (requests run on worker
# threads) and hand freed memory back to the system after each request.
try:
    _libc = ctypes.CDLL("libc.so.6")
    _libc.mallopt(-8, 2)  # M_ARENA_MAX = 2
except (OSError, AttributeError):
    _libc = None


def release_memory() -> None:
    gc.collect()
    if _libc is not None:
        _libc.malloc_trim(0)

st.set_page_config(
    page_title="AmropaliNet - AI Mango Doctor",
    page_icon="🥭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _replace(text: str, old: str, new: str, where: str) -> str:
    if old not in text:
        raise RuntimeError(f"streamlit_app.py: '{old}' not found in {where} - update the site build")
    return text.replace(old, new)


@st.cache_resource(show_spinner=False)
def build_site() -> str:
    """Copy the website into a folder Streamlit can serve as a component."""
    out = Path(tempfile.gettempdir()) / "amropalinet_site"
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(ROOT / "static", out / "static")
    shutil.copy(ROOT / "mango_disease_ai" / "docs.html", out / "guide.html")

    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    html = html.replace('"/static/', '"static/')
    # No live /docs on Streamlit: "Try the API" opens the library guide instead
    html = _replace(html, 'href="/docs"', 'href="guide.html"', "index.html")
    html = _replace(
        html,
        '<script src="static/js/i18n.js" defer></script>',
        '<script src="static/js/streamlit_bridge.js"></script>\n'
        '    <script src="static/js/i18n.js" defer></script>',
        "index.html",
    )
    # Streamlit Cloud draws its own badge in the bottom-right corner: keep the phone
    # "Scan" button above it
    html = _replace(
        html,
        "</head>",
        "    <style>.fab { bottom: calc(76px + env(safe-area-inset-bottom)); }</style>\n</head>",
        "index.html",
    )
    (out / "index.html").write_text(html, encoding="utf-8")

    main_js = out / "static" / "js" / "main.js"
    js = main_js.read_text(encoding="utf-8")
    js = _replace(js, '"/static/', '"static/', "main.js")
    js = _replace(js, 'new URLSearchParams(location.search).has("demo")', "Boolean(window.MANGO_DEMO)", "main.js")
    main_js.write_text(js, encoding="utf-8")
    return str(out)


@st.cache_resource(show_spinner=False)
def api():
    """The library's REST API in memory. Entering the client starts the model warm-up."""
    from fastapi.testclient import TestClient

    from mango_disease_ai.server import create_app

    client = TestClient(create_app(), raise_server_exceptions=False)
    client.__enter__()  # runs the lifespan: loads AA-ENet + the mango checker in the background
    return client


def answer(req: dict) -> dict:
    """Answer one fetch() from the page."""
    out = {"id": req.get("id")}
    path = str(req.get("path", ""))
    if not re.fullmatch(r"/api/[a-z_]+", path):
        return {**out, "status": 404, "content_type": "application/json", "text": '{"detail": "Not found"}'}
    try:
        client = api()
        if req.get("method") == "POST":
            files = {
                key: (f.get("name") or "photo.jpg", base64.b64decode(f.get("b64", "")), f.get("type"))
                for key, f in (req.get("files") or {}).items()
            }
            r = client.post(path, data=req.get("fields") or {}, files=files or None)
        else:
            r = client.get(path)
    except Exception as exc:  # keep the page alive; it shows its own error message
        return {**out, "status": 500, "content_type": "application/json",
                "text": json.dumps({"detail": {"code": "server_error", "message": str(exc)[:200]}})}
    ctype = r.headers.get("content-type", "application/octet-stream")
    if "json" in ctype or ctype.startswith("text/"):
        return {**out, "status": r.status_code, "content_type": ctype, "text": r.text}
    return {**out, "status": r.status_code, "content_type": ctype, "b64": base64.b64encode(r.content).decode()}


api()  # start loading the models as soon as the first visitor arrives

request = st.session_state.get("site")
if isinstance(request, dict) and request.get("id") and request["id"] != st.session_state.get("answered"):
    st.session_state.response = answer(request)
    st.session_state.answered = request["id"]
    release_memory()

# Full screen website: hide Streamlit's own header, padding and "stale" fading
st.markdown(
    """
    <style>
      header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
      [data-testid="stStatusWidget"], footer { display: none !important; }
      html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow: hidden !important;
      }
      [data-testid="stMainBlockContainer"], .block-container {
        padding: 0 !important; max-width: 100% !important;
      }
      [data-testid="stVerticalBlock"] { gap: 0 !important; }
      [data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style) { display: none !important; }
      iframe[title*="amropalinet_site"] {
        display: block; width: 100vw !important; border: 0;
        height: 100vh !important; height: 100dvh !important;
      }
      .stale-element, [data-stale="true"] { opacity: 1 !important; transition: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

site = components.declare_component("amropalinet_site", path=build_site())
site(key="site", response=st.session_state.get("response"), default=None)
