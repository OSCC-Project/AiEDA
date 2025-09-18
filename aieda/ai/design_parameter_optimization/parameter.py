import sys
import os

from abc import abstractmethod, ABCMeta
import json
from collections import OrderedDict


def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..", "..")
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


setup_paths()

from aieda.flows.base import DbFlow


class AbstractParameter(metaclass=ABCMeta):
    _search_space = None
    config = {}
    next_params = {}

    def __init__(
        self, filename="./config/iEDA/default.json", step=DbFlow.FlowStep.place
    ):
        """
        @brief initialization
        """
        filename = os.path.join(os.path.dirname(__file__), filename)
        self._step = step
        self.__dict__ = {}
        self.initData(filename, step)
        self.formatSearchSpace(step)

    @abstractmethod
    def dumpPlaceFlowConfig(self, filename, config=None, step=DbFlow.FlowStep.place):
        raise NotImplementedError

    @abstractmethod
    def dumpCTSFlowConfig(self, filename, config=None, step=DbFlow.FlowStep.cts):
        raise NotImplementedError

    @abstractmethod
    def dumpRouteFlowConfig(self, filename, config=None, step=DbFlow.FlowStep.route):
        raise NotImplementedError

    @abstractmethod
    def dumpFullFlowConfig(self, filename, config=None, flow_list=None):
        raise NotImplementedError

    def dumpConfigByFlowStep(self, filename, flow_step):
        if flow_step == DbFlow.FlowStep.place:
            self.dumpPlaceFlowConfig(filename)
        elif flow_step == DbFlow.FlowStep.cts:
            self.dumpCTSFlowConfig(filename)
        else:
            pass

    @abstractmethod
    def formatSearchSpace(self, step=None):
        raise NotImplementedError

    def getSearchSpace(self, step=None):
        return self._search_space

    @abstractmethod
    def dumpOriginalConfig(self, filename, step=None, flow_list=None):
        raise NotImplementedError

    def initData(self, filename, step):
        params_dict = {}
        with open(filename, "r") as f:
            params_dict = json.load(f, object_pairs_hook=OrderedDict)
        self.__dict__ = dict()
        for param_step in params_dict:
            step_params_dict = params_dict[param_step]
            for key, value in step_params_dict.items():
                if "default" in value:
                    if isinstance(value["default"], dict):
                        self.__dict__[key] = dict()
                        for k, v in value["default"].items():
                            self.__dict__[key][k] = v
                    else:
                        self.__dict__[key] = value["default"]
                else:
                    self.__dict__[key] = None
        self.__dict__["params_dict"] = params_dict

    def load_list(self, path_list):
        for step, filepath in path_list.items():
            try:
                with open(filepath, "r") as f:
                    self.config[step] = json.load(f)
            except Exception as e:
                print(f"WARNING: load config failed {step}: {e}")

        print(f"DEBUG: load {len(self.config)} configs")

    def updateParams(self, new_param_dict):
        self.next_params = new_param_dict
        print("update self.next_params:", self.next_params)


class iEDAParameter(AbstractParameter):

    def __init__(
        self, filename="./config/iEDA/default.json", step=DbFlow.FlowStep.place
    ):
        self.param_path = os.path.join(os.path.dirname(__file__), filename)
        super().__init__(filename, step)

    def formatSearchSpace(self, step):
        search_path = os.path.join(
            os.path.dirname(__file__), "config/iEDA/search_space.json"
        )
        with open(search_path, "r") as f:
            self.params_dict = json.load(f)
            if step != DbFlow.FlowStep.full_flow:
                self._search_space = self.params_dict.get(step.value.lower(), {})
            else:
                self._search_space = dict()
                for k, v in self.params_dict.items():
                    self._search_space.update(v)

    def getCurrUpdateParams(self, step):
        key_step = step.value.lower()
        print("next_params:", self.next_params)
        curr_param_keys = self.params_dict.get(key_step, {})
        print("curr_param_keys:", curr_param_keys)
        update_params = {
            k: v for k, v in self.next_params.items() if k in curr_param_keys
        }
        print("update_params:", update_params)
        return update_params

    def dumpPlaceFlowConfig(self, filename, config=None, step=DbFlow.FlowStep.place):
        key_step = step.value.lower()

        if key_step not in self.config:
            return
        config = self.config[key_step]
        print("dumpPlaceFlowConfig", config)
        update_params = self.getCurrUpdateParams(step)
        for k in update_params:
            if k in config["PL"]["GP"]["Wirelength"]:
                config["PL"]["GP"]["Wirelength"][k] = update_params[k]
            if k in config["PL"]["GP"]["Density"]:
                config["PL"]["GP"]["Density"][k] = update_params[k]
            if k in config["PL"]["GP"]["Nesterov"]:
                config["PL"]["GP"]["Nesterov"][k] = update_params[k]
        
        print("dumpPlaceFlowConfig:", config)
        print("filename:", filename)
        with open(filename, "w") as f:
            json.dump(config, f, indent=4)

    def dumpCTSFlowConfig(self, filename, config=None, step=DbFlow.FlowStep.cts):
        key_step = step.value.lower()
        if key_step not in self.config:
            return
        config = self.config[key_step]
        update_params = self.getCurrUpdateParams(step)
        curr_search_space = self.params_dict.get(key_step, {})
        for param in curr_search_space:
            param_type = curr_search_space[param].get("type", None)
            if param_type == "str" and param in update_params:
                config[param] = str(update_params[param])
        with open(filename, "w") as f:
            json.dump(config, f, indent=4)

    def dumpRouteFlowConfig(self, filename, config=None, step=DbFlow.FlowStep.route):
        pass

    def dumpFullFlowConfig(self, filename, config=None, flow_list=None):
        for flow_step in flow_list:
            self.dumpConfigByFlowStep(filename, flow_step)

    def dumpOriginalConfig(self, config_paths=None, flow_list=None, filename=None):
        """
        @brief dump original config parameters to json file
        """
        for flow in flow_list:
            step = flow.step
            filename = config_paths[step.value.lower()]
            print("iEDAParameter: dumpOriginalConfig", step, filename)
            self.dumpConfigByFlowStep(filename, step)


if __name__ == "__main__":
    inn = iEDAParameter()
