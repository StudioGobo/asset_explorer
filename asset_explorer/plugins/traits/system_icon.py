# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> system_icon.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import asset_composition
from Qt import QtCore, QtWidgets


class SystemIconTrait(asset_composition.Trait):

    importance = 0

    @classmethod
    def can_bind(cls, identifier: str) -> bool:
        return True

    def icon(self) -> str:
        file_info = QtCore.QFileInfo(self.asset().identifier())
        provider = QtWidgets.QFileIconProvider()
        icon = provider.icon(file_info)
        return icon
