#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : vectorization.py
@Author : yell
@Desc : data vectorization api
'''
import os
import tqdm

from typing import List

from aieda import workspace
from ..workspace.workspace import Workspace
from ..flows import DbFlow
from .io import VectorsParserJson
from .database.vectors import VectorNet

class DataVectors:
    def __init__(self, workspace : Workspace):
        self.workspace = workspace
        
    def load_nets(self, nets_dir:str=None, net_path:str=None):  
        nets = []   
        
        def read_from_dir():
            # get data from nets directory
            for root, dirs, files in os.walk(nets_dir):
                for _, file in tqdm.tqdm(enumerate(files), total=len(files), desc="vectors read nets"):
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
            #read nets from output/vectors/nets in workspace
            nets_dir = self.workspace.paths_table.ieda_vectors['nets']
            
            self.workspace.logger.info("read nets from workspace %s", nets_dir)
            read_from_dir()
        
        return nets
    
    def load_patchs(self, patchs_dir:str=None, patch_path:str=None):  
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
            #read patchs from output/vectors/patchs in workspace
            patchs_dir = self.workspace.paths_table.ieda_vectors['patchs']
            
            self.workspace.logger.info("read patchs from workspace %s", patchs_dir)
            read_from_dir()
        
        return patchs
        
    def load_timing_graph(self, graph_path : str = None):
        from .io import VectorsParserYaml
        
        if graph_path is None:
            graph_path = self.workspace.paths_table.ieda_vectors['timing_wire_graph']
        parser = VectorsParserYaml(yaml_path=graph_path,
                                             logger=self.workspace.logger)
        return parser.get_wire_graph()
    
    def load_timing_wire_paths(self, timing_paths_dir:str=None, file_path:str=None): 
        from .io import VectorsParserYaml
         
        wire_paths = []   
        
        def read_from_dir():
            # get data from directory
            for root, dirs, files in os.walk(timing_paths_dir):
                for _, file in tqdm.tqdm(enumerate(files), total=len(files), desc="timing wire paths"):
                    if file.endswith(".yml"):                    
                        filepath = os.path.join(root, file)
                        
                        parser = VectorsParserYaml(yaml_path=filepath,
                                                   logger=self.workspace.logger)
                        yaml_path_hash, yaml_data = parser.get_timing_wire_paths()
                        
                        wire_paths.append((yaml_path_hash, yaml_data))
                
        if timing_paths_dir is not None and os.path.isdir(timing_paths_dir):
            self.workspace.logger.info("read paths from %s", timing_paths_dir)
            # get timing paths from timing_paths_dir
            read_from_dir()
        
        if file_path is not None and os.path.isfile(file_path):
            self.workspace.logger.info("read paths from %s", file_path)
            # get timing paths from file
            parser = VectorsParserYaml(yaml_path=file_path,
                                       logger=self.workspace.logger)
            yaml_path_hash, yaml_data = parser.get_timing_wire_paths()
            
            wire_paths.append((yaml_path_hash, yaml_data))
            
        if timing_paths_dir is None and file_path is None:
            #read paths from output/vectors/wire_paths in workspace
            timing_paths_dir = self.workspace.paths_table.ieda_vectors['wire_paths']
            
            self.workspace.logger.info("read timing paths from workspace %s", timing_paths_dir)
            read_from_dir()
        
        return wire_paths
    
    
    def generate_nets_patterns(self, vector_nets : List[VectorNet]=[],
                               epsilon: int = 1,
                               patterns_csv : str=None):
        if len(vector_nets) == 0:
            # load data from output/vectors/nets in workspace
            vector_nets = self.load_nets()
            
        from .io import VectorWirePatternGen
        net_patterns_gen = VectorWirePatternGen(epsilon=epsilon)

        for vec_net in tqdm.tqdm(vector_nets, desc="build vector net wires"):
            wires = vec_net.wires
            for wire in wires:
                net_patterns_gen.add_wire(wire)
                
        if patterns_csv is None:
            patterns_csv = self.workspace.paths_table.ieda_vectors['wire_patterns']

        net_patterns_gen.generate(patterns_csv)