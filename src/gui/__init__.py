# -*- coding: utf-8 -*-

"""This package is intended to contain the UI code. It exposes a reference to
the application main window which is needed by the controller at startup and in
those cases when view updates must be triggered explicitly.
"""

from src.gui.window import get_main_window
from src.gui.res import resources
