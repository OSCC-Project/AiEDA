#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : transformer_config.py
@Author : yhqiu
@Desc : configuration module for path delay prediction
"""
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

class DataConfig(ConfigBase):
    """Path delay prediction data config"""
    def __init__(
        self,
        # Data paths
        train_dirs: Optional[List[str]] = None,
        test_dirs: Optional[List[str]] = None,
        dataset_directory: str = "dataset",
        
        # Data sampling
        sample_num: int = 3000,
        train_ratio: float = 0.7,
        random_seed: int = 42,
        
        # Data processing
        normalize: bool = False,
        train_stats_file: str = "train_normalization_stats.json",
        test_stats_file: str = "test_normalization_stats.json",
        
        # Data loading
        batch_size: int = 32,
        num_workers: int = 4,
        pin_memory: bool = True,
        
        # Other parameters
        **kwargs
    ):
        super().__init__(**kwargs)
        # Data paths
        self.train_dirs = train_dirs or []
        self.test_dirs = test_dirs or []
        self.dataset_directory = dataset_directory
        
        # Data sampling
        self.sample_num = sample_num
        self.train_ratio = train_ratio
        self.random_seed = random_seed
        
        # Data processing
        self.normalize = normalize
        self.train_stats_file = train_stats_file
        self.test_stats_file = test_stats_file
        
        # Data loading
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        

class ModelConfig(ConfigBase):
    """Path delay prediction model config"""
    def __init__(
        self,
        # Model architecture parameters
        input_dim: int = 3,
        hidden_dim: int = 32,
        num_layers: int = 3,
        num_heads: int = 4,
        mlp_hidden_dim: int = 64,
        output_dim: int = 1,
        dropout: float = 0.3,
        
        # Training parameters
        learning_rate: float = 0.0001,
        weight_decay: float = 1e-3,
        epochs: int = 100,
        
        # Performance parameters
        device: Optional[str] = None,
        
        # Stage parameters
        do_train: bool = True,
        do_eval: bool = True,
        do_predict: bool = False,
        
        # Model saving
        checkpoint_dir: str = "./checkpoints",
        
        # Other additional parameters
        **kwargs
    ):
        super().__init__(**kwargs)
        # Model architecture parameters
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.mlp_hidden_dim = mlp_hidden_dim
        self.output_dim = output_dim
        self.dropout = dropout
        
        # Training parameters
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.epochs = epochs
        
        # Performance parameters
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Stage parameters
        self.do_train = do_train
        self.do_eval = do_eval
        self.do_predict = do_predict
        
        # Model saving configuration
        self.checkpoint_dir = checkpoint_dir

# Usage examples
if __name__ == "__main__":
    # 1. Use default configuration
    data_config = DataConfig()
    model_config = ModelConfig()
    
    # 2. Create configuration with direct parameters
    data_config = DataConfig(
        sample_num=5000,
        batch_size=64,
        normalize=True
    )
    
    model_config = ModelConfig(
        hidden_dim=64,
        num_layers=4,
        learning_rate=0.001
    )
    
    # 3. Save and load configuration
    data_config.to_json_file("./data_config.json")
    model_config.to_json_file("./model_config.json")
    
    loaded_data_config = DataConfig.from_json_file("./data_config.json")
    loaded_model_config = ModelConfig.from_json_file("./model_config.json")