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
Note: This example is intended only to be run within Autodesk Maya and will
not execute in a standalone python interpreter.

It also assumes the use of Aniseed as the rigging tool.
"""
import maya_composition_example
import maya_asset_explorer_example

# -- Uncomment this if you want to test the headless asset composition example
maya_composition_example.run()

# -- Uncomment this if you want to test the ui tool
maya_asset_explorer_example.run()
