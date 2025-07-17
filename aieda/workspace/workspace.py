""" workspace definition.


"""
def workspace_create(directory : str, design : str):
    ws = Workspace(directory=directory, design=design)
    
    ws.create_wrokspace()
    
    return ws
    
class Workspace:
    def __init__(self, directory : str, design : str):
        self.directory = directory
        self.design = design
        self.paths_table = self.PathsTable(directory, design)
        self.configs = self.Configs(self.paths_table)
    
    def create_wrokspace(self):
        """check if workspace exist, if not exist, create workspace
        """
        #########################################################################
        # step 1, ensure workspace dir exist
        #########################################################################
        import os
        if os.path.exists(self.directory):
            return True
        os.makedirs(self.directory)
        
        #########################################################################
        # step 2, create dir in workspace
        #########################################################################
        for dir in self.paths_table.workspace_top:
            os.makedirs(dir)
        
        for dir in self.paths_table.ieda_output_dirs:
            os.makedirs(dir)
        
        #########################################################################
        # step 3, create flow.json
        #########################################################################
        from .config import FlowParser
        parser = FlowParser(self.paths_table.flow)
        parser.create_json(self.configs.flows)
        
        #########################################################################
        # step 4, create path.json
        #########################################################################
        from .config import PathParser
        parser = PathParser(self.paths_table.path)
        parser.create_json(self.configs.paths)
        
        #########################################################################
        # step 5, create workspace.json
        #########################################################################
        from .config import WorkspaceParser
        if self.configs.workspace.design is None:
            self.configs.workspace.design = self.design
            
        parser = WorkspaceParser(self.paths_table.workspace)
        parser.create_json(self.configs.workspace)
        
        #########################################################################
        # step 6, create parameters.json
        #########################################################################
        from .config import ParametersParser
        parser = ParametersParser(self.paths_table.parameters)
        parser.create_json(self.configs.parameters)
        
        #########################################################################
        # step 7, create iEDA_config
        #########################################################################
        # create dir
        os.makedirs(self.paths_table.ieda_config['config'])
        
        # create flow_config.json
        from .config import ConfigIEDAFlowParser
        parser = ConfigIEDAFlowParser(self.paths_table.ieda_config['initFlow'])
        parser.create_json_default()
        
        # create db_default_config.json
        from .config import ConfigIEDADbParser
        parser = ConfigIEDADbParser(self.paths_table.ieda_config['initDB'])
        parser.create_json_default(self.paths_table)
        
        # create fp_default_config.json
        from .config import ConfigIEDAFloorplanParser
        parser = ConfigIEDAFloorplanParser(self.paths_table.ieda_config['floorplan'])
        parser.create_json_default()
        
        # create no_default_config_fixfanout.json
        from .config import ConfigIEDAFixFanoutParser
        parser = ConfigIEDAFixFanoutParser(self.paths_table.ieda_config['fixFanout'])
        parser.create_json_default(self.paths_table)
        
        # create pl_default_config.json
        from .config import ConfigIEDAPlacementParser
        parser = ConfigIEDAPlacementParser(self.paths_table.ieda_config['place'])
        parser.create_json_default()
        
        # create cts_default_config.json
        from .config import ConfigIEDACTSParser
        parser = ConfigIEDACTSParser(self.paths_table.ieda_config['CTS'])
        parser.create_json_default()
        
        # create to_default_config_drv.json
        from .config import ConfigIEDATimingOptParser
        parser = ConfigIEDATimingOptParser(self.paths_table.ieda_config['optDrv'])
        parser.create_json_default(self.paths_table, "optimize_drv")
        
        # create to_default_config_hold.json
        from .config import ConfigIEDATimingOptParser
        parser = ConfigIEDATimingOptParser(self.paths_table.ieda_config['optHold'])
        parser.create_json_default(self.paths_table, "optimize_hold")
        
        # create to_default_config_setup.json
        from .config import ConfigIEDATimingOptParser
        parser = ConfigIEDATimingOptParser(self.paths_table.ieda_config['optSetup'])
        parser.create_json_default(self.paths_table, "optimize_setup")
        
        # create rt_default_config.json
        from .config import ConfigIEDARouterParser
        parser = ConfigIEDARouterParser(self.paths_table.ieda_config['route'])
        parser.create_json_default(self.paths_table)
        
        # create drc_default_config.json
        from .config import ConfigIEDADrcParser
        parser = ConfigIEDADrcParser(self.paths_table.ieda_config['drc'])
        parser.create_json_default()
        
        #########################################################################
        # step 8 : update config
        #########################################################################
        self.configs.update()

    def set_tech_lef(self, tech_lef : str):
        # update data
        self.configs.paths.tech_lef_path = tech_lef
        
        # update tech lef in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_tech_lef(tech_lef)
        
        # update tech lef in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_tech_lef(tech_lef=tech_lef)
        
    def set_lefs(self, lefs : list[str]):
        # update data
        self.configs.paths.lef_paths = lefs
        
        # update lefs in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_lefs(lefs)
        
        # update lefs in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_lefs(lefs=lefs)
        
    def set_libs(self, libs : list[str]):
        # update data
        self.configs.paths.lib_paths = libs
        
        # update libs in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_libs(libs)
        
        # update libs in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_libs(libs=libs)
        
    def set_sdc(self, sdc_path : str):
        # update data
        self.configs.paths.sdc_path = sdc_path
        
        # update sdc in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_sdc(sdc_path)
        
        # update sdc in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_sdc(sdc_path=sdc_path)
        
    def set_spef(self, spef_path : str):
        # update data
        self.configs.paths.spef_path = spef_path
        
        # update sdc in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_spef(spef_path)
        
        # update sdc in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_spef(spef_path=spef_path)
    
    def set_def_input(self, def_input : str):
        # update data
        self.configs.paths.def_input_path = def_input
        
        # update def input in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_def_input(def_input)
        
        # update def input in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_def_input(def_path=def_input)
    
    def set_verilog_input(self, verilog_input : str):
        # update data
        self.configs.paths.verilog_input_path = verilog_input
        
        # update verilog input in path.json 
        from .config import PathParser
        json_path = self.paths_table.path
        parser = PathParser(json_path)
        parser.set_verilog_input(verilog_input)
        
        # update verilog input in iEDA_config/db_default_config.json 
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_verilog_input(verilog_path=verilog_input)
        
    def set_flows(self, flows):
        # update data
        self.configs.flows = flows
        
        # update flows in flow.json
        from .config import FlowParser
        parser = FlowParser(self.paths_table.flow)
        parser.create_json(self.configs.flows)
    
    def set_process_node(self, process_node :str):
        # update data
        self.configs.workspace.process_node = process_node
        
        # udpate process_node in workspace.json
        from .config import WorkspaceParser
        parser = WorkspaceParser(self.paths_table.workspace)
        parser.set_process_node(process_node)
    
    def set_design(self, design :str):
        # update data
        self.design = design
        self.configs.workspace.design = design
        
        # udpate design in workspace.json
        from .config import WorkspaceParser
        parser = WorkspaceParser(self.paths_table.workspace)
        parser.set_design(design)
    
    def set_version(self, version :str):
        # update data
        self.configs.workspace.version = version
        
        # udpate version in workspace.json
        from .config import WorkspaceParser
        parser = WorkspaceParser(self.paths_table.workspace)
        parser.set_version(version)
    
    def set_project(self, project :str):
        # update data
        self.configs.workspace.project = project
        
        # udpate project in workspace.json
        from .config import WorkspaceParser
        parser = WorkspaceParser(self.paths_table.workspace)
        parser.set_project(project)
    
    def set_task(self, task :str):
        # update data
        self.configs.workspace.task = task
        
        # udpate project in workspace.json
        from .config import WorkspaceParser
        parser = WorkspaceParser(self.paths_table.workspace)
        parser.set_task(task)
    
    def set_first_routing_layer(self, layer : str):
        from .config import ConfigIEDADbParser
        json_path = self.paths_table.ieda_config['initDB']
        parser = ConfigIEDADbParser(json_path)
        parser.set_first_routing_layer(layer=layer)
        
    def set_ieda_fixfanout_buffer(self, buffer : str):
        from .config import ConfigIEDAFixFanoutParser
        parser = ConfigIEDAFixFanoutParser(self.paths_table.ieda_config['fixFanout'])
        parser.set_insert_buffer(buffer)
    
    def set_ieda_cts_buffers(self, buffers : list[str]):
        from .config import ConfigIEDACTSParser
        parser = ConfigIEDACTSParser(self.paths_table.ieda_config['CTS'])
        parser.set_buffer_type(buffers)
    
    def set_ieda_cts_root_buffer(self, buffer : str):
        from .config import ConfigIEDACTSParser
        parser = ConfigIEDACTSParser(self.paths_table.ieda_config['CTS'])
        parser.set_root_buffer_type(buffer)
    
    def set_ieda_placement_buffers(self, buffers : list[str]):
        from .config import ConfigIEDAPlacementParser
        parser = ConfigIEDAPlacementParser(self.paths_table.ieda_config['place'])
        parser.set_buffer_type(buffers)
    
    def set_ieda_filler_cells_for_first_iteration(self, cells : list[str]):
        from .config import ConfigIEDAPlacementParser
        parser = ConfigIEDAPlacementParser(self.paths_table.ieda_config['filler'])
        parser.set_filler_first_iter(cells)
    
    def set_ieda_filler_cells_for_second_iteration(self, cells : list[str]):
        from .config import ConfigIEDAPlacementParser
        parser = ConfigIEDAPlacementParser(self.paths_table.ieda_config['filler'])
        parser.set_filler_second_iter(cells)
        
    def set_ieda_optdrv_buffers(self, buffers : list[str]):
        from .config import ConfigIEDATimingOptParser
        parser = ConfigIEDATimingOptParser(self.paths_table.ieda_config['optDrv'])
        parser.set_drv_insert_buffers(buffers)
        
    def set_ieda_opthold_buffers(self, buffers : list[str]):
        from .config import ConfigIEDATimingOptParser
        parser = ConfigIEDATimingOptParser(self.paths_table.ieda_config['optHold'])
        parser.set_hold_insert_buffers(buffers)
        
    def set_ieda_optsetup_buffers(self, buffers : list[str]):
        from .config import ConfigIEDATimingOptParser
        parser = ConfigIEDATimingOptParser(self.paths_table.ieda_config['optSetup'])
        parser.set_setup_insert_buffers(buffers)
    
    def set_ieda_router_layer(self, bottom_layer : str, top_layer : str):
        from .config import ConfigIEDARouterParser
        parser = ConfigIEDARouterParser(self.paths_table.ieda_config['route'])
        parser.set_bottom_routing_layer(bottom_layer)
        parser.set_top_routing_layer(top_layer)
    
    def set_ieda_router_timing(self, enable_timing : bool):
        from .config import ConfigIEDARouterParser
        parser = ConfigIEDARouterParser(self.paths_table.ieda_config['route'])
        parser.set_enable_timing(enable_timing)
            
    class PathsTable:
        def __init__(self, directory : str, design : str):
            self.directory = directory
            self.design = design
            self.workspace_top = [
                "{}/analysis".format(self.directory),
                "{}/config".format(self.directory),
                "{}/feature".format(self.directory),
                "{}/output".format(self.directory),
                "{}/script".format(self.directory)
            ]
            
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
            return "{}/config/parameters.json".format(self.directory)
        
        @property
        def ieda_output_dirs(self):
            top_dirs = [
                "{}/output/iEDA/data".format(self.directory),
                "{}/output/iEDA/feature".format(self.directory),
                "{}/output/iEDA/result".format(self.directory),
                "{}/output/iEDA/rpt".format(self.directory)
            ]
            
            return top_dirs
        
        @property
        def ieda_config(self):
            config = {
                      'config'  : "{}/config/iEDA_config".format(self.directory),
                     'initFlow' : "{}/config/iEDA_config/flow_config.json".format(self.directory),
                       'initDB' : "{}/config/iEDA_config/db_default_config.json".format(self.directory),
                    'floorplan' : "{}/config/iEDA_config/fp_default_config.json".format(self.directory),
                    'fixFanout' : "{}/config/iEDA_config/no_default_config_fixfanout.json".format(self.directory),
                        'place' : "{}/config/iEDA_config/pl_default_config.json".format(self.directory),
                          'CTS' : "{}/config/iEDA_config/cts_default_config.json".format(self.directory),
                       'optDrv' : "{}/config/iEDA_config/to_default_config_drv.json".format(self.directory),
                      'optHold' : "{}/config/iEDA_config/to_default_config_hold.json".format(self.directory),
                     'optSetup' : "{}/config/iEDA_config/to_default_config_setup.json".format(self.directory),
                 'legalization' : "{}/config/iEDA_config/pl_default_config.json".format(self.directory),
                        'route' : "{}/config/iEDA_config/rt_default_config.json".format(self.directory),
                       'filler' : "{}/config/iEDA_config/pl_default_config.json".format(self.directory),
                          'drc' : "{}/config/iEDA_config/drc_default_config.json".format(self.directory)
                      }
            
            return config
        
        @property
        def ieda_output(self):
            output = {
                    'result' : "{}/output/iEDA/result".format(self.directory),
                      'data' : "{}/output/iEDA/data".format(self.directory),
                        'fp' : "{}/output/iEDA/data/fp".format(self.directory),
                        'pl' : "{}/output/iEDA/data/pl".format(self.directory),
                       'cts' : "{}/output/iEDA/data/cts".format(self.directory),
                        'no' : "{}/output/iEDA/data/no".format(self.directory),
                        'to' : "{}/output/iEDA/data/to".format(self.directory),
                       'sta' : "{}/output/iEDA/data/sta".format(self.directory),
                       'drc' : "{}/output/iEDA/data/drc".format(self.directory),
                        'rt' : "{}/output/iEDA/data/rt".format(self.directory),   
                    'rt_sta' : "{}/output/iEDA/data/rt/sta".format(self.directory),
                       'rpt' : "{}/output/iEDA/rpt".format(self.directory),
                   'feature' : "{}/output/iEDA/feature".format(self.directory),
                   'vectorization' : "{}/output/iEDA/vectorization".format(self.directory),
                }
            return output
        
        @property
        def innovus_output(self):
            output = {
                    'result' : "{}/output/innovus/result".format(self.directory),
                      'data' : "{}/output/innovus/data".format(self.directory),
                       'rpt' : "{}/output/innovus/rpt".format(self.directory),
                       'log' : "{}/output/innovus/log".format(self.directory),
                   'feature' : "{}/output/innovus/feature".format(self.directory),
                   'vectorization' : "{}/output/innovus/vectorization".format(self.directory),
                }
            return output
        
        @property
        def ieda_report(self):
            report = {
                'drc' : "{}/{}_drc.rpt".format(self.ieda_output['rpt'], self.design)
            }
            
            return report
        
        @property
        def ieda_feature_json(self):
            feature_json = {
                'data_summary'    : "{}/{}_summary.json".format(self.ieda_output['feature'], self.design),
                
                # feature for pr stage
                'floorplan_summary'    : "{}/{}_floorplan_summary.json".format(self.ieda_output['feature'], self.design),
                'floorplan_tool'       : "{}/{}_floorplan_tool.json".format(self.ieda_output['feature'], self.design),
                'place_summary'        : "{}/{}_place_summary.json".format(self.ieda_output['feature'], self.design),
                'place_tool'           : "{}/{}_place_tool.json".format(self.ieda_output['feature'], self.design),
                'CTS_summary'          : "{}/{}_CTS_summary.json".format(self.ieda_output['feature'], self.design),
                'CTS_tool'             : "{}/{}_CTS_tool.json".format(self.ieda_output['feature'], self.design),
                'fixFanout_summary'    : "{}/{}_fixFanout_summary.json".format(self.ieda_output['feature'], self.design),
                'fixFanout_tool'       : "{}/{}_fixFanout_tool.json".format(self.ieda_output['feature'], self.design),
                'optDrv_summary'       : "{}/{}_optDrv_summary.json".format(self.ieda_output['feature'], self.design),
                'optDrv_tool'          : "{}/{}_optDrv_tool.json".format(self.ieda_output['feature'], self.design),
                'optHold_summary'      : "{}/{}_optHold_summary.json".format(self.ieda_output['feature'], self.design),
                'optHold_tool'         : "{}/{}_optHold_tool.json".format(self.ieda_output['feature'], self.design),
                'optSetup_summary'     : "{}/{}_optSetup_summary.json".format(self.ieda_output['feature'], self.design),
                'optSetup_tool'        : "{}/{}_optSetup_tool.json".format(self.ieda_output['feature'], self.design),
                'legalization_summary' : "{}/{}_legalization_summary.json".format(self.ieda_output['feature'], self.design),
                'legalization_tool'    : "{}/{}_legalization_tool.json".format(self.ieda_output['feature'], self.design),
                'filler_summary'       : "{}/{}_filler_summary.json".format(self.ieda_output['feature'], self.design),
                'filler_tool'          : "{}/{}_filler_tool.json".format(self.ieda_output['feature'], self.design),
                'route_summary'        : "{}/{}_route_summary.json".format(self.ieda_output['feature'], self.design),
                'route_tool'           : "{}/{}_route_tool.json".format(self.ieda_output['feature'], self.design),      
                'route_drc'            : "{}/{}_route_drc.json".format(self.ieda_output['feature'], self.design)
            }
            
            return feature_json
        
        @property
        def ieda_feature_jsonl(self):
            feature_jsonl = {
                'CTS_eval' : "{}/{}CTS_eval.jsonl".format(self.ieda_output['feature'], self.design),
                'place_eval' : "{}/{}place_eval.jsonl".format(self.ieda_output['feature'], self.design)                
            }
            
            return feature_jsonl
        
        @property
        def ieda_feature_csv(self):
            feature_csv = {
                'CTS_eval' : "{}/{}CTS_eval.csv".format(self.ieda_output['feature'], self.design),
                'place_eval' : "{}/{}place_eval.csv".format(self.ieda_output['feature'], self.design)                
            }
            
            return feature_csv
        
        @property
        def scripts(self):
            scirpt_paths = {
                           'main'       : "{}/script/main.tcl".format(self.directory),
                           'definition' : "{}/script/definition.tcl".format(self.directory)
                           }
            return scirpt_paths
            
            
    class Configs:
        def __init__(self, paths_table):
            self.paths_table = paths_table
            self.flows = self.__init_flow_json__()
            self.paths = self.__init_path_json__()
            self.workspace = self.__init_workspace_json__()
            self.parameters = self.__init_parameters__()
        
        def update(self):
            self.flows = self.__init_flow_json__()
            self.paths = self.__init_path_json__()
            self.workspace = self.__init_workspace_json__()
            self.parameters = self.__init_parameters__()
            
        @property
        def config_ieda(self):
            from .config import ConfigIEDA
            return ConfigIEDA()
        
        def __init_flow_json__(self):
            from .config import FlowParser
            parser = FlowParser(self.paths_table.flow)
            return parser.get_db()
        
        def __init_path_json__(self):
            from .config import PathParser
            parser = PathParser(self.paths_table.path)
            return parser.get_db()
        
        def __init_workspace_json__(self):
            from .config.json_workspace import WorkspaceParser
            parser = WorkspaceParser(self.paths_table.workspace)
            return parser.get_db()
        
        def __init_parameters__(self):
            from .config.json_parameters import ParametersParser
            parser = ParametersParser(self.paths_table.parameters)
            return parser.get_db()
        
        def reset_flow_states(self):
            from .config import FlowParser
            parser = FlowParser(self.paths_table.flow)
            parser.reset_flow_state()
            
            #reset flows data
            self.flows = self.__init_flow_json__()
        
        def save_flow_state(self, db_flow):
            """save flow state"""
            from .config import FlowParser
            parser = FlowParser(self.paths_table.flow)
            parser.set_flow_state(db_flow)
        
        def get_output_def(self, flow, compressed : bool = True):
            """get ouput def"""
            step_value = "route" if flow.step.value == "full_flow" else flow.step.value
            if flow.eda_tool == "iEDA":
                def_file = "{}/{}_{}.def".format(self.paths_table.ieda_output['result'], self.workspace.design, step_value)
                if compressed:
                    def_file = "{}.gz".format(def_file)
                
            return def_file
        
        def get_output_verilog(self, flow, compressed : bool = True):
            """get ouput def"""
            step_value = "route" if flow.step.value == "full_flow" else flow.step.value
            if flow.eda_tool == "iEDA":
                def_file = "{}/{}_{}.v".format(self.paths_table.ieda_output['result'], self.workspace.design, step_value)
                if compressed:
                    def_file = "{}.gz".format(def_file)
                
            return def_file