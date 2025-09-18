#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : data.py
@Author : yell
@Desc : data generation api
"""
from .base import DbFlow, RunFlowBase


class DataGeneration(RunFlowBase):
    """run ieda eval"""

    from ..workspace import Workspace

    def __init__(self, workspace: Workspace):
        """workspace : use workspace to manage all the data, inlcuding configs,
        process modes, input and output path, feature data and so on
        """
        super().__init__(workspace=workspace)

    def generate_feature(
        self,
        step: DbFlow.FlowStep,
        def_path: str = None,
        verilog_path: str = None,
        output_path: str = None,
    ):
        """generate feature summary data
        def_path : def path to read, must be set
        step : specified step
        output_path : output path for summary feature json
        verilog_path : verilog path to read, optional variable for iEDA flow
        """
        flow = DbFlow(
            eda_tool="iEDA",  # use iEDA to extract feature
            step=step,
            output_def=def_path,
            output_verilog=verilog_path,
        )

        self.generate_flow_feature(flow=flow, output_path=output_path)

    def generate_flow_feature(self, flow: DbFlow, output_path: str = None):
        match flow.step:
            case DbFlow.FlowStep.floorplan:
                from ..eda import IEDAFloorplan

                ieda_flow = IEDAFloorplan(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.fixFanout:
                from ..eda import IEDANetOpt

                ieda_flow = IEDANetOpt(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.place:
                from ..eda import IEDAPlacement

                ieda_flow = IEDAPlacement(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)
                ieda_flow.generate_feature_map()

            case DbFlow.FlowStep.cts:
                from ..eda import IEDACts

                ieda_flow = IEDACts(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)
                ieda_flow.generate_feature_map()

            case DbFlow.FlowStep.optDrv:
                from ..eda import IEDATimingOpt

                ieda_flow = IEDATimingOpt(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.optHold:
                from ..eda import IEDATimingOpt

                ieda_flow = IEDATimingOpt(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.optSetup:
                from ..eda import IEDATimingOpt

                ieda_flow = IEDATimingOpt(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.legalization:
                from ..eda import IEDAPlacement

                ieda_flow = IEDAPlacement(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.route:
                from ..eda import IEDARouting

                ieda_flow = IEDARouting(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

            case DbFlow.FlowStep.filler:
                from ..eda import IEDAPlacement

                ieda_flow = IEDAPlacement(workspace=self.workspace, flow=flow)
                ieda_flow.generate_feature_summary(json_path=output_path)

    def generate_drc(
        self, input_def: str = None, input_verilog: str = None, drc_path: str = None
    ):
        from ..eda import IEDADrc

        if input_def is None:
            input_def = self.workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            )

        flow = DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.drc,
            input_def=input_def,
            input_verilog=input_verilog,
        )
        ieda_flow = IEDADrc(workspace=self.workspace, flow=flow, output_path=drc_path)
        ieda_flow.run_flow()

    def generate_vectors(
        self,
        input_def: str = None,
        input_verilog: str = None,
        vectors_dir: str = None,
        patch_row_step: int = 9,
        patch_col_step: int = 9,
        batch_mode: bool = True,
        is_placement_mode: bool = False,
        sta_mode: int = 0,
    ):
        """run data vectorization flow by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        """
        flow = DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.vectorization,
            input_def=input_def,
            input_verilog=input_verilog,
        )

        if input_def is None:
            # use output def of step route as input def
            flow.input_def = self.workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            )

        # create nets, patchs, wire_graph, wire_paths by iEDA
        from ..eda import IEDAVectorization
        
        flow.set_state_running()
        self.workspace.configs.save_flow_state(flow)
        
        ieda_flow = IEDAVectorization(
            workspace=self.workspace, flow=flow, vectors_dir=vectors_dir
        )
        ieda_flow.generate_vectors(patch_row_step, patch_col_step, batch_mode, is_placement_mode, sta_mode)
        
        flow.set_state_finished()
        self.workspace.configs.save_flow_state(flow)

    def vectors_nets_to_def(
        self,
        input_def: str = None,
        input_verilog: str = None,
        output_def: str = None,
        output_verilog: str = None,
        vectors_dir: str = None,
    ):
        """save vectorization nets data to def by iEDA
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : save def path
        output_verilog : save verilog path
        vectors_dir : vector nets directory
        """
        flow = DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.vectorization,
            input_def=input_def,
            input_verilog=input_verilog,
            output_def=output_def,
            output_verilog=output_verilog
        )

        if input_def is None:
            # use output def of step route as input def
            flow.input_def = self.workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            )
            
        if input_verilog is None:
            # use output def of step route as input def
            flow.input_verilog = self.workspace.configs.get_output_verilog(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            )

        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.vectorization)
            )

        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.vectorization)
            )

        # create nets, patchs, wire_graph, wire_paths by iEDA
        from ..eda import IEDAVectorization

        ieda_flow = IEDAVectorization(
            workspace=self.workspace, flow=flow, vectors_dir=vectors_dir
        )
        ieda_flow.vectors_nets_to_def()

    def vectors_nets_patterns_to_def(
        self,
        pattern_path: str,
        input_def: str = None,
        input_verilog: str = None,
        output_def: str = None,
        output_verilog: str = None,
    ):
        """save vectorization nets patterns data to def by iEDA
        pattern_path : pattern json file path
        input_def : input def path, must be set
        input_verilog :input verilog path, optional variable for iEDA flow
        output_def : save def path
        output_verilog : save verilog path
        """
        flow = DbFlow(
            eda_tool="iEDA",
            step=DbFlow.FlowStep.net_pattern,
            input_def=input_def,
            input_verilog=input_verilog,
            output_def=output_def,
            output_verilog=output_verilog
        )

        if input_def is None:
            # use output def of step route as input def
            flow.input_def = self.workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            )
            
        if input_verilog is None:
            # use output def of step route as input def
            flow.input_verilog = self.workspace.configs.get_output_verilog(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            )

        if output_def is None:
            flow.output_def = self.workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.net_pattern)
            )

        if output_verilog is None:
            flow.output_verilog = self.workspace.configs.get_output_verilog(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.net_pattern)
            )

        # create nets, patchs, wire_graph, wire_paths by iEDA
        from ..eda import IEDAVectorization

        ieda_flow = IEDAVectorization(workspace=self.workspace, flow=flow)
        ieda_flow.vectors_nets_patterns_to_def(path=pattern_path)
