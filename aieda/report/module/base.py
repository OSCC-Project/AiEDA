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
        
    class BaseHtml:
        def __init__(self, workspace: Workspace, display_names_map=None):
            self.workspace = workspace
            self.content = []
            self.display_names_map = display_names_map
            
        def make_title(self, tile):
            info_str= []
            info_str.append(f"<div style='margin-top: 20px; padding-top: 10px; border-top: 1px solid #ccc;'>"
                            f"<h3>{tile}</h3></div>")
            return info_str
                
        def make_seperator(self):
            info_str= []
            info_str.append("<hr>")
            
            return info_str
        
        def make_line_space(self):
            """Add a visible blank line to HTML content"""
            info_str= []
            info_str.append("<div style='margin-top: 10px;'></div>")
            
            return info_str
        
        def make_parameters(self, parameters):
            info_str= []
            if isinstance(parameters, list):
                for (key, value) in parameters:
                    info_str.append(f"<p><b>{key} :</b> {value}</p>")
            else:
                (key, value) = parameters
                info_str.append(f"<p><b>{key} :</b> {value}</p>")
            return info_str
        
        def make_table(self, headers=[], contents=[]):
            info_str= []
            info_str.append("<table border='1' cellspacing='0' cellpadding='3' style='border-collapse:collapse;'>")
            
            # 添加表头行，确保所有header在同一行
            if headers:
                info_str.append("<tr style='background-color:#f0f0f0;'>")
                for header in headers:
                    info_str.append(f"<th style='width:150px;'>{header}</th>")
                info_str.append("</tr>")
            
            for values in contents:
                if len(values) != len(headers):
                    continue
                
                info_str.append("<tr>")
                for value in values:
                    info_str.append(f"<td style='text-align:left;'>{value}</td>")
                info_str.append("</tr>")
                    
            info_str.append("</table>")
            
            return info_str
        
def markdown_to_html(markdown_text):
    """Simple markdown to HTML conversion (no external dependencies)
    
    Args:
        markdown_text: str or list, markdown content
        
    Returns:
        str: HTML content
    """
    def _process_inline_formatting(text):
        """Process inline markdown formatting (bold, italic, etc.)"""
        # Process bold (**text**)
        text = text.replace('**', '<strong>', 1)
        if '**' in text:
            text = text.replace('**', '</strong>', 1)
        # Process italic (*text*)
        text = text.replace('*', '<em>', 1)
        if '*' in text:
            text = text.replace('*', '</em>', 1)
        # Process inline code (`code`)
        while '`' in text:
            start = text.find('`')
            text = text[:start] + '<code>' + text[start+1:]
            if '`' in text[start+6:]:
                end = text.find('`', start+6)
                text = text[:end] + '</code>' + text[end+1:]
            else:
                break
        return text

    # If input is list, join to string
    if isinstance(markdown_text, list):
        markdown_text = '\n'.join(markdown_text)
    elif not isinstance(markdown_text, str):
        markdown_text = str(markdown_text)
    
    # Split into lines and process
    lines = markdown_text.split('\n')
    html_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{line[5:]}</h4>')
        elif line.startswith('##### '):
            html_lines.append(f'<h5>{line[6:]}</h5>')
        elif line.startswith('###### '):
            html_lines.append(f'<h6>{line[7:]}</h6>')
        # Tables
        elif line.startswith('|') and '|' in line and i + 1 < len(lines) and lines[i + 1].startswith('|') and '-' in lines[i + 1]:
            html_lines.append('<table border="1" cellspacing="0" cellpadding="3" style="border-collapse:collapse; width: 100%;">')
            
            # Header row
            header_cells = [cell.strip() for cell in line.split('|')[1:-1]]
            html_lines.append('<tr style="background-color:#f0f0f0;">')
            for cell in header_cells:
                html_lines.append(f'<th>{cell}</th>')
            html_lines.append('</tr>')
            
            # Skip separator row
            i += 2
            
            # Process data rows
            while i < len(lines) and lines[i].startswith('|'):
                data_cells = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                html_lines.append('<tr>')
                for cell in data_cells:
                    html_lines.append(f'<td>{cell}</td>')
                html_lines.append('</tr>')
                i += 1
            html_lines.append('</table>')
            continue
        # Lists (unordered)
        elif line.startswith('- ') or line.startswith('* '):
            html_lines.append('<ul>')
            while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                content = lines[i][2:]
                # Process inline formatting
                content = _process_inline_formatting(content)
                html_lines.append(f'<li>{content}</li>')
                i += 1
            html_lines.append('</ul>')
            continue
        # Lists (ordered)
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
            html_lines.append('<ol>')
            while i < len(lines) and lines[i][0].isdigit() and '.' in lines[i]:
                content = lines[i].split('. ', 1)[1] if '. ' in lines[i] else lines[i]
                # Process inline formatting
                content = _process_inline_formatting(content)
                html_lines.append(f'<li>{content}</li>')
                i += 1
            html_lines.append('</ol>')
            continue
        # Code blocks
        elif line.startswith('```'):
            html_lines.append('<pre><code>')
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                html_lines.append(lines[i])
                i += 1
            html_lines.append('</code></pre>')
        # Paragraph with inline formatting
        else:
            if line.strip():
                # Process inline formatting
                line = _process_inline_formatting(line)
                html_lines.append(f'<p>{line}</p>')
            else:
                html_lines.append('<br>')
        i += 1
    
    # Combine with basic styling
    html_content = '\n'.join(html_lines)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 10px; }}
      h1, h2, h3, h4, h5, h6 {{ color: #333; margin-top: 20px; margin-bottom: 10px; }}
      pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
      code {{ font-family: monospace; }}
      ul, ol {{ padding-left: 30px; }}
      table {{ margin: 15px 0; }}
      th {{ font-weight: bold; text-align: left; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """    