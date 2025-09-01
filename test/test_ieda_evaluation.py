#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_ieda_evaluation.py
@Author : yhqiu
@Desc : test ieda evaluation API
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################

######################################################################################
import os

os.environ["iEDA"] = "ON"
######################################################################################


from aieda import workspace_create, DbFlow, IEDAEvaluation

if __name__ == "__main__":
    # step 1 : create workspace
    import os

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)

    workspace = workspace_create(directory=workspace_dir, design="gcd")

    # step 2: init evaluation by workspace
    run_eval = IEDAEvaluation(
        workspace=workspace, flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place)
    )

    # step 3: run iEDA wirelength evaluation
    hpwl = run_eval.total_wirelength_hpwl()
    print("Total HPWL: {}".format(hpwl))

    stwl = run_eval.total_wirelength_stwl()
    print("Total STWL: {}".format(stwl))

    grwl = run_eval.total_wirelength_grwl()
    print("Total GRWL: {}".format(grwl))

    # step 4: run iEDA density evaluation
    max_density, avg_density = run_eval.cell_density(bin_cnt_x=256, bin_cnt_y=256)
    print("Max cell density: {}, Avg cell density: {}".format(max_density, avg_density))

    max_density, avg_density = run_eval.pin_density(bin_cnt_x=256, bin_cnt_y=256)
    print("Max pin density: {}, Avg pin density: {}".format(max_density, avg_density))

    max_density, avg_density = run_eval.net_density(bin_cnt_x=256, bin_cnt_y=256)
    print("Max net density: {}, Avg net density: {}".format(max_density, avg_density))

    # step 5: run iEDA congestion evaluation
    max_congestion, total_congestion = run_eval.rudy_congestion(
        bin_cnt_x=256, bin_cnt_y=256
    )
    print(
        "Max RUDY congestion: {}, Total RUDY congestion: {}".format(
            max_congestion, total_congestion
        )
    )

    max_congestion, total_congestion = run_eval.lut_rudy_congestion(
        bin_cnt_x=256, bin_cnt_y=256
    )
    print(
        "Max LUT RUDY congestion: {}, Total LUT RUDY congestion: {}".format(
            max_congestion, total_congestion
        )
    )

    max_congestion, total_congestion = run_eval.egr_congestion()
    print(
        "Max EGR congestion: {}, Total EGR congestion: {}".format(
            max_congestion, total_congestion
        )
    )

    # step 6: run iEDA timing and power evaluation
    hpwl_result = run_eval.timing_power_hpwl()
    for clock_timing in hpwl_result["clock_timings"]:
        print(f"Clock Name: {clock_timing['clock_name']}")
        print(f"  Setup WNS: {clock_timing['setup_wns']}")
        print(f"  Setup TNS: {clock_timing['setup_tns']}")
        print(f"  Hold WNS: {clock_timing['hold_wns']}")
        print(f"  Hold TNS: {clock_timing['hold_tns']}")
        print(f"  Suggested Frequency: {clock_timing['suggest_freq']}")
    print(f"Static Power: {hpwl_result['static_power']}")
    print(f"Dynamic Power: {hpwl_result['dynamic_power']}")

    stwl_result = run_eval.timing_power_stwl()
    for clock_timing in stwl_result["clock_timings"]:
        print(f"Clock Name: {clock_timing['clock_name']}")
        print(f"  Setup WNS: {clock_timing['setup_wns']}")
        print(f"  Setup TNS: {clock_timing['setup_tns']}")
        print(f"  Hold WNS: {clock_timing['hold_wns']}")
        print(f"  Hold TNS: {clock_timing['hold_tns']}")
        print(f"  Suggested Frequency: {clock_timing['suggest_freq']}")
    print(f"Static Power: {stwl_result['static_power']}")
    print(f"Dynamic Power: {stwl_result['dynamic_power']}")

    egr_result = run_eval.timing_power_egr()
    for clock_timing in egr_result["clock_timings"]:
        print(f"Clock Name: {clock_timing['clock_name']}")
        print(f"  Setup WNS: {clock_timing['setup_wns']}")
        print(f"  Setup TNS: {clock_timing['setup_tns']}")
        print(f"  Hold WNS: {clock_timing['hold_wns']}")
        print(f"  Hold TNS: {clock_timing['hold_tns']}")
        print(f"  Suggested Frequency: {clock_timing['suggest_freq']}")
    print(f"Static Power: {egr_result['static_power']}")
    print(f"Dynamic Power: {egr_result['dynamic_power']}")

    exit(0)
