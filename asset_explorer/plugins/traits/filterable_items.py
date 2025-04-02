# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> filterable_items.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import asset_composition
from asset_composition._trait import _TraitAction


# --------------------------------------------------------------------------------------
class FilterableTrait(asset_composition.Trait):

    # ----------------------------------------------------------------------------------
    @classmethod
    def can_bind(cls, identifier) -> bool:
        return True

    def is_visible(self) -> bool:
        if self.asset().label() in self.asset().app.config.get_setting(
            "filtered_labels"
        ):
            return False
        return True

    # ----------------------------------------------------------------------------------
    def actions(self) -> list[_TraitAction]:

        if not self.is_visible():
            return []

        return [
            self.create_action(
                "Filter Out",
                self.filter_out,
                "Query",
            ),
        ]

    # ----------------------------------------------------------------------------------
    def filter_out(self) -> None:
        """
        Adds the current asset to the favourites list
        """
        self.asset().app.config.add_to(
            "filtered_labels",
            self.asset().label(),
        )
        self.asset().changed.emit()
        self.asset().ui_item().setHidden(True)
