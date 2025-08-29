#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : patterns.py
@Author : yell
@Desc : data patterns api
"""
import os
import tqdm

from typing import List

from ..workspace.workspace import Workspace
from .database.vectors import VectorNet, VectorWire
from .vectors import DataVectors


class DataPatterns(DataVectors):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def generate_wire_patterns(
        self,
        vector_nets: List[VectorNet] = [],
        epsilon: int = 1,
        patterns_csv: str = None,
    ):
        if len(vector_nets) == 0:
            # load data from output/vectors/nets in workspace
            vector_nets = self.load_nets()

        if patterns_csv is None:
            patterns_csv = self.workspace.paths_table.ieda_vectors["wire_patterns"]

        from .io import VectorWirePatterns

        wire_patterns = VectorWirePatterns(
            patterns_csv=patterns_csv, logger=self.workspace.logger, epsilon=epsilon
        )

        wire_patterns.generate(vector_nets)

    def load_wire_patterns(self, patterns_csv: str = None):
        if patterns_csv is None:
            # load data from workspace
            patterns_csv = self.workspace.paths_table.ieda_vectors["wire_patterns"]

    def generate_wire_sequences(
        self,
        vector_nets: List[VectorNet] = [],
        epsilon: int = 1,
        sequences_json: str = None,
    ):
        if len(vector_nets) == 0:
            # load data from output/vectors/nets in workspace
            vector_nets = self.load_nets()

        if sequences_json is None:
            # save data to workspace
            sequences_json = self.workspace.paths_table.ieda_vectors["wire_sequences"]

        import networkx as nx
        from .io import VectorWireSequences

        wire_sequences = VectorWireSequences(
            json_path=sequences_json, logger=self.workspace.logger, epsilon=epsilon
        )
        wire_sequences.generate(vector_nets)

    def load_wire_sequences(self, sequences_json: str = None):
        data = []

        if sequences_json is None:
            # load data from workspace
            sequences_json = self.workspace.paths_table.ieda_vectors["wire_sequences"]

        from .io import VectorWireSequences

        wire_sequences = VectorWireSequences(
            json_path=sequences_json, logger=self.workspace.logger
        )
        return wire_sequences.load_sequences()
