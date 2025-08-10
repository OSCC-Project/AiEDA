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


LIB_PATHS = [
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
    "/data/project_share/process_node/T28_lib/ccslib/RocketTile_postroute_func_ssg0p81vm40c_cworst_T_setup.lib",
    "/data/project_share/process_node/T28_lib/ccslib/ts6n28hpcplvta2048x32m8sw_130a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/ccslib/ts1n28hpcplvtb2048x48m8sw_180a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/ccslib/ts1n28hpcplvtb8192x64m8sw_180a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts5n28hpcplvta256x64m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts1n28hpcplvtb1024x64m4sw_180a_ssg0p81v125c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts5n28hpcplvta256x128m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/beihai/lib/ts5n28hpcplvta64x88m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/beihai/lib/ts5n28hpcplvta512x64m4sw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/beihai/lib/ts5n28hpcplvta64x84m2fw_130a_ssg0p81v125c.lib"
]

DESIGNS_T28 = [
        # "/data2/project_share/dataset_baseline/s713/workspace",
        "/data2/project_share/dataset_baseline/s44/workspace",
        "/data2/project_share/dataset_baseline/apb4_rng/workspace",
        "/data2/project_share/dataset_baseline/gcd/workspace",
        "/data2/project_share/dataset_baseline/s1238/workspace",
        "/data2/project_share/dataset_baseline/s1488/workspace",
        "/data2/project_share/dataset_baseline/apb4_archinfo/workspace",
        "/data2/project_share/dataset_baseline/apb4_ps2/workspace",
        "/data2/project_share/dataset_baseline/s9234/workspace",
        "/data2/project_share/dataset_baseline/apb4_timer/workspace",
        "/data2/project_share/dataset_baseline/s13207/workspace",
        "/data2/project_share/dataset_baseline/apb4_i2c/workspace",
        "/data2/project_share/dataset_baseline/s5378/workspace",
        "/data2/project_share/dataset_baseline/apb4_pwm/workspace",
        "/data2/project_share/dataset_baseline/apb4_wdg/workspace",
        "/data2/project_share/dataset_baseline/apb4_clint/workspace",
        "/data2/project_share/dataset_baseline/ASIC/workspace",
        "/data2/project_share/dataset_baseline/s15850/workspace",
        "/data2/project_share/dataset_baseline/apb4_uart/workspace",
        "/data2/project_share/dataset_baseline/s38417/workspace",
        "/data2/project_share/dataset_baseline/s35932/workspace",
        "/data2/project_share/dataset_baseline/s38584/workspace",
        "/data2/project_share/dataset_baseline/BM64/workspace",
        "/data2/project_share/dataset_baseline/picorv32/workspace",
        "/data2/project_share/dataset_baseline/PPU/workspace",
        "/data2/project_share/dataset_baseline/blabla/workspace",
        "/data2/project_share/dataset_baseline/aes_core/workspace",
        "/data2/project_share/dataset_baseline/aes/workspace",
        "/data2/project_share/dataset_baseline/salsa20/workspace",
        # "/data2/project_share/dataset_baseline/jpeg_encoder/workspace",
        # "/data2/project_share/dataset_baseline/eth_top/workspace",
        # "/data2/project_share/dataset_baseline/yadan_riscv_sopc/workspace",
        # "/data2/project_share/dataset_baseline/beihai/workspace",
        # "/data2/project_share/dataset_baseline/shanghai_MS/workspace",
        # "/data2/project_share/dataset_baseline/nvdla/workspace",
        # "/data2/project_share/dataset_baseline/ZJU_asic_top/workspace",
        # "/data2/project_share/dataset_baseline/iEDA_2023/workspace",
        # "/data2/project_share/dataset_baseline/ysyx4_SoC2/workspace",
        # "/data2/project_share/dataset_baseline/BEIHAI_2.0/workspace",
        # "/data2/project_share/dataset_baseline/AIMP/workspace",
        # "/data2/project_share/dataset_baseline/AIMP_2.0/workspace",
        # "/data2/project_share/dataset_baseline/ysyx6/workspace",
        # "/data2/project_share/dataset_baseline/WUKONG/workspace",
        # "/data2/project_share/dataset_baseline/ysyx4_SoC1/workspace",
        # "/data2/project_share/dataset_baseline/ysyx4_2/workspace",
        # "/data2/project_share/dataset_baseline/T1/workspace",
        # "/data2/project_share/dataset_baseline/T1_machamp/workspace",
        # "/data2/project_share/dataset_baseline/nanhu-G/workspace",
        # "/data2/project_share/dataset_baseline/openC910/workspace",
        # "/data2/project_share/dataset_baseline/T1_sandslash/workspace",
    ]


def test_vectors_generation(workspace, design, patch_row_step : int, patch_col_step : int):
    # step 1 : init by workspace
    data_gen = DataGeneration(workspace)
    
    # step 2 : generate vectors
    vectors_dir="/data2/project_share/dataset_baseline/" + design + "/workspace/output/innovus/vectors"
    input_def = "/data2/project_share/dataset_baseline/" + design + "/workspace/output/innovus/result/" + design + "_route.def"
    import os
    if not os.path.exists(input_def):
        # If uncompressed file not found, try to read compressed DEF file
        input_def = "/data2/project_share/dataset_baseline/" + design + "/workspace/output/innovus/result/" + design + "_route.def.gz"
    
    data_gen.generate_vectors(input_def=input_def,
                               vectors_dir=vectors_dir,
                               patch_row_step=patch_row_step,
                               patch_col_step=patch_col_step)
    # data_gen.generate_patterns()
    # vectors_dir="/data/project_share/dataset_baseline/gcd/workspace/output/innovus/vectors"
    
    # data_gen.generate_patterns()
    
def test_vectors_load(workspace):
    data_load = DataVectors(workspace)
    
    cells = data_load.load_cells()
    
    instances = data_load.load_instances()
    
    nets = data_load.load_nets()
    
    patchs = data_load.load_patchs()
    
    instance_graph = data_load.load_instance_graph()
    
    timing_graph = data_load.load_timing_graph()
    
    timint_wire_paths = data_load.load_timing_wire_paths()
    
    print(1)
    
if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data/project_share/dataset_baseline/eth_top/workspace"
    # workspace_dir = "/data2/project_share/dataset_baseline/s713/workspace"
    # workspace_dir = "/data/project_share/dataset_baseline/gcd/workspace"
    # workspace = workspace_create(directory=workspace_dir, design="s713")
    
    # workspace.set_libs(LIB_PATHS)
    
    # test_vectors_generation(workspace, patch_row_step=18, patch_col_step=18)
    # test_vectors_load(workspace)
    
    for workspace_dir in DESIGNS_T28:
        print("process workspace : ", workspace_dir)
        
        design = workspace_dir.split("/")[-2]
        workspace = workspace_create(directory=workspace_dir, design=design)
        
        workspace.set_libs(LIB_PATHS)
        
        test_vectors_generation(workspace, design, patch_row_step=18, patch_col_step=18)
        
        # test_vectors_load(workspace)

    exit(0)

