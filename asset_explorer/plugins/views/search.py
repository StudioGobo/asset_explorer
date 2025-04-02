# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> search.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
from typing import AnyStr

import asset_composition

import asset_explorer


# noinspection PyUnresolvedReferences,PyPep8Naming
class SearchView(asset_explorer.View):
    """
    This is a fairly simple view that will use the filter to show
    only assets which match the given filter.
    """

    identifier = "Search View"

    def populate(self, filter_value: AnyStr | None = None) -> None:
        """
        This is triggered when the user enters some filter text, and
        for this particular view we only populate the view when that
        changes.
        """

        # -- Clear the current results before re-populating
        self.clear()

        # -- Trigger a search for assets and pass the filter string
        results = self.app.compositor.search(
            search_from=self.app.config.get_setting("search_roots") or "",
            query=filter_value,
        )

        # -- Cycle the results, adding them to the view
        for asset in sorted(results, key=lambda a: a.label()):
            asset_item = asset_explorer.AssetItem(asset, app=self.app)

            # -- Add each item as a top level item. Note that these can still
            # -- be expanded.
            self.addTopLevelItem(asset_item)
