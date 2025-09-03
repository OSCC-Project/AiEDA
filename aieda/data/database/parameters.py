#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : parameters.py
@Author : zhanghongda
@Desc : parameters database
"""
import json
from dataclasses import dataclass


@dataclass
class EDAParameters(object):
    """data structure"""

    placement_target_density = 0.4
    placement_init_wirelength_coef = 0.14
    placement_min_wirelength_force_bar = -54.04
    placement_max_phi_coef = 1.04  
    cts_skew_bound = "0.1"
    cts_max_buf_tran = "1.2"
    cts_max_sink_tran = "1.1"
    cts_max_cap = "0.2"
    cts_max_fanout = "32"
    cts_cluster_size = "32"