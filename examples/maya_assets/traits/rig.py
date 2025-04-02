# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> rig.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import os
import maya.cmds as mc
import asset_composition


class MayaNode(asset_composition.Trait):
    """
    General maya node trait. This allows for the node
    to be selected
    """

    importance = 2

    @classmethod
    def can_bind(cls, identifier: str) -> bool:
        if mc.objExists(identifier):
            return True
        return False

    def label(self):
        return self.asset().identifier()

    def _select(self):
        mc.select(
            self.label(),
        )

    def actions(self):
        return [
            self.create_action(
                name="Select",
                function=self._select,
                category="Interact",
            )
        ]


class AniseedRig(asset_composition.Trait):
    """
    This trait is specific to aniseed rigs:
    https://github.com/mikemalinowski/aniseed
        """
    importance = 3

    @classmethod
    def can_bind(cls, identifier: str) -> bool:
        if mc.objExists("%s.aniseed_rig" % identifier):
            return True
        return False

    def label(self):
        return self.asset().identifier()

    def icon(self):
        return os.path.join(
            os.path.dirname(__file__),
            "asset.png",
        )

    def children(self):
        """
        For an aniseed rig asset, our children are what we expect to
        export

        :return:
        """
        return self.get_exportables()

    def get_exportables(self):

        exportables = []

        # -- Get the children of the rig
        children = mc.listRelatives(
            self.asset().label(),
            children=True,
        )

        # -- If there are not children then there are no exportables
        if not children:
            return exportables

        # -- Cycle the children, scraping the particulars of an aniseed rig
        for child in children:
            if "skeleton" in child.lower():
                exportables.extend(
                    [
                        name
                        for name in mc.listRelatives(child, children=True)
                    ]
                )

            if "geometry" in child.lower():
                exportables.extend(
                    [
                        mc.listRelatives(name, parent=True)[0]
                        for name in (mc.listRelatives(child, children=True, type="mesh", ad=True) or [])
                    ]
                )

        return exportables

    def _select_exportables(self):
        mc.select(self.get_exportables())

    def actions(self):
        return [
            self.create_action(
                name="Select Exportables",
                function=self._select_exportables,
                category="Interact",
            )
        ]


class ExportGeometry(asset_composition.Trait):
    """
    This trait represents exportable geometry
    """
    importance = 3

    @classmethod
    def can_bind(cls, identifier: str) -> bool:

        if not mc.objExists(identifier):
            return False

        # -- Get the shapes and test for a mesh
        shapes = mc.listRelatives(
            identifier,
            children=True,
            type="mesh",
        )

        if shapes:
            return True

        return False

    def label(self):
        return self.asset().identifier()

    def icon(self):
        return os.path.join(
            os.path.dirname(__file__),
            "geometry.png",
        )

    def children(self):
        return []

    def parent(self):
        return mc.listRelatives(self.asset().label(), parent=True)


class ExportJoint(asset_composition.Trait):
    """
    This trait represents exportable joints
    """
    importance = 3

    @classmethod
    def can_bind(cls, identifier: str) -> bool:
        if not mc.objExists(identifier):
            return False

        if mc.nodeType(identifier) == "joint":
            return True

        return False

    def label(self):
        return self.asset().identifier()

    def icon(self):
        return os.path.join(
            os.path.dirname(__file__),
            "bone.png",
        )

    def children(self):
        return [
            name
            for name in mc.listRelatives(self.asset().label(), children=True, type="joint") or list()
        ]

    def parent(self):
        return mc.listRelatives(self.asset().label(), parent=True)[0]
