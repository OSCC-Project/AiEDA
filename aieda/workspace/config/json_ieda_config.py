#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : config_ieda_ieda.py
@Author : yell
@Desc : set iEDA config
"""

from ...utility.json_parser import JsonParser


class ConfigIEDAFlowParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "ConfigPath": {
                "idb_path": "./iEDA_config/db_default_config.json",
                "ifp_path": "./iEDA_config/fp_default_config.json",
                "ipl_path": "./iEDA_config/pl_default_config.json",
                "irt_path": "./iEDA_config/rt_default_config.json",
                "idrc_path": "./iEDA_config/drc_default_config.json",
                "icts_path": "./iEDA_config/cts_default_config.json",
                "ito_path": "./iEDA_config/to_default_config.json",
                "ipnp_path": "./iEDA_config/pnp_default_config.json",
            }
        }

        return dict_data

    def create_json_default(self):
        # create json
        if self.read_create():
            self.json_data = self.default_json

        return self.write()


class ConfigIEDADbParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "INPUT": {
                "tech_lef_path": "",
                "lef_paths": "",
                "def_path": "",
                "verilog_path": "",
                "lib_path": "",
                "sdc_path": "",
            },
            "OUTPUT": {"output_dir_path": ""},
            "LayerSettings": {"routing_layer_1st": ""},
        }
        return dict_data

    def create_json_default(self, paths_table):
        # create json
        if self.read_create():
            self.json_data = self.default_json
            self.json_data["OUTPUT"]["output_dir_path"] = paths_table.ieda_output[
                "result"
            ]

        return self.write()

    def set_tech_lef(self, tech_lef: str):
        if self.read():
            self.json_data["INPUT"]["tech_lef_path"] = tech_lef

            # save file
            return self.write()

        return False

    def set_lefs(self, lefs: list[str]):
        if self.read():
            self.json_data["INPUT"]["lef_paths"] = lefs

            # save file
            return self.write()

        return False

    def set_def_input(self, def_path: str):
        if self.read():
            self.json_data["INPUT"]["def_path"] = def_path

            # save file
            return self.write()

        return False

    def set_verilog_input(self, verilog_path: str):
        if self.read():
            self.json_data["INPUT"]["verilog_path"] = verilog_path

            # save file
            return self.write()

        return False

    def set_libs(self, libs: list[str]):
        if self.read():
            self.json_data["INPUT"]["lib_path"] = libs

            # save file
            return self.write()

        return False

    def set_sdc(self, sdc_path: str):
        if self.read():
            self.json_data["INPUT"]["sdc_path"] = sdc_path

            # save file
            return self.write()

        return False

    def set_spef(self, spef_path: str):
        if self.read():
            self.json_data["INPUT"]["spef_path"] = spef_path

            # save file
            return self.write()

        return False

    def set_output_dir(self, output_dir: str):
        if self.read():
            self.json_data["OUTPUT"]["output_dir_path"] = output_dir

            # save file
            return self.write()

        return False

    def set_first_routing_layer(self, layer: str):
        if self.read():
            self.json_data["LayerSettings"]["routing_layer_1st"] = layer

            # save file
            return self.write()

        return False


class ConfigIEDACTSParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "use_skew_tree_alg": "OFF",
            "router_type": "GOCA",
            "delay_type": "elmore",
            "cluster_type": "kmeans",
            "skew_bound": "0.08",
            "max_buf_tran": "1.0",
            "max_sink_tran": "1.0",
            "max_cap": "0.15",
            "max_fanout": "32",
            "min_length": "50",
            "max_length": "300",
            "scale_size": 50,
            "cluster_size": 32,
            "routing_layer": [4, 5],
            "buffer_type": [],
            "root_buffer_type": "",
            "root_buffer_required": "OFF",
            "inherit_root": "OFF",
            "break_long_wire": "OFF",
            "level_max_length": ["300", "250"],
            "level_max_fanout": [32, 12],
            "level_max_cap": ["0.15"],
            "level_skew_bound": ["0.08"],
            "level_cluster_ratio": ["1", "0.9"],
            "shift_level": 1,
            "latency_opt_level": 1,
            "global_latency_opt_ratio": "0.5",
            "local_latency_opt_ratio": "0.9",
            "external_model": [],
            "use_netlist": "OFF",
            "net_list": [],
        }
        return dict_data

    def create_json_default(self):
        # create json
        if self.read_create():
            self.json_data = self.default_json

        return self.write()

    def set_buffer_type(self, buffer_type: list[str]):
        if self.read():
            self.json_data["buffer_type"] = buffer_type

            # save file
            return self.write()

        return False

    def set_root_buffer_type(self, root_buffer_type: str):
        if self.read():
            self.json_data["root_buffer_type"] = root_buffer_type

            # save file
            return self.write()

        return False

    def set_skew_bound(self, skew_bound: float):
        if self.read():
            self.json_data["skew_bound"] = str(skew_bound)

            # save file
            return self.write()

        return False

    def set_max_buf_tran(self, max_buf_tran: float):
        if self.read():
            self.json_data["max_buf_tran"] = str(max_buf_tran)

            # save file
            return self.write()

        return False

    def set_max_sink_tran(self, max_sink_tran: float):
        if self.read():
            self.json_data["max_sink_tran"] = str(max_sink_tran)

            # save file
            return self.write()

        return False

    def set_max_cap(self, max_cap: float):
        if self.read():
            self.json_data["max_cap"] = str(max_cap)

            # save file
            return self.write()

        return False

    def set_max_fanout(self, max_fanout: int):
        if self.read():
            self.json_data["max_fanout"] = str(max_fanout)

            # save file
            return self.write()

        return False

    def set_cluster_size(self, cluster_size: int):
        if self.read():
            self.json_data["cluster_size"] = cluster_size

            # save file
            return self.write()

        return False


class ConfigIEDAFixFanoutParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "file_path": {
                "design_work_space": "",
                "sdc_file": "",
                "lib_files": [],
                "lef_files": [],
                "def_file": "",
                "output_def": "",
                "report_file": "",
                "gds_file": "",
            },
            "insert_buffer": "",
            "max_fanout": 30,
        }

        return dict_data

    def create_json_default(self, paths_table):
        # create json
        if self.read_create():
            self.json_data = self.default_json

            self.json_data["file_path"]["design_work_space"] = paths_table.ieda_output[
                "no"
            ]
            self.json_data["file_path"]["output_def"] = "{}/ino.def".format(
                paths_table.ieda_output["no"]
            )
            self.json_data["file_path"]["report_file"] = "{}/ino.rpt".format(
                paths_table.ieda_output["no"]
            )
            self.json_data["file_path"]["gds_file"] = "{}/ino.gds".format(
                paths_table.ieda_output["no"]
            )

        return self.write()

    def set_insert_buffer(self, insert_buffer: str):
        if self.read():
            self.json_data["insert_buffer"] = insert_buffer

            # save file
            return self.write()

        return False


class ConfigIEDAPlacementParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "PL": {
                "is_max_length_opt": 0,
                "max_length_constraint": 1000000,
                "is_timing_effort": 0,
                "is_congestion_effort": 0,
                "ignore_net_degree": 100,
                "num_threads": 1,
                "info_iter_num": 10,
                "GP": {
                    "Wirelength": {
                        "init_wirelength_coef": 0.25,
                        "reference_hpwl": 446000000,
                        "min_wirelength_force_bar": -300,
                    },
                    "Density": {
                        "target_density": 0.8,
                        "is_adaptive_bin": 1,
                        "bin_cnt_x": 128,
                        "bin_cnt_y": 128,
                    },
                    "Nesterov": {
                        "max_iter": 2000,
                        "max_backtrack": 10,
                        "init_density_penalty": 0.00008,
                        "target_overflow": 0.1,
                        "initial_prev_coordi_update_coef": 100,
                        "min_precondition": 1.0,
                        "min_phi_coef": 0.95,
                        "max_phi_coef": 1.05,
                    },
                },
                "BUFFER": {"max_buffer_num": 10000, "buffer_type": []},
                "LG": {"max_displacement": 1000000, "global_right_padding": 0},
                "DP": {
                    "max_displacement": 1000000,
                    "global_right_padding": 0,
                    "enable_networkflow": 0,
                },
                "Filler": {"first_iter": [], "second_iter": [], "min_filler_width": 1},
            }
        }

        return dict_data

    def create_json_default(self):
        # create json
        if self.read_create():
            self.json_data = self.default_json

        return self.write()

    def set_buffer_type(self, buffer_type: list[str]):
        if self.read():
            self.json_data["PL"]["BUFFER"]["buffer_type"] = buffer_type

            # save file
            return self.write()

        return False

    def set_filler_first_iter(self, first_iter: list[str]):
        if self.read():
            self.json_data["PL"]["Filler"]["first_iter"] = first_iter

            # save file
            return self.write()

        return False

    def set_filler_second_iter(self, second_iter: list[str]):
        if self.read():
            self.json_data["PL"]["Filler"]["second_iter"] = second_iter

            # save file
            return self.write()

        return False

    def set_target_density(self, target_density):
        if self.read():
            self.json_data["PL"]["GP"]["Density"]["target_density"] = target_density

            # save file
            return self.write()

        return False

    def set_max_phi_coef(self, max_phi_coef):
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["max_phi_coef"] = max_phi_coef

            # save file
            return self.write()

        return False

    def set_init_wirelength_coef(self, init_wirelength_coef):
        if self.read():
            self.json_data["PL"]["GP"]["Wirelength"][
                "init_wirelength_coef"
            ] = init_wirelength_coef

            # save file
            return self.write()

        return False

    def set_min_wirelength_force_bar(self, min_wirelength_force_bar):
        if self.read():
            self.json_data["PL"]["GP"]["Wirelength"][
                "min_wirelength_force_bar"
            ] = min_wirelength_force_bar

            # save file
            return self.write()

        return False

    def set_max_backtrack(self, max_backtrack):
        """Set max backtrack for Nesterov"""
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["max_backtrack"] = max_backtrack
            return self.write()
        return False

    def set_init_density_penalty(self, init_density_penalty):
        """Set initial density penalty for Nesterov"""
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["init_density_penalty"] = init_density_penalty
            return self.write()
        return False

    def set_target_overflow(self, target_overflow):
        """Set target overflow for Nesterov"""
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["target_overflow"] = target_overflow
            return self.write()
        return False

    def set_initial_prev_coordi_update_coef(self, initial_prev_coordi_update_coef):
        """Set initial previous coordinate update coefficient for Nesterov"""
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["initial_prev_coordi_update_coef"] = initial_prev_coordi_update_coef
            return self.write()
        return False

    def set_min_precondition(self, min_precondition):
        """Set min precondition for Nesterov"""
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["min_precondition"] = min_precondition
            return self.write()
        return False

    def set_min_phi_coef(self, min_phi_coef):
        """Set min phi coefficient for Nesterov"""
        if self.read():
            self.json_data["PL"]["GP"]["Nesterov"]["min_phi_coef"] = min_phi_coef
            return self.write()
        return False

class ConfigIEDARouterParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "RT": {
                "-temp_directory_path": "",
                "-bottom_routing_layer": "",
                "-top_routing_layer": "",
                "-thread_number": "50",
                "-enable_timing": "0",
                "-output_csv": "0",
                "-output_inter_result": "0",
            }
        }

        return dict_data

    def create_json_default(self, paths_table):
        # create json
        if self.read_create():
            self.json_data = self.default_json

            self.json_data["RT"]["-temp_directory_path"] = "{}".format(
                paths_table.ieda_output["rt"]
            )

        return self.write()

    def set_bottom_routing_layer(self, bottom_routing_layer: str):
        if self.read():
            self.json_data["RT"]["-bottom_routing_layer"] = bottom_routing_layer

            # save file
            return self.write()

        return False

    def set_top_routing_layer(self, top_routing_layer: str):
        if self.read():
            self.json_data["RT"]["-top_routing_layer"] = top_routing_layer

            # save file
            return self.write()

        return False

    def set_thread_number(self, thread_number: int):
        if self.read():
            self.json_data["RT"]["-thread_number"] = thread_number

            # save file
            return self.write()

        return False

    def set_enable_timing(self, enable_timing: bool):
        if self.read():
            if enable_timing:
                self.json_data["RT"]["-enable_timing"] = "1"
            else:
                self.json_data["RT"]["-enable_timing"] = "0"

            # save file
            return self.write()

        return False


class ConfigIEDATimingOptParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "file_path": {
                "design_work_space": "",
                "sdc_file": "",
                "lib_files": "",
                "lef_files": "",
                "def_file": "",
                "output_def": "",
                "report_file": "",
                "gds_file": "",
            },
            "specific_prefix": {
                "drv": {"make_buffer": "drv_buffer_", "make_net": "drv_net_"},
                "hold": {"make_buffer": "hold_buffer_", "make_net": "hold_net_"},
                "setup": {"make_buffer": "setup_buffer_", "make_net": "setup_net_"},
            },
            "routing_tree": "flute",
            "setup_target_slack": 0.0,
            "hold_target_slack": 0.4,
            "max_insert_instance_percent": 0.2,
            "max_core_utilization": 0.8,
            "fix_fanout": False,
            "optimize_drv": False,
            "optimize_hold": False,
            "optimize_setup": False,
            "DRV_insert_buffers": [],
            "setup_insert_buffers": [],
            "hold_insert_buffers": [],
            "number_of_decreasing_slack_iter": 5,
            "max_allowed_buffering_fanout": 20,
            "min_divide_fanout": 8,
            "optimize_endpoints_percent": 1.0,
            "drv_optimize_iter_number": 5,
        }

        return dict_data

    def create_json_default(self, paths_table, opt_type: str):
        # create json
        if self.read_create():
            self.json_data = self.default_json

            self.json_data["file_path"]["design_work_space"] = paths_table.ieda_output[
                "to"
            ]
            self.json_data["file_path"]["output_def"] = "{}/ito.def".format(
                paths_table.ieda_output["to"]
            )
            self.json_data["file_path"]["report_file"] = "{}/ito.rpt".format(
                paths_table.ieda_output["to"]
            )
            self.json_data["file_path"]["gds_file"] = "{}/ito.gds".format(
                paths_table.ieda_output["to"]
            )

            if opt_type == "optimize_drv":
                self.json_data["optimize_drv"] = True
                self.json_data["optimize_hold"] = False
                self.json_data["optimize_setup"] = False

            if opt_type == "optimize_hold":
                self.json_data["optimize_drv"] = False
                self.json_data["optimize_hold"] = True
                self.json_data["optimize_setup"] = False

            if opt_type == "optimize_setup":
                self.json_data["optimize_drv"] = False
                self.json_data["optimize_hold"] = False
                self.json_data["optimize_setup"] = True

        return self.write()

    def set_drv_insert_buffers(self, buffer_type: list[str]):
        if self.read():
            self.json_data["DRV_insert_buffers"] = buffer_type

            # save file
            return self.write()

        return False

    def set_hold_insert_buffers(self, hold_insert_buffers: list[str]):
        if self.read():
            self.json_data["hold_insert_buffers"] = hold_insert_buffers

            # save file
            return self.write()

        return False

    def set_setup_insert_buffers(self, setup_insert_buffers: list[str]):
        if self.read():
            self.json_data["setup_insert_buffers"] = setup_insert_buffers

            # save file
            return self.write()

        return False


class ConfigIEDAFloorplanParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {}

        return dict_data

    def create_json_default(self):
        # create json
        if self.read_create():
            self.json_data = self.default_json

        return self.write()


class ConfigIEDADrcParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {}

        return dict_data

    def create_json_default(self):
        # create json
        if self.read_create():
            self.json_data = self.default_json

        return self.write()


class ConfigIEDAPNPParser(JsonParser):
    """config iEDA json"""

    def __init__(self, json_path: str, logger):
        super().__init__(json_path, logger)

    @property
    def default_json(self):
        dict_data = {
            "timing": {"design_workspace": ""},
            "power": {"power_net_name": "VDD"},
            "egr": {"map_path": ""},
            "grid": {
                "power_layers": ["met5", "met4"],
                "follow_pin_layers": ["met1"],
                "follow_pin_width": 480.0,
                "power_port_layer": "met5",
                "ho_region_num": 1,
                "ver_region_num": 1,
            },
            "simulated_annealing": {
                "initial_temp": 100.0,
                "cooling_rate": 0.95,
                "min_temp": 0.1,
                "iterations_per_temp": 10,
                "ir_drop_weight": 0.6,
                "overflow_weight": 0.4,
                "modifiable_layer_min": "met2",
                "modifiable_layer_max": "met5",
            },
            "templates": {
                "horizontal": [
                    {
                        "width": 1600.0,
                        "pg_offset": 6800.0,
                        "space": 13600.0,
                        "offset": 1200.0,
                    }
                ],
                "vertical": [
                    {
                        "width": 1600.0,
                        "pg_offset": 6800.0,
                        "space": 13600.0,
                        "offset": 1200.0,
                    }
                ],
                "layer_specific": {},
            },
        }

        return dict_data

    def create_json_default(self, paths_table):
        # create json
        if self.read_create():
            self.json_data = self.default_json

            self.json_data["timing"]["design_workspace"] = "{}".format(
                paths_table.ieda_output["pnp"]
            )
            self.json_data["egr"]["map_path"] = "{}".format(
                paths_table.ieda_output["pnp"]
            )

        return self.write()
    
    def set_pnp_grid_power_layers(self, power_layers: list[str]):
        if self.read():
            self.json_data["grid"]["power_layers"] = power_layers

            # save file
            return self.write()

        return False
    
    def set_pnp_grid_follow_pin_layers(self, follow_pin_layers: list[str]):
        if self.read():
            self.json_data["grid"]["follow_pin_layers"] = follow_pin_layers

            # save file
            return self.write()

        return False
    
    def set_pnp_grid_follow_pin_width(self, follow_pin_width):
        if self.read():
            self.json_data["grid"]["follow_pin_width"] = follow_pin_width

            # save file
            return self.write()

        return False
    
    def set_pnp_grid_power_port_layer(self, power_port_layer: str):
        if self.read():
            self.json_data["grid"]["power_port_layer"] = power_port_layer

            # save file
            return self.write()

        return False
    
    def set_pnp_simulated_annealing_modifiable_layer_min(self, modifiable_layer_min: str):
        if self.read():
            self.json_data["simulated_annealing"]["modifiable_layer_min"] = modifiable_layer_min

            # save file
            return self.write()

        return False
    
    def set_pnp_simulated_annealing_modifiable_layer_max(self, modifiable_layer_max: str):
        if self.read():
            self.json_data["simulated_annealing"]["modifiable_layer_max"] = modifiable_layer_max

            # save file
            return self.write()

        return False
    
    def set_templates_horizontal_width(self, width):
        if self.read():
            self.json_data["templates"]["horizontal"]["width"] = width

            # save file
            return self.write()

        return False
    
    def set_templates_horizontal_pg_offset(self, pg_offset):
        if self.read():
            self.json_data["templates"]["horizontal"]["pg_offset"] = pg_offset

            # save file
            return self.write()

        return False
    
    def set_templates_horizontal_space(self, space):
        if self.read():
            self.json_data["templates"]["horizontal"]["space"] = space

            # save file
            return self.write()

        return False
    
    def set_templates_horizontal_offset(self, offset):
        if self.read():
            self.json_data["templates"]["horizontal"]["offset"] = offset

            # save file
            return self.write()

        return False
    
    def set_templates_vertical_width(self, width):
        if self.read():
            self.json_data["templates"]["vertical"]["width"] = width

            # save file
            return self.write()

        return False
    
    def set_templates_vertical_pg_offset(self, pg_offset):
        if self.read():
            self.json_data["templates"]["vertical"]["pg_offset"] = pg_offset

            # save file
            return self.write()

        return False
    
    def set_templates_vertical_space(self, space):
        if self.read():
            self.json_data["templates"]["vertical"]["space"] = space

            # save file
            return self.write()

        return False
    
    def set_templates_vertical_offset(self, offset):
        if self.read():
            self.json_data["templates"]["vertical"]["offset"] = offset

            # save file
            return self.write()

        return False
