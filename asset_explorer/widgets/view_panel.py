# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> view_panel.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
from typing import AnyStr

import Qt
import qtility

from .. import delegate, view


# noinspection PyUnresolvedReferences
class ViewPanel(Qt.QtWidgets.QWidget):
    """
    The view panel is a widget which can show different view plugins.
    View plugins allow assets to be visualised in different ways. For instance
    one view plugin might show the assets as a tree, whilst others might show
    a flat list or a search mechanism or node graph etc.

    This widget is always the parent of the views we're switching between.
    """

    viewChanged = Qt.QtCore.Signal()

    def __init__(
        self,
        app: "asset_explorer.Explorer",
        parent: Qt.QtWidgets.QWidget | None = None,
    ):
        super(ViewPanel, self).__init__(parent=parent)

        # -- Store our project roots
        self.app: "asset_explorer.Explorer" = app

        # -- Define our main layout
        self.setLayout(
            qtility.layouts.slimify(
                Qt.QtWidgets.QVBoxLayout(self),
            ),
        )

        self.active_view: "asset_explorer.View" = None
        self.active_view_name: AnyStr = ""

        # -- Create the combo box that we will use to present
        # -- the available views to the user
        self.view_selector = Qt.QtWidgets.QComboBox()

        # -- Populate that combo box and ensure its set to whatever
        # -- the user last set it to
        self.populate_view_selector()
        qtility.widgets.setComboByText(
            combo_box=self.view_selector,
            label=self.app.config.get_setting("active_view"),
        )
        self.layout().addWidget(self.view_selector)

        # -- Now add the Asset Filter
        self.asset_filter = Qt.QtWidgets.QLineEdit()
        self.layout().addWidget(self.asset_filter)

        # -- Hook up our signals and slots
        self.asset_filter.returnPressed.connect(self.apply_filter)
        self.view_selector.currentIndexChanged.connect(self.switch_view)

        self.switch_view()

    def switch_view(self, desired_view: AnyStr | None = None, *args, **kwargs) -> None:
        """
        Switch the view based on what the current view combo is set to
        """
        # -- If we're told explicitly which view, then do the switch through the combo
        # -- box and allow the signal/slot to resolve
        if desired_view and isinstance(desired_view, str):
            qtility.widgets.setComboByText(self.view_selector, desired_view)
            return

        # -- If we have an active view, mark it for delete
        if self.active_view:
            self.layout().removeWidget(self.active_view)
            self.active_view.deleteLater()
            self.active_view = None

        # -- Read what view is desired
        self.active_view_name = self.view_selector.currentText()

        # -- If for any reason we dont have one, do nothing
        if not self.active_view_name:
            return

        # -- Get the widget and instance it
        view_widget: view.View = self.app.config.views.request(self.active_view_name)
        self.active_view = view_widget(
            app=self.app,
            parent=self,
        )

        # -- We always want the same delegate to be applied - this gives
        # -- visual consistency. Note that this hard coded size needs parametrising
        self.active_view.setItemDelegate(
            delegate.AssetDelegate(
                size=self.app.config.get_setting("item_size"),
            ),
        )

        # -- Finally, add the view to the layout
        self.layout().addWidget(
            self.active_view,
        )

        self.viewChanged.emit()

    def get_active_view_type(self) -> AnyStr | None:
        """
        Returns hte name of the active view
        """
        if not self.active_view:
            return None

        return self.active_view.__class__.__name__

    def apply_filter(self, *args, **kwargs) -> None:
        """
        All views implement a method to apply a filter - this allows a user to restrict
        what they are being shown
        """
        if not self.active_view:
            return

        self.active_view.populate(self.asset_filter.text())

    def populate_view_selector(self) -> None:
        """
        This will populate the combo box with all the available views.
        """
        self.view_selector.clear()

        for view_type in sorted(
            self.app.config.views.plugins(), key=lambda x: x.identifier
        ):
            self.view_selector.addItem(view_type.identifier)

    def force_refresh(self) -> None:
        """
        This will trigger a view switch even if the view name is the same
        """
        self.switch_view()
