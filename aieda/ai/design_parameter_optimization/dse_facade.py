#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   dse_facade.py
@Time    :   2025-08-29 10:54:34
@Author  :   zhanghongda
@Version :   1.0
@Contact :   zhanghongda24@mails.ucas.ac.cn
@Desc    :   dse facade
"""
import sys
import os
import time
import logging
import datetime
import json


def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..", "..")
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


setup_paths()

from aieda.data.database.enum import DSEMethod
from aieda.workspace.workspace import Workspace
from aieda.ai.design_parameter_optimization.model import NNIOptimization
from aieda.data.database.parameters import EDAParameters


class DSEFacade:
    def __init__(self, workspace : Workspace, step=None, **kwargs):
        self.workspace = workspace

        self.experiment_name = kwargs.get("experiment_name")
        self.scenario_name = kwargs.get("scenario_name", "test_sweep")
        self.seed = kwargs.get("seed", 0)
        self.sweep_worker_num = kwargs.get("sweep_worker_num", 1)
        self.run_count = kwargs.get("run_count", 3)
        self.multobj_flag = kwargs.get("multobj_flag", 0)
        self.store_ref = kwargs.get("store_ref", 0)
        self.benchmark_flag = kwargs.get("benchmark_flag", False)
        self.workspace_root = self.workspace.directory
        self.project_name = self.workspace.design
        self.tech = kwargs.get("tech", workspace.configs.workspace.process_node)
        self.step = step

        self.params = None
        self._search_space = None

    def _create_search_space(self):
        #create search space
        search_space = {}
        
        # placement parameters search space
        search_space["placement_target_density"] = {
            "_type": "uniform",
            "_value": [0.3, 0.8]
        }
        search_space["placement_init_wirelength_coef"] = {
            "_type": "uniform", 
            "_value": [0.1, 0.5]
        }
        search_space["placement_min_wirelength_force_bar"] = {
            "_type": "uniform",
            "_value": [-500.0, -50.0]
        }
        search_space["placement_max_phi_coef"] = {
            "_type": "uniform",
            "_value": [0.75, 1.25]
        }
        search_space["placement_max_backtrack"] = {
            "_type": "uniform",
            "_value": [5, 50]
        }
        search_space["placement_init_density_penalty"] = {
            "_type": "uniform",
            "_value": [0.0, 0.001]
        }
        search_space["placement_target_overflow"] = {
            "_type": "uniform",
            "_value": [0.0, 0.2]
        }
        search_space["placement_initial_prev_coordi_update_coef"] = {
            "_type": "uniform",
            "_value": [50.0, 1000.0]
        }
        search_space["placement_min_precondition"] = {
            "_type": "uniform",
            "_value": [1.0, 10.0]
        }
        search_space["placement_min_phi_coef"] = {
            "_type": "uniform",
            "_value": [0.75, 1.25]
        }
        
        return search_space

    def objective(self, trial):
        return self.start(trial=trial)

    def run_nni(
        self,
        algorithm="TPE",
        direction="minimize",
        search_space=dict(),
        concurrency=1,
        max_trial_number=2000,
        flows=None,
    ):
        from nni.experiment import Experiment
        import random

        experiment = Experiment("local")
        port = 8088
        try:
            arg_setting = ""
            processed_keys = set()

            for k, v in vars(self).items():

                if k.startswith("_") or k in ["workspace", "params", "search_space"]:
                    continue

                if k in processed_keys:
                    continue

                if k == "step" and hasattr(v, "name"):
                    step_name = v.name
                    arg_setting += f" --{k} {step_name}"
                    processed_keys.add(k)
                    continue

                if isinstance(v, bool):
                    if v:
                        arg_setting += f" --{k}"
                elif v is not None:
                    arg_setting += f" --{k} {v}"
                processed_keys.add(k)

            trial_command = f"python model.py {arg_setting}"

            experiment.config.trial_command = trial_command
            experiment.config.trial_code_directory = os.path.dirname(__file__)
            experiment.config.search_space = search_space

            experiment.config.tuner.name = algorithm
            experiment.config.tuner.class_args["optimize_mode"] = direction

            experiment.config.max_trial_number = self.run_count
            experiment.config.trial_concurrency = self.sweep_worker_num
            experiment.run(port)

        except Exception as e:
            print(f"Change to ohter port. {e}")
            port = random.Random().randint(3000, 60036)
            experiment.run(port)

    def start(self, optimize=DSEMethod.NNI, eda_tool="iEDA", step=None):
        if step is not None:
            self.step = step
            
        self.params = self.workspace.configs.parameters

        if hasattr(self.params, 'num_threads'):
            os.environ["OMP_NUM_THREADS"] = "%d" % (self.params.num_threads)

        if optimize == DSEMethod.NNI:
            self._search_space = self._create_search_space()
            print("DSE Search Space:", self._search_space)
            
            method = NNIOptimization(
                args=None,
                workspace=self.workspace,
                parameter=self.params,
                step=self.step,
            )
            method._search_config = self._search_space
            self.run_nni(search_space=self._search_space, flows=None)
        elif optimize == DSEMethod.OPTUNA:
            pass
