#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_flow_closure.py
@Author : yhqiu
@Desc : closure flow: EDA data_generation -> data parse and load -> model training -> model inference -> guide EDA optimization
@Desc : use net_wirelength_predict as an example
"""

######################################################################################
import os
import torch

# set EDA tools working environment
os.environ["iEDA"] = "ON"

from aieda.workspace import workspace_create
from aieda.flows import DbFlow, RunIEDA, DataGeneration
from aieda.analysis import CellTypeAnalyzer, WireDistributionAnalyzer
from aieda.ai import (
    TabNetDataConfig,
    TabNetDataProcess,
    TabNetModelConfig,
    TabNetTrainer,
)

######################################################################################
current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit("/", 1)[0]
workspace_dir = "{}/example/sky130_test".format(root)

# all workspace directory
WORKSPACES = {"gcd": workspace_dir}

# name map
DISPLAY_NAME = {"gcd": "GCD"}

if __name__ == "__main__":
    workspace_list = []
    for design, dir in WORKSPACES.items():
        # step 1: create workspace list
        workspace = workspace_create(directory=dir, design=design)
        workspace_list.append(workspace)

        # step 2 : init iEDA by workspace and run flows (✔)
        run_ieda = RunIEDA(workspace)
        run_ieda.run_flows()

        # step 3: init DataGeneration by workspace and generate vectors (✔)
        data_gen = DataGeneration(workspace)
        data_gen.generate_vectors(
            input_def=workspace.configs.get_output_def(
                DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
            ),
            vectors_dir=workspace.paths_table.ieda_output["vectors"],
            patch_row_step=18,
            patch_col_step=18,
        )

    # step 4.1: design-level analysis (✔)
    cell_analyzer = CellTypeAnalyzer()
    cell_analyzer.load(
        workspace_dirs=workspace_list,
        flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route),
        dir_to_display_name=DISPLAY_NAME,
    )
    cell_analyzer.analyze()
    cell_analyzer.visualize(save_path=workspace_dir)

    # step 4.2: net-level analysis (✔)
    wire_analyzer = WireDistributionAnalyzer()
    wire_analyzer.load(
        workspace_dirs=workspace_list,
        pattern="/output/iEDA/vectors/nets",
        dir_to_display_name=DISPLAY_NAME,
    )
    wire_analyzer.analyze()
    wire_analyzer.visualize(save_path=workspace_dir)

    # step 5.1: data config and sub-dataset generation (✔)
    data_config = TabNetDataConfig(
        raw_input_dirs=workspace_list,
        pattern="/output/iEDA/vectors/nets",
        model_input_file="./net_dataset.csv",
        plot_dir="./analysis_fig",
        normalization_params_file="./normalization_params/wl_baseline_normalization_params.json",
        extracted_feature_columns=[
            "id",
            "wire_len",
            "width",
            "height",
            "fanout",
            "aspect_ratio",
            "l_ness",
            "rsmt",
            "via_num",
        ],
        wl_baseline_feature_columns=[
            "width",
            "height",
            "pin_num",
            "aspect_ratio",
            "l_ness",
            "rsmt",
            "area",
            "route_ratio_x",
            "route_ratio_y",
        ],
        test_size=0.2,
        random_state=42,
    )
    data_processor = TabNetDataProcess(data_config)
    data_processor.run_pipeline()

    # step 5.2: model config, training and evaluate (✔)
    wirelength_baseline_model_config = {
        "n_d": 64,
        "n_a": 128,
        "n_steps": 4,
        "gamma": 1.8,
        "n_independent": 2,
        "n_shared": 2,
        "lambda_sparse": 1e-5,
        "learning_rate": 0.01,
        "batch_size": 2048,
        "max_epochs": 100,
        "patience": 20,
        "device": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        "num_workers": 4,
        "pin_memory": True,
    }
    model_config = TabNetModelConfig(
        do_train=True,
        do_eval=True,
        output_dir="./",
        baseline_model_config=wirelength_baseline_model_config,
    )
    trainer = TabNetTrainer(data_config=data_config, model_config=model_config)
    data_dict = trainer.train()
    # results = trainer.evaluate(data_dict)
    trainer.save_models("./saved_models")

    # step 5.3: model export as onnx (✔)
    onnx_path, normalization_path = trainer.export_model_to_onnx(
        model_type="wirelength",
        model_path="./saved_models/baseline_model.zip",
        onnx_path="./saved_models/baseline_model.onnx",
        num_features=9,
    )
    print(f"ONNX model exported to: {onnx_path}")
    print(f"Normalization parameters saved to: {normalization_path}")

    # step 6: model inference for specific design  (✔)
    run_ieda = RunIEDA(workspace_list[0])
    run_ieda.run_ai_placement(
        input_def=workspace.configs.get_output_def(
            DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)
        ),
        onnx_path=onnx_path,
        normalization_path=normalization_path,
    )

    exit(0)
