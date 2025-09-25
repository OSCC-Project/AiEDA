#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : sta.py
@Author : yell
@Desc : sta api
"""
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow


class IEDASta(IEDAIO):
    """sta api"""

    def __init__(self, workspace: Workspace, flow: DbFlow, output_dir: str = None):
        self.output_dir = output_dir
        super().__init__(workspace=workspace, flow=flow)

    def _configs(self):
        super()._configs()

        if self.output_dir == None:
            self.output_dir = self.workspace.paths_table.ieda_output["sta"]
        self.rpt_dir = self.workspace.paths_table.ieda_output["rpt"]

    def _run_flow(self):
        self.read_def()

        self.ieda.run_sta(self.output_dir)
        # self.ieda.report_timing()

    def init_sta(self):
        self.ieda.set_design_workspace(self.output_dir)
        self.ieda.read_netlist(self.flow.input_verilog)
        self.ieda.read_liberty(self.workspace.configs.paths.lib_paths)
        self.ieda.link_design(self.workspace.design)
        self.ieda.read_sdc(self.workspace.configs.paths.sdc_path)
        # self.ieda.init_sta(output=self.output_dir)

    def create_data_flow(self):
        self.ieda.create_data_flow()

    def get_used_lib(self):
        self.ieda.set_design_workspace(self.output_dir)
        self.ieda.read_liberty(self.workspace.configs.paths.lib_paths)

        lef_paths = [
            self.workspace.configs.paths.tech_lef_path
        ] + self.workspace.configs.paths.lef_paths
        self.ieda.read_lef_def(lef_paths, self.flow.input_def)

        libs = self.ieda.get_used_libs()

        return libs
