#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : net_opt.py
@Author : yell
@Desc : net opt api
"""
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow


class IEDANetOpt(IEDAIO):
    """net opt api"""

    def __init__(self, workspace: Workspace, flow: DbFlow):
        super().__init__(workspace=workspace, flow=flow)

    def _configs(self):
        super()._configs()

        self.ieda_config = self.workspace.paths_table.ieda_config["fixFanout"]

    def _run_flow(self):
        self.read_def()

        self.ieda.run_no_fixfanout(self.ieda_config)

        self.def_save()
        self.verilog_save(self.cell_names)

        self._generate_feature_summary()
        self._generate_feature_tool()

    def _generate_feature_summary(self, json_path: str = None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json[
                "fixFanout_summary"
            ]

        self.read_output_def()

        # generate feature summary data
        self.ieda.feature_summary(json_path)

    def _generate_feature_tool(self):
        self.read_output_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json

        # generate feature tool data
        self.ieda.feature_tool(
            ieda_feature_json["fixFanout_tool"], DbFlow.FlowStep.fixFanout.value
        )
