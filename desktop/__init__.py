# desktop/ - the DESKTOP APP track.
#
# Playwright only drives browsers, so it cannot touch a native Windows
# app's window. This package shows the same page->helper->test layering
# as the web track (see pages/, helpers/, conftest.py at the repo root),
# built instead on pywinauto, a Python library that drives native Windows
# UI via Microsoft's UI Automation (UIA) framework - the same
# accessibility layer screen readers use, which is why it can "see" and
# click controls without any cooperation from the app itself.
