#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : log.py
@Author : yell
@Desc : logging
'''

import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from typing import Optional

class Logger:
    def __init__(
        self,
        name: str = "aieda",
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        level: int = logging.INFO,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            formatter = logging.Formatter(fmt)
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            if log_file:
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=max_bytes, backupCount=backup_count
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)


def create_logger(name: str = "aieda",
               log_file: Optional[str] = None,
               max_bytes: int = 10 * 1024 * 1024,  # 10MB
               backup_count: int = 5,
               level: int = logging.INFO,
               fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s") -> Logger:
    if log_file is not None and os.path.exists(log_file):
        return Logger(name=name,
                  log_file=log_file,
                  max_bytes=max_bytes,
                  backup_count=backup_count,
                  level=level,
                  fmt=fmt)
    else:    
        return Logger(name=name,
                  log_file=None,
                  max_bytes=max_bytes,
                  backup_count=backup_count,
                  level=level,
                  fmt=fmt)