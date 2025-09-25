#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : base.py
@Author : yell
@Desc : iEDA base framework
"""
import os

if os.environ.get("iEDA") == "ON":
    from ...third_party.iEDA.bin import ieda_py as ieda
else:
    ieda = None

from ...workspace import Workspace
from ...flows import DbFlow


class IEDABase:
    """Manage flow"""

    def __init__(self, workspace: Workspace, flow: DbFlow):
        if ieda == None:
            workspace.logger.error("Error, iEDA library is not load.")
            exit(0)
        self.ieda = ieda
        self.workspace = workspace
        self.flow = flow
        self._configs()

    def _configs(self):
        if self.flow.output_def is None:
            self.flow.output_def = self.workspace.configs.get_output_def(self.flow)

        if self.flow.output_verilog is None:
            self.flow.output_verilog = self.workspace.configs.get_output_verilog(
                self.flow
            )

    def get_ieda(self):
        return self.ieda

    ######################################################################
    # data operation
    ######################################################################
    def set_net(self, net_name: str, net_type: str):
        return self.ieda.set_net(net_name=net_name, net_type=net_type)
