""" workspace definition.


"""
from enum import Enum, auto, unique

def workspace_create(directory : str, design : str):
    ws = Workspace(directory=directory, design=design)
    
    return ws
    
class Workspace:
    def __init__(self, directory : str, design : str):
        self.directory = directory
        self.design = design
        self.paths_table = self.PathsTable(directory, design)
        self.configs = self.Configs(self.paths_table)
    
    def __init_paths__(self):
        pass
    
    def update_config(self, eda_tool = "iEDA"):
        pass
    
    class PathsTable:
        def __init__(self, directory : str, design : str):
            self.directory = directory
            self.design = design
            
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