#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : vectors.py
@Author : yell
@Desc : data vectorization api
"""
import os
import tqdm

from typing import List

from ..workspace.workspace import Workspace
from ..flows import DbFlow
from .io import VectorsParserJson


class DataVectors:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def load_cells(self, cells_path: str = None):
        if cells_path is None:
            # read from workspace vectors/tech/cells.json
            cells_path = self.workspace.paths_table.ieda_vectors["cells"]

        parser = VectorsParserJson(json_path=cells_path, logger=self.workspace.logger)
        return parser.get_cells()

    def load_layers(self, tech_path: str = None):
        if tech_path is None:
            # read from workspace vectors/tech/tech.json
            tech_path = self.workspace.paths_table.ieda_vectors["tech"]

        parser = VectorsParserJson(json_path=tech_path, logger=self.workspace.logger)
        return parser.get_layers()

    def load_vias(self, tech_path: str = None):
        if tech_path is None:
            # read from workspace vectors/tech/tech.json
            tech_path = self.workspace.paths_table.ieda_vectors["tech"]

        parser = VectorsParserJson(json_path=tech_path, logger=self.workspace.logger)
        return parser.get_vias()

    def load_instances(self, instances_path: str = None):
        if instances_path is None:
            # read from workspace vectors/instances/instances.json
            instances_path = self.workspace.paths_table.ieda_vectors["instances"]

        parser = VectorsParserJson(
            json_path=instances_path, logger=self.workspace.logger
        )
        return parser.get_instances()

    def load_nets(self, nets_dir: str = None, net_path: str = None):
        nets = []

        def read_from_dir():
            # get data from nets directory
            for root, dirs, files in os.walk(nets_dir):
                for _, file in tqdm.tqdm(
                    enumerate(files), total=len(files), desc="vectors read nets"
                ):
                    if file.endswith(".json"):
                        filepath = os.path.join(root, file)

                        json_parser = VectorsParserJson(filepath)

                        nets.extend(json_parser.get_nets())

        if nets_dir is not None and os.path.isdir(nets_dir):
            self.workspace.logger.info("read nets from %s", nets_dir)
            # get data from nets directory
            read_from_dir()

        if net_path is not None and os.path.isfile(net_path):
            self.workspace.logger.info("read nets from %s", net_path)
            # get nets from nets josn file
            json_parser = VectorsParserJson(net_path)

            nets.extend(json_parser.get_nets())

        if nets_dir is None and net_path is None:
            # read nets from output/vectors/nets in workspace
            nets_dir = self.workspace.paths_table.ieda_vectors["nets"]

            self.workspace.logger.info("read nets from workspace %s", nets_dir)
            read_from_dir()

        return nets

    def load_patchs(self, patchs_dir: str = None, patch_path: str = None):
        patchs = []

        def read_from_dir():
            # get data from nets directory
            for root, dirs, files in os.walk(patchs_dir):
                for file in files:
                    if file.endswith(".json"):
                        filepath = os.path.join(root, file)
                        self.workspace.logger.info("read patchs from %s", filepath)
                        json_parser = VectorsParserJson(filepath)

                        patchs.extend(json_parser.get_patchs())

        if patchs_dir is not None and os.path.isdir(patchs_dir):
            self.workspace.logger.info("read patchs from %s", patchs_dir)
            # get data from patchs directory
            read_from_dir()

        if patch_path is not None and os.path.isfile(patch_path):
            self.workspace.logger.info("read patchs from %s", patch_path)
            # get nets from nets josn file
            json_parser = VectorsParserJson(patch_path)

            patchs.extend(json_parser.get_patchs())

        if patchs_dir is None and patch_path is None:
            # read patchs from output/vectors/patchs in workspace
            patchs_dir = self.workspace.paths_table.ieda_vectors["patchs"]

            self.workspace.logger.info("read patchs from workspace %s", patchs_dir)
            read_from_dir()

        return patchs

    def load_timing_graph(self, graph_path: str = None):
        if graph_path is None:
            graph_path = self.workspace.paths_table.ieda_vectors["timing_wire_graph"]
        parser = VectorsParserJson(json_path=graph_path, logger=self.workspace.logger)
        return parser.get_wire_graph()

    def load_timing_wire_paths(
        self, timing_paths_dir: str = None, file_path: str = None
    ):
        wire_paths = []

        def read_from_dir():
            # get data from directory
            for root, dirs, files in os.walk(timing_paths_dir):
                for _, file in tqdm.tqdm(
                    enumerate(files), total=len(files), desc="timing wire paths"
                ):
                    if file.endswith(".json"):
                        filepath = os.path.join(root, file)

                        parser = VectorsParserJson(
                            json_path=filepath, logger=self.workspace.logger
                        )
                        path_hash, wire_path_graph = parser.get_timing_wire_paths()

                        wire_paths.append((path_hash, wire_path_graph))

        if timing_paths_dir is not None and os.path.isdir(timing_paths_dir):
            self.workspace.logger.info("read paths from %s", timing_paths_dir)
            # get timing paths from timing_paths_dir
            read_from_dir()

        if file_path is not None and os.path.isfile(file_path):
            self.workspace.logger.info("read paths from %s", file_path)
            # get timing paths from file
            parser = VectorsParserJson(
                json_path=file_path, logger=self.workspace.logger
            )
            path_hash, wire_path_graph = parser.get_timing_wire_paths()

            wire_paths.append((path_hash, wire_path_graph))

        if timing_paths_dir is None and file_path is None:
            # read paths from output/vectors/wire_paths in workspace
            timing_paths_dir = self.workspace.paths_table.ieda_vectors["wire_paths"]

            self.workspace.logger.info(
                "read timing paths from workspace %s", timing_paths_dir
            )
            read_from_dir()

        return wire_paths

    def load_timing_paths_metrics(
        self, timing_paths_dir: str = None, file_path: str = None
    ):
        wire_paths = []

        def read_from_dir():
            # get data from directory
            for root, dirs, files in os.walk(timing_paths_dir):
                for _, file in tqdm.tqdm(
                    enumerate(files), total=len(files), desc="timing wire paths"
                ):
                    if file.endswith(".json"):
                        filepath = os.path.join(root, file)

                        parser = VectorsParserJson(
                            json_path=filepath, logger=self.workspace.logger
                        )
                        vec_paths = parser.get_timing_paths_metrics()

                        wire_paths.append(vec_paths)

        if timing_paths_dir is not None and os.path.isdir(timing_paths_dir):
            self.workspace.logger.info("read paths from %s", timing_paths_dir)
            # get timing paths from timing_paths_dir
            read_from_dir()

        if file_path is not None and os.path.isfile(file_path):
            self.workspace.logger.info("read paths from %s", file_path)
            # get timing paths from file
            parser = VectorsParserJson(
                json_path=file_path, logger=self.workspace.logger
            )
            vec_paths = parser.get_timing_paths_metrics()

            wire_paths.append(vec_paths)

        if timing_paths_dir is None and file_path is None:
            # read paths from output/vectors/wire_paths in workspace
            timing_paths_dir = self.workspace.paths_table.ieda_vectors["wire_paths"]

            self.workspace.logger.info(
                "read timing paths from workspace %s", timing_paths_dir
            )
            read_from_dir()

        return wire_paths

    def load_instance_graph(self, graph_path: str = None):
        if graph_path is None:
            graph_path = self.workspace.paths_table.ieda_vectors[
                "timing_instance_graph"
            ]

        parser = VectorsParserJson(json_path=graph_path, logger=self.workspace.logger)
        return parser.get_instance_graph()
