#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import os
from multiprocessing import Process

def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

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
from aieda.ai.DSE.arguments import Arguements
from aieda.ai.DSE.config import ConfigManagement

import nni
import numpy as np
import time
import logging
import json

class AbstractOptimizationMethod(metaclass=ABCMeta):
    _parameter = None
    _search_config = None
    def __init__(self, args, workspace, parameter, algorithm="TPE", goal="minimize", step=DbFlow.FlowStep.place):
        self._method = algorithm
        self._goal = goal
        self._args = args
        self._workspace = workspace
        self._parameter = parameter
        self._step = step
        self._best_metric = float("inf")
        self.initOptimization()

    def getFeatureMetrics(self, data, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=None):
        hpwl, wns, tns, freq = self.getPlaceResults()
        
        place_data = dict()
        place_data["hpwl"] = hpwl
        place_data["wns"] = wns
        place_data["tns"] = tns
        place_data["freq"] = freq
        
        if len(place_data):
            data["place"] = place_data
        
        return data

    def getIEDAIO(self, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=FeatureOption.eval):
        try:

            feature = IEDAIO(
                workspace=self._workspace,  
                flow=DbFlow(eda_tool=eda_tool, step=step)
            )
            return feature
        except Exception as e:
            return None
    
    def getFeatureDB(self, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=FeatureOption.eval):
        try:
            feature = IEDAIO(
                workspace=self._workspace,  
                flow=DbFlow(eda_tool=eda_tool, step=step)
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
        self._parameter._search_space = self._parameter.getSearchSpace()
        self.formatSweepConfig()

    @abstractmethod
    def formatSweepConfig(self):
        raise NotImplementedError
    
    @abstractmethod
    def loadParams(self, Parameter):
        raise NotImplementedError

    @abstractmethod
    def runOptimization(self, step=DbFlow.FlowStep.place, option=FeatureOption.tools, metrics={"hpwl": 1.0, "tns": 0.0, "wns": 0.0}, pre_step=DbFlow.FlowStep. fixFanout, tool="iEDA"):
        raise NotImplementedError

    @abstractmethod 
    def getNextParams(self):
       raise NotImplementedError
    
    def getPlaceResults(self):
        hpwl,wns,tns,freq = None,None,None,None
        try:
            workspace = self._workspace
            output_dir = os.path.join(workspace, "output/iEDA/data/pl/report/summary_report.txt")
            out_lines = open(output_dir).readlines()
            for i in range(len(out_lines)):
                line = out_lines[i]
                if "Total HPWL" in line:
                    hpwl = line.replace(" ", "").split("|")[-2]
                elif "Late TNS".lower() in line.lower() and "|" in out_lines[i+2]:
                    new_line = out_lines[i+2]
                    datas = new_line.replace(" ", "").split("|")
                    wns = datas[-3]
                    tns = datas[-2]
            freq_dir = os.path.join(workspace, "output/iEDA/data/pl/log/info_ipl_glog.INFO") 
            lines = open(freq_dir).readlines()
            for i in range(len(lines)):
                line = lines[i]
                if "Freq(MHz)" in line and "|" in lines[i+2]:
                    next_line = lines[i+2]
                    datas = next_line.strip().replace(" ", "").split("|")
                    freq = datas[-2]
                    if wns is None:
                        pass
                    if tns is None:
                        pass
                    break
        except Exception as e:
            print(e)
        return float(hpwl),float(wns),float(tns),float(freq)
    
    def getOperationEngine(self, step, tool, pre_step):
        dir_workspace = self._workspace
        project_name = self._args.project_name
        engine = None
        eda_tool = "iEDA"

        if step == DbFlow.FlowStep.floorplan:
            pass
        
        if step == DbFlow.FlowStep.fixFanout:
            pass
        if step == DbFlow.FlowStep.place:

            workspace = Workspace(dir_workspace, project_name)
            input_def = f"{dir_workspace}/output/iEDA/result/{project_name}_fixFanout.def.gz"
            input_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_fixFanout.v.gz"
            output_def = f"{dir_workspace}/output/iEDA/result/{project_name}_place.def.gz"
            output_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_place.v.gz"
            flow = DbFlow(
                eda_tool=eda_tool,
                step=step,
                input_def=input_def,
                input_verilog=input_verilog,
                output_def=output_def,
                output_verilog=output_verilog
            )

            engine = IEDAPlacement(workspace=workspace, flow=flow)
    
        if step == DbFlow.FlowStep.cts:
            engine = IEDACts(dir_workspace = dir_workspace,
                             input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                             input_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                             eda_tool = tool,
                             pre_step = DbFlow(eda_tool = eda_tool,step = pre_step),
                             step = DbFlow(eda_tool = eda_tool,step = step))
            
        if step == DbFlow.FlowStep.optDrv:
            return DbFlow.FlowStep.optDrv
            
        if step == DbFlow.FlowStep.optHold:
            return DbFlow.FlowStep.optHold
            
        if step == DbFlow.FlowStep.optSetup:
            return DbFlow.FlowStep.optSetup
            
        if step == DbFlow.FlowStep.legalization:
            return DbFlow.FlowStep.legalization
            
        if step == DbFlow.FlowStep.route:
            engine = IEDARouting(dir_workspace = dir_workspace,
                             input_def=f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.def.gz",
                             input_verilog = f"{dir_workspace}/output/iEDA/result/{project_name}_{pre_step.value}.v.gz",
                             eda_tool = tool,
                             pre_step = DbFlow(eda_tool = eda_tool,step = pre_step),
                             step = DbFlow(eda_tool = eda_tool,step = step))
            
        if step == DbFlow.FlowStep.filler:
            return DbFlow.FlowStep.filler
            
        if step == DbFlow.FlowStep.gds:
            return DbFlow.FlowStep.gds
        
        if step == DbFlow.FlowStep.drc:
            return DbFlow.FlowStep.drc

        return engine

        
class NNIOptimization(AbstractOptimizationMethod):
    _parameter = None
    _search_config = dict()

    def __init__(self, args, workspace, parameter, algorithm="TPE", goal="minimize", step=DbFlow.FlowStep.place):

        super().__init__(args, workspace, parameter, algorithm, goal, step)
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

        hpwl,wns,tns,freq = self.getPlaceResults()
        messages = ""
        metric = 0.0

        hpwl_ref = metrics.get("hpwl", 1.0)
        messages += f"hpwl: {hpwl}, "
        metric += hpwl/hpwl_ref

        messages += f"wns: {wns}, "
        wns_ref = metrics.get("wns", 0.0)
        metric += np.exp(wns_ref)/np.exp(wns)

        messages += f"tns: {tns}, "
        tns_ref = metrics.get("tns", 0.0)
        metric += np.exp(tns_ref)/np.exp(tns)
        
        results["place_hpwl"] = hpwl
        results["place_wns"] = wns
        results["place_tns"] = tns
        results["place_freq"] = freq
        messages += f"place_hpwl: {hpwl}, place_wns: {wns}, place_tns: {tns}, place_freq: {freq}\n"
        logging.info(messages)
        return metric
    
    def logRouteMetrics(self, metrics, results):
        feature = self.getFeatureDB(eda_tool="iEDA", step=DbFlow.FlowStep.route, option=FeatureOption.tools)
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
                    metric += route_wl/metrics["route_wl"]
                if "route_tns" in metrics:
                    metric += np.exp(metrics["route_tns"])/np.exp(route_tns)
                if "route_wns" in metrics:
                    metric += np.exp(metrics["route_wns"])/np.exp(route_wns)
                if "route_freq" in metrics:
                    metric += route_freq/metrics["route_freq"]
        logging.info(messages)
        return metric
        
    def logFeature(self, metrics, step):
        metric = 0.0
        results = dict()
          
        if step == DbFlow.FlowStep.place:
            metric = self.logPlaceMetrics(metrics, results)
        else:
            self.logPlaceMetrics(metrics, results)
            metric = self.logRouteMetrics(metrics, results)
        if metric < self._best_metric:
            flow_list = self.config_manage.getFlowList()
            best_config_paths = self.config_manage.getBestConfigPathList()
            self._parameter.dumpOriginalConfig(best_config_paths, flow_list)
        nni.report_final_result(metric)

    def GenerateDataset(self, params, step=DbFlow.FlowStep.place, tool="iEDA"):
        # if step==DbFlow.FlowStep.place:
        data = dict()
        data["params"] = params
        data = self.getFeatureMetrics(data, eda_tool="iEDA", step=DbFlow.FlowStep.place, option=None)
        # print(data)
        filepath = f"{self._args.result_dir}/benchmark/{self._args.tech}"
        filename = f"{self._args.result_dir}/benchmark/{self._args.tech}/{self._args.project_name}_{self._step.value}.jsonl"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        # print(filename)
        with open(filename, "a+") as bf:
            bf.write(json.dumps(data))
            bf.write("\n")
            bf.flush()
    
    def runTask(self, algorithm="TPE", goal="minimize", step=DbFlow.FlowStep.place, tool="iEDA", pre_step=DbFlow.FlowStep.fixFanout):
        dir_workspace = self._workspace
        project_name = self._args.project_name
        engine = self.getOperationEngine(step, tool, pre_step)
        
        if engine:
            if hasattr(engine, '__run_flow__'):
                engine.__run_flow__()
            elif hasattr(engine, 'run_placement'):
                engine.run_placement()
            elif hasattr(engine, 'run'):
                engine.run()
            else:
                print(f" 引擎没有找到可用的执行方法")

        else:
            print(f"Engine creation failed")

    def runOptimization(self, step=DbFlow.FlowStep.place, option=FeatureOption.tools, metrics={"hpwl": 1.0, "tns": 0.0, "wns": 0.0}, pre_step=DbFlow.FlowStep.cts, tool="iEDA"):
        tt = time.time()
        next_params = self.getNextParams()
        self.config_manage = ConfigManagement(self._args, tool)
        config_paths = self.config_manage.getConfigPathList()
        self._parameter.updateParams(next_params)
        flow_list = self.config_manage.getFlowList()
        self._parameter.dumpOriginalConfig(config_paths, flow_list)
        for db_flow in flow_list:
            step = db_flow.step
            pre_step = DbFlow.FlowStep. fixFanout
            tool = db_flow.eda_tool
            p = Process(target=self.runTask, args=("bayes", "minimize", step, tool, pre_step)) #实例化进程对象
            p.start()
            p.join()
        self.logFeature(metrics, step)
        self.GenerateDataset(next_params, step, tool)
        total_time = time.time() - tt
        logging.info("task takes %.3f seconds" % (total_time))

if __name__ == "__main__":
    
    tool = os.environ.get('eda_tool', "iEDA")
    args = Arguements.parse(sys.argv[1:])
    parameter = os.environ.get('eda_tool', "iEDA")
    config_manage = ConfigManagement(args, tool)
    step = config_manage.getStep()
    dir_workspace = config_manage.getWorkspacePath()
    eda_tool = "iEDA"

    params = config_manage.getParameters()

    method = NNIOptimization(args, dir_workspace, params, algorithm="TPE", goal="maximize", step=step)
    method.runOptimization(tool=eda_tool, step=step, pre_step=DbFlow.FlowStep.place, metrics={})