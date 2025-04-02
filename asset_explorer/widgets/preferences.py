# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> preferences.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
This module stores the widgets for allowing users to interact with and
define their browser preferences
"""
import qfactory
import qtility
from Qt import QtCore, QtGui, QtWidgets

from .. import resources


class PreferencesWidget(QtWidgets.QWidget):
    """
    This is the main preferences widget that can be embedded into tools
    """

    changed: QtCore.Signal = QtCore.Signal()

    # ----------------------------------------------------------------------------------
    def __init__(self, app: "asset_explorer.Explorer", parent=None):
        super(PreferencesWidget, self).__init__(parent=parent)

        self.app: "asset_explorer.Explorer" = app

        # -- Set our basic layout
        self.setLayout(QtWidgets.QVBoxLayout(self))

        # -- Load in our ui file
        self.ui = qtility.designer.load(
            resources.get("preferences.ui"),
        )
        self.layout().addWidget(self.ui)

        self.filters_editor = FilterOptionsWidget(app=self.app)
        self.ui.preferences_layout.addWidget(self.filters_editor)

        self.search_editor = SearchRootsWidget(app=self.app)
        self.ui.preferences_layout.addWidget(self.search_editor)

        # -- Create our factory editing widgets
        self.trait_editor = qfactory.FactoryWidget(self.app.config.traits)
        self.discovery_editor = qfactory.FactoryWidget(self.app.config.discovery)
        self.view_editor = qfactory.FactoryWidget(self.app.config.views)

        # -- Add them to their corresponding layouts
        self.ui.traits_layout.insertWidget(0, self.trait_editor)
        self.ui.searches_layout.insertWidget(0, self.discovery_editor)
        self.ui.views_layout.insertWidget(0, self.view_editor)

        # -- Populate our static values
        self.populate()

        # -- Hook up the signals and slots
        self.app.config.traits.plugins_changed.connect(self.reflect_change)
        self.app.config.discovery.plugins_changed.connect(self.reflect_change)
        self.app.config.views.plugins_changed.connect(self.reflect_change)
        self.ui.item_size.valueChanged.connect(self.reflect_change)
        self.ui.auto_sort.stateChanged.connect(self.reflect_change)
        self.filters_editor.changed.connect(self.reflect_change)
        self.search_editor.changed.connect(self.reflect_change)

    def populate(self) -> None:
        self.ui.item_size.setValue(
            self.app.config.get_setting("item_size"),
        )
        self.ui.auto_sort.setChecked(self.app.config.get_setting("auto_sort"))

    def reflect_change(self) -> None:

        # -- Write everything to the config before we instigate a refresh,
        # -- that way any changes we make in the config will be reflected
        self.serialise_changes()

        # -- Get the current view, then re-populate the view
        # -- list (as the factories may have changed). Then
        # -- switch the view - which will cause it to redraw
        current_view = self.app.view_panel.active_view.identifier
        self.app.view_panel.populate_view_selector()

        self.app.view_panel.switch_view(current_view)

        # -- As we may have changed traits, clear the
        # -- cache on the compositor too
        self.app.compositor.get.cache_clear()

    def serialise_changes(self) -> None:

        self.app.config.set_setting(
            "search_roots",
            self.search_editor.paths(),
        )

        self.app.config.set_setting(
            "filtered_labels",
            self.filters_editor.labels(),
        )
        # -- Store the settings
        self.app.config.set_setting(
            "item_size",
            self.ui.item_size.value(),
        )

        self.app.config.set_setting(
            "auto_sort",
            self.ui.auto_sort.isChecked(),
        )

        self.app.config.set_setting(
            "active_view",
            self.app.view_panel.active_view.identifier,
        )

        # -- Finally, serialise the config - this will ensure
        # -- that if it came from a persistent file, that that
        # -- file will update and keep the changes
        self.app.config.serialise()


# noinspection PyUnresolvedReferences,PyPep8Naming
class FilterOptionsWidget(QtWidgets.QWidget):
    """
    This is a bespoke widget for managing filters. A filter is a pattern
    which the user has chosen to add to restrict what is shown in a view
    """

    # -- This signal will be emitted whenever the value of this
    # -- widget changes
    changed = QtCore.Signal()

    def __init__(self, app: "asset_explorer.Explorer", parent=None):
        super(FilterOptionsWidget, self).__init__(parent=parent)

        self.app: "asset_explorer.Explorer" = app

        # -- Build our base layout
        self.setLayout(
            QtWidgets.QVBoxLayout(self),
        )

        self.label = QtWidgets.QLabel("Filters")
        self.layout().addWidget(self.label)

        # -- Create our sub widgets
        self.item_list = QtWidgets.QListWidget(self)
        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        # -- Add our subwidgets the main layout
        self.layout().addWidget(self.item_list)
        self.layout().addWidget(self.add_button)
        self.layout().addWidget(self.remove_button)

        # -- Hook up our signals and slots
        self.remove_button.clicked.connect(self.remove)
        self.add_button.clicked.connect(self.add)

        # -- Finally we populate the list
        self.populate()

    def labels(self) -> list:
        return [
            self.item_list.item(idx).text() for idx in range(self.item_list.count())
        ]

    def populate(self) -> None:
        """
        This will populate the list with all the filters defined in the
        settings
        """
        # -- Start by clearing out the current values
        self.item_list.clear()

        # -- Add the values from the settings into the filter list
        for item in self.app.config.get_setting("filtered_labels"):
            self.item_list.addItem(item)

    def remove(self) -> None:
        """
        This will remove the selected filter from the list
        """
        # -- If nothing is selected then we do nothing
        if not self.item_list.currentItem():
            return

        # -- Take the item from the list
        item = self.item_list.takeItem(self.item_list.currentRow())
        self.app.config.remove_from("filtered_labels", item.text())

        # -- Emit the fact that this has changed
        self.changed.emit()

    def add(self) -> None:
        item_to_add = qtility.request.text(
            title="Add Filter",
            message="Please type a filter to add",
            parent=self,
        )
        if not item_to_add:
            return

        self.item_list.addItem(item_to_add)
        self.app.config.add_to("filtered_labels", item_to_add)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """
        This is triggered when the filter option is shown, so we repopulate the
        view
        """
        self.populate()


# noinspection PyUnresolvedReferences,PyPep8Naming
class SearchRootsWidget(QtWidgets.QWidget):
    # -- This signal will be emitted whenever the value of this
    # -- widget changes
    changed = QtCore.Signal()

    def __init__(self, app: "asset_explorer.Explorer", parent=None):
        super(SearchRootsWidget, self).__init__(parent=parent)

        self.app: "asset_explorer.Explorer" = app

        # -- Build our base layout
        self.setLayout(
            QtWidgets.QVBoxLayout(self),
        )

        self.label = QtWidgets.QLabel("Search Roots")
        self.layout().addWidget(self.label)

        # -- Create our sub widgets
        self.item_list = QtWidgets.QListWidget(self)
        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        # -- Add our subwidgets the main layout
        self.layout().addWidget(self.item_list)
        self.layout().addWidget(self.add_button)
        self.layout().addWidget(self.remove_button)

        # -- Hook up our signals and slots
        self.remove_button.clicked.connect(self.remove)
        self.add_button.clicked.connect(self.add)

        # -- Finally we populate the list
        self.populate()

    def paths(self) -> list:
        return [
            self.item_list.item(idx).text() for idx in range(self.item_list.count())
        ]

    def populate(self) -> None:
        """
        This will populate the list with all the filters defined in the
        settings
        """
        # -- Start by clearing out the current values
        self.item_list.clear()

        # -- Add the values from the settings into the filter list
        for item in self.app.config.get_setting("search_roots"):
            self.item_list.addItem(item)

    def remove(self) -> None:
        """
        This will remove the selected filter from the list
        """
        # -- If nothing is selected then we do nothing
        if not self.item_list.currentItem():
            return

        # -- Take the item from the list
        item = self.item_list.takeItem(self.item_list.currentRow())
        self.app.config.remove_from("search_roots", item.text())

        # -- Emit the fact that this has changed
        self.changed.emit()

    def add(self) -> None:
        search_roots = self.app.config.get_setting("search_roots")
        start_point = "" if len(search_roots) == 0 else search_roots[0]

        item_to_add = qtility.request.folderpath(
            title="Add Search Root",
            path=start_point,
            parent=self,
        )

        if not item_to_add:
            return

        self.item_list.addItem(item_to_add)
        self.app.config.add_to("search_roots", item_to_add)
        self.changed.emit()

    def showEvent(self, event: QtGui.QShowEvent):
        """
        This is triggered when the filter option is shown, so we repopulate the
        view
        """
        self.populate()
