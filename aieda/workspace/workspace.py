#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : workspace.py
@Author : yell
@Desc : workspace definition.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..utility import create_logger

if TYPE_CHECKING:
    from ..data.database.parameters import EDAParameters


def workspace_create(directory: str, design: str, flow_list=None):
    ws = Workspace(directory=directory, design=design)

    ws.create_workspace(flow_list=flow_list)

    return ws


class Workspace:
    def __init__(self, directory: str, design: str=None):
        self.directory = directory       
        self.design = self.init_design(design)
        self.paths_table = self.PathsTable(directory, design)
        if os.path.exists(self.directory):
            self.logger = create_logger(name=design, log_file=self.paths_table.log)
            self.configs = self.Configs(
                paths_table=self.paths_table, logger=self.logger
            )
        else:
            self.logger = None
            self.configs = None
            
    def init_design(self, design):
        if design is None:
            from aieda.workspace.config.json_workspace import WorkspaceParser
            path = "{}/config/workspace.json".format(self.directory)
            parser = WorkspaceParser(path)
            if parser.read():
                design = parser.get_db().design
        return design

    def create_workspace(self, flow_list=None):
        """check if workspace exist, if not exist, create workspace"""
        #########################################################################
        # step 1, ensure workspace dir exist
        #########################################################################
        if os.path.exists(self.directory):
            self.logger.info("the workspace is existed: {}".format(self.directory))
            return True

        os.makedirs(self.directory)

        #########################################################################
        # step 2, create dir in workspace
        #########################################################################
        for dir in self.paths_table.workspace_top:
            os.makedirs(dir)

        for dir in self.paths_table.ieda_output_dirs:
            os.makedirs(dir)

        # create log and update logger and init configs
        os.makedirs(self.paths_table.log_dir)
        with open(self.paths_table.log, "a") as file:
            file.write("\n start AiEDA logging for design {} ...".format(self.design))
        self.logger = create_logger(name=self.design, log_file=self.paths_table.log)
        self.configs = self.Configs(paths_table=self.paths_table, logger=self.logger)
        self.configs.flows = flow_list

        #########################################################################
        # step 3, create flow.json
        #########################################################################
        from .config import FlowParser

        parser = FlowParser(self.paths_table.flow, self.logger)
        parser.create_json(self.configs.flows)

        #########################################################################
        # step 4, create path.json
        #########################################################################
        from .config import PathParser

        parser = PathParser(self.paths_table.path, self.logger)
        parser.create_json(self.configs.paths)

        #########################################################################
        # step 5, create workspace.json
        #########################################################################
        from .config import WorkspaceParser

        if self.configs.workspace.design is None:
            self.configs.workspace.design = self.design

        parser = WorkspaceParser(self.paths_table.workspace, self.logger)
        parser.create_json(self.configs.workspace)

        #########################################################################
        # step 6, create parameter.json
        #########################################################################
        from .config import ParametersParser

        parser = ParametersParser(self.paths_table.parameters, self.logger)
        parser.create_json(self.configs.parameters)

        #########################################################################
        # step 7, create iEDA_config
        #########################################################################
        # create dir
        os.makedirs(self.paths_table.ieda_config["config"])

        # create flow_config.json
        from .config import ConfigIEDAFlowParser

        parser = ConfigIEDAFlowParser(
            self.paths_table.ieda_config["initFlow"], self.logger
        )
        parser.create_json_default()

        # create db_default_config.json
        from .config import ConfigIEDADbParser

        parser = ConfigIEDADbParser(self.paths_table.ieda_config["initDB"], self.logger)
        parser.create_json_default(self.paths_table)

        # create fp_default_config.json
        from .config import ConfigIEDAFloorplanParser

        parser = ConfigIEDAFloorplanParser(
            self.paths_table.ieda_config["floorplan"], self.logger
        )
        parser.create_json_default()

        # create pnp_default_config.json
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(self.paths_table.ieda_config["pnp"], self.logger)
        parser.create_json_default(self.paths_table)

        # create no_default_config_fixfanout.json
        from .config import ConfigIEDAFixFanoutParser

        parser = ConfigIEDAFixFanoutParser(
            self.paths_table.ieda_config["fixFanout"], self.logger
        )
        parser.create_json_default(self.paths_table)

        # create pl_default_config.json
        from .config import ConfigIEDAPlacementParser

        parser = ConfigIEDAPlacementParser(
            self.paths_table.ieda_config["place"], self.logger
        )
        parser.create_json_default()

        # create cts_default_config.json
        from .config import ConfigIEDACTSParser

        parser = ConfigIEDACTSParser(self.paths_table.ieda_config["CTS"], self.logger)
        parser.create_json_default()

        # create to_default_config_drv.json
        from .config import ConfigIEDATimingOptParser

        parser = ConfigIEDATimingOptParser(
            self.paths_table.ieda_config["optDrv"], self.logger
        )
        parser.create_json_default(self.paths_table, "optimize_drv")

        # create to_default_config_hold.json
        from .config import ConfigIEDATimingOptParser

        parser = ConfigIEDATimingOptParser(
            self.paths_table.ieda_config["optHold"], self.logger
        )
        parser.create_json_default(self.paths_table, "optimize_hold")

        # create to_default_config_setup.json
        from .config import ConfigIEDATimingOptParser

        parser = ConfigIEDATimingOptParser(
            self.paths_table.ieda_config["optSetup"], self.logger
        )
        parser.create_json_default(self.paths_table, "optimize_setup")

        # create rt_default_config.json
        from .config import ConfigIEDARouterParser

        parser = ConfigIEDARouterParser(
            self.paths_table.ieda_config["route"], self.logger
        )
        parser.create_json_default(self.paths_table)

        # create drc_default_config.json
        from .config import ConfigIEDADrcParser

        parser = ConfigIEDADrcParser(self.paths_table.ieda_config["drc"], self.logger)
        parser.create_json_default()

        #########################################################################
        # step 8 : update config
        #########################################################################
        self.configs.update()

        self.logger.info("create workspace success : {}".format(self.directory))

    def set_tech_lef(self, tech_lef: str):
        # update data
        self.configs.paths.tech_lef_path = tech_lef

        # update tech lef in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_tech_lef(tech_lef)

        # update tech lef in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_tech_lef(tech_lef=tech_lef)

    def set_lefs(self, lefs: list[str]):
        # update data
        self.configs.paths.lef_paths = lefs

        # update lefs in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_lefs(lefs)

        # update lefs in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_lefs(lefs=lefs)

    def set_libs(self, libs: list[str]):
        # update data
        self.configs.paths.lib_paths = libs

        # update libs in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_libs(libs)

        # update libs in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_libs(libs=libs)

    def set_max_libs(self, libs: list[str]):
        # update data
        self.configs.paths.max_lib_paths = libs

        # update libs in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_max_libs(libs)

    def set_min_libs(self, libs: list[str]):
        # update data
        self.configs.paths.min_lib_paths = libs

        # update libs in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_min_libs(libs)

    def set_sdc(self, sdc_path: str):
        # update data
        self.configs.paths.sdc_path = sdc_path

        # update sdc in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_sdc(sdc_path)

        # update sdc in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_sdc(sdc_path=sdc_path)

    def set_spef(self, spef_path: str):
        # update data
        self.configs.paths.spef_path = spef_path

        # update sdc in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_spef(spef_path)

        # update sdc in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_spef(spef_path=spef_path)

    def set_rcworst(self, rcworst_path: str):
        # update data
        self.configs.paths.rcworst_path = rcworst_path

        # update sdc in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_rcworst(rcworst_path)

    def set_rcbest(self, rcbest_path: str):
        # update data
        self.configs.paths.rcbest_path = rcbest_path

        # update sdc in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_rcbest(rcbest_path)

    def set_def_input(self, def_input: str):
        # update data
        self.configs.paths.def_input_path = def_input

        # update def input in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_def_input(def_input)

        # update def input in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_def_input(def_path=def_input)

    def set_verilog_input(self, verilog_input: str):
        # update data
        self.configs.paths.verilog_input_path = verilog_input

        # update verilog input in path.json
        from .config import PathParser

        json_path = self.paths_table.path
        parser = PathParser(json_path, self.logger)
        parser.set_verilog_input(verilog_input)

        # update verilog input in iEDA_config/db_default_config.json
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_verilog_input(verilog_path=verilog_input)

    def set_flows(self, flows):
        # update data
        self.configs.flows = flows

        # update flows in flow.json
        from .config import FlowParser

        parser = FlowParser(self.paths_table.flow, self.logger)
        parser.create_json(self.configs.flows)

    def set_process_node(self, process_node: str):
        # update data
        self.configs.workspace.process_node = process_node

        # udpate process_node in workspace.json
        from .config import WorkspaceParser

        parser = WorkspaceParser(self.paths_table.workspace, self.logger)
        parser.set_process_node(process_node)

    def set_design(self, design: str):
        # update data
        self.design = design
        self.configs.workspace.design = design

        # udpate design in workspace.json
        from .config import WorkspaceParser

        parser = WorkspaceParser(self.paths_table.workspace, self.logger)
        parser.set_design(design)

    def set_version(self, version: str):
        # update data
        self.configs.workspace.version = version

        # udpate version in workspace.json
        from .config import WorkspaceParser

        parser = WorkspaceParser(self.paths_table.workspace, self.logger)
        parser.set_version(version)

    def set_project(self, project: str):
        # update data
        self.configs.workspace.project = project

        # udpate project in workspace.json
        from .config import WorkspaceParser

        parser = WorkspaceParser(self.paths_table.workspace, self.logger)
        parser.set_project(project)

    def set_task(self, task: str):
        # update data
        self.configs.workspace.task = task

        # udpate project in workspace.json
        from .config import WorkspaceParser

        parser = WorkspaceParser(self.paths_table.workspace, self.logger)
        parser.set_task(task)

    def set_first_routing_layer(self, layer: str):
        from .config import ConfigIEDADbParser

        json_path = self.paths_table.ieda_config["initDB"]
        parser = ConfigIEDADbParser(json_path, self.logger)
        parser.set_first_routing_layer(layer=layer)

    def set_ieda_fixfanout_buffer(self, buffer: str):
        from .config import ConfigIEDAFixFanoutParser

        parser = ConfigIEDAFixFanoutParser(
            self.paths_table.ieda_config["fixFanout"], self.logger
        )
        parser.set_insert_buffer(buffer)
        
    def set_ieda_pnp_grid_power_layers(self, power_layers: list[str]):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_pnp_grid_power_layers(power_layers)
        
    def set_ieda_pnp_grid_follow_pin_layers(self, follow_pin_layers: list[str]):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_pnp_grid_follow_pin_layers(follow_pin_layers)
        
    def set_ieda_pnp_grid_follow_pin_width(self, follow_pin_width):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_pnp_grid_follow_pin_width(follow_pin_width)
        
    def set_ieda_pnp_grid_power_port_layer(self, power_port_layer: str):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_pnp_grid_power_port_layer(power_port_layer)
        
    def set_ieda_pnp_simulated_annealing_modifiable_layer_min(self, modifiable_layer_min: str):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_pnp_simulated_annealing_modifiable_layer_min(modifiable_layer_min)
        
    def set_ieda_pnp_simulated_annealing_modifiable_layer_max(self, modifiable_layer_max: str):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_pnp_simulated_annealing_modifiable_layer_max(modifiable_layer_max)
        
    def set_ieda_templates_horizontal_width(self, width):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_horizontal_width(width)
        
    def set_ieda_templates_horizontal_pg_offset(self, pg_offset):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_horizontal_pg_offset(pg_offset)
        
    def set_ieda_templates_horizontal_space(self, space):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_horizontal_space(space)
        
    def set_ieda_templates_horizontal_offset(self, offset):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_horizontal_offset(offset)
        
    def set_ieda_templates_vertical_width(self, width):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_vertical_width(width)
        
    def set_ieda_templates_vertical_pg_offset(self, pg_offset):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_vertical_pg_offset(pg_offset)
        
    def set_ieda_templates_vertical_space(self, space):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_vertical_space(space)
        
    def set_ieda_templates_vertical_offset(self, offset):
        from .config import ConfigIEDAPNPParser

        parser = ConfigIEDAPNPParser(
            self.paths_table.ieda_config["pnp"], self.logger
        )
        parser.set_templates_vertical_offset(offset)
        
    def set_ieda_cts_buffers(self, buffers: list[str]):
        from .config import ConfigIEDACTSParser

        parser = ConfigIEDACTSParser(self.paths_table.ieda_config["CTS"], self.logger)
        parser.set_buffer_type(buffers)

    def set_ieda_cts_root_buffer(self, buffer: str):
        from .config import ConfigIEDACTSParser

        parser = ConfigIEDACTSParser(self.paths_table.ieda_config["CTS"], self.logger)
        parser.set_root_buffer_type(buffer)

    def set_ieda_placement_buffers(self, buffers: list[str]):
        from .config import ConfigIEDAPlacementParser

        parser = ConfigIEDAPlacementParser(
            self.paths_table.ieda_config["place"], self.logger
        )
        parser.set_buffer_type(buffers)

    def set_ieda_filler_cells_for_first_iteration(self, cells: list[str]):
        from .config import ConfigIEDAPlacementParser

        parser = ConfigIEDAPlacementParser(
            self.paths_table.ieda_config["filler"], self.logger
        )
        parser.set_filler_first_iter(cells)

    def set_ieda_filler_cells_for_second_iteration(self, cells: list[str]):
        from .config import ConfigIEDAPlacementParser

        parser = ConfigIEDAPlacementParser(
            self.paths_table.ieda_config["filler"], self.logger
        )
        parser.set_filler_second_iter(cells)

    def set_ieda_optdrv_buffers(self, buffers: list[str]):
        from .config import ConfigIEDATimingOptParser

        parser = ConfigIEDATimingOptParser(
            self.paths_table.ieda_config["optDrv"], self.logger
        )
        parser.set_drv_insert_buffers(buffers)

    def set_ieda_opthold_buffers(self, buffers: list[str]):
        from .config import ConfigIEDATimingOptParser

        parser = ConfigIEDATimingOptParser(
            self.paths_table.ieda_config["optHold"], self.logger
        )
        parser.set_hold_insert_buffers(buffers)

    def set_ieda_optsetup_buffers(self, buffers: list[str]):
        from .config import ConfigIEDATimingOptParser

        parser = ConfigIEDATimingOptParser(
            self.paths_table.ieda_config["optSetup"], self.logger
        )
        parser.set_setup_insert_buffers(buffers)

    def set_ieda_router_layer(self, bottom_layer: str, top_layer: str):
        from .config import ConfigIEDARouterParser

        parser = ConfigIEDARouterParser(
            self.paths_table.ieda_config["route"], self.logger
        )
        parser.set_bottom_routing_layer(bottom_layer)
        parser.set_top_routing_layer(top_layer)

    def set_ieda_router_timing(self, enable_timing: bool):
        from .config import ConfigIEDARouterParser

        parser = ConfigIEDARouterParser(
            self.paths_table.ieda_config["route"], self.logger
        )
        parser.set_enable_timing(enable_timing)

    def update_parameters(self, parameters: EDAParameters):
        """update parameters and save to parameter.json"""
        # update data in configs
        self.configs.parameters = parameters
        # update parameter.json
        from .config import ParametersParser

        parser = ParametersParser(self.paths_table.parameters, self.logger)
        parser.create_json(parameters)

        # update iEDA_config/pl_default_config.json
        from .config import ConfigIEDAPlacementParser

        parser = ConfigIEDAPlacementParser(
            self.paths_table.ieda_config["place"], self.logger
        )
        parser.set_target_density(parameters.placement_target_density)
        parser.set_max_phi_coef(parameters.placement_max_phi_coef)
        parser.set_init_wirelength_coef(parameters.placement_init_wirelength_coef)
        parser.set_min_wirelength_force_bar(
            parameters.placement_min_wirelength_force_bar
        )
        parser.set_max_backtrack(parameters.placement_max_backtrack)
        parser.set_init_density_penalty(parameters.placement_init_density_penalty)
        parser.set_target_overflow(parameters.placement_target_overflow)
        parser.set_initial_prev_coordi_update_coef(parameters.placement_initial_prev_coordi_update_coef)
        parser.set_min_precondition(parameters.placement_min_precondition)
        parser.set_min_phi_coef(parameters.placement_min_phi_coef)

        # update iEDA_config/cts_default_config.json
        from .config import ConfigIEDACTSParser

        parser = ConfigIEDACTSParser(self.paths_table.ieda_config["CTS"], self.logger)
        parser.set_skew_bound(parameters.cts_skew_bound)
        parser.set_max_buf_tran(parameters.cts_max_buf_tran)
        parser.set_max_sink_tran(parameters.cts_max_sink_tran)
        parser.set_max_cap(parameters.cts_max_cap)
        parser.set_max_fanout(parameters.cts_max_fanout)
        parser.set_cluster_size(parameters.cts_cluster_size)

    def load_parameters(self, parameters_json: str):
        """load parameters data from json"""
        from .config import ParametersParser

        parser = ParametersParser(parameters_json, self.logger)
        self.configs.parameters = parser.get_db()

    def print_paramters(self):
        from .config import ParametersParser

        parser = ParametersParser(self.paths_table.parameters, self.logger)
        parser.print_json()

    class PathsTable:
        def __init__(self, directory: str, design: str):
            self.directory = directory
            self.design = design
            self.workspace_top = [
                "{}/analyse".format(self.directory),
                "{}/config".format(self.directory),
                "{}/feature".format(self.directory),
                "{}/output".format(self.directory),
                "{}/script".format(self.directory),
                "{}/report".format(self.directory)
            ]

        @property
        def analysis_dir(self):
            return "{}/analyse".format(self.directory)
        
        @property
        def output_dir(self):
            return "{}/output".format(self.directory)

        @property
        def flow(self):
            """path for flow config"""
            return "{}/config/flow.json".format(self.directory)

        @property
        def path(self):
            """path for pdk and design"""
            return "{}/config/path.json".format(self.directory)

        @property
        def workspace(self):
            """path for workspace setting"""
            return "{}/config/workspace.json".format(self.directory)

        @property
        def parameters(self):
            """path for parameters setting"""
            return "{}/config/parameter.json".format(self.directory)

        @property
        def log_dir(self):
            """directory for log file"""
            return "{}/output/log".format(self.directory)

        @property
        def log(self):
            """path for log file"""
            return "{}/{}.log".format(self.log_dir, self.design)
        
        @property
        def report_dir(self):
            return "{}/report".format(self.directory)
        
        @property
        def report(self):
            """path for workspace report file"""
            report_paths = {
                "summary_md": "{}/report/summary.md".format(self.directory),
                "summary_html": "{}/report/summary.html".format(self.directory)
            }
            return report_paths

        @property
        def ieda_output_dirs(self):
            top_dirs = [
                "{}/output/iEDA/data".format(self.directory),
                "{}/output/iEDA/feature".format(self.directory),
                "{}/output/iEDA/result".format(self.directory),
                "{}/output/iEDA/rpt".format(self.directory),
                "{}/output/iEDA/vectors/place".format(self.directory),
                "{}/output/iEDA/vectors/route".format(self.directory),
            ]

            return top_dirs

        @property
        def ieda_config(self):
            config = {
                "config": "{}/config/iEDA_config".format(self.directory),
                "initFlow": "{}/config/iEDA_config/flow_config.json".format(
                    self.directory
                ),
                "initDB": "{}/config/iEDA_config/db_default_config.json".format(
                    self.directory
                ),
                "floorplan": "{}/config/iEDA_config/fp_default_config.json".format(
                    self.directory
                ),
                "pnp": "{}/config/iEDA_config/pnp_default_config.json".format(
                    self.directory
                ),
                "fixFanout": "{}/config/iEDA_config/no_default_config_fixfanout.json".format(
                    self.directory
                ),
                "place": "{}/config/iEDA_config/pl_default_config.json".format(
                    self.directory
                ),
                "CTS": "{}/config/iEDA_config/cts_default_config.json".format(
                    self.directory
                ),
                "optDrv": "{}/config/iEDA_config/to_default_config_drv.json".format(
                    self.directory
                ),
                "optHold": "{}/config/iEDA_config/to_default_config_hold.json".format(
                    self.directory
                ),
                "optSetup": "{}/config/iEDA_config/to_default_config_setup.json".format(
                    self.directory
                ),
                "legalization": "{}/config/iEDA_config/pl_default_config.json".format(
                    self.directory
                ),
                "route": "{}/config/iEDA_config/rt_default_config.json".format(
                    self.directory
                ),
                "filler": "{}/config/iEDA_config/pl_default_config.json".format(
                    self.directory
                ),
                "drc": "{}/config/iEDA_config/drc_default_config.json".format(
                    self.directory
                ),
            }

            return config

        @property
        def ieda_output(self):
            output = {
                "result": "{}/output/iEDA/result".format(self.directory),
                "data": "{}/output/iEDA/data".format(self.directory),
                "fp": "{}/output/iEDA/data/fp".format(self.directory),
                "pnp": "{}/output/iEDA/data/pnp".format(self.directory),
                "pl": "{}/output/iEDA/data/pl".format(self.directory),
                "cts": "{}/output/iEDA/data/cts".format(self.directory),
                "no": "{}/output/iEDA/data/no".format(self.directory),
                "to": "{}/output/iEDA/data/to".format(self.directory),
                "sta": "{}/output/iEDA/data/sta".format(self.directory),
                "drc": "{}/output/iEDA/data/drc".format(self.directory),
                "rt": "{}/output/iEDA/data/rt".format(self.directory),
                "rt_sta": "{}/output/iEDA/data/rt/sta".format(self.directory),
                "rpt": "{}/output/iEDA/rpt".format(self.directory),
                "feature": "{}/output/iEDA/feature".format(self.directory),
                "vectors": "{}/output/iEDA/vectors".format(self.directory),
                "pl_vectors": "{}/output/iEDA/vectors/place".format(self.directory),
                "rt_vectors": "{}/output/iEDA/vectors/route".format(self.directory),
            }
            return output

        @property
        def ieda_report(self):
            report = {
                "drc": "{}/{}_drc.rpt".format(self.ieda_output["rpt"], self.design)
            }

            return report

        @property
        def ieda_feature_json(self):
            feature_json = {
                "data_summary": "{}/{}_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                # feature for pr stage
                "floorplan_summary": "{}/{}_floorplan_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "floorplan_tool": "{}/{}_floorplan_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "place_summary": "{}/{}_place_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "place_tool": "{}/{}_place_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "place_power": "{}/{}_place_power.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "place_timing": "{}/{}_place_timing.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "CTS_summary": "{}/{}_CTS_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "CTS_tool": "{}/{}_CTS_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "CTS_power": "{}/{}_CTS_power.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "CTS_timing": "{}/{}_CTS_timing.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "fixFanout_summary": "{}/{}_fixFanout_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "fixFanout_tool": "{}/{}_fixFanout_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "optDrv_summary": "{}/{}_optDrv_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "optDrv_tool": "{}/{}_optDrv_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "optHold_summary": "{}/{}_optHold_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "optHold_tool": "{}/{}_optHold_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "optSetup_summary": "{}/{}_optSetup_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "optSetup_tool": "{}/{}_optSetup_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "legalization_summary": "{}/{}_legalization_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "legalization_tool": "{}/{}_legalization_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "filler_summary": "{}/{}_filler_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "filler_tool": "{}/{}_filler_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "route_summary": "{}/{}_route_summary.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "route_tool": "{}/{}_route_tool.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "route_drc": "{}/{}_route_drc.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "route_power": "{}/{}_route_power.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "route_timing": "{}/{}_route_timing.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "place_map": "{}/{}_place_map.json".format(
                    self.ieda_output["feature"], self.design
                ),
                "CTS_map": "{}/{}_CTS_map.json".format(
                    self.ieda_output["feature"], self.design
                ),
            }

            return feature_json

        def ieda_feature_power_json(self, flow):
            power_key = "{}_power".format(flow.step.value)
            json_path = self.ieda_feature_json.get(power_key, None)
            return json_path

        def ieda_feature_timing_json(self, flow):
            timing_key = "{}_timing".format(flow.step.value)
            json_path = self.ieda_feature_json.get(timing_key, None)
            return json_path

        @property
        def ieda_vectors(self):
            vectors_paths = {
                "tech": "{}/tech/tech.json".format(self.ieda_output["vectors"]),
                "cells": "{}/tech/cells.json".format(self.ieda_output["vectors"]),
                "instances": "{}/instances/instances.json".format(
                    self.ieda_output["vectors"]
                ),
                "nets": "{}/nets".format(self.ieda_output["vectors"]),
                "patchs": "{}/patchs".format(self.ieda_output["vectors"]),
                "wire_graph": "{}/wire_graph".format(self.ieda_output["vectors"]),
                "wire_paths": "{}/wire_paths".format(self.ieda_output["vectors"]),
                "instance_graph": "{}/instance_graph".format(
                    self.ieda_output["vectors"]
                ),
                "timing_instance_graph": "{}/instance_graph/timing_instance_graph.json".format(
                    self.ieda_output["vectors"]
                ),
                "timing_wire_graph": "{}/wire_graph/timing_wire_graph.json".format(
                    self.ieda_output["vectors"]
                ),
            }

            return vectors_paths

        @property
        def ieda_gui(self):
            gui_paths = {
                "instance_graph": "{}/instance_graph/instance_graph.png".format(
                    self.ieda_output["vectors"]
                )
            }

            return gui_paths

        @property
        def scripts(self):
            scirpt_paths = {
                "main": "{}/script/main.tcl".format(self.directory),
                "definition": "{}/script/definition.tcl".format(self.directory),
                "sta": "{}/script/sta.tcl".format(self.directory),
                "power": "{}/script/power.tcl".format(self.directory),
                "mmmc": "{}/script/mmmc.tcl".format(self.directory),
                "drc": "{}/script/drc.tcl".format(self.directory),
                "timing": "{}/script/timing.tcl".format(self.directory),
            }
            return scirpt_paths

        @property
        def analysis_images(self):
            """Analysis visualization image paths"""
            image_paths = {
                # Design analysis images
                "design_cell_type_bottom_10": "{}/design_cell_type_bottom_10.png".format(self.analysis_dir),
                "design_cell_type_top_10": "{}/design_cell_type_top_10.png".format(self.analysis_dir),
                "design_core_usage_hist": "{}/design_core_usage_hist.png".format(self.analysis_dir),
                "design_pin_vs_net_ratio": "{}/design_pin_vs_net_ratio.png".format(self.analysis_dir),
                "design_result_stats_heatmap": "{}/design_result_stats_heatmap.png".format(self.analysis_dir),
                "design_result_stats_overview": "{}/design_result_stats_overview.png".format(self.analysis_dir),
                
                # Net analysis images
                "net_correlation_matrix": "{}/net_correlation_matrix.png".format(self.analysis_dir),
                "net_wire_length_distribution": "{}/net_wire_length_distribution.png".format(self.analysis_dir),
                
                # Patch analysis images
                "patch_congestion_wire_density_regression": "{}/patch_congestion_wire_density_regression.png".format(self.analysis_dir),
                "patch_feature_correlation": "{}/patch_feature_correlation.png".format(self.analysis_dir),
                "patch_feature_distributions": "{}/patch_feature_distributions.png".format(self.analysis_dir),
                "patch_layer_comparison": "{}/patch_layer_comparison.png".format(self.analysis_dir),
                
                # Path analysis images
                "path_delay_boxplot": "{}/path_delay_boxplot.png".format(self.analysis_dir),
                "path_delay_scatter": "{}/path_delay_scatter.png".format(self.analysis_dir),
                "path_stage_delay_scatter": "{}/path_stage_delay_scatter.png".format(self.analysis_dir),
                "path_stage_errorbar": "{}/path_stage_errorbar.png".format(self.analysis_dir),
            }
            return image_paths

        def get_image_path(self, image_type: str, design_name: str = None):
            """Get specific image path by type
            Args:
                image_type: Type of image (e.g., 'net_wire_length_distribution', 'design_pin_vs_net_ratio')
                design_name: Design name for MapAnalyzer images (optional)
            """
            if design_name and image_type.startswith('patch_map_'):
                # For individual feature maps: patch_map_{design}_{feature}
                feature = image_type.replace('patch_map_', '')
                return "{}/patch_map_{}_{}.png".format(self.analysis_dir, design_name, feature.replace(' ', '_'))
            elif design_name and image_type == 'patch_map_union':
                return "{}/patch_map_{}_union.png".format(self.analysis_dir, design_name)
            
            return self.analysis_images.get(image_type, None)

    class Configs:
        def __init__(self, paths_table, logger):
            self.paths_table = paths_table
            self.logger = logger
            self.flows = self._init_flow_json()
            self.paths = self._init_path_json()
            self.workspace = self._init_workspace_json()
            self.parameters = self._init_parameters()

        def update(self):
            self.flows = self._init_flow_json()
            self.paths = self._init_path_json()
            self.workspace = self._init_workspace_json()
            self.parameters = self._init_parameters()

        def _init_flow_json(self):
            from .config import FlowParser

            parser = FlowParser(self.paths_table.flow, self.logger)
            return parser.get_db()

        def _init_path_json(self):
            from .config import PathParser

            parser = PathParser(self.paths_table.path, self.logger)
            return parser.get_db()

        def _init_workspace_json(self):
            from .config.json_workspace import WorkspaceParser

            parser = WorkspaceParser(self.paths_table.workspace, self.logger)
            return parser.get_db()

        def _init_parameters(self):
            from .config.json_parameters import ParametersParser

            parser = ParametersParser(self.paths_table.parameters, self.logger)
            return parser.get_db()

        def reset_flow_states(self):
            from .config import FlowParser

            parser = FlowParser(self.paths_table.flow, self.logger)
            parser.reset_flow_state()

            # reset flows data
            self.flows = self._init_flow_json()

        def save_flow_state(self, db_flow):
            """save flow state"""
            from .config import FlowParser

            parser = FlowParser(self.paths_table.flow, self.logger)
            parser.set_flow_state(db_flow)

        def get_output_def(self, flow, compressed: bool = True):
            """get ouput def"""
            step_value = "route" if flow.step.value == "full_flow" else flow.step.value
            if flow.eda_tool == "iEDA":
                def_file = "{}/{}_{}.def".format(
                    self.paths_table.ieda_output["result"],
                    self.workspace.design,
                    step_value,
                )
                if compressed:
                    def_file = "{}.gz".format(def_file)

            return def_file

        def get_output_verilog(self, flow, compressed: bool = True):
            """get ouput def"""
            step_value = "route" if flow.step.value == "full_flow" else flow.step.value
            if flow.eda_tool == "iEDA":
                def_file = "{}/{}_{}.v".format(
                    self.paths_table.ieda_output["result"],
                    self.workspace.design,
                    step_value,
                )
                if compressed:
                    def_file = "{}.gz".format(def_file)

            return def_file
