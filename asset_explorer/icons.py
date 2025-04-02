# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> icons.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
Icons are an integral part of the asset explorer but they are computationally
expensive to constantly resolve or convert to pixmaps. Therefore this module
attempts to make that both easy and quick - by resolving paths but caching the
results for future use.
"""
import functools
import os
from typing import AnyStr

import Qt

# -- This is the location we look at for icons that are ask for which do
# -- not use absolute paths
_ICON_DIR: str = os.path.join(
    os.path.dirname(__file__),
    "icons",
)


@functools.cache
def path(icon_name: AnyStr) -> AnyStr:
    """
    This will return the absolute path of the icon. If an absolute path is given
    then it will be returned otherwise it will be searched for within the icons folder

    Args:
        icon_name (AnyStr): icon name to attempt to resolve a path from

    Returns:
        Absolute path of the icon
    """
    if not icon_name:
        return ""

    if os.path.exists(icon_name):
        return icon_name

    return os.path.join(
        _ICON_DIR,
        icon_name + ".png",
    )


# noinspection PyUnresolvedReferences
@functools.cache
def build_icon(icon_path: AnyStr) -> Qt.QtGui.QIcon:
    """
    This will create a QIcon from the icon path. This will cache the result, meaning
    that if you request the same icon multiple times it will only do the QIcon
    instancing once.
    """
    if not icon_path:
        return

    if ":" not in icon_path:
        icon_path = path(icon_path)

    return Qt.QtGui.QIcon(icon_path)


# noinspection PyUnresolvedReferences
@functools.cache
def as_pixmap(icon_path: AnyStr, size) -> Qt.QtGui.QPixmap:
    """
    This will generate a pixmap from the icon path with a specified size. This
    function is cached.
    """
    # -- If we're not given an icon we cannot do anything
    if not icon_path:
        return None

    # -- If this is not an absolute path to an icon then we look for
    # --  it within the icons folder directly
    if not ":" in icon_path:
        icon_path = path(icon_path)

    # -- Load the icon as a scaled pixmap to the size requested
    return Qt.QtGui.QPixmap(icon_path).scaled(
        Qt.QtCore.QSize(size, size),
        mode=Qt.QtCore.Qt.SmoothTransformation,
    )
