"""
desktop/conftest.py
====================
pytest loads this before running any test under desktop/. Kept separate
from the repo's root conftest.py on purpose: pywinauto is Windows-only,
so nothing outside this folder needs to import it, and the web track
keeps working even where pywinauto isn't installed.
"""

pytest_plugins = [
    "desktop.fixtures.calculator",
]
