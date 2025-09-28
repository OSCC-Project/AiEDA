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
        
        # Create text display area (upper part)
        self.text_display = QLabel("Select a workspace to see details")
        self.text_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.text_display.setWordWrap(True)
        self.text_display.setMinimumHeight(200)
        # Reduced padding from 10px to 0px to make it closer to title_label
        self.text_display.setStyleSheet("background-color: white; padding: 0px; border-radius: 4px;")
        self.text_display.setTextFormat(Qt.RichText)
        
        # Create text input area (lower part)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter information here...")
        
        # Add widgets to layout with 10:1 ratio
        main_layout.addWidget(self.text_display, 10)  # 10 parts for display
        main_layout.addWidget(self.text_input, 1)    # 1 part for input
        
    def load_workspace(self):
        info_str = []
            
        info_str.append(f"<p><b>Design:</b> {self.workspace.design}</p>")
        info_str.append(f"<p><b>Directory:</b> {self.workspace.directory}</p>")
        
        info_str.append("<hr>")
        
        info_str.append(f"<p><b>Process node:</b> {self.workspace.configs.workspace.process_node}</p>")
        info_str.append(f"<p><b>version:</b> {self.workspace.configs.workspace.version}</p>")
        
        info_str.append("<hr>")
        
        info_str.append("<p><b>Flows:</b></p>")
        info_str.append("<table border='1' cellspacing='0' cellpadding='3' style='border-collapse:collapse;'>")
        info_str.append("<tr style='background-color:#f0f0f0;'>")
        info_str.append("<th style='width:150px;'>Step</th>")
        info_str.append("<th style='width:150px;'>EDA Tool</th>")
        info_str.append("<th style='width:150px;'>State</th>")
        info_str.append("<th style='width:150px;'>Runtime</th>")
        info_str.append("</tr>")
        
        for flow in self.workspace.configs.flows:
            step_str = str(flow.step.value)[:50]
            tool_str = str(flow.eda_tool)[:50]
            state_str = str(flow.state.value)[:50]
            runtime_str = str(flow.runtime)[:50]
            info_str.append("<tr>")
            info_str.append(f"<td style='text-align:left;'>{step_str}</td>")
            info_str.append(f"<td style='text-align:left;'>{tool_str}</td>")
            info_str.append(f"<td style='text-align:left;'>{state_str}</td>")
            info_str.append(f"<td style='text-align:left;'>{runtime_str}</td>")
            info_str.append("</tr>")
        
        info_str.append("</table>")
        self.text_display.setText('\n'.join(info_str))
        
        