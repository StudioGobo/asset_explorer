# ----------------------------------------------------------------------------
# Copyright (c) Studio Gobo Ltd 2025
# Licensed under the MIT license.  
# See LICENSE.TXT in the project root for license information.
# ----------------------------------------------------------------------------
# File			-> maya_asset_explorer_example.py
# Created		-> March 2025
# Author		-> Michael Malinowski (Studio Gobo)
# ----------------------------------------------------------------------------
import os
import qtility
import asset_explorer

import maya.cmds as mc
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from Qt import QtWidgets


# --------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class MayaExplorerWidget(QtWidgets.QWidget):
    """
    This widget will monitor for show and hide events as well
    as script jobs which bind into the maya event manager
    """

    def __init__(self, configuration, *args, **kwargs):
        super(MayaExplorerWidget, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.explorer = asset_explorer.Explorer(configuration)
        self.layout().addWidget(self.explorer)

        # -- We update the ui based on various maya events. So we can correctly
        # -- unregister these, we store the event id's
        self.script_job_ids = list()

        # -- Register into the maya events system
        self._register_script_jobs()

    # --------------------------------------------------------------------------
    def _register_script_jobs(self):
        """
        Registers script jobs for maya events. If the events have already
        been registered they will not be re-registered.
        """
        # -- Only register if they are not already registered
        if self.script_job_ids:
            return

        # -- Define the list of events we will register a refresh
        # -- with
        events = [
            "SceneOpened",
            "NewSceneOpened",
        ]

        for event in events:
            self.script_job_ids.append(
                mc.scriptJob(
                    event=[
                        event,
                        self.update_explorer,
                    ]
                )
            )

    # ----------------------------------------------------------------------------------
    def _unregister_script_jobs(self):
        """
        This will unregster all the events tied with this UI. It will
        then clear any registered ID's stored within the class.
        """
        for job_id in self.script_job_ids:
            mc.scriptJob(
                kill=job_id,
                force=True,
            )

        # -- Clear all our job ids
        self.script_job_ids = list()

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def showEvent(self, event):
        """
        Maya re-uses UI's, so we regsiter our events whenever the ui
        is shown
        """
        self._register_script_jobs()
        self.update_explorer()

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def hideEvent(self, event):
        """
        Maya re-uses UI's, so we unregister the script job events whenever
        the ui is not visible.
        """
        self._unregister_script_jobs()

    def update_explorer(self):
        self.explorer.view_panel.force_refresh()


# --------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class DockableExplorer(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    """
    This is the dockable window wrapper which defines the window and allows
    it to dock in maya
    """

    OBJECT_NAME = "DockableAssetExplorerWindow"

    def __init__(self, configuration, *args, **kwargs):
        super(DockableExplorer, self).__init__(*args, **kwargs)

        # -- Set the window properties
        self.setObjectName(DockableExplorer.OBJECT_NAME)
        self.setWindowTitle('Asset Explorer')

        self.app = MayaExplorerWidget(
            configuration=configuration,
            parent=self,
        )
        self.setCentralWidget(
            self.app,
        )

    # ----------------------------------------------------------------------------------
    @classmethod
    def instance(cls):
        import gc
        for obj in gc.get_objects():
            if isinstance(obj, DockableExplorer):
                return obj


# --------------------------------------------------------------------------------------
def remove_workspace_control(control):
    if mc.workspaceControl(control, q=True, exists=True):

        try:
            mc.workspaceControl(control,e=True, close=True)
        except: pass

        try:
            mc.deleteUI(control,control=True)
        except: pass

        return


# --------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyUnusedLocal
def launch(*args, **kwargs):
    """
    This function should be called to invoke the app ui in maya
    """

    if DockableExplorer.instance():
        DockableExplorer.instance().show()
        return

    remove_workspace_control(
        DockableExplorer.OBJECT_NAME + "WorkspaceControl"
    )

    # -- Create a configuration which is pointing to all the
    # -- plugin paths we want to utilise
    configuration = asset_explorer.Configuration()
    configuration.traits.add_path(
        os.path.join(
            os.path.dirname(__file__),
            "traits",
        ),
    )
    configuration.discovery.add_path(
        os.path.join(
            os.path.dirname(__file__),
            "discovery",
        ),
    )
    configuration.views.add_path(
        os.path.join(
            os.path.dirname(__file__),
            "views",
        ),
    )
    # -- Apply the config options
    configuration.set_setting("active_view", "Scene View")
    configuration.set_setting("auto_sort", True)
    configuration.serialise(filepath=r"D:\foobar.json")
    # -- Instance the tool
    window = DockableExplorer(
        configuration=configuration,
        parent=qtility.windows.application(),
    )

    # -- Ensure its correctly docked in the ui
    window.show(
        dockable=True,
        area='right',
        floating=False,
        # retain=False,
    )

    mc.workspaceControl(
        f'{window.objectName()}WorkspaceControl',
        e=True,
        ttc=["AttributeEditor", -1],
        wp="preferred",
        mw=150,
    )


def run():
    launch()
