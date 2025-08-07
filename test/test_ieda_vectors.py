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
    DataVectors
)


lib_paths = [
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140ssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140hvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140lvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140mbssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140mblvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140oppssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140opphvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140opplvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140oppuhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140oppulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140uhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140ssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140hvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140lvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140mbssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140mblvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140oppssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140opphvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140opplvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140oppuhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140oppulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140uhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140ssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140hvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140lvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140mbssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140mbhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140oppssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140opphvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140opplvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140oppuhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140uhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140mbhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140ulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140ulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x128m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta256x32m4fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x32m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x64m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x80m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x8m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta512x64m4f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta512x64m4fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x32m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x8m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta32x32m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta32x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x80m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta256x16m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts6n28hpcplvta512x2m8f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta8x144m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts6n28hpcplvta16x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta8x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x64m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta1024x32m8fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta256x144m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x144m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tphn28hpcpgv18ssg0p81v1p62v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/PLLTS28HPMLAINT_SS_0P81_125C.lib",
    "/data/project_share/process_node/dataset_baseline/lib/RocketTile_MAX.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts1n28hpcplvtb8192x64m8sw_180a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts5n28hpcplvta256x64m2fw_130a_ssg0p9v125c.lib"
]

def test_vectors_generation(workspace, patch_row_step : int, patch_col_step : int):
    # step 1 : init by workspace
    data_gen = DataGeneration(workspace)
    
    # step 2 : generate vectors
    # vectors_dir="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/vectors"
    # data_gen.generate_vectors(input_def="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/result/eth_top_route.def",
    #                            vectors_dir=vectors_dir)
    # data_gen.generate_vectors()
    
    # data_gen.generate_patterns()
    # vectors_dir="/data/project_share/dataset_baseline/gcd/workspace/output/innovus/vectors"
    data_gen.generate_vectors(patch_row_step=patch_row_step,
                              patch_col_step=patch_col_step)
    
    data_gen.generate_patterns()
    
def test_vectors_load(workspace):
    data_load = DataVectors(workspace)
    
    # cells = data_load.load_cells()
    
    # instances = data_load.load_instances()
    
    # nets = data_load.load_nets()
    
    # patchs = data_load.load_patchs()
    
    timing_graph = data_load.load_timing_graph()
    
    timint_wire_paths = data_load.load_timing_wire_paths()
    
    print(1)
    
if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data/project_share/dataset_baseline/eth_top/workspace"
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130_1"
    # workspace_dir = "/data/project_share/dataset_baseline/gcd/workspace"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # workspace.set_libs(lib_paths)
    
    # test_vectors_generation(workspace, patch_row_step=9, patch_col_step=9)
    test_vectors_load(workspace)

    exit(0)

