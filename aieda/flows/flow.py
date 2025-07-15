#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : flow.py
@Author : yell
@Desc : flow data structure
'''
from enum import Enum

class DbFlow(object): 
    class FlowStep(Enum):
        """PR step
        """
        NoStep = ""
        initFlow = "initFlow"
        initDB = "initDB"
        edi = "edi"
        floorplan = "floorplan"
        pdn = "PDN"
        prePlace = "prePlace"
        place = "place"
        globalPlace = "gp"
        detailPlace = "dp"
        cts = "CTS"
        route = "route"
        globalRouting = "gr"
        detailRouting = "dr"
        eco = "eco"
        fixFanout = "fixFanout"
        optDrv = "optDrv"
        optHold = "optHold"
        optSetup = "optSetup"
        legalization = "legalization"
        filler = "filler"
        drc = "drc"
        sta = "sta"
        rcx = "rcx"
        gds = "gds"
        full_flow = 'full_flow'
        
    class FlowState(Enum):
        """flow running state
        """
        Unstart = "unstart"
        Success = "success"
        Ongoing = "ongoing"
        Imcomplete = "incomplete"
        Ignored = "ignored"
    
    def __init__(self, 
                 eda_tool, 
                 step : FlowStep, 
                 state : FlowState=FlowState.Ignored,
                 input_def=None, 
                 input_verilog=None,
                 output_def=None,
                 output_verilog=None):    
        self.eda_tool = eda_tool
        self.step : self.FlowStep = step
        self.state : self.FlowState = state
        
        self.input_def = input_def
        self.input_verilog = input_verilog
        self.output_def = output_def
        self.output_verilog = output_verilog

    def set_state_unstart(self):
        """set_state_unstart"""
        self.state = self.FlowState.Unstart
    
    def set_state_running(self):
        """set_state_running"""
        self.state = self.FlowState.Ongoing
        
    def set_state_finished(self):
        """set_state_finished"""
        self.state = self.FlowState.Success
    
    def set_state_imcomplete(self):
        """set_state_imcomplete"""
        self.state = self.FlowState.Imcomplete
        
    def set_first_flow(self):
        """set_first_flow"""
        self.is_first = True
        
    def is_new(self):
        """get task new"""
        if( self.state != self.FlowState.Unstart):
            return True
        else :
            return False
        
    def is_ongoing(self):
        """if task is ongoing"""
        if( self.state == self.FlowState.Ongoing):
            return True
        else :
            return False
    
    def is_finish(self):
        """if task finished"""
        if( self.state == self.FlowState.Success):
            return True
        else :
            return False
        
    def is_imcomplete(self):
        """is task not finished"""
        if( self.state == self.FlowState.Imcomplete):
            return True
        else :
            return False
        
    def is_first_flow(self):
        """if 1st flow in flowlist"""
        return self.is_first    
