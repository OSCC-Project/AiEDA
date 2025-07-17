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
    RunIEDA
)

def test_28nm():
    # step 1 : create workspace
    # workspace_dir = "{}/example/backend_flow".format(root)
    workspace_dir = "/data2/huangzengrong/test_aieda/workspace1"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : set workspace parameters
    # set def input 
    workspace.set_def_input("/data/project_share/dataset_baseline/gcd/workspace/output/iEDA/result/gcd_floorplan.def")
    
    # set verilog input
    workspace.set_verilog_input("/data/project_share/dataset_baseline/gcd/workspace/output/iEDA/result/gcd_floorplan.v")
    
    # set tech lef
    workspace.set_tech_lef("/data/project_share/process_node/T28_lib/tech/tsmcn28_9lm6X2ZUTRDL.tlef")
    
    # set lefs
    lefs = [
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140hvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140lvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140mb.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140mblvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140opp.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140opphvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140opplvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140oppuhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140oppulvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140uhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140hvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140lvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140mb.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140mblvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140opp.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140opphvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140opplvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140oppuhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140oppulvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140uhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140hvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140lvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140mb.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140mbhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140opp.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140opphvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140opplvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140oppuhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp40p140uhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140mbhvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp30p140ulvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tcbn28hpcplusbwp35p140ulvt.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta64x128m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta64x128m2fw_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta256x32m4fw_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta128x32m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta128x64m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta128x80m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta128x8m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta512x64m4f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta512x64m4fw_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta64x32m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta64x8m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta64x64m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta8x128m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts6n28hpcplvta16x128m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta8x144m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts6n28hpcplvta512x2m8f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta256x16m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta64x80m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta32x128m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta32x32m2f_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta1024x32m8fw_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta128x144m2fw_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/ts5n28hpcplvta256x144m2fw_130a.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tpbn28v.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tphn28hpcpgv18_9lm.lef",
            "/data/project_share/process_node/dataset_baseline/lef/PLLTS28HPMLAINT.lef",
            "/data/project_share/process_node/dataset_baseline/lef/tpbn28v_9lm.lef"
        ]
    workspace.set_lefs(lefs)
    
    # set libs
    libs = [
        "/data/project_share/process_node/dataset_baseline/lib_min/tcbn28hpcplusbwp40p140lvtssg0p81v125c.lib",
        "/data/project_share/process_node/dataset_baseline/lib_min/tcbn28hpcplusbwp30p140lvtssg0p81v125c.lib",
        "/data/project_share/process_node/dataset_baseline/lib_min/tcbn28hpcplusbwp40p140ssg0p81v125c.lib",
        "/data/project_share/process_node/dataset_baseline/lib_min/tcbn28hpcplusbwp40p140hvtssg0p81v125c.lib"
        ]
    workspace.set_libs(libs)
    
    # set sdc
    workspace.set_sdc("/data/project_share/dataset_baseline/gcd/syn_netlist/gcd.sdc")
    
    # set workspace info
    workspace.set_process_node("t28")
    workspace.set_project("gcd")
    workspace.set_design("gcd")
    workspace.set_version("V1")
    workspace.set_task("run_eda")
    
    # config iEDA config
    workspace.set_first_routing_layer("M1")
    workspace.set_ieda_fixfanout_buffer("BUFFD8BWP30P140LVT")
    workspace.set_ieda_cts_buffers(
        [
        "BUFFD3BWP30P140LVT",
        "BUFFD4BWP30P140LVT",
        "BUFFD6BWP30P140LVT",
        "BUFFD8BWP30P140LVT",
        "BUFFD12BWP30P140LVT",
        "BUFFD16BWP30P140LVT"
        ]
    )
    workspace.set_ieda_cts_root_buffer("BUFFD12BWP30P140LVT")
    workspace.set_ieda_placement_buffers(
        [
            "BUFFD3BWP30P140LVT",
            "BUFFD4BWP30P140LVT",
            "BUFFD6BWP30P140LVT",
            "BUFFD8BWP30P140LVT",
            "BUFFD12BWP30P140LVT",
            "BUFFD16BWP30P140LVT"
        ]
    )
    workspace.set_ieda_filler_cells_for_first_iteration(
        [
            "DCAP64BWP40P140HVT",
            "DCAP32BWP40P140HVT",
            "DCAP16BWP40P140HVT",
            "DCAP8BWP40P140HVT",
            "DCAP4BWP40P140HVT"
        ]
    )
    workspace.set_ieda_filler_cells_for_second_iteration(
        [
            "FILL64BWP40P140HVT",
            "FILL32BWP40P140HVT",
            "FILL16BWP40P140HVT",
            "FILL8BWP40P140HVT",
            "FILL4BWP40P140HVT",
            "FILL3BWP40P140HVT",
            "FILL2BWP40P140HVT"
        ]
    )
    workspace.set_ieda_optdrv_buffers(
        [
        "BUFFD4BWP30P140LVT",
        "BUFFD8BWP30P140LVT",
        "BUFFD16BWP30P140LVT"
        ]
    )
    workspace.set_ieda_opthold_buffers(
        [
        "BUFFD1BWP40P140LVT",
        "DEL150MD1BWP40P140LVT",
        "DEL100MD1BWP40P140LVT",
        "DEL075MD1BWP40P140LVT",
        "DEL050MD1BWP40P140LVT",
        "DEL025D1BWP40P140LVT",
        "BUFFD1BWP40P140HVT",
        "DEL150MD1BWP40P140HVT",
        "DEL100MD1BWP40P140HVT",
        "DEL075MD1BWP40P140HVT",
        "DEL050MD1BWP40P140HVT",
        "DEL025D1BWP40P140HVT"
        ]
    )
    workspace.set_ieda_optsetup_buffers(
        [
        "BUFFD4BWP30P140LVT",
        "BUFFD8BWP30P140LVT",
        "BUFFD16BWP30P140LVT"
        ]
    )
    workspace.set_ieda_router_layer(bottom_layer="M2", top_layer="M7")
    
def test_sky130():
    # step 1 : create workspace
    # workspace_dir = "{}/example/backend_flow".format(root)
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
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
    
    # config iEDA config
    workspace.set_first_routing_layer("met1")
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

if __name__ == "__main__":  
    # test_28nm()
    test_sky130()

    exit(0)

