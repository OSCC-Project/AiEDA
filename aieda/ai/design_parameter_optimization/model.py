
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import os
from multiprocessing import Process
import nni
import numpy as np
import time
import logging
import json
import argparse
import numpy as np
import traceback
def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..", "..")
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


import atexit

setup_paths()
from enum import Enum
from abc import abstractmethod, ABCMeta

from aieda.flows.base import DbFlow
from aieda.eda.iEDA.placement import IEDAPlacement
from aieda.eda.iEDA.routing import IEDARouting
from aieda.eda.iEDA.cts import IEDACts
from aieda.eda.iEDA.io import IEDAIO
from aieda.data.database.enum import FeatureOption
from aieda.workspace.workspace import Workspace
from aieda.data.database.parameters import EDAParameters


class AbstractOptimizationMethod(metaclass=ABCMeta):
    _parameter = None
    _search_config = None

    def __init__(
        self,
        args,
        workspace : Workspace,
        parameter,
        algorithm="TPE",
        goal="minimize",
        step=DbFlow.FlowStep.place,
    ):
        self._method = algorithm
        self._goal = goal
        self._workspace = workspace
        self._parameter = parameter
        self._step = step
        self._project_name = workspace.design
        self._run_count = 100
        self._result_dir = workspace.paths_table.output_dir
        self._tech = workspace.configs.workspace.process_node
        self.initOptimization()

    def getFeatureMetrics(
        self, data, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=None
    ):
        hpwl = self.getPlaceResults()

        place_data = dict()
        place_data["hpwl"] = hpwl

        if len(place_data):
            data["place"] = place_data
        return data

    def getIEDAIO(
        self, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=FeatureOption.eval
    ):
        try:

            feature = IEDAIO(
                workspace=self._workspace, flow=DbFlow(eda_tool=eda_tool, step=step)
            )
            return feature
        except Exception as e:
            return None

    def getFeatureDB(
        self, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=FeatureOption.eval
    ):
        try:
            feature = IEDAIO(
                workspace=self._workspace, flow=DbFlow(eda_tool=eda_tool, step=step)
            )
            feature.generate(reload=True)
            db = feature.get_db()
            return db
        except Exception as e:
            return None

    @abstractmethod
    def logFeature(self, metrics, step):
        raise NotImplementedError

    def setParameter(self, Parameter):
        self._parameter = Parameter

    def initOptimization(self):
        if hasattr(self._parameter, 'getSearchSpace'):
            self._parameter._search_space = self._parameter.getSearchSpace()
        elif hasattr(self, '_search_config'):
            self._parameter._search_space = self._search_config
        self.formatSweepConfig()

    @abstractmethod
    def formatSweepConfig(self):
        raise NotImplementedError

    @abstractmethod
    def loadParams(self, Parameter):
        raise NotImplementedError

    @abstractmethod
    def runOptimization(
        self,
        step=DbFlow.FlowStep.place,
        option=FeatureOption.tools,
        metrics={"hpwl": 1.0, "tns": -20.0, "wns": -0.55},
        pre_step=DbFlow.FlowStep.fixFanout,
        tool="iEDA",
    ):
        raise NotImplementedError

    @abstractmethod
    def getNextParams(self):
        raise NotImplementedError

    def getPlaceResults(self):
        hpwl = None
        try:
            workspace: Workspace = self._workspace
            output_dir = os.path.join(
                workspace.paths_table.output_dir,
                "iEDA/data/pl/report/summary_report.txt",
            )
            out_lines = open(output_dir).readlines()
            for line in out_lines:
                if "Total HPWL" in line:
                    hpwl = line.replace(" ", "").split("|")[-2]
                    break

        except Exception as e:
            print(f"Error parsing HPWL: {e}")
            hpwl = "0.0"
            
        return float(hpwl)

    def getOperationEngine(self, step, tool, pre_step):
        workspace_obj: Workspace = self._workspace
        dir_workspace = workspace_obj.directory
        project_name = self._project_name
        engine = None
        eda_tool = "iEDA"

        if step == DbFlow.FlowStep.place:
            workspace = workspace_obj
            input_def = (
                f"{dir_workspace}/output/iEDA/result/{project_name}_fixFanout.def.gz"
            )
            input_verilog = (
                f"{dir_workspace}/output/iEDA/result/{project_name}_fixFanout.v.gz"
            )
            output_def = (
                f"{dir_workspace}/output/iEDA/result/{project_name}_place.def.gz"
            )
            output_verilog = (
                f"{dir_workspace}/output/iEDA/result/{project_name}_place.v.gz"
            )

            flow = DbFlow(
                eda_tool=eda_tool,
                step=step,
                input_def=input_def,
                input_verilog=input_verilog,
                output_def=output_def,
                output_verilog=output_verilog,
            )

            engine = IEDAPlacement(workspace=workspace, flow=flow)

        if step == DbFlow.FlowStep.cts:
            engine = IEDACts(
                dir_workspace=dir_workspace,
                input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                input_verilog=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                eda_tool=tool,
                pre_step=DbFlow(eda_tool=eda_tool, step=pre_step),
                step=DbFlow(eda_tool=eda_tool, step=step),
            )

        if step == DbFlow.FlowStep.legalization:
            return DbFlow.FlowStep.legalization

        if step == DbFlow.FlowStep.route:
            engine = IEDARouting(
                dir_workspace=dir_workspace,
                input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                input_verilog=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                eda_tool=tool,
                pre_step=DbFlow(eda_tool=eda_tool, step=pre_step),
                step=DbFlow(eda_tool=eda_tool, step=step),
            )

        return engine


class NNIOptimization(AbstractOptimizationMethod):
    _parameter = None
    _search_config = dict()

    def __init__(
        self,
        args,
        workspace : Workspace,
        parameter,
        algorithm="TPE",
        goal="minimize",
        step=DbFlow.FlowStep.place,
    ):

        super().__init__(args, workspace, parameter, algorithm, goal, step)
        self.trial_times = []
        self.trial_start_time = None
        
    def getNextParams(self):
        return nni.get_next_parameter()

    def loadParams(self, Parameter):
        self._parameter = Parameter

    def initOptimization(self):
        super().initOptimization()

    def formatSweepConfig(self):
        nni_search_space = self._parameter._search_space
        for key in nni_search_space:
            param = nni_search_space[key]
            if "distribution" in param:
                self._search_config[key] = {
                    "_type": param["distribution"],
                    "_value": [param["min"], param["max"]],
                }
            else:
                self._search_config[key] = {
                    "_type": "choice",
                    "_value": param["values"],
                }

    def logPlaceMetrics(self, metrics, results):

        hpwl = self.getPlaceResults()
        messages = ""
        metric = 0.0

        # 只优化 HPWL
        hpwl_ref = metrics.get("hpwl", 1.0)
        hpwl_contrib = hpwl / hpwl_ref
        messages += f"hpwl: {hpwl}, "
        metric = hpwl_contrib 

        results["place_hpwl"] = hpwl
            
        # print the contributions of each metric
        messages += f"place_hpwl: {hpwl}\n"
        messages += f"Contributions - HPWL: {hpwl_contrib:.6f}, Total: {metric:.6f}\n"
        logging.info(messages)
        return metric

    def logRouteMetrics(self, metrics, results):
        feature = self.getFeatureDB(
            eda_tool="iEDA", step=DbFlow.FlowStep.route, option=FeatureOption.tools
        )
        messages = ""
        metric = 0.0
        if feature.routing_summary:
            if feature.routing_summary.dr_summary:
                route_data = feature.routing_summary.dr_summary.summary[-1][-1]
                print(route_data)
                route_wl = route_data.total_wire_length
                clock = route_data.clocks_timing[-1]
                route_wns = clock.setup_wns
                route_tns = clock.setup_tns
                route_freq = clock.suggest_freq
                messages += f"route_wl: {route_wl}, route_tns: {route_tns}, route_wns: {route_wns}, route_freq: {route_freq}."

                metric += route_freq
                results["route_wl"] = route_wl
                results["route_tns"] = route_tns
                results["route_wns"] = route_wns
                results["route_freq"] = route_freq
                if "route_wl" in metrics:
                    metric += route_wl / metrics["route_wl"]
                if "route_tns" in metrics:
                    metric += np.exp(metrics["route_tns"]) / np.exp(route_tns)
                if "route_wns" in metrics:
                    metric += np.exp(metrics["route_wns"]) / np.exp(route_wns)
                if "route_freq" in metrics:
                    metric += route_freq / metrics["route_freq"]
        logging.info(messages)
        return metric

    def logFeature(self, metrics, step):
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # best_metric_file = os.path.join(current_dir, "best_metric.txt")
        best_metric_file = "{}/best_metric.txt".format(self._workspace.paths_table.analysis_dir)
        try:
            with open(best_metric_file, "r") as f:
                current_best = float(f.read().strip())
        except:
            current_best = float("inf")
        metric = 0.0
        results = dict()
        if step == DbFlow.FlowStep.place:
            metric = self.logPlaceMetrics(metrics, results)
        else:
            self.logPlaceMetrics(metrics, results)
            metric = self.logRouteMetrics(metrics, results)

        if metric < current_best:
            with open(best_metric_file, "w") as f:
                f.write(str(metric))

            best_params_file = "{}/best_parameters.json".format(self._workspace.paths_table.analysis_dir)
            with open(best_params_file, "w") as f:
                json.dump(self._workspace.configs.parameters.__dict__, f, indent=2)
            
            print(f"New best metric found: {metric}")
        else:
            print(f"There is no better metric that {metric} >= {current_best}")

        self.checkAndSyncBestToDefault()
        nni.report_final_result(metric)
        return metric

    def checkAndSyncBestToDefault(self):
        try:
            trial_number = os.environ.get("NNI_TRIAL_SEQ_ID", "")
            if trial_number:
                current_trial = int(trial_number) + 1
                max_trial_num = self._run_count
                if current_trial >= max_trial_num:
                    best_params_file = "{}/best_parameters.json".format(self._workspace.paths_table.analysis_dir)
                    if os.path.exists(best_params_file):
                        with open(best_params_file, "r") as f:
                            best_params = json.load(f)
                        
                        
                        best_eda_params = EDAParameters()
                        for key, value in best_params.items():
                            if hasattr(best_eda_params, key):
                                setattr(best_eda_params, key, value)
                        
                        self._workspace.update_parameters(best_eda_params)
                        print("The best parameter has been restored to workspace")
                    
                    print(f"DSE optimization completed after {max_trial_num} trials")
            else:
                print(f"The trial number is not set, skip trial check")
        except Exception as e:
            print(f"Error: check trial status: {e}")

    def GenerateDataset(self, params, step=DbFlow.FlowStep.place, tool="iEDA",metric=None):
        data = dict()
        data["params"] = params
        data = self.getFeatureMetrics(
            data, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=None
        )
        if metric is not None:
            data["metric"] = metric
        else:
            metrics = {"hpwl": 1.0, "tns": -20.0, "wns": -0.55}
            results = {}
            metric = self.logPlaceMetrics(metrics, results)
            data["metric"] = metric
        print(f"Trial metric: {data['metric']:.6f}")
        filepath = f"{self._result_dir}/benchmark/{self._tech}"
        filename = f"{self._result_dir}/benchmark/{self._tech}/{self._project_name}_{self._step.value}.jsonl"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(filename, "a+") as bf:
            bf.write(json.dumps(data))
            bf.write("\n")
            bf.flush()

    def runTask(
        self,
        algorithm="TPE",
        goal="minimize",
        step=DbFlow.FlowStep.place,
        tool="iEDA",
        pre_step=DbFlow.FlowStep.fixFanout,
    ):
        engine = self.getOperationEngine(step, tool, pre_step)
        if engine:
            if hasattr(engine, "_run_flow"):
                engine._run_flow()
            elif hasattr(engine, "_run_placement"):
                engine._run_placement()
            elif hasattr(engine, "run"):
                engine.run()
            else:
                print(f"NO_RUN")

        else:
            print(f"Engine creation failed")

    def _update_workspace_parameters(self, next_params):
        

        new_params = EDAParameters()

        for param_name, param_value in next_params.items():
            if hasattr(new_params, param_name):
                setattr(new_params, param_name, param_value)
                print(f"Updated {param_name} = {param_value}")

        self._workspace.update_parameters(new_params)

    def runOptimization(
        self,
        step=DbFlow.FlowStep.place,
        option=FeatureOption.tools,
        metrics={"hpwl": 1.0, "tns": -20.0, "wns": -0.55},
        pre_step=DbFlow.FlowStep.fixFanout,
        tool="iEDA",
    ):
        trial_start = time.time()
        tt = time.time()
        next_params = self.getNextParams()

        self._update_workspace_parameters(next_params)

        self.runTask(tool=tool, step=step, pre_step=pre_step)
        
        metric = self.logFeature(metrics, step)
        self.GenerateDataset(next_params, step, tool, metric)
        trial_time = time.time() - trial_start
        self.trial_times.append(trial_time)
        total_time = time.time() - tt
        logging.info("task takes %.3f seconds" % (total_time))
        logging.info("trial takes %.3f seconds" % (trial_time))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace_root", type=str, required=True)
    parser.add_argument("--project_name", type=str, required=True)
    parser.add_argument("--step", type=str, required=True)
    parser.add_argument("--eda_tool", type=str, default="iEDA")
    parser.add_argument("--run_count", type=int, default=3)
    parser.add_argument("--tech", type=str, default="sky130")

    args, unknown = parser.parse_known_args()
    workspace_root = args.workspace_root
    project_name = args.project_name
    step = args.step
    eda_tool = args.eda_tool

    try:
        workspace = Workspace(workspace_root, project_name)

        params = workspace.configs.parameters

        if isinstance(step, str):
            try:
                step_enum = getattr(DbFlow.FlowStep, step)
            except AttributeError:
                step_enum = DbFlow.FlowStep.place
        else:
            step_enum = step

        method = NNIOptimization(
            args=None,
            workspace=workspace,
            parameter=params,
            algorithm="TPE",
            goal="minimize",
            step=step_enum,
        )
        method._project_name = project_name
        method._run_count = args.run_count
        method._tech = args.tech

        method.runOptimization(
            tool=eda_tool,
            step=step_enum,
            pre_step=DbFlow.FlowStep.fixFanout,
            metrics={"hpwl": 1.0, "tns": -20.0, "wns": -0.55},
        )

    except Exception as e:
        traceback.print_exc()

        try:
            nni.get_next_parameter()
        except:
            pass
        nni.report_final_result(0.0)


if __name__ == "__main__":
    main()
