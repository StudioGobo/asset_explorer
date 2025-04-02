# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> config.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
"""
This module contains the storage and retrieval functions for all
the user editable settings.
"""
import json
import os
from typing import Any

import asset_composition

from . import view


class Configuration(asset_composition.Configuration):
    """
    This configuration extends the general asset composition
    configuration and adds in data specific to the asset explorer.
    """

    def __init__(self, *args, **kwargs) -> None:
        # -- Factory storage
        self._view_factory: view.ViewFactory = view.ViewFactory()

        # -- Parameter storage
        self._settings = dict(
            active_view="",
            item_size=32,
            filtered_labels=[],
            search_roots=[],
            favourites=[],
            auto_sort=False,
        )

        # -- Now that we have defined our factory and data, call the super
        super(Configuration, self).__init__(*args, **kwargs)

        # -- Include the built-in paths
        self._include_builtins()

    @property
    def views(self) -> view.ViewFactory:
        """
        Expose a read accessor to the view factory
        :return:
        """
        return self._view_factory

    def get_setting(self, setting_name: str) -> Any:
        """
        Method for returning a setting of a given name

        Args:
            setting_name (str): The name of the setting to retrieved

        :return:
        """
        return self._settings[setting_name]

    def set_setting(self, setting_name: str, value: Any) -> None:
        """
        This will apply the given setting

        Args:
            setting_name (str): The name of the setting to set
            value (Any): The value to set
        """
        self._settings[setting_name] = value

    def add_to(self, setting_name: str, value: Any) -> None:
        """
        This will add the given value to the setting - with the assumption
        that the setting is a list

        Args:
            setting_name (str): The name of the setting to add
            value (Any): The value to add
        """
        self._settings[setting_name].append(value)

    def remove_from(self, setting_name: str, value: Any) -> None:
        """
        This will remove the given value from the setting - with the assumption

        Args:
            setting_name (str): The name of the setting to remove
            value (Any): The value to remove
        """
        if value in self._settings[setting_name]:
            self._settings[setting_name].remove(value)

    @property
    def settings(self) -> dict:
        """
        This gives access to the settings data
        """
        return self._settings

    def _include_builtins(self) -> None:
        """
        Private function which auto-populates the factories with the traits
        and plugins specific to the explorer
        :return:
        """
        self.traits.add_path(
            os.path.join(
                os.path.dirname(__file__),
                "plugins",
                "traits",
            ),
        )
        self.views.add_path(
            os.path.join(
                os.path.dirname(__file__),
                "plugins",
                "views",
            ),
        )

    def serialise(self, filepath: str = None) -> dict:
        """
        This will serialise (write) all the data from the configuration
        to a dictionary and optionally write it to a file.

        Args:
            filepath (str): The filepath to write the data to
        """
        data: dict = super(Configuration, self).serialise(filepath)

        ui_data = dict(
            view_paths=self.views.paths(),
            disabled_views=[
                view_name
                for view_name in self.views.identifiers(include_disabled=True)
                if self.views.is_disabled(view_name)
            ],
            explorer=self.settings,
        )
        data.update(ui_data)

        if self._filepath:
            with open(self._filepath, "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)

        return data

    # noinspection SpellCheckingInspection
    def _deserialise(self, filepath: str) -> None:
        """
        This will populate the configuration based on the file
        given

        Args:
            filepath: The absolute path to the configuration file
        """
        super(Configuration, self)._deserialise(filepath)

        # -- Read the data file
        with open(filepath, "r") as f:
            data: dict = json.load(f)

        if data.get("explorer"):
            self._settings.update(data["explorer"])

        # -- Disable any
        for path in data["view_paths"]:
            self._view_factory.add_path(path)

        # -- Add the disabled traits
        for disabled_view in data["disabled_views"]:
            self._view_factory.set_disabled(disabled_view, True)
