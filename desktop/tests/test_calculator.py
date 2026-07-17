"""
Desktop Test: Add two numbers on Windows Calculator
====================================================
The desktop-track equivalent of the web track's simplest test: it shows
the whole chain working end to end (fixture -> helper -> page object)
without anything specific to arithmetic getting in the way.

Run just this file with:
    pytest --confcutdir=desktop desktop/tests/test_calculator.py --reruns 0

--confcutdir=desktop stops pytest from also loading the root conftest.py
- without it, the web track's autouse ad-blocker fixture (which needs a
browser) would attach itself to these tests too, since autouse fixtures
apply repo-wide by default, not just to the folder that defines them.
--reruns 0 turns off the web track's default retry-on-failure - useful
there for a flaky website, not useful here.
"""

from pywinauto.timings import wait_until_passes

from desktop.helpers.flows import compute


def test_add_two_numbers(calculator):
    # The `calculator` fixture (desktop/fixtures/calculator.py) already
    # launched a fresh Calculator for us, and will close it afterwards.
    compute(calculator, 7, "+", 5)

    def result_is_12():
        assert calculator.result_value() == "12"

    # Like expect(...) on the web side: poll for up to 5 seconds instead
    # of asserting once, in case the display takes a moment to update.
    wait_until_passes(5, 0.2, result_is_12)


def test_each_test_gets_a_fresh_calculator(calculator):
    # No cleanup needed here: this is a NEW Calculator instance (the
    # fixture reruns for every test), so it always starts at 0.
    def starts_at_zero():
        assert calculator.result_value() == "0"

    wait_until_passes(5, 0.2, starts_at_zero)
