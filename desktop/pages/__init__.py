# desktop/pages/ - one class per app, the desktop equivalent of pages/
# in the web track: WHERE things are (control names/ids) and what a user
# can do (methods). Tests and helpers never touch pywinauto directly.

from desktop.pages.base_app import BaseApp
from desktop.pages.calculator_page import CalculatorPage
