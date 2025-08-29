#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : drc.py
@Author : yell
@Desc : DRC api
"""
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow


class IEDADrc(IEDAIO):
    """DRC api"""

    def __init__(self, workspace: Workspace, flow: DbFlow, output_path: str = None):
        self.feature_path = output_path
        super().__init__(workspace=workspace, flow=flow)

    def _configs(self):
        super()._configs()

        self.ieda_config = self.workspace.paths_table.ieda_config["drc"]
        self.report_path = self.workspace.paths_table.ieda_report["drc"]
        if self.feature_path is None:
            self.feature_path = self.workspace.paths_table.ieda_feature_json[
                "route_drc"
            ]

    def _run_flow(self):
        self.read_def()

        self.ieda.init_drc(
            temp_directory_path=self.workspace.paths_table.ieda_output["drc"],
            thread_number=128,
            golden_directory_path="",
        )

        self.ieda.run_drc(config=self.ieda_config, report=self.report_path)

        self.ieda.save_drc(path=self.feature_path)
