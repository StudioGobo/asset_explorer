# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> tree.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
from typing import AnyStr

import asset_composition

import asset_explorer


# noinspection PyUnresolvedReferences
class HierarchyTreeView(asset_explorer.View):

    identifier = "Hierarchy View"

    def __init__(self, *args, **kwargs):
        super(HierarchyTreeView, self).__init__(*args, **kwargs)

        self.setAlternatingRowColors(True)

    def populate(self, filter_value: AnyStr | None = None) -> None:

        self.clear()

        # -- Initialise with the project roots
        for root in self.app.config.get_setting("search_roots"):
            item = asset_explorer.AssetItem(
                self.app.compositor.get(root),
                app=self.app,
            )
            self.addTopLevelItem(item)

            item.populate_children()

    def navigate_to_path(self, path, from_this=None) -> None:

        if not from_this:

            # -- Start by determining which project root this path
            # -- belongs to
            for idx in range(self.topLevelItemCount()):

                root_item = self.topLevelItem(idx)

                if path.startswith(root_item.asset().identifier()):
                    root_item.setExpanded(True)
                    self.navigate_to_path(
                        path,
                        from_this=root_item,
                    )
                    break

            return

        # -- To reach here, we have a from_this node
        for idx in range(from_this.childCount()):

            child = from_this.child(idx)

            if path.startswith(child.asset().identifier()):
                child.setExpanded(True)

                if path == child.asset().identifier():
                    child.setSelected(True)
                    return

                self.navigate_to_path(
                    path,
                    from_this=child,
                )
                break
