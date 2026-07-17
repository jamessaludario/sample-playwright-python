"""
desktop/helpers/flows.py
=========================
User JOURNEYS for the Calculator app - the desktop equivalent of
helpers/flows.py on the web side. Same layering:

    test  ->  desktop/helpers/flows.py  ->  desktop/pages/  ->  the app
    (WHAT to verify)     (the journey)      (WHERE things are)

Notice these functions don't know any button names - only CalculatorPage
(desktop/pages/calculator_page.py) does.
"""

from desktop.pages.calculator_page import CalculatorPage


def compute(calculator: CalculatorPage, first: int, operator: str, second: int):
    """
    Key in `first operator second =` on the given (already open)
    calculator, e.g. compute(calculator, 7, "+", 5) presses 7, +, 5, =.
    """
    calculator.press_number(first)
    calculator.press_operator(operator)
    calculator.press_number(second)
    calculator.press_equals()
