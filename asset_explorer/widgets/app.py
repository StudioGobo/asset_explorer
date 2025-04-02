# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> app.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import asset_composition
from Qt import QtCore, QtWidgets

from .. import config, icons
from . import preferences, view_panel


# noinspection PyUnresolvedReferences
class Explorer(QtWidgets.QWidget):
    """
    This is the main Asset Explorer Widget which hosts the view panel
    and preferences.
    """

    itemSelected: QtCore.Signal = QtCore.Signal(object)
    itemDoubleClicked: QtCore.Signal = QtCore.Signal(object)

    def __init__(
        self,
        configuration: config.Configuration,
        parent: QtWidgets.QWidget | None = None,
    ):
        super(Explorer, self).__init__(parent=parent)

        # -- If we're not given a key we use a default
        self._config: config.Configuration = configuration
        self._compositor = asset_composition.Compositor(self._config)

        # -- Define the base layout of the widget
        self.setLayout(QtWidgets.QVBoxLayout())

        # -- Add in the tab widget
        self.tab_widget: QtWidgets.QTabWidget = QtWidgets.QTabWidget(parent=self)

        # -- Build the view panel and the preferences widgets
        self.view_panel = view_panel.ViewPanel(app=self)
        self.preferences = preferences.PreferencesWidget(app=self)

        # -- Add the widgets to their respective tabs
        self.tab_widget.addTab(self.view_panel, "Explorer")
        self.tab_widget.addTab(self.preferences, "Preferences")

        # -- Add the tab widget to the layout
        self.layout().addWidget(self.tab_widget)

        # -- Hook up any signals and slots
        self.view_panel.viewChanged.connect(self.preferences.serialise_changes)

    @property
    def config(self) -> config.Configuration:
        """
        Many submodules and widgets will want immediate access to the explorers
        settings, as this is where the users preferences are stored and read from.
        """
        return self._config

    @property
    def compositor(self) -> asset_composition.Compositor:
        return self._compositor


# noinspection PyUnresolvedReferences
class AppWindow(QtWidgets.QMainWindow):
    """
    This is a wrapping window holding the main widget
    """

    def __init__(
        self,
        configuration: config.Configuration,
        parent: QtWidgets.QWidget | None = None,
    ):
        super(AppWindow, self).__init__(parent=parent)

        # -- Instance the application widget
        self.setCentralWidget(
            Explorer(
                configuration=configuration,
                parent=self,
            ),
        )

        # -- Set the branding properties
        self.setWindowTitle("Asset Explorer")
        self.setWindowIcon(icons.build_icon("Entity"))
