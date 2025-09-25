#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : gnn_delay_model.py
@Author : AI Assistant
@Desc : GNN delay prediction model implementation
'''
import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import (
    GCNConv, SAGEConv, GINConv, 
    global_mean_pool, global_max_pool, global_add_pool
)
from torch_geometric.data import Data, Batch
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from typing import Dict, Any, Tuple, Optional, Union, List
import logging
from tqdm import tqdm
import os


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer, supports longer sequences"""
    
    def __init__(self, d_model: int, max_len: int = 10000):
        super().__init__()
        self.d_model = d_model
        
        # Create positional encoding
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """Add positional encoding to input tensor"""
        x = x + self.pe[:x.size(0), :]
        return x


class GNNLayer(nn.Module):
    """GNN layer supporting multiple GNN variants"""
    
    def __init__(self, in_channels: int, out_channels: int, gnn_type: str = 'gcn', 
                 heads: int = 1, dropout: float = 0.1, edge_dim: int = None):
        super().__init__()
        self.gnn_type = gnn_type
        self.out_channels = out_channels
        
        if gnn_type == 'gcn':
            self.conv = GCNConv(in_channels, out_channels)
        elif gnn_type == 'sage':
            self.conv = SAGEConv(in_channels, out_channels)
        elif gnn_type == 'gin':
            # GIN requires MLP as edge update function
            mlp = nn.Sequential(
                nn.Linear(in_channels, out_channels),
                nn.ReLU(),
                nn.Linear(out_channels, out_channels)
            )
            self.conv = GINConv(mlp)
        else:
            raise ValueError(f"Unsupported GNN type: {gnn_type}")
        
        # Layer normalization and dropout
        self.layer_norm = nn.LayerNorm(out_channels)
        self.dropout = nn.Dropout(dropout)
        
        # Residual connection
        self.residual = (in_channels == out_channels)
        if self.residual:
            self.residual_proj = nn.Identity()
        else:
            self.residual_proj = nn.Linear(in_channels, out_channels)
    
    def forward(self, x, edge_index, edge_attr=None):
        """Forward pass"""
        residual = x
        
        # GNN convolution
        if self.gnn_type in ['gcn', 'sage']:
            x = self.conv(x, edge_index)
        elif self.gnn_type == 'gin':
            x = self.conv(x, edge_index)
        else:  # gat, transformer
            x = self.conv(x, edge_index)
        
        # Residual connection
        if self.residual:
            x = x + self.residual_proj(residual)
        
        # Layer normalization and activation
        x = self.layer_norm(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        return x


class FixedGNNTransformerModel(nn.Module):
    """Fixed GNN+Transformer model with removed components causing constant predictions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        
        # Input dimension configuration
        node_feature_dim = config.get('node_feature_dim', 9)
        edge_feature_dim = config.get('edge_feature_dim', 8)
        hidden_dim = config.get('hidden_dim', 128)
        num_layers = config.get('num_layers', 3)
        num_heads = config.get('num_heads', 8)
        dropout = config.get('dropout', 0.1)
        gnn_type = config.get('gnn_type', 'gcn')
        
        # Transformer parameters
        d_model = config.get('d_model', 128)
        nhead = config.get('nhead', 8)
        num_encoder_layers = config.get('num_encoder_layers', 3)
        dim_feedforward = config.get('dim_feedforward', 512)
        transformer_dropout = config.get('transformer_dropout', 0.1)
        
        # Edge feature processing
        self.edge_dim = hidden_dim // 2
        self.edge_encoder = nn.Linear(edge_feature_dim, self.edge_dim)
        
        # Node feature encoding
        self.node_encoder = nn.Sequential(
            nn.Linear(node_feature_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # GNN layer construction
        self.gnn_layers = nn.ModuleList()
        
        # First GNN layer
        self.gnn_layers.append(GNNLayer(
            hidden_dim, hidden_dim, gnn_type, num_heads, dropout, self.edge_dim
        ))
        
        # Subsequent GNN layers
        for _ in range(num_layers - 1):
            self.gnn_layers.append(GNNLayer(
                hidden_dim, hidden_dim, gnn_type, num_heads, dropout, self.edge_dim
            ))
        
        # Graph-level feature aggregation
        self.graph_pooling = config.get('graph_pooling', 'mean')  # mean, max, add
        
        # Transformer encoder
        self.pos_encoding = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=transformer_dropout,
            batch_first=True,
            norm_first=True  # Pre-norm for better training stability
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_encoder_layers)
        
        # Projection to transformer dimension
        self.output_projection = nn.Sequential(
            nn.Linear(hidden_dim, d_model),
            nn.LayerNorm(d_model),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Simplified node delay predictor - removed value range calibrator and output processor
        self.node_delay_predictor = nn.Sequential(
            nn.Linear(d_model, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, hidden_dim // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 4, 1)
        )
        
        # Add output scaling layer to match target value range
        self.output_scaling = nn.Parameter(torch.tensor(1.0))
        self.output_bias = nn.Parameter(torch.tensor(0.0))
    
    def forward(self, data):
        """Fixed forward pass"""
        x, edge_index, edge_attr = data.x, data.edge_index, data.edge_attr
        
        # Node feature encoding
        x = self.node_encoder(x)
        
        # Edge feature processing
        if edge_attr is not None:
            edge_attr = self.edge_encoder(edge_attr)
        
        # GNN feature extraction
        for gnn_layer in self.gnn_layers:
            x = gnn_layer(x, edge_index, edge_attr)
        
        # Projection to transformer dimension
        x = self.output_projection(x)
        
        # Transformer processing
        x = x.unsqueeze(0)  # Add sequence dimension
        x = self.pos_encoding(x)
        
        # Use gradient checkpointing to reduce memory usage
        if self.training and hasattr(torch.utils.checkpoint, 'checkpoint'):
            x = torch.utils.checkpoint.checkpoint(
                self.transformer_encoder, x, use_reentrant=False
            )
        else:
            x = self.transformer_encoder(x)
        
        x = x.squeeze(0)  # Remove sequence dimension
        
        # Node delay prediction
        node_delays = self.node_delay_predictor(x)  # (num_nodes, 1)
        
        # Apply learnable scaling and offset
        final_delays = node_delays * self.output_scaling + self.output_bias
        
        return final_delays.squeeze(-1)  # (num_nodes,)


class NodeDelayPredictor:
    """Fixed node delay predictor"""
    
    def __init__(self, config: Dict[str, Any], model_name: str = "FixedGNNTransformer_NodeDelay"):
        """
        Initialize fixed node delay prediction model
        
        Args:
            config: Model configuration dictionary
            model_name: Model name
        """
        self.config = config
        self.model_name = model_name
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        # Create model
        self._create_model()
    
    def _create_model(self) -> None:
        """Create fixed GNN+Transformer model"""
        self.logger.info(f"Creating fixed {self.model_name} model")
        
        # Get device
        device = self.config.get('device', 'cpu')
        
        # Create model
        self.model = FixedGNNTransformerModel(self.config)
        
        # Move to device
        self.model = self.model.to(device)
        self.logger.info(f"Model moved to device: {device}")
        
        # Print model information
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        self.logger.info(f"Total parameters: {total_params:,}")
        self.logger.info(f"Trainable parameters: {trainable_params:,}")
    
    def fit(self, train_loader, val_loader=None, callbacks=None) -> Dict[str, List[float]]:
        """
        Train fixed model
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            callbacks: Callback function list
        
        Returns:
            Dict: Training history
        """
        if self.model is None:
            raise ValueError("Model not initialized")
        
        device = self.config.get('device', 'cpu')
        
        # Get training parameters
        learning_rate = self.config.get('learning_rate', 0.001)
        weight_decay = self.config.get('weight_decay', 1e-4)
        max_epochs = self.config.get('max_epochs', 200)
        
        # Create optimizer
        grouped_parameters = self._get_grouped_parameters()
        optimizer = torch.optim.AdamW(
            grouped_parameters,
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.999),
            eps=1e-8
        )
        
        # Learning rate scheduler
        scheduler = self._get_scheduler(optimizer, train_loader, max_epochs)
        
        # Loss function
        criterion = self._get_loss_function()
        
        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'train_mae': [],
            'val_mae': [],
            'train_r2': [],
            'val_r2': []
        }
        
        # Early stopping and model saving
        best_val_loss = float('inf')
        best_val_mae = float('inf')
        patience_counter = 0
        patience = self.config.get('patience', 30)
        
        # Create progress bar
        pbar = tqdm(range(max_epochs), desc="Training", ncols=100)
        
        for epoch in pbar:
            # Training
            train_loss, train_mae, train_r2 = self._train_epoch(
                train_loader, optimizer, criterion, device, scheduler
            )
            
            # Validation
            if val_loader is not None:
                val_loss, val_mae, val_r2 = self._validate_epoch(
                    val_loader, criterion, device
                )
                
                # Learning rate scheduling
                if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    scheduler.step(val_loss)
                
                # Model saving
                is_best = val_loss < best_val_loss
                if is_best:
                    best_val_loss = val_loss
                    best_val_mae = val_mae
                    patience_counter = 0
                    
                    # Save best model
                    if self.config.get('save_best_model', True):
                        self._save_best_model(epoch, optimizer, scheduler, 
                                            train_loss, train_mae, train_r2,
                                            val_loss, val_mae, val_r2)
                else:
                    patience_counter += 1
                
                # Early stopping check
                if patience_counter >= patience:
                    self.logger.info(f"Early stopping at epoch {epoch}")
                    pbar.close()
                    break
            else:
                val_loss = val_mae = val_r2 = 0.0
            
            # Record history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_mae'].append(train_mae)
            history['val_mae'].append(val_mae)
            history['train_r2'].append(train_r2)
            history['val_r2'].append(val_r2)
            
            # Update progress bar
            pbar.set_postfix({
                'TrLoss': f'{train_loss:.4f}',
                'ValLoss': f'{val_loss:.4f}',
                'TrMAE': f'{train_mae:.4f}',
                'ValMAE': f'{val_mae:.4f}',
                'TrR²': f'{train_r2:.3f}',
                'ValR²': f'{val_r2:.3f}',
                'Patience': f'{patience_counter}/{patience}'
            })
            
            # Regular detailed output
            if epoch % 10 == 0:
                self.logger.info(
                    f"Epoch {epoch}: train_loss={train_loss:.4f}, "
                    f"val_loss={val_loss:.4f}, train_mae={train_mae:.4f}, "
                    f"val_mae={val_mae:.4f}, train_r2={train_r2:.4f}, val_r2={val_r2:.4f}"
                )
        
        pbar.close()
        return history
    
    def _train_epoch(self, train_loader, optimizer, criterion, device, scheduler=None):
        """Train one epoch"""
        self.model.train()
        total_loss = 0.0
        total_mae = 0.0
        total_r2 = 0.0
        num_batches = 0
        
        batch_pbar = tqdm(train_loader, desc="Training batches", leave=False, ncols=80)
        
        for batch_idx, batch in enumerate(batch_pbar):
            batch = batch.to(device)
            optimizer.zero_grad()
            
            # Forward pass
            node_pred = self.model(batch)
            
            # Calculate loss
            if hasattr(batch, 'valid_mask'):
                valid_mask = batch.valid_mask
                if torch.sum(valid_mask) > 0:
                    loss = criterion(node_pred[valid_mask], batch.y[valid_mask])
                else:
                    loss = criterion(node_pred, batch.y)
            else:
                loss = criterion(node_pred, batch.y)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if self.config.get('gradient_clip', 0) > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), 
                    self.config['gradient_clip']
                )
            
            # Optimizer step
            optimizer.step()
            
            # Learning rate scheduling
            if scheduler is not None and not isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step()
            
            # Calculate metrics
            with torch.no_grad():
                if hasattr(batch, 'valid_mask'):
                    valid_mask = batch.valid_mask
                    if torch.sum(valid_mask) > 0:
                        mae = F.l1_loss(node_pred[valid_mask], batch.y[valid_mask]).item()
                        pred_np = node_pred[valid_mask].cpu().numpy().flatten()
                        target_np = batch.y[valid_mask].cpu().numpy().flatten()
                    else:
                        mae = F.l1_loss(node_pred, batch.y).item()
                        pred_np = node_pred.cpu().numpy().flatten()
                        target_np = batch.y.cpu().numpy().flatten()
                else:
                    mae = F.l1_loss(node_pred, batch.y).item()
                    pred_np = node_pred.cpu().numpy().flatten()
                    target_np = batch.y.cpu().numpy().flatten()
                
                if len(pred_np) > 1 and len(target_np) > 1:
                    r2 = r2_score(target_np, pred_np)
                else:
                    r2 = 0.0
                
                total_loss += loss.item()
                total_mae += mae
                total_r2 += r2
                num_batches += 1
                
                # Update batch progress bar
                batch_pbar.set_postfix({
                    'Loss': f'{loss.item():.4f}',
                    'MAE': f'{mae:.4f}',
                    'R²': f'{r2:.3f}'
                })
        
        batch_pbar.close()
        return total_loss / num_batches, total_mae / num_batches, total_r2 / num_batches
    
    def _validate_epoch(self, val_loader, criterion, device):
        """Validate one epoch"""
        self.model.eval()
        total_loss = 0.0
        total_mae = 0.0
        total_r2 = 0.0
        num_batches = 0
        
        batch_pbar = tqdm(val_loader, desc="Validation batches", leave=False, ncols=80)
        
        with torch.no_grad():
            for batch in batch_pbar:
                batch = batch.to(device)
                
                # Forward pass
                node_pred = self.model(batch)
                
                # Calculate loss and metrics
                if hasattr(batch, 'valid_mask'):
                    valid_mask = batch.valid_mask
                    if torch.sum(valid_mask) > 0:
                        loss = criterion(node_pred[valid_mask], batch.y[valid_mask])
                        mae = F.l1_loss(node_pred[valid_mask], batch.y[valid_mask]).item()
                        pred_np = node_pred[valid_mask].cpu().numpy().flatten()
                        target_np = batch.y[valid_mask].cpu().numpy().flatten()
                    else:
                        loss = criterion(node_pred, batch.y)
                        mae = F.l1_loss(node_pred, batch.y).item()
                        pred_np = node_pred.cpu().numpy().flatten()
                        target_np = batch.y.cpu().numpy().flatten()
                else:
                    loss = criterion(node_pred, batch.y)
                    mae = F.l1_loss(node_pred, batch.y).item()
                    pred_np = node_pred.cpu().numpy().flatten()
                    target_np = batch.y.cpu().numpy().flatten()
                
                if len(pred_np) > 1 and len(target_np) > 1:
                    r2 = r2_score(target_np, pred_np)
                else:
                    r2 = 0.0
                
                total_loss += loss.item()
                total_mae += mae
                total_r2 += r2
                num_batches += 1
                
                # Update batch progress bar
                batch_pbar.set_postfix({
                    'Loss': f'{loss.item():.4f}',
                    'MAE': f'{mae:.4f}',
                    'R²': f'{r2:.3f}'
                })
        
        batch_pbar.close()
        return total_loss / num_batches, total_mae / num_batches, total_r2 / num_batches
    
    def _get_grouped_parameters(self):
        """Get grouped parameters for different learning rates"""
        no_decay = ['bias', 'LayerNorm.weight', 'BatchNorm.weight', 'norm']
        
        grouped_parameters = [
            {
                'params': [p for n, p in self.model.named_parameters()
                          if not any(nd in n for nd in no_decay)],
                'weight_decay': self.config.get('weight_decay', 1e-4)
            },
            {
                'params': [p for n, p in self.model.named_parameters()
                          if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0
            }
        ]
        
        return grouped_parameters
    
    def _get_scheduler(self, optimizer, train_loader, max_epochs):
        """Get learning rate scheduler"""
        scheduler_type = self.config.get('scheduler_type', 'cosine')
        
        if scheduler_type == 'cosine':
            # Cosine annealing scheduler
            return torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=max_epochs, eta_min=1e-6
            )
        elif scheduler_type == 'plateau':
            # Validation-based scheduler
            return torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', patience=10, factor=0.5, min_lr=1e-6, verbose=True
            )
        elif scheduler_type == 'onecycle':
            # OneCycle learning rate scheduling
            return torch.optim.lr_scheduler.OneCycleLR(
                optimizer,
                max_lr=self.config.get('learning_rate', 0.001),
                total_steps=max_epochs * len(train_loader),
                pct_start=0.3,
                div_factor=25.0,
                final_div_factor=10000.0
            )
        else:
            # Default step scheduler
            return torch.optim.lr_scheduler.StepLR(
                optimizer, step_size=max_epochs // 3, gamma=0.1
            )
    
    def _get_loss_function(self):
        """Get loss function"""
        loss_type = self.config.get('loss_type', 'mse')
        
        if loss_type == 'mse':
            return nn.MSELoss()
        elif loss_type == 'mae':
            return nn.L1Loss()
        elif loss_type == 'huber':
            beta = self.config.get('loss_alpha', 0.1)
            return nn.SmoothL1Loss(beta=beta)
        elif loss_type == 'combined':
            return self._combined_loss
        else:
            raise ValueError(f"Unsupported loss type: {loss_type}")
    
    def _combined_loss(self, pred, target):
        """Combined loss function"""
        mse_loss = F.mse_loss(pred, target)
        mae_loss = F.l1_loss(pred, target)
        
        # Relative error loss
        epsilon = 1e-8
        relative_err = torch.abs((pred - target) / (torch.abs(target) + epsilon))
        relative_loss = torch.mean(relative_err)
        
        # Combined loss
        alpha = self.config.get('mse_weight', 0.5)
        beta = self.config.get('mae_weight', 0.3)
        gamma = self.config.get('relative_weight', 0.2)
        
        return alpha * mse_loss + beta * mae_loss + gamma * relative_loss
    
    def _save_best_model(self, epoch, optimizer, scheduler, train_loss, train_mae, train_r2,
                        val_loss, val_mae, val_r2):
        """Save best model"""
        best_model_state = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': getattr(scheduler, 'state_dict', lambda: None)(),
            'val_loss': val_loss,
            'val_mae': val_mae,
            'val_r2': val_r2,
            'train_loss': train_loss,
            'train_mae': train_mae,
            'train_r2': train_r2,
            'config': self.config
        }
        
        # Save to file
        output_dir = self.config.get('output_dir', '.')
        os.makedirs(output_dir, exist_ok=True)
        best_model_path = os.path.join(output_dir, f"{self.model_name}_best.pt")
        torch.save(best_model_state, best_model_path)
        self.logger.info(f"Best model saved to: {best_model_path}")
    
    def predict(self, data_loader) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not initialized")
        
        self.model.eval()
        device = self.config.get('device', 'cpu')
        
        predictions = []
        targets = []
        
        batch_pbar = tqdm(data_loader, desc="Prediction", leave=False, ncols=80)
        
        with torch.no_grad():
            for batch in batch_pbar:
                batch = batch.to(device)
                
                # Forward pass
                node_pred = self.model(batch)
                
                # Move to CPU
                node_pred = node_pred.cpu()
                
                # Extract valid predictions
                if hasattr(batch, 'valid_mask'):
                    valid_mask = batch.valid_mask.cpu()
                    if torch.sum(valid_mask) > 0:
                        pred_np = node_pred[valid_mask].numpy().flatten()
                        target_np = batch.y[valid_mask].cpu().numpy().flatten()
                    else:
                        pred_np = node_pred.numpy().flatten()
                        target_np = batch.y.cpu().numpy().flatten()
                else:
                    pred_np = node_pred.numpy().flatten()
                    target_np = batch.y.cpu().numpy().flatten()
                
                predictions.extend(pred_np)
                targets.extend(target_np)
                
                # Update progress bar
                batch_pbar.set_postfix({
                    'Valid samples': f'{len(predictions)}'
                })
        
        batch_pbar.close()
        return np.array(predictions), np.array(targets)
    
    def evaluate(self, data_loader) -> Dict[str, float]:
        """Evaluate model performance"""
        predictions, targets = self.predict(data_loader)

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
        
        return {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'mae': mae,
            'r2': r2,
            'mape': mape
        }
    
    def save_model(self, filepath: str):
        """Save model"""
        if self.model is None:
            raise ValueError("Model not initialized")
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'model_name': self.model_name
        }, filepath)
    
    def load_model(self, filepath: str):
        """Load model"""
        checkpoint = torch.load(filepath, map_location=self.config.get('device', 'cpu'))
        
        self.config = checkpoint['config']
        self.model_name = checkpoint['model_name']
        
        self._create_model()
        self.model.load_state_dict(checkpoint['model_state_dict'])


def get_config(gnn_type: str = 'gcn', hidden_dim: int = 128, 
                    num_layers: int = 3, learning_rate: float = 0.001):
    """
    Get fixed model configuration
    
    Args:
        gnn_type: GNN type ('gcn', 'gat', 'transformer', 'sage', 'gin')
        hidden_dim: Hidden dimension
        num_layers: Number of GNN layers
        learning_rate: Learning rate
    
    Returns:
        Dict: Configuration dictionary
    """
    return {
        # Input dimensions
        'node_feature_dim': 9,
        'edge_feature_dim': 8,
        
        # GNN configuration
        'gnn_type': gnn_type,
        'hidden_dim': hidden_dim,
        'num_layers': num_layers,
        'num_heads': 8 if gnn_type in ['gat', 'transformer'] else 1,
        'dropout': 0.1,
        
        # Transformer configuration
        'd_model': hidden_dim,
        'nhead': 8,
        'num_encoder_layers': 3,
        'dim_feedforward': hidden_dim * 4,
        'transformer_dropout': 0.1,
        
        # Training configuration
        'learning_rate': learning_rate,
        'weight_decay': 1e-4,
        'max_epochs': 200,
        'patience': 30,
        'batch_size': 16,
        
        # Learning rate scheduling
        'scheduler_type': 'cosine',
        
        # Loss function
        'loss_type': 'combined',
        'mse_weight': 0.5,
        'mae_weight': 0.3,
        'relative_weight': 0.2,
        
        # Regularization
        'gradient_clip': 1.0,
        
        # Model saving
        'save_best_model': True,
        'output_dir': './results',
        
        # Device
        'device': 'cuda' if torch.cuda.is_available() else 'cpu'
    }


# Usage examples
if __name__ == "__main__":
    # Test fixed model
    gnn_types = ['gcn', 'gat', 'sage', 'gin']
    
    for gnn_type in gnn_types:
        print(f"\n=== Testing fixed {gnn_type.upper()} model ===")
        config = get_config(gnn_type=gnn_type)
        model = NodeDelayPredictor(config, f"Fixed_{gnn_type.upper()}_NodeDelay")
        print(f"Model created successfully: {model.model_name}")
        print(f"Total parameters: {sum(p.numel() for p in model.model.parameters()):,}")
        print(f"GNN type: {gnn_type}")
        print(f"Hidden dimension: {config['hidden_dim']}")
        print(f"Number of layers: {config['num_layers']}")
