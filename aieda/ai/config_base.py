#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : config_base.py
@Author : yhqiu
@Desc : configuration base class for AI4EDA tasks
'''

import json
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

class ConfigBase:
    """Base configuration class"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary"""
        return cls(**config_dict)

    @classmethod
    def from_json_file(cls, json_file: Union[str, Path]) -> "Config":
        """Load configuration from JSON file"""
        with open(json_file, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {key: value for key, value in self.__dict__.items()
                if not key.startswith('_')}

    def to_json_file(self, json_file: Union[str, Path]) -> None:
        """Save configuration to JSON file"""
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def update(self, **kwargs) -> None:
        """Update configuration parameters"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self) -> "Config":
        """Copy configuration"""
        return self.from_dict(self.to_dict())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"