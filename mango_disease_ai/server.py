"""
mango_disease_ai.server
=======================
The REST API of the mango-disease-ai library (FastAPI). The AmropaliNet website
runs on this same API.

Start it with ONE command after `pip install "mango-disease-ai[api]"`:

    mango-api                               # console script
    python -m mango_disease_ai.server       # same thing
    mango-api --port 8080                   # custom port

Then open:
    http://localhost:8000          welcome page
    http://localhost:8000/docs     Swagger UI (try every endpoint)
    http://localhost:8000/guide    full documentation

Endpoints
---------
GET  /api/health     server + model status
GET  /api/diseases   information for all 7 classes
POST /api/analyze    image -> diagnosis JSON (+ Grad-CAM + marked affected area)
POST /api/report     image + name (+ lang=en|bn) -> PDF report

Errors return JSON ``{"detail": {"code": ..., "message": ...}}`` with codes:
400 bad_type / too_large / empty / bad_image / no_name / bad_lang,
422 not_mango (+ mango_confidence), 503 model_missing / mango_check_unavailable /
bn_pdf_unavailable, 500 analysis_failed / report_failed.
"""

from __future__ import annotations

import os

# PyTorch only: keep `transformers` from importing TensorFlow/Keras if they are installed.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import argparse
import io
import logging
import re
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

log = logging.getLogger("mango_disease_ai")


def _version() -> str:
    from mango_disease_ai import __version__

    return __version__


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["0.2.0"])
    model: str = Field("loading", description="MAF-Net status: loading / ok / error")
    model_error: Optional[str] = Field(None, description="Why the MAF-Net model could not be loaded")
    mango_check: str = Field("loading", description="CLIP mango checker status: loading / ok / error")
    mango_check_error: Optional[str] = Field(None, description="Why the CLIP mango checker could not be loaded")


class AnalyzeResponse(BaseModel):
    is_mango: bool
    mango_confidence: float
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None
    all_scores: list[dict] = Field(default_factory=list)
    disease_info: dict = Field(default_factory=dict)
    gradcam_base64: Optional[str] = Field(None, description="JPEG (base64) of the Grad-CAM heatmap overlay")
    original_base64: Optional[str] = Field(None, description="JPEG (base64) of the photo, 448x448")
    marked_base64: Optional[str] = Field(None, description="JPEG (base64) with the likely affected area outlined")
    affected_percent: Optional[float] = Field(None, description="Share of the photo inside the outline (%)")


class DiseaseListResponse(BaseModel):
    diseases: dict


# ---------------------------------------------------------------------------
# Model status + warm-up
# ---------------------------------------------------------------------------
_status = {"model": "loading", "model_error": None, "mango_check": "loading", "mango_check_error": None}
# Grad-CAM toggles gradients on the shared model, so run one analysis at a time.
_analysis_lock = threading.Lock()

CLIP_HELP = (
    "The mango checker (CLIP) could not be loaded. On the first scan it downloads about "
    "600 MB from Hugging Face, so the computer needs internet once."
)


def _load_mango_checker() -> None:
    from mango_disease_ai.model import load_mango_detector

    try:
        load_mango_detector()
        _status.update(mango_check="ok", mango_check_error=None)
    except Exception as exc:  # network / Hugging Face problems
        _status.update(mango_check="error", mango_check_error=f"{CLIP_HELP} Details: {exc}")
        raise


def _warm_up() -> None:
    """Load MAF-Net and CLIP in the background so the first request is fast."""
    try:
        from mango_disease_ai.model import load_model

        load_model()
        _status.update(model="ok", model_error=None)
        log.info("MAF-Net model loaded")
    except Exception as exc:
        _status.update(model="error", model_error=str(exc))
        log.error("MAF-Net model NOT loaded: %s", exc)
    try:
        _load_mango_checker()
        log.info("CLIP mango checker loaded")
    except Exception as exc:
        log.error("CLIP mango checker NOT loaded: %s", exc)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    threading.Thread(target=_warm_up, daemon=True).start()
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp", "image/tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _fail(status: int, code: str, message: str, **extra):
    """Raise an error clients can recognise by `detail.code`."""
    raise HTTPException(status_code=status, detail={"code": code, "message": message, **extra})


def _read_upload(file: UploadFile) -> bytes:
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        _fail(400, "bad_type", f"Unsupported file type: {file.content_type}. Upload JPEG, PNG, WebP, BMP or TIFF.")
    data = file.file.read()
    if len(data) > MAX_FILE_SIZE:
        _fail(400, "too_large", "File too large. Maximum size is 10 MB.")
    if not data:
        _fail(400, "empty", "Uploaded file is empty.")
    try:
        from PIL import Image

        Image.open(io.BytesIO(data)).verify()
    except Exception:
        _fail(400, "bad_image", "This file could not be read as an image.")
    return data


def _run_analysis(img_bytes: bytes, include_gradcam: bool = True) -> dict:
    """Mango check (CLIP) -> MAF-Net -> Grad-CAM, with a clear error for each failure."""
    from mango_disease_ai.model import ModelNotReadyError, resolve_model_path

    try:
        resolve_model_path()
    except ModelNotReadyError as exc:
        _fail(503, "model_missing", str(exc))

    if _status["mango_check"] != "ok":
        try:
            _load_mango_checker()
        except Exception:
            _fail(503, "mango_check_unavailable", _status["mango_check_error"] or CLIP_HELP)

    try:
        from mango_disease_ai import analyze

        with _analysis_lock:
            result = analyze(img_bytes, include_gradcam=include_gradcam)
    except ModelNotReadyError as exc:
        _fail(503, "model_missing", str(exc))
    except Exception as exc:
        log.exception("Analysis failed")
        _fail(500, "analysis_failed", f"Analysis failed: {exc}")

    _status.update(model="ok", model_error=None)

    if not result["is_mango"]:
        _fail(
            422,
            "not_mango",
            "This image does not appear to be a mango. Please upload a clear photo of a mango fruit or leaf.",
            mango_confidence=result["mango_confidence"],
        )
    return result


WELCOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mango Disease AI API</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#e6edf3;
         display:flex;align-items:center;justify-content:center;min-height:100vh}
    .card{background:#161b22;border:1px solid #30363d;border-radius:16px;
          padding:48px 56px;max-width:600px;width:90%;text-align:center;
          box-shadow:0 8px 32px rgba(0,0,0,.4)}
    .emoji{font-size:3rem;margin-bottom:12px}
    h1{color:#3fb950;font-size:2rem;margin-bottom:8px}
    .version{color:#8b949e;font-size:.85rem;margin-bottom:16px}
    p{color:#8b949e;line-height:1.7;margin-bottom:20px}
    .install{background:#0d1117;border:1px solid #30363d;border-radius:8px;
             padding:12px 16px;font-family:monospace;font-size:.85rem;
             color:#a5d6ff;margin:16px 0;text-align:left}
    .badges{margin:16px 0 28px}
    .badge{display:inline-block;background:#1f6feb22;border:1px solid #1f6feb55;
           color:#79c0ff;border-radius:6px;padding:4px 12px;font-size:.78rem;margin:4px}
    .buttons{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:24px}
    a.btn{display:inline-block;padding:12px 28px;border-radius:8px;font-weight:600;
          text-decoration:none;font-size:.95rem;transition:opacity .2s}
    a.btn:hover{opacity:.85}
    .btn-primary{background:#3fb950;color:#0d1117}
    .btn-guide{background:#7c3aed;color:#fff}
    .btn-outline{background:transparent;color:#79c0ff;border:1px solid #1f6feb}
    .endpoints{margin-top:24px;text-align:left;background:#0d1117;border:1px solid #30363d;
               border-radius:8px;padding:16px 20px}
    .endpoints h3{color:#79c0ff;font-size:.85rem;margin-bottom:10px;letter-spacing:.05em}
    .endpoint{display:flex;align-items:center;gap:10px;padding:5px 0;font-size:.82rem;
              border-bottom:1px solid #21262d}
    .endpoint:last-child{border-bottom:none}
    .method{font-weight:700;min-width:40px;font-size:.75rem}
    .get{color:#3fb950}.post{color:#e3b341}
    .path{color:#e6edf3;font-family:monospace}
    .desc{color:#8b949e}
  </style>
</head>
<body>
  <div class="card">
    <div class="emoji">&#129389;</div>
    <h1>Mango Disease AI</h1>
    <div class="version">v__VERSION__ &bull; AIUB R&amp;D ICCA Research Group</div>
    <p>AI-powered Amropali mango disease detection API.<br>
       Detect 7 diseases, mark the affected area and get PDF reports in English or Bangla.</p>
    <div class="install">pip install mango-disease-ai[api]<br>mango-api</div>
    <div class="badges">
      <span class="badge">MAF-Net Model</span>
      <span class="badge">CLIP Validation</span>
      <span class="badge">Grad-CAM++</span>
      <span class="badge">PDF Reports</span>
      <span class="badge">7 Disease Classes</span>
    </div>
    <div class="buttons">
      <a class="btn btn-primary" href="/docs">&#128216; Swagger UI</a>
      <a class="btn btn-guide" href="/guide">&#128214; Full Docs</a>
      <a class="btn btn-outline" href="/api/health">&#10084;&#65039; Health</a>
    </div>
    <div class="endpoints">
      <h3>AVAILABLE ENDPOINTS</h3>
      <div class="endpoint"><span class="method get">GET</span><span class="path">/api/health</span><span class="desc"> - Server health check</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="path">/api/diseases</span><span class="desc"> - All 7 disease info</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="path">/api/analyze</span><span class="desc"> - Image &rarr; JSON diagnosis</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="path">/api/report</span><span class="desc"> - Image + name &rarr; PDF</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="path">/guide</span><span class="desc"> - Animated documentation</span></div>
    </div>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app(web_root: str | Path | None = None) -> FastAPI:
    """
    Build the API app.

    web_root: optional folder with ``templates/index.html`` and ``static/``. When given,
    that website is served at "/" (this is how AmropaliNet runs on the library);
    otherwise "/" shows the library welcome page.
    """
    app = FastAPI(
        title="Mango Disease AI API",
        description=(
            "AI-powered Amrapali mango disease detection (mango-disease-ai library).\n\n"
            "Upload a mango fruit or leaf photo and receive:\n"
            "- Mango check (non-mango photos are rejected)\n"
            "- Disease class (7 classes) with confidence scores\n"
            "- Grad-CAM heatmap and the likely affected area outlined\n"
            "- Symptoms and treatment\n"
            "- PDF report in English or Bangla\n\n"
            "**Model**: MAF-Net (MobileNetV2 + Multi-Scale Fusion + Coordinate Attention)  \n"
            "**Team**: AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman), "
            "supervised by Dr. Md. Saef Ullah Miah"
        ),
        version=_version(),
        contact={"name": "AIUB Student Group", "email": "arponamit.55@gmail.com", "url": "https://github.com/Arpon-30"},
        license_info={"name": "MIT"},
        lifespan=_lifespan,
    )
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    if web_root is not None:
        from fastapi.staticfiles import StaticFiles

        web_root = Path(web_root)
        app.mount("/static", StaticFiles(directory=web_root / "static"), name="static")

        @app.get("/", include_in_schema=False)
        def website():
            return FileResponse(web_root / "templates" / "index.html")
    else:
        @app.get("/", response_class=HTMLResponse, include_in_schema=False)
        def welcome():
            return WELCOME_HTML.replace("__VERSION__", _version())

    @app.get("/guide", response_class=HTMLResponse, include_in_schema=False)
    def guide():
        """Full documentation page bundled inside the package."""
        docs = Path(__file__).parent / "docs.html"
        if docs.exists():
            return HTMLResponse(docs.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>docs.html not found</h1>", status_code=404)

    @app.get("/api/health", response_model=HealthResponse, tags=["System"], summary="Health check")
    def health():
        """Server status plus whether the AI models are ready (`loading`, `ok` or `error`)."""
        return {"status": "ok", "version": _version(), **_status}

    @app.get("/api/diseases", response_model=DiseaseListResponse, tags=["Diseases"], summary="All 7 classes")
    def list_diseases():
        """Scientific name, description, symptoms and remedies for all 7 classes."""
        from mango_disease_ai.model import DISEASE_INFO

        return {"diseases": DISEASE_INFO}

    @app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Analysis"], summary="Analyze a mango photo")
    def analyze_image(
        image: UploadFile = File(..., description="Mango fruit or leaf photo (JPEG/PNG/WebP/BMP/TIFF, max 10 MB)"),
        include_gradcam: bool = Form(True, description="Include heatmap + marked area (slower). False = faster."),
    ):
        """
        Mango check (CLIP) -> disease class (MAF-Net) -> Grad-CAM++ heatmap and marked
        affected area -> disease info. Error codes are listed in the module docstring.
        """
        return _run_analysis(_read_upload(image), include_gradcam=include_gradcam)

    @app.post(
        "/api/report",
        tags=["Analysis"],
        summary="PDF diagnosis report (English or Bangla)",
        response_class=Response,
        responses={200: {"content": {"application/pdf": {}}, "description": "PDF file"}},
    )
    def generate_report(
        image: UploadFile = File(..., description="Mango fruit or leaf photo (max 10 MB)"),
        user_name: str = Form(..., description="Name printed on the report"),
        lang: str = Form("en", description="Report language: 'en' (English) or 'bn' (Bangla)"),
    ):
        """Analyze the photo and return a one-page PDF report."""
        if not user_name or not user_name.strip():
            _fail(400, "no_name", "user_name is required and cannot be empty.")
        lang = (lang or "en").strip().lower()
        if lang not in ("en", "bn"):
            _fail(400, "bad_lang", "lang must be 'en' or 'bn'.")

        result = _run_analysis(_read_upload(image))

        try:
            from mango_disease_ai import generate_pdf
            from mango_disease_ai.report_engine import BanglaPdfUnavailable

            pdf_bytes = generate_pdf(result, user_name=user_name.strip(), lang=lang)
        except BanglaPdfUnavailable as exc:
            _fail(503, "bn_pdf_unavailable", str(exc))
        except Exception as exc:
            log.exception("PDF generation failed")
            _fail(500, "report_failed", f"PDF generation failed: {exc}")

        # HTTP headers must be ASCII: plain fallback name + UTF-8 name (e.g. Bangla) per RFC 5987
        name = user_name.strip()
        ascii_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "report"
        suffix = "_BN" if lang == "bn" else ""
        disposition = (
            f'attachment; filename="AmropaliNet_Report_{ascii_name}{suffix}.pdf"; '
            f"filename*=UTF-8''{quote('AmropaliNet_Report_' + name + suffix + '.pdf')}"
        )
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": disposition})

    return app


# Default app used by `mango-api` and `uvicorn mango_disease_ai.server:app`
app = create_app()


def main():
    """Console script entry point: `mango-api`"""
    try:
        import uvicorn
    except ImportError:
        print("\n[ERROR] uvicorn is not installed.")
        print('Run: pip install "mango-disease-ai[api]"\n')
        sys.exit(1)

    parser = argparse.ArgumentParser(prog="mango-api", description="Mango Disease AI - REST API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload (development)")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(f"  Mango Disease AI - REST API server v{_version()}")
    print("=" * 60)
    print(f"  Welcome page http://localhost:{args.port}")
    print(f"  Swagger UI   http://localhost:{args.port}/docs")
    print(f"  Full docs    http://localhost:{args.port}/guide")
    print(f"  Health       http://localhost:{args.port}/api/health")
    print("  Press CTRL+C to stop.")
    print("=" * 60 + "\n")

    uvicorn.run("mango_disease_ai.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
