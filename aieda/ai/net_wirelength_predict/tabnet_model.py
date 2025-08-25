#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : tabnet_model.py
@Author : yhqiu
@Desc : TabNet model definitions and utilities
'''
import numpy as np
import torch
import torch.nn as nn
from pytorch_tabnet.tab_model import TabNetRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from typing import Dict, Any, Tuple, Optional, Union, List
import logging


class TabNetBaseModel:
    """TabNet model wrapper"""

    def __init__(self, config: Dict[str, Any], model_name: str = "TabNet"):
        """
        Initialize TabNet model

        Args:
            config: Model configuration dictionary
            model_name: Name of the model for logging
        """
        self.config = config
        self.model_name = model_name
        self.model = None
        self.logger = logging.getLogger(__name__)

        # Create model
        self._create_model()

    def _create_model(self) -> None:
        """Create TabNet model instance"""
        self.logger.info(
            f"Creating {self.model_name} model, config: {self.config}")

        device_name = self.config.get('device', 'auto')
        if isinstance(device_name, torch.device):
            device_name = str(device_name)

        self.model = TabNetRegressor(
            n_d=self.config.get('n_d', 64),
            n_a=self.config.get('n_a', 128),
            n_steps=self.config.get('n_steps', 4),
            gamma=self.config.get('gamma', 1.8),
            n_independent=self.config.get('n_independent', 2),
            n_shared=self.config.get('n_shared', 2),
            lambda_sparse=self.config.get('lambda_sparse', 1e-5),
            optimizer_fn=torch.optim.Adam,
            optimizer_params=dict(lr=self.config.get('learning_rate', 0.01)),
            scheduler_params=dict(
                mode="min",
                patience=5,
                min_lr=1e-5,
                factor=0.9
            ),
            scheduler_fn=torch.optim.lr_scheduler.ReduceLROnPlateau,
            mask_type="entmax",
            device_name=device_name,
            verbose=0
        )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray,
            X_val: np.ndarray = None, y_val: np.ndarray = None,
            callbacks: List = None) -> None:
        """
        Train the model

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            callbacks: List of callback functions
        """
        if self.model is None:
            raise ValueError("Model not initialized")

        # Ensure y is 2D array
        y_train = y_train.reshape(-1, 1)
        if y_val is not None:
            y_val = y_val.reshape(-1, 1)

        # Prepare evaluation set
        eval_set = [
            (X_val, y_val)] if X_val is not None and y_val is not None else None
        eval_name = ['val'] if eval_set is not None else None
        eval_metric = ['rmse'] if eval_set is not None else None

        # Train model
        self.model.fit(
            X_train=X_train,
            y_train=y_train,
            eval_set=eval_set,
            eval_name=eval_name,
            eval_metric=eval_metric,
            max_epochs=self.config.get('max_epochs', 100),
            patience=self.config.get('patience', 20),
            batch_size=self.config.get('batch_size', 1024),
            virtual_batch_size=128,
            num_workers=self.config.get('num_workers', 0),
            pin_memory=self.config.get('pin_memory', True),
            drop_last=self.config.get('drop_last', False),
            callbacks=callbacks or []
        )

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions

        Args:
            X: Input features

        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        return self.model.predict(X)

    def save_model(self, filepath: str) -> None:
        """
        Save model to file

        Args:
            filepath: Path to save the model
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        self.model.save_model(filepath)
        self.logger.info(f"{self.model_name} saved to {filepath}")

    def load_model(self, filepath: str) -> None:
        """
        Load model from file

        Args:
            filepath: Path to load the model from
        """
        if self.model is None:
            self._create_model()

        self.model.load_model(filepath)
        self.logger.info(f"{self.model_name} model loaded from {filepath}")

    def get_feature_importances(self) -> np.ndarray:
        """
        Get feature importances

        Returns:
            Feature importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        return self.model.feature_importances_

    def export_to_onnx(self, filepath: str, input_shape: Tuple[int, ...]) -> None:
        """
        Export model to ONNX format

        Args:
            filepath: Path to save the ONNX model
            input_shape: Shape of the input tensor (batch_size, num_features)
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        # Set model to evaluation mode
        self.model.network.eval()

        # Create a dummy input tensor
        dummy_input = torch.randn(*input_shape, device=self.model.device_name)

        # Export the model
        torch.onnx.export(
            self.model.network,
            dummy_input,
            filepath,
            export_params=True,
            opset_version=13,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'},
                          'output': {0: 'batch_size'}},
        )

        self.logger.info(
            f"{self.model_name} model exported to ONNX format at {filepath}")

    def load_onnx_model(self, filepath: str) -> None:
        """
        Load ONNX model (for inference only)

        Args:
            filepath: Path to the ONNX model
        """
        try:
            import onnxruntime
        except ImportError:
            raise ImportError(
                "Please install onnxruntime to load ONNX models: pip install onnxruntime")

        self.onnx_session = onnxruntime.InferenceSession(filepath)
        self.logger.info(f"ONNX model loaded from {filepath}")

    def predict_onnx(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using ONNX model

        Args:
            X: Input features (numpy array)

        Returns:
            Predictions
        """
        if not hasattr(self, 'onnx_session'):
            raise ValueError("ONNX model not loaded yet")

        # Run inference
        input_name = self.onnx_session.get_inputs()[0].name
        output_name = self.onnx_session.get_outputs()[0].name
        predictions = self.onnx_session.run(
            [output_name], {input_name: X.astype(np.float32)})

        return predictions[0]


class ViaPredictor(TabNetBaseModel):
    """Via number prediction model"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "Via Predictor")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict via numbers (rounded to integers and non-negative)

        Args:
            X: Input features

        Returns:
            Predicted via numbers
        """
        raw_predictions = super().predict(X)
        # Round to integer and ensure non-negative
        predictions = np.round(raw_predictions).astype(int)
        predictions = np.maximum(0, predictions)
        return predictions

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate via prediction performance

        Args:
            X_test: Test features
            y_test: Test targets

        Returns:
            Evaluation metrics
        """
        y_pred = self.predict(X_test)

        # Calculate evaluation metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        exact_match_ratio = np.mean(y_pred == y_test)
        close_match_ratio = np.mean(np.abs(y_pred - y_test) <= 1)

        results = {
            'RMSE': rmse,
            'MAE': mae,
            'Exact_Match_Ratio': exact_match_ratio,
            'Close_Match_Ratio': close_match_ratio
        }

        # Log evaluation results
        self.logger.info(f"{self.model_name} evaluation results:")
        for metric, value in results.items():
            if metric in ['Exact_Match_Ratio', 'Close_Match_Ratio']:
                self.logger.info(f"{metric}: {value*100:.2f}%")
            else:
                self.logger.info(f"{metric}: {value:.4f}")

        return results


class WirelengthPredictor(TabNetBaseModel):
    """Wirelength ratio prediction model"""

    def __init__(self, config: Dict[str, Any], model_name: str = "Wirelength Predictor"):
        super().__init__(config, model_name)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate wirelength prediction performance

        Args:
            X_test: Test features
            y_test: Test targets

        Returns:
            Evaluation metrics
        """
        y_pred = self.predict(X_test)

        # Calculate evaluation metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100

        results = {
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'MAPE': mape
        }

        # Log evaluation results
        self.logger.info(f"{self.model_name} evaluation results:")
        for metric, value in results.items():
            self.logger.info(f"{metric}: {value:.4f}")

        return results


class BaselineWirelengthPredictor(WirelengthPredictor):
    """Baseline wirelength prediction model (without via features)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "Baseline Wirelength Predictor")


class WithViaWirelengthPredictor(WirelengthPredictor):
    """Wirelength prediction model with via features"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "With Via Wirelength Predictor")


class WithPredViaWirelengthPredictor(WirelengthPredictor):
    """Wirelength prediction model with predicted via features"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "With Predicted Via Wirelength Predictor")
