# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> delegate.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import functools
import typing
from typing import Any, AnyStr

from Qt import QtCore, QtGui, QtWidgets

from . import constants, icons


# noinspection PyUnresolvedReferences
class AssetDelegate(QtWidgets.QAbstractItemDelegate):
    """
    The Delegate defines how we paint an item in the tree view.
    """

    def __init__(self, size: int, parent: QtWidgets.QWidget = None) -> None:
        super(AssetDelegate, self).__init__(parent=parent)
        self._size: int = size

    def sizeHint(self, *args, **kwargs) -> QtCore.QSize:
        """
        Override for returning the size of the draw area
        """
        return QtCore.QSize(
            self._size,
            self._size,
        )

    # noinspection PyUnusedLocal
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """
        This is responsible for painting the delegate. We use a delegate to
        allow us to do color/grayscale switching etc.
        """

        # -- Get the asset path from the index data
        label: AnyStr = index.data(QtCore.Qt.DisplayRole)
        icon: AnyStr | QtGui.QPixmap = index.data(QtCore.Qt.DecorationRole)

        if isinstance(icon, str):
            # -- Ask for our main icon
            pixmap = icons.as_pixmap(
                index.data(QtCore.Qt.DecorationRole),
                self._size,
            )

        elif isinstance(icon, QtGui.QPixmap):
            pixmap = icon.pixmap(self._size)

        elif isinstance(icon, QtGui.QIcon):
            pixmap = icon.pixmap(self._size)

        else:
            pixmap = None

        # -- Retrieve any custom data
        custom_data: dict[str, Any] = index.data(
            constants.DATA_ROLE,
        )

        # -- Get a list of overlaying icons. Any trait can return overlaying
        # -- icons to better represent its state
        overlay_icons: list[QtGui.QPixmap] = [
            icons.as_pixmap(icon, self._size)
            for icon in index.data(constants.STATUS_ICONS_ROLE)
        ]

        # -- We'll use these values a lot, so call the functions
        # -- only once
        width: int = self._size
        height: int = self._size
        icon_opacity: float = 0.85

        # -- If we have a pixmap we draw the icon
        if pixmap:
            painter.setOpacity(icon_opacity)
            painter.drawPixmap(
                option.rect.x(),
                option.rect.y(),
                height,
                width,
                pixmap,
            )

        # -- Paint the overlays
        for overlay_icon in overlay_icons:
            painter.setOpacity(icon_opacity)
            painter.drawPixmap(
                option.rect.x(),
                option.rect.y(),
                height,
                width,
                overlay_icon,
            )

        # -- Now we restore the opacity back to full before starting
        # -- to draw the text
        painter.setOpacity(1)
        font_size: int = max(8, (int(height * 0.15)))
        painter.setFont(self.font(font_size))

        # -- Define the text area
        text_rect: QtCore.QRect = QtCore.QRect(
            option.rect.x() + width + (width * 0.2),
            option.rect.y() + (height * 0.1),
            option.rect.width(),
            option.rect.height() * 0.5,
        )

        pen_color = option.palette.color(QtGui.QPalette.Text)
        painter.setPen(pen_color)

        painter.drawText(
            text_rect,
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
            label,
        )

    # ----------------------------------------------------------------------------------
    @functools.cache
    def font(self, font_size: int) -> QtGui.QFont:
        """
        Returns the QFont for the given size

        Args:
            font_size: The size of the font to be instanced

        Returns:
            QtGui.QFont
        """
        return QtGui.QFont("ariel", font_size)
