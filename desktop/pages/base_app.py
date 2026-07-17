"""
desktop/pages/base_app.py
==========================
The parent class every desktop page object inherits from. It plays the
same role BasePage (pages/base_page.py) plays for the web track: launch
"your" app and hand back its main window, so the child class can get
straight to describing controls.
"""

from pywinauto import Desktop
from pywinauto.application import Application


class BaseApp:
    # Child classes (CalculatorPage, ...) override these with "their"
    # app's launch command and window title, the same way LoginPage
    # overrides BasePage.path.
    app_path = None
    window_title = None

    def __init__(self):
        self.app = None
        self.window = None

    def open(self):
        """
        Launch the app and grab its main window.

        backend="uia" talks to apps through UI Automation, the framework
        that also powers screen readers - it understands modern
        Windows/UWP apps (Calculator, Settings, Store apps). The older
        backend="win32" only sees classic win32 controls and simply
        won't find these at all, so uia is the safer default here.

        We start the app, then look its window up SEPARATELY through
        Desktop(...) by title, rather than through the Application object
        start() gave us. Reason: several modern Windows apps (Calculator
        included) launch via a short-lived stub process that immediately
        hands off to the real app process under a DIFFERENT process id.
        Application.start()'s own window() lookup filters by the stub's
        (now-dead) pid, so it waits the full timeout and fails even
        though the window is genuinely on screen - it was just being
        searched for under the wrong process. Desktop(...).window()
        matches by title alone, so it isn't fooled by the handoff.
        """
        Application(backend="uia").start(self.app_path)

        # Like expect(...) on the web side, this POLLS instead of a
        # fixed sleep: it waits until the window reports itself visible
        # and ready to receive input, up to 10 seconds, then continues
        # the moment it's true (often much sooner).
        self.window = Desktop(backend="uia").window(title=self.window_title)
        self.window.wait("visible ready", timeout=10)

        # Now that we've found the REAL window, connect an Application to
        # ITS process (not the stub's) so close() below can kill the app
        # that's actually running instead of an already-dead process.
        self.app = Application(backend="uia").connect(
            process=self.window.element_info.process_id
        )
        return self

    def close(self):
        """
        Force-close the app and everything it spawned. Tests call this
        in cleanup (via the `calculator` fixture) so apps never pile up
        between test runs, the same way delete_account() cleans up
        accounts on the web side.
        """
        if self.app is not None:
            self.app.kill()
