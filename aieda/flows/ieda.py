#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : ieda.py
@Author : yell
@Desc : run iEDA flow api
'''
import os
from multiprocessing import Process
from ..workspace import Workspace
from .flow import DbFlow

class RunIEDA:
    '''run eda backend flow
    '''
    
    def __init__(self, workspace : Workspace):        
        self.workspace = workspace
        
        self.default_flows = {
            "floorplan" : None,
            "fixFanout" : None,
            "place" : None,
            "CTS" : None,
            "optDrv" : None,
            "optHold" : None,
            "legalization" : None,
            "route" : None,
            "filler" : None,
        }
    
    def __get_workspace_flows__(self):
        flows = self.workspace.configs.flows
        for i in range(0, len(flows)):
            if i == 0:
                # using data in path.json 
                if flows[i].input_def is None:
                    flows[i].input_def = self.workspace.configs.paths.def_input_path
                if flows[i].input_verilog is None:
                    flows[i].input_verilog = self.workspace.configs.paths.verilog_input_path
            else:
                #use pre flow output
                if flows[i].input_def is None:
                    flows[i].input_def = flows[i-1].output_def
                if flows[i].input_verilog is None:
                    flows[i].input_verilog = flows[i-1].output_verilog
            
            flows[i].output_def = self.workspace.configs.get_output_def(flows[i])
            flows[i].output_verilog = self.workspace.configs.get_output_verilog(flows[i])
        
        return flows
    
    def run_flows(self, flows=None, reset=False):
        if flows is None:
            if reset:
                #reset flow state to unstart
                self.workspace.configs.reset_flow_states()
            flows = self.__get_workspace_flows__()
        else:
            if reset:
                for flow in flows:
                    flow.set_state_unstart()
        
        for flow in flows:
            self.run_flow(flow)
            
        #check all flow success  
        for flow in flows:
            if not flow.is_finish():
                return False
        
        return True
            
    def run_flow(self, flow : DbFlow):
        """run flow"""            
        def __run_eda__(flow : DbFlow):
            """run eda tool""" 
            match flow.step:
                case DbFlow.FlowStep.floorplan:
                    from ..eda import IEDAFloorplan
                    ieda_flow = IEDAFloorplan(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_floorplan()
                    
                case DbFlow.FlowStep.fixFanout:
                    from ..eda import IEDANetOpt
                    ieda_flow = IEDANetOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_fix_fanout()
                    
                case DbFlow.FlowStep.place:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_placement()
                
                case DbFlow.FlowStep.cts:
                    from ..eda import IEDACts
                    ieda_flow = IEDACts(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_cts()
                    
                case DbFlow.FlowStep.optDrv:
                    from ..eda import IEDATimingOpt
                    ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_to_drv()
                    
                case DbFlow.FlowStep.optHold:
                    from ..eda import IEDATimingOpt
                    ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_to_hold()
                    
                case DbFlow.FlowStep.optSetup:
                    from ..eda import IEDATimingOpt
                    ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_to_setup()
                    
                case DbFlow.FlowStep.legalization:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_legalization()
                    
                case DbFlow.FlowStep.route:
                    from ..eda import IEDARouting
                    ieda_flow = IEDARouting(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_routing()
                
                case DbFlow.FlowStep.filler:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_filler()
        
        def check_flow_state( flow : DbFlow):
            """check state"""
            #check flow success if output def & verilog file exist
            output_def = self.workspace.configs.get_output_def(flow=flow, compressed=True)
            output_verilog = self.workspace.configs.get_output_verilog(flow=flow, compressed=True)
            
            return (os.path.exists(output_def) and os.path.exists(output_verilog))
        
        if flow.is_finish() is True:
            return True
        
        #set state running
        flow.set_state_running()
        self.workspace.configs.save_flow_state(flow)
             
        #run eda tool
        p = Process(target=__run_eda__, args=(flow,))
        p.start()
        p.join()
        
        #save flow state
        is_success = False
        if check_flow_state(flow) is True:
            flow.set_state_finished()
            is_success = True
        else:
            flow.set_state_imcomplete()   
            is_success = False 
            
        self.workspace.configs.save_flow_state(flow)
        return is_success
    
    def run_fixFanout(self, input_def, 
                      input_verilog=None,
                      output_def=None,
                      output_verilog=None):
        if output_def is None:
            output_def = self.workspace
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.fixFanout,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        return self.run_flow(flow)