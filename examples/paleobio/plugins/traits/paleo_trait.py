# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> paleo_trait.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import functools
import json
import os
import shutil
import urllib.request
import weakref
from typing import Self

import asset_composition
import Qt
from asset_composition._trait import _TraitAction


class PaleoBioRestApiResourceTrait(asset_composition.Trait):

    importance = 100
    CACHE_DIR: str = os.path.join(
        os.environ["APPDATA"],
        "PALEO_RESOURCES",
    )

    def __init__(self, *args, **kwargs):
        super(PaleoBioRestApiResourceTrait, self).__init__(*args, **kwargs)
        DB.cache.get_data(self)

    @classmethod
    def can_bind(cls, identifier: str) -> bool:
        return True

    # TODO: Add typing
    def label(self):
        return self.asset().identifier()

    def children(self) -> list:
        return sorted(list(set(DB.cache.get_children(self))))

    def actions(self) -> list[_TraitAction]:
        return [
            self.create_action(
                name="Taxonomy Data",
                function=functools.partial(
                    DB.cache.get_data,
                    self,
                ),
                category="",
                hidden=True,
            )
        ]

    def icon(self):
        return DB.cache.get_icon(self)


class DataCache(Qt.QtCore.QThread):

    INSTANCE = None

    def __init__(self, *args, **kwargs):
        super(DataCache, self).__init__(*args, **kwargs)

        self._cache = dict(
            icons=dict(),
            data=dict(),
            children=dict(),
        )

        self._queue: list = []

    @classmethod
    def as_singleton(cls) -> Self:
        if cls.INSTANCE is None:
            cls.INSTANCE: Self = cls()
            cls.INSTANCE.start()
        return cls.INSTANCE

    @functools.lru_cache(maxsize=None)
    def get_cache_path(self) -> str:
        CACHE_DIR: str = os.path.join(
            os.environ["APPDATA"],
            "PALEO_RESOURCES",
        )
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        return CACHE_DIR

    # TODO: Add typing
    @functools.lru_cache(maxsize=None)
    def data_filepath(self, name) -> str:
        return os.path.join(
            self.get_cache_path(),
            name + "_data.json",
        )

    # TODO: Add typing
    @functools.lru_cache(maxsize=None)
    def child_filepath(self, name) -> str:
        return os.path.join(
            self.get_cache_path(),
            name + "_children.json",
        )

    # TODO: Add typing
    @functools.lru_cache(maxsize=None)
    def icon_filepath(self, name) -> str:
        return os.path.join(
            self.get_cache_path(),
            name + ".png",
        )

    # TODO: Add typing
    @functools.lru_cache(maxsize=None)
    def base_icon_filepath(self, icon_id) -> str:
        return os.path.join(
            self.get_cache_path(),
            str(icon_id) + "_base_icon.png",
        )

    # TODO: Add typing
    def get_data(self, trait):
        name = trait.asset().identifier()

        # -- If its primed and cached, return it
        if name in self._cache["data"]:
            return self._cache["data"][name]

        # -- Check if the cache file is ready
        if os.path.exists(self.data_filepath(name)):
            with open(self.data_filepath(name), "r") as f:
                self._cache["data"][name] = json.load(f)
                return self._cache["data"][name]

        # -- To reach here means we need to queue it
        self.queue_data_request(weakref.ref(trait), "data")
        return dict(nam=name)

    # TODO: Add typing
    def get_children(self, trait):
        name = trait.asset().identifier()
        if name in self._cache["children"]:
            return self._cache["children"][name]

        # -- Check if a cached file already exists
        if os.path.exists(self.child_filepath(name)):
            with open(self.child_filepath(name), "r") as f:
                self._cache["children"][name] = json.load(f)
                return self._cache["children"][name]

        # -- We need to queue a request for the data
        self.queue_data_request(weakref.ref(trait), "children")
        return []

    # TODO: Add typing
    def get_icon(self, trait):
        name = trait.asset().identifier()
        if name in self._cache["icons"]:
            return self._cache["icons"][name]

        # -- Check if the file already exists
        if os.path.exists(self.icon_filepath(name)):
            self._cache["icons"][name] = self.icon_filepath(name)
            return self._cache["icons"][name]

        # -- To reach here means we need to queue it
        self.queue_data_request(weakref.ref(trait), "icon")
        return

    # TODO: Add typing
    def queue_data_request(self, trait_ref, access_type) -> None:
        self._queue.append((trait_ref, access_type))

    def run(self):
        while True:

            # -- If there is nothing queued, then do nothing
            if not self._queue:
                import time

                time.sleep(1)
                continue

            # -- Take the first item in the queue to operate on
            trait_ref, access_type = self._queue.pop(0)

            # -- If the trait is no longer with us, skip it!
            if not trait_ref():
                continue

            # -- Get the name of the asset
            name = trait_ref().asset().identifier()

            # -- Determine what type of operation we need to do
            if access_type == "data":

                # -- Resolve the rest api url
                url_name = name.replace(" ", "+")
                url = (
                    r"https://paleobiodb.org/data1.2/taxa/list.json?rowcount&show=class&show=img&show=full&name="
                    + url_name
                )

                with urllib.request.urlopen(url) as response:
                    data = json.load(response)["records"][0]

                    # -- Write the data to a persistent cache
                    cache_file = self.data_filepath(name)
                    with open(cache_file, "w") as f:
                        json.dump(data, f)

                    # -- Store the data in our own cache
                    self._cache["data"][name] = data

                # -- Emit the fact that this has been done
                if trait_ref():
                    trait = trait_ref().asset().status_changed.emit()

            elif access_type == "children":

                url_name = name.replace(" ", "+")
                url = (
                    r"https://paleobiodb.org/data1.2/taxa/list.json?rowcount&show=class&rel=children&name="
                    + url_name
                )

                with urllib.request.urlopen(url) as response:
                    data = json.load(response)["records"]

                    children = [
                        item["nam"]
                        for item in data
                        if "oid" in item and item["nam"] != name
                    ]

                    cache_file = self.child_filepath(name)
                    with open(cache_file, "w") as f:
                        json.dump(children, f)

                    self._cache["children"][name] = children

                if trait_ref():
                    trait = trait_ref().asset().changed.emit()

            elif access_type == "icon":
                url_name = name.replace(" ", "+")
                url = (
                    r"https://paleobiodb.org/data1.2/taxa/list.json?rowcount&show=class&show=img&show=full&name="
                    + url_name
                )

                with urllib.request.urlopen(url) as response:
                    data = json.load(response)["records"][0]

                if "img" not in data:
                    continue

                # -- Many assets share the same icons, so look for the base
                # -- icon first, as we wont have to download it again if it
                # -- already has been downloaded
                base_icon_path = os.path.join(
                    self.get_cache_path(),
                    data["img"] + "_base_icon.png",
                )

                if not os.path.exists(base_icon_path):
                    url = (
                        r"https://paleobiodb.org/data1.2/taxa/thumb.png?id="
                        + data["img"]
                    )
                    response = urllib.request.urlopen(url)
                    image = response.read()

                    with open(base_icon_path, "wb") as file:
                        file.write(image)

                shutil.copy(
                    str(base_icon_path),
                    str(self.icon_filepath(name)),
                )

                # -- Store the path in the cache
                self._cache["icons"][name] = self.icon_filepath(name)

                if trait_ref():
                    trait_ref().asset().status_changed.emit()


class DB:
    cache: DataCache = DataCache().as_singleton()
