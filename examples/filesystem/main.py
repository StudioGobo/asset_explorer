# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> main.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
This example is a basic example which shows how the asset explorer
can be pointed to your local hard drive and be given different
locations to query.
"""
import os
import asset_explorer
import asset_composition

if __name__ == '__main__':

    # -- Create a new configuration
    configuration = asset_explorer.Configuration()

    # -- Add the built in traits
    configuration.traits.add_path(
        os.path.join(
            os.path.dirname(asset_composition.__file__),
            "plugins",
            "filesystem",
            "traits",
        ),
    )
    configuration.discovery.add_path(
        os.path.join(
            os.path.dirname(asset_composition.__file__),
            "plugins",
            "filesystem",
            "discovery",
        ),
    )

    configuration.add_to(
        "search_roots",
        os.path.dirname(
            asset_explorer.__file__,
        ),
    )
    configuration.set_setting("active_view", "Hierarchy View")

    asset_explorer.launch(
        configuration=configuration,
        blocking=True,
    )
