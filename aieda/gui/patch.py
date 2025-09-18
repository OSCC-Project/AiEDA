"""
@File : patch.py
@Author : yell
@Desc : Patch Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGroupBox, QGridLayout, QScrollArea, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF


class PatchLayout(QWidget):
    """Patch Layout UI component"""
    
    def __init__(self, patch):
        self.patch = patch
        super().__init__()
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI components"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel("Patch View")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Add title to layout
        self.main_layout.addWidget(title_label)