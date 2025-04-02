# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> favourite.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import asset_composition
from asset_composition._trait import _TraitAction


# --------------------------------------------------------------------------------------
class FavouritesTrait(asset_composition.Trait):

    # ----------------------------------------------------------------------------------
    @classmethod
    def can_bind(cls, identifier) -> bool:
        return True

    # ----------------------------------------------------------------------------------
    def actions(self) -> list[_TraitAction]:

        if self.asset().identifier() in self.asset().app.config.get_setting(
            "favourites"
        ):
            return [
                self.create_action(
                    "Remove From Favourites",
                    self.remove_from_favourites,
                    "Favourites",
                    "Remove From Favourites",
                ),
            ]

        return [
            self.create_action(
                name="Add To Favourites",
                function=self.add_to_favourites,
                category="Favourites",
                icon="Add To Favourites",
            ),
        ]

    # ----------------------------------------------------------------------------------
    def add_to_favourites(self) -> None:
        """
        Adds the current asset to the favourites list
        """
        self.asset().app.config.add_to("favourites", self.asset().identifier())
        self.asset().status_changed.emit()

    # ----------------------------------------------------------------------------------
    def remove_from_favourites(self) -> None:
        """
        Removes the current asset from the favourites
        """
        self.asset().app.config.remove_from("favourites", self.asset().identifier())
        self.asset().status_changed.emit()

    def status_icons(self) -> list[str]:
        if self.asset().identifier() in self.asset().app.config.get_setting(
            "favourites"
        ):
            return ["Favourite"]
        return list()
