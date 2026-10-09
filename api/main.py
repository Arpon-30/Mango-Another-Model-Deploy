"""
AmropaliNet web app
===================
The website runs on the REST API of our own library, ``mango-disease-ai``
(``mango_disease_ai.server``, also published on PyPI). This file only adds the
website pages on top of it.

Run locally:
    python run.py                                  (opens the browser)
    uvicorn api.main:app --reload --port 8000

Then visit: http://localhost:8000 (website) · /docs (API) · /guide (library docs)
"""

from pathlib import Path

from mango_disease_ai.server import create_app

app = create_app(web_root=Path(__file__).resolve().parent.parent)
