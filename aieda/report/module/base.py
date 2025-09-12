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
    
    def get_image_path(self, image_type: str, design_name: str = None):
        path = self.workspace.paths_table.get_image_path(
                        image_type=image_type,
                        design_name=design_name)
        
        if self.workspace.directory in path:
            path = path.replace(self.workspace.directory, '', 1)
        
        return "..{}".format(path)
    
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
                header_str = "{}|{} ".format(header_str, header)
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
        
        def add_class_members(self, obj):
            from dataclasses import asdict
            
            def travel(json_node, parent_name=None):
                for field_name, field_value in json_node.items():
                    if parent_name is None:
                        parameter_name = field_name
                    else:
                        parameter_name = "{}_{}".format(parent_name, field_name)
                        
                    if isinstance(field_value, dict):
                        travel(json_node = field_value, parent_name=parameter_name)
                    elif isinstance(field_value, list):
                        for item in field_value:
                            travel(json_node = item, parent_name=parameter_name)
                    else:
                        self.add_parameter(parameter_name, field_value)
                        
            travel(asdict(obj))
        
    class Image():
        from typing import Optional
        
        def __init__(self, image_path : str):
            self.image_path = image_path
            
        def image_content(self,
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
            
            return ["<div align=\"{}\"> <img src=\"{}\" width=\"{}\" height=\"{}\"  alt=\"{}\" /> </div>".format(align, self.image_path, width, height, alt).strip(),
                    "",
                    ""]
    class Images:
        from typing import List, Optional
        
        def __init__(self, image_paths: List[str]):
            """
            Initialize with a list of image paths
            
            Args:
                image_paths: List of image file paths
            """
            self.image_paths = image_paths
            # Validate all image paths exist
            # for path in self.image_paths:
            #     if not os.path.exists(path):
            #         raise FileNotFoundError(f"Image file not found: {path}")
        
        def images_content(self,
            width: str = "auto",
            height: str = "400",
            alts: Optional[List[str]] = None,
            align: str = "left",
            per_row: int = 3,
            gap: str = "10px"
            ) -> List[str]:
            """
            Generate markdown content for multiple images displayed side by side
            
            Args:
                width: Pixel width or string of percentage for each image
                height: Pixel height or "auto"
                alts: List of image descriptions, should match image_paths length
                align: Alignment for the container (left/center/right)
                per_row: Number of images to display per row
                gap: Gap between images (CSS length value)
                
            Returns:
                List of strings with markdown content for multiple images
            """
            # Validate alts length if provided
            if alts is not None and len(alts) != len(self.image_paths):
                raise ValueError("Length of alts must match length of image_paths")
            
            # Use empty strings for alts if not provided
            if alts is None:
                alts = ["" for _ in self.image_paths]
            
            content = []
            
            # Create image containers row by row
            for i in range(0, len(self.image_paths), per_row):
                # Start a new row container with flexbox
                row_container_start = f'<div align="{align}"><div style="display: flex; justify-content: {align}; gap: {gap}; flex-wrap: wrap;">'
                content.append(row_container_start)
                
                # Add images for this row
                for j in range(i, min(i + per_row, len(self.image_paths))):
                    img_tag = f'  <div style="flex: 0 0 auto;"><img src="{self.image_paths[j]}" width="{width}" height="{height}" alt="{alts[j]}" /></div>'
                    content.append(img_tag)
                
                # Close the row container
                row_container_end = '</div></div>'
                content.append(row_container_end)
                content.append("")  # Add empty line after each row
            
            return content