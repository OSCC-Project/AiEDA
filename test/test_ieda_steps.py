#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_steps.py
@Author : yell
@Desc : test physical design steps for iEDA
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    Workspace,
    workspace_create,
    RunIEDA,
    DbFlow
)

def run_floorplan_sky130_gcd(workspace : Workspace):
    def run_floorplan():
        from aieda import IEDAFloorplan
        
        flow = DbFlow(eda_tool="iEDA", 
                      step=DbFlow.FlowStep.floorplan,
                      input_def=workspace.configs.paths.def_input_path,
                      input_verilog=workspace.configs.paths.verilog_input_path)
        #set state running
        flow.set_state_running()
        workspace.configs.save_flow_state(flow)
    
        # run floorplan
        ieda_fp = IEDAFloorplan(workspace, flow)
        ieda_fp.read_verilog()
        
        ieda_fp.init_floorplan_by_area(die_area="0.0    0.0   149.96   150.128",
                                      core_area="9.996 10.08 139.964  140.048",
                                      core_site="unit",
                                      io_site="unit",
                                      corner_site="unit")
        
        ieda_fp.gern_track(layer="li1", x_start=240, x_step=480, y_start=185, y_step=370)
        ieda_fp.gern_track(layer="met1", x_start=185, x_step=370, y_start=185, y_step=370)
        ieda_fp.gern_track(layer="met2", x_start=240, x_step=480, y_start=240, y_step=480)
        ieda_fp.gern_track(layer="met3", x_start=370, x_step=740, y_start=370, y_step=740)
        ieda_fp.gern_track(layer="met4", x_start=480, x_step=960, y_start=480, y_step=960)
        ieda_fp.gern_track(layer="met5", x_start=185, x_step=3330, y_start=185, y_step=3330)
        
        ieda_fp.add_pdn_io(net_name="VDD", direction="INOUT", is_power=True)
        ieda_fp.add_pdn_io(net_name="VSS", direction="INOUT", is_power=False)
        
        ieda_fp.global_net_connect(net_name="VDD", instance_pin_name="VPWR", is_power=True)
        ieda_fp.global_net_connect(net_name="VDD", instance_pin_name="VPB", is_power=True)
        ieda_fp.global_net_connect(net_name="VDD", instance_pin_name="vdd", is_power=True)
        ieda_fp.global_net_connect(net_name="VSS", instance_pin_name="VGND", is_power=False)
        ieda_fp.global_net_connect(net_name="VSS", instance_pin_name="VNB", is_power=False)
        ieda_fp.global_net_connect(net_name="VSS", instance_pin_name="VNB", is_power=False)
        
        ieda_fp.auto_place_pins(layer="met5", width=2000, height=2000)
        
        ieda_fp.tapcell(tapcell="sky130_fd_sc_hs__tap_1",
                        distance=14,
                        endcap="sky130_fd_sc_hs__fill_1")
        
        ieda_fp.set_net(net_name="clk", net_type="CLOCK")
        
        # ieda_fp.pnp()
        
        ieda_fp.def_save()
        ieda_fp.verilog_save()
        
        #save flow state
        flow.set_state_finished()
        workspace.configs.save_flow_state(flow)
    
         
    #run eda tool
    from multiprocessing import Process
    p = Process(target=run_floorplan, args=())
    p.start()
    p.join()
    

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data2/huangzengrong/test_aieda/minirv3"
    # workspace = workspace_create(directory=workspace_dir, design="minirv")
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130_5"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : init iEDA by workspace
    run_ieda = RunIEDA(workspace)
    
    # step 3 : run each step of physical flow by iEDA 
    run_floorplan_sky130_gcd(workspace)
    
    run_ieda.run_pdn(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.floorplan)))
    
    run_ieda.run_fix_fanout(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.pdn)))
    # run_ieda.run_fix_fanout(input_def="/home/taosimin/tosujianrong/0816/iPNP_result2.def")
    
    run_ieda.run_placement(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)))
    
    run_ieda.run_CTS(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place)))
    
    run_ieda.run_optimizing_drv(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts)))
    
    run_ieda.run_optimizing_hold(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv)))
    
    run_ieda.run_legalization(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold)))
    
    run_ieda.run_routing(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization)))
    
    run_ieda.run_filler(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)))
    
    run_ieda.run_drc(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)))

    exit(0)

