# AmropaliNet - Docker image (website + mango-disease-ai REST API)
# Builds a CPU-only image suitable for Hugging Face Spaces (free tier)
#
# Build:  docker build -t mango-disease-ai:latest .
# Run:    docker run -p 7860:7860 mango-disease-ai:latest
# Docs:   http://localhost:7860/docs

FROM python:3.10-slim

# ── System dependencies ────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Create non-root user (required by Hugging Face Spaces) ────────────────
RUN useradd -m -u 1000 appuser
WORKDIR /app

# ── Install Python dependencies ───────────────────────────────────────────
# Copy requirements first for better Docker layer caching
COPY api/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Hugging Face cache (CLIP mango checker lives here) ───────────────────
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV USE_TF=0
ENV TRANSFORMERS_NO_TF=1

# Download the CLIP mango checker (~600 MB) at build time, so the live site
# does not download it again after every restart / wake-up.
RUN python -c "from transformers import CLIPModel, CLIPProcessor; \
CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); \
CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')"

# ── Copy application code ─────────────────────────────────────────────────
COPY mango_disease_ai/ ./mango_disease_ai/
COPY api/ ./api/
COPY templates/ ./templates/
COPY static/ ./static/

# ── Ownership ──────────────────────────────────────────────────────────────
RUN chown -R appuser:appuser /app
USER appuser

# ── Expose port 7860 (Hugging Face Spaces default) ────────────────────────
EXPOSE 7860

# ── Start FastAPI with uvicorn ─────────────────────────────────────────────
CMD ["uvicorn", "api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "7860", \
     "--workers", "1", \
     "--timeout-keep-alive", "120"]
