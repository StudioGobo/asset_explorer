# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> item.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import weakref

import asset_composition
from Qt import QtCore, QtWidgets

from .. import constants, icons


# noinspection PyUnresolvedReferences
class AssetItem(QtWidgets.QTreeWidgetItem):
    """
    All views should use the AssetItem class. This takes in an asset and keeps a pointer
    to it. It also manages any changed requests as well as any data that needs to be
    passed to the delegate.
    """

    def __init__(
        self,
        asset: asset_composition.Asset,
        app: "asset_explorer.Explorer",
        *args,
        **kwargs,
    ):
        super(AssetItem, self).__init__(*args, **kwargs)

        # -- Store a reference to the panel and the asset
        self._app: "asset_explorer.Explorer" = app
        self._asset: asset_composition.Asset = asset

        # -- Store a reference to the panel on the asset, and connect the
        # -- asset changed events
        self._asset.app = self._app
        self._asset.status_changed.connect(self.update_data)
        self._asset.changed.connect(
            self.populate_children,
        )

        # -- Finally we trigger a data update which scrapes the
        # -- asset data into teh data roles which can be used
        # -- by the delegates
        self.update_data()

    @property
    def app(self) -> "asset_explorer.Explorer":
        """
        Convenience read only property to access the app from the item
        :return:
        """
        return self._app

    def update_data(self, *args, **kwargs) -> None:
        """
        This will read the asset state and store the required data in the data
        roles - which allow the delegate to access important information.
        """
        try:
            self.setText(0, f"{self._asset.label()} :: " + str(self._asset))

        except RuntimeError:
            return

        self.setData(
            0,
            QtCore.Qt.DecorationRole,
            self._asset.icon(),
        )

        self.setData(
            0,
            QtCore.Qt.DisplayRole,
            self._asset.label(),
        )

        self.setData(0, constants.STATUS_ICONS_ROLE, self._asset.status_icons())

        self.setData(0, constants.DATA_ROLE, self._asset.custom_data())

    def populate_children(
        self,
        regenerate: bool = False,
        expand_additional_depth: bool = True,
    ) -> None:
        """
        This method will attempt to spawn additional AssetItem classes
        as children of the current one. Children are always provided
        by the asset traits rather that inferred.
        """

        # if self.childCount():
        #     return

        # -- Clear current children before we repopulate it. But wrap it
        # -- in a try in case we have a threaded callback.
        try:
            while self.childCount():
                self.removeChild(self.child(0))

            # -- Get a list of children which we consider to
            # -- be relevant to show
            assets = []

            for child in self.asset().children():
                asset_ = self.app.compositor.get(child)
                assets.append(asset_)

            for asset_ in assets:
                child_item = AssetItem(asset_, app=self.app)
                self.addChild(child_item)
                asset_.ui_item = weakref.ref(child_item)

                if not asset_.is_visible():
                    child_item.setHidden(True)

            # -- If we need to expand an additional depth (to be able to show the
            # -- "has children" icon, then initialise that now too
            if expand_additional_depth:
                for idx in range(self.childCount()):
                    child_item = self.child(idx)

                    child_item.populate_children(
                        expand_additional_depth=False,
                    )

        except RuntimeError:
            pass

    def asset(self) -> asset_composition.Asset:
        """
        This gives access to the asset this item represents
        :return:
        """
        return self._asset

    def context_menu(self, parent: QtWidgets.QWidget = None) -> QtWidgets.QMenu:
        """
        This will generate the qmenu for this item based on all the actions
        defined in traits for the asset.

        Args:
            parent: The parent widget for the menu

        Returns:
            The QMenu
        """
        # -- Create a new menu
        menu: QtWidgets.QMenu = QtWidgets.QMenu(parent)

        # -- Before populating the menu, group all the actions by their
        # -- given categories
        menus_by_category = {}

        for action in self._asset.actions():
            if not action.category() in menus_by_category:
                menus_by_category[action.category()] = []
            menus_by_category[action.category()].append(action)

        # -- Now our data is constructed per category we can start to
        # -- add them to the menu
        for category in sorted(menus_by_category):

            # -- Always split the categories by a separator
            menu.addSeparator()

            sorted_actions: list = sorted(
                menus_by_category[category], key=lambda action: action.name()
            )

            # -- Now add each item
            for action in sorted_actions:

                # -- Build the action item
                menu_action: QtWidgets.QAction = QtWidgets.QAction(
                    icons.build_icon(action.icon()),
                    action.name(),
                    menu,
                )

                # -- Connect the menu action signal/slot
                menu_action.triggered.connect(action.function)

                # -- Finally add the action to the menu
                menu.addAction(menu_action)

        return menu
