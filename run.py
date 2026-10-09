"""
Start AmropaliNet with one click (VS Code ▶ Run) or: python run.py
Opens http://localhost:8000 in your browser.

Small missing packages (for example uharfbuzz, needed for the Bangla PDF) are
installed automatically on start. Big ones (PyTorch etc.) come from:
    python -m pip install -r api/requirements.txt
"""

import importlib.util
import os
import subprocess
import sys
import threading
import webbrowser

# PyTorch only: keep transformers from importing TensorFlow/Keras if installed
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

PORT = 8000

# import name -> pip requirement (small packages, safe to install automatically)
SMALL_PACKAGES = {
    "uharfbuzz": "uharfbuzz==0.56.2",
    "fastapi": "fastapi==0.115.0",
    "uvicorn": "uvicorn[standard]==0.32.0",
    "multipart": "python-multipart==0.0.12",
    "fpdf": "fpdf2==2.8.2",
}
# import name -> what to tell the user (large packages, installed from requirements)
BIG_PACKAGES = ["torch", "torchvision", "timm", "transformers", "cv2", "scipy", "PIL", "numpy"]


def _missing(names):
    return [n for n in names if importlib.util.find_spec(n) is None]


def ensure_packages() -> None:
    missing_small = _missing(SMALL_PACKAGES)
    if missing_small:
        specs = [SMALL_PACKAGES[n] for n in missing_small]
        print("Installing missing packages:", ", ".join(specs))
        subprocess.run([sys.executable, "-m", "pip", "install", *specs], check=False)
        importlib.invalidate_caches()

    missing_big = _missing(BIG_PACKAGES)
    if missing_big:
        print("\nThese packages are missing:", ", ".join(missing_big))
        print("Install everything once with:")
        print(f'  "{sys.executable}" -m pip install -r api/requirements.txt\n')
        sys.exit(1)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ensure_packages()

    import uvicorn

    threading.Timer(2.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    uvicorn.run("api.main:app", host="127.0.0.1", port=PORT)
