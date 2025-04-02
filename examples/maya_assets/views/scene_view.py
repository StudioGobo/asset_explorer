# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> scene_view.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import typing
import asset_explorer
import asset_composition


# noinspection PyUnresolvedReferences
class SceneView(asset_explorer.View):
    """
    This view will present the user with any items which have been marked
    as favourites.
    """
    identifier = "Scene View"

    def __init__(self, *args, **kwargs):
        super(SceneView, self).__init__(*args, **kwargs)
        self.populate()

    def populate(self, filter_value: typing.AnyStr or None = None):

        # -- Clear the current contents before we start repopulating
        self.clear()

        # -- Ensure we're always working with a string
        # -- filter
        filter_value = filter_value or ""

        # -- Cycle the favourites we have stored
        for asset in self.app.compositor.search(filter_value or "*"):
            # -- Now that we know we need to display this item we
            # -- can instance the item object and add it as a top
            # -- level item
            item = asset_explorer.AssetItem(asset, app=self.app)
            self.addTopLevelItem(item)

            # -- Ensure we populate its children. This is important
            # -- as it will show a chevron if it has children.
            item.populate_children()
