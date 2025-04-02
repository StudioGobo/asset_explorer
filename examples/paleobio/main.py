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
This example demonstrates multiple aspects of asset composition and the
asset explorer. Specifically:

    * Embedding the Explorer widget in a higher level tool
    * Demonstrating non-file related assets (REST API)
    * Demonstrating a basic way of implementing threading within the Explorer

Please check the requirements.txt of the asset_explorer and ensure all
requirements are met before running this module.
"""
import os

import asset_composition
from Qt import QtCore, QtGui, QtWidgets

import asset_explorer


# noinspection PyUnresolvedReferences
class PaleoTool(QtWidgets.QWidget):
    """
    This is a wrapping tool which we will embed the Explorer widget with
    and then extend with additional functionality.
    """

    def __init__(self, parent=None, *args, **kwargs):
        super(PaleoTool, self).__init__(parent=parent)

        # -- Build our base layout
        self.setLayout(QtWidgets.QHBoxLayout())

        # -- Instance the explorer widget and add it to the layout
        self.explorer = asset_explorer.Explorer(*args, **kwargs)
        self.layout().addWidget(self.explorer)

        # -- Add a custom made info widget and add that to the layout too
        self.info_panel = InfoWidget(parent=self)
        self.layout().addWidget(self.info_panel)

        # -- Hook up the signals to ensure our info panel updates
        # -- as a user interacts with the explorer widget
        self.explorer.itemSelected.connect(self.info_panel.populate_data)

        self.setWindowTitle("Paleobio Explorer")


# noinspection PyUnresolvedReferences
class InfoWidget(QtWidgets.QWidget):
    """
    This widget is a bespoke widget to show specific details about
    different dinosaurs.
    """

    def __init__(self, parent=None):
        super(InfoWidget, self).__init__(parent=parent)

        # -- Create our basic layout
        self.setLayout(QtWidgets.QVBoxLayout())

        # -- Add our image label
        self.image = QtWidgets.QLabel()
        self.layout().addWidget(self.image)

        # -- Now we can start adding our fields - these are fields of
        # -- information we will want to present to the user
        self.label = self.add_labeled_entry("Name", self.layout())
        self.classification = self.add_labeled_entry("Class", self.layout())
        self.era = self.add_labeled_entry("Era", self.layout())
        self.environment = self.add_labeled_entry("Environment", self.layout())
        self.descendents = self.add_labeled_entry("Known Descendents", self.layout())

        # -- Finally add a spacer item so all the fields are pushed to the top
        # -- of the layout
        self.layout().addSpacerItem(
            QtWidgets.QSpacerItem(
                10,
                0,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding,
            ),
        )

    # TODO: Add typing
    def add_labeled_entry(self, name, parent_layout):
        """
        This is a convenience function for creating an entry for a displaying
        information along with a label
        """
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(name)
        label.setMinimumWidth(125)
        result = QtWidgets.QLabel()

        layout.addWidget(label)
        layout.addWidget(result)

        parent_layout.addLayout(layout)
        return result

    def reset_data(self) -> None:
        """
        This will clear the current contents of the labels
        """
        self.era.setText("")
        self.label.setText("")
        self.descendents.setText("")
        self.classification.setText("")

    # TODO: Add typing
    def populate_data(self, item) -> None:
        """
        This will reset the contents of the panel and re-populate them
        with the details of the given item
        :param item:
        :return:
        """
        # -- Set the main label
        self.label.setText(item.asset().label())

        # -- Read the icon and the data from the asset. Note that
        # -- we're calling a bespoke action from our paleo trait
        icon = item.asset().icon()
        data = item.asset().action("Taxonomy Data").call()

        # -- Start setting the specific data
        if "tei" in data:
            if "tli" in data:
                self.era.setText("%s to %s" % (data["tei"], data["tli"]))
            else:
                self.era.setText(data["tei"])

        if "siz" in data:
            self.descendents.setText(str(max(0, data["siz"] - 1)))

        if "cll" in data:
            self.classification.setText(data["cll"])

        if "jev" in data:
            self.environment.setText(data["jev"])

        if icon and isinstance(icon, str):
            self.image.setPixmap(QtGui.QPixmap(icon))
            return

        if icon and isinstance(icon, QtGui.QIcon):
            self.image.setPixmap(icon.pixmap(QtCore.QSize(200, 200)))
            print("setting image")
            return


if __name__ == "__main__":

    # noinspection PyUnresolvedReferences
    q_app: QtWidgets.QApplication = QtWidgets.QApplication()

    config_path: str = os.path.join(
        os.environ["APPDATA"],
        "PALEOBIO",
        "configuration.json",
    )

    # -- If the config already exists, re-use it. That way the user
    # -- will have a consistent experience across sessions. If the
    # -- config does not exist, then we define a new one
    if os.path.exists(config_path):
        configuration = asset_explorer.Configuration(filepath=config_path)

    else:
        # -- Create a new configuration
        configuration = asset_explorer.Configuration()

        configuration.traits.add_path(
            os.path.join(
                os.path.dirname(__file__),
                "plugins",
                "traits",
            )
        )
        configuration.discovery.add_path(
            os.path.join(
                os.path.dirname(__file__),
                "plugins",
                "discovery",
            )
        )

        # -- Define a project key. The project key defines the projects
        # -- settings/configuration
        configuration.set_setting(
            "search_roots",
            [
                "Megalosauridae",
            ],
        )
        configuration.set_setting("active_view", "Folder View")
        configuration.set_setting("auto_sort", True)

        # -- Save the config so that any changes the user makes
        # -- will be persistent
        configuration.serialise(filepath=config_path)

    # -- Rather than just show the asset explorer, this will launch an actual
    # -- wrapping tool which embeds the explorer but extends it with additional
    # -- functionality.
    w = PaleoTool(configuration=configuration)
    w.show()

    # -- Block the thread
    q_app.exec()
