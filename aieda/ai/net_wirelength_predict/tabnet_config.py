#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : tabnet_config.py
@Author : yhqiu
@Desc : configuration module for data and model
'''
import sys
import os
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import torch

# import aieda
current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit('/', 3)[0]
sys.path.append(root)

from aieda.ai import ConfigBase
from aieda.workspace import Workspace

class DataConfig(ConfigBase):
    """Tabnet data config"""
    def __init__(
        self,
        # Data paths: raw data directories, model input file, visualization file storage directory
        raw_input_dirs: List[Workspace],
        pattern : Optional[str] = None,
        model_input_file: str = "dataset.csv",
        plot_dir : str = "./plots",
        
        # Data features: features extracted from raw data directories
        extracted_feature_columns: Optional[List[str]] = None,
        # Features for via prediction model
        via_feature_columns: Optional[List[str]] = None,
        # Features for wirelength baseline model
        wl_baseline_feature_columns: Optional[List[str]] = None,
        # Features for wirelength with via model
        wl_with_via_feature_columns: Optional[List[str]] = None,
        
        # Data cleaning: max fanout, max aspect ratio, outlier multiplier
        max_fanout: int = 30,
        max_aspect_ratio: float = 5.0,
        outlier_multiplier: float = 1.5,
        
        # Data splitting: test set ratio, validation set ratio, random seed, whether to use stratified sampling
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42,
        stratify: bool = True,   
             
        # Data processing: target value binning configuration
        target_bins: Optional[List[float]] = None,
        target_labels: Optional[List[str]] = None,
        
        # Other parameters
        **kwargs
    ):
        super().__init__(**kwargs)
        # Data paths
        self.raw_input_dirs = raw_input_dirs
        self.pattern = pattern
        self.model_input_file = model_input_file
        self.plot_dir = plot_dir
        
        # Data features
        self.extracted_feature_columns = extracted_feature_columns or self._get_extracted_feature_columns()
        self.via_feature_columns = via_feature_columns or self._get_default_via_feature_columns()
        self.wl_baseline_feature_columns = wl_baseline_feature_columns or self._get_default_wl_baseline_feature_columns()
        self.wl_with_via_feature_columns = wl_with_via_feature_columns or self._get_default_wl_with_via_feature_columns()
        
        # Data cleaning
        self.max_fanout = max_fanout
        self.max_aspect_ratio = max_aspect_ratio
        self.outlier_multiplier = outlier_multiplier
        
        # Data splitting
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.stratify = stratify
        
        # Data processing
        self.target_bins = target_bins or [
            0, 0.8, 0.9, 1.0, 1.1, 1.2, float('inf')]
        self.target_labels = target_labels or [
            '<0.8', '0.8-0.9', '0.9-1.0', '1.0-1.1', '1.1-1.2', '>1.2']


    def _get_extracted_feature_columns(self) -> List[str]:
        return ['id', 'wire_len', 'width', 'height', 'fanout', 'aspect_ratio', 'l_ness', 'rsmt', 'via_num']

    def _get_default_via_feature_columns(self) -> List[str]:
        return ['width', 'height', 'pin_num', 'aspect_ratio', 'l_ness', 'rsmt', 'area', 'route_ratio_x', 'route_ratio_y']

    def _get_default_wl_baseline_feature_columns(self) -> List[str]:
        return ['width', 'height', 'pin_num', 'aspect_ratio', 'l_ness', 'rsmt', 'area', 'route_ratio_x', 'route_ratio_y']

    def _get_default_wl_with_via_feature_columns(self) -> List[str]:
        return ['width', 'height', 'pin_num', 'aspect_ratio', 'l_ness', 'rsmt', 'area', 'route_ratio_x', 'route_ratio_y', 'via_num']


class ModelConfig(ConfigBase):
    """TabNet model config"""
    def __init__(
        self,
        # TabNet core architecture parameters
        n_d: int = 64,
        n_a: int = 128,
        n_steps: int = 4,
        gamma: float = 1.8,
        n_independent: int = 2,
        n_shared: int = 2,
        lambda_sparse: float = 1e-5,
        
        # Training parameters
        learning_rate: float = 0.01,
        batch_size: int = 2048,
        max_epochs: int = 100,
        patience: int = 20,
        drop_last: bool = False,

        # Performance parameters
        device: Optional[str] = None,
        num_workers: int = 0,
        pin_memory: bool = True,
        
        # Stage parameters
        do_train: bool = True,
        do_eval: bool = True,
        do_predict: bool = False,
        
        # Model saving
        output_dir: str = "./results",
        model_name: str = "tabnet_model",
        
        # Specific parameters
        via_model_config: Optional[Dict[str, Any]] = None,
        baseline_model_config: Optional[Dict[str, Any]] = None,
        with_via_model_config: Optional[Dict[str, Any]] = None,
        
        # Other additional parameters
        **kwargs
    ):
        super().__init__(**kwargs)
        # TabNet core architecture parameters
        self.n_d = n_d  # Decision layer dimension
        self.n_a = n_a  # Attention layer dimension
        self.n_steps = n_steps  # Number of decision steps
        self.gamma = gamma  # Relaxation factor
        self.n_independent = n_independent  # Number of independent GLU layers
        self.n_shared = n_shared  # Number of shared GLU layers
        self.lambda_sparse = lambda_sparse  # Sparsity regularization coefficient
        
        # Training parameters
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.patience = patience
        self.drop_last = drop_last

        # Performance parameters
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        
        # Stage parameters
        self.do_train = do_train
        self.do_eval = do_eval
        self.do_predict = do_predict
        
        # Model saving configuration
        self.output_dir = output_dir
        self.model_name = model_name
        
        # Specific parameters
        self.via_model_config = via_model_config or {
            'n_d': 16,
            'n_a': 32,
            'n_steps': 5,
            'gamma': 1.3,
            'n_independent': 2,
            'n_shared': 2,
            'lambda_sparse': 1e-4,
            'learning_rate': 0.01,
            'batch_size': 512,
            'max_epochs': 100,
            'patience': 20,
            'device': device,
            'num_workers': 8,
            'pin_memory': True
        }
        self.baseline_model_config = baseline_model_config or {
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
            'device': device,
            'num_workers': 8,
            'pin_memory': True
        }
        self.with_via_model_config = with_via_model_config or {
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
            'device': device,
            'num_workers': 8,
            'pin_memory': True
        }
        

# Usage examples
if __name__ == "__main__":
    # 1. Use default configuration
    config = ModelConfig()
    print("Default config:", config.n_d, config.learning_rate)

    # 2. Create configuration with direct parameters
    config = ModelConfig(
        n_d=32,
        learning_rate=0.005,
        batch_size=1024
    )
    print("Custom config:", config.n_d, config.learning_rate)

    # 3. Create configuration from dictionary
    config_dict = {
        "n_d": 48,
        "n_a": 96,
        "learning_rate": 0.008
    }
    config = ModelConfig.from_dict(config_dict)
    print("From dictionary:", config.n_d, config.n_a)

    # 4. Dynamically modify configuration
    config.update(learning_rate=0.001, batch_size=512)
    print("After modification:", config.learning_rate, config.batch_size)

    # 5. Save and load configuration
    config.to_json_file("./config.json")
    loaded_config = ModelConfig.from_json_file("./config.json")
    print("Loaded config:", loaded_config.learning_rate)
