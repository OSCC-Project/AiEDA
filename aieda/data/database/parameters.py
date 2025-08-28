#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : parameters.py
@Author : zhanghongda
@Desc : parameters database
'''
import json 
from dataclasses import dataclass
@dataclass
class EDAParameters(object):
    """data structure"""
    def __init__(self, workspace_dir=None):
        self.workspace_dir = workspace_dir
        self.load_default_params()
    
    def load_default_params(self):
        """load default config file"""
        try:
            import os
            
            if self.workspace_dir is None:
                self.pl_config = {"PL": {}}
                return

            default_config_file = os.path.join(self.workspace_dir, "config/iEDA_config/pl_default_config.json")
            
            if os.path.exists(default_config_file):
                with open(default_config_file, 'r') as f:
                    default_config = json.load(f)
                
                if 'PL' in default_config:
                    pl_config = default_config['PL']
                    self.pl_config = {"PL": pl_config}
                else:
                    self.pl_config = {"PL": {}}
            else:
                self.pl_config = {"PL": {}}
                
        except Exception as e:
            self.pl_config = {"PL": {}}
        
    def sync_to_default_config(self, dse_config):
        try:
            import os
            current_workspace = os.getcwd()

            default_config_file = os.path.join(current_workspace, "config/iEDA_config/pl_default_config.json")
            
            with open(default_config_file, 'w') as f:
                json.dump(dse_config, f, indent=4)
            
            print(f"here is the config: {dse_config}")
            
        except Exception as e:
            pass
    
    

    