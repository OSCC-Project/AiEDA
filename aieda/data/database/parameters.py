#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : parameters.py
@Author : yell
@Desc : parameters database
'''
import json 
from dataclasses import dataclass

@dataclass
class EDAParameters(object):
    """data structure"""
    def __init__(self):
        # load default config file
        self.load_default_params()
    
    def load_default_params(self):
        """load default config file"""
        try:
            # get current workspace
            import os
            current_workspace = os.getcwd()
            
            # build default config file path
            default_config_file = os.path.join(current_workspace, "config/iEDA_config/pl_default_config.json")
            
            with open(default_config_file, 'r') as f:
                default_config = json.load(f)
            
            # load default config
            if 'PL' in default_config:
                pl_config = default_config['PL']
                self.pl_config = {"PL": pl_config}
                
                
                
        except Exception as e:
            print(f"warning: failed to load default config file: {e}")
            self.pl_config = {}
    
    def sync_to_default_config(self, dse_config):
        try:
            import os
            current_workspace = os.getcwd()

            default_config_file = os.path.join(current_workspace, "config/iEDA_config/pl_default_config.json")
            

            with open(default_config_file, 'w') as f:
                json.dump(dse_config, f, indent=4)
            
            print(f"here is the config: {dse_config}")
            
        except Exception as e:
            print(f"warning: failed to sync to default config file: {e}")
    
    

    