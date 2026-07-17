"""
desktop/fixtures/calculator.py
================================
The `calculator` fixture: the desktop-track equivalent of the `page`
fixture pytest-playwright gives the web track. It launches a fresh
Calculator before each test and guarantees it's closed afterwards, so
tests never manage the app's lifecycle themselves.
"""

import pytest

from desktop.pages.calculator_page import CalculatorPage


@pytest.fixture
def calculator():
    app = CalculatorPage().open()
    yield app
    app.close()
