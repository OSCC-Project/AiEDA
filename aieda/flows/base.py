#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : flow.py
@Author : yell
@Desc : flow data structure
'''
from enum import Enum

class DbFlow(object): 
    class FlowStep(Enum):
        """PR step
        """
        NoStep = ""
        initFlow = "initFlow"
        initDB = "initDB"
        floorplan = "floorplan"
        pdn = "PDN"
        place = "place"
        globalPlace = "gp"
        detailPlace = "dp"
        cts = "CTS"
        route = "route"
        globalRouting = "gr"
        detailRouting = "dr"
        eco = "eco"
        fixFanout = "fixFanout"
        optDrv = "optDrv"
        optHold = "optHold"
        optSetup = "optSetup"
        legalization = "legalization"
        filler = "filler"
        drc = "drc"
        sta = "sta"
        rcx = "rcx"
        gds = "gds"
        full_flow = 'full_flow',
        vectorization = 'vectorization'
        ai_place = "ai_place"
        
    class FlowState(Enum):
        """flow running state
        """
        Unstart = "unstart"
        Success = "success"
        Ongoing = "ongoing"
        Imcomplete = "incomplete"
        Ignored = "ignored"
    
    def __init__(self, 
                 eda_tool, 
                 step : FlowStep, 
                 state : FlowState=FlowState.Ignored,
                 input_def=None, 
                 input_verilog=None,
                 output_def=None,
                 output_verilog=None):    
        self.eda_tool = eda_tool
        self.step : self.FlowStep = step
        self.state : self.FlowState = state
        
        self.input_def = input_def
        self.input_verilog = input_verilog
        self.output_def = output_def
        self.output_verilog = output_verilog

    def set_state_unstart(self):
        """set_state_unstart"""
        self.state = self.FlowState.Unstart
    
    def set_state_running(self):
        """set_state_running"""
        self.state = self.FlowState.Ongoing
        
    def set_state_finished(self):
        """set_state_finished"""
        self.state = self.FlowState.Success
    
    def set_state_imcomplete(self):
        """set_state_imcomplete"""
        self.state = self.FlowState.Imcomplete
        
    def set_first_flow(self):
        """set_first_flow"""
        self.is_first = True
        
    def is_new(self):
        """get task new"""
        if( self.state != self.FlowState.Unstart):
            return True
        else :
            return False
        
    def is_ongoing(self):
        """if task is ongoing"""
        if( self.state == self.FlowState.Ongoing):
            return True
        else :
            return False
    
    def is_finish(self):
        """if task finished"""
        if( self.state == self.FlowState.Success):
            return True
        else :
            return False
        
    def is_imcomplete(self):
        """is task not finished"""
        if( self.state == self.FlowState.Imcomplete):
            return True
        else :
            return False
        
    def is_first_flow(self):
        """if 1st flow in flowlist"""
        return self.is_first    


class RunFlowBase:
    '''run eda backend flow
    '''
    from ..workspace.workspace import Workspace
    def __init__(self, workspace : Workspace):  
        """workspace : use workspace to manage all the data, inlcuding configs, 
                       process modes, input and output path, feature data and so on
        """     
        self.workspace = workspace
        
        # physical design flow order
        self.default_flows = None
    
    def _get_workspace_flows(self):
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

            match flows[i].step:
                # if step is drc and vectorization, flow do not output def and v, so set output path as preview step   
                case DbFlow.FlowStep.drc | DbFlow.FlowStep.vectorization:
                    flows[i].output_def = flows[i].input_def
                    flows[i].output_verilog = flows[i].input_verilog
                case _:
                    flows[i].output_def = self.workspace.configs.get_output_def(flows[i])
                    flows[i].output_verilog = self.workspace.configs.get_output_verilog(flows[i])
        
        return flows  
    
    def run_flows(self, flows=None, reset=False):
        if flows is None:
            if reset:
                #reset flow state to unstart
                self.workspace.configs.reset_flow_states()
            flows = self._get_workspace_flows()
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
        pass
    
    def check_flow_state(self, flow : DbFlow):
        """check state"""
        #check flow success if output def & verilog file exist
        import os
        
        match flow.step:
            case DbFlow.FlowStep.drc | DbFlow.FlowStep.vectorization:
                return True
            case _:
                # tool step flow, check output def
                output_def = self.workspace.configs.get_output_def(flow=flow, compressed=True)
                output_verilog = self.workspace.configs.get_output_verilog(flow=flow, compressed=True)
                
                return (os.path.exists(output_def) and os.path.exists(output_verilog))
