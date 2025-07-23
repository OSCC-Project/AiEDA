#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : ieda.py
@Author : yell
@Desc : run iEDA flow api
'''
from multiprocessing import Process

from .flow import DbFlow, RunFlowBase

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
            
    def run_flow(self, flow : DbFlow, output_dir:str=None):
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
                    
                case DbFlow.FlowStep.vectorization:
                    from ..eda import IEDAVectorization
                    ieda_flow = IEDAVectorization(workspace=self.workspace,
                                              flow=flow,
                                              vectors_dir=output_dir)
                    ieda_flow.run_vectorization()
        
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
        if self.check_flow_state(flow) is True:
            flow.set_state_finished()
            is_success = True
        else:
            flow.set_state_imcomplete()   
            is_success = False 
            
        self.workspace.configs.save_flow_state(flow)
        return is_success
    
    def run_fixFanout(self, 
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
    
    def run_vectorization(self, 
                input_def:str, 
                input_verilog:str=None,
                vectors_dir:str=None):   
        """ run data vectorization flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.vectorization,
                      input_def=input_def,
                      input_verilog=input_verilog)
        
        if input_def is None:
            # use output def of step route as input def
            flow.input_def = self.workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route))
        
        def vectorization(flow):
            from ..eda import IEDAVectorization
            ieda_flow = IEDAVectorization(workspace=self.workspace,
                                      flow=flow,
                                      vectors_dir=vectors_dir)
            ieda_flow.run_vectorization()
    
        p = Process(target=vectorization, args=(flow,))
        p.start()
        p.join()

class RunEval(RunFlowBase):
    '''run ieda eval
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
            
    
    def run_eval_flow(self, flow : DbFlow):
        match flow.step:
            case DbFlow.FlowStep.floorplan:
                from ..eda import IEDAFloorplan
                ieda_flow = IEDAFloorplan(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_eval()
                
            case DbFlow.FlowStep.fixFanout:
                from ..eda import IEDANetOpt
                ieda_flow = IEDANetOpt(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_eval()
                
            case DbFlow.FlowStep.place:
                from ..eda import IEDAPlacement
                ieda_flow = IEDAPlacement(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_place_eval()
            
            case DbFlow.FlowStep.cts:
                from ..eda import IEDACts
                ieda_flow = IEDACts(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_eval()
                
            case DbFlow.FlowStep.optDrv:
                from ..eda import IEDATimingOpt
                ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_drv_eval()
                
            case DbFlow.FlowStep.optHold:
                from ..eda import IEDATimingOpt
                ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_hold_eval()
                
            case DbFlow.FlowStep.optSetup:
                from ..eda import IEDATimingOpt
                ieda_flow = IEDATimingOpt(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_setup_eval()
                
            case DbFlow.FlowStep.legalization:
                from ..eda import IEDAPlacement
                ieda_flow = IEDAPlacement(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_legalization_eval()
                
            case DbFlow.FlowStep.route:
                from ..eda import IEDARouting
                ieda_flow = IEDARouting(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_eval()
            
            case DbFlow.FlowStep.filler:
                from ..eda import IEDAPlacement
                ieda_flow = IEDAPlacement(workspace=self.workspace,
                                            flow=flow)
                ieda_flow.run_filler_eval()

    def run_floorplan_eval(self, 
                      input_def:str, 
                      input_verilog:str=None,
                      output_def:str=None,
                      output_verilog:str=None):   
        """ run floorplan eval by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : output def path, optional variable, if not set, use default path in workspace
        output_verilog : output verilog path, optional variable, if not set, use default path in workspace
        """
        flow = DbFlow(eda_tool="iEDA",
                      step=DbFlow.FlowStep.floorplan,
                      input_def=input_def,
                      input_verilog=input_verilog,
                      output_def=output_def,
                      output_verilog=output_verilog)
        
        #check flow path, if None, set to default path in workspace  
        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(flow)
        
        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(flow)
        
        return self.run_eval_flow(flow)

    def run_fixFanout_eval(self, 
                      input_def:str, 
                      input_verilog:str=None,
                      output_def:str=None,
                      output_verilog:str=None):   
        """ run fix fanout eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_placement_eval(self, 
                      input_def:str, 
                      input_verilog:str=None,
                      output_def:str=None,
                      output_verilog:str=None):   
        """ run placement eval by iEDA
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
        
        return self.run_eval_flow(flow)

    def run_CTS_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run CTS eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_optimizing_drv_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run timing optimization drv eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_optimizing_hold_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run timing optimization hold eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_optimizing_setup_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run timing optimization setup eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_legalization_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run legalization eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_routing_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run routing eval by iEDA
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
        
        return self.run_eval_flow(flow)
    
    def run_filler_eval(self, 
                input_def:str, 
                input_verilog:str=None,
                output_def:str=None,
                output_verilog:str=None):   
        """ run instances filling eval by iEDA
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
        
        return self.run_eval_flow(flow)
