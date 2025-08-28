#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_vectors.py
@Author : yell
@Desc : test data vectorization for iEDA
'''
######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    DbFlow,
    DataGeneration,
    DataVectors,
    Workspace
)


def test_vectors_generation(workspace : Workspace, patch_row_step : int, patch_col_step : int):
    # step 1 : init by workspace
    data_gen = DataGeneration(workspace)
    
    # step 2 : generate vectors
    data_gen.generate_vectors(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)),
                               vectors_dir=workspace.paths_table.ieda_output['vectors'],
                               patch_row_step=patch_row_step,
                               patch_col_step=patch_col_step)
    data_gen.generate_patterns()
    
def test_vectors_nets_to_def(workspace : Workspace):
    # step 1 : init by workspace
    data_gen = DataGeneration(workspace)
    
    # step 2 : transform vectors nets to def  
    data_gen.vectors_nets_to_def()
    
def test_vectors_load(workspace):
    data_load = DataVectors(workspace)
    
    layers = data_load.load_layers()
    
    vias = data_load.load_vias()
    
    cells = data_load.load_cells()
    
    instances = data_load.load_instances()
    
    nets = data_load.load_nets()
    
    patchs = data_load.load_patchs()
    
    instance_graph = data_load.load_instance_graph()
    
    timing_graph = data_load.load_timing_graph()
    
    timint_wire_paths = data_load.load_timing_wire_paths()
    
    print(1)
    
if __name__ == "__main__":  
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit('/', 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)
    
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    test_vectors_generation(workspace, patch_row_step=9, patch_col_step=9)
    test_vectors_nets_to_def(workspace)
    test_vectors_load(workspace)

    exit(0)

