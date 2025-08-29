#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : gds.py
@Author : yell
@Desc : gds api
"""
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow


class IEDAGds(IEDAIO):
    """gds api"""

    def __init__(self, workspace: Workspace, flow: DbFlow, output_gds: str):
        self.output_gds = output_gds
        super().__init__(workspace=workspace, flow=flow)

    def _run_flow(self):
        self.read_def()
        self.run_def_to_gds(self.output_gds)
