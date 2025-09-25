#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : routing.py
@Author : yell
@Desc : routing api
"""
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow


class IEDARouting(IEDAIO):
    """routing api"""

    def __init__(self, workspace: Workspace, flow: DbFlow):
        super().__init__(workspace=workspace, flow=flow)

    def _configs(self):
        super()._configs()

        self.ieda_config = self.workspace.paths_table.ieda_config["route"]
        self.rt_sta_dir = self.workspace.paths_table.ieda_output["rt_sta"]

    def _run_flow(self):
        import os
        import json
        from .sta import IEDASta

        def is_timing_enable():
            if os.path.exists(self.ieda_config):
                with open(self.ieda_config, "r", encoding="utf-8") as f_reader:
                    json_data = json.load(f_reader)

                    # check if time enable
                    if json_data["RT"]["-enable_timing"] == "1":
                        return True

            return False

        self.read_def()

        if is_timing_enable():
            sta = IEDASta(
                workspace=self.workspace, flow=self.flow, output_dir=self.rt_sta_dir
            )
            sta.init_sta()

        self.ieda.init_rt(config=self.ieda_config)
        self.ieda.run_rt()
        self.close_routing()

        self.def_save()
        self.verilog_save(self.cell_names)

        self._generate_feature_summary()
        self._generate_feature_tool()

    def close_routing(self):
        self.ieda.destroy_rt()

    def _generate_feature_summary(self, json_path: str = None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json["route_summary"]

        self.read_output_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json

        # generate feature summary data
        self.ieda.feature_summary(json_path)

    def _generate_feature_tool(self):
        self.read_output_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json

        # generate feature route data
        self.ieda.feature_tool(
            ieda_feature_json["route_tool"], DbFlow.FlowStep.route.value
        )

    # read route json file to iEDA route data
    def feature_route_read(self, json_path: str):
        self.ieda.feature_route_read(path=json_path)

    # read route def and save route data to json
    def feature_route(self, json_path: str):
        self.ieda.feature_route(path=json_path)
