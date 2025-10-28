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
        self.markdown_display = None
        
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
        
        # Create markdown display area with same properties as text_display
        self.markdown_display = QTextEdit()
        self.markdown_display.setReadOnly(True)  # Make it read-only
        self.markdown_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.markdown_display.setMinimumHeight(200)
        self.markdown_display.setStyleSheet("background-color: white; padding: 0px; border-radius: 4px;")
        self.markdown_display.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
        self.markdown_display.setAcceptRichText(True)  # Rich text support for HTML
        self.markdown_display.hide()  # Hide by default
        
        # Create text input area (lower part)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter information here...")
        self.text_input.setMinimumHeight(100)  # Increase input box height
        self.text_input.setAcceptRichText(False)  # Keep plain text for simplicity
        
        # Add widgets to layout with 10:1 ratio
        main_layout.addWidget(self.text_display, 8)  # 10 parts for display
        main_layout.addWidget(self.markdown_display, 8)  # Same size as text_display
        main_layout.addWidget(self.text_input, 2)    # 1 part for input
    
    def make_html(self, info_str=[]):
        """Display HTML content in text_display and hide markdown_display"""
        # Show text_display and hide markdown_display
        self.text_display.show()
        self.markdown_display.hide()
        
        # Set HTML content and scroll to bottom
        self.text_display.setHtml('\n'.join(info_str))
        self.text_display.verticalScrollBar().setValue(
            self.text_display.verticalScrollBar().maximum())
    
    def make_markdown(self, markdown_text):
        """Display markdown content in markdown_display and hide text_display
        
        Args:
            markdown_text: str or list, markdown content to display
        """
        # Show markdown_display and hide text_display
        self.markdown_display.show()
        self.text_display.hide()
        
        try:
            # Convert markdown to HTML
            from aieda.report.module.base import markdown_to_html
            html_content = markdown_to_html(markdown_text)
            
            # Set HTML content and scroll to top
            self.markdown_display.setHtml(html_content)
            self.markdown_display.verticalScrollBar().setValue(0)
        except Exception as e:
            # If conversion fails, show error message
            self.markdown_display.setHtml(f"<p style='color: red;'>Error displaying markdown: {str(e)}</p>")
        
    def load_workspace(self):
        from aieda.report import ReportSummary
        reportor = ReportSummary(self.workspace)
        info_str = reportor.ReportHtml(self.workspace).summary_workspace()
       
        self.make_html(info_str)
        
    def on_net_selected(self, selected_net):
        from aieda.report import ReportSummary
        reportor = ReportSummary(self.workspace)
        info_str = reportor.ReportHtml(self.workspace).summary_net(selected_net)
            
        self.make_html(info_str)
        
    def on_flow_selected(self, flow):
        # from aieda.report import ReportSummary
        # reportor = ReportSummary(self.workspace)
        # info_str = reportor.ReportHtml(self.workspace).summary_flow(flow)
        
        # self.make_html(info_str)
        from aieda.report import ReportSummary
        reportor = ReportSummary.ReportMarkdown(self.workspace)
        info_str = reportor.summary_flow(flow)
        
        self.make_markdown(info_str)
        