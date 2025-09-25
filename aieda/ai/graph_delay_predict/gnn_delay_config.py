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

class NodeDelayDataConfig(ConfigBase):
    """GNN node delay prediction data config"""
    def __init__(
        self,
        # Data paths: raw data directories, model input file, visualization file storage directory
        raw_input_dirs: List[str],
        pattern: str = "/output/innovus/vectors/timing_data",
        model_input_file: str = "./gnn_node_delay_dataset.pt",
        plot_dir: str = "./gnn_node_delay_analysis_plots",
        
        # Data features: node and edge feature dimensions
        node_feature_dim: int = 9,
        edge_feature_dim: int = 8,
        
        # Data cleaning: delay thresholds, outlier detection, graph size constraints
        min_delay_threshold: float = 1e-15,
        max_delay_threshold: float = 1e-6,
        outlier_std_threshold: float = 3.0,
        min_nodes_per_graph: int = 3,
        min_edges_per_graph: int = 2,
        
        # Data splitting: train, validation, test set ratios
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        
        # Data processing: PyTorch Geometric parameters
        batch_size: int = 32,
        num_workers: int = 4,
        
        # Other parameters
        random_seed: int = 42,
        **kwargs
    ):
        super().__init__(**kwargs)
        # Data paths
        self.raw_input_dirs = raw_input_dirs
        self.pattern = pattern
        self.model_input_file = model_input_file
        self.plot_dir = plot_dir
        
        # Data features
        self.node_feature_dim = node_feature_dim
        self.edge_feature_dim = edge_feature_dim
        
        # Data cleaning
        self.min_delay_threshold = min_delay_threshold
        self.max_delay_threshold = max_delay_threshold
        self.outlier_std_threshold = outlier_std_threshold
        self.min_nodes_per_graph = min_nodes_per_graph
        self.min_edges_per_graph = min_edges_per_graph
        
        # Data splitting
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        
        # Data processing
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.random_seed = random_seed


class NodeDelayModelConfig(ConfigBase):
    """GNN node delay prediction model config"""
    def __init__(
        self,
        # Model input dimensions: node and edge feature dimensions
        node_feature_dim: int = 9,
        edge_feature_dim: int = 8,
        
        # GNN architecture parameters: hidden dimensions, layers, attention heads
        hidden_dim: int = 128,
        num_layers: int = 3,
        num_heads: int = 8,
        dropout: float = 0.1,
        activation: str = 'relu',
        conv_type: str = 'gcn',  # 'gcn', 'sage', 'gin'
        
        # Transformer parameters: model dimensions, encoder layers, feedforward
        d_model: int = 128,
        nhead: int = 8,
        num_encoder_layers: int = 3,
        dim_feedforward: int = 512,
        transformer_dropout: float = 0.1,
        
        # Training parameters: learning rate, batch size, epochs, patience
        learning_rate: float = 0.001,
        batch_size: int = 32,
        max_epochs: int = 200,
        patience: int = 30,
        weight_decay: float = 1e-4,
        
        # Performance parameters: device, workers, memory pinning
        device: Optional[str] = None,
        num_workers: int = 4,
        pin_memory: bool = True,
        
        # Stage parameters: training, evaluation, prediction control
        do_train: bool = True,
        do_eval: bool = True,
        do_predict: bool = False,
        
        # Model saving: output directory, model name, save path
        output_dir: str = "./results",
        model_name: str = "gnn_node_delay_model",
        model_save_path: str = "./models/gnn_node_delay_model.pt",
        
        # Loss function parameters: loss type and alpha for huber loss
        loss_type: str = 'mae',  # 'mse', 'mae', 'huber'
        loss_alpha: float = 0.1,  # for huber loss
        
        # Regularization and optimization: L2 regularization, gradient clipping
        l2_reg: float = 1e-5,
        gradient_clip: float = 1.0,
        scheduler_patience: int = 10,
        scheduler_factor: float = 0.5,
        
        # Other parameters
        **kwargs
    ):
        super().__init__(**kwargs)
        # Model dimensions
        self.node_feature_dim = node_feature_dim
        self.edge_feature_dim = edge_feature_dim
        
        # GNN architecture parameters
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.dropout = dropout
        self.activation = activation
        self.conv_type = conv_type
        
        # Transformer parameters
        self.d_model = d_model
        self.nhead = nhead
        self.num_encoder_layers = num_encoder_layers
        self.dim_feedforward = dim_feedforward
        self.transformer_dropout = transformer_dropout
        
        # Training parameters
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.patience = patience
        self.weight_decay = weight_decay

        # Performance parameters
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        
        # Stage parameters
        self.do_train = do_train
        self.do_eval = do_eval
        self.do_predict = do_predict
        
        # Model saving
        self.output_dir = output_dir
        self.model_name = model_name
        self.model_save_path = model_save_path
        
        # Loss function
        self.loss_type = loss_type
        self.loss_alpha = loss_alpha
        
        # Regularization and optimization
        self.l2_reg = l2_reg
        self.gradient_clip = gradient_clip
        self.scheduler_patience = scheduler_patience
        self.scheduler_factor = scheduler_factor


# Usage examples
if __name__ == "__main__":
    # 1. Use default configuration
    data_config = NodeDelayDataConfig(
        raw_input_dirs=[
            "/data2/project_share/dataset_baseline/s713/workspace",
            "/data2/project_share/dataset_baseline/s44/workspace",
            "/data2/project_share/dataset_baseline/gcd/workspace"
        ],
        pattern="/output/innovus/vectors/timing_data",
        model_input_file="./gnn_node_delay_dataset.pt",
        batch_size=32,
        random_seed=42
    )
    print("Data config:", data_config.node_feature_dim, data_config.batch_size)

    # 2. Create configuration with direct parameters
    model_config = NodeDelayModelConfig(
        node_feature_dim=9,
        edge_feature_dim=8,
        hidden_dim=128,
        learning_rate=0.001,
        max_epochs=200,
        patience=10
    )
    print("Model config:", model_config.hidden_dim, model_config.learning_rate)

    # 3. Create configuration from dictionary
    config_dict = {
        "hidden_dim": 256,
        "num_layers": 4,
        "learning_rate": 0.0005,
        "dropout": 0.2
    }
    model_config = NodeDelayModelConfig.from_dict(config_dict)
    print("From dictionary:", model_config.hidden_dim, model_config.num_layers)

    # 4. Dynamically modify configuration
    model_config.update(learning_rate=0.0001, batch_size=16)
    print("After modification:", model_config.learning_rate, model_config.batch_size)

    # 5. Save and load configuration
    model_config.to_json_file("./gnn_node_delay_config.json")
    loaded_config = NodeDelayModelConfig.from_json_file("./gnn_node_delay_config.json")
    print("Loaded config:", loaded_config.learning_rate)
