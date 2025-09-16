# -*- encoding: utf-8 -*-
"""
@File : workspace.py
@Author : yell
@Desc : Workspace UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QGroupBox, QGridLayout, QCheckBox)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from aieda.gui.chip import ChipLayout
from aieda.workspace import Workspace


class WorkspaceUI(QMainWindow):
    """Main application window"""
    
    def __init__(self, workspace):
        super().__init__()
        self.workspace = workspace
        self.layout_display = None
        self.init_ui()
        self.load_layout()
    
    def init_ui(self):
        """Initialize user interface"""
        # Set window properties
        self.setWindowTitle("AiEDA Workspace")
        self.setGeometry(100, 100, 1200, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create control panel
        control_panel = QGroupBox("Control Panel")
        control_layout = QHBoxLayout()
        
        # Workspace selection button
        self.workspace_label = QLabel("design:{}, workspace:{}".format(self.workspace.design, self.workspace.directory))
        
        # Add to control panel
        control_layout.addWidget(self.workspace_label)
        control_layout.addStretch()
        
        control_panel.setLayout(control_layout)
        
        # Create display area
        self.display_widget = QWidget()
        self.display_layout = QVBoxLayout(self.display_widget)
        self.display_layout.addWidget(QLabel("Please select a workspace and load layout"))
        
        # Add to main layout
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.display_widget, 1)  # 1 means stretchable
        
        # Create status bar message
        self.statusBar().showMessage("Ready")
    
    def load_layout(self):
        """Load chip layout"""
        if not self.workspace:
            QMessageBox.warning(self, "Warning", "Please select a workspace first")
            return
        
        try:
            # Clear previous display
            for i in reversed(range(self.display_layout.count())):
                widget = self.display_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Create and display layout display component
            self.layout_display = ChipLayout(self.workspace)
            self.display_layout.addWidget(self.layout_display)
            
            self.statusBar().showMessage("Chip layout loaded successfully")
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load layout: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load chip layout:\n{str(e)}")
            
            # Add error message to display area
            error_label = QLabel(f"Loading failed: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red;")
            self.display_layout.addWidget(error_label)