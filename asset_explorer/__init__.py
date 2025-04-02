# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> __init__.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
The Asset Explorer is a PySide based ui tool which exposes views
to interact with assets
"""
# -- Import our classes that plugin developers will want
# -- easy access to
from .view import View
from .view import ViewFactory
from .config import Configuration
from .widgets.app import Explorer
from .widgets.item import AssetItem

# -- Import our main launch function
from .entry import launch

__version__ = "1.1.4"
