#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : tabnet_trainer.py
@Author : yhqiu
@Desc : TabNet trainer for wirelength prediction
'''
import pandas as pd
import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
import time
import logging
from typing import Dict, Any, Tuple, Optional, Union, List
from tqdm import tqdm
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from tabnet_config import DataConfig, ModelConfig
from tabnet_process import DataProcessor
from tabnet_model import (
    ViaPredictor, 
    BaselineWirelengthPredictor, 
    WithViaWirelengthPredictor,
    WithPredViaWirelengthPredictor
)


class TrainingCallback:
    """Training callback for progress tracking"""
    
    def __init__(self, pbar, history, logger):
        self.pbar = pbar
        self.trainer = None
        self.epoch_count = 0
        self.history = history
        self.logger = logger

    def set_trainer(self, trainer):
        self.trainer = trainer

    def on_train_begin(self, logs=None):
        if logs is None:
            logs = {}
        self.pbar.reset()
        self.epoch_count = 0

    def on_train_end(self, logs=None):
        if logs is None:
            logs = {}
        self.pbar.close()

    def on_epoch_begin(self, epoch, logs=None):
        """Called at the beginning of each epoch"""
        if logs is None:
            logs = {}

    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}

        self.epoch_count += 1

        # Record training history
        train_loss = logs.get('loss', 0)
        val_loss = logs.get('val_rmse', 0)

        self.history['train_loss'].append(train_loss)
        self.history['val_loss'].append(val_loss)

        if self.epoch_count % 10 == 0:
            self.logger.info(
                f"Epoch {epoch} | loss: {train_loss:.5f} | val_rmse: {val_loss:.5f}")

        self.pbar.update(1)
        self.pbar.set_postfix({
            'loss': f"{train_loss:.4f}",
            'val_rmse': f"{val_loss:.4f}"
        })

    def on_batch_begin(self, batch, logs=None):
        """Called at the beginning of each batch"""
        if logs is None:
            logs = {}

    def on_batch_end(self, batch, logs=None):
        """Called at the end of each batch"""
        if logs is None:
            logs = {}


class TabNetTrainer:
    """TabNet trainer for two-stage wirelength prediction"""
    
    def __init__(self, data_config: DataConfig, model_config: ModelConfig):
        """
        Initialize trainer
        
        Args:
            data_config: Data configuration
            model_config: Model configuration
        """
        self.model_config = model_config
        self.data_config = data_config
        
        # Initialize data processor
        self.data_processor = DataProcessor(self.data_config)
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self.via_model = None
        self.baseline_model = None
        self.with_via_model = None
        self.with_pred_via_model = None

    def train(self) -> Dict[str, Any]:
        """Train complete two-stage prediction system"""
        self.logger.info("=== Starting Two-Stage Wirelength Ratio Prediction System Training ===")

        # Load and preprocess data
        data_path = self.data_config.model_input_file
        data_dict = self.data_processor.load_and_preprocess_data(data_path)

        if self.model_config.do_train:
            # Train via_num prediction model
            X_via_train, y_via_train = data_dict['via_train']
            self.train_via_model(X_via_train, y_via_train)

            # Train baseline wirelength ratio model
            X_wl_baseline_train, y_wl_train = data_dict['wl_baseline_train']
            self.train_baseline_model(X_wl_baseline_train, y_wl_train)

            # Train wirelength ratio model with real via_num
            X_wl_with_real_via_train, y_wl_train_real = data_dict['wl_with_real_via_train']
            self.train_with_via_model(X_wl_with_real_via_train, y_wl_train_real)

            # Use predicted via num to replace real via num, then train wirelength ratio model with predicted via_num
            X_wl_with_pred_via_train = X_wl_with_real_via_train.copy()
            X_wl_with_pred_via_train[:, -1] = self.via_model.predict(X_via_train).reshape(-1)
            self.train_with_pred_via_model(X_wl_with_pred_via_train, y_wl_train_real)

        return data_dict

    def train_via_model(self, X_train: np.ndarray, y_train: np.ndarray) -> ViaPredictor:
        """Train via_num prediction model"""
        self.logger.info("=== Starting Via Prediction Model Training ===")

        # Create model
        self.via_model = ViaPredictor(self.model_config.via_model_config)

        # Train with progress tracking
        self._train_with_progress(
            self.via_model, X_train, y_train,
            self.model_config.via_model_config,
            "Via Prediction"
        )

        return self.via_model

    def train_baseline_model(self, X_train: np.ndarray, y_train: np.ndarray) -> BaselineWirelengthPredictor:
        """Train baseline wirelength prediction model"""
        self.logger.info("=== Starting Baseline Model Training ===")

        # Create model
        self.baseline_model = BaselineWirelengthPredictor(self.model_config.baseline_model_config)

        # Train with progress tracking
        self._train_with_progress(
            self.baseline_model, X_train, y_train,
            self.model_config.baseline_model_config,
            "Baseline"
        )

        return self.baseline_model

    def train_with_via_model(self, X_train: np.ndarray, y_train: np.ndarray) -> WithViaWirelengthPredictor:
        """Train wirelength prediction model with via features"""
        self.logger.info("=== Starting With Via Model Training ===")

        # Create model
        self.with_via_model = WithViaWirelengthPredictor(self.model_config.with_via_model_config)

        # Train with progress tracking
        self._train_with_progress(
            self.with_via_model, X_train, y_train,
            self.model_config.with_via_model_config,
            "WithVia"
        )

        return self.with_via_model
    
    def train_with_pred_via_model(self, X_train: np.ndarray, y_train: np.ndarray) -> WithPredViaWirelengthPredictor:
        """Train wirelength prediction model with predicted via features"""
        self.logger.info("=== Starting With Predicted Via Model Training ===")

        # Create model
        self.with_pred_via_model = WithPredViaWirelengthPredictor(self.model_config.with_via_model_config)

        # Train with progress tracking
        self._train_with_progress(
            self.with_pred_via_model, X_train, y_train,
            self.model_config.with_via_model_config,
            "WithPredictedVia"
        )

        return self.with_pred_via_model

    def _train_with_progress(self, model, X_train: np.ndarray, y_train: np.ndarray, 
                            config: Dict[str, Any], model_name: str) -> None:
        """Training method with progress bar"""
        # Data splitting for validation
        X_train_final, X_val, y_train_final, y_val = train_test_split(
            X_train, y_train,
            test_size=self.data_config.val_size,
            random_state=self.data_config.random_state
        )

        # Create progress bar
        max_epochs = config.get('max_epochs', 100)
        pbar = tqdm(total=max_epochs, desc=f"Training {model_name} model")

        # Training history record
        history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': []
        }

        # Create callback
        callback = TrainingCallback(pbar, history, self.logger)

        # Train model
        model.fit(
            X_train=X_train_final,
            y_train=y_train_final,
            X_val=X_val,
            y_val=y_val,
            callbacks=[callback]
        )

    def evaluate(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate model performance"""
        if not self.model_config.do_eval:
            return {}

        self.logger.info("=== Starting Model Evaluation ===")

        results = {}

        # Evaluate via model
        if self.via_model is not None:
            X_via_test, y_via_test = data_dict['via_test']
            via_results = self.via_model.evaluate(X_via_test, y_via_test)
            via_pred = self.via_model.predict(X_via_test)
            results['via_results'] = via_results
            results['via_pred'] = via_pred

        # Evaluate baseline model
        if self.baseline_model is not None:
            X_wl_baseline_test, y_wl_test = data_dict['wl_baseline_test']
            baseline_results = self.baseline_model.evaluate(X_wl_baseline_test, y_wl_test)
            baseline_pred = self.baseline_model.predict(X_wl_baseline_test)
            results['baseline_results'] = baseline_results
            results['baseline_pred'] = baseline_pred
            results['y_wl_test'] = y_wl_test

        # Evaluate model with real via
        if self.with_via_model is not None:
            X_wl_with_real_via_test, _ = data_dict['wl_with_real_via_test']
            real_via_results = self.with_via_model.evaluate(X_wl_with_real_via_test, y_wl_test)
            real_via_pred = self.with_via_model.predict(X_wl_with_real_via_test)
            results['real_via_results'] = real_via_results
            results['real_via_pred'] = real_via_pred
        
        # Evaluate model with predicted via
        if self.with_pred_via_model is not None:
            X_wl_with_pred_via_test, _ = data_dict['wl_with_real_via_test']
            X_wl_with_pred_via_test[:, -1] = results['via_pred'].reshape(-1)
            with_pred_via_results = self.with_pred_via_model.evaluate(X_wl_with_pred_via_test, y_wl_test)
            with_pred_via_pred = self.with_pred_via_model.predict(X_wl_with_pred_via_test)
            results['with_pred_via_results'] = with_pred_via_results
            results['with_pred_via_pred'] = with_pred_via_pred 
            
        # Print comparison results
        self._print_comparison_results(results)
        
        # Generate plots
        self._generate_evaluation_plots(results, data_dict)

        return results

    def _print_comparison_results(self, results: Dict[str, Any]) -> None:
        """Print model comparison results"""
        self.logger.info("=== Wirelength Prediction Model Performance Comparison ===")
        metrics = ['RMSE', 'MAE', 'R2', 'MAPE']
        self.logger.info(f"{'Metric':<8} | {'Baseline':<12} | {'Real Via Model':<12} | {'Predicted Via Model':<12}")
        self.logger.info("-"*60)
        
        for metric in metrics:
            baseline = results['baseline_results'].get(metric, 0)
            real_via = results['real_via_results'].get(metric, 0)
            pred_via = results['with_pred_via_results'].get(metric, 0)
            
            if metric == 'R2':
                real_diff = ((real_via - baseline) / abs(baseline)) * 100 if baseline != 0 else float('inf')
                pred_diff = ((pred_via - baseline) / abs(baseline)) * 100 if baseline != 0 else float('inf')
                real_diff_str = f"{real_diff:+.2f}%"
                pred_diff_str = f"{pred_diff:+.2f}%"     
            else:
                real_diff = ((real_via - baseline) / baseline) * 100 if baseline != 0 else float('inf')
                pred_diff = ((pred_via - baseline) / baseline) * 100 if baseline != 0 else float('inf')
                real_diff_str = f"{real_diff:+.2f}%"
                pred_diff_str = f"{pred_diff:+.2f}%"      
            
            self.logger.info(f"{metric:<8} | {baseline:<12.4f} | {real_via:<12.4f} ({real_diff_str}) | {pred_via:<12.4f} ({pred_diff_str})")

    def _generate_evaluation_plots(self, results: Dict[str, Any], data_dict: Dict[str, Any]) -> None:
        """Generate evaluation plots"""
        # Via prediction analysis plot
        y_via_test = data_dict['via_test'][1]
        via_pred = results.get('via_pred', None)
        if y_via_test is not None and via_pred is not None:
            self._plot_via_prediction_analysis(y_via_test, via_pred, self.data_config.plot_dir)
        
        # Wirelength error distribution plot
        y_wl_test = results.get('y_wl_test', None)
        baseline_pred = results.get('baseline_pred', None)
        with_pred_via_pred = results.get('with_pred_via_pred', None)
        if all(x is not None for x in [y_wl_test, baseline_pred, with_pred_via_pred]):
            self._plot_wl_error_distribution(y_wl_test, baseline_pred, with_pred_via_pred, self.data_config.plot_dir)

    def _plot_wl_error_distribution(self, y_test, baseline_pred, pred_via_pred, save_dir):
        """KDE plot of error distribution for baseline and predicted via"""
        # Ensure all inputs are 1D
        y_test = np.asarray(y_test).reshape(-1)
        baseline_pred = np.asarray(baseline_pred).reshape(-1)
        pred_via_pred = np.asarray(pred_via_pred).reshape(-1)

        baseline_errors = baseline_pred - y_test
        pred_via_errors = pred_via_pred - y_test

        plt.figure(figsize=(10, 8))
        colors = ['#1f77b4', '#2ca02c']
        labels = ['without via_num', 'with via_num']

        sns.histplot(baseline_errors, kde=True, color=colors[0], label=labels[0], alpha=0.6, bins=20)
        sns.histplot(pred_via_errors, kde=True, color=colors[1], label=labels[1], alpha=0.6, bins=20)
        plt.axvline(x=0, color='r', linestyle='--', linewidth=2)
        plt.xlabel('Prediction Error (predict - actual)', fontsize=22)
        plt.ylabel('Frequency', fontsize=22)
        plt.title('Prediction Error Distribution Comparison', fontsize=25, fontweight='bold')

        # Remove duplicate legend entries
        handles, labels_ = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels_, handles))
        plt.legend(by_label.values(), by_label.keys(), prop={'size': 20}, loc='upper right')

        plt.tight_layout()
        save_path = os.path.join(save_dir, 'model_error_distribution.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_via_prediction_analysis(self, y_test, y_pred, save_dir):
        """Plot via_num prediction result analysis"""
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Print original data point count
        total_points = len(y_test)
        
        # Data sampling: if data volume exceeds 30000, randomly sample
        max_points = 30000
        if total_points > max_points:
            indices = np.random.choice(total_points, max_points, replace=False)
            y_test_sampled = y_test[indices]
            y_pred_sampled = y_pred[indices]
        else:
            y_test_sampled = y_test
            y_pred_sampled = y_pred
        
        # Set font size
        plt.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 18,
            'axes.labelsize': 16,
            'xtick.labelsize': 15,
            'ytick.labelsize': 15,
            'legend.fontsize': 15
        })
        
        try:
            plt.figure(figsize=(10, 8))
            plt.scatter(y_test_sampled, y_pred_sampled, 
                       alpha=0.5,  # Set transparency
                       s=20,       # Set point size
                       c='blue',   # Set point color
                       label='Predicted points')
            
            # Add perfect prediction line
            max_val = max(np.max(y_test_sampled), np.max(y_pred_sampled))
            min_val = min(np.min(y_test_sampled), np.min(y_pred_sampled))
            plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Ideal line')
            
            plt.xlabel('Actual Via Number', fontsize=16)
            plt.ylabel('Predicted Via Number', fontsize=16)
            plt.title('TabNet: Via Number Prediction', fontsize=18, fontweight='bold')
            
            # Add R² value to the plot
            r2 = r2_score(y_test_sampled, y_pred_sampled)
            plt.text(0.05, 0.95, f'R² = {r2:.4f}', 
                    transform=plt.gca().transAxes, 
                    fontsize=14,
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
            
            # Add legend
            plt.legend()
            
            plt.tight_layout()
            plt.savefig(save_dir / 'tabnet_via_prediction.png', 
                       dpi=300,
                       bbox_inches='tight',
                       format='png')
            plt.close()
        
            self.logger.info(f"Via number prediction analysis plot saved: {save_dir}")
            
        except Exception as e:
            self.logger.error(f"Error occurred during plotting: {str(e)}")
            raise

    def save_models(self, save_dir: str) -> None:
        """
        Save all trained models
        
        Args:
            save_dir: Directory to save models
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        if self.via_model is not None:
            via_path = save_dir / "via_model.zip"
            self.via_model.save_model(str(via_path))
            
        if self.baseline_model is not None:
            baseline_path = save_dir / "baseline_model.zip"
            self.baseline_model.save_model(str(baseline_path))
            
        if self.with_via_model is not None:
            with_via_path = save_dir / "with_via_model.zip"
            self.with_via_model.save_model(str(with_via_path))
            
        if self.with_pred_via_model is not None:
            with_pred_via_path = save_dir / "with_pred_via_model.zip"
            self.with_pred_via_model.save_model(str(with_pred_via_path))
        
        self.logger.info(f"All models saved to {save_dir}")

    def load_models(self, save_dir: str) -> None:
        """
        Load all trained models
        
        Args:
            save_dir: Directory to load models from
        """
        save_dir = Path(save_dir)
        
        # Load via model
        via_path = save_dir / "via_model.zip"
        if via_path.exists():
            self.via_model = ViaPredictor(self.model_config.via_model_config)
            self.via_model.load_model(str(via_path))
            
        # Load baseline model
        baseline_path = save_dir / "baseline_model.zip"
        if baseline_path.exists():
            self.baseline_model = BaselineWirelengthPredictor(self.model_config.baseline_model_config)
            self.baseline_model.load_model(str(baseline_path))
            
        # Load with via model
        with_via_path = save_dir / "with_via_model.zip"
        if with_via_path.exists():
            self.with_via_model = WithViaWirelengthPredictor(self.model_config.with_via_model_config)
            self.with_via_model.load_model(str(with_via_path))
            
        # Load with predicted via model
        with_pred_via_path = save_dir / "with_pred_via_model.zip"
        if with_pred_via_path.exists():
            self.with_pred_via_model = WithPredViaWirelengthPredictor(self.model_config.with_via_model_config)
            self.with_pred_via_model.load_model(str(with_pred_via_path))
        
        self.logger.info(f"Models loaded from {save_dir}")

    def predict(self, X_features: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Make predictions using trained models
        
        Args:
            X_features: Dictionary containing feature arrays for different models
                       Keys: 'via', 'baseline', 'with_via'
        
        Returns:
            Dictionary containing predictions from different models
        """
        predictions = {}
        
        # Via prediction
        if self.via_model is not None and 'via' in X_features:
            via_pred = self.via_model.predict(X_features['via'])
            predictions['via_pred'] = via_pred
        
        # Baseline prediction
        if self.baseline_model is not None and 'baseline' in X_features:
            baseline_pred = self.baseline_model.predict(X_features['baseline'])
            predictions['baseline_pred'] = baseline_pred
        
        # With via prediction (using real via)
        if self.with_via_model is not None and 'with_via' in X_features:
            with_via_pred = self.with_via_model.predict(X_features['with_via'])
            predictions['with_via_pred'] = with_via_pred
        
        # With predicted via prediction
        if (self.with_pred_via_model is not None and 
            'with_via' in X_features and 
            'via_pred' in predictions):
            # Replace last column (via_num) with predicted values
            X_with_pred_via = X_features['with_via'].copy()
            X_with_pred_via[:, -1] = predictions['via_pred'].reshape(-1)
            with_pred_via_pred = self.with_pred_via_model.predict(X_with_pred_via)
            predictions['with_pred_via_pred'] = with_pred_via_pred
        
        return predictions


if __name__ == "__main__":
    # Data configuration
    data_config = DataConfig(
        model_input_file="./iEDA_combined_nets_cleaned.csv",
        plot_dir="./analysis_plots",
        via_feature_columns=['width', 'height', 'pin_num', 'aspect_ratio',
                             'l_ness', 'rsmt', 'area', 'route_ratio_x',
                             'route_ratio_y'],
        wl_baseline_feature_columns=['width', 'height', 'pin_num', 'aspect_ratio',
                                     'l_ness', 'rsmt', 'area', 'route_ratio_x',
                                     'route_ratio_y'],
        wl_with_via_feature_columns=['width', 'height', 'pin_num', 'aspect_ratio',
                                     'l_ness', 'rsmt', 'area', 'route_ratio_x',
                                     'route_ratio_y', 'via_num'],
        test_size=0.2,
        random_state=42,
    )
    
    # Model configuration
    via_model_config = {
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
        'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
        'num_workers': 0,
        'pin_memory': True
    }
    baseline_model_config = {
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
        'num_workers': 0,
        'pin_memory': True
    }
    model_config = ModelConfig(
        do_train=True,
        do_eval=True,
        output_dir="./",
        via_model_config=via_model_config,
        baseline_model_config=baseline_model_config,
        with_via_model_config=baseline_model_config,
    )

    # Create trainer
    trainer = TabNetTrainer(
        data_config=data_config,
        model_config=model_config
    )

    # Train model
    data_dict = trainer.train()

    # Evaluate model
    results = trainer.evaluate(data_dict)
    
    # Save models
    trainer.save_models("./saved_models")