#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_flow_closure.py
@Author : yhqiu
@Desc : closure flow: EDA data_generation -> data parse and load -> model training -> model inference -> guide EDA optimization
@Desc : use net_wirelength_predict as an example
'''

######################################################################################
import os
import torch

# import aieda
from import_aieda import import_aieda
import_aieda()

from aieda.workspace import workspace_create
from aieda.flows import DbFlow, RunIEDA, DataGeneration
from aieda.eda.iEDA.placement import IEDAPlacement
from aieda.analysis import CellTypeAnalyzer, WireDistributionAnalyzer
from aieda.ai import TabNetDataConfig, TabNetDataProcess, TabNetModelConfig, TabNetTrainer

######################################################################################

BASE_DIRS = [
    "/data2/project_share/dataset_baseline/s713",
    "/data2/project_share/dataset_baseline/s44",
    "/data2/project_share/dataset_baseline/apb4_rng",
    "/data2/project_share/dataset_baseline/gcd",
    "/data2/project_share/dataset_baseline/s1238",
    "/data2/project_share/dataset_baseline/s1488",
    "/data2/project_share/dataset_baseline/apb4_archinfo",
    "/data2/project_share/dataset_baseline/apb4_ps2",
    "/data2/project_share/dataset_baseline/s9234",
    "/data2/project_share/dataset_baseline/apb4_timer",
    "/data2/project_share/dataset_baseline/s13207",
    "/data2/project_share/dataset_baseline/apb4_i2c",
    "/data2/project_share/dataset_baseline/s5378",
    "/data2/project_share/dataset_baseline/apb4_pwm",
    "/data2/project_share/dataset_baseline/apb4_wdg",
    "/data2/project_share/dataset_baseline/apb4_clint",
    "/data2/project_share/dataset_baseline/ASIC",
    "/data2/project_share/dataset_baseline/s15850",
    "/data2/project_share/dataset_baseline/apb4_uart",
    "/data2/project_share/dataset_baseline/s38417",
    "/data2/project_share/dataset_baseline/s35932",
    "/data2/project_share/dataset_baseline/s38584",
    "/data2/project_share/dataset_baseline/BM64",
    "/data2/project_share/dataset_baseline/picorv32",
    "/data2/project_share/dataset_baseline/PPU",
    "/data2/project_share/dataset_baseline/blabla",
    "/data2/project_share/dataset_baseline/aes_core",
    "/data2/project_share/dataset_baseline/aes",
    "/data2/project_share/dataset_baseline/salsa20",
    "/data2/project_share/dataset_baseline/jpeg_encoder",
    "/data2/project_share/dataset_baseline/eth_top"
]

DISPLAY_NAME = {
    "s713": "s713",
    "s44": "s44",
    "apb4_rng": "apb4_rng",
    "gcd": "gcd",
    "s1238": "s1238",
    "s1488": "s1488",
    "apb4_archinfo": "apb4_arch",
    "apb4_ps2": "apb4_ps2",
    "s9234": "s9234",
    "apb4_timer": "apb4_timer",
    "s13207": "s13207",
    "apb4_i2c": "apb4_i2c",
    "s5378": "s5378",
    "apb4_pwm": "apb4_pwm",
    "apb4_wdg": "apb4_wdg",
    "apb4_clint": "apb4_clint",
    "ASIC": "ASIC",
    "s15850": "s15850",
    "apb4_uart": "apb4_uart",
    "s38417": "s38417",
    "s35932": "s35932",
    "s38584": "s38584",
    "BM64": "BM64",
    "picorv32": "picorv32",
    "PPU": "PPU",
    "blabla": "blabla",
    "aes_core": "aes_core",
    "aes": "aes",
    "salsa20": "salsa20",
    "jpeg_encoder": "jpeg",
    "eth_top": "eth_top"
}


if __name__ == "__main__":
    workspace_list = []
    for base_dir in BASE_DIRS:
        # step 1: create workspace list
        workspace = workspace_create(
            directory=base_dir+"/workspace", design=os.path.basename(base_dir))
        workspace_list.append(workspace)

        # step 2 : init iEDA by workspace and run flows (✔)
        run_ieda = RunIEDA(workspace)
        run_ieda.run_flows()

        # step 3: init DataGeneration by workspace and generate vectors (✔)
        data_gen = DataGeneration(workspace)
        data_gen.generate_vectors(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)),
                                  vectors_dir=workspace.paths_table.ieda_output['vectors'],
                                  patch_row_step=18,
                                  patch_col_step=18)

    # step 4.1: design-level analysis (✔)
    cell_analyzer = CellTypeAnalyzer()
    cell_analyzer.load(
        workspace_dirs=workspace_list,
        flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route),
        dir_to_display_name=DISPLAY_NAME
    )
    cell_analyzer.analyze()
    cell_analyzer.visualize(save_path="./")
    
    # step 4.2: net-level analysis (✔)
    wire_analyzer = WireDistributionAnalyzer()
    wire_analyzer.load(
        workspace_dirs=workspace_list,
        pattern = "/output/innovus/vectors/nets",
        dir_to_display_name=DISPLAY_NAME
    )
    wire_analyzer.analyze()
    wire_analyzer.visualize(save_path=".")

    # step 5.1: data config and sub-dataset generation (✔)
    data_config = TabNetDataConfig(
        raw_input_dirs=workspace_list,
        pattern="/output/innovus/vectors/nets",
        model_input_file="./net_dataset.csv",
        plot_dir="./analysis_fig",
        normalization_params_file="./normalization_params/wl_baseline_normalization_params.json",
        extracted_feature_columns=['id', 'wire_len', 'width', 'height',
                                   'fanout', 'aspect_ratio', 'l_ness', 'rsmt',
                                   'via_num'],
        wl_baseline_feature_columns=['width', 'height', 'pin_num', 'aspect_ratio',
                                     'l_ness', 'rsmt', 'area', 'route_ratio_x',
                                     'route_ratio_y'],
        test_size=0.2,
        random_state=42,
    )
    data_processor = TabNetDataProcess(data_config)
    data_processor.run_pipeline()
    
    # step 5.2: model config, training and evaluate (✔)
    wirelength_baseline_model_config = {
        'n_d': 64,
        'n_a': 128,
        'n_steps': 4,
        'gamma': 1.8,
        'n_independent': 2,
        'n_shared': 2,
        'lambda_sparse': 1e-5,
        'learning_rate': 0.01,
        'batch_size': 2048,
        'max_epochs': 100,
        'patience': 20,
        'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
        'num_workers': 4,
        'pin_memory': True
    }
    model_config = TabNetModelConfig(
        do_train=True,
        do_eval=True,
        output_dir="./",
        baseline_model_config=wirelength_baseline_model_config,
    )
    trainer = TabNetTrainer(
        data_config=data_config,
        model_config=model_config
    )
    data_dict = trainer.train()
    # results = trainer.evaluate(data_dict)
    trainer.save_models("./saved_models")
    
    # step 5.3: model export as onnx (✔)
    onnx_path, normalization_path = trainer.export_model_to_onnx(
        model_type='wirelength',
        model_path='./saved_models/baseline_model.zip',
        onnx_path='./saved_models/baseline_model.onnx',
        num_features=9
    )
    print(f"ONNX model exported to: {onnx_path}")
    print(f"Normalization parameters saved to: {normalization_path}")
    

    # step 6: model inference for specific design  (✔)
    # onnx_path = "/home/yhqiu/aieda_fork/test/saved_models/baseline_model.onnx"
    # normalization_path = "/home/yhqiu/aieda_fork/test/normalization_params/wl_baseline_normalization_params.json"
    run_ieda = RunIEDA(workspace_list[0])
    run_ieda.run_ai_placement(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)),
                               onnx_path=onnx_path, 
                               normalization_path=normalization_path)
        
    exit(0)
