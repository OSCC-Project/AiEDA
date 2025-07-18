#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : parameters.py
@Author : yell
@Desc : parameters database
'''
from dataclasses import dataclass

@dataclass
class EDAParameters(object):
    """data structure"""
    placement_target_density = 0.8
    

    