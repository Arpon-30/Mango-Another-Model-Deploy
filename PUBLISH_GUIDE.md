# Publish `mango-disease-ai` v0.2.0 on PyPI

The library code lives in `mango_disease_ai/` (model, fonts and Bangla text included).
The website (`api/main.py`) runs on the same code, so what you publish is exactly what the
website uses.

## 1. Build (Windows PowerShell, inside the project folder)

```powershell
& "E:\Anaconda\envs\tf_new\python.exe" -m pip install --upgrade build twine
& "E:\Anaconda\envs\tf_new\python.exe" -m build
```

This creates two files in `dist\`:
`mango_disease_ai-0.2.0-py3-none-any.whl` and `mango_disease_ai-0.2.0.tar.gz` (about 17 MB each - the model is inside).

## 2. Check

```powershell
& "E:\Anaconda\envs\tf_new\python.exe" -m twine check dist\*
```

Both lines must say `PASSED`.

## 3. Upload

```powershell
& "E:\Anaconda\envs\tf_new\python.exe" -m twine upload dist\*
```

- Username: `__token__`
- Password: your PyPI **API token** (starts with `pypi-`). Create one at
  https://pypi.org/manage/account/token/ - never commit it or share it.

PyPI does not allow the same version twice. For the next release, raise the version in
**both** `pyproject.toml` and `mango_disease_ai/__init__.py` (for example `0.2.1`).

## 4. Test like a developer

```powershell
& "E:\Anaconda\envs\tf_new\python.exe" -m pip install --upgrade "mango-disease-ai[api]"
mango-api
```

Open http://localhost:8000/docs and try `/api/analyze` with a mango photo.

## Keep your account safe

- PyPI **recovery codes** and **API tokens** are passwords. Keep them out of this project
  folder, ZIP files, chats and GitHub. `.gitignore` blocks files named `*Recovery-Codes*`.
- If a recovery code file was ever shared, create new codes in PyPI account settings
  (this cancels the old ones).
