# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> navigation.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import asset_composition
from asset_composition._trait import _TraitAction


# --------------------------------------------------------------------------------------
class NavigationTrait(asset_composition.Trait):

    # ----------------------------------------------------------------------------------
    @classmethod
    def can_bind(cls, identifier) -> bool:
        return True

    # ----------------------------------------------------------------------------------
    def actions(self) -> list[_TraitAction]:

        if "Folder View" not in self.asset().app.config.views.identifiers():
            return []

        # -- If we're already in the folder view then we should not show this
        # -- action
        if self.asset().app.config.get_setting("active_view") == "Folder View":
            return []

        return [
            self.create_action(
                "Show in Tree View",
                self.navigate_to,
                "Navigation",
                "Show In Tree View",
            ),
        ]

    # ----------------------------------------------------------------------------------
    def navigate_to(self) -> None:
        """
        Adds the current asset to the favourites list
        """
        self.asset().app.view_panel.switch_view("Folder View")
        self.asset().app.view_panel.active_view.navigate_to_path(
            self.asset().identifier(),
        )
