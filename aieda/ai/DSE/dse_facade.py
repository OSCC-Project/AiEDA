#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dse_facade.py
@Time    :   2024-08-29 10:54:34
@Author  :   SivanLaai
@Version :   1.0
@Contact :   lyhhap@163.com
@Desc    :   dse facade
'''
import sys
import os
import time
import logging
import datetime
import json
def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

setup_paths()

from aieda.flows.base import DbFlow
from aieda.data.database.enum import DSEMethod
from aieda.ai.DSE.arguments import Arguements
from aieda.ai.DSE.config import ConfigManagement
from aieda.ai.DSE.model import NNIOptimization


class DSEFacade:
    params = None
    def objective(self, trial):
        return self.start(trial=trial)

    def run_nni(self, algorithm="TPE", direction="minimize", search_space=dict(), concurrency=1, max_trial_number=2000, flows=None):
        from nni.experiment import Experiment
        import random
        experiment = Experiment('local')
        port = 8088

        try:
            arg_setting = ""
            for k,v in vars(self.args).items():
               if isinstance(v, bool):
                   if v:
                       arg_setting += f" --{k}"
               elif v is not None:
                   arg_setting += f" --{k} {v}"
            trial_command = f'python model.py {arg_setting}'
            print(trial_command)
            experiment.config.trial_command = trial_command 
            experiment.config.trial_code_directory = os.path.dirname(__file__)
            experiment.config.search_space = search_space

            experiment.config.tuner.name = algorithm
            experiment.config.tuner.class_args['optimize_mode'] = direction

            experiment.config.max_trial_number = self.args.run_count
            experiment.config.trial_concurrency = self.args.sweep_worker_num
            experiment.run(port)
        except Exception as e:
            print(e)
            port = random.Random().randint(3000, 60036)
            experiment.run(port)

    def start(self, optimize=DSEMethod.NNI, eda_tool="iEDA", step=DbFlow.FlowStep.place):

        self.args = Arguements.parse(sys.argv[1:])
        config_manage = ConfigManagement(self.args, eda_tool)
        self.step = config_manage.getStep()
        dir_workspace = config_manage.getWorkspacePath()

        self.params = config_manage.getParameters()

        os.environ["OMP_NUM_THREADS"] = "%d" % (self.params.num_threads)


        if optimize==DSEMethod.NNI:
            method = NNIOptimization(self.args, dir_workspace, self.params, self.step)
            self._search_space = method._search_config
            print(self._search_space)
            self.run_nni(search_space=self._search_space, flows=self.args.flows)
        elif optimize==DSEMethod.OPTUNA:
            pass

if __name__ == "__main__":
    auto = DSEFacade(None) 
    auto.start(optimize=DSEMethod.NNI)