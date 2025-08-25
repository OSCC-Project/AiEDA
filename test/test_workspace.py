#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_flows.py
@Author : yell
@Desc : test physical design flows for iEDA
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    RunIEDA,
    DbFlow
)
    
def create_workspace_sky130_gcd(workspace_dir):
    flow_db_list = []

    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.floorplan, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.pdn, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optSetup, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.drc, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.vectorization, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.filler, state=DbFlow.FlowState.Unstart)) 
    
    # step 1 : create workspace
    # workspace_dir = "{}/example/backend_flow".format(root)
    workspace = workspace_create(directory=workspace_dir, design="gcd", flow_list=flow_db_list)
    
    import sys
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit('/', 1)[0]
    foundry_dir = "{}/aieda/third_party/iEDA/scripts/foundry/sky130".format(root)
    
    # step 2 : set workspace parameters
    # set def input 
    example_sky130_dir = "{}/example/sky130_gcd".format(root)
    workspace.set_def_input("{}/output/iEDA/result/gcd_floorplan.def".format(example_sky130_dir))
    
    # set verilog input
    workspace.set_verilog_input("{}/output/iEDA/result/gcd_floorplan.v".format(example_sky130_dir))
    
    # set tech lef
    workspace.set_tech_lef("{}/lef/sky130_fd_sc_hs.tlef".format(foundry_dir))
    
    # set lefs
    lefs = [
            "{}/lef/sky130_fd_sc_hs_merged.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__com_bus_slice_10um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__com_bus_slice_1um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__com_bus_slice_20um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__com_bus_slice_5um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__connect_vcchib_vccd_and_vswitch_vddio_slice_20um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__corner_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__disconnect_vccd_slice_5um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__disconnect_vdda_slice_5um.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__gpiov2_pad_wrapped.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vccd_hvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vccd_lvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vdda_hvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vdda_lvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vddio_hvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vddio_lvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vssa_hvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vssa_lvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vssd_hvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vssd_lvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vssio_hvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_ef_io__vssio_lvc_pad.lef".format(foundry_dir),
            "{}/lef/sky130_fd_io__top_xres4v2.lef".format(foundry_dir),
            "{}/lef/sky130io_fill.lef".format(foundry_dir),
            "{}/lef/sky130_sram_1rw1r_128x256_8.lef".format(foundry_dir),
            "{}/lef/sky130_sram_1rw1r_44x64_8.lef".format(foundry_dir),
            "{}/lef/sky130_sram_1rw1r_64x256_8.lef".format(foundry_dir),
            "{}/lef/sky130_sram_1rw1r_80x64_8.lef".format(foundry_dir)
        ]
    workspace.set_lefs(lefs)
    
    # set libs
    libs = [
        "{}/lib/sky130_fd_sc_hs__tt_025C_1v80.lib".format(foundry_dir),
        "{}/lib/sky130_dummy_io.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_128x256_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_44x64_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_64x256_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_80x64_8_TT_1p8V_25C.lib".format(foundry_dir)
        ]
    workspace.set_libs(libs)
    
    # set sdc
    workspace.set_sdc("{}/sdc/gcd.sdc".format(foundry_dir))
    
    # set spef
    workspace.set_spef("{}/spef/gcd.spef".format(foundry_dir))
    
    # set workspace info
    workspace.set_process_node("sky130")
    workspace.set_project("gcd")
    workspace.set_design("gcd")
    workspace.set_version("V1")
    workspace.set_task("run_eda")
    
    workspace.set_first_routing_layer("li1")
    
    # config iEDA config
    workspace.set_ieda_fixfanout_buffer("sky130_fd_sc_hs__buf_8")
    workspace.set_ieda_cts_buffers(
        [
        "sky130_fd_sc_hs__buf_1"
        ]
    )
    workspace.set_ieda_cts_root_buffer("sky130_fd_sc_hs__buf_1")
    workspace.set_ieda_placement_buffers(
        [
            "sky130_fd_sc_hs__buf_1"
        ]
    )
    workspace.set_ieda_filler_cells_for_first_iteration(
        [
           "sky130_fd_sc_hs__fill_8",
            "sky130_fd_sc_hs__fill_4",
            "sky130_fd_sc_hs__fill_2",
            "sky130_fd_sc_hs__fill_1"
        ]
    )
    workspace.set_ieda_filler_cells_for_second_iteration(
        [
            "sky130_fd_sc_hs__fill_8",
            "sky130_fd_sc_hs__fill_4",
            "sky130_fd_sc_hs__fill_2",
            "sky130_fd_sc_hs__fill_1"
        ]
    )
    workspace.set_ieda_optdrv_buffers(
        [
        "sky130_fd_sc_hs__buf_8"
        ]
    )
    workspace.set_ieda_opthold_buffers(
        [
        "sky130_fd_sc_hs__buf_8"
        ]
    )
    workspace.set_ieda_optsetup_buffers(
        [
        "sky130_fd_sc_hs__buf_8"
        ]
    )
    workspace.set_ieda_router_layer(bottom_layer="met1", top_layer="met4")
    
    return workspace

def create_workspace_cx55_minirv(workspace_dir):
    flow_db_list = []

    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.floorplan, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optSetup, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization, state=DbFlow.FlowState.Unstart))
    flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.drc, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.vectorization, state=DbFlow.FlowState.Unstart))
    # flow_db_list.append(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.filler, state=DbFlow.FlowState.Unstart)) 

    # step 1 : create workspace
    workspace = workspace_create(directory=workspace_dir, design="minirv", flow_list=flow_db_list)
    
    import sys
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit('/', 1)[0]
    foundry_dir = "/data2/project_share/cx55/minirv_cx55/lib"
    
    # step 2 : set workspace parameters
    # set def input 
    workspace.set_def_input("/data2/project_share/cx55/minirv_cx55/workspace_cx55/output/iEDA/result/minirv.def")
    
    # set verilog input
    workspace.set_verilog_input("/data2/project_share/cx55/minirv_cx55/workspace_cx55/output/iEDA/result/minirv.v")
    
    # set tech lef
    workspace.set_tech_lef("/data2/project_share/cx55/minirv_cx55/lib/tlef_1P6M_7T_0530_zzs.lef")
    
    # set lefs
    lefs = [
            "/data2/project_share/cx55/minirv_cx55/lib/ICSSCA_N55_H7BH.lef",
            "/data2/project_share/cx55/minirv_cx55/lib/ICSSCA_N55_H7BL.lef",
            "/data2/project_share/cx55/minirv_cx55/lib/ICSSCA_N55_H7BR.lef"
        ]
    workspace.set_lefs(lefs)
    
    # set libs
    libs = [
        "/data2/project_share/cx55/minirv_cx55/lib/ETSCA_N55_H7BH_DTT_PTYPICAL_V1P2_T25.lib",
        "/data2/project_share/cx55/minirv_cx55/lib/ETSCA_N55_H7BL_DTT_PTYPICAL_V1P2_T25.lib",
        "/data2/project_share/cx55/minirv_cx55/lib/ETSCA_N55_H7BR_DTT_PTYPICAL_V1P2_T25.lib"
        ]
    workspace.set_libs(libs)
    
    # set sdc
    workspace.set_sdc("/data2/project_share/cx55/minirv_cx55/syn_netlist/default.sdc")
    
    # set spef
    workspace.set_spef("")
    
    # set workspace info
    workspace.set_process_node("cx55")
    workspace.set_project("minirv")
    workspace.set_design("minirv")
    workspace.set_version("V1")
    workspace.set_task("run_eda")
    
    workspace.set_first_routing_layer("MET1")
    
    # config iEDA config
    workspace.set_ieda_fixfanout_buffer("BUFX4H7L")
    workspace.set_ieda_cts_buffers(
        [
        "BUFX4H7L"
        ]
    )
    workspace.set_ieda_cts_root_buffer("BUFX4H7L")
    workspace.set_ieda_placement_buffers(
        [
            "BUFX4H7L"
        ]
    )
    workspace.set_ieda_filler_cells_for_first_iteration(
        [
            "FILLCAP32H7H"
        ]
    )
    workspace.set_ieda_filler_cells_for_second_iteration(
        [
            "FILLCAP32H7H"
        ]
    )
    workspace.set_ieda_optdrv_buffers(
        [
        "BUFX4H7L"
        ]
    )
    workspace.set_ieda_opthold_buffers(
        [
        "BUFX4H7L"
        ]
    )
    workspace.set_ieda_optsetup_buffers(
        [
        "BUFX4H7L"
        ]
    )
    workspace.set_ieda_router_layer(bottom_layer="MET1", top_layer="MET5")
    
    return workspace

if __name__ == "__main__":    
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130_5"
    workspace = create_workspace_sky130_gcd(workspace_dir)
    # workspace_dir = "/data2/huangzengrong/test_aieda/minirv4"
    # workspace = create_workspace_cx55_minirv(workspace_dir)

    exit(0)

