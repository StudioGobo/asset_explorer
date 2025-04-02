# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> maya_scene.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
This discovery mechanism will search the paleobio rest api for a dinosaur
and return the results
"""
import maya.cmds as mc
import asset_composition


class MayaAssetSearch(asset_composition.DiscoveryPlugin):
    """
    Discovery traits allow us to expose a mechanism of searching. In this case we
    expose a mechanism to search for local files/folders within a users machine.
    """
    @classmethod
    def search(cls, query, search_from=None):
        results = []

        search_attribute_tests = [
            "aniseed_rig",
            "project_asset",
        ]

        for item in mc.ls(query, recursive=True, o=True):
            matched = False
            for search_attribute in search_attribute_tests:
                if mc.objExists("%s.%s" % (item, search_attribute)):
                    matched = True
                    break

            if not matched:
                continue

            results.append(item)

        return sorted(results)
