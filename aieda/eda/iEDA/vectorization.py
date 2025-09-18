#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : vecorization.py
@Author : yell
@Desc : eda data vecorization api
"""
from multiprocessing import Process
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow
from ...data.database.enum import FeatureOption


class IEDAVectorization(IEDAIO):
    """eda data vecorization api"""

    def __init__(self, workspace: Workspace, flow: DbFlow, vectors_dir: str = None):
        self.vectors_dir = vectors_dir
        super().__init__(workspace=workspace, flow=flow)

    def _configs(self):
        super()._configs()

        if self.vectors_dir is None:
            self.vectors_dir = self.workspace.paths_table.ieda_output["vectors"]

    def generate_vectors(self, patch_row_step: int = 9, patch_col_step: int = 9, batch_mode: bool = True, is_placement_mode: bool = False):
        def _generate_vectors():
            self.read_def()

            self.ieda.generate_vectors(
                dir=self.vectors_dir,
                patch_row_step=patch_row_step,
                patch_col_step=patch_col_step,
                batch_mode=batch_mode,
                is_placement_mode=is_placement_mode,
            )

        if self.inited_flag:
            _generate_vectors()
        else:
            p = Process(target=_generate_vectors, args=())
            p.start()
            p.join()

    def vectors_nets_to_def(self):
        def _read_nets():
            self.read_def()
            self.ieda.read_vectors_nets(dir=self.vectors_dir)
            self.def_save()
            self.verilog_save(self.cell_names)

        if self.inited_flag:
            _read_nets()
        else:
            p = Process(target=_read_nets, args=())
            p.start()
            p.join()

    def vectors_nets_patterns_to_def(self, path):
        def _read_nets_patterns():
            self.read_def()
            self.ieda.read_vectors_nets_patterns(path=path)
            self.def_save()
            self.verilog_save(self.cell_names)

        if self.inited_flag:
            _read_nets_patterns()
        else:
            p = Process(target=_read_nets_patterns, args=())
            p.start()
            p.join()
