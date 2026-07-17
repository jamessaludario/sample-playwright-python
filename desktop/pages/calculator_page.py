"""
desktop/pages/calculator_page.py
=================================
Windows Calculator - the ONE place that knows the names of its buttons
and how to read its result display. Desktop apps have nothing like the
web's data-qa attributes, so we automate by the same accessible name a
screen reader announces for each button ("One", "Plus", "Equals", ...).

These names come from Microsoft's own Calculator (confirmed against
pywinauto's published examples). If a Windows update ever renames one,
re-discover it with:
    python -m pywinauto.application  # or
    CalculatorPage().open().window.print_control_identifiers()
and fix it here - this is the only file that would need to change.
"""

import re

from desktop.pages.base_app import BaseApp

_DIGIT_NAMES = {
    "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
    "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine",
}
_OPERATOR_NAMES = {"+": "Plus", "-": "Minus", "*": "Multiply by", "/": "Divide by"}


class CalculatorPage(BaseApp):
    app_path = "calc.exe"
    window_title = "Calculator"

    def _click_button(self, accessible_name: str):
        self.window.child_window(
            title=accessible_name, control_type="Button"
        ).click_input()

    def press_number(self, number: int):
        """Press each digit of `number` in order, e.g. press_number(42) -> 4, 2."""
        for digit in str(number):
            self._click_button(_DIGIT_NAMES[digit])

    def press_operator(self, operator: str):
        """Press an operator button: one of + - * /."""
        self._click_button(_OPERATOR_NAMES[operator])

    def press_equals(self):
        self._click_button("Equals")

    def clear(self):
        """Reset the display to 0, so tests always start from a clean state."""
        self._click_button("Clear")

    def result_text(self) -> str:
        """
        The result display's full accessible text, e.g. "Display is 12".
        Exposed raw (like the web tests asserting on visible text) so
        a test can check it directly with plain equality/`in`.
        """
        return self.window.child_window(
            auto_id="CalculatorResults", control_type="Text"
        ).window_text()

    def result_value(self) -> str:
        """Just the number part of result_text(), e.g. "12"."""
        match = re.search(r"-?[\d.,]+$", self.result_text())
        return match.group().replace(",", "") if match else ""
