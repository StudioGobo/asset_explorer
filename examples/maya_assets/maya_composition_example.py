# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> maya_composition_example.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
Note: This example is intended only to be run within Autodesk Maya and will
not execute in a standalone python interpreter.

It also assumes the use of Aniseed as the rigging tool.
"""
import os
import asset_composition


def run():

    # -- Start by creating a configuration which is pointing to our
    # -- maya traits and plugins
    configuration = asset_composition.Configuration()
    configuration.traits.add_path(
        os.path.join(
            os.path.dirname(__file__),
            "traits",
        ),
    )
    configuration.discovery.add_path(
        os.path.join(
            os.path.dirname(__file__),
            "discovery",
        ),
    )

    # -- Instance the compositor. This is what we will use
    # -- to get asset objects and run searched
    compositor = asset_composition.Compositor(configuration=configuration)

    # -- Find all the assets in the scene
    assets = compositor.search(query="*")

    # -- Cycle the assets and print the children
    for asset in assets:
        print("Found Asset : %s" % asset.label())

        for child in asset.children():

            child_asset = compositor.get(child)
            print(f"    Child : {child_asset.label()}")

        # -- Select the exportable parts of this rig
        if asset.has_action("Select Exportables"):
            asset.action("Select Exportables").call()
