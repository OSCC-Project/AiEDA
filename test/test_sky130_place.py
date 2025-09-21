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
import json
import argparse
import re
from datetime import datetime

os.environ["iEDA"] = "ON"

from aieda.workspace import Workspace, workspace_create
from aieda.flows import DbFlow, RunIEDA, DataGeneration
from aieda.data.database import EDAParameters
from aieda.analysis import CellTypeAnalyzer, CoreUsageAnalyzer, PinDistributionAnalyzer, ResultStatisAnalyzer
from aieda.analysis import WireDistributionAnalyzer, MetricsCorrelationAnalyzer
from aieda.analysis import DelayAnalyzer, StageAnalyzer
from aieda.analysis import WireDensityAnalyzer, FeatureCorrelationAnalyzer, MapAnalyzer


def parse_top_module_from_tcl(design_name: str):
    try:
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        tcl_path = os.path.join(current_dir, "script", "generated", f"{design_name}.tcl")
        if not os.path.exists(tcl_path):
            return None
        patt = re.compile(r'^\s*set\s+top_module\s+([A-Za-z_][A-Za-z0-9_$]*)\s*$', re.IGNORECASE)
        with open(tcl_path, 'r') as f:
            for line in f:
                m = patt.match(line)
                if m:
                    return m.group(1)
    except Exception:
        return None
    return None



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


def run_eda_flow(workspace: Workspace, clock_nets, top_module=None):
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
            ieda_fp.read_verilog(top_module=top_module or "")

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
                net_name="VDD", instance_pin_name="VPB", is_power=True
            )
            ieda_fp.global_net_connect(
                net_name="VDD", instance_pin_name="vdd", is_power=True
            )
            ieda_fp.global_net_connect(
                net_name="VSS", instance_pin_name="VGND", is_power=False
            )
            ieda_fp.global_net_connect(
                net_name="VSS", instance_pin_name="VNB", is_power=False
            )
            ieda_fp.global_net_connect(
                net_name="VSS", instance_pin_name="VNB", is_power=False
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
    try:
        # step 1 : create workspace
        workspace = create_workspace_sky130(workspace_dir=design_info["workspace"],
                                            design= design_info["design"],
                                            verilog= design_info["verilog"],
                                            sdc=design_info["sdc"],
                                            spef=design_info["spef"])

        # step 2 : set paramters
        set_parameters(workspace)

        # # step 3 : run physical design flow
        run_eda_flow(workspace, design_info["clock"], top_module=design_info.get("top_module"))

        # 刷新一次配置，确保读取最新的 flow.json
        workspace.configs.update()

        # 汇总运行结果
        summary = summarize_workspace(workspace)
        summary.update({
            "design": design_info["design"],
            "alias": design_info["alias"],
        })
        return summary
    except Exception as e:
        # 兜底：尽可能返回可定位信息
        result = {
            "design": design_info.get("design", ""),
            "alias": design_info.get("alias", ""),
            "workspace": os.path.join(design_info.get("workspace",""), design_info.get("design","")),
            "status": "failed",
            "error": str(e),
        }
        return result

def summarize_workspace(workspace: Workspace, required_steps=("floorplan", "fixFanout", "place")):
    flows = workspace.configs.flows
    step_states = {f.step.value: f.state.value for f in flows if f.eda_tool == "iEDA"}

    # 判定整体是否成功（以必需步骤全部 success 为准）
    status = "success" if all(step_states.get(s) == "success" for s in required_steps) else "failed"

    # 找最后一个成功的步骤
    ordered_steps = [
        "floorplan", "PDN", "fixFanout", "place", "CTS", "optDrv", "optHold",
        "optSetup", "legalization", "route", "drc", "vectorization", "filler"
    ]
    last_ok = None
    for s in ordered_steps:
        if step_states.get(s) == "success":
            last_ok = s

    # 关键产物路径（以 place 步骤为例）
    place_def = workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place))
    place_v = workspace.configs.get_output_verilog(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place))

    return {
        "workspace": workspace.directory,
        "flow_json": workspace.paths_table.flow,
        "log": getattr(workspace.paths_table, "log", ""),
        "step_states": step_states,
        "last_successful_step": last_ok,
        "status": status,
        "artifacts": {
            "place_def": place_def,
            "place_v": place_v,
        }
    }


def get_target_workspace_dir(workspace_root: str, design: str) -> str:
    base = os.path.basename(os.path.normpath(workspace_root))
    return workspace_root if base == design else os.path.join(workspace_root, design)


def is_first_class_floorplan_unfinished(workspace_root: str, design: str) -> bool:
    ws = get_target_workspace_dir(workspace_root, design)
    flow_path = os.path.join(ws, "config", "flow.json")
    if not os.path.exists(flow_path):
        return False  # 未运行或无数据，避免误判
    try:
        with open(flow_path, "r") as f:
            data = json.load(f)
        for e in data.get("flow", []):
            if e.get("step") == "floorplan":
                return e.get("state") != "success"
    except Exception:
        return False
    return False


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(description="Run iEDA flow for designs from a JSON list")
    default_json = os.path.join(os.path.dirname(__file__), "script", "design_list.json")
    parser.add_argument("--design-list", "-l", type=str, default=default_json, help="Path to design_list.json")
    parser.add_argument("--summary-out", "-o", type=str, default=None, help="Optional path to write batch summary JSON")
    parser.add_argument("--first-class-only", action="store_true", help="Only run designs with floorplan not success (Class A)")
    parser.add_argument("--classify-out", type=str, default=None, help="Write Class-A (floorplan unfinished) design list JSON")
    args = parser.parse_args()

    with open(args.design_list, "r") as f:
        raw_list = json.load(f)

    design_list = []
    for item in raw_list:
        top_mod = parse_top_module_from_tcl(item["design"])  # 从生成的 TCL 解析 top_module（若无则为 None）
        design_list.append({
            "design": item["design"],
            "alias": item.get("alias", item["design"]),
            "workspace": item["workspace"],
            "verilog": item["verilog"],
            "sdc": item["sdc"],
            "spef": item.get("spef", ""),
            "clock": item.get("clk_port_name", []),
            "top_module": top_mod,
        })


    # 可选：筛选“第一类”（floorplan 未成功）并/或导出分类结果
    if args.first_class_only or args.classify_out:
        class_a = [d for d in design_list if is_first_class_floorplan_unfinished(d["workspace"], d["design"])]
        if args.classify_out:
            os.makedirs(os.path.dirname(args.classify_out), exist_ok=True)
            with open(args.classify_out, "w") as f:
                json.dump({
                    "class": "A",
                    "criteria": "floorplan state != success",
                    "count": len(class_a),
                    "designs": [
                        {"design": d["design"], "workspace": get_target_workspace_dir(d["workspace"], d["design"]), "top_module": d.get("top_module")}
                        for d in class_a
                    ]
                }, f, indent=2)
            print("Class-A list written to {} ({} designs)".format(args.classify_out, len(class_a)))
        if args.first_class_only:
            print("Filtering to Class-A designs only ({} of {})".format(len(class_a), len(design_list)))
            design_list = class_a

    results = []
    for design_info in design_list:
        res = crate_data(design_info)
        results.append(res)
        print("[{}] {} last_ok={} workspace={}".format(
            res.get("status", "failed"), res.get("design", ""), res.get("last_successful_step", None), res.get("workspace", "")
        ))

    # 写出批量汇总
    if args.summary_out is None:
        summary_dir = os.path.join(os.path.dirname(__file__), "output", "_summary")
        os.makedirs(summary_dir, exist_ok=True)
        summary_path = os.path.join(summary_dir, "batch_summary_{}.json".format(datetime.now().strftime("%Y%m%d_%H%M%S")))
    else:
        summary_path = args.summary_out
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)

    with open(summary_path, "w") as f:
        json.dump({"results": results}, f, indent=2)

    print("Summary written to {}".format(summary_path))
    exit(0)
