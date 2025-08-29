#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : placement.py
@Author : yell
@Desc : placement api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAPlacement(IEDAIO):
    """placement api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def _configs(self):
        super()._configs()
        
        self.ieda_config = self.workspace.paths_table.ieda_config['place']
    
    def _run_flow(self): 
        match self.flow.step:
            case DbFlow.FlowStep.place:
                self._run_placement()  
            case DbFlow.FlowStep.legalization:
                self._run_legalization()   
            case DbFlow.FlowStep.filler:
                self._run_filler()      
    '''    
    def _run_placement(self):
        self.read_def()
        
        self.ieda.run_placer(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self._generate_placement_feature_summary()
        self._generate_placement_feature_tool()
        self._generate_feature_map()
    '''
    def _run_placement(self):
        print("DEBUG: _run_placement开始")
        
        print("DEBUG: 第1步：读取DEF文件")
        self.read_def()
        print("DEBUG: 第1步完成")
        
        print("DEBUG: 第2步：运行placement算法")
        self.ieda.run_placer(self.ieda_config)
        print("DEBUG: 第2步完成")
        
        print("DEBUG: 第3步：保存DEF文件")
        self.def_save()
        print("DEBUG: 第3步完成")
        
        print("DEBUG: 第4步：保存Verilog文件")
        self.verilog_save(self.cell_names)
        print("DEBUG: 第4步完成")
        
        print("DEBUG: 第5步：生成特征数据")
        self._generate_placement_feature_summary()
        self._generate_placement_feature_tool()
        self._generate_feature_map()
        print("DEBUG: 第5步完成")
        
        print("DEBUG: _run_placement完成")

    def _run_legalization(self):
        self.read_def()
        
        self.ieda.run_incremental_flow(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self._generate_legalization_feature_summary()
        self._generate_legalization_feature_tool()
        
    def _run_filler(self):
        self.read_def()
        
        self.ieda.run_filler(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self._generate_filler_feature_summary()
        self._generate_filler_feature_tool()
    
    def _generate_feature_summary(self, json_path:str=None):
        match self.flow.step:
            case DbFlow.FlowStep.place:
                self._generate_placement_feature_summary(json_path)  
            case DbFlow.FlowStep.legalization:
                self._generate_legalization_feature_summary(json_path)   
            case DbFlow.FlowStep.filler:
                self._generate_filler_feature_summary(json_path)
                
    def _generate_placement_feature_summary(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['place_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def _generate_legalization_feature_summary(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['legalization_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def _generate_filler_feature_summary(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['filler_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def _generate_feature_tool(self):
        match self.flow.step:
            case DbFlow.FlowStep.place:
                self._generate_placement_feature_tool()  
            case DbFlow.FlowStep.legalization:
                self._generate_legalization_feature_tool()   
            case DbFlow.FlowStep.filler:
                self._generate_filler_feature_tool()
        
    def _generate_placement_feature_tool(self):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['place_tool'], DbFlow.FlowStep.place.value)
    
    def _generate_feature_map(self, map_grid_size = 1):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate eval metrics. The default map_grid_size is 1X row_height.
        self.ieda.feature_pl_eval(ieda_feature_json['place_map'], map_grid_size)
        
    def _generate_legalization_feature_tool(self):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['legalization_tool'], DbFlow.FlowStep.legalization.value)
        
    def _generate_filler_feature_tool(self):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['filler_tool'], DbFlow.FlowStep.filler.value)
        
    def run_mp(self, config : str, tcl_path=""):
        self.ieda.runMP(config, tcl_path)
    
    def run_refinement(self, tcl_path=""):
        self.ieda.runRef(tcl_path)
        
    def _run_ai_placement(self, onnx_path: str, normalization_path: str):
        """
        Run AI-guided placement using ONNX model
        
        Args:
            onnx_path: Path to the ONNX model file
            normalization_path: Path to the normalization parameters JSON file
        """
        
        self.read_def()
        
        self.ieda.run_ai_placement(self.ieda_config, onnx_path, normalization_path)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        # self._generate_placement_feature_summary()
        # self._generate_placement_feature_tool()
        # self._generate_feature_map()
        
    # build macro drc distribution
    def feature_macro_drc_distribution(self, path: str, drc_path: str):
        self.ieda.feature_macro_drc(path=path, drc_path=drc_path)