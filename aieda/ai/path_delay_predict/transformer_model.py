#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : transformer_model.py
@Author : yhqiu
@Desc : Model module for path delay prediction using transformer architecture
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism"""

    def __init__(self, hidden_dim: int, num_heads: int, dropout: float = 0.1):
        """
        Initialize multi-head attention.

        Args:
            hidden_dim: Hidden dimension size
            num_heads: Number of attention heads
            dropout: Dropout rate
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads

        assert (
            self.head_dim * num_heads == hidden_dim
        ), "hidden_dim must be divisible by num_heads"

        self.q_linear = nn.Linear(hidden_dim, hidden_dim)
        self.k_linear = nn.Linear(hidden_dim, hidden_dim)
        self.v_linear = nn.Linear(hidden_dim, hidden_dim)
        self.out_linear = nn.Linear(hidden_dim, hidden_dim)

        self.dropout = nn.Dropout(dropout)
        self.scale = torch.sqrt(torch.FloatTensor([self.head_dim]))

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of multi-head attention.

        Args:
            query: Query tensor [batch_size, seq_len, hidden_dim]
            key: Key tensor [batch_size, seq_len, hidden_dim]
            value: Value tensor [batch_size, seq_len, hidden_dim]
            mask: Optional attention mask

        Returns:
            Tuple of (output tensor, attention weights)
        """
        batch_size = query.shape[0]

        # Linear transformations
        Q = self.q_linear(query)  # [batch_size, seq_len, hidden_dim]
        K = self.k_linear(key)  # [batch_size, seq_len, hidden_dim]
        V = self.v_linear(value)  # [batch_size, seq_len, hidden_dim]

        # Reshape tensors for multi-head attention computation
        Q = Q.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        K = K.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        V = V.view(batch_size, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        # Calculate attention scores
        energy = torch.matmul(Q, K.permute(0, 1, 3, 2)) / self.scale.to(query.device)

        if mask is not None:
            energy = energy.masked_fill(mask == 0, -1e10)

        # Apply softmax to get attention weights
        attention = self.dropout(F.softmax(energy, dim=-1))

        # Apply attention weights to value matrix
        x = torch.matmul(attention, V)
        x = x.permute(0, 2, 1, 3).contiguous()
        x = x.view(batch_size, -1, self.hidden_dim)

        # Final linear layer
        x = self.out_linear(x)

        return x, attention


class CrossAttentionBlock(nn.Module):
    """Cross-attention block with self-attention and feed-forward network"""

    def __init__(self, hidden_dim: int, num_heads: int, dropout: float = 0.1):
        """
        Initialize cross-attention block.

        Args:
            hidden_dim: Hidden dimension size
            num_heads: Number of attention heads
            dropout: Dropout rate
        """
        super().__init__()
        self.self_attn = MultiHeadAttention(hidden_dim, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(hidden_dim, num_heads, dropout)
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.norm3 = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.ffn = nn.Sequential(
            nn.Linear(hidden_dim, 4 * hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(4 * hidden_dim, hidden_dim),
            nn.Dropout(dropout),
        )

    def forward(
        self,
        x: torch.Tensor,
        context: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass of cross-attention block.

        Args:
            x: Input tensor
            context: Context tensor for cross-attention
            mask: Optional attention mask

        Returns:
            Output tensor
        """
        # Self-attention
        attn_output, _ = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Cross-attention
        cross_attn_output, _ = self.cross_attn(x, context, context, mask)
        x = self.norm2(x + self.dropout(cross_attn_output))

        # Feed-forward network
        ffn_output = self.ffn(x)
        x = self.norm3(x + ffn_output)

        return x


class GatedResidualNetwork(nn.Module):
    """Gated residual network with skip connections"""

    def __init__(
        self, input_dim: int, hidden_dim: int, output_dim: int, dropout: float = 0.1
    ):
        """
        Initialize gated residual network.

        Args:
            input_dim: Input dimension
            hidden_dim: Hidden dimension
            output_dim: Output dimension
            dropout: Dropout rate
        """
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        self.input_layer = nn.Linear(input_dim, hidden_dim)
        self.hidden_layer = nn.Linear(hidden_dim, output_dim)
        self.skip_layer = (
            nn.Linear(input_dim, output_dim)
            if input_dim != output_dim
            else nn.Identity()
        )

        self.gate = nn.Linear(input_dim + output_dim, output_dim)
        self.norm = nn.LayerNorm(output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of gated residual network.

        Args:
            x: Input tensor

        Returns:
            Output tensor
        """
        # Main path
        hidden = F.elu(self.input_layer(x))
        hidden = self.dropout(hidden)
        hidden = self.hidden_layer(hidden)

        # Residual connection
        skip = self.skip_layer(x)

        # Gating mechanism
        gate_input = torch.cat([x, hidden], dim=-1)
        gate = torch.sigmoid(self.gate(gate_input))

        # Apply gating
        output = gate * hidden + (1 - gate) * skip

        # Layer normalization
        output = self.norm(output)

        return output


class MultiScaleFeatureFusion(nn.Module):
    """Multi-scale feature fusion module"""

    def __init__(
        self, input_dim: int, hidden_dims: list, output_dim: int, dropout: float = 0.1
    ):
        """
        Initialize multi-scale feature fusion.

        Args:
            input_dim: Input dimension
            hidden_dims: List of hidden dimensions for different scales
            output_dim: Output dimension
            dropout: Dropout rate
        """
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim

        # Multi-scale feature extraction
        self.scale_layers = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(input_dim, dim),
                    nn.LayerNorm(dim),
                    nn.GELU(),
                    nn.Dropout(dropout),
                )
                for dim in hidden_dims
            ]
        )

        # Feature fusion
        self.fusion_layer = nn.Linear(sum(hidden_dims), output_dim)
        self.norm = nn.LayerNorm(output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of multi-scale feature fusion.

        Args:
            x: Input tensor

        Returns:
            Output tensor
        """
        # Multi-scale feature extraction
        multi_scale_features = [layer(x) for layer in self.scale_layers]

        # Feature fusion
        fused = torch.cat(multi_scale_features, dim=-1)
        output = self.fusion_layer(fused)
        output = self.norm(output)
        output = self.dropout(output)

        return output


class PathDelayPredictor(nn.Module):
    """Path delay predictor using transformer architecture"""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int,
        num_heads: int,
        feature_dim: int,
        mlp_hidden_dim: int,
        output_dim: int,
        dropout: float = 0.1,
    ):
        """
        Initialize path delay predictor.

        Args:
            input_dim: Input dimension
            hidden_dim: Hidden dimension
            num_layers: Number of transformer layers
            num_heads: Number of attention heads
            feature_dim: Feature dimension for positional encoding
            mlp_hidden_dim: MLP hidden dimension
            output_dim: Output dimension
            dropout: Dropout rate
        """
        super().__init__()

        # Input embedding
        self.input_embedding = nn.Linear(input_dim, hidden_dim)
        self.pos_encoding = nn.Parameter(torch.zeros(1, feature_dim, hidden_dim))

        # Feature normalization layer
        self.input_norm = nn.BatchNorm1d(input_dim)

        # Multi-scale feature extraction
        self.multi_scale_fusion = MultiScaleFeatureFusion(
            input_dim=input_dim,
            hidden_dims=[hidden_dim // 4, hidden_dim // 2, hidden_dim, hidden_dim * 2],
            output_dim=hidden_dim,
            dropout=dropout,
        )

        # Cross-attention layers
        self.cross_attention_layers = nn.ModuleList(
            [
                CrossAttentionBlock(hidden_dim, num_heads, dropout)
                for _ in range(num_layers)
            ]
        )

        # Self-attention layer to capture internal sequence relationships
        self.self_attention = MultiHeadAttention(hidden_dim, num_heads, dropout)
        self.attn_norm = nn.LayerNorm(hidden_dim)

        # Gated residual networks
        self.grn1 = GatedResidualNetwork(
            input_dim=hidden_dim,
            hidden_dim=mlp_hidden_dim,
            output_dim=hidden_dim,
            dropout=dropout,
        )

        self.grn2 = GatedResidualNetwork(
            input_dim=hidden_dim,
            hidden_dim=mlp_hidden_dim,
            output_dim=hidden_dim,
            dropout=dropout,
        )

        # Output layer
        self.output_layer = nn.Sequential(
            nn.Linear(hidden_dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, mlp_hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(mlp_hidden_dim // 2, output_dim),
        )

        # Initialize positional encoding
        nn.init.xavier_uniform_(self.pos_encoding)

        # Add residual connection
        self.has_residual = input_dim == output_dim
        if self.has_residual:
            self.residual_proj = nn.Linear(input_dim, output_dim)
            self.final_norm = nn.LayerNorm(output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of path delay predictor.

        Args:
            x: Input tensor [batch_size, seq_len, input_dim]

        Returns:
            Output tensor [batch_size, output_dim]
        """
        batch_size, seq_len = x.shape[0], x.shape[1]

        # Save original input for residual connection
        original_x = x

        # Input normalization
        x_normalized = self.input_norm(x.permute(0, 2, 1)).permute(0, 2, 1)

        # Multi-scale feature extraction
        multi_scale_features = self.multi_scale_fusion(x_normalized)

        # Input embedding
        x = self.input_embedding(x_normalized)

        # Add positional encoding
        x = x + self.pos_encoding[:, :seq_len, :]

        # Self-attention processing
        self_attn_out, _ = self.self_attention(x, x, x)
        x = self.attn_norm(x + self_attn_out)

        # Create context information
        context = multi_scale_features

        # Cross-attention layers
        for layer in self.cross_attention_layers:
            x = layer(x, context)

        # Global pooling
        avg_pool = torch.mean(x, dim=1)
        max_pool, _ = torch.max(x, dim=1)
        x = avg_pool + max_pool

        # Multi-layer gated residual networks
        x = self.grn1(x)
        x = self.grn2(x)

        # Output layer
        output = self.output_layer(x)

        # Add residual connection (if input and output dimensions match)
        if self.has_residual:
            # Global pooling for original input
            orig_pooled = torch.mean(original_x, dim=1)
            residual = self.residual_proj(orig_pooled)
            output = self.final_norm(output + residual)

        return output


# Usage example
if __name__ == "__main__":
    # Model parameters
    input_dim = 3
    hidden_dim = 32
    num_layers = 3
    num_heads = 4
    feature_dim = 100  # Max sequence length
    mlp_hidden_dim = 64
    output_dim = 1
    dropout = 0.3

    # Create model
    model = PathDelayPredictor(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        num_heads=num_heads,
        feature_dim=feature_dim,
        mlp_hidden_dim=mlp_hidden_dim,
        output_dim=output_dim,
        dropout=dropout,
    )

    # Test forward pass
    batch_size = 8
    seq_len = 50
    x = torch.randn(batch_size, seq_len, input_dim)

    output = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
