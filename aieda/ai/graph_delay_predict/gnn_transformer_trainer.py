import os
import sys
import json
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# import aieda
current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit('/', 3)[0]
sys.path.append(root)

from aieda.ai.graph_delay_predict.gnn_delay_model import NodeDelayPredictor, get_config
from aieda.ai.graph_delay_predict.gnn_delay_process import RCNetworkDataProcessor, RCNetworkDataConfig
from aieda.ai.graph_delay_predict.gnn_delay_config import NodeDelayModelConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GNNTransformerTrainingConfig:
    """GNN+Transformer node delay prediction training configuration"""
    # Dataset directories
    raw_input_dirs: List[str]
    
    # Data processing configuration
    data_config: Optional[RCNetworkDataConfig] = None
    
    # Model configuration
    model_config: Optional[Dict[str, Any]] = None
    
    # Training output paths
    model_save_path: str = "./models/gnn_transformer_delay_model.pt"
    results_dir: str = "./results"
    
    # Training control parameters
    use_pretrained_data: bool = True
    pretrained_data_path: str = "./rc_network_dataset.pt"
    
    # Visualization configuration
    plot_training_curves: bool = True
    save_predictions: bool = True
    
    # GNN type selection
    gnn_type: str = 'gcn'  # 'gcn', 'gat', 'sage', 'gin', 'transformer'
    
    # Debug and monitoring configuration
    enable_gradient_monitoring: bool = True
    enable_prediction_validation: bool = True
    gradient_clip_norm: float = 1.0
    learning_rate_warmup_epochs: int = 10
    
    def __post_init__(self):
        """Post-initialization processing, create default configurations"""
        if self.data_config is None:
            self.data_config = RCNetworkDataConfig(
                raw_input_dirs=self.raw_input_dirs,
                pattern="/output/innovus/vectors/timing_data",
                model_input_file="./rc_network_dataset.pt",
                plot_dir="./rc_network_analysis_plots",
                node_feature_dim=9,
                edge_feature_dim=8,
                min_delay_threshold=1e-12,
                max_delay_threshold=3,
                min_nodes_per_net=5,
                min_edges_per_net=4,
                min_paths_per_net=2,
                critical_path_delay_ratio=0.8,
                max_critical_paths=3,
                debug_net_construction=True,
                use_design_specific_normalization=True,
                save_normalization_params=True,
                normalization_params_file="./design_normalization_params.json",
                train_ratio=0.7,
                val_ratio=0.15,
                test_ratio=0.15,
                batch_size=16,
                num_workers=4,
                random_seed=43
            )
        
        if self.model_config is None:
            self.model_config = get_config(
                gnn_type=self.gnn_type,
                hidden_dim=128,
                num_layers=3,
                learning_rate=0.001  # Increased learning rate
            )
            # Add configurations
            self.model_config.update({
                'gradient_clip': self.gradient_clip_norm,
                'loss_type': 'combined',
                'mse_weight': 0.5,
                'mae_weight': 0.3,
                'relative_weight': 0.2,
                'scheduler_type': 'cosine',
                'patience': 20,  # Increased patience
                'max_epochs': 200,  # Increased training epochs
                'enable_value_calibrator': False,  # Temporarily disable value range calibrator
                'enable_output_processor': False,  # Temporarily disable output processor
            })

class GNNTransformerTrainer:
    """GNN+Transformer node delay prediction trainer """
    
    def __init__(self, config: GNNTransformerTrainingConfig):
        """
        Initialize trainer
        
        Args:
            config: Training configuration
        """
        self.config = config
        self.data_processor = RCNetworkDataProcessor(config.data_config)
        self.model = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        self.design_normalization_params = None
        self.logger = logging.getLogger(__name__)
        
        # Create output directories
        os.makedirs(os.path.dirname(config.model_save_path), exist_ok=True)
        os.makedirs(config.results_dir, exist_ok=True)
        
        # Gradient monitoring
        self.gradient_norms = []
        self.prediction_stats = []
    
    def prepare_data(self):
        """Prepare data"""
        self.logger.info("Starting data preparation")
        
        if self.config.use_pretrained_data and os.path.exists(self.config.pretrained_data_path):
            # Use preprocessed data
            self.logger.info(f"Loading preprocessed data: {self.config.pretrained_data_path}")
            processed_data = torch.load(self.config.pretrained_data_path)
            
            train_data = processed_data['train_data']
            val_data = processed_data['val_data']
            test_data = processed_data['test_data']
            
            # Load design-specific normalization parameters
            if 'design_normalization_params' in processed_data:
                self.design_normalization_params = processed_data['design_normalization_params']
                self.logger.info("Loaded design-specific normalization parameters")
            
            # Create data loaders
            self.train_loader, self.val_loader, self.test_loader = self.data_processor.create_data_loaders(
                train_data, val_data, test_data
            )
            
            # Analyze data statistics
            self._analyze_data_statistics(train_data, val_data, test_data)
            
            self.logger.info(f"Loading completed - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        else:
            # Reprocess data
            self.logger.info("Starting data reprocessing")
            result = self.data_processor.run_pipeline()
            
            if result is None:
                raise ValueError("Data processing failed")
            
            self.train_loader = result['train_loader']
            self.val_loader = result['val_loader']
            self.test_loader = result['test_loader']
            
            # Save design-specific normalization parameters
            if hasattr(self.data_processor, 'design_normalization_params'):
                self.design_normalization_params = self.data_processor.design_normalization_params
                self.logger.info("Saved design-specific normalization parameters")
            
            self.logger.info(f"Data processing completed - Total networks: {result['total_networks']}")
        
        self.logger.info("Data preparation completed")
    
    def _analyze_data_statistics(self, train_data, val_data, test_data):
        """Analyze data statistics"""
        all_targets = []
        for data in train_data + val_data + test_data:
            if hasattr(data, 'y'):
                all_targets.extend(data.y.cpu().numpy().flatten())
        
        all_targets = np.array(all_targets)
        
        self.logger.info(f"Data statistics:")
        self.logger.info(f"  Target value range: {np.min(all_targets):.6f} - {np.max(all_targets):.6f}")
        self.logger.info(f"  Target value mean: {np.mean(all_targets):.6f}")
        self.logger.info(f"  Target value std: {np.std(all_targets):.6f}")
        self.logger.info(f"  Target value median: {np.median(all_targets):.6f}")
        
        # Check for outliers
        q1, q3 = np.percentile(all_targets, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = np.sum((all_targets < lower_bound) | (all_targets > upper_bound))
        self.logger.info(f"  Outlier count: {outliers} ({outliers/len(all_targets)*100:.2f}%)")
    
    def create_model(self):
        """Create model"""
        self.logger.info(f"Creating {self.config.gnn_type.upper()} model")
        
        # Update model configuration
        self.config.model_config.update({
            'node_feature_dim': self.config.data_config.node_feature_dim,
            'edge_feature_dim': self.config.data_config.edge_feature_dim,
            'device': self.config.model_config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu'),
            'output_dir': self.config.results_dir
        })
        
        # Create model
        model_name = f"{self.config.gnn_type.upper()}_NodeDelay"
        self.model = NodeDelayPredictor(self.config.model_config, model_name)
        
        # Add gradient monitoring hooks
        if self.config.enable_gradient_monitoring:
            self._add_gradient_hooks()
        
        self.logger.info("Model creation completed")
    
    def _add_gradient_hooks(self):
        """Add gradient monitoring hooks"""
        def gradient_hook(name):
            def hook(module, grad_input, grad_output):
                if grad_output is not None and len(grad_output) > 0:
                    grad = grad_output[0]
                    if grad is not None:
                        grad_norm = grad.norm().item()
                        self.gradient_norms.append((name, grad_norm))
                        if grad_norm < 1e-8:
                            self.logger.warning(f"Gradient vanishing warning: {name} gradient norm = {grad_norm:.2e}")
                        elif grad_norm > 100:
                            self.logger.warning(f"Gradient explosion warning: {name} gradient norm = {grad_norm:.2e}")
            return hook
        
        # Add gradient monitoring for key layers
        for name, module in self.model.model.named_modules():
            if isinstance(module, (nn.Linear, nn.Conv1d, nn.LayerNorm)):
                module.register_backward_hook(gradient_hook(name))
    
    def train_model(self):
        """Train model"""
        if self.model is None:
            raise ValueError("Model not created")
        
        if self.train_loader is None:
            raise ValueError("Data not prepared")
        
        self.logger.info("Starting model training")
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info("GPU cache cleared")
        
        # Train model
        history = self.model.fit(self.train_loader, self.val_loader)
        
        # Save model
        self.model.save_model(self.config.model_save_path)
        self.logger.info(f"Model saved to: {self.config.model_save_path}")
        
        # Save gradient monitoring results
        if self.config.enable_gradient_monitoring and self.gradient_norms:
            self._save_gradient_analysis()
        
        return history
    
    def _save_gradient_analysis(self):
        """Save gradient analysis results"""
        if not self.gradient_norms:
            return
        
        # Group gradient norms by layer name
        layer_grads = {}
        for name, norm in self.gradient_norms:
            if name not in layer_grads:
                layer_grads[name] = []
            layer_grads[name].append(norm)
        
        # Calculate statistics
        grad_stats = {}
        for name, norms in layer_grads.items():
            grad_stats[name] = {
                'mean': np.mean(norms),
                'std': np.std(norms),
                'min': np.min(norms),
                'max': np.max(norms),
                'count': len(norms)
            }
        
        # Save to file
        grad_file = os.path.join(self.config.results_dir, 'gradient_analysis.json')
        with open(grad_file, 'w') as f:
            json.dump(grad_stats, f, indent=2)
        
        self.logger.info(f"Gradient analysis results saved to: {grad_file}")
    
    def evaluate_model(self):
        """Evaluate model"""
        if self.model is None or self.test_loader is None:
            raise ValueError("Model or test data not prepared")
        
        self.logger.info("Starting model evaluation")
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info("GPU cache cleared before evaluation")
        
        # Get predictions and targets
        predictions, targets = self.model.predict(self.test_loader)
        
        # Prediction validation
        if self.config.enable_prediction_validation:
            self._validate_predictions(predictions, targets)
        
        # Calculate metrics
        mse = mean_squared_error(targets, predictions)
        mae = mean_absolute_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        # MAPE calculation
        valid_mask = np.abs(targets) > 1e-8
        if np.sum(valid_mask) > 0:
            mape = np.mean(np.abs((targets[valid_mask] - predictions[valid_mask]) / 
                                (targets[valid_mask] + 1e-8))) * 100
        else:
            mape = float('inf')
        
        test_metrics = {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'mae': mae,
            'r2': r2,
            'mape': mape
        }
        
        self.logger.info("Test set evaluation results:")
        for metric, value in test_metrics.items():
            if value == float('inf'):
                self.logger.info(f"{metric}: inf")
            else:
                self.logger.info(f"{metric}: {value:.6f}")
        
        # Print statistics
        self.logger.info(f"Target value range: {np.min(targets):.4f} - {np.max(targets):.4f}")
        self.logger.info(f"Prediction value range: {np.min(predictions):.4f} - {np.max(predictions):.4f}")
        self.logger.info(f"Target value mean: {np.mean(targets):.4f}, std: {np.std(targets):.4f}")
        self.logger.info(f"Prediction value mean: {np.mean(predictions):.4f}, std: {np.std(predictions):.4f}")

        # Generate visualization charts
        if self.config.plot_training_curves:
            self._plot_evaluation_results(predictions, targets, test_metrics)

        if self.config.save_predictions:
            # Save prediction results
            pred_file = os.path.join(self.config.results_dir, 'predictions.npz')
            np.savez(pred_file, 
                    predictions=predictions, 
                    targets=targets,
                    gnn_type=self.config.gnn_type,
                    model_config=self.config.model_config)
            self.logger.info(f"Prediction results saved to: {pred_file}")
        
        return test_metrics
    
    def _validate_predictions(self, predictions, targets):
        """Validate prediction results"""
        # Check if predictions are all constants
        pred_std = np.std(predictions)
        pred_unique = len(np.unique(predictions))
        
        self.logger.info(f"Prediction validation:")
        self.logger.info(f"  Prediction value std: {pred_std:.6f}")
        self.logger.info(f"  Prediction unique value count: {pred_unique}")
        
        if pred_std < 1e-6:
            self.logger.error("❌ Warning: Predictions are almost constant, model may not have learned effective features!")
            self.logger.error(f"    Prediction value range: {np.min(predictions):.6f} - {np.max(predictions):.6f}")
        elif pred_unique < 10:
            self.logger.warning("⚠️  Warning: Insufficient prediction diversity, possible overfitting or underfitting")
        else:
            self.logger.info("✅ Prediction validation passed")
        
        # Check correlation between predictions and targets
        correlation = np.corrcoef(predictions, targets)[0, 1]
        self.logger.info(f"  Prediction-target correlation: {correlation:.4f}")
        
        if correlation < 0.1:
            self.logger.warning("⚠️  Warning: Very low correlation between predictions and targets")
        elif correlation > 0.8:
            self.logger.info("✅ Good correlation between predictions and targets")
    
    def _plot_evaluation_results(self, predictions, targets, test_metrics):
        """Plot evaluation results"""
        from datetime import datetime
        os.makedirs(self.config.results_dir, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.style.use('seaborn-v0_8-whitegrid')

        # 1. Pred vs True scatter plot
        plt.figure(figsize=(10, 8))
        plt.scatter(targets, predictions, s=15, alpha=0.6, color='steelblue')
        low, high = min(targets.min(), predictions.min()), max(targets.max(), predictions.max())
        plt.plot([low, high], [low, high], 'r--', lw=2, label='Perfect Prediction')
        plt.xlabel('True Delay (normalized)')
        plt.ylabel('Predicted Delay (normalized)')
        plt.title(f'Prediction vs True Values - {self.config.gnn_type.upper()}\n(R²={test_metrics["r2"]:.4f}, MAE={test_metrics["mae"]:.4f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.results_dir, f'pred_vs_true_{self.config.gnn_type}_{stamp}.png'), dpi=300)
        plt.close()

        # 2. Residual histogram
        residual = targets - predictions
        plt.figure(figsize=(10, 6))
        plt.hist(residual, bins=50, color='steelblue', alpha=0.7, edgecolor='k')
        plt.axvline(0, color='r', linestyle='--', linewidth=2, label='Perfect Prediction')
        plt.axvline(np.mean(residual), color='orange', linestyle='-', linewidth=2, 
                   label=f'Mean Residual: {np.mean(residual):.4f}')
        plt.xlabel('Residual (True - Predicted)')
        plt.ylabel('Count')
        plt.title(f'Residual Distribution - {self.config.gnn_type.upper()}\n(MAE={test_metrics["mae"]:.4f}, Std={np.std(residual):.4f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.results_dir, f'residual_hist_{self.config.gnn_type}_{stamp}.png'), dpi=300)
        plt.close()

        # 3. Prediction error distribution
        plt.figure(figsize=(10, 6))
        error_percent = np.abs((targets - predictions) / (targets + 1e-8)) * 100
        plt.hist(error_percent, bins=50, color='orange', alpha=0.7, edgecolor='k')
        plt.axvline(np.mean(error_percent), color='r', linestyle='--', linewidth=2, 
                   label=f'Mean Error: {np.mean(error_percent):.2f}%')
        plt.xlabel('Absolute Percentage Error (%)')
        plt.ylabel('Count')
        plt.title(f'Error Distribution - {self.config.gnn_type.upper()}\n(Mean Error: {np.mean(error_percent):.2f}%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.results_dir, f'error_dist_{self.config.gnn_type}_{stamp}.png'), dpi=300)
        plt.close()
        
        # 4. Prediction value distribution comparison
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.hist(targets, bins=50, alpha=0.7, label='Targets', color='blue')
        plt.xlabel('Value')
        plt.ylabel('Count')
        plt.title('Target Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.hist(predictions, bins=50, alpha=0.7, label='Predictions', color='red')
        plt.xlabel('Value')
        plt.ylabel('Count')
        plt.title('Prediction Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.results_dir, f'distribution_comparison_{self.config.gnn_type}_{stamp}.png'), dpi=300)
        plt.close()
    
    def plot_results(self, history: Dict[str, List[float]], test_metrics: Dict[str, float]):
        """Plot training results"""
        if not self.config.plot_training_curves:
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Training loss
        axes[0, 0].plot(history['train_loss'], label='Train Loss', color='blue', linewidth=2)
        axes[0, 0].plot(history['val_loss'], label='Val Loss', color='orange', linewidth=2)
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].set_title(f'Training and Validation Loss - {self.config.gnn_type.upper()}')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # MAE
        axes[0, 1].plot(history['train_mae'], label='Train MAE', color='green', linewidth=2)
        axes[0, 1].plot(history['val_mae'], label='Val MAE', color='red', linewidth=2)
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('MAE')
        axes[0, 1].set_title(f'Mean Absolute Error - {self.config.gnn_type.upper()}')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # R2 Score
        axes[1, 0].plot(history['train_r2'], label='Train R²', color='purple', linewidth=2)
        axes[1, 0].plot(history['val_r2'], label='Val R²', color='brown', linewidth=2)
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('R² Score')
        axes[1, 0].set_title(f'R² Score - {self.config.gnn_type.upper()}')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Test metrics
        metrics_text = f"Test Metrics ({self.config.gnn_type.upper()}):\n"
        for metric, value in test_metrics.items():
            if value == float('inf'):
                metrics_text += f"{metric.upper()}: inf\n"
            else:
                metrics_text += f"{metric.upper()}: {value:.6f}\n"
        
        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes, 
                       fontsize=12, verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        axes[1, 1].set_title('Test Metrics')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plot_path = os.path.join(self.config.results_dir, f'training_results_{self.config.gnn_type}.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Training results plot saved to: {plot_path}")
        csv_path = os.path.join(self.config.results_dir,
                           f'training_results_{self.config.gnn_type}.csv')

        # Convert history to DataFrame (automatically fill epoch index)
        df = pd.DataFrame(history)
        df.insert(0, 'epoch', range(1, len(df) + 1))  # First column is epoch, starting from 1
        df.to_csv(csv_path, index=False, float_format='%.6f')

        self.logger.info(f"Training history saved to: {csv_path}")
    
    def run_complete_pipeline(self):
        """Run complete training pipeline"""
        self.logger.info(f"Starting complete improved GNN+Transformer node delay prediction training pipeline - {self.config.gnn_type.upper()}")
        
        try:
            # 1. Prepare data
            self.logger.info("Step 1/5: Prepare data")
            self.prepare_data()
            
            # 2. Create model
            self.logger.info("Step 2/5: Create model")
            self.create_model()
            
            # 3. Train model
            self.logger.info("Step 3/5: Train model")
            history = self.train_model()
            
            # 4. Evaluate model
            self.logger.info("Step 4/5: Evaluate model")
            test_metrics = self.evaluate_model()
            
            # 5. Plot results
            self.logger.info("Step 5/5: Plot results")
            self.plot_results(history, test_metrics)
            
            # Save training summary
            def convert_to_serializable(obj):
                """Convert numpy types to Python native types"""
                if isinstance(obj, (np.integer, np.floating)):
                    return obj.item()
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_to_serializable(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                else:
                    return obj
            
            summary = {
                'model_name': self.model.model_name,
                'gnn_type': self.config.gnn_type,
                'data_config': {
                    'node_feature_dim': int(self.config.data_config.node_feature_dim),
                    'edge_feature_dim': int(self.config.data_config.edge_feature_dim),
                    'train_ratio': float(self.config.data_config.train_ratio)
                },
                'model_config': convert_to_serializable(self.config.model_config),
                'final_metrics': convert_to_serializable(test_metrics),
                'model_path': self.config.model_save_path,
                'fixes_applied': [
                    'Disabled ValueRangeCalibrator',
                    'Disabled OutputProcessor', 
                    'Improved loss function weights',
                    'Added gradient monitoring',
                    'Added prediction validation',
                    'Increased learning rate',
                    'Added gradient clipping'
                ]
            }
            
            summary_path = os.path.join(self.config.results_dir, f'training_summary_{self.config.gnn_type}.json')
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"GNN+Transformer {self.config.gnn_type.upper()} node delay prediction training completed!")
            self.logger.info(f"Training summary saved to: {summary_path}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Training pipeline failed: {e}")
            import traceback
            self.logger.error(f"Detailed error information: {traceback.format_exc()}")
            return None

def compare_gnn_models(base_dirs: List[str], gnn_types: List[str] = None):
    """
    Compare performance of different GNN models 
    
    Args:
        base_dirs: Dataset directory list
        gnn_types: List of GNN types to compare
    """
    if gnn_types is None:
        gnn_types = ['gcn', 'sage', 'gin']
    
    results = {}
    
    for gnn_type in gnn_types:
        print(f"\n{'='*60}")
        print(f"Training {gnn_type.upper()} model")
        print(f"{'='*60}")
        
        # Create configuration
        config = GNNTransformerTrainingConfig(
            raw_input_dirs=base_dirs,
            model_save_path=f"./models/{gnn_type}_delay_model.pt",
            results_dir=f"./results_{gnn_type}",
            gnn_type=gnn_type,
            use_pretrained_data=True,
            plot_training_curves=True,
            save_predictions=True,
            enable_gradient_monitoring=False,
            enable_prediction_validation=True
        )
        
        # Create trainer
        trainer = GNNTransformerTrainer(config)
        
        # Run training
        result = trainer.run_complete_pipeline()
        
        if result:
            results[gnn_type] = result['final_metrics']
            print(f"✅ {gnn_type.upper()} model training completed")
            print(f"R² Score: {result['final_metrics']['r2']:.4f}")
            print(f"MAE: {result['final_metrics']['mae']:.4f}")
        else:
            print(f"❌ {gnn_type.upper()} model training failed")
    
    # Compare results
    if results:
        print(f"\n{'='*60}")
        print("Model performance comparison")
        print(f"{'='*60}")
        
        comparison_df = pd.DataFrame(results).T
        comparison_df = comparison_df.sort_values('r2', ascending=False)
        
        print(comparison_df.round(6))
        
        # Save comparison results
        os.makedirs('./results', exist_ok=True)
        comparison_df.to_csv('./results/model_comparison.csv')
        print(f"\nComparison results saved to: ./results/model_comparison.csv")
        
        # Find best model
        best_model = comparison_df.index[0]
        best_r2 = comparison_df.loc[best_model, 'r2']
        print(f"\n🏆 Best model: {best_model.upper()} (R² = {best_r2:.4f})")
    
    return results

if __name__ == "__main__":
    # Base directory configuration
    BASE_DIRS = [
        "/data2/project_share/dataset_baseline/s713/workspace",
        "/data2/project_share/dataset_baseline/s44/workspace",
        "/data2/project_share/dataset_baseline/apb4_rng/workspace",
        "/data2/project_share/dataset_baseline/gcd/workspace",
        "/data2/project_share/dataset_baseline/s1238/workspace",
        "/data2/project_share/dataset_baseline/s1488/workspace",
        "/data2/project_share/dataset_baseline/apb4_archinfo/workspace",
        "/data2/project_share/dataset_baseline/apb4_ps2/workspace",
        "/data2/project_share/dataset_baseline/s9234/workspace",
        "/data2/project_share/dataset_baseline/apb4_timer/workspace",
        "/data2/project_share/dataset_baseline/s13207/workspace",
        "/data2/project_share/dataset_baseline/apb4_i2c/workspace",
        "/data2/project_share/dataset_baseline/s5378/workspace",
        "/data2/project_share/dataset_baseline/apb4_pwm/workspace",
        "/data2/project_share/dataset_baseline/apb4_wdg/workspace",
        "/data2/project_share/dataset_baseline/apb4_clint/workspace",
        "/data2/project_share/dataset_baseline/ASIC/workspace",
        "/data2/project_share/dataset_baseline/s15850/workspace",
        "/data2/project_share/dataset_baseline/apb4_uart/workspace",
        "/data2/project_share/dataset_baseline/s38417/workspace",
        "/data2/project_share/dataset_baseline/s35932/workspace",
        "/data2/project_share/dataset_baseline/s38584/workspace",
        "/data2/project_share/dataset_baseline/BM64/workspace",
        "/data2/project_share/dataset_baseline/picorv32/workspace",
        "/data2/project_share/dataset_baseline/PPU/workspace",
        "/data2/project_share/dataset_baseline/blabla/workspace",
        "/data2/project_share/dataset_baseline/aes_core/workspace",
        "/data2/project_share/dataset_baseline/aes/workspace",
        "/data2/project_share/dataset_baseline/salsa20/workspace",
        "/data2/project_share/dataset_baseline/jpeg_encoder/workspace",
        "/data2/project_share/dataset_baseline/eth_top/workspace"
    ]
    
    # Select GNN types to train
    GNN_TYPES = ['sage', 'gin', 'gcn']  
    
    print("🚀 Starting GNN+Transformer node delay prediction training")
    print(f"📊 Will train the following GNN types: {', '.join(GNN_TYPES)}")
    print(f"📁 Dataset directory count: {len(BASE_DIRS)}")
    
    # Compare different GNN models
    results = compare_gnn_models(BASE_DIRS, GNN_TYPES)
    
    if results:
        print("\n🎉 All model training completed!")
        print("📈 Please check each model's results directory and comparison results file")
    else:
        print("\n❌ Model training failed, please check error messages")