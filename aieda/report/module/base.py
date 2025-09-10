#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : base.py
@Author : yell
@Desc : base report
"""

import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from ...workspace import Workspace

class ReportBase:    
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.content = []
           
    def generate_markdown(self, path : str):
        pass
    
    def generate_pdf(self, path : str):
        pass
    
    
    class TableMatrix():
        def __init__(self, headers = []):
            self.headers = headers
            self.max_num = len(headers)
    
            self.content = []
            self.rows = []
            
            self._make_header()
            
        def _make_header(self):
            header_str = ""
            seperator = ""
            
            for header in self.headers:
                header_str = "{}| ".format(header_str)
                seperator = "{}|------".format(seperator)
           
                
            header_str = "{} |".format(header_str)
            seperator = "{}|".format(seperator)
                
            self.content.append(header_str.strip())
            self.content.append(seperator.strip())

        def add_row(self, row_value):
            self.rows.append(row_value)
        
        def make_table(self):  
            for row_data in self.rows:
                if len(row_data) > self.max_num:
                    print("error row data")
                    continue
                
                row_str = "" 
                for col_data in row_data:    
                    row_str = "{}|{}".format(row_str, col_data)
                
                row_str = "{}|".format(row_str)
                self.content.append(row_str.strip())
            
            return self.content
        
    class TableParameters():
        def __init__(self, max_num):
            self.max_num = max_num
    
            self.content = []
            self.parameters = []
            
            self._make_header()
            
        def _make_header(self):
            header_str = ""
            seperator = ""
            
            for i in range(0, self.max_num):
                header_str = "{}|  |  ".format(header_str)
                seperator = "{}|------|------".format(seperator)
                
            header_str = "{}|".format(header_str)
            seperator = "{}|".format(seperator)
                
            self.content.append(header_str.strip())
            self.content.append(seperator.strip())

        def add_parameter(self, name, value):
            self.parameters.append((name, value))
        
        def make_table(self):  
            row_str = ""
            param_num = 0
            for ((name, value)) in self.parameters:     
                row_str = "{}|{}|{}".format(row_str, name, value)
                param_num = param_num + 1
                
                if param_num == self.max_num:
                    row_str = "{}|".format(row_str)
                    self.content.append(row_str.strip())
                    
                    # reset
                    row_str = ""
                    param_num = 0
            #add last        
            if param_num > 0:
                row_str = "{}|".format(row_str)
                self.content.append(row_str.strip())
            
            return self.content
        
    class Image():
        from typing import Optional
        
        def __init__(self, image_path : str):
            self.image_path = image_path
            
        def generate_image_markdown(self,
            width: str = "100%",
            height: str = "100%",
            alt: str = "",
            align = "center"
            ) -> str:
            """
            generate markdown iamge content
            
            width: pixel width or string of percentage
            height: pixel height
            alt: image description
            
            return:
                content with standard markdown string
            """

            if not self.image_path.strip():
                raise ValueError("error image not exist.")
            
            return "<div align=\"{}\"> <img src=\"{}\" width=\"{}\" height=\"{}\"  alt=\"{}\" /> </div>".format(align, self.image_path, width, height, alt).strip()