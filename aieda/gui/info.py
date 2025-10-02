"""
@File : info.py
@Author : yell
@Desc : Infomation UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QCheckBox, QTextEdit, QLineEdit
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

class WorkspaceInformation(QWidget):
    """Workspace information display component with text display and input functionality
    
    This class provides a UI component with a text display area and text input area
    in a 10:1 vertical ratio layout.
    
    Attributes:
        text_display (QTextEdit): Text display area for showing information
        text_input (QLineEdit): Text input area for user input
    """
    
    def __init__(self, workspace, parent=None):
        """Initialize the WorkspaceInformation component
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.workspace = workspace
        
        # Initialize UI components
        self.text_display = None
        self.text_input = None
        
        # Initialize the layout
        self.init_ui()
        
        self.load_workspace()
    
    def init_ui(self):
        """Initialize the UI components and layout"""
        # Create main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create text display area (upper part) with scroll functionality
        self.text_display = QTextEdit("Select a workspace to see details")
        self.text_display.setReadOnly(True)  # Make it read-only
        self.text_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.text_display.setMinimumHeight(200)
        self.text_display.setStyleSheet("background-color: white; padding: 0px; border-radius: 4px;")
        self.text_display.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
        self.text_display.setAcceptRichText(True)  # Keep rich text support
        
        # Create text input area (lower part)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter information here...")
        self.text_input.setMinimumHeight(100)  # Increase input box height
        self.text_input.setAcceptRichText(False)  # Keep plain text for simplicity
        
        # Add widgets to layout with 10:1 ratio
        main_layout.addWidget(self.text_display, 8)  # 10 parts for display
        main_layout.addWidget(self.text_input, 2)    # 1 part for input
        
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
        """添加一个可见的空白行到HTML内容中"""
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
    
    def make_html(self, info_str=[]):
        self.text_display.setHtml('\n'.join(info_str))
        self.text_display.verticalScrollBar().setValue(
            self.text_display.verticalScrollBar().maximum())

        
    def load_workspace(self):
        info_str = []
        
        info_str += self.make_title("Workspace information")
        
        info_str += self.make_parameters(("Design", self.workspace.design))
        info_str += self.make_parameters(("Directory", self.workspace.directory))
        info_str += self.make_parameters(("Process node", self.workspace.configs.workspace.process_node))
        info_str += self.make_parameters(("version", self.workspace.configs.workspace.version))
        
        info_str += self.make_seperator()
        
        info_str += self.make_title("Flows")
        
        flow_headers = ["Step", "EDA Tool", "State", "Runtime"]
        flow_values = []
        
        for flow in self.workspace.configs.flows:
            flow_values.append((flow.step.value, flow.eda_tool, flow.state.value, flow.runtime))
             
        info_str += self.make_table(flow_headers, flow_values)
        
        # Use setHtml to properly render HTML content in QTextEdit
        self.make_html(info_str)
        
    def on_net_selected(self, selected_net):
        """处理网络选择事件，将网络详情添加到文本显示区域并滚动到底部"""
        info_str = []
        
        info_str += self.make_title(f"Net information : {selected_net.name}")
        info_str += self.make_line_space()
        
        headers = ["Feature", "Value"]
        values = []

        feature = selected_net.feature
        
        values.append(("llx", feature.llx))
        values.append(("lly", feature.lly))
        values.append(("urx", feature.urx))
        values.append(("ury", feature.ury))
        values.append(("width", feature.width))
        values.append(("height", feature.height))
        values.append(("area", feature.area))
        values.append(("aspect_ratio", feature.aspect_ratio))
        values.append(("wire_len", feature.wire_len))
        values.append(("via_num", feature.via_num))
        values.append(("drc_num", feature.drc_num))
        values.append(("R", feature.R))
        values.append(("C", feature.C))
        values.append(("power", feature.power))
        values.append(("delay", feature.delay))
        values.append(("slew", feature.slew))
        values.append(("volume", feature.volume))
        values.append(("l_ness", feature.l_ness))
        values.append(("layer_ratio", feature.layer_ratio))
        
        if feature.place_feature is not None:
            place_feature = feature.place_feature
            
            values.append(("placement_pin_num", place_feature.pin_num))
            values.append(("placement_aspect_ratio", place_feature.aspect_ratio))
            values.append(("placement_width", place_feature.width))
            values.append(("placement_height", place_feature.height))
            values.append(("placement_area", place_feature.area))
            values.append(("placement_l_ness", place_feature.l_ness))
            values.append(("placement_rsmt", place_feature.rsmt))
            values.append(("placement_hpwl", place_feature.hpwl))
        
        info_str += self.make_table(headers, values)
            
        self.make_html(info_str)