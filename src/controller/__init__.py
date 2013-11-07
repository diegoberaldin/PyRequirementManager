# -*- coding: utf-8 -*-

"""This package contains the application controller and should not be imported
anywhere except in the application entry point where the controller must be
instantiated and started.
"""

# needed at startup for controller initialization
from src.controller.events import ApplicationController
