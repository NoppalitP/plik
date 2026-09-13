"""Plik (พลิก): Next-Gen Intelligent Thai-English Keyboard Switcher & Auto-Corrector."""

import sys

__version__ = "1.0.0"

# Register alias in sys.modules so legacy plik imports resolve smoothly
if "plik" not in sys.modules:
    sys.modules["plik"] = sys.modules[__name__]
