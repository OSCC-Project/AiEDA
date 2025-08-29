#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   dse_facade.py
@Time    :   2024-08-29 10:54:34
@Author  :   SivanLaai
@Version :   1.0
@Contact :   lyhhap@163.com
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

from aieda.flows.base import DbFlow
from aieda.data.database.enum import DSEMethod
from aieda.workspace.workspace import Workspace
from aieda.ai.design_parameter_optimization.config import ConfigManagement
from aieda.ai.design_parameter_optimization.model import NNIOptimization


class DSEFacade:
    def __init__(self, workspace_root=None, project_name=None, step=None, **kwargs):
        self.workspace = Workspace(workspace_root, project_name)

        self.experiment_name = kwargs.get("experiment_name")
        self.scenario_name = kwargs.get("scenario_name", "test_sweep")
        self.seed = kwargs.get("seed", 0)
        self.sweep_worker_num = kwargs.get("sweep_worker_num", 1)
        self.run_count = kwargs.get("run_count", 3)
        self.multobj_flag = kwargs.get("multobj_flag", 0)
        self.store_ref = kwargs.get("store_ref", 0)
        self.benchmark_flag = kwargs.get("benchmark_flag", False)
        self.workspace_root = workspace_root
        self.project_name = project_name
        self.tech = kwargs.get("tech", "sky130")
        self.step = step

        self.params = None
        self._search_space = None

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
        config_manage = ConfigManagement(
            workspace=self.workspace, eda_tool=eda_tool, step=self.step
        )
        dir_workspace = config_manage.getWorkspacePath()
        self.params = config_manage.getParameters()

        os.environ["OMP_NUM_THREADS"] = "%d" % (self.params.num_threads)

        if optimize == DSEMethod.NNI:
            method = NNIOptimization(
                args=None,
                workspace=dir_workspace,
                parameter=self.params,
                step=self.step,
            )
            self._search_space = method._search_config
            print(self._search_space)
            self.run_nni(search_space=self._search_space, flows=None)
        elif optimize == DSEMethod.OPTUNA:
            pass
