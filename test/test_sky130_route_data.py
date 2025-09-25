#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_ieda_flows.py
@Author : yell
@Desc : test physical design flows for iEDA
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################
import os

os.environ["iEDA"] = "ON"

from aieda.workspace import Workspace, workspace_create
from aieda.flows import DbFlow, RunIEDA, DataGeneration
from aieda.data.database import EDAParameters


def create_workspace_sky130(workspace_dir, design, verilog, sdc, spef=""):
    flow_db_list = []

    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.floorplan,
            state=DbFlow.FlowState.Unstart,
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.pdn, state=DbFlow.FlowState.Unstart
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.fixFanout,
            state=DbFlow.FlowState.Unstart,
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.place, state=DbFlow.FlowState.Unstart
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.cts, state=DbFlow.FlowState.Unstart
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.optDrv, state=DbFlow.FlowState.Unstart
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.optHold,
            state=DbFlow.FlowState.Unstart,
        )
    )

    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.legalization,
            state=DbFlow.FlowState.Unstart,
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.route, state=DbFlow.FlowState.Unstart
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.drc, state=DbFlow.FlowState.Unstart
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.vectorization,
            state=DbFlow.FlowState.Unstart,
        )
    )
    flow_db_list.append(
        DbFlow(
            eda_tool="iEDA", step=DbFlow.FlowStep.filler, state=DbFlow.FlowState.Unstart
        )
    )

    # step 1 : create workspace
    target_workspace_dir = os.path.join(workspace_dir, design) if os.path.basename(os.path.normpath(workspace_dir)) != design else workspace_dir
    workspace = workspace_create(
        directory=target_workspace_dir, design=design, flow_list=flow_db_list
    )

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]
    # get foundry from iEDA
    foundry_dir = "{}/aieda/third_party/iEDA/scripts/foundry/sky130".format(root)

    # step 2 : set workspace process node definition
    # set verilog input
    workspace.set_verilog_input(verilog)

    # set tech lef
    workspace.set_tech_lef("{}/lef/sky130_fd_sc_hd.tlef".format(foundry_dir))

    # set lefs
    lefs = [
        "{}/lef/sky130_fd_sc_hd_merged.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_10um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_1um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_20um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_5um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__connect_vcchib_vccd_and_vswitch_vddio_slice_20um.lef".format(
            foundry_dir
        ),
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
        "{}/lef/sky130_sram_1rw1r_80x64_8.lef".format(foundry_dir),
    ]
    workspace.set_lefs(lefs)

    # set libs
    libs = [
        "{}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib".format(foundry_dir),
        "{}/lib/sky130_dummy_io.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_128x256_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_44x64_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_64x256_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_80x64_8_TT_1p8V_25C.lib".format(foundry_dir),
    ]
    workspace.set_libs(libs)

    # set sdc
    workspace.set_sdc(sdc)

    # set spef
    workspace.set_spef(spef)

    # set workspace info
    workspace.set_process_node("sky130")
    workspace.set_project(design)
    workspace.set_design(design)
    workspace.set_version("V1")
    workspace.set_task("run_eda")

    workspace.set_first_routing_layer("li1")

    # config iEDA config
    workspace.set_ieda_fixfanout_buffer("sky130_fd_sc_hd__buf_8")
    workspace.set_ieda_cts_buffers(["sky130_fd_sc_hd__buf_1"])
    workspace.set_ieda_cts_root_buffer("sky130_fd_sc_hd__buf_1")
    workspace.set_ieda_placement_buffers(["sky130_fd_sc_hd__buf_1"])
    workspace.set_ieda_filler_cells_for_first_iteration(
        [
            "sky130_fd_sc_hd__fill_8",
            "sky130_fd_sc_hd__fill_4",
            "sky130_fd_sc_hd__fill_2",
            "sky130_fd_sc_hd__fill_1",
        ]
    )
    workspace.set_ieda_filler_cells_for_second_iteration(
        [
            "sky130_fd_sc_hd__fill_8",
            "sky130_fd_sc_hd__fill_4",
            "sky130_fd_sc_hd__fill_2",
            "sky130_fd_sc_hd__fill_1",
        ]
    )
    workspace.set_ieda_optdrv_buffers(["sky130_fd_sc_hd__buf_8"])
    workspace.set_ieda_opthold_buffers(["sky130_fd_sc_hd__buf_8"])
    workspace.set_ieda_optsetup_buffers(["sky130_fd_sc_hd__buf_8"])
    workspace.set_ieda_router_layer(bottom_layer="met1", top_layer="met4")

    return workspace



def run_eda_flow(workspace: Workspace):
 
    run_ieda = RunIEDA(workspace)
    
    run_ieda.run_CTS(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place)
        )
    )

    run_ieda.run_optimizing_drv(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts)
        )
    )

    run_ieda.run_optimizing_hold(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv)
        )
    )

    run_ieda.run_legalization(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold)
        )
    )

    run_ieda.run_routing(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization)
        )
    )


if __name__ == "__main__":
    # step 1 : create workspace
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/output".format(root)
    design = "gcd"
    verilog = "{}/example/output/{}/output/iEDA/result/{}_place.v.gz".format(root, design, design)
    sdc = ""
    spef = ""
    
    workspace = create_workspace_sky130(workspace_dir, design, verilog, sdc, spef)
    run_eda_flow(workspace)
    
    exit(0)
