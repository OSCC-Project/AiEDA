#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : transformer_trainer.py
@Author : yhqiu
@Desc : Training module for path delay prediction
"""
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingLR
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from tqdm import tqdm
import json
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from transformer_config import ModelConfig
from transformer_model import PathDelayPredictor


class EarlyStopping:
    """Early stopping to stop training when validation loss doesn't improve"""
    
    def __init__(self, patience: int = 7, min_delta: float = 0, restore_best_weights: bool = True):
        """
        Initialize early stopping.
        
        Args:
            patience: Number of epochs with no improvement after which training will be stopped
            min_delta: Minimum change in the monitored quantity to qualify as an improvement
            restore_best_weights: Whether to restore model weights from the epoch with the best value
        """
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights
        self.best_loss = None
        self.counter = 0
        self.best_weights = None
        
    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        """
        Check if training should be stopped.
        
        Args:
            val_loss: Current validation loss
            model: Model to potentially save weights from
            
        Returns:
            True if training should be stopped, False otherwise
        """
        if self.best_loss is None:
            self.best_loss = val_loss
            self.save_checkpoint(model)
        elif val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            self.save_checkpoint(model)
        else:
            self.counter += 1
            
        if self.counter >= self.patience:
            if self.restore_best_weights:
                model.load_state_dict(self.best_weights)
            return True
        return False
    
    def save_checkpoint(self, model: nn.Module) -> None:
        """Save model weights."""
        self.best_weights = model.state_dict().copy()


class MetricsCalculator:
    """Calculator for various regression metrics"""
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate regression metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        
        # Calculate R² score
        try:
            r2 = r2_score(y_true, y_pred)
        except:
            r2 = 0.0
            
        # Calculate MAPE (Mean Absolute Percentage Error)
        try:
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        except:
            mape = float('inf')
            
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'mape': mape
        }


class PathDelayTrainer:
    """Trainer for path delay prediction model"""
    
    def __init__(self, config: ModelConfig):
        """
        Initialize trainer.
        
        Args:
            config: Model configuration
        """
        self.config = config
        self.device = torch.device(config.device)
        
        # Initialize model
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_metrics = []
        self.val_metrics = []
        
        # Early stopping
        self.early_stopping = EarlyStopping(patience=10, min_delta=0.001)
        
        # Ensure checkpoint directory exists
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        
    def build_model(self, input_dim: int, feature_dim: int) -> None:
        """
        Build and initialize model.
        
        Args:
            input_dim: Input feature dimension
            feature_dim: Maximum sequence length
        """
        self.model = PathDelayPredictor(
            input_dim=input_dim,
            hidden_dim=self.config.hidden_dim,
            num_layers=self.config.num_layers,
            num_heads=self.config.num_heads,
            feature_dim=feature_dim,
            mlp_hidden_dim=self.config.mlp_hidden_dim,
            output_dim=self.config.output_dim,
            dropout=self.config.dropout
        ).to(self.device)
        
        # Initialize optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        
        # Initialize scheduler
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        # Initialize loss function
        self.criterion = nn.MSELoss()
        
        print(f"Model built with {sum(p.numel() for p in self.model.parameters()):,} parameters")
        
    def train_epoch(self, train_loader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """
        Train for one epoch.
        
        Args:
            train_loader: Training data loader
            
        Returns:
            Tuple of (average loss, metrics dictionary)
        """
        self.model.train()
        total_loss = 0.0
        all_predictions = []
        all_targets = []
        
        progress_bar = tqdm(train_loader, desc="Training")
        
        for batch_idx, (features, targets) in enumerate(progress_bar):
            features = features.to(self.device)
            targets = targets.to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            predictions = self.model(features)
            loss = self.criterion(predictions, targets)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            # Update parameters
            self.optimizer.step()
            
            # Accumulate loss and predictions
            total_loss += loss.item()
            all_predictions.extend(predictions.cpu().detach().numpy())
            all_targets.extend(targets.cpu().detach().numpy())
            
            # Update progress bar
            progress_bar.set_postfix({'loss': loss.item()})
        
        # Calculate metrics
        avg_loss = total_loss / len(train_loader)
        metrics = MetricsCalculator.calculate_metrics(
            np.array(all_targets), 
            np.array(all_predictions)
        )
        
        return avg_loss, metrics
    
    def validate_epoch(self, val_loader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """
        Validate for one epoch.
        
        Args:
            val_loader: Validation data loader
            
        Returns:
            Tuple of (average loss, metrics dictionary)
        """
        self.model.eval()
        total_loss = 0.0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            progress_bar = tqdm(val_loader, desc="Validation")
            
            for features, targets in progress_bar:
                features = features.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                predictions = self.model(features)
                loss = self.criterion(predictions, targets)
                
                # Accumulate loss and predictions
                total_loss += loss.item()
                all_predictions.extend(predictions.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
                
                # Update progress bar
                progress_bar.set_postfix({'loss': loss.item()})
        
        # Calculate metrics
        avg_loss = total_loss / len(val_loader)
        metrics = MetricsCalculator.calculate_metrics(
            np.array(all_targets), 
            np.array(all_predictions)
        )
        
        return avg_loss, metrics
    
    def train(
        self, 
        train_loader: DataLoader, 
        val_loader: DataLoader,
        input_dim: int,
        feature_dim: int
    ) -> Dict[str, List]:
        """
        Train the model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            input_dim: Input feature dimension
            feature_dim: Maximum sequence length
            
        Returns:
            Training history dictionary
        """
        # Build model
        self.build_model(input_dim, feature_dim)
        
        print(f"Starting training for {self.config.epochs} epochs...")
        print(f"Device: {self.device}")
        
        best_val_loss = float('inf')
        
        for epoch in range(self.config.epochs):
            print(f"\\nEpoch {epoch+1}/{self.config.epochs}")
            print("-" * 50)
            
            # Training phase
            train_loss, train_metrics = self.train_epoch(train_loader)
            self.train_losses.append(train_loss)
            self.train_metrics.append(train_metrics)
            
            # Validation phase
            val_loss, val_metrics = self.validate_epoch(val_loader)
            self.val_losses.append(val_loss)
            self.val_metrics.append(val_metrics)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Print epoch results
            print(f"Train Loss: {train_loss:.6f}, Train RMSE: {train_metrics['rmse']:.6f}")
            print(f"Val Loss: {val_loss:.6f}, Val RMSE: {val_metrics['rmse']:.6f}")
            print(f"Val R²: {val_metrics['r2']:.4f}, Val MAE: {val_metrics['mae']:.6f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_checkpoint(epoch, val_loss, is_best=True)
                print(f"New best model saved with validation loss: {val_loss:.6f}")
            
            # Early stopping
            if self.early_stopping(val_loss, self.model):
                print(f"Early stopping triggered at epoch {epoch+1}")
                break
        
        # Save final model
        self.save_checkpoint(epoch, val_loss, is_best=False)
        
        # Save training history
        self.save_training_history()
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics
        }
    
    def save_checkpoint(self, epoch: int, loss: float, is_best: bool = False) -> None:
        """
        Save model checkpoint.
        
        Args:
            epoch: Current epoch
            loss: Current loss
            is_best: Whether this is the best model so far
        """
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'loss': loss,
            'config': self.config.to_dict()
        }
        
        # Save current checkpoint
        checkpoint_path = os.path.join(self.config.checkpoint_dir, 'last_checkpoint.pth')
        torch.save(checkpoint, checkpoint_path)
        
        # Save best checkpoint
        if is_best:
            best_path = os.path.join(self.config.checkpoint_dir, 'best_checkpoint.pth')
            torch.save(checkpoint, best_path)
    
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """
        Load model checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        # Load optimizer state
        if self.optimizer is not None:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        # Load scheduler state
        if self.scheduler is not None:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        print(f"Checkpoint loaded from {checkpoint_path}")
        print(f"Epoch: {checkpoint['epoch']}, Loss: {checkpoint['loss']:.6f}")
    
    def save_training_history(self) -> None:
        """Save training history to JSON file."""
        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics
        }
        
        history_path = os.path.join(self.config.checkpoint_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"Training history saved to {history_path}")
    
    def plot_training_history(self, save_path: Optional[str] = None) -> None:
        """
        Plot training history.
        
        Args:
            save_path: Optional path to save the plot
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        epochs = range(1, len(self.train_losses) + 1)
        
        # Plot losses
        ax1.plot(epochs, self.train_losses, 'b-', label='Training Loss')
        ax1.plot(epochs, self.val_losses, 'r-', label='Validation Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Plot RMSE
        train_rmse = [m['rmse'] for m in self.train_metrics]
        val_rmse = [m['rmse'] for m in self.val_metrics]
        ax2.plot(epochs, train_rmse, 'b-', label='Training RMSE')
        ax2.plot(epochs, val_rmse, 'r-', label='Validation RMSE')
        ax2.set_title('Training and Validation RMSE')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('RMSE')
        ax2.legend()
        ax2.grid(True)
        
        # Plot R²
        train_r2 = [m['r2'] for m in self.train_metrics]
        val_r2 = [m['r2'] for m in self.val_metrics]
        ax3.plot(epochs, train_r2, 'b-', label='Training R²')
        ax3.plot(epochs, val_r2, 'r-', label='Validation R²')
        ax3.set_title('Training and Validation R²')
        ax3.set_xlabel('Epoch')
        ax3.set_ylabel('R²')
        ax3.legend()
        ax3.grid(True)
        
        # Plot MAE
        train_mae = [m['mae'] for m in self.train_metrics]
        val_mae = [m['mae'] for m in self.val_metrics]
        ax4.plot(epochs, train_mae, 'b-', label='Training MAE')
        ax4.plot(epochs, val_mae, 'r-', label='Validation MAE')
        ax4.set_title('Training and Validation MAE')
        ax4.set_xlabel('Epoch')
        ax4.set_ylabel('MAE')
        ax4.legend()
        ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training history plot saved to {save_path}")
        
        plt.show()
    
    def predict(self, data_loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on data.
        
        Args:
            data_loader: Data loader for prediction
            
        Returns:
            Tuple of (predictions, targets)
        """
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for features, targets in tqdm(data_loader, desc="Predicting"):
                features = features.to(self.device)
                targets = targets.to(self.device)
                
                predictions = self.model(features)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
        
        return np.array(all_predictions), np.array(all_targets)


# Usage example
if __name__ == "__main__":
    
    # Create model configuration
    config = ModelConfig(
        hidden_dim=64,
        num_layers=4,
        num_heads=8,
        mlp_hidden_dim=128,
        learning_rate=0.001,
        epochs=100,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    # Create trainer
    trainer = PathDelayTrainer(config)
    
    print("Trainer initialized successfully!")
    print(f"Configuration: {config}")