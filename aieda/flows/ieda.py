#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : ieda.py
@Author : yell
@Desc : run iEDA flow api
'''
from .base import DbFlow, RunFlowBase

class RunIEDA(RunFlowBase):
    '''run eda backend flow
    '''
    from ..workspace import Workspace
    def __init__(self, workspace : Workspace):  
        """workspace : use workspace to manage all the data, inlcuding configs, 
                       process modes, input and output path, feature data and so on
        """     
        super().__init__(workspace=workspace)
        
        # physical design flow order for iEDA
        self.default_flows = [
            "floorplan",
            "pdn",
            "fixFanout",
            "place",
            "CTS",
            "optDrv",
            "optHold",
            "optSetup",
            "legalization",
            "route",
            "filler"
        ]
            
    def run_flow(self, flow : DbFlow, output_path:str=None):
        """run flow"""            
        def _run_eda(flow : DbFlow):
            """run eda tool""" 
            match flow.step:
                case DbFlow.FlowStep.floorplan:
                    from ..eda import IEDAFloorplan
                    ieda_flow = IEDAFloorplan(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.pdn:
                    from ..eda import IEDAPdn
                    ieda_flow = IEDAPdn(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.fixFanout:
                    from ..eda import IEDANetOpt
                    ieda_flow = IEDANetOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.place:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                
                case DbFlow.FlowStep.cts:
                    from ..eda import IEDACts
                    ieda_flow = IEDACts(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.optDrv:
                    from ..eda import IEDATimingOpt
                    ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.optHold:
                    from ..eda import IEDATimingOpt
                    ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.optSetup:
                    from ..eda import IEDATimingOpt
                    ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.legalization:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.route:
                    from ..eda import IEDARouting
                    ieda_flow = IEDARouting(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                
                case DbFlow.FlowStep.filler:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow.run_flow()
                    
                case DbFlow.FlowStep.vectorization:
                    from ..eda import IEDAVectorization
                    ieda_flow = IEDAVectorization(workspace=self.workspace,
                                              flow=flow,
                                              vectors_dir=output_path)
                    ieda_flow.generate_vectors()
                    
                case DbFlow.FlowStep.drc:
                    from ..eda import IEDADrc
                    ieda_flow = IEDADrc(workspace=self.workspace,
                                        flow=flow,
                                        output_path=output_path)
                    ieda_flow.run_flow()
        
        if flow.is_finish() is True:
            return True
        
        #set state running
        flow.set_state_running()
        self.workspace.configs.save_flow_state(flow)
             
        #run eda tool
        _run_eda(flow)
        
        #save flow state
        is_success = False
        if self.check_flow_state(flow) is True:
            flow.set_state_finished()
            is_success = True
        else:
            flow.set_state_imcomplete()   
            is_success = False 
            
        self.workspace.configs.save_flow_state(flow)
        return is_success
    
    
    def run_ai_flow(self, flow : DbFlow, onnx_path:str=None, normalization_path:str=None):
        """run ai eda tool"""            
        def _run_ai_eda(flow : DbFlow):
            """run eda tool""" 
            match flow.step:
                case DbFlow.FlowStep.ai_place:
                    from ..eda import IEDAPlacement
                    ieda_flow = IEDAPlacement(workspace=self.workspace,
                                              flow=flow)
                    ieda_flow._run_ai_placement(onnx_path=onnx_path, normalization_path=normalization_path)
                
        
        if flow.is_finish() is True:
            return True
        
        #set state running
        flow.set_state_running()
        self.workspace.configs.save_flow_state(flow)
             
        #run eda tool
        _run_ai_eda(flow)
        
        #save flow state
        is_success = False
        if self.check_flow_state(flow) is True:
            flow.set_state_finished()
            is_success = True
        else:
            flow.set_state_imcomplete()   
            is_success = False 
            
        self.workspace.configs.save_flow_state(flow)
        return is_success
    
    def run_fix_fanout(self, 
                      input_def:str, 
                      input_verilog:str=None,
                      output_def:str=None,
                      output_verilog:str=None):   
        """ run fix fanout flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.fixFanout,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_placement(self, 
                      input_def:str, 
                      input_verilog:str=None,
                      output_def:str=None,
                      output_verilog:str=None):   
        """ run placement flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.place,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_ai_placement(self,
                         input_def:str,
                         input_verilog:str=None,
                         output_def:str=None,
                         output_verilog:str=None,
                         onnx_path:str=None,
                         normalization_path:str=None):
        
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.ai_place,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_ai_flow(flow, onnx_path=onnx_path, normalization_path=normalization_path)
            

    def run_CTS(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run CTS flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.cts,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_optimizing_drv(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run timing optimization drv flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.optDrv,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_optimizing_hold(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run timing optimization hold flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.optHold,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_optimizing_setup(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run timing optimization setup flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.cts,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_legalization(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run legalization flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.legalization,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_routing(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run routing flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.route,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_filler(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run instances filling flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.filler,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_flow(flow)
    
    def run_drc(self, 
                input_def:str, 
                input_verilog:str=None,
                drc_path : str = None):   
        """ run instances filling flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        drc_path : output def path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.drc,
                      input_def=input_def,
                      input_verilog=input_verilog)
               
        return self.run_flow(flow, output_path=drc_path)
    
    def run_pdn(self, 
                input_def:str, 
                input_verilog:str=None):   
        """ run instances filling flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        drc_path : output def path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.pdn,
                      input_def=input_def,
                      input_verilog=input_verilog)
               
        return self.run_flow(flow)