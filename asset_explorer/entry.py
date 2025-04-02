# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> entry.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
This module creates an easy and user friendly entry point. This is useful
if you're planning to immediately deploy the tool and allow the user to
configure it.
"""
import qtility
from Qt import QtWidgets

from . import config
from .widgets.app import AppWindow


# noinspection PyUnresolvedReferences
def launch(
    configuration: config.Configuration,
    blocking: bool = True,
    parent: QtWidgets.QWidget | None = None,
) -> QtWidgets.QWidget:
    """
    This function is the main entry point to launching the asset browser. You should
    provide it with the project roots.

    Arguments:
        configuration (config.Configuration): A configuration instance to allow
            the tool to utilise all the traits, discoveries and views.
        blocking (bool, optional): If True, the app will block the main loop until
        parent (QWidget | None, optional): Parent to place the window under
    """

    # -- Get the QApplication instance. This will generate one for us if one
    # -- is not already running
    qapp: QtWidgets.QApplication = qtility.app.get()

    # -- Instance the window and show it
    w = AppWindow(
        configuration=configuration,
        parent=parent,
    )
    w.show()

    # -- If we're blocking (i.e, running standalone) call the exec_ blocking
    # -- thread. Typically, you don't want to do this if you're running the
    # -- explorer within another application that is managing the QApplication
    # -- instance
    if blocking:
        qapp.exec_()

    # -- Return the widget in case any external tool wants to interact with
    # -- it.
    return w
