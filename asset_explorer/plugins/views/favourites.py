# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> favourites.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
from typing import AnyStr

import asset_composition

import asset_explorer


# noinspection PyUnresolvedReferences
class FavouritesView(asset_explorer.View):
    """
    This view will present the user with any items which have been marked
    as favourites.
    """

    identifier = "Favourites View"

    def __init__(self, *args, **kwargs):
        super(FavouritesView, self).__init__(*args, **kwargs)
        self.populate()

    def populate(self, filter_value: AnyStr | None = None) -> None:

        # -- Clear the current contents before we start repopulating
        self.clear()

        # -- Ensure we're always working with a string
        # -- filter
        filter_value = filter_value or ""

        # -- Cycle the favourites we have stored
        for favourite in self.app.config.get_setting("favourites"):

            # -- Get the asset for this item
            asset = self.app.compositor.get(
                favourite,
            )

            # -- If the filter text does not match we skip
            # -- over it.
            if filter_value not in asset.label():
                continue

            # -- Now that we know we need to display this item we
            # -- can instance the item object and add it as a top
            # -- level item
            item = asset_explorer.AssetItem(asset, app=self.app)
            self.addTopLevelItem(item)

            # -- Ensure we populate its children. This is important
            # -- as it will show a chevron if it has children.
            item.populate_children()
