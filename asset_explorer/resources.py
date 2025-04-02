# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> resources.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
As many of the modules and widgets dynamically retrieve resources (images, ui files
etc), this module contains convenience functionality to access them.
"""
import os

# -- Cache this variable so we don't reconstruct the
# -- path every time a resource is requested
_RES_FOLDER: str = os.path.join(
    os.path.dirname(__file__),
    "_res",
)


# --------------------------------------------------------------------------------------
def get(name: str) -> str:
    """
    Returns the absolute path to the resource with the given
    resource name

    Args:
        name (str): The filename to get from the res folder

    Returns:
        str: The absolute path of the resource
    """
    return os.path.join(
        _RES_FOLDER,
        name,
    )
