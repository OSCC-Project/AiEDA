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
from aieda.analysis import CellTypeAnalyzer, CoreUsageAnalyzer, PinDistributionAnalyzer, ResultStatisAnalyzer
from aieda.analysis import WireDistributionAnalyzer, MetricsCorrelationAnalyzer
from aieda.analysis import DelayAnalyzer, StageAnalyzer
from aieda.analysis import WireDensityAnalyzer, FeatureCorrelationAnalyzer, MapAnalyzer


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
    # flow_db_list.append(
    #     DbFlow(
    #         eda_tool="iEDA",
    #         step=DbFlow.FlowStep.optSetup,
    #         state=DbFlow.FlowState.Unstart,
    #     )
    # )
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
    workspace = workspace_create(
        directory=workspace_dir, design="gcd", flow_list=flow_db_list
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


def set_parameters(workspace: Workspace):
    parameters = EDAParameters()
    parameters.placement_target_density = 0.4
    # parameters.placement_max_phi_coef = 1.04
    # parameters.placement_init_wirelength_coef = 0.15
    # parameters.placement_min_wirelength_force_bar = -54.04
    # parameters.cts_skew_bound = 0.1
    # parameters.cts_max_buf_tran = 1.2
    # parameters.cts_max_sink_tran = 1.1
    # parameters.cts_max_cap = 0.2
    # parameters.cts_max_fanout = 32
    # parameters.cts_cluster_size = 32

    workspace.update_parameters(parameters=parameters)

    workspace.print_paramters()


def run_eda_flow(workspace: Workspace, clock_nets):
    def run_floorplan_sky130(workspace: Workspace, clock_nets):
        def run_floorplan():
            from aieda.eda import IEDAFloorplan

            flow = DbFlow(
                eda_tool="iEDA",
                step=DbFlow.FlowStep.floorplan,
                input_def=workspace.configs.paths.def_input_path,
                input_verilog=workspace.configs.paths.verilog_input_path,
            )
            # set state running
            flow.set_state_running()
            workspace.configs.save_flow_state(flow)

            # run floorplan
            ieda_fp = IEDAFloorplan(workspace, flow)
            ieda_fp.read_verilog()

            ieda_fp.init_floorplan_by_core_utilization(
                core_site="unithd",
                io_site="unithd",
                corner_site="unithd",
                core_util=0.3,
                x_margin=0,
                y_margin=0,
                xy_ratio=1,
            )
            # ieda_fp.init_floorplan_by_area(die_area="0.0    0.0   149.96   150.128",
            #                               core_area="9.996 10.08 139.964  140.048",
            #                               core_site="unit",
            #                               io_site="unit",
            #                               corner_site="unit")

            ieda_fp.gern_track(
                layer="li1", x_start=240, x_step=480, y_start=185, y_step=370
            )
            ieda_fp.gern_track(
                layer="met1", x_start=185, x_step=370, y_start=185, y_step=370
            )
            ieda_fp.gern_track(
                layer="met2", x_start=240, x_step=480, y_start=240, y_step=480
            )
            ieda_fp.gern_track(
                layer="met3", x_start=370, x_step=740, y_start=370, y_step=740
            )
            ieda_fp.gern_track(
                layer="met4", x_start=480, x_step=960, y_start=480, y_step=960
            )
            ieda_fp.gern_track(
                layer="met5", x_start=185, x_step=3330, y_start=185, y_step=3330
            )

            ieda_fp.add_pdn_io(net_name="VDD", direction="INOUT", is_power=True)
            ieda_fp.add_pdn_io(net_name="VSS", direction="INOUT", is_power=False)

            ieda_fp.global_net_connect(
                net_name="VDD", instance_pin_name="VPWR", is_power=True
            )

            ieda_fp.global_net_connect(
                net_name="VSS", instance_pin_name="VGND", is_power=False
            )

            ieda_fp.auto_place_pins(layer="met5", width=2000, height=2000)

            ieda_fp.tapcell(
                tapcell="sky130_fd_sc_hd__tap_1",
                distance=14,
                endcap="sky130_fd_sc_hd__fill_1",
            )
            
            for clock_net in clock_nets:
                ieda_fp.set_net(net_name=clock_net, net_type="CLOCK")               

            ieda_fp.def_save()
            ieda_fp.verilog_save()

            # save flow state
            flow.set_state_finished()
            workspace.configs.save_flow_state(flow)

        # run eda tool
        from multiprocessing import Process

        p = Process(target=run_floorplan, args=())
        p.start()
        p.join()

    # run each step of physical flow by iEDA
    run_floorplan_sky130(workspace, clock_nets)

    # init iEDA by workspace
    run_ieda = RunIEDA(workspace)

    run_ieda.run_pdn(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.floorplan)
        )
    )

    run_ieda.run_fix_fanout(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.pdn)
        )
    )

    run_ieda.run_placement(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)
        )
    )
    
    return

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

    run_ieda.run_filler(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
        )
    )

    run_ieda.run_drc(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
        )
    )


def generate_vectors(workspace: Workspace, patch_row_step: int, patch_col_step: int, batch_mode : bool = True):
    # step 1 : init by workspace
    data_gen = DataGeneration(workspace)

    # step 2 : generate vectors
    data_gen.generate_vectors(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
        ),
        vectors_dir=workspace.paths_table.ieda_output["vectors"],
        patch_row_step=patch_row_step,
        patch_col_step=patch_col_step,
        batch_mode=batch_mode,
    )
    
def report_summary(workspace, design, design_alias):
    from aieda.report import ReportGenerator
    
    DISPLAY_NAME = {design: design_alias}
    
    report = ReportGenerator(workspace)
    report.generate_report_workspace(display_names_map=DISPLAY_NAME)

def crate_data(design_info):
    # step 1 : create workspace
    workspace = create_workspace_sky130(workspace_dir=design_info["workspace"], 
                                        design= design_info["design"], 
                                        verilog= design_info["verilog"],
                                        sdc=design_info["sdc"],
                                        spef=design_info["spef"])
    # workspace = workspace_create(directory=workspace_dir, design="gcd")

    # step 2 : set paramters
    set_parameters(workspace)

    # # step 3 : run physical design flow
    run_eda_flow(workspace, design_info["clock"])

    # step 4 : generate vectors
    # generate_vectors(workspace, 9, 9)
    
    # # step 5 report summary for workspace
    # report_summary(workspace, design_info["design"], design_info["alias"])
    
if __name__ == "__main__":
    design_list = [
        # {
        #     "design" : "gcd",
        #     "alias" : "gcd",
        #     "workspace" : "/home/huangzengrong/aieda_0.1/aieda_fork/example/sky130_gcd",
        #     "verilog" : "/data2/project_share/dataset_skywater130/gcd/syn_netlist/gcd.v",
        #     "sdc" : "/home/huangzengrong/aieda_0.1/aieda_fork/aieda/third_party/iEDA/scripts/foundry/sky130/sdc/gcd.sdc",
        #     "spef" : "/home/huangzengrong/aieda_0.1/aieda_fork/aieda/third_party/iEDA/scripts/foundry/sky130/spef/gcd.spef",
        #     "clock" :["clk"]
        # },
        {
            "design" : "aes",
            "alias" : "aes",
            "workspace" : "/home/huangzengrong/aieda_0.1/aieda_fork/example/sky130_aes",
            "verilog" : "/data2/project_share/dataset_skywater130/aes/syn_netlist/aes.v",
            "sdc" : "/home/huangzengrong/aieda_0.1/aieda_fork/aieda/third_party/iEDA/scripts/foundry/sky130/sdc/gcd.sdc",
            "spef" : "",
            "clock" :["clk"]
        }
    ]
    
    for design_info in design_list:
        crate_data(design_info)
    
    exit(0)
