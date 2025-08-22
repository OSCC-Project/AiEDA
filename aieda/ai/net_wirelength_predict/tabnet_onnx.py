#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : export_onnx.py
@Author : yhqiu
@Desc : Export TabNet model to ONNX format
'''
import os
import numpy as np
import torch
import logging
from typing import Dict, Any, Optional, Tuple

from tabnet_model import TabNetModel, BaselineWirelengthPredictor, ViaPredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_via_model_config() -> Dict[str, Any]:
    """
    Load via model configuration

    Returns:
        Configuration dictionary
    """
    return {
        'n_d': 16,
        'n_a': 32,
        'n_steps': 5,
        'gamma': 1.3,
        'n_independent': 2,
        'n_shared': 2,
        'lambda_sparse': 1e-4,
        'learning_rate': 0.01,
        'max_epochs': 100,
        'patience': 20,
        'batch_size': 512,
        'device': 'cpu'  # Use CPU for export to avoid device issues
    }


def load_wirelength_model_config() -> Dict[str, Any]:
    """
    Load wirelength model configuration

    Returns:
        Configuration dictionary
    """
    return {
        'n_d': 64,
        'n_a': 128,
        'n_steps': 4,
        'gamma': 1.8,
        'n_independent': 2,
        'n_shared': 2,
        'lambda_sparse': 1e-5,
        'learning_rate': 0.01,
        'max_epochs': 100,
        'patience': 20,
        'batch_size': 2048,
        'device': 'cpu'  # Use CPU for export to avoid device issues
    }


def export_model_to_onnx(model_type: str = 'wirelength') -> None:
    """
    Export model to ONNX format

    Args:
        model_type: Type of model to export ('wirelength' or 'via')
    """

    # Create model instance
    if model_type == 'wirelength':
        config = load_wirelength_model_config()
        model = BaselineWirelengthPredictor(config)
        # Replace with your actual model path
        model_path = '/home/yhqiu/aieda_fork/aieda/ai/net_wirelength_predict/saved_models/baseline_model.zip'
        onnx_path = '/home/yhqiu/aieda_fork/aieda/ai/net_wirelength_predict/saved_models/baseline_model.onnx'
    elif model_type == 'via':
        config = load_via_model_config()
        model = ViaPredictor(config)
        # Replace with your actual model path
        model_path = '/home/yhqiu/aieda_fork/aieda/ai/net_wirelength_predict/saved_models/via_model.zip'
        onnx_path = '/home/yhqiu/aieda_fork/aieda/ai/net_wirelength_predict/saved_models/via_model.onnx'
    else:
        raise ValueError(
            f"Invalid model_type: {model_type}. Must be 'wirelength' or 'via'")

    # Load trained model
    try:
        model.load_model(model_path)
        logger.info(f"Successfully loaded model from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        return

    # Determine input shape (assuming you have 10 features, replace with actual number)
    # You can find the number of features from your training data
    num_features = 9  # Replace with actual number of features
    input_shape = (1, num_features)  # Batch size 1 for export

    # Export to ONNX
    try:
        model.export_to_onnx(onnx_path, input_shape)
        logger.info(
            f"Successfully exported model to ONNX format at {onnx_path}")
    except Exception as e:
        logger.error(f"Failed to export model to ONNX format: {e}")
        return

    # Verify ONNX model
    try:
        # Load ONNX model
        model.load_onnx_model(onnx_path)

        # Create test input
        test_input = np.random.rand(*input_shape).astype(np.float32)
        logger.info(f"Test input type: {type(test_input)}")
        logger.info(f"Test input shape: {test_input.shape}")

        # Predict with original model
        torch_pred = model.predict(test_input)

        # Predict with ONNX model - ensure input is numpy array
        try:
            onnx_pred = model.predict_onnx(test_input)
        except TypeError as te:
            logger.warning(f"Type error during ONNX prediction: {te}")
            logger.info("Trying to convert input to numpy array explicitly...")
            # Ensure input is a numpy array
            test_input_np = np.array(test_input, dtype=np.float32)
            onnx_pred = model.predict_onnx(test_input_np)

        # Handle ONNX output which might be a list or other format
        logger.info(f"ONNX prediction raw type: {type(onnx_pred)}")

        # Convert ONNX output to numpy array if needed
        if isinstance(onnx_pred, list):
            # If it's a list of arrays, take the first element
            if len(onnx_pred) > 0 and hasattr(onnx_pred[0], '__array__'):
                onnx_pred_np = np.array(onnx_pred[0])
            else:
                onnx_pred_np = np.array(onnx_pred)
        elif hasattr(onnx_pred, '__array__'):
            # If it has __array__ method, convert to numpy
            onnx_pred_np = np.array(onnx_pred)
        else:
            # Try direct conversion
            onnx_pred_np = np.array(onnx_pred)

        # Ensure torch prediction is also numpy array
        torch_pred_np = np.array(torch_pred) if not isinstance(
            torch_pred, np.ndarray) else torch_pred

        # Log predictions safely
        logger.info(f"Original model prediction: {torch_pred_np.tolist()}")
        logger.info(f"ONNX model prediction: {onnx_pred_np.tolist()}")

        # Compare predictions
        diff = np.max(np.abs(torch_pred_np - onnx_pred_np))
        logger.info(f"Maximum difference between predictions: {diff}")

        if diff < 1e-5:
            logger.info(
                "Predictions from ONNX model match closely with original model.")
        else:
            logger.warning(
                "Predictions from ONNX model differ significantly from original model.")

    except Exception as e:
        logger.error(f"Failed to verify ONNX model: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return


if __name__ == '__main__':
    # Export wirelength prediction model
    export_model_to_onnx('wirelength')

    # Export via prediction model (uncomment below)
    # export_model_to_onnx('via')
