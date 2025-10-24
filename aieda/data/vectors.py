#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : vectors.py
@Author : yell
@Desc : data vectorization api
"""
import os
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

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
            # 收集所有JSON文件路径
            json_files = []
            for root, dirs, files in os.walk(nets_dir):
                for file in files:
                    if file.endswith(".json"):
                        json_files.append(os.path.join(root, file))
            
            # 如果文件数量较少，使用顺序处理
            if len(json_files) < 10:
                for filepath in tqdm.tqdm(json_files, desc="vectors read nets"):
                    json_parser = VectorsParserJson(filepath)
                    nets.extend(json_parser.get_nets())
            else:
                # 使用线程池并行处理
                max_workers = min(multiprocessing.cpu_count(), 16)
                results = []
                
                with tqdm.tqdm(total=len(json_files), desc="vectors read nets") as pbar:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 提交所有任务
                        future_to_file = {executor.submit(process_net_file, filepath): filepath 
                                        for filepath in json_files}
                        
                        # 收集结果
                        for future in as_completed(future_to_file):
                            try:
                                result = future.result()
                                if result:
                                    nets.extend(result)
                            except Exception as e:
                                print(f"Error processing file {future_to_file[future]}: {e}")
                            pbar.update(1)
        
        def process_net_file(filepath):
            """在线程中处理单个网络文件"""
            json_parser = VectorsParserJson(filepath)
            return json_parser.get_nets()

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
            # 收集所有JSON文件路径
            json_files = []
            for root, dirs, files in os.walk(patchs_dir):
                for file in files:
                    if file.endswith(".json"):
                        json_files.append(os.path.join(root, file))
            
            # 如果文件数量较少，使用顺序处理
            if len(json_files) < 10:
                for filepath in tqdm.tqdm(json_files, desc="vectors read patchs"):
                    json_parser = VectorsParserJson(filepath)
                    patchs.extend(json_parser.get_patchs())
            else:
                # 使用线程池并行处理
                max_workers = min(multiprocessing.cpu_count(), 16)
                
                with tqdm.tqdm(total=len(json_files), desc="vectors read patchs") as pbar:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 提交所有任务
                        future_to_file = {executor.submit(process_patch_file, filepath): filepath 
                                        for filepath in json_files}
                        
                        # 收集结果
                        for future in as_completed(future_to_file):
                            try:
                                result = future.result()
                                if result:
                                    patchs.extend(result)
                            except Exception as e:
                                print(f"Error processing file {future_to_file[future]}: {e}")
                            pbar.update(1)
        
        def process_patch_file(filepath):
            """在线程中处理单个patch文件"""
            json_parser = VectorsParserJson(filepath)
            return json_parser.get_patchs()

        if patchs_dir is not None and os.path.isdir(patchs_dir):
            self.workspace.logger.info("read patchs from %s", patchs_dir)
            # get data from patchs directory
            read_from_dir()

        if patch_path is not None and os.path.isfile(patch_path):
            self.workspace.logger.info("read patchs from %s", patch_path)
            # get patchs from patch josn file
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
            # 收集所有JSON文件路径
            json_files = []
            for root, dirs, files in os.walk(timing_paths_dir):
                for file in files:
                    if file.endswith(".json"):
                        json_files.append(os.path.join(root, file))
            
            # 如果文件数量较少，使用顺序处理
            if len(json_files) < 10:
                for filepath in tqdm.tqdm(json_files, desc="timing wire paths"):
                    parser = VectorsParserJson(
                        json_path=filepath, logger=self.workspace.logger
                    )
                    path_hash, wire_path_graph = parser.get_timing_wire_paths()
                    wire_paths.append((path_hash, wire_path_graph))
            else:
                # 使用线程池并行处理
                max_workers = min(multiprocessing.cpu_count(), 16)
                
                with tqdm.tqdm(total=len(json_files), desc="timing wire paths") as pbar:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 提交所有任务
                        future_to_file = {executor.submit(process_wire_path_file, filepath): filepath 
                                        for filepath in json_files}
                        
                        # 收集结果
                        for future in as_completed(future_to_file):
                            try:
                                result = future.result()
                                if result:
                                    wire_paths.append(result)
                            except Exception as e:
                                print(f"Error processing file {future_to_file[future]}: {e}")
                            pbar.update(1)
        
        def process_wire_path_file(filepath):
            """在线程中处理单个wire path文件"""
            parser = VectorsParserJson(
                json_path=filepath, logger=self.workspace.logger
            )
            path_hash, wire_path_graph = parser.get_timing_wire_paths()
            return (path_hash, wire_path_graph)

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
            # 收集所有JSON文件路径
            json_files = []
            for root, dirs, files in os.walk(timing_paths_dir):
                for file in files:
                    if file.endswith(".json"):
                        json_files.append(os.path.join(root, file))
            
            # 如果文件数量较少，使用顺序处理
            if len(json_files) < 10:
                for filepath in tqdm.tqdm(json_files, desc="timing wire paths"):
                    parser = VectorsParserJson(
                        json_path=filepath, logger=self.workspace.logger
                    )
                    vec_paths = parser.get_timing_paths_metrics()
                    wire_paths.append(vec_paths)
            else:
                # 使用线程池并行处理
                max_workers = min(multiprocessing.cpu_count(), 16)
                
                with tqdm.tqdm(total=len(json_files), desc="timing wire paths") as pbar:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 提交所有任务
                        future_to_file = {executor.submit(process_timing_metrics_file, filepath): filepath 
                                        for filepath in json_files}
                        
                        # 收集结果
                        for future in as_completed(future_to_file):
                            try:
                                result = future.result()
                                if result:
                                    wire_paths.append(result)
                            except Exception as e:
                                print(f"Error processing file {future_to_file[future]}: {e}")
                            pbar.update(1)
        
        def process_timing_metrics_file(filepath):
            """在线程中处理单个timing metrics文件"""
            parser = VectorsParserJson(
                json_path=filepath, logger=self.workspace.logger
            )
            return parser.get_timing_paths_metrics()

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

    def load_wire_paths_data(
        self, timing_paths_dir: str = None, file_path: str = None
    ):
        """Load detailed wire path data including capacitance, slew, resistance, incr and nodes."""
        wire_paths_data = []

        def read_from_dir():
            # 收集所有JSON文件路径
            json_files = []
            for root, dirs, files in os.walk(timing_paths_dir):
                for file in files:
                    if file.endswith(".json"):
                        json_files.append(os.path.join(root, file))
            
            # 如果文件数量较少，使用顺序处理
            if len(json_files) < 10:
                for filepath in tqdm.tqdm(json_files, desc="wire paths data"):
                    parser = VectorsParserJson(
                        json_path=filepath, logger=self.workspace.logger
                    )
                    wire_path_data = parser.get_wire_paths_data()
                    wire_paths_data.append(wire_path_data)
            else:
                # 使用线程池并行处理
                max_workers = min(multiprocessing.cpu_count(), 16)
                
                with tqdm.tqdm(total=len(json_files), desc="wire paths data") as pbar:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 提交所有任务
                        future_to_file = {executor.submit(process_wire_paths_data_file, filepath): filepath 
                                        for filepath in json_files}
                        
                        # 收集结果
                        for future in as_completed(future_to_file):
                            try:
                                result = future.result()
                                if result:
                                    wire_paths_data.append(result)
                            except Exception as e:
                                print(f"Error processing file {future_to_file[future]}: {e}")
                            pbar.update(1)
        
        def process_wire_paths_data_file(filepath):
            """在线程中处理单个wire paths数据文件"""
            parser = VectorsParserJson(
                json_path=filepath, logger=self.workspace.logger
            )
            return parser.get_wire_paths_data()

        if timing_paths_dir is not None and os.path.isdir(timing_paths_dir):
            self.workspace.logger.info("read wire paths data from %s", timing_paths_dir)
            # get timing paths from timing_paths_dir
            read_from_dir()

        if file_path is not None and os.path.isfile(file_path):
            self.workspace.logger.info("read wire paths data from %s", file_path)
            # get timing paths from file
            parser = VectorsParserJson(
                json_path=file_path, logger=self.workspace.logger
            )
            wire_path_data = parser.get_wire_paths_data()

            if wire_path_data:
                wire_paths_data.append(wire_path_data)

        if timing_paths_dir is None and file_path is None:
            # read paths from output/vectors/wire_paths in workspace
            timing_paths_dir = self.workspace.paths_table.ieda_vectors["wire_paths"]

            self.workspace.logger.info(
                "read wire paths data from workspace %s", timing_paths_dir
            )
            read_from_dir()

        return wire_paths_data

    def load_instance_graph(self, graph_path: str = None):
        if graph_path is None:
            graph_path = self.workspace.paths_table.ieda_vectors[
                "timing_instance_graph"
            ]

        parser = VectorsParserJson(json_path=graph_path, logger=self.workspace.logger)
        return parser.get_instance_graph()
