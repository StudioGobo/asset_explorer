# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> view.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
This module contains the view base class (which is required when implementing
your own views for the explorer, as well as the factory which holds the references
to the available views.
"""
from typing import AnyStr

import factories
from Qt import QtCore, QtGui, QtWidgets


# noinspection PyUnresolvedReferences,PyPep8Naming
class View(QtWidgets.QTreeWidget):
    """
    All custom views should inherit from this and implement the three methods
    defined below.
    """

    identifier: str = ""

    def __init__(
        self,
        app: "asset_explorer.Explorer",
        parent: QtWidgets.QWidget = None,
    ):
        super().__init__(parent=parent)

        self._app: "asset_explorer.Explorer" = app
        self.populate()

        if self._app.config.get_setting("auto_sort"):
            self.sortItems(0, QtCore.Qt.AscendingOrder)
            self.setSortingEnabled(True)

        self.itemClicked.connect(self._click_propagation)
        self.itemDoubleClicked.connect(self._double_click_propagation)
        self.itemExpanded.connect(self._initialise_children)

    def populate(self, filter_value: AnyStr | None = None) -> None:
        """
        This should cause a redraw of the view. Ideally clearing out the view and
        recreating it whilst keeping the users current placement (where possible)
        """
        pass

    def _click_propagation(self, item: "AssetItem") -> None:
        """
        When the user clicks something, propagate any signalling upward
        :param item: Item being clicked
        """
        self.app.itemSelected.emit(item)

    def _double_click_propagation(self, item: "AssetItem") -> None:
        """
        When the user double clicks something, propagate any signalling upward
        :param item: Item being clicked
        """
        self.app.itemDoubleClicked.emit(item)

    def _initialise_children(self, item: "AssetItem") -> None:
        """
        Initialise a populating of the items children
        :param item: Item to initialise children for
        :return:
        """
        item.populate_children()

    # TODO: Add typing
    def mousePressEvent(self, event) -> None:
        """
        When an item is clicked we build the context menu for the current item
        """
        super(View, self).mousePressEvent(event)

        if event.button() == QtCore.Qt.RightButton:

            if not self.currentItem():
                return

            menu = self.currentItem().context_menu(parent=self)
            menu.popup(QtGui.QCursor().pos())

    @property
    def app(self) -> QtWidgets.QApplication:
        """
        Convenience read only property for accessing the app from the view
        :return:
        """
        return self._app


class ViewFactory(factories.Factory):
    """
    The trait library is a factory holding a reference to all the available traits.
    Note that this should be treated as a singleton in most situations for the
    purpose of performance.
    """

    # -- Private variable for holding the active instance
    _INSTANCE: "ViewFactory" = None

    def __init__(self, search_paths=None, exclude_builtin=False):
        # -- Initialise the parent class
        super(ViewFactory, self).__init__(
            abstract=View,
            paths=search_paths or list(),
            plugin_identifier="identifier",
        )
